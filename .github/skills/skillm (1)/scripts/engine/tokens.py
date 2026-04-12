"""
tokens.py — Token type system for the Skillm procedural language.

Four token layers corresponding to the four-layer skillm stack:

  Layer 1 (Cognitive):   THINK, MODULATE, SAY, NARRATE, RECALL
  Layer 2 (Domain):      TRAVERSE, TRANSITION, DETECT, SIMULATE, RECONCILE, MAP_ENTITY
  Layer 3 (Execution):   WORKFLOW_START, STEP, WORKFLOW_END
  Layer 4 (Meta):        INGEST, EMBED, RETRIEVE, TRAIN

Plus the 10 universal MCP verbs that cut across all layers:
  DISCOVER, INSPECT, CREATE, MUTATE, DESTROY,
  NAVIGATE, COMPOSE, OBSERVE, ORCHESTRATE, CLASSIFY
"""

from __future__ import annotations

import math
import json
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from typing import Optional, Any


# ── Layer Enum ────────────────────────────────────────────────────────────────

class Layer(Enum):
    COGNITIVE = 1
    DOMAIN = 2
    EXECUTION = 3
    META = 4


# ── Token Types ───────────────────────────────────────────────────────────────

class TokenType(Enum):
    """All token types across the four-layer stack."""
    # Layer 1: Cognitive (from deltecho-cognitive)
    THINK = "THINK"
    MODULATE = "MODULATE"
    SAY = "SAY"
    NARRATE = "NARRATE"
    RECALL = "RECALL"
    SESSION_START = "SESSION_START"
    SESSION_END = "SESSION_END"

    # Layer 2: Domain (from fincosys hypergraph)
    TRAVERSE = "TRAVERSE"
    TRANSITION = "TRANSITION"
    DETECT = "DETECT"
    SIMULATE = "SIMULATE"
    RECONCILE = "RECONCILE"
    MAP_ENTITY = "MAP_ENTITY"

    # Layer 3: Execution (from cipc-assistant workflow)
    WORKFLOW_START = "WORKFLOW_START"
    STEP = "STEP"
    WORKFLOW_END = "WORKFLOW_END"

    # Layer 4: Meta (from regima-rag-knowledge)
    INGEST = "INGEST"
    EMBED = "EMBED"
    RETRIEVE = "RETRIEVE"
    TRAIN = "TRAIN"

    # Universal MCP verbs (cross-layer)
    DISCOVER = "DISCOVER"
    INSPECT = "INSPECT"
    CREATE = "CREATE"
    MUTATE = "MUTATE"
    DESTROY = "DESTROY"
    NAVIGATE = "NAVIGATE"
    COMPOSE = "COMPOSE"
    OBSERVE = "OBSERVE"
    ORCHESTRATE = "ORCHESTRATE"
    CLASSIFY = "CLASSIFY"

    # Semiring identities
    NOOP = "ε"       # multiplicative identity
    IMPOSSIBLE = "∅"  # additive identity / zero


TOKEN_LAYER = {
    TokenType.THINK: Layer.COGNITIVE,
    TokenType.MODULATE: Layer.COGNITIVE,
    TokenType.SAY: Layer.COGNITIVE,
    TokenType.NARRATE: Layer.COGNITIVE,
    TokenType.RECALL: Layer.COGNITIVE,
    TokenType.SESSION_START: Layer.COGNITIVE,
    TokenType.SESSION_END: Layer.COGNITIVE,
    TokenType.TRAVERSE: Layer.DOMAIN,
    TokenType.TRANSITION: Layer.DOMAIN,
    TokenType.DETECT: Layer.DOMAIN,
    TokenType.SIMULATE: Layer.DOMAIN,
    TokenType.RECONCILE: Layer.DOMAIN,
    TokenType.MAP_ENTITY: Layer.DOMAIN,
    TokenType.WORKFLOW_START: Layer.EXECUTION,
    TokenType.STEP: Layer.EXECUTION,
    TokenType.WORKFLOW_END: Layer.EXECUTION,
    TokenType.INGEST: Layer.META,
    TokenType.EMBED: Layer.META,
    TokenType.RETRIEVE: Layer.META,
    TokenType.TRAIN: Layer.META,
}


# ── Token ─────────────────────────────────────────────────────────────────────

@dataclass
class Token:
    """A single token in the procedural language.

    Each token has a type, optional continuous parameters (valence, arousal,
    salience from the cognitive layer), and a payload dict for tool-specific
    parameters.
    """
    type: TokenType
    tool: str = ""
    params: dict = field(default_factory=dict)
    description: str = ""

    # Continuous signals (Layer 1: Cognitive)
    valence: float = 0.0     # [-1, 1] positive/negative affect
    arousal: float = 0.0     # [0, 1] activation level
    salience: float = 0.5    # [0, 1] attention weight

    # Neural parameters (Layer 3: Execution)
    weight: float = 1.0
    bias: float = 0.0

    # Metadata
    timestamp: str = ""
    source_id: str = ""

    @property
    def layer(self) -> Optional[Layer]:
        return TOKEN_LAYER.get(self.type)

    @property
    def is_cognitive(self) -> bool:
        return self.layer == Layer.COGNITIVE

    @property
    def is_terminal(self) -> bool:
        return self.type in (TokenType.NOOP, TokenType.IMPOSSIBLE,
                             TokenType.SESSION_END, TokenType.WORKFLOW_END)

    def activation(self) -> float:
        """Compute the token's activation value (forward pass output).

        For cognitive tokens: sigmoid(valence * salience + arousal)
        For execution tokens: sigmoid(weight * salience + bias)
        For others: salience
        """
        if self.is_cognitive:
            x = self.valence * self.salience + self.arousal
        elif self.layer == Layer.EXECUTION:
            x = self.weight * self.salience + self.bias
        else:
            return self.salience
        return 1.0 / (1.0 + math.exp(-x))

    def to_dict(self) -> dict:
        d = asdict(self)
        d["type"] = self.type.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> Token:
        d = dict(d)
        d["type"] = TokenType(d["type"])
        return cls(**{k: v for k, v in d.items()
                      if k in cls.__dataclass_fields__})

    def __repr__(self) -> str:
        parts = [self.type.value]
        if self.tool:
            parts.append(f"tool={self.tool}")
        if self.description:
            parts.append(f'"{self.description}"')
        act = self.activation()
        parts.append(f"act={act:.3f}")
        return f"Token({', '.join(parts)})"


# ── Endocrine State (Layer 1 modulation) ──────────────────────────────────────

@dataclass
class EndocrineState:
    """Virtual endocrine snapshot that modulates token selection probabilities.

    Maps to the dte_endocrine_snapshots table in deltecho-cognitive.
    """
    cognitive_mode: str = "NEUTRAL"
    cortisol: float = 0.15
    dopamine: float = 0.30
    serotonin: float = 0.40
    oxytocin: float = 0.10
    norepinephrine: float = 0.10
    endorphin: float = 0.10
    melatonin: float = 0.00
    gaba: float = 0.30

    @property
    def stress(self) -> float:
        return self.cortisol + self.norepinephrine

    @property
    def reward(self) -> float:
        return self.dopamine + self.endorphin

    @property
    def calm(self) -> float:
        return self.serotonin + self.gaba + self.oxytocin

    def modulation_vector(self) -> list[float]:
        """Return the 8-dimensional modulation vector."""
        return [self.cortisol, self.dopamine, self.serotonin, self.oxytocin,
                self.norepinephrine, self.endorphin, self.melatonin, self.gaba]

    def attention_bias(self) -> float:
        """Compute attention bias from endocrine state.

        High stress → higher salience threshold (focus on important things).
        High reward → lower salience threshold (explore more).
        """
        return 0.5 + 0.3 * self.stress - 0.2 * self.reward

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> EndocrineState:
        return cls(**{k: v for k, v in d.items()
                      if k in cls.__dataclass_fields__})


# ── Skill Metrics (Layer 3 neural parameters) ────────────────────────────────

@dataclass
class SkillMetrics:
    """Neural network parameters for a single skill.

    Maps to the skill_metrics table in cipc-assistant.
    Implements a single-neuron perceptron with gradient tracking.
    """
    skill_name: str = ""
    workflow_type: str = ""
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_duration_ms: float = 0.0

    # Neural parameters
    weight: float = 1.0
    bias: float = 0.0
    learning_rate: float = 0.01
    gradient_accum: float = 0.0
    last_forward_output: Optional[float] = None
    last_backward_grad: Optional[float] = None

    @property
    def success_rate(self) -> float:
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count

    def forward(self, x: float) -> float:
        """Forward pass: sigmoid(w*x + b)."""
        z = self.weight * x + self.bias
        output = 1.0 / (1.0 + math.exp(-max(-500, min(500, z))))
        self.last_forward_output = output
        return output

    def backward(self, target: float) -> float:
        """Backward pass: compute gradient and accumulate.

        Returns the gradient for upstream propagation.
        """
        if self.last_forward_output is None:
            return 0.0
        output = self.last_forward_output
        error = output - target
        # Sigmoid derivative: output * (1 - output)
        grad = error * output * (1.0 - output)
        self.gradient_accum += grad
        self.last_backward_grad = grad
        return grad

    def update(self):
        """Apply accumulated gradient to update parameters."""
        if self.gradient_accum != 0.0:
            self.weight -= self.learning_rate * self.gradient_accum
            self.bias -= self.learning_rate * self.gradient_accum
            self.gradient_accum = 0.0

    def record_execution(self, success: bool, duration_ms: float):
        """Record an execution outcome and update neural parameters."""
        self.execution_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        # Running average of duration
        n = self.execution_count
        self.avg_duration_ms = ((n - 1) * self.avg_duration_ms + duration_ms) / n
        # Train the perceptron
        x = self.success_rate
        self.forward(x)
        self.backward(1.0 if success else 0.0)
        self.update()

    def to_dict(self) -> dict:
        d = asdict(self)
        d["success_rate"] = self.success_rate
        return d

    @classmethod
    def from_dict(cls, d: dict) -> SkillMetrics:
        d = dict(d)
        d.pop("success_rate", None)
        return cls(**{k: v for k, v in d.items()
                      if k in cls.__dataclass_fields__})
