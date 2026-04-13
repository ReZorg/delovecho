---
name: get-shit-done
description: "Meta-prompting, context engineering, and spec-driven development system for Claude Code, OpenCode, and Gemini CLI. Use when building software with AI coding assistants, structuring multi-phase development workflows, solving context rot in long AI sessions, or when the user mentions GSD, get-shit-done, spec-driven development, or context engineering for AI coding."
---

# Get Shit Done (GSD)

Context engineering layer that makes AI coding assistants reliable at scale. Solves **context rot** — quality degradation as the AI fills its context window — by giving each execution task a fresh 200k-token context.

**Repository:** [rzonedevops/get-shit-done](https://github.com/rzonedevops/get-shit-done) (fork of [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done))
**Package:** `get-shit-done-cc` v1.18.0 on npm | **License:** MIT | **Author:** TÂCHES

## Installation

```bash
npx get-shit-done-cc@latest
```

Prompts for runtime (Claude Code / OpenCode / Gemini / all) and location (global / local). Non-interactive:

```bash
npx get-shit-done-cc --claude --global   # Claude Code → ~/.claude/
npx get-shit-done-cc --opencode --global # OpenCode → ~/.config/opencode/
npx get-shit-done-cc --gemini --global   # Gemini → ~/.gemini/
npx get-shit-done-cc --all --global      # All runtimes
npx get-shit-done-cc --claude --local    # Current project only → ./.claude/
```

Recommended: run Claude Code with `claude --dangerously-skip-permissions` for frictionless automation.

## Core Workflow

Six-step cycle: **Initialize → Discuss → Plan → Execute → Verify → Complete**.

### 1. Initialize — `/gsd:new-project [--auto @idea.md]`

Deep questioning extracts the user's vision, parallel research agents investigate the domain, requirements are scoped, and a phased roadmap is created.

**Creates:** `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `.planning/research/`

For existing codebases, run `/gsd:map-codebase` first — parallel agents analyze stack, architecture, conventions, and concerns.

### 2. Discuss — `/gsd:discuss-phase [N]`

Capture implementation preferences before planning. Identifies gray areas (visual layout, API design, content structure) and asks targeted questions. Output feeds into research and planning.

**Creates:** `{phase}-CONTEXT.md`

### 3. Plan — `/gsd:plan-phase [N]`

Research → create 2–3 atomic XML task plans → verify against requirements. Each plan fits in a fresh context window.

**Creates:** `{phase}-RESEARCH.md`, `{phase}-{N}-PLAN.md`

### 4. Execute — `/gsd:execute-phase <N>`

Wave-based parallel execution. Fresh 200k context per plan. Atomic git commit per task. Automated verification against goals.

**Creates:** `{phase}-{N}-SUMMARY.md`, `{phase}-VERIFICATION.md`

### 5. Verify — `/gsd:verify-work [N]`

User acceptance testing — walks through deliverables one at a time. Auto-diagnoses failures with debug agents and creates fix plans.

**Creates:** `{phase}-UAT.md`, fix plans if issues found

### 6. Complete — `/gsd:complete-milestone` then `/gsd:new-milestone`

Archive milestone, tag release, start next version cycle.

### Quick Mode — `/gsd:quick`

Ad-hoc tasks with GSD guarantees (atomic commits, state tracking) but no research/verification overhead. Lives in `.planning/quick/`.

## Commands Reference

| Command | Purpose |
|---------|---------|
| `/gsd:new-project [--auto]` | Full init: questions → research → requirements → roadmap |
| `/gsd:discuss-phase [N]` | Capture implementation decisions before planning |
| `/gsd:plan-phase [N]` | Research + plan + verify for a phase |
| `/gsd:execute-phase <N>` | Execute plans in parallel waves |
| `/gsd:verify-work [N]` | User acceptance testing |
| `/gsd:complete-milestone` | Archive milestone, tag release |
| `/gsd:new-milestone [name]` | Start next version |
| `/gsd:quick` | Ad-hoc task with GSD guarantees |
| `/gsd:map-codebase` | Analyze existing codebase |
| `/gsd:progress` | Current position and next steps |
| `/gsd:debug [desc]` | Systematic debugging with persistent state |
| `/gsd:settings` | Configure model profile and workflow agents |
| `/gsd:set-profile <profile>` | Switch model profile |
| `/gsd:add-phase` | Append phase to roadmap |
| `/gsd:insert-phase [N]` | Insert urgent work (decimal numbering) |
| `/gsd:remove-phase [N]` | Remove future phase, renumber |
| `/gsd:pause-work` / `/gsd:resume-work` | Session handoff and restore |
| `/gsd:add-todo` / `/gsd:check-todos` | Capture and review ideas |
| `/gsd:help` | Show all commands |

## Architecture

### Multi-Agent Orchestration

Thin orchestrator spawns specialized agents, collects results, routes to next step. Orchestrator never does heavy lifting — main context stays at 30–40%.

| Agent | Role |
|-------|------|
| `gsd-project-researcher` | Research domain ecosystem (4 parallel: stack, features, architecture, pitfalls) |
| `gsd-research-synthesizer` | Synthesize parallel research into SUMMARY.md |
| `gsd-roadmapper` | Create roadmap with requirement mapping and success criteria |
| `gsd-phase-researcher` | Research implementation approaches for a specific phase |
| `gsd-planner` | Create atomic XML task plans |
| `gsd-plan-checker` | Verify plans achieve phase goals (revision loop, max 3 iterations) |
| `gsd-executor` | Implement plans in fresh 200k context windows |
| `gsd-verifier` | Goal-backward verification — checks outcomes, not just task completion |
| `gsd-debugger` | Systematic debugging with persistent state |
| `gsd-codebase-mapper` | Analyze existing codebase structure and patterns |
| `gsd-integration-checker` | Check cross-phase integration |

### Model Profiles

| Profile | Planning | Execution | Verification |
|---------|----------|-----------|--------------|
| `quality` | Opus | Opus | Sonnet |
| `balanced` (default) | Opus | Sonnet | Sonnet |
| `budget` | Sonnet | Sonnet | Haiku |

Switch with `/gsd:set-profile <profile>` or edit `.planning/config.json`.

### XML Plan Format

```xml
<task type="auto">
  <name>Create login endpoint</name>
  <files>src/app/api/auth/login/route.ts</files>
  <action>
    Use jose for JWT. Validate credentials against users table.
    Return httpOnly cookie on success.
  </action>
  <verify>curl -X POST localhost:3000/api/auth/login returns 200 + Set-Cookie</verify>
  <done>Valid credentials return cookie, invalid return 401</done>
</task>
```

### Planning Directory Structure

```
.planning/
├── PROJECT.md          # Vision, core value, requirements, constraints, decisions
├── REQUIREMENTS.md     # Checkable requirements with v1/v2 scoping
├── ROADMAP.md          # Phases with goals, dependencies, success criteria
├── STATE.md            # Living memory — position, metrics, blockers (<100 lines)
├── config.json         # Settings (mode, depth, profile, agents, git)
├── research/           # Domain research (STACK, FEATURES, ARCHITECTURE, PITFALLS, SUMMARY)
├── codebase/           # Codebase analysis from /gsd:map-codebase
├── phases/NN-slug/     # Per-phase: CONTEXT, RESEARCH, PLAN, SUMMARY, VERIFICATION, UAT
├── quick/              # Ad-hoc task tracking
└── todos/              # Captured ideas
```

## Configuration

Stored in `.planning/config.json`. Configure via `/gsd:settings`.

| Setting | Options | Default |
|---------|---------|---------|
| `mode` | `yolo`, `interactive` | `interactive` |
| `depth` | `quick`, `standard`, `comprehensive` | `standard` |
| `model_profile` | `quality`, `balanced`, `budget` | `balanced` |
| `workflow.research` | `true`/`false` | `true` |
| `workflow.plan_check` | `true`/`false` | `true` |
| `workflow.verifier` | `true`/`false` | `true` |
| `parallelization.enabled` | `true`/`false` | `true` |
| `planning.commit_docs` | `true`/`false` | `true` |
| `git.branching_strategy` | `none`, `phase`, `milestone` | `none` |

## gsd-tools.js CLI

Centralizes deterministic operations. See `references/gsd-tools-reference.md` for full command list.

Key commands:

```bash
node ~/.claude/get-shit-done/bin/gsd-tools.js state load
node ~/.claude/get-shit-done/bin/gsd-tools.js init <command> [args]
node ~/.claude/get-shit-done/bin/gsd-tools.js phase add|insert|remove|complete <args>
node ~/.claude/get-shit-done/bin/gsd-tools.js roadmap get-phase|analyze <args>
node ~/.claude/get-shit-done/bin/gsd-tools.js commit <message> --files <f1> <f2>
node ~/.claude/get-shit-done/bin/gsd-tools.js progress [json|table|bar]
node ~/.claude/get-shit-done/bin/gsd-tools.js verify plan-structure|phase-completeness <args>
```

## Design Principles

1. **Fresh context per plan** — each task gets 200k tokens, zero accumulated garbage
2. **Orchestrator stays lean** — spawns agents, integrates results, never does heavy lifting
3. **Atomic git commits** — one commit per task, independently revertable, bisect-friendly
4. **Goal-backward verification** — verify outcomes exist and work, not just that tasks ran
5. **Dream extraction** — collaborative thinking, not checklist interrogation
6. **Complexity in the system** — user sees simple commands, system handles orchestration

## Applying GSD Principles in Manus

When structuring complex development tasks within Manus:

1. **Break work into phases** with clear goals and success criteria
2. **Use fresh context isolation** — delegate atomic subtasks to parallel workers
3. **Create structured planning docs** (PROJECT.md, REQUIREMENTS.md, ROADMAP.md) for large projects
4. **Verify outcomes, not tasks** — check that deliverables actually work, not just that code was written
5. **Extract the vision first** — ask until you understand what the user wants before building

## Troubleshooting

- **Commands not found:** Restart Claude Code; verify files in `~/.claude/commands/gsd/`
- **Docker:** Set `CLAUDE_CONFIG_DIR=/home/user/.claude` before installing
- **Update:** `npx get-shit-done-cc@latest`
- **Uninstall:** `npx get-shit-done-cc --claude --global --uninstall`
