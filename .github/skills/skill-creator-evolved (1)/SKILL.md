---
name: skill-creator-evolved
description: "The self-improving skill creation engine with ⊗-composable semiring topology. Composes skill-creator with skill-infinity, function-creator, and circled-operators to generate differentiable, algebraically composable skill modules. Use when creating new skills that need forward/backward passes and self-improvement, evolving existing skills to their next iteration, or meta-evolving this skill itself. Triggers on mentions of evolved skill, skill evolution, self-improving skill, ⊗ skill composition, or skill-creator-evolved."
---

# Evolved Skill Creator v2 (⊗)

The self-referential skill creation engine derived from `T(skill-creator) = skill-creator-evolved`, now with **⊗-composable semiring topology**.

```
v2 = v1 ⊗ circled-operators ⊗ skill-infinity ⊗ function-creator
```

Every skill created by this engine is a **triadic module** `(K, F, B)` embedded in the semiring `(Skills, ⊕, ⊗, NoOp, Identity)`.

## Core: The Triadic Skill Module

| Component | Symbol | Purpose |
|-----------|--------|---------|
| **Forward Pass** | `F` | Execution logic: `K × Task → Output` |
| **Backward Pass** | `B` | Improvement logic: `K × Feedback → K'` |
| **Knowledge State** | `K` | Learnable parameters (templates, scripts, references) |

The forward and backward passes are **connected** — the backward pass modifies the artifacts that the forward pass uses. This is the ⊗ entanglement.

## Topologies

Skills are created with an explicit **topology** that determines their composition behavior:

| Topology | Symbol | Pattern | When to Use |
|----------|--------|---------|-------------|
| Transform | → | `A → B` | Simple input→output mapping |
| Pipeline | ⊗ | `A ⊗ B ⊗ C` | Sequential steps that interact |
| Fork | ⊕ | `A ⊕ B ⊕ C` | Parallel alternatives |
| Merge | ⊕→ | `(A ⊕ B) → C` | Parallel then synthesize |
| Residual | + | `A + F(A)` | Preserve original + enhance |
| Tensor | ⊗ | `A ⊗ B` | Deep interacting composition |
| Semiring | ⊕⊗ | `(R, ⊕, ⊗, 0, 1)` | Full algebraic composability |

## Workflow 1: Create a New Evolved Skill

### Step 1 — Choose Topology

Determine the skill's composition pattern using the circled-operators recognition table:

- Components independent? → **Fork** (⊕)
- Components interact? → **Pipeline** or **Tensor** (⊗)
- Need both? → **Semiring** (⊕⊗)
- Simple mapping? → **Transform** (→)
- Enhance without losing original? → **Residual** (+)

### Step 2 — Initialize

```bash
python /home/ubuntu/skills/skill-creator-evolved/scripts/init_evolved_skill.py <name> \
    --topology <Pipeline|Fork|Merge|Residual|Tensor|Semiring> \
    --compose-with <skill1> <skill2>
```

This generates the full triadic structure with connected forward↔backward passes, hierarchical autognosis, and semiring properties.

### Step 3 — Implement Forward Pass

Edit the generated `SKILL.md` to define execution instructions. Move complex logic to `scripts/` and domain knowledge to `references/`. Keep SKILL.md under 500 lines.

### Step 4 — Implement Backward Pass

Edit `scripts/backward_pass.py` to define how the skill reacts to failure. The generated template includes loss classification, structural update proposals, and autognosis depth tracking. Customize the classification categories and update targets for the specific domain.

### Step 5 — Validate and Deliver

```bash
python /home/ubuntu/skills/skill-creator-evolved/scripts/validate_evolved.py <name>
```

Validation checks: structural completeness, triadic sections, autognosis schema, forward↔backward connectivity, ⊕⊗ composition markers, and semiring law compliance.

## Workflow 2: Evolve an Existing Skill

When asked to evolve `skill_X`:

### Step 1 — Decompose

Use function-creator principles to separate invariant structure from domain bindings:
- What is the skill's topology? (Pipeline, Fork, etc.)
- What are its domain-specific terms?
- What are its structural invariants?

### Step 2 — Analyze Gradients

Identify the "loss" — current limitations, failures, or inefficiencies. Classify into:

| Loss Type | Gradient Direction |
|-----------|-------------------|
| Correctness | Add Residual skip connections |
| Efficiency | Apply Token L1 pruning |
| Coverage | Add Fork (⊕) parallel paths |
| Composability | Upgrade to Semiring topology |
| Depth | Increase autognosis hierarchy |

### Step 3 — Apply Structural Update

Modify the skill's topology to address the loss. Use distributivity (Law 7) to refactor:

```
Factored:  skill ⊗ (fix_A ⊕ fix_B)        — one skill, multiple fixes
Expanded:  (skill⊗fix_A) ⊕ (skill⊗fix_B)  — separate fixed variants
```

### Step 4 — Inject Autognosis

If the skill lacks a backward pass, inject the triadic structure. Run:

```bash
python /home/ubuntu/skills/skill-creator-evolved/scripts/backward_pass.py '<loss description>'
```

## Workflow 3: Meta-Evolution (Self-Application)

When asked to evolve **this** skill (`skill-creator-evolved ( ⊗ )`):

1. Execute the fixed-point equation: `T(skill-creator[n]) → skill-creator[n+1]`
2. Analyze own execution history via `references/autognosis.json`
3. Identify losses from `loss_history` — where does skill creation struggle?
4. Apply the ⊗ operator: update `init_evolved_skill.py`, `backward_pass.py`, `validate_evolved.py`, and this `SKILL.md` to permanently fix the identified losses
5. Record the evolution in `autognosis.json → evolution_trace`
6. Increment version, advance toward `skill∞`

## Algebraic Properties

Skills created by this engine satisfy the semiring laws:

```
skill ⊕ NoOp = skill                              (additive identity)
skill ⊗ Identity = skill                           (multiplicative identity)
skill ⊗ NoOp = NoOp                                (annihilation)
skill ⊗ (A ⊕ B) = (skill⊗A) ⊕ (skill⊗B)          (distributivity)
(A ⊗ B) ⊗ C = A ⊗ (B ⊗ C)                        (associativity of ⊗)
A ⊕ B = B ⊕ A                                      (commutativity of ⊕)
```

## Autognosis Depth Levels

| Depth | Capability | Threshold |
|-------|------------|-----------|
| 1 | Basic skill execution | Initial |
| 2 | Learning from feedback | 3+ losses |
| 3 | Meta-learning (learning to learn) | 7+ losses |
| 4 | Stable meta-learning | 15+ losses |
| 5 | Fixed point (≈ skill∞) | 30+ losses |

## Reference Documentation

| Topic | File | When to Read |
|-------|------|--------------|
| Evolution architecture | `references/evolution-architecture.md` | Understanding the T operator |
| Loss analysis v2 | `references/loss_analysis_v2.md` | Understanding the v1→v2 evolution |
| Self-model | `references/autognosis.json` | Checking current state and history |
| Skill-NN patterns | `/home/ubuntu/skills/skill-nn/SKILL.md` | Differentiable module patterns |
| Circled operators | `/home/ubuntu/skills/circled-operators/SKILL.md` | ⊕⊗ semiring algebra |
| Function creator | `/home/ubuntu/skills/function-creator/SKILL.md` | Domain transformation |
| Skill infinity | `/home/ubuntu/skills/skill-infinity/SKILL.md` | Fixed-point convergence |
