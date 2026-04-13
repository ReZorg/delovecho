#!/usr/bin/env python3

import numpy as np
from reservoirpy.nodes import Node, TrainableNode, OnlineNode

class DeltaChatMessageNode(Node):
    """Encodes DeltaChat message metadata into a feature vector."""

    def __init__(self, input_dim=None, name=None):
        super().__init__(input_dim=input_dim, name=name)

    def initialize(self, x):
        self._set_input_dim(x)
        # Output: is_bot, is_info, has_html, has_attachment, show_padlock
        self.output_dim = 5
        self.state = {"out": np.zeros((self.output_dim,))}
        self.initialized = True

    def _step(self, state, msg_data):
        # msg_data is a dict from get_messages result
        features = np.array([
            float(msg_data.get("isBot", False)),
            float(msg_data.get("isInfo", False)),
            float(msg_data.get("hasHtml", False)),
            1.0 if msg_data.get("file") else 0.0,
            float(msg_data.get("showPadlock", False)),
        ])
        return {"out": features}

class ConversationStateNode(TrainableNode):
    """Tracks conversation state across multiple chats."""

    def __init__(self, input_dim=None, output_dim=None, name=None):
        super().__init__(input_dim=input_dim, output_dim=output_dim, name=name)
        self.Wout = None

    def initialize(self, x, y=None):
        self._set_input_dim(x)
        self._set_output_dim(y)
        self.state = {"out": np.zeros((self.output_dim,))}
        self.initialized = True

    def _step(self, state, x):
        if self.Wout is None:
            return {"out": np.zeros(self.output_dim)}
        return {"out": x @ self.Wout}

    def fit(self, x, y, warmup=0):
        if not self.initialized:
            self.initialize(x, y)
        x_train = x[warmup:]
        y_train = y[warmup:]
        self.Wout = np.linalg.lstsq(x_train, y_train, rcond=None)[0]
        return self

class CognitiveResponseNode(OnlineNode):
    """Generates ec9o-modulated response vectors."""

    def __init__(self, alpha=1e-6, input_dim=None, output_dim=None, name=None):
        super().__init__(alpha=alpha, input_dim=input_dim, output_dim=output_dim, name=name)
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
        Px = self.P @ x
        k = Px / (1 + x @ Px)
        prediction = x @ self.Wout
        error = prediction - y
        self.Wout -= np.outer(k, error)
        self.P -= np.outer(k, Px)
        return prediction
