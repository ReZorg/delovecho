/* Copyright (c) 2024-2026 Dovecho authors, see the included COPYING file */

/* Unit tests for dove9-sys6-mail-scheduler: priority-to-phase mapping,
   cycle boundaries, scheduling, FIFO fallback, capacity warnings. */

#include "dove9-test-common.h"
#include "../integration/dove9-sys6-mail-scheduler.h"
#include "../types/dove9-types.h"

#include <string.h>

static void test_scheduler_create(void)
{
	struct dove9_sys6_scheduler *sched;

	dove9_test_begin("sys6 scheduler create/destroy");

	sched = dove9_sys6_scheduler_create();
	DOVE9_TEST_ASSERT_NOT_NULL(sched);
	dove9_sys6_scheduler_destroy(&sched);
	DOVE9_TEST_ASSERT_NULL(sched);

	dove9_test_end();
}

static void test_priority_to_phase(void)
{
	dove9_test_begin("priority maps to correct phase");

	/* High priority (7-9) → phase 1 */
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_sys6_priority_to_phase(9), 1);
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_sys6_priority_to_phase(8), 1);
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_sys6_priority_to_phase(7), 1);

	/* Medium priority (4-6) → phase 2 */
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_sys6_priority_to_phase(6), 2);
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_sys6_priority_to_phase(5), 2);
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_sys6_priority_to_phase(4), 2);

	/* Low priority (1-3) → phase 3 */
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_sys6_priority_to_phase(3), 3);
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_sys6_priority_to_phase(2), 3);
	DOVE9_TEST_ASSERT_UINT_EQ(dove9_sys6_priority_to_phase(1), 3);

	dove9_test_end();
}

static void test_cycle_positions(void)
{
	struct dove9_sys6_scheduler *sched;
	struct dove9_sys6_positions pos;
	int i;

	dove9_test_begin("cycle positions computed correctly");

	sched = dove9_sys6_scheduler_create();

	/* At step 0 all positions should be at initial state */
	pos = dove9_sys6_scheduler_get_positions(sched);
	DOVE9_TEST_ASSERT_UINT_EQ(pos.dyadic_phase, 0);
	DOVE9_TEST_ASSERT_UINT_EQ(pos.triadic_phase, 0);

	/* Advance some steps */
	for (i = 0; i < 7; i++)
		dove9_sys6_scheduler_advance(sched);

	pos = dove9_sys6_scheduler_get_positions(sched);
	/* step 7: dyadic = 7%2 = 1, triadic = 7%3 = 1 */
	DOVE9_TEST_ASSERT_UINT_EQ(pos.dyadic_phase, 1);
	DOVE9_TEST_ASSERT_UINT_EQ(pos.triadic_phase, 1);

	dove9_sys6_scheduler_destroy(&sched);
	dove9_test_end();
}

static void test_cycle_boundaries(void)
{
	struct dove9_sys6_scheduler *sched;
	int sys6_completed = 0;
	int grand_completed = 0;
	int i;

	dove9_test_begin("Sys6 at 30 steps, Grand at 60 steps");

	sched = dove9_sys6_scheduler_create();

	for (i = 0; i < 60; i++) {
		dove9_sys6_scheduler_advance(sched);
		if (dove9_sys6_scheduler_is_sys6_boundary(sched))
			sys6_completed++;
		if (dove9_sys6_scheduler_is_grand_boundary(sched))
			grand_completed++;
	}

	/* 60 steps: 2 Sys6 boundaries (at 30, 60) and 1 Grand boundary (at 60) */
	DOVE9_TEST_ASSERT_UINT_EQ(sys6_completed, 2);
	DOVE9_TEST_ASSERT_UINT_EQ(grand_completed, 1);

	dove9_sys6_scheduler_destroy(&sched);
	dove9_test_end();
}

static void test_schedule_mail(void)
{
	struct dove9_sys6_scheduler *sched;
	struct dove9_sys6_slot slot;
	int ret;

	dove9_test_begin("schedule_mail assigns slot");

	sched = dove9_sys6_scheduler_create();

	ret = dove9_sys6_scheduler_enqueue(sched, "msg-001", 8, &slot);
	DOVE9_TEST_ASSERT_INT_EQ(ret, 0);
	DOVE9_TEST_ASSERT_UINT_EQ(slot.phase, 1); /* high priority → phase 1 */

	dove9_sys6_scheduler_destroy(&sched);
	dove9_test_end();
}

static void test_next_slot(void)
{
	struct dove9_sys6_scheduler *sched;
	struct dove9_sys6_slot slot;
	int ret;

	dove9_test_begin("next_slot returns enqueued item");

	sched = dove9_sys6_scheduler_create();
	dove9_sys6_scheduler_enqueue(sched, "msg-a", 5, &slot);

	ret = dove9_sys6_scheduler_next(sched, &slot);
	DOVE9_TEST_ASSERT_INT_EQ(ret, 0);
	DOVE9_TEST_ASSERT_STR_EQ(slot.message_id, "msg-a");

	/* Queue should be empty now */
	ret = dove9_sys6_scheduler_next(sched, &slot);
	DOVE9_TEST_ASSERT(ret != 0);

	dove9_sys6_scheduler_destroy(&sched);
	dove9_test_end();
}

static void test_fifo_fallback(void)
{
	struct dove9_sys6_scheduler *sched;
	struct dove9_sys6_slot slot;

	dove9_test_begin("same-priority items dequeue in FIFO order");

	sched = dove9_sys6_scheduler_create();

	dove9_sys6_scheduler_enqueue(sched, "first", 5, &slot);
	dove9_sys6_scheduler_enqueue(sched, "second", 5, &slot);
	dove9_sys6_scheduler_enqueue(sched, "third", 5, &slot);

	dove9_sys6_scheduler_next(sched, &slot);
	DOVE9_TEST_ASSERT_STR_EQ(slot.message_id, "first");

	dove9_sys6_scheduler_next(sched, &slot);
	DOVE9_TEST_ASSERT_STR_EQ(slot.message_id, "second");

	dove9_sys6_scheduler_next(sched, &slot);
	DOVE9_TEST_ASSERT_STR_EQ(slot.message_id, "third");

	dove9_sys6_scheduler_destroy(&sched);
	dove9_test_end();
}

int main(void)
{
	dove9_test_fn tests[] = {
		test_scheduler_create,
		test_priority_to_phase,
		test_cycle_positions,
		test_cycle_boundaries,
		test_schedule_mail,
		test_next_slot,
		test_fifo_fallback,
	};
	return dove9_test_run("dove9-sys6-scheduler", tests, 7);
}
