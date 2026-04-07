/* Copyright (c) 2024-2026 Dovecho authors, see the included COPYING file */

/* End-to-end integration test: exercises the full cognitive pipeline
   from mail arrival through triadic processing to reply generation.
   Validates the complete Dove9 "Everything is a Chatbot" data flow. */

#include "dove9-test-common.h"
#include "dove9-test-mocks.h"
#include "../dove9-system.h"
#include "../types/dove9-types.h"
#include "../core/dove9-kernel.h"
#include "../integration/dove9-mail-protocol-bridge.h"
#include "../integration/dove9-sys6-mail-scheduler.h"

#include <string.h>

/* ---- Full pipeline: mail → kernel → triadic → reply ---- */

static void test_full_pipeline(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	struct dove9_mail_message inbound, reply;
	int ret;

	dove9_test_begin("full pipeline: mail → cognitive → reply");

	dove9_mock_reset();

	sys = dove9_system_create();
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "echo@dove9.local");
	cfg.enable_triadic = true;
	cfg.enable_sys6 = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_system_init(sys, &cfg);
	dove9_system_start(sys);

	memset(&inbound, 0, sizeof(inbound));
	snprintf(inbound.from, sizeof(inbound.from), "alice@example.com");
	snprintf(inbound.to, sizeof(inbound.to), "echo@dove9.local");
	snprintf(inbound.subject, sizeof(inbound.subject), "Philosophy question");
	snprintf(inbound.body, sizeof(inbound.body),
		 "What is the relationship between perception and memory?");
	inbound.flags = DOVE9_MAIL_FLAG_RECENT;

	ret = dove9_system_process_mail(sys, &inbound, &reply);

	DOVE9_TEST_ASSERT_INT_EQ(ret, 0);
	DOVE9_TEST_ASSERT(reply.body[0] != '\0');
	DOVE9_TEST_ASSERT_STR_EQ(reply.to, "alice@example.com");
	DOVE9_TEST_ASSERT_STR_EQ(reply.from, "echo@dove9.local");
	DOVE9_TEST_ASSERT(strncmp(reply.subject, "Re:", 3) == 0);

	/* Verify cognitive services were invoked */
	DOVE9_TEST_ASSERT(dove9_mock_llm_generate_calls > 0);
	DOVE9_TEST_ASSERT(dove9_mock_memory_retrieve_relevant_calls > 0);
	DOVE9_TEST_ASSERT(dove9_mock_memory_store_calls > 0);

	dove9_system_stop(sys);
	dove9_system_destroy(&sys);
	dove9_test_end();
}

/* ---- Multiple users, concurrent-like processing ---- */

static void test_multi_user_pipeline(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	struct dove9_mail_message mail, reply;
	const char *users[] = {
		"alice@example.com", "bob@example.com", "carol@example.com"
	};
	int i;

	dove9_test_begin("multi-user pipeline: 3 users get replies");

	dove9_mock_reset();

	sys = dove9_system_create();
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "echo@dove9.local");
	cfg.enable_triadic = true;
	cfg.enable_sys6 = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_system_init(sys, &cfg);
	dove9_system_start(sys);

	for (i = 0; i < 3; i++) {
		memset(&mail, 0, sizeof(mail));
		snprintf(mail.from, sizeof(mail.from), "%s", users[i]);
		snprintf(mail.to, sizeof(mail.to), "echo@dove9.local");
		snprintf(mail.subject, sizeof(mail.subject), "Q from user %d", i);
		snprintf(mail.body, sizeof(mail.body), "Hello from %s", users[i]);

		dove9_system_process_mail(sys, &mail, &reply);
		DOVE9_TEST_ASSERT(reply.body[0] != '\0');
		DOVE9_TEST_ASSERT_STR_EQ(reply.to, users[i]);
	}

	/* Each user should have triggered LLM calls */
	DOVE9_TEST_ASSERT(dove9_mock_llm_generate_calls >= 3);

	dove9_system_stop(sys);
	dove9_system_destroy(&sys);
	dove9_test_end();
}

/* ---- Mail bridge + kernel round-trip ---- */

static void test_bridge_kernel_roundtrip(void)
{
	struct dove9_mail_bridge *bridge;
	struct dove9_kernel *kernel;
	struct dove9_mail_message mail;
	struct dove9_process_request req;
	struct dove9_process *proc;

	dove9_test_begin("mail → bridge → kernel → process creation");

	bridge = dove9_mail_bridge_create();
	kernel = dove9_kernel_create();

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@test.com");
	snprintf(mail.to, sizeof(mail.to), "bot@test.com");
	snprintf(mail.subject, sizeof(mail.subject), "Integration");
	snprintf(mail.body, sizeof(mail.body), "Full path test");
	mail.flags = DOVE9_MAIL_FLAG_FLAGGED;

	dove9_mail_to_process(bridge, &mail, &req);
	proc = dove9_kernel_spawn(kernel, req.body, req.priority);

	DOVE9_TEST_ASSERT_NOT_NULL(proc);
	DOVE9_TEST_ASSERT(proc->priority >= 7); /* FLAGGED = high priority */

	dove9_kernel_destroy(&kernel);
	dove9_mail_bridge_destroy(&bridge);
	dove9_test_end();
}

/* ---- Sys6 scheduler + mail bridge integration ---- */

static void test_sys6_mail_scheduling(void)
{
	struct dove9_sys6_scheduler *sched;
	struct dove9_mail_bridge *bridge;
	struct dove9_mail_message mails[3];
	struct dove9_process_request req;
	struct dove9_sys6_slot slot;
	int i;

	dove9_test_begin("Sys6 scheduler prioritizes flagged mail");

	sched = dove9_sys6_scheduler_create();
	bridge = dove9_mail_bridge_create();

	/* 3 mails with different priorities */
	for (i = 0; i < 3; i++) {
		memset(&mails[i], 0, sizeof(mails[i]));
		snprintf(mails[i].from, sizeof(mails[i].from), "user%d@test.com", i);
		snprintf(mails[i].to, sizeof(mails[i].to), "bot@test.com");
		snprintf(mails[i].body, sizeof(mails[i].body), "Mail %d", i);
	}
	mails[0].flags = DOVE9_MAIL_FLAG_NONE;    /* low */
	mails[1].flags = DOVE9_MAIL_FLAG_FLAGGED;  /* high */
	mails[2].flags = DOVE9_MAIL_FLAG_RECENT;   /* medium */

	for (i = 0; i < 3; i++) {
		char msg_id[32];
		snprintf(msg_id, sizeof(msg_id), "msg-%d", i);
		dove9_mail_to_process(bridge, &mails[i], &req);
		dove9_sys6_scheduler_enqueue(sched, msg_id, req.priority, &slot);
	}

	/* First dequeued should be highest priority */
	dove9_sys6_scheduler_next(sched, &slot);
	DOVE9_TEST_ASSERT_STR_EQ(slot.message_id, "msg-1"); /* FLAGGED */

	dove9_sys6_scheduler_destroy(&sched);
	dove9_mail_bridge_destroy(&bridge);
	dove9_test_end();
}

/* ---- Degraded context propagation ---- */

static void test_degraded_context_pipeline(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	struct dove9_mail_message mail, reply;

	dove9_test_begin("degraded context still produces reply");

	dove9_mock_reset();

	sys = dove9_system_create();
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "echo@dove9.local");
	cfg.enable_triadic = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_system_init(sys, &cfg);
	dove9_system_start(sys);

	/* Empty body = low-quality input */
	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "tester@test.com");
	snprintf(mail.to, sizeof(mail.to), "echo@dove9.local");
	mail.body[0] = '\0';

	dove9_system_process_mail(sys, &mail, &reply);
	/* Should still produce some reply, even minimal */
	DOVE9_TEST_ASSERT(reply.body[0] != '\0' || reply.subject[0] != '\0');

	dove9_system_stop(sys);
	dove9_system_destroy(&sys);
	dove9_test_end();
}

/* ---- Memory accumulation across messages ---- */

static void test_memory_accumulation(void)
{
	struct dove9_system *sys;
	struct dove9_system_config cfg;
	struct dove9_mail_message mail, reply;
	unsigned int stores_after_1, stores_after_3;
	int i;

	dove9_test_begin("memory stores accumulate across messages");

	dove9_mock_reset();

	sys = dove9_system_create();
	memset(&cfg, 0, sizeof(cfg));
	snprintf(cfg.bot_address, sizeof(cfg.bot_address), "echo@dove9.local");
	cfg.enable_triadic = true;
	cfg.llm = &dove9_mock_llm;
	cfg.memory = &dove9_mock_memory;
	cfg.persona = &dove9_mock_persona;
	dove9_system_init(sys, &cfg);
	dove9_system_start(sys);

	/* Send 1 message */
	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@test.com");
	snprintf(mail.to, sizeof(mail.to), "echo@dove9.local");
	snprintf(mail.body, sizeof(mail.body), "Message 1");
	dove9_system_process_mail(sys, &mail, &reply);
	stores_after_1 = dove9_mock_memory_store_calls;

	/* Send 2 more */
	for (i = 2; i <= 3; i++) {
		snprintf(mail.body, sizeof(mail.body), "Message %d", i);
		dove9_system_process_mail(sys, &mail, &reply);
	}
	stores_after_3 = dove9_mock_memory_store_calls;

	/* More messages = more memory stores */
	DOVE9_TEST_ASSERT(stores_after_3 > stores_after_1);

	dove9_system_stop(sys);
	dove9_system_destroy(&sys);
	dove9_test_end();
}

int main(void)
{
	dove9_test_fn tests[] = {
		test_full_pipeline,
		test_multi_user_pipeline,
		test_bridge_kernel_roundtrip,
		test_sys6_mail_scheduling,
		test_degraded_context_pipeline,
		test_memory_accumulation,
	};
	return dove9_test_run("dove9-integration", tests, 6);
}
