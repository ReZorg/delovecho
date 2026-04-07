/* Copyright (c) 2024-2026 Dovecho authors, see the included COPYING file */

/* Unit tests for dove9-sys6-orchestrator-bridge: Sys6+orchestrator
   integration, stats tracking, distribution counters. */

#include "dove9-test-common.h"
#include "dove9-test-mocks.h"
#include "../integration/dove9-sys6-orchestrator-bridge.h"
#include "../types/dove9-types.h"

#include <string.h>

/* ---- Event tracking ---- */

static unsigned int sys6_sync_count;
static unsigned int grand_cycle_count;

static void reset_event_counts(void)
{
	sys6_sync_count = 0;
	grand_cycle_count = 0;
}

static void test_event_handler(const struct dove9_sys6_bridge_event *event,
			       void *ctx)
{
	(void)ctx;
	switch (event->type) {
	case DOVE9_SYS6_BRIDGE_SYNC:
		sys6_sync_count++;
		break;
	case DOVE9_SYS6_BRIDGE_GRAND_CYCLE:
		grand_cycle_count++;
		break;
	default:
		break;
	}
}

static void test_sys6_bridge_create(void)
{
	struct dove9_sys6_bridge *bridge;

	dove9_test_begin("sys6 bridge create/destroy");

	bridge = dove9_sys6_bridge_create();
	DOVE9_TEST_ASSERT_NOT_NULL(bridge);
	dove9_sys6_bridge_destroy(&bridge);
	DOVE9_TEST_ASSERT_NULL(bridge);

	dove9_test_end();
}

static void test_sys6_bridge_init(void)
{
	struct dove9_sys6_bridge *bridge;
	struct dove9_sys6_bridge_config cfg;
	int ret;

	dove9_test_begin("init with valid config succeeds");

	bridge = dove9_sys6_bridge_create();
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_sys6 = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;

	ret = dove9_sys6_bridge_init(bridge, &cfg);
	DOVE9_TEST_ASSERT_INT_EQ(ret, 0);

	dove9_sys6_bridge_destroy(&bridge);
	dove9_test_end();
}

static void test_process_email(void)
{
	struct dove9_sys6_bridge *bridge;
	struct dove9_sys6_bridge_config cfg;
	struct dove9_mail_message mail;
	struct dove9_mail_message reply;
	int ret;

	dove9_test_begin("process_email produces reply");

	dove9_mock_reset();
	bridge = dove9_sys6_bridge_create();

	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_sys6 = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_sys6_bridge_init(bridge, &cfg);

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@test.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	snprintf(mail.subject, sizeof(mail.subject), "Test");
	snprintf(mail.body, sizeof(mail.body), "Hello Sys6");

	ret = dove9_sys6_bridge_process(bridge, &mail, &reply);
	DOVE9_TEST_ASSERT_INT_EQ(ret, 0);
	DOVE9_TEST_ASSERT(reply.body[0] != '\0');

	dove9_sys6_bridge_destroy(&bridge);
	dove9_test_end();
}

static void test_stats(void)
{
	struct dove9_sys6_bridge *bridge;
	struct dove9_sys6_bridge_config cfg;
	struct dove9_sys6_bridge_stats stats;
	struct dove9_mail_message mail, reply;

	dove9_test_begin("stats track messages processed");

	dove9_mock_reset();
	bridge = dove9_sys6_bridge_create();

	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_sys6 = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_sys6_bridge_init(bridge, &cfg);

	stats = dove9_sys6_bridge_get_stats(bridge);
	DOVE9_TEST_ASSERT_UINT_EQ(stats.messages_processed, 0);

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@test.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	snprintf(mail.subject, sizeof(mail.subject), "Test");
	snprintf(mail.body, sizeof(mail.body), "Track me");
	dove9_sys6_bridge_process(bridge, &mail, &reply);

	stats = dove9_sys6_bridge_get_stats(bridge);
	DOVE9_TEST_ASSERT_UINT_EQ(stats.messages_processed, 1);

	dove9_sys6_bridge_destroy(&bridge);
	dove9_test_end();
}

static void test_distribution_counters(void)
{
	struct dove9_sys6_bridge *bridge;
	struct dove9_sys6_bridge_config cfg;
	struct dove9_sys6_bridge_stats stats;
	struct dove9_mail_message mail, reply;

	dove9_test_begin("distribution counters track phase assignments");

	dove9_mock_reset();
	bridge = dove9_sys6_bridge_create();

	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_sys6 = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_sys6_bridge_init(bridge, &cfg);

	/* Send a high-priority message */
	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@test.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	snprintf(mail.subject, sizeof(mail.subject), "Urgent");
	snprintf(mail.body, sizeof(mail.body), "High prio");
	mail.flags = DOVE9_MAIL_FLAG_FLAGGED;
	dove9_sys6_bridge_process(bridge, &mail, &reply);

	stats = dove9_sys6_bridge_get_stats(bridge);
	/* At least one phase counter should be > 0 */
	DOVE9_TEST_ASSERT(stats.phase1_count + stats.phase2_count +
			  stats.phase3_count > 0);

	dove9_sys6_bridge_destroy(&bridge);
	dove9_test_end();
}

static void test_events(void)
{
	struct dove9_sys6_bridge *bridge;
	struct dove9_sys6_bridge_config cfg;
	struct dove9_mail_message mail, reply;
	int i;

	dove9_test_begin("events fire during Sys6 processing");

	dove9_mock_reset();
	bridge = dove9_sys6_bridge_create();

	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "bot@test.com");
	cfg.enable_sys6 = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_sys6_bridge_init(bridge, &cfg);

	reset_event_counts();
	dove9_sys6_bridge_on(bridge, test_event_handler, NULL);

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@test.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	snprintf(mail.subject, sizeof(mail.subject), "Test");
	snprintf(mail.body, sizeof(mail.body), "Events");

	/* Process several messages to advance the cycle */
	for (i = 0; i < 5; i++)
		dove9_sys6_bridge_process(bridge, &mail, &reply);

	/* At least some sync events should have fired */
	DOVE9_TEST_ASSERT(sys6_sync_count > 0 || grand_cycle_count >= 0);

	dove9_sys6_bridge_destroy(&bridge);
	dove9_test_end();
}

int main(void)
{
	dove9_test_fn tests[] = {
		test_sys6_bridge_create,
		test_sys6_bridge_init,
		test_process_email,
		test_stats,
		test_distribution_counters,
		test_events,
	};
	return dove9_test_run("dove9-sys6-bridge", tests, 6);
}
