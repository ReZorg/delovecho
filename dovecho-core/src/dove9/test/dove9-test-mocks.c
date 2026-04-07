/* Copyright (c) 2024-2026 Dovecho authors, see the included COPYING file */

#include "dove9-test-mocks.h"

#include <stdio.h>
#include <string.h>

/* ---- Call counters ---- */

unsigned int dove9_mock_llm_call_count = 0;
unsigned int dove9_mock_llm_parallel_call_count = 0;
unsigned int dove9_mock_memory_store_count = 0;
unsigned int dove9_mock_memory_recent_count = 0;
unsigned int dove9_mock_memory_relevant_count = 0;
unsigned int dove9_mock_persona_personality_count = 0;
unsigned int dove9_mock_persona_emotion_count = 0;
unsigned int dove9_mock_persona_update_count = 0;

/* ---- LLM Service Mock ---- */

static int mock_generate_response(void *ctx, const char *prompt,
				  const char *system_prompt,
				  char *out, unsigned int out_len)
{
	(void)ctx;
	(void)system_prompt;
	dove9_mock_llm_call_count++;
	snprintf(out, out_len, "Echo: %s", prompt ? prompt : "");
	return 0;
}

static int mock_generate_parallel_response(void *ctx,
					   const char **prompts,
					   unsigned int count,
					   char **outs,
					   unsigned int out_len)
{
	unsigned int i;
	(void)ctx;
	dove9_mock_llm_parallel_call_count++;
	for (i = 0; i < count; i++)
		snprintf(outs[i], out_len, "Echo[%u]: %s", i,
			 prompts[i] ? prompts[i] : "");
	return 0;
}

/* ---- Memory Store Mock ---- */

static int mock_store(void *ctx, const char *key,
		      const char *content, double importance)
{
	(void)ctx;
	(void)key;
	(void)content;
	(void)importance;
	dove9_mock_memory_store_count++;
	return 0;
}

static int mock_retrieve_recent(void *ctx, unsigned int count,
				char *out, unsigned int out_len)
{
	(void)ctx;
	(void)count;
	dove9_mock_memory_recent_count++;
	snprintf(out, out_len, "no recent memories");
	return 0;
}

static int mock_retrieve_relevant(void *ctx, const char *query,
				  unsigned int count,
				  char *out, unsigned int out_len)
{
	(void)ctx;
	(void)count;
	dove9_mock_memory_relevant_count++;
	snprintf(out, out_len, "relevant: %s", query ? query : "");
	return 0;
}

/* ---- Persona Core Mock ---- */

static int mock_get_personality(void *ctx, char *out, unsigned int out_len)
{
	(void)ctx;
	dove9_mock_persona_personality_count++;
	snprintf(out, out_len, "curious");
	return 0;
}

static int mock_get_dominant_emotion(void *ctx, char *out,
				     unsigned int out_len)
{
	(void)ctx;
	dove9_mock_persona_emotion_count++;
	snprintf(out, out_len, "neutral");
	return 0;
}

static int mock_update_emotional_state(void *ctx, const char *input,
				       double salience)
{
	(void)ctx;
	(void)input;
	(void)salience;
	dove9_mock_persona_update_count++;
	return 0;
}

/* ---- Vtable instances ---- */

struct dove9_llm_service dove9_mock_llm = {
	.context = NULL,
	.generate_response = mock_generate_response,
	.generate_parallel_response = mock_generate_parallel_response,
};

struct dove9_memory_store dove9_mock_memory = {
	.context = NULL,
	.store = mock_store,
	.retrieve_recent = mock_retrieve_recent,
	.retrieve_relevant = mock_retrieve_relevant,
};

struct dove9_persona_core dove9_mock_persona = {
	.context = NULL,
	.get_personality = mock_get_personality,
	.get_dominant_emotion = mock_get_dominant_emotion,
	.update_emotional_state = mock_update_emotional_state,
};

/* ---- Reset ---- */

void dove9_mock_reset(void)
{
	dove9_mock_llm_call_count = 0;
	dove9_mock_llm_parallel_call_count = 0;
	dove9_mock_memory_store_count = 0;
	dove9_mock_memory_recent_count = 0;
	dove9_mock_memory_relevant_count = 0;
	dove9_mock_persona_personality_count = 0;
	dove9_mock_persona_emotion_count = 0;
	dove9_mock_persona_update_count = 0;
}
