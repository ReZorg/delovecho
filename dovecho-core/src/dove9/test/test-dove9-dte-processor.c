/* Copyright (c) 2024-2026 Dovecho authors, see the included COPYING file */

/* Unit tests for dove9-dte-processor: creation, cognitive vtable dispatch,
   T-function routing, mock call counters, destroy semantics. */

#include "dove9-test-common.h"
#include "dove9-test-mocks.h"
#include "../cognitive/dove9-dte-processor.h"

#include <string.h>

static void test_dte_processor_create(void)
{
	struct dove9_dte_processor_config cfg = {
		.enable_parallel_cognition = false,
		.memory_retrieval_count = 5,
		.salience_threshold = 0.2,
	};
	struct dove9_dte_processor *dte;

	dove9_test_begin("create returns non-NULL");

	dte = dove9_dte_processor_create(&cfg, &dove9_mock_llm,
					 &dove9_mock_memory, &dove9_mock_persona);
	DOVE9_TEST_ASSERT_NOT_NULL(dte);
	dove9_dte_processor_destroy(&dte);
	DOVE9_TEST_ASSERT_NULL(dte);

	dove9_test_end();
}

static void test_as_cognitive_vtable(void)
{
	struct dove9_dte_processor_config cfg = {
		.enable_parallel_cognition = false,
		.memory_retrieval_count = 3,
		.salience_threshold = 0.1,
	};
	struct dove9_dte_processor *dte;
	struct dove9_cognitive_processor proc;

	dove9_test_begin("as_cognitive returns 6 non-NULL function pointers");

	dte = dove9_dte_processor_create(&cfg, &dove9_mock_llm,
					 &dove9_mock_memory, &dove9_mock_persona);
	proc = dove9_dte_processor_as_cognitive(dte);

	DOVE9_TEST_ASSERT_NOT_NULL(proc.process_t1_perception);
	DOVE9_TEST_ASSERT_NOT_NULL(proc.process_t2_idea_formation);
	DOVE9_TEST_ASSERT_NOT_NULL(proc.process_t4_sensory_input);
	DOVE9_TEST_ASSERT_NOT_NULL(proc.process_t5_action_sequence);
	DOVE9_TEST_ASSERT_NOT_NULL(proc.process_t7_memory_encoding);
	DOVE9_TEST_ASSERT_NOT_NULL(proc.process_t8_balanced_response);

	dove9_dte_processor_destroy(&dte);
	dove9_test_end();
}

static void test_t1_perception_dispatch(void)
{
	struct dove9_dte_processor_config cfg = {
		.enable_parallel_cognition = false,
		.memory_retrieval_count = 3,
		.salience_threshold = 0.1,
	};
	struct dove9_dte_processor *dte;
	struct dove9_cognitive_processor proc;
	struct dove9_cognitive_context ctx;

	dove9_test_begin("T1 dispatch calls memory retrieve_relevant");

	dove9_mock_reset();
	dove9_cognitive_context_init(&ctx);
	snprintf(ctx.input, sizeof(ctx.input), "test perception");
	ctx.salience = 0.5;

	dte = dove9_dte_processor_create(&cfg, &dove9_mock_llm,
					 &dove9_mock_memory, &dove9_mock_persona);
	proc = dove9_dte_processor_as_cognitive(dte);
	proc.process_t1_perception(proc.context, &ctx, DOVE9_MODE_REFLECTIVE);

	DOVE9_TEST_ASSERT(dove9_mock_memory_retrieve_relevant_calls > 0);

	dove9_dte_processor_destroy(&dte);
	dove9_test_end();
}

static void test_t2_idea_formation_dispatch(void)
{
	struct dove9_dte_processor_config cfg = {
		.enable_parallel_cognition = false,
		.memory_retrieval_count = 3,
		.salience_threshold = 0.1,
	};
	struct dove9_dte_processor *dte;
	struct dove9_cognitive_processor proc;
	struct dove9_cognitive_context ctx;

	dove9_test_begin("T2 dispatch calls LLM generate_response");

	dove9_mock_reset();
	dove9_cognitive_context_init(&ctx);
	snprintf(ctx.input, sizeof(ctx.input), "test idea");
	ctx.salience = 0.5;

	dte = dove9_dte_processor_create(&cfg, &dove9_mock_llm,
					 &dove9_mock_memory, &dove9_mock_persona);
	proc = dove9_dte_processor_as_cognitive(dte);
	proc.process_t2_idea_formation(proc.context, &ctx, DOVE9_MODE_EXPRESSIVE);

	DOVE9_TEST_ASSERT(dove9_mock_llm_generate_calls > 0);

	dove9_dte_processor_destroy(&dte);
	dove9_test_end();
}

static void test_t7_memory_encoding_stores(void)
{
	struct dove9_dte_processor_config cfg = {
		.enable_parallel_cognition = false,
		.memory_retrieval_count = 3,
		.salience_threshold = 0.1,
	};
	struct dove9_dte_processor *dte;
	struct dove9_cognitive_processor proc;
	struct dove9_cognitive_context ctx;

	dove9_test_begin("T7 dispatch calls memory store");

	dove9_mock_reset();
	dove9_cognitive_context_init(&ctx);
	snprintf(ctx.input, sizeof(ctx.input), "remember this");
	snprintf(ctx.response, sizeof(ctx.response), "I will remember");
	ctx.salience = 0.5;

	dte = dove9_dte_processor_create(&cfg, &dove9_mock_llm,
					 &dove9_mock_memory, &dove9_mock_persona);
	proc = dove9_dte_processor_as_cognitive(dte);
	proc.process_t7_memory_encoding(proc.context, &ctx, DOVE9_MODE_REFLECTIVE);

	DOVE9_TEST_ASSERT(dove9_mock_memory_store_calls > 0);

	dove9_dte_processor_destroy(&dte);
	dove9_test_end();
}

static void test_low_salience_skips(void)
{
	struct dove9_dte_processor_config cfg = {
		.enable_parallel_cognition = false,
		.memory_retrieval_count = 3,
		.salience_threshold = 0.5,
	};
	struct dove9_dte_processor *dte;
	struct dove9_cognitive_processor proc;
	struct dove9_cognitive_context ctx;

	dove9_test_begin("low salience context is not processed");

	dove9_mock_reset();
	dove9_cognitive_context_init(&ctx);
	snprintf(ctx.input, sizeof(ctx.input), "very low salience");
	ctx.salience = 0.01;

	dte = dove9_dte_processor_create(&cfg, &dove9_mock_llm,
					 &dove9_mock_memory, &dove9_mock_persona);
	proc = dove9_dte_processor_as_cognitive(dte);
	proc.process_t2_idea_formation(proc.context, &ctx, DOVE9_MODE_EXPRESSIVE);

	/* With salience below threshold, LLM should not be called */
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_mock_llm_generate_calls, 0);

	dove9_dte_processor_destroy(&dte);
	dove9_test_end();
}

int main(void)
{
	dove9_test_fn tests[] = {
		test_dte_processor_create,
		test_as_cognitive_vtable,
		test_t1_perception_dispatch,
		test_t2_idea_formation_dispatch,
		test_t7_memory_encoding_stores,
		test_low_salience_skips,
	};
	return dove9_test_run("dove9-dte-processor", tests, 6);
}
