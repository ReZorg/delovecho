---
goal: "Build & Test Infrastructure for dovecho-core C Cognitive Layer"
version: 1.0
date_created: 2026-04-07
last_updated: 2026-04-10
owner: DeLovEcho Architecture Team
status: 'Completed'
tags: [infrastructure, architecture, dovecho-core, c, autotools, testing, ci]
---

# Introduction

![Status: Completed](https://img.shields.io/badge/status-Completed-brightgreen)

This plan establishes the complete build, test, and CI infrastructure for the Dove9 C cognitive layer (`dovecho-core/src/dove9-*`). The layer currently exists as 9 `.c` files and 10 `.h` files with a standalone `dove9-Makefile.am`, but is not yet wired into the Dovecho Autotools build system, has no C test harness, and is absent from the CI pipeline. This plan delivers: (1) full Autotools integration so `libdove9.la` builds as part of `make`, (2) a self-contained C unit test suite following the existing Dovecot `test-common.h` pattern, (3) Valgrind-clean validation, (4) `gcov`/`lcov` coverage reporting, and (5) a GitHub Actions CI job for the C layer on the `dovecho-core` branch.

## 1. Requirements & Constraints

- **REQ-001**: `libdove9.la` SHALL build as part of the standard `./configure && make` flow in `dovecho-core/`.
- **REQ-002**: `make check` SHALL execute all Dove9 C unit tests and report pass/fail via the existing `run-test.sh` Valgrind wrapper.
- **REQ-003**: Unit tests SHALL cover all 9 modules: types, logger, triadic-engine, dte-processor, kernel, mail-protocol-bridge, orchestrator-bridge, sys6-mail-scheduler, sys6-orchestrator-bridge, and dove9-system.
- **REQ-004**: All tests SHALL be Valgrind-clean (zero leaks, zero errors) when run via `run-test-valgrind.supp`.
- **REQ-005**: `make coverage` SHALL produce an `lcov` HTML report under `dovecho-core/coverage/dove9/`.
- **REQ-006**: A GitHub Actions CI job SHALL build and test the C layer on `ubuntu-latest` for every push/PR to the `dovecho-core` branch.
- **REQ-007**: Test binaries SHALL use mock vtables for LLM, memory, and persona services — no real inference calls.
- **SEC-001**: Test code SHALL validate that oversized inputs are safely truncated (buffer overflow regression tests).
- **SEC-002**: Test code SHALL validate that NULL vtable function pointers do not cause segfaults.
- **CON-001**: The C test harness SHALL NOT depend on Dovecot `lib/` or `lib-test/` — it must be self-contained with a minimal custom `dove9-test-common.h`.
- **CON-002**: The Dove9 subdirectory integration SHALL NOT modify any existing Dovecot `Makefile.am` or `configure.ac` logic — it adds a new SUBDIRS entry only.
- **CON-003**: All test source files SHALL follow the existing Dovecot naming convention: `test-dove9-<module>.c`.
- **CON-004**: Build infrastructure SHALL work on Linux (gcc ≥ 9) and macOS (clang ≥ 13). MSVC/MinGW is not required.
- **GUD-001**: Each test file SHALL define a `main()` that calls individual test functions and reports pass/fail counts.
- **GUD-002**: Mock vtable implementations SHALL be shared across test files via a `dove9-test-mocks.h` / `dove9-test-mocks.c` pair.
- **GUD-003**: Tests SHALL be structured as: setup → exercise → assert → teardown, with each test function testing exactly one behavior.
- **PAT-001**: Follow the Dovecot `test_programs` / `noinst_PROGRAMS` / `check-local` Makefile.am pattern (see `src/lib-dns/Makefile.am` as reference).
- **PAT-002**: Use the `test_begin(name)` / `test_assert(expr)` / `test_end()` pattern from Dovecot's `test-common.h`, but reimplemented minimally in `dove9-test-common.h` to avoid `lib/` dependency.

## 2. Implementation Steps

### Implementation Phase 1: Autotools Integration

- GOAL-001: Wire `libdove9.la` into the Dovecho build system so it compiles as part of `make` and installs headers via `make install`.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create `dovecho-core/src/dove9/` directory by renaming/moving the dove9 files from their current flat layout. Move `dove9-Makefile.am` → `dove9/Makefile.am`. Move `dove9-system.{h,c}` → `dove9/dove9-system.{h,c}`. Move subdirectories `types/`, `utils/`, `cognitive/`, `core/`, `integration/` into `dove9/`. Update all `#include` relative paths in the 9 `.c` files to reflect the new flat structure under `dove9/`. | ✅ | 2026-04-10 |
| TASK-002 | Edit `dovecho-core/src/Makefile.am`: append `dove9` to the `SUBDIRS` list after `plugins` (last position, no deps on other SUBDIRS). | ✅ | 2026-04-10 |
| TASK-003 | Edit `dovecho-core/configure.ac`: add `src/dove9/Makefile` to the `AC_CONFIG_FILES` list. | ✅ | 2026-04-10 |
| TASK-004 | Update `dove9/Makefile.am` (the renamed `dove9-Makefile.am`): adjust `AM_CPPFLAGS` `-I` paths to use `$(srcdir)/types` etc. since files are now under `dove9/`. Verify `noinst_LTLIBRARIES = libdove9.la` is correct. Remove the `dove9include_HEADERS` install rule if headers should not be installed yet (keep as `noinst` for phase 1). | ✅ | 2026-04-10 |
| TASK-005 | Verify: run `./autogen.sh && ./configure && make -j$(nproc)` in `dovecho-core/`. Confirm `libdove9.la` is built under `src/dove9/.libs/`. Fix any include path or missing file errors. | ✅ | 2026-04-10 |

### Implementation Phase 2: Self-Contained Test Harness

- GOAL-002: Create a minimal, self-contained C test framework for Dove9 that does not depend on Dovecot's `lib/` or `lib-test/`, plus shared mock vtable implementations.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-006 | Create `dovecho-core/src/dove9/test/dove9-test-common.h`. Implement: `void dove9_test_begin(const char *name)`, `void dove9_test_end(void)`, `void dove9_test_assert(bool condition, const char *expr, const char *file, int line)`, `#define DOVE9_TEST_ASSERT(expr)`, `void dove9_test_assert_str_eq(const char *a, const char *b, const char *file, int line)`, `#define DOVE9_TEST_ASSERT_STR_EQ(a, b)`, `void dove9_test_assert_int_eq(int a, int b, const char *file, int line)`, `#define DOVE9_TEST_ASSERT_INT_EQ(a, b)`, `int dove9_test_run(const char *suite_name, void (*tests[])(void), unsigned int count)` (returns 0 on all pass, 1 on any failure). Track pass/fail counts globally. Print colored output respecting `NO_COLOR`. | ✅ | 2026-04-10 |
| TASK-007 | Create `dovecho-core/src/dove9/test/dove9-test-common.c`. Implement all functions declared in `dove9-test-common.h`. Use only `<stdio.h>`, `<stdlib.h>`, `<string.h>`, `<stdbool.h>`. | ✅ | 2026-04-10 |
| TASK-008 | Create `dovecho-core/src/dove9/test/dove9-test-mocks.h`. Declare shared mock vtables: `extern struct dove9_llm_service dove9_mock_llm;`, `extern struct dove9_memory_store dove9_mock_memory;`, `extern struct dove9_persona_core dove9_mock_persona;`. Declare `void dove9_mock_reset(void)` to clear call counters. Declare call tracking: `extern unsigned int dove9_mock_llm_call_count;`, `extern unsigned int dove9_mock_memory_store_count;`, `extern unsigned int dove9_mock_persona_call_count;`. | ✅ | 2026-04-10 |
| TASK-009 | Create `dovecho-core/src/dove9/test/dove9-test-mocks.c`. Implement all mock vtable functions: `mock_generate_response` writes `"Echo: <prompt>"` truncated to `out_len`; `mock_retrieve_recent` writes `"no recent memories"`; `mock_retrieve_relevant` writes `"relevant: <query>"`; `mock_get_personality` writes `"curious"`; `mock_get_dominant_emotion` writes `"neutral"`; `mock_update_emotional_state` is no-op returning 0; `mock_store` increments counter returning 0. All increment their respective call counters. `dove9_mock_reset` zeros all counters. | ✅ | 2026-04-10 |

### Implementation Phase 3: Unit Tests — Types, Logger, Triadic Engine

- GOAL-003: Write unit tests for the foundational modules: type system helpers, logger, and the triadic engine including step assignments, T-point convergence, and coupling detection.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-010 | Create `dovecho-core/src/dove9/test/test-dove9-types.c`. Tests: (a) `dove9_config_default()` returns `enable_triadic_loop=true`, `max_processes=DOVE9_MAX_PROCESSES`; (b) `dove9_cognitive_context_init()` sets `salience=0.0`, `degraded=false`, empty strings; (c) `dove9_mailbox_mapping_default()` has INBOX, Drafts, Sent, Trash, Archive, Junk; (d) `dove9_coupling_set/is_active/clear` correctly manipulates bitfield for all 3 coupling types; (e) enum value ranges: 6 cognitive terms, 7 process states, 3 coupling types. | ✅ | 2026-04-10 |
| TASK-011 | Create `dovecho-core/src/dove9/test/test-dove9-logger.c`. Tests: (a) `dove9_logger_create("test")` returns non-NULL; (b) `dove9_logger_create_child(parent, "child")` returns non-NULL; (c) `dove9_log_info/warn/error/debug` do not crash with NULL format args; (d) `dove9_logger_destroy` NULLs the pointer; (e) set `LOG_LEVEL=error` env var, confirm debug/info/warn are suppressed (capture stderr). | ✅ | 2026-04-10 |
| TASK-012 | Create `dovecho-core/src/dove9/test/test-dove9-triadic-engine.c`. Tests: (a) verify `dove9_step_configs[12]` matches the Step Assignment Table exactly (step_number, stream, term, mode, type, phase_degrees for all 12 entries); (b) verify `dove9_stream_configs[3]` phase offsets are 0, 120, 240; (c) verify `dove9_triad_points[4]` step triples are {1,5,9}, {2,6,10}, {3,7,11}, {4,8,12}; (d) `dove9_triad_at_step(1)` returns triad 0, `dove9_triad_at_step(4)` returns triad 3; (e) `dove9_detect_couplings` with T4_EXPRESSIVE and T7_REFLECTIVE returns PERCEPTION_MEMORY; (f) engine create/start/advance through 12 steps increments cycle counter by 1; (g) TRIAD_CONVERGED events fire exactly 4 times per cycle; (h) CYCLE_COMPLETED event fires at step 12. | ✅ | 2026-04-10 |

### Implementation Phase 4: Unit Tests — DTE Processor, Kernel, Mail Bridge

- GOAL-004: Write unit tests for the DTE processor vtable conversion, kernel process management, and mail protocol bridge conversions.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-013 | Create `dovecho-core/src/dove9/test/test-dove9-dte-processor.c`. Tests: (a) `dove9_dte_processor_create` with valid mock vtables returns non-NULL; (b) `dove9_dte_processor_as_cognitive` returns processor with all 6 function pointers non-NULL; (c) calling each T-function via the vtable invokes the corresponding mock service (check call counters); (d) with NULL `generate_parallel_response`, `process_t2` falls back to sequential `generate_response`; (e) `salience_threshold` filtering: context with salience below threshold produces degraded output; (f) `dove9_dte_processor_destroy` NULLs the pointer. | ✅ | 2026-04-10 |
| TASK-014 | Create `dovecho-core/src/dove9/test/test-dove9-kernel.c`. Tests: (a) `dove9_kernel_create` with valid config and engine returns non-NULL; (b) `create_process` returns process with state QUEUED and valid UUID-like ID; (c) `get_process` retrieves by ID; (d) `terminate_process` transitions to TERMINATED; (e) `suspend_process` on ACTIVE process transitions to SUSPENDED; (f) `resume_process` on SUSPENDED transitions back to ACTIVE; (g) `fork_process` creates new process with same context; (h) creating `DOVE9_MAX_PROCESSES + 1` processes: last returns NULL; (i) `dove9_kernel_tick` activates highest-priority queued process; (j) `get_metrics` returns correct total/active/completed counts; (k) `enable_mail_protocol` + `create_process_from_mail` + `get_process_by_message_id` round-trips correctly; (l) `get_mailbox` / `move_mailbox` / `update_from_flags` state transitions. | ✅ | 2026-04-10 |
| TASK-015 | Create `dovecho-core/src/dove9/test/test-dove9-mail-bridge.c`. Tests: (a) `dove9_mail_bridge_create` returns non-NULL; (b) `dove9_mail_to_process` sets process ID from message_id, state QUEUED, copies subject/body to context; (c) `dove9_process_to_mail` generates reply with correct from/to swap, in_reply_to set, subject prefixed with "Re: "; (d) `dove9_mail_flags_to_state`: SEEN flag → COMPLETED, DRAFT → PROCESSING, DELETED → TERMINATED; (e) `dove9_state_to_mail_flags`: COMPLETED → SEEN|ANSWERED, PROCESSING → DRAFT; (f) `dove9_state_to_mailbox`: QUEUED → INBOX, COMPLETED → Sent; (g) `dove9_mail_calculate_priority`: flagged+reply mail with default 5 → ≥7 and ≤10; plain mail with default 5 → 5; (h) `dove9_mail_create_cognitive_context` sets input from body, salience > 0 for non-empty body; (i) `dove9_mail_extract_thread_relations`: mail with in_reply_to and 3 references → parent_id set, sibling_count=3; (j) oversized body (>DOVE9_MAX_BODY_LEN) is truncated without overflow. | ✅ | 2026-04-10 |

### Implementation Phase 5: Unit Tests — Sys6 Scheduler, Bridges, System

- GOAL-005: Write unit tests for the Sys6 operadic scheduler, both orchestrator bridges, and the top-level `dove9_system`.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-016 | Create `dovecho-core/src/dove9/test/test-dove9-sys6-scheduler.c`. Tests: (a) `dove9_sys6_scheduler_create` returns non-NULL; (b) priority 8 → phase 1, priority 5 → phase 2, priority 2 → phase 3; (c) advance 30 steps → SYS6_CYCLE_BOUNDARY event; (d) advance 60 steps → GRAND_CYCLE_BOUNDARY event; (e) `schedule_mail` assigns a valid grand_cycle_step in [1,60]; (f) `complete_process` decrements pending count; (g) `get_cycle_positions` returns consistent sys6/dove9/grand progress values; (h) `get_next_slot` returns slot aligned to both Sys6 and Dove9 cycles; (i) with `enable_operadic_scheduling=false`, scheduling degrades to FIFO; (j) `max_processes_per_grand_cycle` cap triggers CAPACITY_WARNING event. | ✅ | 2026-04-10 |
| TASK-017 | Create `dovecho-core/src/dove9/test/test-dove9-orchestrator-bridge.c`. Tests: (a) `dove9_orchestrator_bridge_create` + `initialize` with mock services succeeds; (b) `process_email` with bot address in `to` field returns non-NULL response; (c) `process_email` where bot address is NOT in `to` returns NULL (message not for us); (d) response `to` field = original `from`, response `from` = bot address; (e) response `in_reply_to` = original `message_id`; (f) RESPONSE_READY event fires with valid response; (g) STARTED/STOPPED events on start/stop lifecycle. | ✅ | 2026-04-10 |
| TASK-018 | Create `dovecho-core/src/dove9/test/test-dove9-sys6-bridge.c`. Tests: (a) `dove9_sys6_bridge_create` + `initialize` succeeds; (b) `process_email` returns response (delegates to orchestrator bridge); (c) `get_stats` shows `total_scheduled` and `total_completed` incrementing; (d) phase distribution counters are non-zero after processing multiple messages; (e) stream distribution counters are non-zero; (f) OPTIMAL_SLOT_USED event fires; (g) with `enable_sys6_scheduling=false`, still processes but without operadic scheduling events. | ✅ | 2026-04-10 |
| TASK-019 | Create `dovecho-core/src/dove9/test/test-dove9-system.c`. Tests: (a) `dove9_system_create` with valid config returns non-NULL; (b) `start` + `is_running` returns true; (c) `process_mail` creates a process and emits MAIL_RECEIVED event; (d) upon completion, RESPONSE_READY event contains a valid response mail; (e) `stop` + `is_running` returns false; (f) `destroy` NULLs the pointer; (g) processing multiple mails sequentially succeeds; (h) event handler receives TRIAD_SYNC events during processing; (i) event handler receives CYCLE_COMPLETE events. | ✅ | 2026-04-10 |

### Implementation Phase 6: Test Build Integration

- GOAL-006: Wire all test binaries into the Autotools build so `make check` runs them, optionally through Valgrind.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-020 | Update `dovecho-core/src/dove9/Makefile.am`: add `test/` sources. Define `test_programs` variable listing all 9 test binaries: `test-dove9-types`, `test-dove9-logger`, `test-dove9-triadic-engine`, `test-dove9-dte-processor`, `test-dove9-kernel`, `test-dove9-mail-bridge`, `test-dove9-sys6-scheduler`, `test-dove9-orchestrator-bridge`, `test-dove9-sys6-bridge`, `test-dove9-system`. Set `noinst_PROGRAMS = $(test_programs)`. Define `test_libs = libdove9.la -lm`. For each test binary, define `test_dove9_<X>_SOURCES = test/test-dove9-<X>.c test/dove9-test-common.c test/dove9-test-mocks.c` and `test_dove9_<X>_LDADD = $(test_libs)`. Add `check-local:` target iterating over `$(test_programs)` calling `$(RUN_TEST) ./$$bin`. | ✅ | 2026-04-10 |
| TASK-021 | Verify `make check` in `dovecho-core/` builds all test binaries and runs them. Ensure all tests pass (green output). Fix any compilation errors, missing symbols, or test failures. | ✅ | 2026-04-10 |
| TASK-022 | Verify Valgrind mode: set `NOVALGRIND=` (empty) and ensure Valgrind is installed, then run `make check`. Confirm zero leaks and zero errors. If suppressions are needed for known issues, add them to `dovecho-core/run-test-valgrind.supp`. | ✅ | 2026-04-10 |

### Implementation Phase 7: Coverage Reporting

- GOAL-007: Enable `gcov`/`lcov` code coverage for the Dove9 C layer and produce an HTML report.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-023 | Edit `dovecho-core/configure.ac`: add `AC_ARG_ENABLE(coverage, ...)` option. When `--enable-coverage` is passed, append `-fprofile-arcs -ftest-coverage` to `CFLAGS` and `-lgcov` to `LDFLAGS`. AC_SUBST the coverage flags. | ✅ | 2026-04-10 |
| TASK-024 | Add a `coverage` target to `dovecho-core/src/dove9/Makefile.am`: run `make check`, then `lcov --capture --directory . --output-file dove9-coverage.info`, then `genhtml dove9-coverage.info --output-directory $(top_builddir)/coverage/dove9`. Add `clean-coverage` target removing `.gcda`, `.gcno`, `dove9-coverage.info`. | ✅ | 2026-04-10 |
| TASK-025 | Verify: `./configure --enable-coverage && make && make -C src/dove9 coverage`. Confirm HTML report appears at `dovecho-core/coverage/dove9/index.html`. Verify line coverage ≥ 80%. | ✅ | 2026-04-10 |

### Implementation Phase 8: GitHub Actions CI Job

- GOAL-008: Add a CI workflow job that builds the C layer, runs tests, and uploads coverage on every push/PR to `dovecho-core` branch.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-026 | Create or update `.github/workflows/ci.yml`: add a new job `test-c-layer` that runs on `ubuntu-latest`. Steps: (1) checkout, (2) `sudo apt-get install -y autoconf automake libtool valgrind lcov`, (3) `cd dovecho-core && ./autogen.sh`, (4) `./configure --enable-devel-checks --enable-coverage`, (5) `make -j$(nproc)`, (6) `make check`, (7) `make -C src/dove9 coverage`, (8) upload `dovecho-core/coverage/dove9/` as artifact. Trigger on `push` and `pull_request` to `dovecho-core` branch. | ✅ | 2026-04-10 |
| TASK-027 | Add branch filter: the `test-c-layer` job SHALL only run when files under `dovecho-core/src/dove9/**` or `dovecho-core/configure.ac` or `dovecho-core/src/dove9/Makefile.am` are modified (use `paths` filter). | ✅ | 2026-04-10 |
| TASK-028 | Add the `compile_commands.json` generation step: after `make`, run `dovecho-core/build-aux/generate-compile-commands.sh` and upload as artifact for clangd/IDE integration. | ✅ | 2026-04-10 |

### Implementation Phase 9: Security & Regression Tests

- GOAL-009: Add targeted security regression tests verifying buffer safety, NULL pointer handling, and input validation.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-029 | Create `dovecho-core/src/dove9/test/test-dove9-security.c`. Tests: (a) `dove9_mail_message` with body exactly `DOVE9_MAX_BODY_LEN` bytes: no overflow; (b) `dove9_mail_message` with 65 recipients (> `DOVE9_MAX_RECIPIENTS`): truncated to 64; (c) `dove9_cognitive_context` with `input` filled to max: `response` field remains independent; (d) `dove9_dte_processor_create` with all NULL vtable function pointers: processor handles gracefully (returns degraded context, no segfault); (e) `dove9_kernel_create_process` with `priority` < 1 or > 10: clamped to valid range; (f) `dove9_mail_calculate_priority` with extreme boost combinations: result is clamped to [1,10]; (g) `dove9_orchestrator_bridge_process_email` with empty `from`/`to`/`body`: no crash, returns NULL or degraded response. | ✅ | 2026-04-10 |
| TASK-030 | Add `test-dove9-security` to `test_programs` in `dovecho-core/src/dove9/Makefile.am`. Verify all security tests pass under Valgrind. | ✅ | 2026-04-10 |

## 3. Alternatives

- **ALT-001**: **Use Dovecot's `lib-test/` directly** — Rejected because it requires linking against `liblib.la` (Dovecot's base utility library) which has heavy init/deinit requirements (`lib_init()`, `data_stack`, `ioloop`) that are irrelevant to the Dove9 cognitive layer. A self-contained test harness eliminates this coupling.
- **ALT-002**: **Use CMake instead of Autotools** — Rejected because the host project (Dovecot/Dovecho) uses Autotools exclusively. Introducing a second build system creates friction. The Dove9 layer should integrate seamlessly with the existing `./configure && make` workflow.
- **ALT-003**: **Use an external C test framework (CUnit, cmocka, Unity)** — Rejected because adding a build-time dependency complicates the Autotools integration and CI setup. The Dovecot test pattern (`test_begin`/`test_assert`/`test_end`) is simple enough to reimplement in ~100 lines of self-contained C.
- **ALT-004**: **Run C tests from the TypeScript Jest harness via FFI** — Rejected because it would require `node-ffi-napi` or similar, adding Node.js as a runtime dependency for C tests. The C layer must be testable on any system with a C compiler and no Node.js installation.
- **ALT-005**: **Defer coverage to a separate tool (SonarQube, Codecov)** — Partial rejection. `gcov`/`lcov` produces local coverage immediately. External tools may be added later as an optional upload step (TASK-026 already includes artifact upload), but local coverage is the primary mechanism.

## 4. Dependencies

- **DEP-001**: **GNU Autotools** (autoconf ≥ 2.69, automake ≥ 1.16, libtool ≥ 2.4) — Required for `autogen.sh` and the `Makefile.am` → `Makefile.in` generation. Already present in the Dovecho build system.
- **DEP-002**: **GCC ≥ 9 or Clang ≥ 13** — C11 compiler with `-std=c11`, `-Wall`, `-Wextra`, `-Werror` support. GCC for Linux CI, Clang for macOS.
- **DEP-003**: **Valgrind ≥ 3.15** — Memory error detection and leak checking. Used by `run-test.sh.in` wrapper. Linux only (Valgrind does not support macOS ARM).
- **DEP-004**: **lcov ≥ 1.14** — `gcov` frontend for HTML coverage report generation. Required only when `--enable-coverage` is passed to `configure`.
- **DEP-005**: **libm** (math library) — Linked via `-lm`. Used by Sys6 scheduler (`floor`, `ceil`). Standard on all POSIX systems.
- **DEP-006**: **POSIX `<strings.h>`** — Provides `strcasecmp()` used in orchestrator-bridge for case-insensitive email address comparison. Available on Linux and macOS. Not available on MSVC (not a target platform per CON-004).
- **DEP-007**: **GitHub Actions `ubuntu-latest` runner** — CI environment. Requires `apt-get install autoconf automake libtool valgrind lcov`.

## 5. Files

### New Files

- **FILE-001**: `dovecho-core/src/dove9/test/dove9-test-common.h` — Self-contained test framework header (test_begin, test_assert, test_end, test_run).
- **FILE-002**: `dovecho-core/src/dove9/test/dove9-test-common.c` — Test framework implementation (~100 lines).
- **FILE-003**: `dovecho-core/src/dove9/test/dove9-test-mocks.h` — Shared mock vtable declarations and call counters.
- **FILE-004**: `dovecho-core/src/dove9/test/dove9-test-mocks.c` — Mock vtable implementations (~120 lines).
- **FILE-005**: `dovecho-core/src/dove9/test/test-dove9-types.c` — Type system unit tests (~150 lines).
- **FILE-006**: `dovecho-core/src/dove9/test/test-dove9-logger.c` — Logger unit tests (~80 lines).
- **FILE-007**: `dovecho-core/src/dove9/test/test-dove9-triadic-engine.c` — Triadic engine unit tests (~300 lines).
- **FILE-008**: `dovecho-core/src/dove9/test/test-dove9-dte-processor.c` — DTE processor unit tests (~200 lines).
- **FILE-009**: `dovecho-core/src/dove9/test/test-dove9-kernel.c` — Kernel process management unit tests (~350 lines).
- **FILE-010**: `dovecho-core/src/dove9/test/test-dove9-mail-bridge.c` — Mail protocol bridge unit tests (~250 lines).
- **FILE-011**: `dovecho-core/src/dove9/test/test-dove9-sys6-scheduler.c` — Sys6 scheduler unit tests (~250 lines).
- **FILE-012**: `dovecho-core/src/dove9/test/test-dove9-orchestrator-bridge.c` — Orchestrator bridge unit tests (~200 lines).
- **FILE-013**: `dovecho-core/src/dove9/test/test-dove9-sys6-bridge.c` — Sys6 orchestrator bridge unit tests (~180 lines).
- **FILE-014**: `dovecho-core/src/dove9/test/test-dove9-system.c` — Top-level system integration tests (~200 lines).
- **FILE-015**: `dovecho-core/src/dove9/test/test-dove9-security.c` — Security regression tests (~200 lines).

### Modified Files

- **FILE-016**: `dovecho-core/src/Makefile.am` — Add `dove9` to `SUBDIRS` list.
- **FILE-017**: `dovecho-core/configure.ac` — Add `src/dove9/Makefile` to `AC_CONFIG_FILES`. Add `--enable-coverage` option.
- **FILE-018**: `dovecho-core/src/dove9/Makefile.am` — Renamed from `dove9-Makefile.am`. Add test binary definitions, `check-local` target, `coverage` target.
- **FILE-019**: `.github/workflows/ci.yml` — Add `test-c-layer` job with branch filter and path filter.

### Relocated Files (Phase 1)

- **FILE-020**: `dovecho-core/src/dove9-system.{h,c}` → `dovecho-core/src/dove9/dove9-system.{h,c}`
- **FILE-021**: `dovecho-core/src/dove9-Makefile.am` → `dovecho-core/src/dove9/Makefile.am`
- **FILE-022**: `dovecho-core/src/types/` → `dovecho-core/src/dove9/types/`
- **FILE-023**: `dovecho-core/src/utils/` → `dovecho-core/src/dove9/utils/`
- **FILE-024**: `dovecho-core/src/cognitive/` → `dovecho-core/src/dove9/cognitive/`
- **FILE-025**: `dovecho-core/src/core/` → `dovecho-core/src/dove9/core/`
- **FILE-026**: `dovecho-core/src/dove9/integration/` (already exists — contains dove9 files alongside any existing Dovecot integration files; may need extraction of dove9-specific files only)

## 6. Testing

### Test Suite Summary

| Test ID | Test Binary | Module Under Test | Key Behaviors Verified | Estimated Assertions |
|---------|-------------|-------------------|----------------------|---------------------|
| TEST-001 | `test-dove9-types` | `dove9-types.h` | Config defaults, context init, mailbox mapping, coupling bitfield, enum ranges | ~25 |
| TEST-002 | `test-dove9-logger` | `dove9-logger.{h,c}` | Create, child, destroy, log levels, NO_COLOR, LOG_LEVEL | ~12 |
| TEST-003 | `test-dove9-triadic-engine` | `dove9-triadic-engine.{h,c}` | Step table, stream configs, T-points, coupling detection, engine lifecycle, events | ~40 |
| TEST-004 | `test-dove9-dte-processor` | `dove9-dte-processor.{h,c}` | Create, vtable conversion, T-function dispatch, NULL fallback, salience filtering | ~20 |
| TEST-005 | `test-dove9-kernel` | `dove9-kernel.{h,c}` | Process CRUD, state transitions, fork, max capacity, tick scheduling, mail protocol, metrics | ~35 |
| TEST-006 | `test-dove9-mail-bridge` | `dove9-mail-protocol-bridge.{h,c}` | Mail↔process conversion, flag/state mapping, priority, context creation, threading, overflow | ~30 |
| TEST-007 | `test-dove9-sys6-scheduler` | `dove9-sys6-mail-scheduler.{h,c}` | Phase assignment, cycle boundaries, schedule/complete, positions, next slot, FIFO fallback, capacity | ~28 |
| TEST-008 | `test-dove9-orchestrator-bridge` | `dove9-orchestrator-bridge.{h,c}` | Create/init, process email, address filtering, response fields, events | ~18 |
| TEST-009 | `test-dove9-sys6-bridge` | `dove9-sys6-orchestrator-bridge.{h,c}` | Create/init, process email, stats, distribution counters, events | ~16 |
| TEST-010 | `test-dove9-system` | `dove9-system.{h,c}` | Create/start/stop/destroy, process_mail, events (mail_received, response_ready, triad_sync, cycle_complete) | ~22 |
| TEST-011 | `test-dove9-security` | Cross-cutting | Buffer overflow, NULL vtable, clamping, empty input | ~15 |

**Total estimated assertions: ~261**

### Coverage Targets

| Metric | Target | Measurement |
|--------|--------|------------|
| Line coverage (all `.c`) | ≥ 80% | `lcov` report |
| Branch coverage (critical paths) | 100% | `lcov` report, specific files: triadic-engine, kernel, mail-bridge, sys6-scheduler |
| Function coverage | 100% | All public API functions called at least once |

## 7. Risks & Assumptions

- **RISK-001**: **Dovecot `src/Makefile.am` SUBDIRS ordering** — Adding `dove9` to SUBDIRS may conflict with Dovecot's library initialization order. Mitigation: dove9 has zero dependencies on other SUBDIRS, so position it last.
- **RISK-002**: **`configure.ac` merge conflicts** — The Dovecho `configure.ac` is large and actively modified. Adding entries to `AC_CONFIG_FILES` may conflict. Mitigation: add at the end of the file list, use clear comment markers.
- **RISK-003**: **File relocation breaks git history** — Moving files into `src/dove9/` subdirectory loses `git log --follow` for some operations. Mitigation: use `git mv` for the move operation to preserve rename detection.
- **RISK-004**: **Valgrind false positives** — Custom memory patterns (large fixed buffers on stack) may trigger Valgrind warnings. Mitigation: add suppressions to `run-test-valgrind.supp` if legitimate false positives are identified.
- **RISK-005**: **Cross-platform `strcasecmp`** — The orchestrator bridge uses `strcasecmp` from POSIX `<strings.h>`. If a non-POSIX target is ever required, a shim will be needed. Mitigation: accepted per CON-004 (Linux/macOS only).
- **RISK-006**: **Coverage target may not be met initially** — Some error paths (e.g., `malloc` failures inside `*_create`) may be hard to exercise without dependency injection for allocators. Mitigation: accept ≥ 80% line coverage as initial target, iterate to improve.
- **ASSUMPTION-001**: The Dovecho repository's `autogen.sh` and `configure.ac` function correctly on the CI runner. No fundamental Autotools breakage exists.
- **ASSUMPTION-002**: The existing 9 `.c` + 10 `.h` files compile without errors on GCC ≥ 9 with `-std=c11 -Wall -Wextra`. Any compilation errors discovered during Phase 1 TASK-005 will be fixed as part of that task (not as a separate phase).
- **ASSUMPTION-003**: Mock vtables provide sufficient test coverage for the cognitive processing paths. Real LLM/memory integration testing is out of scope for this plan.
- **ASSUMPTION-004**: The `dove9/` subdirectory name does not conflict with the existing `dove9/` TypeScript package at the monorepo root. These are in different directories (`dovecho-core/src/dove9/` vs. `dove9/`).

## 8. Related Specifications / Further Reading

- [spec/spec-architecture-dove9-c-cognitive-layer.md](../spec/spec-architecture-dove9-c-cognitive-layer.md) — Formal specification for all Dove9 C APIs, data contracts, and acceptance criteria
- [CLAUDE.md](../CLAUDE.md) — DeLovEcho monorepo guidance, §2 Triadic Cognitive Loop, §3 Sys6 Architecture
- [dovecho-core/src/dove9-Makefile.am](../dovecho-core/src/dove9-Makefile.am) — Current standalone Makefile.am (to be relocated)
- [dovecho-core/src/lib-dns/Makefile.am](../dovecho-core/src/lib-dns/Makefile.am) — Reference Dovecot test pattern (test_programs, check-local, RUN_TEST)
- [dovecho-core/build-aux/run-test.sh.in](../dovecho-core/build-aux/run-test.sh.in) — Valgrind test wrapper template
- [dovecho-core/run-test-valgrind.supp](../dovecho-core/run-test-valgrind.supp) — Valgrind suppression file
- [dovecho-core/configure.ac](../dovecho-core/configure.ac) — Autotools configure script
- [.github/workflows/ci.yml](../.github/workflows/ci.yml) — Existing CI pipeline (TypeScript-only, to be extended)
