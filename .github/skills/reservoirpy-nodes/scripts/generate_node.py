#!/usr/bin/env python3
"""
Generate ReservoirPy custom node templates.

Usage:
    python generate_node.py <node_type> <ClassName> [output_file]

Arguments:
    node_type   : One of 'node', 'trainable', 'online', 'parallel'
    ClassName   : Name for the new node class (e.g., MyCustomNode)
    output_file : Optional output file path (default: stdout)

Examples:
    python generate_node.py node MyActivation
    python generate_node.py trainable MyReadout my_readout.py
    python generate_node.py online MyRLS
    python generate_node.py parallel MyRidge
"""

import sys
from pathlib import Path

TEMPLATES = {
    "node": '''"""
{class_name} - Custom ReservoirPy Node

A basic non-trainable node for reservoir computing.
"""

from typing import Callable, Optional, Union
import numpy as np
from reservoirpy import Node
from reservoirpy.type import State, Timestep, Timeseries, NodeInput


class {class_name}(Node):
    """Custom node implementation.

    Parameters
    ----------
    param : float
        Example parameter for the node.
    input_dim : int, optional
        Input dimension. Can be inferred at first call.
    dtype : type, default to np.float64
        Numerical type for node parameters.
    name : str, optional
        Node name.

    Example
    -------
    >>> node = {class_name}(param=1.0)
    >>> x = np.random.randn(100, 10)
    >>> output = node.run(x)
    """

    initialized: bool = False
    input_dim: Optional[int] = None
    output_dim: Optional[int] = None
    name: Optional[str] = None
    state: State

    def __init__(
        self,
        param: float = 1.0,
        input_dim: Optional[int] = None,
        dtype: type = np.float64,
        name: Optional[str] = None,
    ):
        self.param = param
        self.input_dim = input_dim
        self.dtype = dtype
        self.name = name

    def initialize(self, x: Union[NodeInput, Timestep]):
        """Initialize node dimensions and state.

        Parameters
        ----------
        x : array-like
            Input data to infer dimensions from.
        """
        self._set_input_dim(x)
        self.output_dim = self.input_dim  # Modify as needed

        # Initialize state - MUST have "out" key
        self.state = {{"out": np.zeros((self.output_dim,), dtype=self.dtype)}}
        self.initialized = True

    def _step(self, state: State, x: Timestep) -> State:
        """Process a single timestep.

        MUST be purely functional - no self mutation allowed.

        Parameters
        ----------
        state : dict
            Current state of the node.
        x : array of shape (input_dim,)
            Input timestep.

        Returns
        -------
        dict
            New state with "out" key.
        """
        # Your computation here
        y = x * self.param
        return {{"out": y}}

    def _run(self, state: State, x: Timeseries) -> tuple[State, Timeseries]:
        """Process a timeseries (optional vectorized version).

        Parameters
        ----------
        state : dict
            Current state of the node.
        x : array of shape (timesteps, input_dim)
            Input timeseries.

        Returns
        -------
        tuple[dict, array]
            Final state and output timeseries.
        """
        # Vectorized computation
        out = x * self.param
        return {{"out": out[-1]}}, out
''',

    "trainable": '''"""
{class_name} - Custom Trainable ReservoirPy Node

A trainable node with offline .fit() method.
"""

from typing import Callable, Optional, Union
import numpy as np
from reservoirpy import TrainableNode
from reservoirpy.type import State, Timestep, Timeseries, NodeInput, Weights


class {class_name}(TrainableNode):
    """Custom trainable node implementation.

    Parameters
    ----------
    ridge : float, default to 0.0
        L2 regularization parameter.
    input_dim : int, optional
        Input dimension. Can be inferred at first call.
    output_dim : int, optional
        Output dimension. Can be inferred at first call.
    name : str, optional
        Node name.

    Example
    -------
    >>> node = {class_name}(ridge=1e-5)
    >>> x = np.random.randn(100, 10)
    >>> y = np.random.randn(100, 3)
    >>> node.fit(x, y, warmup=10)
    >>> predictions = node.run(x)
    """

    initialized: bool = False
    input_dim: Optional[int] = None
    output_dim: Optional[int] = None
    name: Optional[str] = None
    state: State

    # Learned parameters
    Wout: Weights = None
    bias: Weights = None

    def __init__(
        self,
        ridge: float = 0.0,
        input_dim: Optional[int] = None,
        output_dim: Optional[int] = None,
        name: Optional[str] = None,
    ):
        self.ridge = ridge
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.name = name
        self.state = {{}}

    def initialize(
        self,
        x: Union[NodeInput, Timestep],
        y: Optional[Union[NodeInput, Timestep]] = None,
    ):
        """Initialize node dimensions and state.

        Parameters
        ----------
        x : array-like
            Input data to infer input dimension.
        y : array-like, optional
            Target data to infer output dimension.
        """
        self._set_input_dim(x)
        self._set_output_dim(y)

        # Initialize weights if needed
        if self.Wout is None:
            self.Wout = np.zeros((self.input_dim, self.output_dim))
        if self.bias is None:
            self.bias = np.zeros((self.output_dim,))

        self.state = {{"out": np.zeros((self.output_dim,))}}
        self.initialized = True

    def _step(self, state: State, x: Timestep) -> State:
        """Process a single timestep.

        Parameters
        ----------
        state : dict
            Current state of the node.
        x : array of shape (input_dim,)
            Input timestep.

        Returns
        -------
        dict
            New state with "out" key.
        """
        return {{"out": x @ self.Wout + self.bias}}

    def _run(self, state: State, x: Timeseries) -> tuple[State, Timeseries]:
        """Process a timeseries (vectorized).

        Parameters
        ----------
        state : dict
            Current state of the node.
        x : array of shape (timesteps, input_dim)
            Input timeseries.

        Returns
        -------
        tuple[dict, array]
            Final state and output timeseries.
        """
        out = x @ self.Wout + self.bias
        return {{"out": out[-1]}}, out

    def fit(
        self,
        x: NodeInput,
        y: Optional[NodeInput] = None,
        warmup: int = 0,
    ) -> "{class_name}":
        """Train the node offline.

        Parameters
        ----------
        x : array-like of shape ([series,] timesteps, input_dim)
            Input sequences dataset.
        y : array-like of shape ([series,] timesteps, output_dim)
            Teacher signals dataset.
        warmup : int, default to 0
            Number of timesteps to discard at beginning.

        Returns
        -------
        {class_name}
            Trained node instance.
        """
        if not self.initialized:
            self.initialize(x, y)

        # Handle warmup
        x_train = x[warmup:]
        y_train = y[warmup:] if y is not None else None

        # Your training logic here
        # Example: Ridge regression
        XTX = x_train.T @ x_train
        XTY = x_train.T @ y_train
        ridge_I = self.ridge * np.eye(self.input_dim)
        self.Wout = np.linalg.solve(XTX + ridge_I, XTY)
        self.bias = np.mean(y_train - x_train @ self.Wout, axis=0)

        return self
''',

    "online": '''"""
{class_name} - Custom Online ReservoirPy Node

A node with incremental .partial_fit() learning.
"""

from typing import Callable, Optional, Union
import numpy as np
from reservoirpy import OnlineNode
from reservoirpy.type import State, Timestep, Timeseries, NodeInput, Weights


class {class_name}(OnlineNode):
    """Custom online learning node implementation.

    Parameters
    ----------
    alpha : float, default to 1e-6
        Initial diagonal value of covariance matrix P.
    forgetting : float, default to 1.0
        Forgetting factor (1.0 = no forgetting).
    input_dim : int, optional
        Input dimension. Can be inferred at first call.
    output_dim : int, optional
        Output dimension. Can be inferred at first call.
    name : str, optional
        Node name.

    Example
    -------
    >>> node = {class_name}(alpha=1e-3)
    >>> x = np.random.randn(100, 10)
    >>> y = np.random.randn(100, 3)
    >>> predictions = node.partial_fit(x, y)
    """

    initialized: bool = False
    input_dim: Optional[int] = None
    output_dim: Optional[int] = None
    name: Optional[str] = None
    state: State

    # Learned parameters
    Wout: Weights = None
    bias: Weights = None
    P: np.ndarray = None  # Covariance matrix

    def __init__(
        self,
        alpha: float = 1e-6,
        forgetting: float = 1.0,
        input_dim: Optional[int] = None,
        output_dim: Optional[int] = None,
        name: Optional[str] = None,
    ):
        self.alpha = alpha
        self.forgetting = forgetting
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.name = name
        self.state = {{}}

    def initialize(
        self,
        x: Union[NodeInput, Timestep],
        y: Optional[Union[NodeInput, Timestep]] = None,
    ):
        """Initialize node dimensions and state.

        Parameters
        ----------
        x : array-like
            Input data to infer input dimension.
        y : array-like, optional
            Target data to infer output dimension.
        """
        self._set_input_dim(x)
        self._set_output_dim(y)

        # Initialize weights
        self.Wout = np.zeros((self.input_dim, self.output_dim))
        self.bias = np.zeros((self.output_dim,))
        self.P = np.eye(self.input_dim) / self.alpha

        self.state = {{"out": np.zeros((self.output_dim,))}}
        self.initialized = True

    def _step(self, state: State, x: Timestep) -> State:
        """Process a single timestep (inference only).

        Parameters
        ----------
        state : dict
            Current state of the node.
        x : array of shape (input_dim,)
            Input timestep.

        Returns
        -------
        dict
            New state with "out" key.
        """
        return {{"out": x @ self.Wout + self.bias}}

    def _run(self, state: State, x: Timeseries) -> tuple[State, Timeseries]:
        """Process a timeseries (inference only).

        Parameters
        ----------
        state : dict
            Current state of the node.
        x : array of shape (timesteps, input_dim)
            Input timeseries.

        Returns
        -------
        tuple[dict, array]
            Final state and output timeseries.
        """
        out = x @ self.Wout + self.bias
        return {{"out": out[-1]}}, out

    def _learning_step(self, x: Timestep, y: Optional[Timestep]) -> Timestep:
        """Single step of online learning.

        Called by partial_fit() for each timestep.

        Parameters
        ----------
        x : array of shape (input_dim,)
            Input timestep.
        y : array of shape (output_dim,), optional
            Target timestep.

        Returns
        -------
        array of shape (output_dim,)
            Prediction for this timestep.
        """
        # RLS-style update
        Px = self.P @ x
        k = Px / (self.forgetting + x @ Px)

        # Compute prediction
        prediction = x @ self.Wout + self.bias

        if y is not None:
            # Compute error and update weights
            error = prediction - y
            self.Wout -= np.outer(k, error)

            # Update covariance matrix
            self.P = (self.P - np.outer(k, Px)) / self.forgetting

        return prediction
''',

    "parallel": '''"""
{class_name} - Custom Parallel ReservoirPy Node

A trainable node with parallel multi-series training.
"""

from typing import Callable, Iterable, Optional, Union
import numpy as np
from scipy import linalg
from reservoirpy import ParallelNode
from reservoirpy.type import State, Timestep, Timeseries, NodeInput, Weights


class {class_name}(ParallelNode):
    """Custom parallel trainable node implementation.

    Supports parallel training on multiple timeseries using
    the worker/master pattern.

    Parameters
    ----------
    ridge : float, default to 0.0
        L2 regularization parameter.
    fit_bias : bool, default to True
        Whether to learn a bias term.
    input_dim : int, optional
        Input dimension. Can be inferred at first call.
    output_dim : int, optional
        Output dimension. Can be inferred at first call.
    name : str, optional
        Node name.

    Example
    -------
    >>> node = {class_name}(ridge=1e-5)
    >>> # Multiple timeseries
    >>> x_list = [np.random.randn(100, 10) for _ in range(5)]
    >>> y_list = [np.random.randn(100, 3) for _ in range(5)]
    >>> node.fit(x_list, y_list, warmup=10, workers=4)
    """

    initialized: bool = False
    input_dim: Optional[int] = None
    output_dim: Optional[int] = None
    name: Optional[str] = None
    state: State

    # Learned parameters
    Wout: Weights = None
    bias: Weights = None

    def __init__(
        self,
        ridge: float = 0.0,
        fit_bias: bool = True,
        input_dim: Optional[int] = None,
        output_dim: Optional[int] = None,
        name: Optional[str] = None,
    ):
        self.ridge = ridge
        self.fit_bias = fit_bias
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.name = name
        self.state = {{}}

    def initialize(
        self,
        x: Union[NodeInput, Timestep],
        y: Optional[Union[NodeInput, Timestep]] = None,
    ):
        """Initialize node dimensions and state.

        Parameters
        ----------
        x : array-like
            Input data to infer input dimension.
        y : array-like, optional
            Target data to infer output dimension.
        """
        self._set_input_dim(x)
        self._set_output_dim(y)

        self.state = {{"out": np.zeros((self.output_dim,))}}
        self.initialized = True

    def _step(self, state: State, x: Timestep) -> State:
        """Process a single timestep.

        Parameters
        ----------
        state : dict
            Current state of the node.
        x : array of shape (input_dim,)
            Input timestep.

        Returns
        -------
        dict
            New state with "out" key.
        """
        return {{"out": x @ self.Wout + self.bias}}

    def _run(self, state: State, x: Timeseries) -> tuple[State, Timeseries]:
        """Process a timeseries (vectorized).

        Parameters
        ----------
        state : dict
            Current state of the node.
        x : array of shape (timesteps, input_dim)
            Input timeseries.

        Returns
        -------
        tuple[dict, array]
            Final state and output timeseries.
        """
        out = x @ self.Wout + self.bias
        return {{"out": out[-1]}}, out

    def worker(self, x: Timeseries, y: Optional[Timeseries] = None):
        """Compute partial results for one timeseries.

        This method runs in parallel across multiple workers.
        Return values are collected and passed to master().

        Parameters
        ----------
        x : array of shape (timesteps, input_dim)
            Input timeseries.
        y : array of shape (timesteps, output_dim), optional
            Target timeseries.

        Returns
        -------
        tuple
            Partial results to be aggregated by master().
        """
        # Compute sufficient statistics
        x_sum = np.sum(x, axis=0)
        y_sum = np.sum(y, axis=0) if y is not None else None
        sample_size = x.shape[0]
        XXT = x.T @ x
        YXT = x.T @ y if y is not None else None

        return XXT, YXT, x_sum, y_sum, sample_size

    def master(self, generator: Iterable):
        """Aggregate worker results and compute final weights.

        Parameters
        ----------
        generator : Iterable
            Generator yielding worker results.
        """
        XXT = np.zeros((self.input_dim, self.input_dim))
        YXT = np.zeros((self.input_dim, self.output_dim))
        X_sum = np.zeros((self.input_dim,))
        Y_sum = np.zeros((self.output_dim,))
        total_samples = 0

        # Aggregate results
        for xxt, yxt, x_sum, y_sum, sample_size in generator:
            XXT += xxt
            YXT += yxt
            X_sum += x_sum
            Y_sum += y_sum
            total_samples += sample_size

        # Compute bias-corrected statistics if needed
        if self.fit_bias:
            X_means = X_sum / total_samples
            Y_means = Y_sum / total_samples
            XXT -= total_samples * np.outer(X_means, X_means)
            YXT -= total_samples * np.outer(X_means, Y_means)

        # Solve for weights
        ridge_I = self.ridge * np.eye(self.input_dim)
        self.Wout = linalg.solve(XXT + ridge_I, YXT, assume_a="sym")

        # Compute bias
        if self.fit_bias:
            self.bias = Y_means - X_means @ self.Wout
        else:
            self.bias = np.zeros((self.output_dim,))
'''
}


def generate_node(node_type: str, class_name: str) -> str:
    """Generate node template code."""
    node_type = node_type.lower()
    if node_type not in TEMPLATES:
        valid = ", ".join(TEMPLATES.keys())
        raise ValueError(f"Unknown node type: {node_type}. Valid types: {valid}")

    return TEMPLATES[node_type].format(class_name=class_name)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    node_type = sys.argv[1]
    class_name = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        code = generate_node(node_type, class_name)

        if output_file:
            Path(output_file).write_text(code)
            print(f"Generated {class_name} ({node_type}) -> {output_file}")
        else:
            print(code)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
