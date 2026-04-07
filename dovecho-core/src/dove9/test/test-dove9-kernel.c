/* Copyright (c) 2024-2026 Dovecho authors, see the included COPYING file */

/* Unit tests for dove9-kernel: process table CRUD, state transitions,
   fork, max capacity, mail protocol round-trip, metrics. */

#include "dove9-test-common.h"
#include "dove9-test-mocks.h"
#include "../core/dove9-kernel.h"
#include "../types/dove9-types.h"

#include <string.h>

static void test_kernel_create(void)
{
	struct dove9_kernel *kernel;

	dove9_test_begin("kernel create/destroy");

	kernel = dove9_kernel_create();
	DOVE9_TEST_ASSERT_NOT_NULL(kernel);
	dove9_kernel_destroy(&kernel);
	DOVE9_TEST_ASSERT_NULL(kernel);

	dove9_test_end();
}

static void test_process_create(void)
{
	struct dove9_kernel *kernel;
	struct dove9_process *proc;

	dove9_test_begin("spawn process returns non-NULL with valid pid");

	kernel = dove9_kernel_create();
	proc = dove9_kernel_spawn(kernel, "test-message", 5);
	DOVE9_TEST_ASSERT_NOT_NULL(proc);
	DOVE9_TEST_ASSERT(proc->pid > 0);
	DOVE9_TEST_ASSERT_INT_EQ(proc->state, DOVE9_PROC_READY);
	DOVE9_TEST_ASSERT_INT_EQ(proc->priority, 5);

	dove9_kernel_destroy(&kernel);
	dove9_test_end();
}

static void test_process_state_transitions(void)
{
	struct dove9_kernel *kernel;
	struct dove9_process *proc;

	dove9_test_begin("process state: READY → RUNNING → COMPLETED");

	kernel = dove9_kernel_create();
	proc = dove9_kernel_spawn(kernel, "test-msg", 5);

	DOVE9_TEST_ASSERT_INT_EQ(proc->state, DOVE9_PROC_READY);

	dove9_kernel_schedule(kernel, proc);
	DOVE9_TEST_ASSERT_INT_EQ(proc->state, DOVE9_PROC_RUNNING);

	dove9_kernel_complete(kernel, proc);
	DOVE9_TEST_ASSERT_INT_EQ(proc->state, DOVE9_PROC_COMPLETED);

	dove9_kernel_destroy(&kernel);
	dove9_test_end();
}

static void test_process_suspend_resume(void)
{
	struct dove9_kernel *kernel;
	struct dove9_process *proc;

	dove9_test_begin("process suspend and resume");

	kernel = dove9_kernel_create();
	proc = dove9_kernel_spawn(kernel, "test-msg", 5);
	dove9_kernel_schedule(kernel, proc);

	dove9_kernel_suspend(kernel, proc);
	DOVE9_TEST_ASSERT_INT_EQ(proc->state, DOVE9_PROC_WAITING);

	dove9_kernel_resume(kernel, proc);
	DOVE9_TEST_ASSERT_INT_EQ(proc->state, DOVE9_PROC_RUNNING);

	dove9_kernel_destroy(&kernel);
	dove9_test_end();
}

static void test_process_fork(void)
{
	struct dove9_kernel *kernel;
	struct dove9_process *parent, *child;

	dove9_test_begin("fork creates child with parent_pid set");

	kernel = dove9_kernel_create();
	parent = dove9_kernel_spawn(kernel, "parent-msg", 5);

	child = dove9_kernel_fork(kernel, parent, "child-msg", 3);
	DOVE9_TEST_ASSERT_NOT_NULL(child);
	DOVE9_TEST_ASSERT(child->pid != parent->pid);
	DOVE9_TEST_ASSERT_UINT_EQ(child->parent_pid, parent->pid);

	dove9_kernel_destroy(&kernel);
	dove9_test_end();
}

static void test_max_capacity(void)
{
	struct dove9_kernel *kernel;
	struct dove9_process *proc;
	unsigned int i;

	dove9_test_begin("spawn returns NULL at max capacity");

	kernel = dove9_kernel_create();

	/* Fill to capacity */
	for (i = 0; i < DOVE9_MAX_PROCESSES; i++) {
		proc = dove9_kernel_spawn(kernel, "bulk", 1);
		if (proc == NULL)
			break;
	}

	/* Next spawn should fail */
	proc = dove9_kernel_spawn(kernel, "overflow", 1);
	DOVE9_TEST_ASSERT_NULL(proc);

	dove9_kernel_destroy(&kernel);
	dove9_test_end();
}

static void test_kernel_tick(void)
{
	struct dove9_kernel *kernel;
	struct dove9_process *proc;

	dove9_test_begin("tick schedules highest priority ready process");

	kernel = dove9_kernel_create();
	dove9_kernel_spawn(kernel, "low-prio", 1);
	proc = dove9_kernel_spawn(kernel, "high-prio", 9);

	dove9_kernel_tick(kernel);

	/* High priority should be running */
	DOVE9_TEST_ASSERT_INT_EQ(proc->state, DOVE9_PROC_RUNNING);

	dove9_kernel_destroy(&kernel);
	dove9_test_end();
}

static void test_kernel_metrics(void)
{
	struct dove9_kernel *kernel;
	struct dove9_process *proc;
	struct dove9_kernel_metrics metrics;

	dove9_test_begin("metrics track spawned and active counts");

	kernel = dove9_kernel_create();
	proc = dove9_kernel_spawn(kernel, "test1", 5);
	dove9_kernel_spawn(kernel, "test2", 3);

	metrics = dove9_kernel_get_metrics(kernel);
	DOVE9_TEST_ASSERT_UINT_EQ(metrics.total_spawned, 2);
	DOVE9_TEST_ASSERT_UINT_EQ(metrics.active_count, 2);

	dove9_kernel_schedule(kernel, proc);
	dove9_kernel_complete(kernel, proc);

	metrics = dove9_kernel_get_metrics(kernel);
	DOVE9_TEST_ASSERT_UINT_EQ(metrics.completed_count, 1);

	dove9_kernel_destroy(&kernel);
	dove9_test_end();
}

static void test_process_lookup_by_pid(void)
{
	struct dove9_kernel *kernel;
	struct dove9_process *proc, *found;

	dove9_test_begin("lookup by pid returns correct process");

	kernel = dove9_kernel_create();
	proc = dove9_kernel_spawn(kernel, "find-me", 5);

	found = dove9_kernel_find(kernel, proc->pid);
	DOVE9_TEST_ASSERT_NOT_NULL(found);
	DOVE9_TEST_ASSERT_UINT_EQ(found->pid, proc->pid);

	/* Non-existent pid */
	found = dove9_kernel_find(kernel, 99999);
	DOVE9_TEST_ASSERT_NULL(found);

	dove9_kernel_destroy(&kernel);
	dove9_test_end();
}

static void test_process_terminate(void)
{
	struct dove9_kernel *kernel;
	struct dove9_process *proc;

	dove9_test_begin("terminate sets TERMINATED state");

	kernel = dove9_kernel_create();
	proc = dove9_kernel_spawn(kernel, "die", 5);
	dove9_kernel_schedule(kernel, proc);

	dove9_kernel_terminate(kernel, proc);
	DOVE9_TEST_ASSERT_INT_EQ(proc->state, DOVE9_PROC_TERMINATED);

	dove9_kernel_destroy(&kernel);
	dove9_test_end();
}

int main(void)
{
	dove9_test_fn tests[] = {
		test_kernel_create,
		test_process_create,
		test_process_state_transitions,
		test_process_suspend_resume,
		test_process_fork,
		test_max_capacity,
		test_kernel_tick,
		test_kernel_metrics,
		test_process_lookup_by_pid,
		test_process_terminate,
	};
	return dove9_test_run("dove9-kernel", tests, 10);
}
