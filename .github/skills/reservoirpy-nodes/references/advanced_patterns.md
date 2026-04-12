# Advanced Node Patterns

## Table of Contents

1. [State Space Model Node](#state-space-model-node)
2. [Attention Mechanism Node](#attention-mechanism-node)
3. [Convolutional Node](#convolutional-node)
4. [Gated Recurrent Node](#gated-recurrent-node)
5. [Mixture of Experts Node](#mixture-of-experts-node)
6. [Delay Line Node](#delay-line-node)
7. [Multi-State Node](#multi-state-node)

## State Space Model Node

Implements a discrete state space model (SSM) like S4/Mamba.

```python
import numpy as np
from reservoirpy import Node
from reservoirpy.type import State, Timestep, Timeseries

class SSMNode(Node):
    """Discrete State Space Model node.

    Implements: x[t+1] = A @ x[t] + B @ u[t]
                y[t] = C @ x[t] + D @ u[t]
    """

    def __init__(
        self,
        state_dim: int,
        input_dim: int = None,
        output_dim: int = None,
        dt: float = 1.0,
        name: str = None,
    ):
        self.state_dim = state_dim
        self.input_dim = input_dim
        self.output_dim = output_dim or state_dim
        self.dt = dt
        self.name = name

    def initialize(self, x):
        self._set_input_dim(x)
        if self.output_dim is None:
            self.output_dim = self.state_dim

        # Initialize SSM matrices
        self.A = np.eye(self.state_dim) * 0.99  # Stable dynamics
        self.B = np.random.randn(self.state_dim, self.input_dim) * 0.1
        self.C = np.random.randn(self.output_dim, self.state_dim) * 0.1
        self.D = np.zeros((self.output_dim, self.input_dim))

        # Hidden state
        self.state = {
            "out": np.zeros((self.output_dim,)),
            "hidden": np.zeros((self.state_dim,)),
        }
        self.initialized = True

    def _step(self, state, x):
        h = state["hidden"]
        h_next = self.A @ h + self.B @ x
        y = self.C @ h_next + self.D @ x
        return {"out": y, "hidden": h_next}
```

## Attention Mechanism Node

Self-attention for sequence processing.

```python
import numpy as np
from reservoirpy import Node

class AttentionNode(Node):
    """Single-head self-attention node.

    Maintains a context window of past inputs.
    """

    def __init__(
        self,
        embed_dim: int,
        context_length: int = 32,
        name: str = None,
    ):
        self.embed_dim = embed_dim
        self.context_length = context_length
        self.output_dim = embed_dim
        self.name = name

    def initialize(self, x):
        self._set_input_dim(x)
        d = self.embed_dim

        # Query, Key, Value projections
        scale = 1.0 / np.sqrt(d)
        self.Wq = np.random.randn(d, self.input_dim) * scale
        self.Wk = np.random.randn(d, self.input_dim) * scale
        self.Wv = np.random.randn(d, self.input_dim) * scale

        # Context buffer
        self.state = {
            "out": np.zeros((self.output_dim,)),
            "context": np.zeros((self.context_length, self.input_dim)),
            "position": 0,
        }
        self.initialized = True

    def _step(self, state, x):
        ctx = state["context"].copy()
        pos = state["position"]

        # Update context buffer (circular)
        ctx[pos % self.context_length] = x
        new_pos = pos + 1

        # Compute attention
        valid_len = min(new_pos, self.context_length)
        context = ctx[:valid_len]

        q = self.Wq @ x  # (d,)
        K = context @ self.Wk.T  # (len, d)
        V = context @ self.Wv.T  # (len, d)

        # Attention scores
        scores = K @ q / np.sqrt(self.embed_dim)  # (len,)
        weights = np.exp(scores - scores.max())
        weights /= weights.sum()

        # Weighted sum
        y = weights @ V  # (d,)

        return {"out": y, "context": ctx, "position": new_pos}
```

## Convolutional Node

1D convolution for temporal patterns.

```python
import numpy as np
from reservoirpy import Node

class Conv1DNode(Node):
    """1D Convolutional node with temporal receptive field."""

    def __init__(
        self,
        filters: int,
        kernel_size: int,
        stride: int = 1,
        name: str = None,
    ):
        self.filters = filters
        self.kernel_size = kernel_size
        self.stride = stride
        self.output_dim = filters
        self.name = name

    def initialize(self, x):
        self._set_input_dim(x)

        # Initialize kernel
        scale = np.sqrt(2.0 / (self.kernel_size * self.input_dim))
        self.kernel = np.random.randn(
            self.filters, self.kernel_size, self.input_dim
        ) * scale
        self.bias = np.zeros((self.filters,))

        # Buffer for temporal context
        self.state = {
            "out": np.zeros((self.output_dim,)),
            "buffer": np.zeros((self.kernel_size, self.input_dim)),
        }
        self.initialized = True

    def _step(self, state, x):
        buf = state["buffer"].copy()

        # Shift buffer and add new input
        buf[:-1] = buf[1:]
        buf[-1] = x

        # Convolution (sum over time and input dims)
        y = np.einsum("fti,ti->f", self.kernel, buf) + self.bias
        y = np.maximum(y, 0)  # ReLU

        return {"out": y, "buffer": buf}
```

## Gated Recurrent Node

GRU-style gating mechanism.

```python
import numpy as np
from reservoirpy import Node

class GRUNode(Node):
    """Gated Recurrent Unit node."""

    def __init__(self, units: int, name: str = None):
        self.units = units
        self.output_dim = units
        self.name = name

    def initialize(self, x):
        self._set_input_dim(x)
        n, d = self.units, self.input_dim

        # Gate weights
        scale = 1.0 / np.sqrt(d + n)
        self.Wz = np.random.randn(n, d + n) * scale  # Update gate
        self.Wr = np.random.randn(n, d + n) * scale  # Reset gate
        self.Wh = np.random.randn(n, d + n) * scale  # Candidate

        self.state = {"out": np.zeros((n,))}
        self.initialized = True

    def _step(self, state, x):
        h = state["out"]
        xh = np.concatenate([x, h])

        z = self._sigmoid(self.Wz @ xh)  # Update gate
        r = self._sigmoid(self.Wr @ xh)  # Reset gate

        xrh = np.concatenate([x, r * h])
        h_candidate = np.tanh(self.Wh @ xrh)

        h_new = (1 - z) * h + z * h_candidate
        return {"out": h_new}

    @staticmethod
    def _sigmoid(x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
```

## Mixture of Experts Node

Sparse expert routing.

```python
import numpy as np
from reservoirpy import Node

class MoENode(Node):
    """Mixture of Experts with top-k routing."""

    def __init__(
        self,
        num_experts: int,
        expert_dim: int,
        top_k: int = 2,
        name: str = None,
    ):
        self.num_experts = num_experts
        self.expert_dim = expert_dim
        self.top_k = top_k
        self.output_dim = expert_dim
        self.name = name

    def initialize(self, x):
        self._set_input_dim(x)
        n_exp = self.num_experts
        d_in = self.input_dim
        d_out = self.expert_dim

        # Router
        self.router = np.random.randn(n_exp, d_in) * 0.1

        # Expert weights
        self.experts_W = np.random.randn(n_exp, d_out, d_in) * 0.1
        self.experts_b = np.zeros((n_exp, d_out))

        self.state = {"out": np.zeros((d_out,))}
        self.initialized = True

    def _step(self, state, x):
        # Compute router logits
        logits = self.router @ x
        probs = np.exp(logits - logits.max())
        probs /= probs.sum()

        # Top-k selection
        top_k_idx = np.argsort(probs)[-self.top_k:]
        top_k_probs = probs[top_k_idx]
        top_k_probs /= top_k_probs.sum()  # Renormalize

        # Compute expert outputs
        y = np.zeros((self.expert_dim,))
        for i, idx in enumerate(top_k_idx):
            expert_out = self.experts_W[idx] @ x + self.experts_b[idx]
            y += top_k_probs[i] * expert_out

        return {"out": y}
```

## Delay Line Node

Tapped delay line for temporal features.

```python
import numpy as np
from reservoirpy import Node

class DelayLineNode(Node):
    """Tapped delay line node.

    Outputs concatenation of current and delayed inputs.
    """

    def __init__(self, delays: list[int], name: str = None):
        self.delays = sorted(delays)
        self.max_delay = max(delays) if delays else 0
        self.name = name

    def initialize(self, x):
        self._set_input_dim(x)
        self.output_dim = self.input_dim * (len(self.delays) + 1)

        # Buffer for delayed values
        buffer_size = self.max_delay + 1
        self.state = {
            "out": np.zeros((self.output_dim,)),
            "buffer": np.zeros((buffer_size, self.input_dim)),
            "position": 0,
        }
        self.initialized = True

    def _step(self, state, x):
        buf = state["buffer"].copy()
        pos = state["position"]
        buf_size = buf.shape[0]

        # Store current input
        buf[pos % buf_size] = x

        # Gather delayed values
        outputs = [x]  # Current
        for d in self.delays:
            idx = (pos - d) % buf_size
            outputs.append(buf[idx])

        y = np.concatenate(outputs)
        return {"out": y, "buffer": buf, "position": pos + 1}
```

## Multi-State Node

Node with multiple named state variables.

```python
import numpy as np
from reservoirpy import Node

class MultiStateNode(Node):
    """Node demonstrating multiple state variables.

    Useful for complex dynamics with multiple interacting components.
    """

    def __init__(self, units: int, name: str = None):
        self.units = units
        self.output_dim = units
        self.name = name

    def initialize(self, x):
        self._set_input_dim(x)
        n = self.units

        # Multiple weight matrices
        self.W_fast = np.random.randn(n, self.input_dim) * 0.1
        self.W_slow = np.random.randn(n, n) * 0.1
        self.W_out = np.random.randn(n, n) * 0.1

        # Multiple state variables
        self.state = {
            "out": np.zeros((n,)),
            "fast": np.zeros((n,)),  # Fast dynamics
            "slow": np.zeros((n,)),  # Slow dynamics
        }
        self.initialized = True

    def _step(self, state, x):
        fast = state["fast"]
        slow = state["slow"]

        # Fast dynamics (high leak rate)
        fast_new = 0.1 * fast + 0.9 * np.tanh(self.W_fast @ x)

        # Slow dynamics (low leak rate)
        slow_new = 0.95 * slow + 0.05 * np.tanh(self.W_slow @ fast_new)

        # Output combines both
        y = np.tanh(self.W_out @ (fast_new + slow_new))

        return {"out": y, "fast": fast_new, "slow": slow_new}
```

## Best Practices

### State Management

1. **Always include `"out"` key** - Required by the framework
2. **Copy mutable state** - Use `.copy()` to avoid mutation
3. **Keep state minimal** - Only store what's needed between steps

### Performance

1. **Vectorize `_run()`** - Override for batch efficiency
2. **Pre-allocate arrays** - Avoid allocation in `_step()`
3. **Use NumPy operations** - Avoid Python loops in hot paths

### Testing

```python
def test_node(NodeClass, **kwargs):
    """Generic node test."""
    node = NodeClass(**kwargs)
    x = np.random.randn(100, 10)

    # Test run
    out = node.run(x)
    assert out.shape[0] == 100

    # Test step consistency
    node2 = NodeClass(**kwargs)
    for t in range(10):
        y = node2.step(x[t])

    # Compare final states
    np.testing.assert_allclose(
        node.state["out"][:10],
        node2.state["out"][:10],
        rtol=1e-5
    )
```
