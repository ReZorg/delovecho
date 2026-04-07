/* Copyright (c) 2024-2026 Dovecho authors, see the included COPYING file */

/* Unit tests for dove9-mail-protocol-bridge: mail/process conversion,
   flag/state mapping, priority calculation, body truncation. */

#include "dove9-test-common.h"
#include "../integration/dove9-mail-protocol-bridge.h"
#include "../types/dove9-types.h"

#include <string.h>

static void test_bridge_create(void)
{
	struct dove9_mail_bridge *bridge;

	dove9_test_begin("mail bridge create/destroy");

	bridge = dove9_mail_bridge_create();
	DOVE9_TEST_ASSERT_NOT_NULL(bridge);
	dove9_mail_bridge_destroy(&bridge);
	DOVE9_TEST_ASSERT_NULL(bridge);

	dove9_test_end();
}

static void test_mail_to_process(void)
{
	struct dove9_mail_bridge *bridge;
	struct dove9_mail_message mail;
	struct dove9_process_request req;

	dove9_test_begin("mail_to_process extracts subject and body");

	bridge = dove9_mail_bridge_create();

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@example.com");
	snprintf(mail.to, sizeof(mail.to), "bot@example.com");
	snprintf(mail.subject, sizeof(mail.subject), "Hello Bot");
	snprintf(mail.body, sizeof(mail.body), "Please help me");

	dove9_mail_to_process(bridge, &mail, &req);

	DOVE9_TEST_ASSERT_STR_EQ(req.sender, "user@example.com");
	DOVE9_TEST_ASSERT(strlen(req.body) > 0);
	DOVE9_TEST_ASSERT(req.priority > 0);

	dove9_mail_bridge_destroy(&bridge);
	dove9_test_end();
}

static void test_process_to_mail(void)
{
	struct dove9_mail_bridge *bridge;
	struct dove9_process_result result;
	struct dove9_mail_message reply;

	dove9_test_begin("process_to_mail has Re: prefix and swapped from/to");

	bridge = dove9_mail_bridge_create();

	memset(&result, 0, sizeof(result));
	snprintf(result.original_from, sizeof(result.original_from), "user@example.com");
	snprintf(result.original_to, sizeof(result.original_to), "bot@example.com");
	snprintf(result.original_subject, sizeof(result.original_subject), "Hello Bot");
	snprintf(result.response, sizeof(result.response), "I can help");

	dove9_process_to_mail(bridge, &result, &reply);

	DOVE9_TEST_ASSERT_STR_EQ(reply.from, "bot@example.com");
	DOVE9_TEST_ASSERT_STR_EQ(reply.to, "user@example.com");
	/* Subject should have Re: prefix */
	DOVE9_TEST_ASSERT(strncmp(reply.subject, "Re: ", 4) == 0);

	dove9_mail_bridge_destroy(&bridge);
	dove9_test_end();
}

static void test_flag_state_mapping(void)
{
	dove9_test_begin("mail flags map to process states");

	/* SEEN → COMPLETED, FLAGGED → RUNNING, ANSWERED → COMPLETED, default → READY */
	DOVE9_TEST_ASSERT_INT_EQ(
		dove9_mail_flag_to_state(DOVE9_MAIL_FLAG_SEEN),
		DOVE9_PROC_COMPLETED);
	DOVE9_TEST_ASSERT_INT_EQ(
		dove9_mail_flag_to_state(DOVE9_MAIL_FLAG_FLAGGED),
		DOVE9_PROC_RUNNING);
	DOVE9_TEST_ASSERT_INT_EQ(
		dove9_mail_flag_to_state(DOVE9_MAIL_FLAG_ANSWERED),
		DOVE9_PROC_COMPLETED);
	DOVE9_TEST_ASSERT_INT_EQ(
		dove9_mail_flag_to_state(DOVE9_MAIL_FLAG_NONE),
		DOVE9_PROC_READY);

	dove9_test_end();
}

static void test_priority_calculation(void)
{
	dove9_test_begin("priority from flags: FLAGGED=9, RECENT=7, default=5");

	DOVE9_TEST_ASSERT_INT_EQ(dove9_mail_priority(DOVE9_MAIL_FLAG_FLAGGED), 9);
	DOVE9_TEST_ASSERT_INT_EQ(dove9_mail_priority(DOVE9_MAIL_FLAG_RECENT), 7);
	DOVE9_TEST_ASSERT_INT_EQ(dove9_mail_priority(DOVE9_MAIL_FLAG_NONE), 5);

	dove9_test_end();
}

static void test_cognitive_context_creation(void)
{
	struct dove9_mail_bridge *bridge;
	struct dove9_mail_message mail;
	struct dove9_cognitive_context ctx;

	dove9_test_begin("mail creates cognitive context with salience");

	bridge = dove9_mail_bridge_create();

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@example.com");
	snprintf(mail.subject, sizeof(mail.subject), "Urgent");
	snprintf(mail.body, sizeof(mail.body), "Please respond");
	mail.flags = DOVE9_MAIL_FLAG_FLAGGED;

	dove9_mail_to_cognitive(bridge, &mail, &ctx);

	DOVE9_TEST_ASSERT(ctx.salience > 0.0);
	DOVE9_TEST_ASSERT(ctx.input[0] != '\0');
	DOVE9_TEST_ASSERT(!ctx.degraded);

	dove9_mail_bridge_destroy(&bridge);
	dove9_test_end();
}

static void test_empty_body_handling(void)
{
	struct dove9_mail_bridge *bridge;
	struct dove9_mail_message mail;
	struct dove9_process_request req;

	dove9_test_begin("empty mail body produces valid request");

	bridge = dove9_mail_bridge_create();

	memset(&mail, 0, sizeof(mail));
	snprintf(mail.from, sizeof(mail.from), "user@example.com");
	snprintf(mail.to, sizeof(mail.to), "bot@example.com");
	snprintf(mail.subject, sizeof(mail.subject), "Empty");
	mail.body[0] = '\0';

	dove9_mail_to_process(bridge, &mail, &req);

	DOVE9_TEST_ASSERT(req.priority > 0);
	DOVE9_TEST_ASSERT_STR_EQ(req.sender, "user@example.com");

	dove9_mail_bridge_destroy(&bridge);
	dove9_test_end();
}

int main(void)
{
	dove9_test_fn tests[] = {
		test_bridge_create,
		test_mail_to_process,
		test_process_to_mail,
		test_flag_state_mapping,
		test_priority_calculation,
		test_cognitive_context_creation,
		test_empty_body_handling,
	};
	return dove9_test_run("dove9-mail-bridge", tests, 7);
}
