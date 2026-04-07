/* Copyright (c) 2024-2026 Dovecho authors, see the included COPYING file */

/* Unit tests for dove9-system: top-level Dove9System lifecycle,
   process_mail, and event emission. */

#include "dove9-test-common.h"
#include "dove9-test-mocks.h"
#include "../dove9-system.h"
#include "../types/dove9-types.h"

#include <string.h>

/* ---- Event tracking ---- */

static unsigned int mail_received_count;
static unsigned int response_ready_count;
static unsigned int triad_sync_count;
static unsigned int cycle_complete_count;

static void reset_event_counts(void)
{
	mail_received_count = 0;
	response_ready_count = 0;
	triad_sync_count = 0;
	cycle_complete_count = 0;
}

static void test_event_handler(const struct dove9_system_event *event,
			       void *ctx)
{
	(void)ctx;
	switch (event->type) {
	case DOVE9_SYS_MAIL_RECEIVED:
		mail_received_count++;
		break;
	case DOVE9_SYS_RESPONSE_READY:
		response_ready_count++;
		break;
	case DOVE9_SYS_TRIAD_SYNC:
		triad_sync_count++;
		break;
	case DOVE9_SYS_CYCLE_COMPLETE:
		cycle_complete_count++;
		break;
	default:
		break;
	}
}

static void test_system_create(void)
{
	struct dove9_system *sys;

	dove9_test_begin("system create/destroy");

	sys = dove9_system_create();
	DOVE9_TEST_ASSERT_NOT_NULL(sys);
	dove9_system_destroy(&sys);
	DOVE9_TEST_ASSERT_NULL(sys);

	dove9_test_end();
}

static void test_system_start_stop(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	int ret;

	dove9_test_begin("system start and stop");

	dove9_mock_reset();

	sys = dove9_system_create();
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_triadic = true;
	cfg.enable_sys6 = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;

	ret = dove9_system_init(sys, &cfg);
	DOVE9_TEST_ASSERT_INT_EQ(ret, 0);

	ret = dove9_system_start(sys);
	DOVE9_TEST_ASSERT_INT_EQ(ret, 0);
	DOVE9_TEST_ASSERT(dove9_system_is_running(sys));

	dove9_system_stop(sys);
	DOVE9_TEST_ASSERT(!dove9_system_is_running(sys));

	dove9_system_destroy(&sys);
	dove9_test_end();
}

static void test_process_mail(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	struct dove9_mail_message mail;
	struct dove9_mail_message reply;
	int ret;

	dove9_test_begin("process_mail produces a reply");

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

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@example.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	snprintf(mail.subject, sizeof(mail.subject), "Hello System");
	snprintf(mail.body, sizeof(mail.body), "Full integration test");

	ret = dove9_system_process_mail(sys, &mail, &reply);
	DOVE9_TEST_ASSERT_INT_EQ(ret, 0);
	DOVE9_TEST_ASSERT(reply.body[0] != '\0');
	DOVE9_TEST_ASSERT_STR_EQ(reply.to, "user@example.com");

	dove9_system_stop(sys);
	dove9_system_destroy(&sys);
	dove9_test_end();
}

static void test_system_events(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	struct dove9_mail_message mail;
	struct dove9_mail_message reply;

	dove9_test_begin("events fire during mail processing");

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

	reset_event_counts();
	dove9_system_on(sys, test_event_handler, NULL);

	dove9_system_start(sys);

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@example.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	snprintf(mail.subject, sizeof(mail.subject), "Event test");
	snprintf(mail.body, sizeof(mail.body), "Trigger events");

	dove9_system_process_mail(sys, &mail, &reply);

	DOVE9_TEST_ASSERT(mail_received_count >= 1);
	DOVE9_TEST_ASSERT(response_ready_count >= 1);

	dove9_system_stop(sys);
	dove9_system_destroy(&sys);
	dove9_test_end();
}

static void test_system_not_started(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	struct dove9_mail_message mail;
	struct dove9_mail_message reply;
	int ret;

	dove9_test_begin("process_mail fails if system not started");

	dove9_mock_reset();

	sys = dove9_system_create();
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_triadic = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_system_init(sys, &cfg);

	/* Don't start the system */
	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@example.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	snprintf(mail.body, sizeof(mail.body), "Should fail");

	ret = dove9_system_process_mail(sys, &mail, &reply);
	DOVE9_TEST_ASSERT(ret != 0);

	dove9_system_destroy(&sys);
	dove9_test_end();
}

static void test_system_double_start(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	int ret1, ret2;

	dove9_test_begin("double start is idempotent");

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

	ret1 = dove9_system_start(sys);
	ret2 = dove9_system_start(sys);
	DOVE9_TEST_ASSERT_INT_EQ(ret1, 0);
	/* Second start should succeed or be no-op */
	DOVE9_TEST_ASSERT(ret2 == 0);

	dove9_system_stop(sys);
	dove9_system_destroy(&sys);
	dove9_test_end();
}

static void test_system_multiple_messages(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	struct dove9_mail_message mail, reply;
	int i;

	dove9_test_begin("system handles multiple sequential messages");

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

	for (i = 0; i < 5; i++) {
		memset(&mail, 0, sizeof(mail));
		snprintf(mail.from, sizeof(mail.from), "user@example.com");
		snprintf(mail.to, sizeof(mail.to), "bot@test.com");
		snprintf(mail.subject, sizeof(mail.subject), "Msg %d", i);
		snprintf(mail.body, sizeof(mail.body), "Body %d", i);

		dove9_system_process_mail(sys, &mail, &reply);
		DOVE9_TEST_ASSERT(reply.body[0] != '\0');
	}

	dove9_system_stop(sys);
	dove9_system_destroy(&sys);
	dove9_test_end();
}

int main(void)
{
	dove9_test_fn tests[] = {
		test_system_create,
		test_system_start_stop,
		test_process_mail,
		test_system_events,
		test_system_not_started,
		test_system_double_start,
		test_system_multiple_messages,
	};
	return dove9_test_run("dove9-system", tests, 7);
}
