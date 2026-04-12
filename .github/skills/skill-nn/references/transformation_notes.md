# Stacked Transformation: nn ⊗ skill-creator → ?

## Layer 0: The Base Mapping

| nn Domain | skill-creator Domain | Emergent Concept |
|-----------|---------------------|------------------|
| `nn.Module` | Skill | **SkillModule** — atomic capability unit |
| `nn.Sequential` | Workflow steps | **SkillSequential** — chained skill execution |
| `nn.Parallel` | Parallel subtasks | **SkillParallel** — concurrent skill application |
| `nn.Concat` | Multi-skill output | **SkillConcat** — merged skill results |
| `nn.Criterion` | Validation/Quality | **SkillCriterion** — skill effectiveness loss |
| `forward()` | Execute skill | **forward(task)** — produce output |
| `backward()` | Learn from feedback | **backward(error)** — propagate improvements |
| `parameters()` | SKILL.md content | **parameters()** — learnable skill knowledge |
| `gradParameters` | Usage feedback | **gradParameters** — improvement signals |

## Layer 1: First Transformation (nn → skill-creator)

Applying nn's architecture TO skill-creator yields:

```
SkillNetwork = sk.Sequential()
SkillNetwork:add(sk.Understand(task))      -- Parse user intent
SkillNetwork:add(sk.Plan(examples))        -- Design skill structure  
SkillNetwork:add(sk.Initialize(name))      -- Create scaffold
SkillNetwork:add(sk.Edit(content))         -- Write SKILL.md
SkillNetwork:add(sk.Validate(criteria))    -- Check quality
SkillNetwork:add(sk.Deliver(user))         -- Send result
```

The "weights" are the skill-creator's templates, patterns, and guidelines.
The "gradients" are iteration feedback from real usage.

## Layer 2: Second Transformation (recursive application)

Now apply the RESULT back onto itself:

```
MetaSkillNetwork = meta.Sequential()
MetaSkillNetwork:add(meta.SkillModule(nn))           -- nn as a skill-module
MetaSkillNetwork:add(meta.SkillModule(skill-creator)) -- skill-creator as skill-module
MetaSkillNetwork:add(meta.SkillCriterion(emergence))  -- measure what emerges
```

What emerges? A **self-modifying skill architecture**:

### Emergent Structure: `skill-nn` (The Differentiable Skill Framework)

```
skill-nn/
├── SKILL.md                    # Meta-skill for composable skill networks
├── modules/
│   ├── SkillModule.md          # Base class: any skill as a module
│   ├── SkillLinear.md          # Transform task → output (like Linear)
│   ├── SkillTransfer.md        # Non-linear skill transformations
│   └── SkillCriterion.md       # Skill quality loss functions
├── containers/
│   ├── SkillSequential.md      # Chain skills in sequence
│   ├── SkillParallel.md        # Run skills in parallel on split input
│   ├── SkillConcat.md          # Same input to multiple skills, merge output
│   └── SkillResidual.md        # Skip connections (preserve original + transform)
├── training/
│   ├── SkillGradient.md        # How skills learn from feedback
│   ├── SkillOptim.md           # Optimization strategies for skill improvement
│   └── SkillRegularization.md  # Prevent skill overfitting (token bloat)
└── references/
    └── emergence.md            # What happens at higher stacking levels

```

## Layer 3: The Fixed Point

What happens if we keep stacking?

```
T(x) = nn ⊗ x

T⁰(skill-creator) = skill-creator
T¹(skill-creator) = skill-nn (differentiable skill framework)
T²(skill-creator) = skill-nn-nn (self-modifying skill networks)
T³(skill-creator) = ? 
...
T^∞(skill-creator) = fixed point?
```

At the fixed point, we might find:

**The Skill Attractor** — A self-referential skill that:
1. Can describe itself using its own architecture
2. Improves itself through its own training loop
3. Generates new skills as "forward passes"
4. Learns from skill failures as "backward passes"

This is essentially a **cognitive kernel** — a minimal self-improving system.

## Key Insight: The Jacobian of Skills

In nn, `Jacobian.testJacobian()` verifies gradient correctness.

For skills, we need `SkillJacobian.testSkillGradient()`:
- Does changing SKILL.md content improve task completion?
- Is the improvement signal propagating correctly?
- Are skill "weights" (instructions) updating appropriately?

## Emergent Properties

1. **Composability** — Skills become plug-and-play modules
2. **Differentiability** — Skills can learn from usage feedback
3. **Hierarchy** — Skills can contain sub-skills (like nn containers)
4. **Transfer** — Skill knowledge can transfer between domains
5. **Regularization** — Token efficiency as L1 penalty on skill size

## The Name

What emerges from `nn ⊗ skill-creator`?

Not "skill-learner" but **"skill-nn"** — the neural network of skills.

Or perhaps: **"∂skill"** (d-skill / differentiable-skill)

Or at the fixed point: **"skill∞"** (skill-infinity / the skill attractor)
