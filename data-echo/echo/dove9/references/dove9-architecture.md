# Dove9 Architecture Reference

Use this reference when the task needs deeper architectural grounding than the main skill body provides.

## Core Thesis

Treat the repository as an "Everything is a Chatbot" operating system:

- The mail server is the CPU.
- Messages are process threads.
- Inference is feedforward.
- Learning is feedback.
- Components should behave like conversational entities with inboxes and outboxes.

## Triadic Cognitive Loop

The core Dove9 rhythm is a 12-step loop across three streams:

| Stream | Phase | Typical role |
| --- | --- | --- |
| `PRIMARY` | `0deg` | immediate cognitive progression |
| `SECONDARY` | `120deg` | phase-shifted companion processing |
| `TERTIARY` | `240deg` | memory/action balancing across the cycle |

The cycle has four convergence points where all three streams are integrated together.

### Cognitive terms

Only these terms are currently active in the Dove9 model:

| Term | Meaning |
| --- | --- |
| `T1_PERCEPTION` | relevance detection and salience parsing |
| `T2_IDEA_FORMATION` | hypothesis and concept assembly |
| `T4_SENSORY_INPUT` | environmental intake and feature extraction |
| `T5_ACTION_SEQUENCE` | action planning and output sequencing |
| `T7_MEMORY_ENCODING` | episodic and semantic consolidation |
| `T8_BALANCED_RESPONSE` | integrated, tension-balanced response |

Do not invent `T3` or `T6` behavior without explicit architectural justification.

### Modes

- Expressive mode emphasizes acting, planning, and output.
- Reflective mode emphasizes simulation, salience, and memory consolidation.

## Tensional Couplings

Key cross-stream relationships:

- `T4E <-> T7R`: perception and memory tension each other.
- `T1R <-> T2E`: reflective assessment informs planning.
- `T8E`: balanced integration resolves multi-stream tension into action.

Use these couplings as guidance when deciding whether a feature belongs in a single component or at an integration point.

## Sys6 Operadic Model

The triadic loop sits inside a broader scheduling system:

- `D`: dyadic channel
- `T`: triadic channel
- `P`: pentadic stage
- `C8`: cubic concurrency
- `K9`: triadic convolution bundle
- `Clock30`: global 30-step synchronization frame

Practical rule: if a feature introduces new periodic behavior, verify it composes intentionally with the 30-step clock.

## Repository Map

| Path | Responsibility |
| --- | --- |
| `dove9/` | triadic cognitive kernel |
| `deep-tree-echo-core/` | LLM services, memory, personality |
| `deep-tree-echo-orchestrator/` | executive daemon, interfaces, scheduler, telemetry |
| `packages/cognitive/` | unified cognitive API |
| `packages/reasoning/` | AtomSpace, PLN, MOSES, OpenPsi, ECAN, distributed reasoning |
| `packages/shared/` | shared types, logger, utilities |
| `packages/ui-components/` | shared UI surfaces |
| `packages/sys6-triality/` | operadic and scheduling implementation |
| `delta-echo-desk/` | desktop AI companion surface |
| `deltecho2/` | desktop Inferno kernel surface |
| `dovecot-core/` | mail server substrate treated as CPU |

## Build Order

Respect this dependency order when reasoning about builds:

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

## Implementation Heuristics

- Expose new cognitive capabilities through `@deltecho/cognitive`.
- Store durable cognitive knowledge in AtomSpace or memory systems, not scattered local state.
- Model external integrations as message processes.
- Emit observable system state through telemetry-compatible logging.
- Favor coherence across packages over short-term convenience in a single module.
