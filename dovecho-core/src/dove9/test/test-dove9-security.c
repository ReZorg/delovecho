/* Copyright (c) 2024-2026 Dovecho authors, see the included COPYING file */

/* Security-focused unit tests: buffer overflow protection, NULL pointer
   resilience, priority clamping, empty/malicious input handling. */

#include "dove9-test-common.h"
#include "dove9-test-mocks.h"
#include "../types/dove9-types.h"
#include "../core/dove9-kernel.h"
#include "../integration/dove9-mail-protocol-bridge.h"
#include "../dove9-system.h"

#include <string.h>

static void test_buffer_overflow_subject(void)
{
	struct dove9_mail_bridge *bridge;
	struct dove9_mail_message mail;
	struct dove9_process_request req;

	dove9_test_begin("oversized subject is safely truncated");

	bridge = dove9_mail_bridge_create();

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@test.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	/* Fill subject to max capacity */
	memset(mail.subject, 'A', sizeof(mail.subject) - 1);
	mail.subject[sizeof(mail.subject) - 1] = '\0';
	snprintf(mail.body, sizeof(mail.body), "test");

	dove9_mail_to_process(bridge, &mail, &req);

	/* Should not segfault; output should be bounded */
	DOVE9_TEST_ASSERT(strlen(req.body) < 65536);

	dove9_mail_bridge_destroy(&bridge);
	dove9_test_end();
}

static void test_null_vtable_resilience(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	int ret;

	dove9_test_begin("NULL LLM vtable is rejected at init");

	sys = dove9_system_create();
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_triadic = true;
	cfg.llm = NULL;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;

	ret = dove9_system_init(sys, &cfg);
	/* Should reject NULL LLM */
	DOVE9_TEST_ASSERT(ret != 0);

	dove9_system_destroy(&sys);
	dove9_test_end();
}

static void test_priority_clamping(void)
{
	struct dove9_kernel *kernel;
	struct dove9_process *proc;

	dove9_test_begin("out-of-range priority is clamped to [1, 9]");

	kernel = dove9_kernel_create();

	/* Priority 0 should be clamped to 1 */
	proc = dove9_kernel_spawn(kernel, "low", 0);
	DOVE9_TEST_ASSERT_NOT_NULL(proc);
	DOVE9_TEST_ASSERT(proc->priority >= 1);

	/* Priority 100 should be clamped to 9 */
	proc = dove9_kernel_spawn(kernel, "high", 100);
	DOVE9_TEST_ASSERT_NOT_NULL(proc);
	DOVE9_TEST_ASSERT(proc->priority <= 9);

	dove9_kernel_destroy(&kernel);
	dove9_test_end();
}

static void test_empty_input_handling(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	struct dove9_mail_message mail;
	struct dove9_mail_message reply;
	int ret;

	dove9_test_begin("completely empty mail does not crash");

	dove9_mock_reset();

	sys = dove9_system_create();
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_triadic = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_system_init(sys, &cfg);
	dove9_system_start(sys);

	/* All-zero mail message */
	memset(&mail, 0, sizeof(mail));
	memset(&reply, 0, sizeof(reply));

	ret = dove9_system_process_mail(sys, &mail, &reply);
	/* May succeed (producing empty reply) or fail gracefully */
	(void)ret;

	dove9_system_stop(sys);
	dove9_system_destroy(&sys);
	dove9_test_end();
}

static void test_double_destroy_safe(void)
{
	struct dove9_kernel *kernel;

	dove9_test_begin("double destroy does not crash");

	kernel = dove9_kernel_create();
	dove9_kernel_destroy(&kernel);
	DOVE9_TEST_ASSERT_NULL(kernel);

	/* Second destroy on NULL pointer should be safe */
	dove9_kernel_destroy(&kernel);
	DOVE9_TEST_ASSERT_NULL(kernel);

	dove9_test_end();
}

static void test_context_init_sets_safe_defaults(void)
{
	struct dove9_cognitive_context ctx;

	dove9_test_begin("cognitive context init sets all fields safely");

	/* Fill with garbage first */
	memset(&ctx, 0xFF, sizeof(ctx));

	dove9_cognitive_context_init(&ctx);

	DOVE9_TEST_ASSERT_DOUBLE_EQ(ctx.salience, 0.0);
	DOVE9_TEST_ASSERT(!ctx.degraded);
	DOVE9_TEST_ASSERT(ctx.input[0] == '\0');
	DOVE9_TEST_ASSERT(ctx.response[0] == '\0');
	DOVE9_TEST_ASSERT(ctx.error[0] == '\0');

	dove9_test_end();
}

int main(void)
{
	dove9_test_fn tests[] = {
		test_buffer_overflow_subject,
		test_null_vtable_resilience,
		test_priority_clamping,
		test_empty_input_handling,
		test_double_destroy_safe,
		test_context_init_sets_safe_defaults,
	};
	return dove9_test_run("dove9-security", tests, 6);
}
