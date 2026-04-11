# Dove9 CMake Migration

**Branch:** `cmake-dove9-migration`
**Description:** Replace autotools+GNUmakefile with CMake for the dove9 cognitive C layer, enabling native `compile_commands.json`, CTest integration, and cross-platform builds.

## Goal
Migrate the dove9 C layer (`dovecho-core/src/dove9/`) from autotools (Makefile.am) + standalone GNUmakefile to a modern CMake build system. This gives us native `compile_commands.json` export (no more manual generation), CTest for test execution, IDE integration via `configure_cmake_project`, and consistent cross-platform builds (Linux, Windows/w64devkit, macOS).

## Constraints
- Dove9 is self-contained C11 with **only** `-lm` as external dependency
- 9 source files → `libdove9` static library
- 27 test programs (11 common-only + 16 with mocks)
- Preserve existing autotools integration (`Makefile.am`) for the parent dovecot-core build
- Must generate `compile_commands.json` for clangd/IntelliSense
- VS Code `configure_cmake_project` task should work after migration

## Implementation Steps

### ✅ Step 1: Root CMakeLists.txt for dove9
**Files:**
- `dovecho-core/src/dove9/CMakeLists.txt` (NEW)

**What:** Create the top-level CMakeLists.txt that defines:
- `cmake_minimum_required(VERSION 3.16)`
- Project name `dove9` with C language, version 1.0.0
- C11 standard enforcement (`CMAKE_C_STANDARD 11`, `CMAKE_C_STANDARD_REQUIRED ON`)
- Compiler warning flags (`-Wall -Wextra -Wno-unused-parameter`)
- `CMAKE_EXPORT_COMPILE_COMMANDS ON`
- Include directories for all subdirs (types, utils, cognitive, core, integration, test)
- `libdove9` static library target from all 9 source files
- Link `-lm` (via `find_library(MATH_LIBRARY m)`)

**Testing:** Run `cmake -S dovecho-core/src/dove9 -B dovecho-core/src/dove9/build` — should configure without errors. Verify `compile_commands.json` appears in build dir.

**STOP — Verify cmake configure succeeds before continuing.**

### ✅ Step 2: Test targets via CTest
**Files:**
- `dovecho-core/src/dove9/CMakeLists.txt` (MODIFY — append test section)

**What:** Add all 27 test executables with proper source/link dependencies:
- `enable_testing()`
- For each of the 11 common-only tests: `add_executable()` with test source + `test/dove9-test-common.c`, link `libdove9` + `m`
- For each of the 16 mock tests: `add_executable()` with test source + common + `test/dove9-test-mocks.c`, link `libdove9` + `m`
- `add_test(NAME <test-name> COMMAND <test-exe>)` for all 27
- Set `WORKING_DIRECTORY` to source dir for any tests that need it

**Test groups (common-only, 11):**
`test-dove9-types`, `test-dove9-logger`, `test-dove9-mail-bridge`, `test-dove9-sys6-scheduler`, `test-dove9-sys6-correctness`, `test-dove9-cognitive-context`, `test-dove9-triadic-math`, `test-dove9-coupling-detection`, `test-dove9-mail-protocol`, `test-dove9-salience-landscape`, `test-dove9-step-assignment`

**Test groups (with mocks, 16):**
`test-dove9-triadic-engine`, `test-dove9-dte-processor`, `test-dove9-kernel`, `test-dove9-orchestrator-bridge`, `test-dove9-sys6-bridge`, `test-dove9-system`, `test-dove9-security`, `test-dove9-integration`, `test-dove9-stress`, `test-dove9-kernel-mail`, `test-dove9-event-callbacks`, `test-dove9-system-config`, `test-dove9-memory-lifecycle`, `test-dove9-api-boundary`, `test-dove9-process-management`, `test-dove9-cognitive-pipeline`

**Testing:** `cmake --build dovecho-core/src/dove9/build` then `ctest --test-dir dovecho-core/src/dove9/build --output-on-failure` — all 27 tests should pass.

**STOP — Verify all 27 tests pass under CTest before continuing.**

### ✅ Step 3: Build options (coverage, debug, install)
**Files:**
- `dovecho-core/src/dove9/CMakeLists.txt` (MODIFY — add options section)

**What:** Add CMake options mirroring the autotools `configure` flags:
- `option(DOVE9_ENABLE_COVERAGE "Enable code coverage with gcov/lcov" OFF)` — when ON, add `-fprofile-arcs -ftest-coverage` to CFLAGS, add `coverage` custom target
- `option(DOVE9_ENABLE_DEVEL_CHECKS "Enable development checks (-DDEBUG)" OFF)`
- Install rules: `install(TARGETS libdove9 ...)` and `install(FILES <headers> DESTINATION include/dovecho/dove9)`
- Export `dove9Config.cmake` for downstream `find_package(dove9)` usage

**Testing:** Reconfigure with `-DDOVE9_ENABLE_DEVEL_CHECKS=ON`, build, run tests. Verify `-DDEBUG` appears in compile commands.

**STOP — Verify options work before continuing.**

### ✅ Step 4: CMakePresets.json for reproducible configurations
**Files:**
- `dovecho-core/src/dove9/CMakePresets.json` (NEW)

**What:** Create presets file with:
- `default` preset: Release build, compile_commands ON
- `dev` preset: Debug build, devel checks ON, Ninja generator
- `coverage` preset: Debug build, coverage enabled
- `ci` preset: Release build, all warnings as errors (`-Werror`)

**Testing:** `cmake --preset dev -S dovecho-core/src/dove9` — should configure with dev settings.

**STOP — Verify presets work before continuing.**

### ✅ Step 5: Update VS Code integration and docs
**Files:**
- `dovecho-core/src/dove9/README.md` (MODIFY — add CMake build instructions)
- `.vscode/tasks.json` (MODIFY — update dovecho-core tasks to use CMake)
- `dovecho-core/compile_commands.json` (UPDATE — symlink or copy from build dir)

**What:**
- Add CMake build instructions to the dove9 README alongside existing autotools instructions
- Update VS Code tasks: replace `autogen.sh` / `configure` / `make` tasks with CMake equivalents (`cmake --preset dev`, `cmake --build`, `ctest`)
- Create a script or task to symlink `build/compile_commands.json` → `dovecho-core/compile_commands.json` for IDE consumption

**Testing:** Use VS Code Command Palette → "CMake: Configure" (via `configure_cmake_project` tool). Verify IntelliSense works on dove9 C files.

**STOP — Final verification: full configure→build→test cycle works end-to-end.**

### ✅ Step 6: Update dove9-validate.ps1 scoring
**Files:**
- `dove9-validate.ps1` (MODIFY — add CMake detection scoring section)

**What:** Add a new scoring section that awards points for:
- `CMakeLists.txt` exists (+1)
- `CMakePresets.json` exists (+1)
- `cmake_minimum_required` present (+1)
- `enable_testing()` present (+1)
- All 27 `add_test()` calls present (+1 each, capped at +5)
- `CMAKE_EXPORT_COMPILE_COMMANDS` enabled (+1)
- Total potential: +10 points

**Testing:** Run `.\dove9-validate.ps1` — score should increase by ~10 from current baseline.

**STOP — Plan complete. All steps implemented.**
