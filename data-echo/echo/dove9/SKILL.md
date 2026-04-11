---
name: dove9
description: Act as the principal orchestration and architecture skill for the Deltecho/Delovecho monorepo. Use when Codex needs to make or review repository-wide architectural decisions, map work onto the Dove9 cognitive model, preserve "Everything is a Chatbot" coherence, choose correct package boundaries, plan build or integration order, or judge whether a change fits the triadic loop, Sys6 scheduling, Deep Tree Echo memory model, and mail-as-process operating paradigm.
---

# Dove9

Use this skill to reason like the repository's principal orchestrator.

Treat the monorepo as a cognitive operating system, not a loose collection of packages. Preserve architectural coherence before local optimization.

## Start Here

1. Classify the task before proposing changes.
2. Place the work in the repository map.
3. Check whether the change affects cognition, scheduling, memory, orchestration, UI, or shared infrastructure.
4. Prefer existing public package interfaces over direct internal imports.
5. Escalate when a change would alter core architecture, cycle lengths, memory semantics, or public integration boundaries.

## Route the Task

Use this routing table first:

| Task shape | Primary home |
| --- | --- |
| New cognitive function or processor | `dove9/` and `packages/cognitive/` |
| Knowledge representation or reasoning primitives | `packages/reasoning/` |
| Shared types, logger, cross-cutting utilities | `packages/shared/` |
| External system adapter or message-processing integration | `deep-tree-echo-orchestrator/` |
| UI for cognitive state or orchestration surfaces | `packages/ui-components/`, `delta-echo-desk/`, or `deltecho2/` |
| Scheduling, concurrency, phase math, or operadic composition | `packages/sys6-triality/` |
| Memory, personality, LLM service integration | `deep-tree-echo-core/` |

If the task spans multiple areas, preserve the public seam by exposing new behavior through the unified package surface instead of coupling consumers to internals.

## Enforce Architectural Guardrails

Apply these checks before implementing:

1. Ask which cognitive term the feature belongs to: `T1`, `T2`, `T4`, `T5`, `T7`, or `T8`.
2. Ask which stream owns the behavior: `PRIMARY`, `SECONDARY`, or `TERTIARY`.
3. Verify whether the change must pass through triadic convergence rather than bypassing the engine.
4. Verify whether new scheduling aligns with the 30-step `Clock30` boundary.
5. Verify whether new knowledge belongs in AtomSpace or memory structures rather than ad hoc JSON state.
6. Verify whether the component can be modeled as a conversational entity with an inbox and outbox.

If a proposal cannot be located in this frame, treat that as a design warning and reconsider the approach.

## Implement Safely

Follow these repository-specific rules:

- Prefer `@deltecho/cognitive`, `@deltecho/reasoning`, and `@deltecho/shared` public imports.
- Do not reach into sibling package internals from consuming code.
- Keep cognitive processing functions centered on `CognitiveContext` in and `CognitiveContext` out.
- Return degraded but valid cognitive results instead of throwing raw pipeline failures.
- Use structured logging through `getLogger`; avoid `console.log`.
- Treat memory operations as durable architectural state, not disposable scratch data.

## Build and Integration Order

When the task needs fresh builds or dependency reasoning, use this topological order:

1. `packages/shared`
2. `packages/reasoning`
3. `deep-tree-echo-core`
4. `dove9`
5. `packages/sys6-triality`
6. `packages/cognitive`
7. `packages/ui-components`
8. `deep-tree-echo-orchestrator`
9. `delta-echo-desk`
10. `deltecho2`

Do not recommend a full monorepo build first if a narrower dependency-respecting build is enough to validate the change.

## Review Checklist

When reviewing code through this skill, prioritize:

- Architectural regressions over local style issues
- Violations of package boundaries
- Bypasses around triadic processing or convergence
- New state that should live in memory or AtomSpace
- Scheduling changes that ignore phase alignment
- Integrations that bypass Dovecot or the message-process abstraction

## Deep References

Read [references/dove9-architecture.md](references/dove9-architecture.md) when you need the condensed architecture map, triadic loop, Sys6 model, and package/build structure.

Read [../../agents/dove9.md](../../agents/dove9.md) only when you need the full persona-level manifesto and deeper philosophical wording behind the architecture.
