# ReservoirPy Node API Reference

## Table of Contents

1. [Node Base Class](#node-base-class)
2. [TrainableNode Class](#trainablenode-class)
3. [OnlineNode Class](#onlinenode-class)
4. [ParallelNode Class](#parallelnode-class)
5. [Type Definitions](#type-definitions)
6. [Utility Functions](#utility-functions)

## Node Base Class

```python
from reservoirpy import Node
```

### Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `initialized` | `bool` | True if node has been initialized |
| `input_dim` | `int \| None` | Expected input dimension |
| `output_dim` | `int \| None` | Expected output dimension |
| `state` | `State` | Current state dict (must have `"out"` key) |
| `name` | `str \| None` | Optional node name |

### Abstract Methods (Must Implement)

#### `initialize(self, x, y=None)`

Initialize node dimensions and state. Called automatically before first use.

```python
def initialize(self, x: Union[NodeInput, Timestep], y: Optional[...] = None):
    self._set_input_dim(x)
    self.output_dim = ...  # Set based on your logic
    self.state = {"out": np.zeros((self.output_dim,))}
    self.initialized = True
```

#### `_step(self, state, x) -> State`

Process single timestep. **Must be purely functional** (no mutation).

```python
def _step(self, state: State, x: Timestep) -> State:
    y = ...  # Your computation
    return {"out": y}
```

### Optional Methods

#### `_run(self, state, x) -> tuple[State, Timeseries]`

Vectorized timeseries processing. Default loops over `_step()`.

```python
def _run(self, state: State, x: Timeseries) -> tuple[State, Timeseries]:
    out = ...  # Vectorized computation
    return {"out": out[-1]}, out
```

### Public Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `step` | `(x: Timestep) -> Timestep` | Process single timestep, update state |
| `run` | `(x: NodeInput, workers=1) -> NodeInput` | Process timeseries |
| `predict` | `(x: NodeInput) -> NodeInput` | Alias for `run()` |
| `reset` | `() -> State` | Reset state to zeros |

### Helper Methods

| Method | Description |
|--------|-------------|
| `_set_input_dim(x)` | Infer and set `input_dim` from data |
| `_set_output_dim(y)` | Infer and set `output_dim` from data |

### Operators

| Operator | Usage | Description |
|----------|-------|-------------|
| `>>` | `node1 >> node2` | Sequential connection |
| `&` | `node1 & node2` | Parallel merge |
| `<<` | `model << node` | Feedback connection |
| `()` | `node(x)` | Alias for `step(x)` |

## TrainableNode Class

```python
from reservoirpy import TrainableNode
```

Extends `Node` with offline training capability.

### Additional Abstract Methods

#### `fit(self, x, y=None, warmup=0) -> TrainableNode`

Offline training method.

```python
def fit(
    self,
    x: NodeInput,
    y: Optional[NodeInput] = None,
    warmup: int = 0,
) -> "TrainableNode":
    if not self.initialized:
        self.initialize(x, y)
    # Training logic
    return self
```

**Parameters:**
- `x`: Input data `(timesteps, input_dim)` or list of timeseries
- `y`: Target data (optional for unsupervised)
- `warmup`: Timesteps to discard at start

## OnlineNode Class

```python
from reservoirpy import OnlineNode
```

Extends `TrainableNode` with incremental learning.

### Additional Abstract Methods

#### `_learning_step(self, x, y) -> Timestep`

Single-step learning update.

```python
def _learning_step(self, x: Timestep, y: Optional[Timestep]) -> Timestep:
    prediction = ...  # Compute prediction
    if y is not None:
        # Update weights based on error
        ...
    return prediction
```

### Public Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `partial_fit` | `(x: Timeseries, y: Timeseries) -> Timeseries` | Incremental training |

**Note:** `partial_fit()` only accepts single timeseries, not lists.

## ParallelNode Class

```python
from reservoirpy import ParallelNode
```

Extends `TrainableNode` with parallel multi-series training.

### Additional Abstract Methods

#### `worker(self, x, y=None)`

Compute partial results for one timeseries. Runs in parallel.

```python
def worker(self, x: Timeseries, y: Optional[Timeseries]):
    # Compute sufficient statistics
    return partial_results
```

#### `master(self, generator)`

Aggregate worker results and update weights.

```python
def master(self, generator: Iterable):
    for results in generator:
        # Aggregate
        ...
    # Compute final weights
    self.Wout = ...
```

### Modified fit() Method

```python
def fit(
    self,
    x: NodeInput,
    y: Optional[NodeInput] = None,
    warmup: int = 0,
    workers: int = 1,  # Number of parallel workers
) -> "ParallelNode":
```

## Type Definitions

```python
from reservoirpy.type import (
    Timestep,        # np.ndarray of shape (features,)
    Timeseries,      # np.ndarray of shape (timesteps, features)
    NodeInput,       # Timeseries | list[Timeseries] | np.ndarray (3D)
    State,           # dict[str, np.ndarray] - must have "out" key
    Weights,         # np.ndarray for weight matrices
)
```

### Type Checking Functions

```python
from reservoirpy.type import is_array, is_multiseries

is_array(x)        # True if numpy array
is_multiseries(x)  # True if list or 3D array
```

## Utility Functions

### Matrix Generation

```python
from reservoirpy.mat_gen import (
    bernoulli,  # Sparse Bernoulli matrix
    normal,     # Normal distribution matrix
    zeros,      # Zero matrix
)
```

### Activation Functions

```python
from reservoirpy.activationsfunc import (
    tanh,
    sigmoid,
    relu,
    softmax,
    softplus,
    identity,
    get_function,  # Get function by name
)
```

### Random Generator

```python
from reservoirpy.utils import rand_generator

rng = rand_generator(seed=42)  # Returns np.random.Generator
```

## Data Validation

```python
from reservoirpy.utils.data_validation import (
    check_timestep,    # Validate single timestep
    check_timeseries,  # Validate timeseries
    check_node_input,  # Validate NodeInput
)
```

## Example: Complete Node Implementation

```python
from typing import Optional, Union
import numpy as np
from reservoirpy import Node
from reservoirpy.type import State, Timestep, Timeseries, NodeInput

class LeakyIntegrator(Node):
    """Leaky integrator neuron layer."""

    def __init__(
        self,
        units: int,
        leak_rate: float = 0.3,
        input_dim: Optional[int] = None,
        dtype: type = np.float64,
        seed: Optional[int] = None,
        name: Optional[str] = None,
    ):
        self.units = units
        self.leak_rate = leak_rate
        self.output_dim = units
        self.input_dim = input_dim
        self.dtype = dtype
        self.name = name

        from reservoirpy.utils import rand_generator
        self.rng = rand_generator(seed)

    def initialize(self, x: Union[NodeInput, Timestep]):
        self._set_input_dim(x)

        # Initialize weights
        self.W = self.rng.standard_normal((self.units, self.input_dim))
        self.W = self.W.astype(self.dtype)

        # Initialize state
        self.state = {"out": np.zeros((self.units,), dtype=self.dtype)}
        self.initialized = True

    def _step(self, state: State, x: Timestep) -> State:
        lr = self.leak_rate
        prev = state["out"]
        new = (1 - lr) * prev + lr * np.tanh(self.W @ x)
        return {"out": new}
```
