/* Copyright (c) 2024-2026 Dovecho authors, see the included COPYING file */

/* Stress and robustness tests for the dove9 cognitive pipeline.
   Validates behavior under high volume, rapid state transitions,
   and adversarial input patterns. */

#include "dove9-test-common.h"
#include "dove9-test-mocks.h"
#include "../dove9-system.h"
#include "../core/dove9-kernel.h"
#include "../cognitive/dove9-triadic-engine.h"
#include "../types/dove9-types.h"

#include <string.h>

/* ---- High volume message processing ---- */

static void test_high_volume_messages(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	struct dove9_mail_message mail, reply;
	int i, success_count = 0;

	dove9_test_begin("system handles 100 messages");

	dove9_mock_reset();

	sys = dove9_system_create();
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_triadic = true;
	cfg.enable_sys6 = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_system_init(sys, &cfg);
	dove9_system_start(sys);

	for (i = 0; i < 100; i++) {
		memset(&mail, 0, sizeof(mail));
		snprintf(mail.from, sizeof(mail.from), "user%d@test.com", i);
		snprintf(mail.to, sizeof(mail.to), "bot@test.com");
		snprintf(mail.subject, sizeof(mail.subject), "Msg #%d", i);
		snprintf(mail.body, sizeof(mail.body), "Body of message %d", i);

		if (dove9_system_process_mail(sys, &mail, &reply) == 0)
			success_count++;
	}

	DOVE9_TEST_ASSERT(success_count == 100);

	dove9_system_stop(sys);
	dove9_system_destroy(&sys);
	dove9_test_end();
}

/* ---- Rapid start/stop cycling ---- */

static void test_rapid_start_stop(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	int i;

	dove9_test_begin("rapid start/stop 20 times doesn't crash");

	dove9_mock_reset();

	sys = dove9_system_create();
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_triadic = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_system_init(sys, &cfg);

	for (i = 0; i < 20; i++) {
		dove9_system_start(sys);
		dove9_system_stop(sys);
	}

	DOVE9_TEST_ASSERT(!dove9_system_is_running(sys));

	dove9_system_destroy(&sys);
	dove9_test_end();
}

/* ---- Kernel at near-capacity ---- */

static void test_kernel_near_capacity(void)
{
	struct dove9_kernel *kernel;
	struct dove9_process *proc;
	struct dove9_kernel_metrics metrics;
	unsigned int i, spawned = 0;

	dove9_test_begin("kernel handles near-capacity gracefully");

	kernel = dove9_kernel_create();

	/* Spawn up to 90% of capacity */
	for (i = 0; i < (DOVE9_MAX_PROCESSES * 9 / 10); i++) {
		proc = dove9_kernel_spawn(kernel, "bulk", 5);
		if (proc != NULL) spawned++;
		else break;
	}

	metrics = dove9_kernel_get_metrics(kernel);
	DOVE9_TEST_ASSERT_UINT_EQ(metrics.total_spawned, spawned);

	dove9_kernel_destroy(&kernel);
	dove9_test_end();
}

/* ---- Triadic engine multi-cycle ---- */

static void test_triadic_multi_cycle(void)
{
	struct dove9_dte_processor_config cfg = {
		.enable_parallel_cognition = false,
		.memory_retrieval_count = 3,
		.salience_threshold = 0.1,
	};
	struct dove9_dte_processor *dte;
	struct dove9_cognitive_processor proc;
	struct dove9_triadic_engine *engine;
	int i;

	dove9_test_begin("triadic engine runs 10 cycles (120 steps)");

	dove9_mock_reset();

	dte = dove9_dte_processor_create(&cfg, &dove9_mock_llm,
					 &dove9_mock_memory, &dove9_mock_persona);
	proc = dove9_dte_processor_as_cognitive(dte);
	engine = dove9_triadic_engine_create(&proc);
	dove9_triadic_engine_start(engine);

	for (i = 0; i < 120; i++)
		dove9_triadic_engine_advance_step(engine);

	DOVE9_TEST_ASSERT_UINT_EQ(dove9_triadic_engine_get_current_cycle(engine), 10);

	dove9_triadic_engine_stop(engine);
	dove9_triadic_engine_destroy(&engine);
	dove9_dte_processor_destroy(&dte);
	dove9_test_end();
}

/* ---- Long input strings ---- */

static void test_long_input_strings(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	struct dove9_mail_message mail, reply;

	dove9_test_begin("very long body is handled safely");

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

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@test.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	/* Fill body to near capacity */
	memset(mail.body, 'X', sizeof(mail.body) - 1);
	mail.body[sizeof(mail.body) - 1] = '\0';

	dove9_system_process_mail(sys, &mail, &reply);
	/* Should not crash */
	DOVE9_TEST_ASSERT(true);

	dove9_system_stop(sys);
	dove9_system_destroy(&sys);
	dove9_test_end();
}

/* ---- Mock call counter accumulation ---- */

static void test_mock_counter_accumulation(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	struct dove9_mail_message mail, reply;
	unsigned int llm_calls;

	dove9_test_begin("mock counters accumulate across messages");

	dove9_mock_reset();
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_mock_llm_generate_calls, 0);

	sys = dove9_system_create();
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_triadic = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_system_init(sys, &cfg);
	dove9_system_start(sys);

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@test.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	snprintf(mail.body, sizeof(mail.body), "First");
	dove9_system_process_mail(sys, &mail, &reply);
	llm_calls = dove9_mock_llm_generate_calls;

	snprintf(mail.body, sizeof(mail.body), "Second");
	dove9_system_process_mail(sys, &mail, &reply);

	DOVE9_TEST_ASSERT(dove9_mock_llm_generate_calls > llm_calls);

	dove9_system_stop(sys);
	dove9_system_destroy(&sys);
	dove9_test_end();
}

/* ---- Reset between test suites ---- */

static void test_mock_reset_clears_all(void)
{
	dove9_test_begin("dove9_mock_reset clears all counters");

	/* Set some counters */
	dove9_mock_llm_generate_calls = 42;
	dove9_mock_memory_store_calls = 17;
	dove9_mock_persona_personality_calls = 99;

	dove9_mock_reset();

	DOVE9_TEST_ASSERT_UINT_EQ(dove9_mock_llm_generate_calls, 0);
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_mock_llm_parallel_calls, 0);
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_mock_memory_store_calls, 0);
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_mock_memory_retrieve_recent_calls, 0);
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_mock_memory_retrieve_relevant_calls, 0);
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_mock_persona_personality_calls, 0);
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_mock_persona_emotion_calls, 0);
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_mock_persona_update_calls, 0);

	dove9_test_end();
}

int main(void)
{
	dove9_test_fn tests[] = {
		test_high_volume_messages,
		test_rapid_start_stop,
		test_kernel_near_capacity,
		test_triadic_multi_cycle,
		test_long_input_strings,
		test_mock_counter_accumulation,
		test_mock_reset_clears_all,
	};
	return dove9_test_run("dove9-stress", tests, 7);
}
