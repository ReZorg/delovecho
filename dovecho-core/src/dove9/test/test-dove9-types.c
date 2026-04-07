/* Copyright (c) 2024-2026 Dovecho authors, see the included COPYING file */

/* Unit tests for dove9-types.h: config defaults, context init,
   mailbox mapping, coupling bitfield helpers, enum ranges. */

#include "dove9-test-common.h"
#include "../types/dove9-types.h"

#include <string.h>

/* ---- Test: config defaults ---- */

static void test_config_default(void)
{
	struct dove9_config cfg = dove9_config_default();

	dove9_test_begin("config_default returns sane values");
	DOVE9_TEST_ASSERT(cfg.enable_triadic_loop == true);
	DOVE9_TEST_ASSERT(cfg.max_processes == DOVE9_MAX_PROCESSES);
	DOVE9_TEST_ASSERT(cfg.max_queue_depth == DOVE9_MAX_QUEUE_DEPTH);
	dove9_test_end();
}

/* ---- Test: cognitive context init ---- */

static void test_cognitive_context_init(void)
{
	struct dove9_cognitive_context ctx;
	dove9_cognitive_context_init(&ctx);

	dove9_test_begin("cognitive_context_init zeroes all fields");
	DOVE9_TEST_ASSERT_DOUBLE_EQ(ctx.salience, 0.0, 0.001);
	DOVE9_TEST_ASSERT(ctx.degraded == false);
	DOVE9_TEST_ASSERT(ctx.input[0] == '\0');
	DOVE9_TEST_ASSERT(ctx.response[0] == '\0');
	DOVE9_TEST_ASSERT(ctx.memory_context[0] == '\0');
	DOVE9_TEST_ASSERT(ctx.error[0] == '\0');
	dove9_test_end();
}

/* ---- Test: mailbox mapping defaults ---- */

static void test_mailbox_mapping_default(void)
{
	struct dove9_mailbox_mapping m = dove9_mailbox_mapping_default();

	dove9_test_begin("mailbox_mapping_default has standard folders");
	DOVE9_TEST_ASSERT_STR_EQ(m.inbox, "INBOX");
	DOVE9_TEST_ASSERT_STR_EQ(m.drafts, "Drafts");
	DOVE9_TEST_ASSERT_STR_EQ(m.sent, "Sent");
	DOVE9_TEST_ASSERT_STR_EQ(m.trash, "Trash");
	DOVE9_TEST_ASSERT_STR_EQ(m.archive, "Archive");
	DOVE9_TEST_ASSERT_STR_EQ(m.junk, "Junk");
	dove9_test_end();
}

/* ---- Test: coupling bitfield ---- */

static void test_coupling_bitfield(void)
{
	unsigned int mask = 0;

	dove9_test_begin("coupling bitfield set/is_active/clear");

	/* Initially empty */
	DOVE9_TEST_ASSERT(!dove9_coupling_is_active(mask, DOVE9_COUPLING_PERCEPTION_MEMORY));
	DOVE9_TEST_ASSERT(!dove9_coupling_is_active(mask, DOVE9_COUPLING_ASSESSMENT_PLANNING));
	DOVE9_TEST_ASSERT(!dove9_coupling_is_active(mask, DOVE9_COUPLING_BALANCED_INTEGRATION));

	/* Set one */
	dove9_coupling_set(&mask, DOVE9_COUPLING_PERCEPTION_MEMORY);
	DOVE9_TEST_ASSERT(dove9_coupling_is_active(mask, DOVE9_COUPLING_PERCEPTION_MEMORY));
	DOVE9_TEST_ASSERT(!dove9_coupling_is_active(mask, DOVE9_COUPLING_ASSESSMENT_PLANNING));

	/* Set another */
	dove9_coupling_set(&mask, DOVE9_COUPLING_BALANCED_INTEGRATION);
	DOVE9_TEST_ASSERT(dove9_coupling_is_active(mask, DOVE9_COUPLING_BALANCED_INTEGRATION));

	/* Clear first */
	dove9_coupling_clear(&mask, DOVE9_COUPLING_PERCEPTION_MEMORY);
	DOVE9_TEST_ASSERT(!dove9_coupling_is_active(mask, DOVE9_COUPLING_PERCEPTION_MEMORY));
	DOVE9_TEST_ASSERT(dove9_coupling_is_active(mask, DOVE9_COUPLING_BALANCED_INTEGRATION));

	dove9_test_end();
}

/* ---- Test: enum value ranges ---- */

static void test_enum_ranges(void)
{
	dove9_test_begin("enum value ranges are correct");

	/* 6 cognitive terms (T1,T2,T4,T5,T7,T8) */
	DOVE9_TEST_ASSERT_INT_EQ(DOVE9_TERM_T1_PERCEPTION, 0);
	DOVE9_TEST_ASSERT_INT_EQ(DOVE9_TERM_T8_BALANCED_RESPONSE, 5);

	/* 7 process states */
	DOVE9_TEST_ASSERT_INT_EQ(DOVE9_STATE_QUEUED, 0);
	DOVE9_TEST_ASSERT_INT_EQ(DOVE9_STATE_TERMINATED, 6);

	/* 3 coupling types */
	DOVE9_TEST_ASSERT_INT_EQ(DOVE9_COUPLING_PERCEPTION_MEMORY, 0);
	DOVE9_TEST_ASSERT_INT_EQ(DOVE9_COUPLING_BALANCED_INTEGRATION, 2);

	/* 2 cognitive modes */
	DOVE9_TEST_ASSERT_INT_EQ(DOVE9_MODE_EXPRESSIVE, 0);
	DOVE9_TEST_ASSERT_INT_EQ(DOVE9_MODE_REFLECTIVE, 1);

	dove9_test_end();
}

/* ---- Test: config limits are valid ---- */

static void test_config_limits_valid(void)
{
	dove9_test_begin("DOVE9_MAX constants are positive and bounded");

	DOVE9_TEST_ASSERT(DOVE9_MAX_PROCESSES > 0);
	DOVE9_TEST_ASSERT(DOVE9_MAX_PROCESSES <= 65536);
	DOVE9_TEST_ASSERT(DOVE9_MAX_QUEUE_DEPTH > 0);
	DOVE9_TEST_ASSERT(DOVE9_MAX_QUEUE_DEPTH <= 65536);

	dove9_test_end();
}

/* ---- Test: step type enum ---- */

static void test_step_type_enum(void)
{
	dove9_test_begin("step type enum has 4 values");

	DOVE9_TEST_ASSERT_INT_EQ(DOVE9_STEP_NORMAL, 0);
	DOVE9_TEST_ASSERT(DOVE9_STEP_PIVOTAL_RR > 0);
	DOVE9_TEST_ASSERT(DOVE9_STEP_TRANSITION > 0);
	DOVE9_TEST_ASSERT(DOVE9_STEP_PIVOTAL_RR != DOVE9_STEP_TRANSITION);

	dove9_test_end();
}

/* ---- Test: stream enum ---- */

static void test_stream_enum(void)
{
	dove9_test_begin("stream enum has 3 values");

	DOVE9_TEST_ASSERT_INT_EQ(DOVE9_STREAM_PRIMARY, 0);
	DOVE9_TEST_ASSERT_INT_EQ(DOVE9_STREAM_SECONDARY, 1);
	DOVE9_TEST_ASSERT_INT_EQ(DOVE9_STREAM_TERTIARY, 2);

	dove9_test_end();
}

/* ---- Test: coupling all-set ---- */

static void test_coupling_all_set(void)
{
	unsigned int mask = 0;

	dove9_test_begin("coupling bitfield supports all 3 simultaneous");

	dove9_coupling_set(&mask, DOVE9_COUPLING_PERCEPTION_MEMORY);
	dove9_coupling_set(&mask, DOVE9_COUPLING_ASSESSMENT_PLANNING);
	dove9_coupling_set(&mask, DOVE9_COUPLING_BALANCED_INTEGRATION);

	DOVE9_TEST_ASSERT(dove9_coupling_is_active(mask, DOVE9_COUPLING_PERCEPTION_MEMORY));
	DOVE9_TEST_ASSERT(dove9_coupling_is_active(mask, DOVE9_COUPLING_ASSESSMENT_PLANNING));
	DOVE9_TEST_ASSERT(dove9_coupling_is_active(mask, DOVE9_COUPLING_BALANCED_INTEGRATION));

	dove9_test_end();
}

/* ---- main ---- */

int main(void)
{
	dove9_test_fn tests[] = {
		test_config_default,
		test_cognitive_context_init,
		test_mailbox_mapping_default,
		test_coupling_bitfield,
		test_enum_ranges,
		test_config_limits_valid,
		test_step_type_enum,
		test_stream_enum,
		test_coupling_all_set,
	};
	return dove9_test_run("dove9-types", tests, 9);
}
