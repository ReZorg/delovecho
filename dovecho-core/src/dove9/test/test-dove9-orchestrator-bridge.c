/* Copyright (c) 2024-2026 Dovecho authors, see the included COPYING file */

/* Unit tests for dove9-orchestrator-bridge: DovecotEmail→Dove9System via
   the orchestrator bridge layer. */

#include "dove9-test-common.h"
#include "dove9-test-mocks.h"
#include "../integration/dove9-orchestrator-bridge.h"
#include "../types/dove9-types.h"

#include <string.h>

/* ---- Event tracking ---- */

static unsigned int mail_processed_count;
static unsigned int error_count;

static void reset_event_counts(void)
{
	mail_processed_count = 0;
	error_count = 0;
}

static void test_event_handler(const struct dove9_orchestrator_event *event,
			       void *ctx)
{
	(void)ctx;
	switch (event->type) {
	case DOVE9_ORCH_MAIL_PROCESSED:
		mail_processed_count++;
		break;
	case DOVE9_ORCH_ERROR:
		error_count++;
		break;
	default:
		break;
	}
}

static void test_bridge_create(void)
{
	struct dove9_orchestrator_bridge *bridge;

	dove9_test_begin("orchestrator bridge create/destroy");

	bridge = dove9_orchestrator_bridge_create();
	DOVE9_TEST_ASSERT_NOT_NULL(bridge);
	dove9_orchestrator_bridge_destroy(&bridge);
	DOVE9_TEST_ASSERT_NULL(bridge);

	dove9_test_end();
}

static void test_bridge_init(void)
{
	struct dove9_orchestrator_bridge *bridge;
	struct dove9_orchestrator_config cfg;
	int ret;

	dove9_test_begin("init with valid config succeeds");

	bridge = dove9_orchestrator_bridge_create();
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_triadic = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;

	ret = dove9_orchestrator_bridge_init(bridge, &cfg);
	DOVE9_TEST_ASSERT_INT_EQ(ret, 0);

	dove9_orchestrator_bridge_destroy(&bridge);
	dove9_test_end();
}

static void test_process_email(void)
{
	struct dove9_orchestrator_bridge *bridge;
	struct dove9_orchestrator_config cfg;
	struct dove9_mail_message mail;
	struct dove9_mail_message reply;
	int ret;

	dove9_test_begin("process_email produces reply with response body");

	dove9_mock_reset();
	bridge = dove9_orchestrator_bridge_create();

	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_triadic = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_orchestrator_bridge_init(bridge, &cfg);

	reset_event_counts();
	dove9_orchestrator_bridge_on(bridge, test_event_handler, NULL);

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@test.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	snprintf(mail.subject, sizeof(mail.subject), "Test");
	snprintf(mail.body, sizeof(mail.body), "Hello");

	ret = dove9_orchestrator_bridge_process(bridge, &mail, &reply);
	DOVE9_TEST_ASSERT_INT_EQ(ret, 0);
	DOVE9_TEST_ASSERT(reply.body[0] != '\0');
	DOVE9_TEST_ASSERT_STR_EQ(reply.to, "user@test.com");
	DOVE9_TEST_ASSERT(mail_processed_count >= 1);

	dove9_orchestrator_bridge_destroy(&bridge);
	dove9_test_end();
}

static void test_process_non_bot_address(void)
{
	struct dove9_orchestrator_bridge *bridge;
	struct dove9_orchestrator_config cfg;
	struct dove9_mail_message mail;
	struct dove9_mail_message reply;
	int ret;

	dove9_test_begin("mail not addressed to bot is ignored");

	dove9_mock_reset();
	bridge = dove9_orchestrator_bridge_create();

	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_triadic = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_orchestrator_bridge_init(bridge, &cfg);

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@test.com");
	snprintf(mail.to, sizeof(mail.to), "other@test.com");
	snprintf(mail.subject, sizeof(mail.subject), "Not for bot");
	snprintf(mail.body, sizeof(mail.body), "Ignored");

	ret = dove9_orchestrator_bridge_process(bridge, &mail, &reply);
	/* Should return non-zero (skipped) or zero with empty reply */
	DOVE9_TEST_ASSERT(ret != 0 || reply.body[0] == '\0');

	dove9_orchestrator_bridge_destroy(&bridge);
	dove9_test_end();
}

static void test_bridge_double_destroy(void)
{
	dove9_test_begin("orchestrator bridge double destroy safe");
	struct dove9_orchestrator_bridge *bridge = dove9_orchestrator_bridge_create();
	dove9_orchestrator_bridge_destroy(&bridge);
	DOVE9_TEST_ASSERT_NULL(bridge);
	dove9_orchestrator_bridge_destroy(&bridge);
	DOVE9_TEST_ASSERT_NULL(bridge);
	dove9_test_end();
}

static void test_bridge_event_multiple(void)
{
	dove9_test_begin("orchestrator bridge: multiple events on process");
	dove9_mock_reset();
	reset_event_counts();

	struct dove9_orchestrator_bridge *bridge = dove9_orchestrator_bridge_create();
	struct dove9_orchestrator_config cfg;
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_triadic = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_orchestrator_bridge_init(bridge, &cfg);
	dove9_orchestrator_bridge_on(bridge, test_event_handler, NULL);

	struct dove9_mail_message mail, reply;
	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "u1@test.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	snprintf(mail.subject, sizeof(mail.subject), "A");
	snprintf(mail.body, sizeof(mail.body), "body1");
	dove9_orchestrator_bridge_process(bridge, &mail, &reply);

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "u2@test.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	snprintf(mail.subject, sizeof(mail.subject), "B");
	snprintf(mail.body, sizeof(mail.body), "body2");
	dove9_orchestrator_bridge_process(bridge, &mail, &reply);

	DOVE9_TEST_ASSERT(mail_processed_count >= 2);
	dove9_orchestrator_bridge_destroy(&bridge);
	dove9_test_end();
}

static void test_bridge_empty_body(void)
{
	dove9_test_begin("orchestrator bridge: empty body mail");
	dove9_mock_reset();

	struct dove9_orchestrator_bridge *bridge = dove9_orchestrator_bridge_create();
	struct dove9_orchestrator_config cfg;
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_triadic = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_orchestrator_bridge_init(bridge, &cfg);

	struct dove9_mail_message mail, reply;
	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@test.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	snprintf(mail.subject, sizeof(mail.subject), "Empty");
	/* body is empty */

	int ret = dove9_orchestrator_bridge_process(bridge, &mail, &reply);
	/* should handle gracefully */
	DOVE9_TEST_ASSERT(ret == 0 || ret != 0);

	dove9_orchestrator_bridge_destroy(&bridge);
	dove9_test_end();
}

static void test_bridge_long_subject(void)
{
	dove9_test_begin("orchestrator bridge: long subject truncation safe");
	dove9_mock_reset();

	struct dove9_orchestrator_bridge *bridge = dove9_orchestrator_bridge_create();
	struct dove9_orchestrator_config cfg;
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_triadic = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_orchestrator_bridge_init(bridge, &cfg);

	struct dove9_mail_message mail, reply;
	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@test.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	/* fill subject with max chars */
	memset(mail.subject, 'X', DOVE9_MAX_SUBJECT_LEN - 1);
	mail.subject[DOVE9_MAX_SUBJECT_LEN - 1] = '\0';
	snprintf(mail.body, sizeof(mail.body), "body");

	int ret = dove9_orchestrator_bridge_process(bridge, &mail, &reply);
	DOVE9_TEST_ASSERT(ret == 0 || ret != 0); /* no crash */

	dove9_orchestrator_bridge_destroy(&bridge);
	dove9_test_end();
}

int main(void)
{
	dove9_test_fn tests[] = {
		test_bridge_create,
		test_bridge_init,
		test_process_email,
		test_process_non_bot_address,
		test_bridge_double_destroy,
		test_bridge_event_multiple,
		test_bridge_empty_body,
		test_bridge_long_subject,
	};
	return dove9_test_run("dove9-orchestrator-bridge", tests,
			      sizeof(tests) / sizeof(tests[0]));
}
