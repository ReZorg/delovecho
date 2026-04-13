# Training Dynamics for Skill Networks

## The Training Loop

```python
# Initialize
network = build_skill_network()
criterion = sk.MultiCriterion()
criterion.add(sk.TaskCompletionCriterion(), weight=1.0)
criterion.add(sk.TokenEfficiencyCriterion(), weight=0.1)

learning_rate = 0.01
momentum = 0.9

# Training
for epoch in range(num_epochs):
    for task, target in task_dataset:
        # Forward pass
        output = network.forward(task)
        loss = criterion.forward(output, target)
        
        # Backward pass
        network.zero_grad()
        grad = criterion.backward(output, target)
        network.backward(task, grad)
        
        # Update
        network.update(learning_rate)
    
    # Decay learning rate
    learning_rate *= 0.95
```

## Gradient Sources

### Explicit Feedback

Direct user signals about output quality.

```python
feedback = Feedback(
    signal=0.8,  # 80% satisfaction
    details="Good analysis but missing competitor data",
    source="user"
)
```

**Gradient computation:**
```python
grad = feedback.signal * (target - output)
```

### Implicit Feedback

Inferred from user behavior.

| Behavior | Signal | Interpretation |
|----------|--------|----------------|
| User accepts output | +1.0 | Success |
| User re-asks question | -0.5 | Partial failure |
| User abandons task | -1.0 | Complete failure |
| User edits output | -0.3 | Needs improvement |
| User shares output | +0.5 | High quality |

### Completion Signal

Binary success/failure.

```python
if task_completed:
    grad = +1.0 * direction_to_current_params
else:
    grad = -1.0 * direction_to_current_params
```

### Efficiency Signal

Pressure to minimize token usage.

```python
efficiency_grad = -lambda_ * sign(num_tokens)
```

## Optimization Algorithms

### Skill Gradient Descent (SKD)

Basic update rule:

```python
params = params - learning_rate * grad
```

### Skill Gradient Descent with Momentum (SKDM)

Accumulate velocity:

```python
velocity = momentum * velocity + grad
params = params - learning_rate * velocity
```

### Adaptive Skill Rate (ASR)

Per-parameter learning rates:

```python
cache = decay * cache + (1 - decay) * grad**2
params = params - learning_rate * grad / (sqrt(cache) + eps)
```

### Skill Adam

Combines momentum and adaptive rates:

```python
m = beta1 * m + (1 - beta1) * grad
v = beta2 * v + (1 - beta2) * grad**2
m_hat = m / (1 - beta1**t)
v_hat = v / (1 - beta2**t)
params = params - learning_rate * m_hat / (sqrt(v_hat) + eps)
```

## Regularization

### Token L1 (Sparsity)

Penalize skill verbosity:

```python
loss += lambda_l1 * sum(abs(token_counts))
```

**Effect:** Encourages concise skills.

### Token L2 (Smoothness)

Penalize large token counts:

```python
loss += lambda_l2 * sum(token_counts**2)
```

**Effect:** Discourages any single skill from being too verbose.

### Skill Dropout

Randomly skip skills during training:

```python
if training and random() < dropout_rate:
    output = input  # Skip this skill
else:
    output = skill.forward(input)
```

**Effect:** Robustness to missing skills.

### Early Stopping

Stop training when validation loss increases:

```python
if val_loss > best_val_loss:
    patience_counter += 1
    if patience_counter >= patience:
        break
else:
    best_val_loss = val_loss
    patience_counter = 0
    save_best_params()
```

**Effect:** Prevent over-specialization.

## Batch Training

### Mini-Batch Updates

Accumulate gradients over multiple tasks:

```python
batch_grad = 0
for task in batch:
    output = network.forward(task)
    loss = criterion.forward(output, target)
    batch_grad += criterion.backward(output, target)

batch_grad /= len(batch)
network.backward(batch_grad)
network.update(learning_rate)
```

### Batch Size Effects

| Batch Size | Effect |
|------------|--------|
| Small (1-4) | Noisy gradients, fast iteration |
| Medium (8-32) | Balanced noise/stability |
| Large (64+) | Stable gradients, slow iteration |

## Learning Rate Schedules

### Constant

```python
lr = initial_lr
```

### Step Decay

```python
lr = initial_lr * (decay_rate ** (epoch // step_size))
```

### Exponential Decay

```python
lr = initial_lr * exp(-decay_rate * epoch)
```

### Cosine Annealing

```python
lr = min_lr + 0.5 * (max_lr - min_lr) * (1 + cos(pi * epoch / max_epochs))
```

### Warmup

```python
if epoch < warmup_epochs:
    lr = initial_lr * (epoch / warmup_epochs)
else:
    lr = scheduled_lr(epoch - warmup_epochs)
```

## Gradient Clipping

Prevent exploding gradients:

```python
grad_norm = sqrt(sum(grad**2))
if grad_norm > max_norm:
    grad = grad * (max_norm / grad_norm)
```

## Curriculum Learning

Train on easier tasks first:

```python
# Sort tasks by difficulty
tasks = sorted(all_tasks, key=lambda t: t.difficulty)

# Train in stages
for stage in range(num_stages):
    stage_tasks = tasks[:int(len(tasks) * (stage + 1) / num_stages)]
    train_on(stage_tasks)
```

## Transfer Learning

### Pre-training

Train on general tasks first:

```python
# Pre-train on general corpus
network.train(general_task_dataset)

# Fine-tune on specific domain
network.train(domain_specific_dataset, learning_rate=0.001)
```

### Freezing Layers

Keep some skills fixed:

```python
# Freeze early skills
for skill in network.skills[:3]:
    skill.requires_grad = False

# Train only later skills
network.train(dataset)
```

### Knowledge Distillation

Transfer from large to small skill network:

```python
teacher = large_skill_network
student = small_skill_network

for task in dataset:
    teacher_output = teacher.forward(task)
    student_output = student.forward(task)
    
    # Match student to teacher
    loss = distillation_loss(student_output, teacher_output)
    student.backward(loss)
    student.update(lr)
```

## Validation

### Holdout Validation

```python
train_tasks, val_tasks = split(all_tasks, ratio=0.8)

for epoch in range(max_epochs):
    train_loss = train_epoch(network, train_tasks)
    val_loss = validate(network, val_tasks)
    
    print(f"Epoch {epoch}: train={train_loss:.4f}, val={val_loss:.4f}")
```

### Cross-Validation

```python
for fold in range(k_folds):
    train_tasks, val_tasks = get_fold(all_tasks, fold)
    network = build_skill_network()
    train(network, train_tasks)
    scores.append(validate(network, val_tasks))

mean_score = sum(scores) / len(scores)
```

## Debugging Training

### Gradient Checking

```python
# Numerical gradient
eps = 1e-5
param_plus = param + eps
param_minus = param - eps
numerical_grad = (loss(param_plus) - loss(param_minus)) / (2 * eps)

# Compare to computed gradient
assert abs(numerical_grad - computed_grad) < 1e-4
```

### Loss Curves

Monitor for:
- **Decreasing train loss**: Learning is happening
- **Flat train loss**: Learning rate too low or stuck
- **Oscillating train loss**: Learning rate too high
- **Val loss increasing**: Overfitting

### Gradient Statistics

```python
print(f"Grad mean: {grad.mean():.4f}")
print(f"Grad std: {grad.std():.4f}")
print(f"Grad max: {grad.max():.4f}")
print(f"Grad min: {grad.min():.4f}")
```

Watch for:
- **Near-zero gradients**: Vanishing gradient problem
- **Huge gradients**: Exploding gradient problem
- **NaN gradients**: Numerical instability
