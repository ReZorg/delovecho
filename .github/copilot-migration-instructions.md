# GitHub Copilot Migration Instructions

## Migration Context

- **Type**: Technology Migration + Pattern Changes
- **From**: `main`
- **To**: `dovecho-core`
- **Date**: 2026-04-07
- **Scope**: Modified files only (branch delta)
- **Primary Focus**: New conventions, generated type-stub patterns, and C/H developer tooling consistency

## Automatic Transformation Rules

### 1. Mandatory Transformations

- **Old Pattern**: No centralized C/C++ editor/indexer setup for `dovecho-core`.
- **New Pattern**: Always keep C/C++ workspace integration aligned with:
  - `.vscode/settings.json`
  - `.vscode/tasks.json`
  - `dovecho-core/.clang-format`
  - `dovecho-core/.clangd`
  - `dovecho-core/build-aux/generate-compile-commands.sh`
- **Trigger**: Any change to C/H files or build workflow in `dovecho-core`.
- **Action**: Update settings/tasks/tooling files together, not in isolation.

- **Old Pattern**: Manual or inconsistent type placeholders in `.pyi` stubs.
- **New Pattern**: Use `_typeshed.Incomplete` for unknown members and keep concise signatures in generated stubs under `.github/agents/.stubs/pyspark34/`.
- **Trigger**: Adding/editing stub files in `.github/agents/.stubs/pyspark34/**`.
- **Action**: Preserve generated-style declaration format and avoid runtime logic in `.pyi` files.

- **Old Pattern**: Mixed formatting/spacing style in C files.
- **New Pattern**: Dovecot-style formatting enforced by `dovecho-core/.clang-format` (tabs, width 8, Linux base style).
- **Trigger**: Any `.c` / `.h` edit under `dovecho-core`.
- **Action**: Format according to repo style before finalizing changes.

### 2. Transformations with Validation

- **Detected Pattern**: C tooling files changed without compile database regeneration path.
- **Suggested Transformation**: Keep `dovecho-core: compile_commands` task and `generate-compile-commands.sh` script aligned.
- **Required Validation**: `compile_commands.json` can be generated successfully when `bear` is installed.
- **Alternatives**: If `bear` unavailable, document fallback and keep script failure message explicit.

- **Detected Pattern**: Massive `.pyi` stub additions with inconsistent module layout.
- **Suggested Transformation**: Keep package tree mirroring real module hierarchy (`IPython`, `OpenSSL`, `absl`, etc.) and use declaration-only style.
- **Required Validation**: No implementation code in stubs; names and modules remain import-path consistent.
- **Alternatives**: If symbol type is unknown, use `Incomplete` rather than guessing narrow types.

### 3. API Correspondences

| Old API / Pattern | New API / Pattern | Notes | Example |
| --- | --- | --- | --- |
| Ad-hoc C build command | Tasked workflow in VS Code | Standardizes developer loop | `dovecho-core: configure (dev)` + `dovecho-core: build` |
| Missing compile DB for IDE | `compile_commands.json` generation task | Improves clangd/C_Cpp accuracy | `dovecho-core: compile_commands` |
| Unstructured unknown types in stubs | `_typeshed.Incomplete` placeholders | Keeps stubs maintainable and truthful | `foo: Incomplete` |
| Unscoped C formatting | `.clang-format` in `dovecho-core` | Enforces consistent style | tabs, Linux style |

### 4. New Patterns to Adopt

- **Pattern**: Branch-aware tooling co-evolution.
- **Usage**: When C/H architecture evolves, update editor tasks/settings in same PR.
- **Implementation**: Pair C/H edits with `.vscode` and `dovecho-core` tooling files.
- **Benefits**: Lower onboarding cost and fewer local environment mismatches.

- **Pattern**: Generated-stub discipline.
- **Usage**: For large `.pyi` drops under `.github/agents/.stubs/pyspark34`.
- **Implementation**: Keep deterministic, declaration-only style and broad placeholder typing where needed.
- **Benefits**: Stable diffs and reduced invalid assumptions in static typing metadata.

### 5. Obsolete Patterns to Avoid

- **Obsolete Pattern**: Editing `dovecho-core` C/H without checking `.clang-format` impact.
- **Why Avoid**: Causes style churn and noisy diffs.
- **Alternative**: Apply formatter-aligned edits.
- **Migration**: Reformat touched regions before commit.

- **Obsolete Pattern**: Handwritten, behavior-rich `.pyi` stubs.
- **Why Avoid**: Stubs are type declarations, not implementations.
- **Alternative**: Keep minimal signatures and placeholder types.
- **Migration**: Replace implementation-like bodies with declaration style.

## File Type Specific Instructions

### C/H Files (`dovecho-core/**/*.c`, `dovecho-core/**/*.h`)

- Prefer existing Dovecot idioms and includes order already used nearby.
- Keep tab-indented style and avoid style-only rewrites outside touched code.
- When adding new compile-time flags/includes, verify clangd compile database path remains valid.

### VS Code Tooling (`.vscode/*.json`)

- Keep C/C++ settings keyed to `dovecho-core/compile_commands.json`.
- Keep tasks shell-compatible with existing workspace expectations.
- Ensure task labels remain stable for contributor documentation.

### Python Stub Files (`.github/agents/.stubs/pyspark34/**/*.pyi`)

- Declaration-only; no runtime logic.
- Use `Incomplete` where source precision is unknown.
- Keep import and module path fidelity to upstream packages.

## Validation and Security

### Automatic Control Points

- Run type/lint checks that consume changed files where available.
- For C workflow changes, verify at minimum:
  - configure path exists (`autogen.sh`, `configure`)
  - build task command resolves
  - compile database generation script is executable and deterministic
- For stub changes, validate parseability and import path consistency.

### Manual Escalation

Situations requiring human intervention:

- ABI-impacting C API changes in `dovecho-core`.
- Any generated stub set where upstream module version is uncertain.
- Build toolchain assumptions that differ across OS environments.

## Migration Monitoring

### Tracking Metrics

- Percentage of C/H changes accompanied by tooling updates.
- Number of stub files following declaration-only convention.
- Number of edits requiring manual follow-up due to platform toolchain differences.

### Error Reporting

When Copilot suggestions are off-pattern, report with:

- offending file path
- expected pattern from this document
- minimal before/after snippet
- whether issue is tooling, style, or type-declaration fidelity

## Contextual Transformation Examples

### Example A: C Tooling Co-Evolution

```text
BEFORE
- C/H files changed in dovecho-core
- No updated compile DB or editor task alignment

AFTER
- C/H edits + `.vscode` task/settings maintained
- `dovecho-core: compile_commands` remains valid

COPILOT RULE
When editing `dovecho-core/**/*.c|h`, also evaluate whether `.vscode/settings.json`, `.vscode/tasks.json`, or compile database workflow needs synchronized updates.
```

### Example B: Stub Consistency

```text
BEFORE
- Narrow guessed type in generated stub with uncertain source type

AFTER
- `_typeshed.Incomplete` used for uncertain members

COPILOT RULE
For `.pyi` files under `.github/agents/.stubs/pyspark34`, prefer correctness-by-declaration over speculative precision.
```
