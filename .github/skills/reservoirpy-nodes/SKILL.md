---
name: reservoirpy-nodes
description: Create custom ReservoirPy nodes for reservoir computing architectures. Use when implementing custom neural operators, trainable layers, online learning nodes, or parallel-trainable nodes for Echo State Networks and computational graph models.
license: MIT
---

# ReservoirPy Custom Nodes

Create custom nodes for ReservoirPy's typed computational graph framework. ReservoirPy nodes are stateful operators that compose into arbitrary neural architectures.

## Node Type Hierarchy

```
Node                    # Basic stateless/stateful operator
╠══ TrainableNode       # Adds offline .fit() method
║   ╠══ ParallelNode    # Parallel training on multiple timeseries
║   ╚══ OnlineNode      # Incremental .partial_fit() learning
```

## Quick Reference

| Node Type | Use Case | Key Methods |
|-----------|----------|-------------|
| `Node` | Reservoirs, activations, transforms | `_step()`, `_run()` |
| `TrainableNode` | Offline-trained layers | `fit()` |
| `OnlineNode` | Incremental/streaming learning | `partial_fit()`, `_learning_step()` |
| `ParallelNode` | Batch training on multi-series | `worker()`, `master()` |

## Creating a Custom Node

### Step 1: Choose Node Type

- **Non-trainable computation** → `Node`
- **Offline batch training** → `TrainableNode`
- **Online/incremental training** → `OnlineNode`
- **Parallel multi-series training** → `ParallelNode`

### Step 2: Implement Required Methods

Run the template generator for your node type:

```bash
python /home/ubuntu/skills/reservoirpy-nodes/scripts/generate_node.py <node_type> <NodeClassName>
```

### Step 3: Key Implementation Rules

1. **`_step()` must be purely functional** - No mutation, no side effects
2. **State dict must have `"out"` key** - Shape `(output_dim,)`
3. **Use `_set_input_dim(x)` and `_set_output_dim(y)`** - For dimension inference
4. **Set `self.initialized = True`** - At end of `initialize()`

## Node Templates

### Basic Node (Non-Trainable)

```python
from reservoirpy import Node
import numpy as np

class MyNode(Node):
    def __init__(self, param, input_dim=None, name=None):
        self.param = param
        self.input_dim = input_dim
        self.name = name

    def initialize(self, x):
        self._set_input_dim(x)
        self.output_dim = self.input_dim  # or custom logic
        self.state = {"out": np.zeros((self.output_dim,))}
        self.initialized = True

    def _step(self, state, x):
        # Pure function: no self mutation
        y = x * self.param  # your computation
        return {"out": y}

    def _run(self, state, x):
        # Optional: vectorized version
        out = x * self.param
        return {"out": out[-1]}, out
```

### TrainableNode (Offline Training)

```python
from reservoirpy import TrainableNode
import numpy as np

class MyTrainableNode(TrainableNode):
    def __init__(self, input_dim=None, output_dim=None, name=None):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.name = name
        self.Wout = None

    def initialize(self, x, y=None):
        self._set_input_dim(x)
        self._set_output_dim(y)
        self.state = {"out": np.zeros((self.output_dim,))}
        self.initialized = True

    def _step(self, state, x):
        return {"out": x @ self.Wout}

    def fit(self, x, y, warmup=0):
        if not self.initialized:
            self.initialize(x, y)
        # Training logic here
        x_train = x[warmup:]
        y_train = y[warmup:]
        self.Wout = np.linalg.lstsq(x_train, y_train, rcond=None)[0]
        return self
```

### OnlineNode (Incremental Learning)

```python
from reservoirpy import OnlineNode
import numpy as np

class MyOnlineNode(OnlineNode):
    def __init__(self, alpha=1e-6, input_dim=None, output_dim=None, name=None):
        self.alpha = alpha
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.name = name
        self.state = {}

    def initialize(self, x, y=None):
        self._set_input_dim(x)
        self._set_output_dim(y)
        self.Wout = np.zeros((self.input_dim, self.output_dim))
        self.P = np.eye(self.input_dim) / self.alpha
        self.state = {"out": np.zeros((self.output_dim,))}
        self.initialized = True

    def _step(self, state, x):
        return {"out": x @ self.Wout}

    def _learning_step(self, x, y):
        # Update weights incrementally
        Px = self.P @ x
        k = Px / (1 + x @ Px)
        prediction = x @ self.Wout
        error = prediction - y
        self.Wout -= np.outer(k, error)
        self.P -= np.outer(k, Px)
        return prediction
```

### ParallelNode (Multi-Series Training)

```python
from reservoirpy import ParallelNode
import numpy as np
from scipy import linalg

class MyParallelNode(ParallelNode):
    def __init__(self, ridge=0.0, input_dim=None, output_dim=None, name=None):
        self.ridge = ridge
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.name = name
        self.state = {}

    def initialize(self, x, y=None):
        self._set_input_dim(x)
        self._set_output_dim(y)
        self.state = {"out": np.zeros((self.output_dim,))}
        self.initialized = True

    def _step(self, state, x):
        return {"out": x @ self.Wout + self.bias}

    def worker(self, x, y):
        # Compute partial results (runs in parallel)
        XXT = x.T @ x
        YXT = x.T @ y
        return XXT, YXT, x.shape[0]

    def master(self, generator):
        # Aggregate results from workers
        XXT = np.zeros((self.input_dim, self.input_dim))
        YXT = np.zeros((self.input_dim, self.output_dim))
        for xxt, yxt, n in generator:
            XXT += xxt
            YXT += yxt
        ridge_I = self.ridge * np.eye(self.input_dim)
        self.Wout = linalg.solve(XXT + ridge_I, YXT, assume_a="sym")
        self.bias = np.zeros((self.output_dim,))
```

## Advanced Patterns

### State Space Model Node

See `references/advanced_patterns.md` for SSM, attention, and other advanced node patterns.

### Feedback Connections

Connect nodes with feedback using `<<` operator:

```python
reservoir = Reservoir(100)
readout = Ridge()
esn = reservoir >> readout
esn = esn << reservoir  # feedback from readout to reservoir
```

### Model Composition

```python
# Sequential: >>
model = node1 >> node2 >> node3

# Parallel merge: &
model = (node1 & node2) >> node3

# Complex graphs
encoder = Reservoir(100)
decoder = Ridge()
model = encoder >> decoder
```

## Testing Custom Nodes

```python
import numpy as np

# Test initialization
node = MyNode(param=2.0)
x = np.random.randn(100, 10)  # 100 timesteps, 10 features

# Test run
output = node.run(x)
assert output.shape == (100, node.output_dim)

# Test step
node.reset()
for t in range(10):
    y = node.step(x[t])
    assert y.shape == (node.output_dim,)
```

## Reference Documentation

- **Advanced patterns**: See `references/advanced_patterns.md`
- **API details**: See `references/api_reference.md`
- **Built-in nodes**: See `references/builtin_nodes.md`
