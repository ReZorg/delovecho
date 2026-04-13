# Skill Containers

Containers compose multiple skills into complex architectures.

## sk.Pipeline (Sequential)

Execute skills in sequence, passing output to next input.

```
task → [skill₁] → [skill₂] → [skill₃] → output
```

### Constructor

```python
pipeline = sk.Pipeline()
```

### Methods

#### add(skill)

Append skill to pipeline.

```python
pipeline.add(sk.Skill("research"))
pipeline.add(sk.Skill("analyze"))
pipeline.add(sk.Skill("synthesize"))
```

#### insert(index, skill)

Insert skill at position.

```python
pipeline.insert(1, sk.Skill("validate"))
```

#### remove(index)

Remove skill at position.

```python
pipeline.remove(2)
```

### Forward Pass

```python
output = pipeline.forward(task)
# Equivalent to:
# x = skill₁.forward(task)
# x = skill₂.forward(x)
# x = skill₃.forward(x)
# output = x
```

### Backward Pass

```python
gradient = pipeline.backward(feedback)
# Gradients flow backward through chain
```

### Example: Document Creation Pipeline

```python
doc_pipeline = sk.Pipeline()
doc_pipeline.add(sk.Skill("understand-requirements"))
doc_pipeline.add(sk.Skill("research-topic"))
doc_pipeline.add(sk.Skill("create-outline"))
doc_pipeline.add(sk.Skill("write-draft"))
doc_pipeline.add(sk.Skill("review-edit"))
doc_pipeline.add(sk.Skill("format-deliver"))

document = doc_pipeline.forward(task)
```

## sk.Fork (Parallel)

Split input, run skills in parallel, merge outputs.

```
        ┌→ [skill₁] →┐
task →──┼→ [skill₂] →┼→ merged_output
        └→ [skill₃] →┘
```

### Constructor

```python
fork = sk.Fork(split_by="dimension", merge_by="concat")
```

| Argument | Options | Description |
|----------|---------|-------------|
| `split_by` | "dimension", "aspect", "copy" | How to split input |
| `merge_by` | "concat", "sum", "vote", "synthesize" | How to merge outputs |

### Split Strategies

#### "dimension"
Split task along a dimension (like nn.Parallel).

```python
fork = sk.Fork(split_by="dimension")
# Task with 3 aspects → each skill gets 1 aspect
```

#### "aspect"
Split by semantic aspects of task.

```python
fork = sk.Fork(split_by="aspect")
# "Research X" → technical, market, competitor aspects
```

#### "copy"
Each skill gets full copy (like nn.Concat).

```python
fork = sk.Fork(split_by="copy")
# All skills see same input
```

### Merge Strategies

#### "concat"
Concatenate outputs.

```python
fork = sk.Fork(merge_by="concat")
# [out₁, out₂, out₃] → combined output
```

#### "sum"
Sum outputs (for numeric).

```python
fork = sk.Fork(merge_by="sum")
# out₁ + out₂ + out₃
```

#### "vote"
Majority vote (for classification).

```python
fork = sk.Fork(merge_by="vote")
# Most common output wins
```

#### "synthesize"
Intelligent synthesis of outputs.

```python
fork = sk.Fork(merge_by="synthesize")
# AI-powered merging of perspectives
```

### Example: Multi-Perspective Analysis

```python
analysis = sk.Fork(split_by="copy", merge_by="synthesize")
analysis.add(sk.Skill("quantitative-analysis"))
analysis.add(sk.Skill("qualitative-analysis"))
analysis.add(sk.Skill("comparative-analysis"))

comprehensive = analysis.forward(task)
```

## sk.Merge (Concat)

Same input to all skills, merge outputs.

```
        ┌→ [skill₁] →┐
task →──┼→ [skill₂] →┼→ merged_output
        └→ [skill₃] →┘
```

Equivalent to `sk.Fork(split_by="copy")`.

### Constructor

```python
merge = sk.Merge(combine="synthesize")
```

### Example: Ensemble Skills

```python
ensemble = sk.Merge(combine="vote")
ensemble.add(sk.Skill("approach-a"))
ensemble.add(sk.Skill("approach-b"))
ensemble.add(sk.Skill("approach-c"))

# Best approach wins
result = ensemble.forward(task)
```

## sk.Residual (Skip Connection)

Add input to skill output.

```
task →──┬→ [skill] →──┬→ output
        └─────────────┘
        output = task + skill(task)
```

### Constructor

```python
residual = sk.Residual(skill)
```

### Purpose

- Preserve original information
- Enable gradient flow
- Allow skill to focus on "delta"

### Example: Enhancement Layer

```python
enhance = sk.Residual(sk.Skill("elaborate"))
# Output = original + elaboration

# Chain multiple residual blocks
deep = sk.Pipeline()
deep.add(sk.Residual(sk.Skill("enhance-1")))
deep.add(sk.Residual(sk.Skill("enhance-2")))
deep.add(sk.Residual(sk.Skill("enhance-3")))
```

## sk.Conditional (Branching)

Route to different skills based on condition.

```
        ┌→ [skill_a] (if condition)
task →──┤
        └→ [skill_b] (else)
```

### Constructor

```python
conditional = sk.Conditional(condition_fn)
conditional.add_branch("true", skill_a)
conditional.add_branch("false", skill_b)
```

### Example: Task Router

```python
def task_type(task):
    if "code" in task.content:
        return "coding"
    elif "write" in task.content:
        return "writing"
    else:
        return "general"

router = sk.Conditional(task_type)
router.add_branch("coding", sk.Skill("code-assistant"))
router.add_branch("writing", sk.Skill("writing-assistant"))
router.add_branch("general", sk.Skill("general-assistant"))
```

## sk.Loop (Iteration)

Repeat skill until condition met.

```
task → [skill] → check → [skill] → check → ... → output
         ↑_________↓        ↑_________↓
```

### Constructor

```python
loop = sk.Loop(skill, max_iterations=10, stop_condition=None)
```

### Example: Iterative Refinement

```python
def is_good_enough(output):
    return output.confidence > 0.9

refine = sk.Loop(
    sk.Skill("refine-output"),
    max_iterations=5,
    stop_condition=is_good_enough
)

refined = refine.forward(initial_draft)
```

## Container Nesting

Containers can contain other containers.

### Example: Complex Architecture

```python
# Research phase (parallel)
research = sk.Fork(split_by="aspect")
research.add(sk.Skill("technical-research"))
research.add(sk.Skill("market-research"))

# Analysis phase (sequential with residual)
analysis = sk.Pipeline()
analysis.add(sk.Skill("synthesize-research"))
analysis.add(sk.Residual(sk.Skill("add-insights")))

# Full workflow
workflow = sk.Pipeline()
workflow.add(sk.Skill("understand-task"))
workflow.add(research)
workflow.add(analysis)
workflow.add(sk.Skill("generate-report"))
workflow.add(sk.Loop(sk.Skill("refine"), max_iterations=3))
workflow.add(sk.Skill("deliver"))
```

## Container Methods Summary

| Method | Pipeline | Fork | Merge | Residual | Conditional | Loop |
|--------|----------|------|-------|----------|-------------|------|
| `add(skill)` | ✓ | ✓ | ✓ | - | - | - |
| `insert(i, skill)` | ✓ | - | - | - | - | - |
| `remove(i)` | ✓ | - | - | - | - | - |
| `add_branch(key, skill)` | - | - | - | - | ✓ | - |
| `forward(task)` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `backward(feedback)` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
