# Skill Module API Reference

## Base Class: sk.Skill

The fundamental building block of skill-nn. Every skill is a module.

### Constructor

```python
skill = sk.Skill(name, parameters=None)
```

| Argument | Type | Description |
|----------|------|-------------|
| `name` | str | Skill identifier |
| `parameters` | dict | Initial skill knowledge (optional) |

### Core Methods

#### forward(task) → Output

Execute the skill on a task.

```python
output = skill.forward(task)
```

| Argument | Type | Description |
|----------|------|-------------|
| `task` | Task | Input task to process |
| **Returns** | Output | Skill execution result |

**Side effects**: Updates `skill.output`

#### backward(feedback) → Gradient

Compute improvement gradient from feedback.

```python
gradient = skill.backward(feedback)
```

| Argument | Type | Description |
|----------|------|-------------|
| `feedback` | Feedback | Signal about output quality |
| **Returns** | Gradient | Improvement direction |

**Side effects**: Updates `skill.gradInput`, accumulates `skill.gradParameters`

#### zero_grad()

Reset accumulated gradients.

```python
skill.zero_grad()
```

#### update(learning_rate)

Apply accumulated gradients to skill parameters.

```python
skill.update(learning_rate)
```

| Argument | Type | Description |
|----------|------|-------------|
| `learning_rate` | float | Step size for update |

#### parameters() → SkillKnowledge

Return learnable skill content.

```python
params = skill.parameters()
```

| Returns | Type | Description |
|---------|------|-------------|
| params | SkillKnowledge | SKILL.md content, templates, etc. |

#### grad_parameters() → Gradient

Return accumulated gradients.

```python
grads = skill.grad_parameters()
```

### State Variables

| Variable | Type | Description |
|----------|------|-------------|
| `skill.output` | Output | Result of last `forward()` |
| `skill.gradInput` | Gradient | Gradient w.r.t. input task |
| `skill.training` | bool | Whether in training mode |

### Utility Methods

#### train() / eval()

Set training/evaluation mode.

```python
skill.train()  # Enable training mode
skill.eval()   # Enable evaluation mode
```

#### clone(share_params=False)

Create a copy of the skill.

```python
skill_copy = skill.clone(share_params=True)
```

#### to_dict() / from_dict()

Serialize/deserialize skill.

```python
data = skill.to_dict()
skill = sk.Skill.from_dict(data)
```

## Transform Modules

### sk.Transform

Linear transformation between task spaces.

```python
transform = sk.Transform(input_space, output_space)
```

Analogous to `nn.Linear`. Maps tasks from one domain to another.

### sk.Embed

Embed discrete task types into continuous space.

```python
embed = sk.Embed(num_task_types, embedding_dim)
```

Analogous to `nn.Embedding`. Useful for task categorization.

## Transfer Functions

### sk.Bound

Constrain output to valid range.

```python
bound = sk.Bound(min_length=0, max_length=1000)
```

### sk.Threshold

Zero out low-confidence outputs.

```python
threshold = sk.Threshold(confidence=0.5)
```

### sk.Normalize

Standardize output format.

```python
normalize = sk.Normalize(format="markdown")
```

### sk.Dropout

Randomly skip processing (training only).

```python
dropout = sk.Dropout(p=0.1)
```

## Container Modules

See `references/containers.md` for detailed container documentation.

### sk.Pipeline

Sequential skill execution.

```python
pipeline = sk.Pipeline()
pipeline.add(skill1)
pipeline.add(skill2)
```

### sk.Fork

Parallel skill execution with input splitting.

```python
fork = sk.Fork(split_by="aspect")
fork.add(skill1)
fork.add(skill2)
```

### sk.Merge

Same input to multiple skills, merge outputs.

```python
merge = sk.Merge(combine="synthesize")
merge.add(skill1)
merge.add(skill2)
```

### sk.Residual

Skip connection: output = input + skill(input).

```python
residual = sk.Residual(skill)
```

## Criterion Modules

See `references/training.md` for training details.

### sk.TaskCompletionCriterion

Measures if task goal was achieved.

```python
criterion = sk.TaskCompletionCriterion()
loss = criterion.forward(output, target_goal)
```

### sk.TokenEfficiencyCriterion

L1 penalty on skill verbosity.

```python
criterion = sk.TokenEfficiencyCriterion(lambda_=0.01)
```

### sk.UserSatisfactionCriterion

Loss from user feedback signals.

```python
criterion = sk.UserSatisfactionCriterion()
```

### sk.MultiCriterion

Weighted combination of criteria.

```python
multi = sk.MultiCriterion()
multi.add(criterion1, weight=1.0)
multi.add(criterion2, weight=0.5)
```

## Factory Functions

### sk.from_skill_md(path)

Load skill from SKILL.md file.

```python
skill = sk.from_skill_md("/home/ubuntu/skills/my-skill/SKILL.md")
```

### sk.compose(*skills)

Create pipeline from multiple skills.

```python
pipeline = sk.compose(skill1, skill2, skill3)
```

### sk.parallel(*skills)

Create fork from multiple skills.

```python
fork = sk.parallel(skill1, skill2, skill3)
```

## Type Definitions

### Task

```python
@dataclass
class Task:
    content: str           # Task description
    context: dict          # Additional context
    constraints: list      # Output constraints
    metadata: dict         # Task metadata
```

### Output

```python
@dataclass
class Output:
    content: Any           # Primary output
    confidence: float      # Confidence score
    metadata: dict         # Output metadata
    trace: list            # Execution trace
```

### Feedback

```python
@dataclass
class Feedback:
    signal: float          # Scalar feedback (-1 to 1)
    details: str           # Textual feedback
    source: str            # Feedback source
    task_id: str           # Associated task
```

### Gradient

```python
@dataclass
class Gradient:
    direction: dict        # Parameter → update direction
    magnitude: float       # Update magnitude
    source: Feedback       # Originating feedback
```

### SkillKnowledge

```python
@dataclass
class SkillKnowledge:
    skill_md: str          # SKILL.md content
    templates: dict        # Template files
    references: dict       # Reference documents
    scripts: dict          # Executable scripts
```
