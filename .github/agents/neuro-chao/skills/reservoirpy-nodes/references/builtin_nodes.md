# Built-in ReservoirPy Nodes

## Table of Contents

1. [Reservoir Nodes](#reservoir-nodes)
2. [Readout Nodes](#readout-nodes)
3. [Activation Nodes](#activation-nodes)
4. [I/O Nodes](#io-nodes)
5. [Advanced Nodes](#advanced-nodes)

## Reservoir Nodes

### Reservoir

Standard Echo State Network reservoir.

```python
from reservoirpy.nodes import Reservoir

reservoir = Reservoir(
    units=100,           # Number of neurons
    lr=0.3,              # Leak rate [0, 1]
    sr=0.9,              # Spectral radius
    input_scaling=1.0,   # Input gain
    input_connectivity=0.1,  # Win sparsity
    rc_connectivity=0.1,     # W sparsity
    activation="tanh",   # Activation function
    seed=42,             # Random seed
)
```

**Key Parameters:**
- `units`: Reservoir size
- `lr`: Leak rate (1.0 = no leaking)
- `sr`: Spectral radius (controls dynamics stability)

### ES2N

Edge of Stability Echo State Network.

```python
from reservoirpy.nodes import ES2N

es2n = ES2N(
    units=100,
    sr=1.0,
    lr=0.3,
    mu=0.5,      # Stability parameter
    eta=1e-3,    # Learning rate for stability
)
```

### IPReservoir

Intrinsic Plasticity Reservoir.

```python
from reservoirpy.nodes import IPReservoir

ip_reservoir = IPReservoir(
    units=100,
    lr=0.3,
    sr=0.9,
    mu=0.0,      # Target mean
    sigma=0.2,   # Target std
    eta=1e-3,    # IP learning rate
)
```

### LocalPlasticityReservoir

Reservoir with local learning rules.

```python
from reservoirpy.nodes import LocalPlasticityReservoir

lp_reservoir = LocalPlasticityReservoir(
    units=100,
    lr=0.3,
    sr=0.9,
    rule="oja",  # Learning rule: "oja", "anti_oja", "bcm"
    eta=1e-4,    # Learning rate
)
```

### LIF

Leaky Integrate-and-Fire spiking neurons.

```python
from reservoirpy.nodes import LIF

lif = LIF(
    units=100,
    tau=20.0,      # Membrane time constant
    threshold=1.0, # Spike threshold
    reset=0.0,     # Reset potential
)
```

## Readout Nodes

### Ridge

Ridge regression readout (L2 regularized).

```python
from reservoirpy.nodes import Ridge

readout = Ridge(
    ridge=1e-5,      # Regularization
    fit_bias=True,   # Learn bias term
)

# Training
readout.fit(states, targets, warmup=100)

# Parallel training
readout.fit(states_list, targets_list, warmup=100, workers=4)
```

### RLS

Recursive Least Squares (online learning).

```python
from reservoirpy.nodes import RLS

rls = RLS(
    alpha=1e-6,      # Initial P diagonal
    forgetting=1.0,  # Forgetting factor
    fit_bias=True,
)

# Online training
predictions = rls.partial_fit(states, targets)
```

### LMS

Least Mean Squares (online learning).

```python
from reservoirpy.nodes import LMS

lms = LMS(
    eta=1e-3,        # Learning rate
    fit_bias=True,
)

predictions = lms.partial_fit(states, targets)
```

### ScikitLearnNode

Wrapper for scikit-learn estimators.

```python
from reservoirpy.nodes import ScikitLearnNode
from sklearn.linear_model import Lasso

sklearn_node = ScikitLearnNode(
    estimator=Lasso(alpha=0.01),
)

sklearn_node.fit(states, targets)
```

## Activation Nodes

### Tanh

```python
from reservoirpy.nodes import Tanh
tanh = Tanh()
```

### Sigmoid

```python
from reservoirpy.nodes import Sigmoid
sigmoid = Sigmoid()
```

### ReLU

```python
from reservoirpy.nodes import ReLU
relu = ReLU()
```

### Softmax

```python
from reservoirpy.nodes import Softmax
softmax = Softmax(beta=1.0)  # Temperature parameter
```

### Softplus

```python
from reservoirpy.nodes import Softplus
softplus = Softplus()
```

### Identity

```python
from reservoirpy.nodes import Identity
identity = Identity()
```

### F (Generic Function)

Apply any element-wise function.

```python
from reservoirpy.nodes import F
import numpy as np

# Custom activation
leaky_relu = F(lambda x: np.where(x > 0, x, 0.01 * x))
```

## I/O Nodes

### Input

Input node for explicit input handling.

```python
from reservoirpy.nodes import Input

input_node = Input(input_dim=10)
```

### Output

Output node for explicit output handling.

```python
from reservoirpy.nodes import Output

output_node = Output(output_dim=5)
```

## Advanced Nodes

### NVAR

Next-Generation Reservoir Computing (nonlinear vector autoregression).

```python
from reservoirpy.nodes import NVAR

nvar = NVAR(
    delay=10,        # Delay embedding
    order=2,         # Polynomial order
    strides=1,       # Stride between delays
)
```

## Common Patterns

### Standard ESN

```python
from reservoirpy.nodes import Reservoir, Ridge

reservoir = Reservoir(100, sr=0.9, lr=0.3)
readout = Ridge(ridge=1e-5)
esn = reservoir >> readout

esn.fit(x_train, y_train, warmup=100)
predictions = esn.run(x_test)
```

### Deep ESN

```python
reservoir1 = Reservoir(100, sr=0.9, name="layer1")
reservoir2 = Reservoir(100, sr=0.9, name="layer2")
readout = Ridge(ridge=1e-5)

deep_esn = reservoir1 >> reservoir2 >> readout
```

### ESN with Feedback

```python
reservoir = Reservoir(100, sr=0.9)
readout = Ridge(ridge=1e-5)

esn = reservoir >> readout
esn = esn << reservoir  # Feedback from readout to reservoir
```

### Parallel Reservoirs

```python
res1 = Reservoir(50, sr=0.9, name="fast")
res2 = Reservoir(50, sr=0.5, name="slow")
readout = Ridge(ridge=1e-5)

# Merge outputs of both reservoirs
model = (res1 & res2) >> readout
```

### Online Learning ESN

```python
reservoir = Reservoir(100, sr=0.9)
readout = RLS(alpha=1e-3)

esn = reservoir >> readout

# Incremental training
for batch_x, batch_y in data_stream:
    predictions = esn.partial_fit(batch_x, batch_y)
```

## Node Inspection

```python
# Check dimensions
print(f"Input dim: {node.input_dim}")
print(f"Output dim: {node.output_dim}")
print(f"Initialized: {node.initialized}")

# Access state
print(f"Current output: {node.state['out']}")

# Reset state
node.reset()

# For trained nodes
print(f"Weights shape: {readout.Wout.shape}")
print(f"Bias: {readout.bias}")
```
