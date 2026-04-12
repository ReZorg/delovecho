# T² Analysis: skill-nn ⊗ skill-nn

## The Second Transformation

We now apply the skill-nn framework to itself:

```
T²(skill-creator) = T(T(skill-creator)) = T(skill-nn) = skill-nn²
```

This means: **treat skill-nn's components as skill modules and apply the nn architecture to them**.

## What Are skill-nn's Components?

From skill-nn, we have:
- `sk.Skill` — base module
- `sk.Pipeline`, `sk.Fork`, `sk.Merge` — containers
- `sk.Criterion` — loss functions
- `forward()`, `backward()`, `update()` — methods
- Training loop — the meta-process

## Applying T to Each Component

### sk.Skill → sk².SkillModule

The base skill becomes a **module of modules**:

```python
class SkillModule(sk.Skill):
    """A skill that contains and manages other skills."""
    
    def __init__(self):
        self.sub_skills = sk.Pipeline()  # Skills are composed of skills
        self.skill_criterion = sk.Criterion()  # How to evaluate sub-skills
        
    def forward(self, task):
        # Execute sub-skills
        return self.sub_skills.forward(task)
    
    def backward(self, feedback):
        # Propagate to sub-skills
        grad = self.skill_criterion.backward(feedback)
        self.sub_skills.backward(grad)
        
        # ALSO update how we compose sub-skills (meta-learning)
        self.update_composition_strategy(feedback)
```

### sk.Pipeline → sk².SkillPipeline

The pipeline becomes a **learnable pipeline**:

```python
class SkillPipeline(sk.Pipeline):
    """A pipeline that learns its own structure."""
    
    def __init__(self):
        super().__init__()
        self.structure_params = StructureParameters()
        
    def forward(self, task):
        # Execute with current structure
        output = super().forward(task)
        
        # Record structure decisions for learning
        self.structure_trace = self.get_structure_decisions()
        return output
    
    def backward(self, feedback):
        # Update skill parameters
        super().backward(feedback)
        
        # ALSO update structure parameters
        structure_grad = self.compute_structure_gradient(feedback)
        self.structure_params.update(structure_grad)
    
    def update_structure(self):
        # Potentially add/remove/reorder skills based on learned structure
        if self.should_add_skill():
            self.add(self.generate_new_skill())
        if self.should_remove_skill():
            self.remove(self.find_weakest_skill())
```

### sk.Criterion → sk².MetaCriterion

The criterion becomes a **learnable criterion**:

```python
class MetaCriterion(sk.Criterion):
    """A criterion that learns what 'good' means."""
    
    def __init__(self):
        self.quality_model = sk.Skill("learn-quality")
        self.weights = LearnableWeights()
        
    def forward(self, output, target):
        # Compute loss using learned quality model
        quality_score = self.quality_model.forward(output)
        target_score = self.quality_model.forward(target)
        return self.distance(quality_score, target_score)
    
    def backward(self, output, target):
        grad = super().backward(output, target)
        
        # ALSO update the quality model itself
        quality_feedback = self.get_quality_feedback()
        self.quality_model.backward(quality_feedback)
        
        return grad
```

### Training Loop → sk².MetaTrainingLoop

The training loop becomes **trainable**:

```python
class MetaTrainingLoop:
    """A training loop that learns how to train."""
    
    def __init__(self):
        self.learning_rate_model = sk.Skill("predict-lr")
        self.batch_size_model = sk.Skill("predict-batch")
        self.stopping_model = sk.Skill("predict-stop")
        
    def train(self, network, dataset):
        for epoch in range(self.max_epochs):
            # Learn optimal hyperparameters
            lr = self.learning_rate_model.forward(network.state())
            batch_size = self.batch_size_model.forward(dataset.state())
            
            # Train with learned hyperparameters
            for batch in dataset.batches(batch_size):
                loss = self.train_step(network, batch, lr)
            
            # Learn whether to stop
            if self.stopping_model.forward(network.state()) > 0.5:
                break
        
        # Meta-update: improve the hyperparameter models
        self.meta_update(network.performance())
```

## The Emergent Structure: skill-nn²

```
skill-nn² = {
    SkillModule:      skill that contains/manages skills
    SkillPipeline:    pipeline that learns its structure
    SkillFork:        parallel execution that learns split strategy
    MetaCriterion:    criterion that learns what "good" means
    MetaTraining:     training that learns how to train
}
```

## Key Insight: Everything Becomes Learnable

At T², the **structure itself becomes learnable**:

| T¹ (skill-nn) | T² (skill-nn²) |
|---------------|----------------|
| Fixed pipeline structure | Learnable pipeline structure |
| Fixed criterion | Learnable criterion |
| Fixed learning rate | Learned learning rate |
| Manual skill composition | Automatic skill composition |
| Human designs architecture | Architecture learns itself |

## The Meta-Learning Equation

At T²:
```
θ* = argmin_θ L(f_θ(task), target)           # T¹: learn parameters
φ* = argmin_φ L(f_{θ*(φ)}(task), target)     # T²: learn how to learn parameters
```

Where:
- θ = skill parameters (SKILL.md content)
- φ = meta-parameters (how skills are composed, trained, evaluated)

## What T² Adds

1. **Neural Architecture Search for Skills** — automatically find optimal skill compositions
2. **Learned Loss Functions** — discover what "good output" means
3. **Adaptive Training** — learn optimal training dynamics
4. **Self-Modifying Structure** — skills that add/remove sub-skills

## Diagram

```
                    ┌─────────────────────────────────────┐
                    │           skill-nn²                  │
                    │  ┌─────────────────────────────┐    │
                    │  │      MetaTrainingLoop       │    │
                    │  │  (learns how to train)      │    │
                    │  └──────────────┬──────────────┘    │
                    │                 │                    │
                    │  ┌──────────────▼──────────────┐    │
                    │  │      SkillPipeline          │    │
                    │  │  (learns its structure)     │    │
                    │  │  ┌────┐ ┌────┐ ┌────┐      │    │
                    │  │  │ S₁ │→│ S₂ │→│ S₃ │ ...  │    │
                    │  │  └────┘ └────┘ └────┘      │    │
                    │  │     ↑ add/remove/reorder    │    │
                    │  └──────────────┬──────────────┘    │
                    │                 │                    │
                    │  ┌──────────────▼──────────────┐    │
                    │  │      MetaCriterion          │    │
                    │  │  (learns what "good" means) │    │
                    │  └─────────────────────────────┘    │
                    └─────────────────────────────────────┘
```

## Next: T³

What happens when we apply T again?
