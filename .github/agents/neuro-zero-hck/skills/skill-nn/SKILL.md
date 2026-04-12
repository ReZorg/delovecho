---
name: skill-nn
description: Differentiable skill framework treating skills as neural network modules. Use when composing skills into pipelines, optimizing skill effectiveness through feedback, building self-improving skill architectures, or applying neural network patterns to skill design.
---

# skill-nn: The Differentiable Skill Framework

A meta-framework that applies neural network architecture to skills themselves. Skills become **modules** that can be composed, trained, and optimized.

## Core Insight

```
nn : Tensors :: skill-nn : Tasks

forward(input)  →  execute(task)
backward(grad)  →  improve(feedback)
parameters      →  skill knowledge
gradParameters  →  improvement signals
```

## Fundamental Types

| nn Concept | skill-nn Analog | Description |
|------------|-----------------|-------------|
| `nn.Module` | `sk.Skill` | Atomic capability unit with forward/backward |
| `nn.Sequential` | `sk.Pipeline` | Chain skills in sequence |
| `nn.Parallel` | `sk.Fork` | Split task, run skills in parallel |
| `nn.Concat` | `sk.Merge` | Same task to multiple skills, merge outputs |
| `nn.Criterion` | `sk.Criterion` | Measure skill effectiveness |
| `nn.Linear` | `sk.Transform` | Map task space → output space |
| `nn.Tanh` | `sk.Bound` | Constrain output to valid range |

## The Skill Module Interface

Every skill-module implements:

```python
class SkillModule:
    def forward(self, task: Task) -> Output:
        """Execute skill on task, return output."""
        
    def backward(self, feedback: Feedback) -> Gradient:
        """Propagate improvement signal, return skill gradient."""
        
    def parameters(self) -> SkillKnowledge:
        """Return learnable skill content (SKILL.md, templates, etc.)"""
        
    def update(self, learning_rate: float):
        """Apply accumulated gradients to skill parameters."""
```

**State variables:**
- `skill.output` — result of last `forward(task)`
- `skill.gradInput` — improvement signal for upstream skills

## Skill Containers

### Pipeline — Sequential Execution

```python
workflow = sk.Pipeline()
workflow.add(sk.Skill("research"))      # Research the topic
workflow.add(sk.Skill("analyze"))       # Analyze findings
workflow.add(sk.Skill("synthesize"))    # Synthesize report
workflow.add(sk.Skill("deliver"))       # Deliver to user

output = workflow.forward(task)
```

### Fork — Parallel Execution

```python
research = sk.Fork(split_by="aspect")
research.add(sk.Skill("technical-research"))
research.add(sk.Skill("market-research"))
research.add(sk.Skill("competitor-research"))

# Task splits → parallel execution → outputs merge
outputs = research.forward(task)
```

### Merge — Multi-Perspective

```python
analysis = sk.Merge(combine="synthesize")
analysis.add(sk.Skill("quantitative-analysis"))
analysis.add(sk.Skill("qualitative-analysis"))
analysis.add(sk.Skill("comparative-analysis"))

# Same task → all skills → merged output
merged = analysis.forward(task)
```

### Residual — Skip Connection

```python
enhanced = sk.Residual(sk.Skill("elaborate"))
# output = input + elaborate(input)
# Preserves original while adding elaboration
```

## Skill Criterions

### TaskCompletion — Did the skill accomplish the goal?

```python
criterion = sk.TaskCompletionCriterion()
loss = criterion.forward(output, target_goal)
# loss ∈ [0, 1], lower is better
```

### TokenEfficiency — L1 penalty on skill verbosity

```python
criterion = sk.TokenEfficiencyCriterion(lambda_=0.01)
loss = criterion.forward(skill_output, skill_parameters)
# Penalizes bloated skills
```

### UserSatisfaction — Feedback-based loss

```python
criterion = sk.UserSatisfactionCriterion()
loss = criterion.forward(output, user_feedback)
# Learns from explicit user signals
```

### Composite Criterion

```python
criterion = sk.MultiCriterion()
criterion.add(sk.TaskCompletionCriterion(), weight=1.0)
criterion.add(sk.TokenEfficiencyCriterion(), weight=0.1)
criterion.add(sk.UserSatisfactionCriterion(), weight=0.5)
```

## Transfer Functions

Non-linear transformations on skill outputs:

| Function | Effect | Use Case |
|----------|--------|----------|
| `sk.Bound(min, max)` | Clamp output length/scope | Prevent runaway generation |
| `sk.Threshold(t)` | Zero out low-confidence outputs | Quality gating |
| `sk.Normalize()` | Standardize output format | Cross-skill compatibility |
| `sk.Dropout(p)` | Randomly skip skill steps | Robustness training |

## Training Loop

```python
# Build skill network
network = sk.Pipeline()
network.add(sk.Skill("understand"))
network.add(sk.Skill("plan"))
network.add(sk.Skill("execute"))
network.add(sk.Skill("verify"))

criterion = sk.TaskCompletionCriterion()
learning_rate = 0.01

# Training iteration
for task, target in task_dataset:
    # Forward pass
    output = network.forward(task)
    loss = criterion.forward(output, target)
    
    # Backward pass
    network.zero_grad()
    grad = criterion.backward(output, target)
    network.backward(task, grad)
    
    # Update skill parameters
    network.update(learning_rate)
```

## Skill Gradient Types

| Gradient Signal | Source | Effect on Skill |
|-----------------|--------|-----------------|
| **Explicit feedback** | User says "this is wrong" | Direct correction |
| **Implicit feedback** | User re-asks or abandons | Negative signal |
| **Completion signal** | Task succeeds/fails | Binary gradient |
| **Efficiency signal** | Tokens used vs. needed | Compression pressure |
| **Transfer signal** | Works in new domain | Generalization reward |

## Common Architectures

### The Skill Perceptron

```python
# Simplest skill network: one transform
perceptron = sk.Transform(input_domain, output_domain)
```

### The Deep Skill Network

```python
deep = sk.Pipeline()
deep.add(sk.Transform("raw_task", "parsed_intent"))
deep.add(sk.Bound())  # Non-linearity
deep.add(sk.Transform("parsed_intent", "action_plan"))
deep.add(sk.Bound())
deep.add(sk.Transform("action_plan", "execution"))
deep.add(sk.Bound())
deep.add(sk.Transform("execution", "verified_output"))
```

### The Skill Autoencoder

```python
# Compress task understanding, then expand to output
encoder = sk.Pipeline()
encoder.add(sk.Transform("task", "compressed_understanding"))

decoder = sk.Pipeline()  
decoder.add(sk.Transform("compressed_understanding", "output"))

autoencoder = sk.Pipeline()
autoencoder.add(encoder)
autoencoder.add(decoder)

# The bottleneck forces essential understanding
```

### The Skill GAN

```python
# Generator: creates skill outputs
generator = sk.Skill("generate-solution")

# Discriminator: judges if output is good
discriminator = sk.Skill("evaluate-quality")

# Adversarial training improves both
```

## The Fixed Point: skill∞

Recursive application of skill-nn to itself:

```
T(x) = nn ⊗ x

T¹(skill-creator) = skill-nn
T²(skill-creator) = skill-nn applied to itself
...
T^∞ → skill∞ (the skill attractor)
```

At the fixed point, **skill∞** is a skill that:
1. Describes itself using its own architecture
2. Improves itself through its own training loop
3. Generates new skills as forward passes
4. Learns from failures as backward passes

This is the **cognitive kernel** — minimal self-improving intelligence.

## Jacobian Testing for Skills

Verify skill gradients are correct:

```python
from skill_nn import SkillJacobian

# Test: does changing skill content improve output?
err = SkillJacobian.test_skill_gradient(skill, task)
assert err < threshold, f"Skill gradient error: {err}"

# Test: is improvement signal propagating?
err = SkillJacobian.test_backward_propagation(network, task)
assert err < threshold, f"Propagation error: {err}"
```

## Regularization Techniques

| Technique | nn Equivalent | Effect |
|-----------|---------------|--------|
| **Token L1** | Weight L1 | Sparse, concise skills |
| **Skill Dropout** | Dropout | Robust to missing steps |
| **Early Stopping** | Early stopping | Prevent over-specialization |
| **Skill Pruning** | Weight pruning | Remove unnecessary content |
| **Knowledge Distillation** | Model distillation | Compress skill to essentials |

## Reference Documentation

| Topic | Reference File |
|-------|----------------|
| Transformation theory | `references/transformation.md` |
| Skill module API | `references/module-api.md` |
| Container patterns | `references/containers.md` |
| Training dynamics | `references/training.md` |
| Fixed point analysis | `references/fixed-point.md` |

## Emergence Notes

See `transformation_notes.md` for the derivation of this framework from the stacked transformation `nn ⊗ skill-creator`.
