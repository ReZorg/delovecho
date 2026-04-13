"""
sequence.py — Action Sequence model with semiring composition.

A Sequence is a procedural program composed from Tokens using:
  ⊗ (pipeline)  — sequential execution
  ⊕ (choice)    — alternative branches
  guard          — try/catch error handling
  loop           — repeated execution

Follows the nn skill's Module API:
  forward(input)  → output
  backward(input, gradOutput) → gradInput
  parameters() → weights, gradWeights
"""

from __future__ import annotations

import json
import math
import uuid
from dataclasses import dataclass, field
from typing import Optional, Any

from .tokens import Token, TokenType, EndocrineState, SkillMetrics, Layer


# ── Sequence Node Types ───────────────────────────────────────────────────────

@dataclass
class ActionNode:
    """Leaf node: a single token invocation."""
    token: Token
    bind: str = ""  # variable name to bind result to

    def forward(self, context: dict) -> float:
        """Forward pass: return token activation."""
        return self.token.activation()

    def backward(self, grad: float) -> float:
        """Backward pass: propagate gradient to token weight."""
        if self.token.layer == Layer.EXECUTION:
            # Update execution-layer token weights
            output = self.token.activation()
            local_grad = grad * output * (1.0 - output)
            self.token.weight -= 0.01 * local_grad
            self.token.bias -= 0.01 * local_grad
            return local_grad
        return grad

    def tokens(self) -> list[Token]:
        return [self.token]

    def depth(self) -> int:
        return 1

    def to_dict(self) -> dict:
        d = {"type": "action", "token": self.token.to_dict()}
        if self.bind:
            d["bind"] = self.bind
        return d


@dataclass
class PipelineNode:
    """⊗ Sequential composition: execute steps in order."""
    steps: list = field(default_factory=list)  # list of nodes

    def forward(self, context: dict) -> float:
        """Forward pass: product of step activations (⊗ semantics)."""
        result = 1.0
        for step in self.steps:
            result *= step.forward(context)
        return result

    def backward(self, grad: float) -> float:
        """Backward pass: chain rule through the pipeline."""
        for step in reversed(self.steps):
            grad = step.backward(grad)
        return grad

    def tokens(self) -> list[Token]:
        result = []
        for step in self.steps:
            result.extend(step.tokens())
        return result

    def depth(self) -> int:
        return 1 + max((s.depth() for s in self.steps), default=0)

    def to_dict(self) -> dict:
        return {
            "type": "pipeline",
            "steps": [s.to_dict() for s in self.steps],
        }


@dataclass
class ChoiceNode:
    """⊕ Additive composition: choose one branch."""
    branches: list = field(default_factory=list)  # list of (label, condition, node)
    strategy: str = "highest_activation"

    def forward(self, context: dict) -> float:
        """Forward pass: max of branch activations (⊕ semantics)."""
        if not self.branches:
            return 0.0
        activations = [(b[2].forward(context), i) for i, b in enumerate(self.branches)]
        best_act, best_idx = max(activations, key=lambda x: x[0])
        self._selected = best_idx
        return best_act

    def backward(self, grad: float) -> float:
        """Backward pass: only propagate to selected branch."""
        if hasattr(self, '_selected') and self._selected < len(self.branches):
            return self.branches[self._selected][2].backward(grad)
        return grad

    def tokens(self) -> list[Token]:
        result = []
        for _, _, node in self.branches:
            result.extend(node.tokens())
        return result

    def depth(self) -> int:
        return 1 + max((n.depth() for _, _, n in self.branches), default=0)

    def to_dict(self) -> dict:
        return {
            "type": "choice",
            "strategy": self.strategy,
            "branches": [
                {"label": label, "when": cond, "node": node.to_dict()}
                for label, cond, node in self.branches
            ],
        }


@dataclass
class GuardNode:
    """Try/catch error handling."""
    try_node: Any = None
    catch_node: Any = None

    def forward(self, context: dict) -> float:
        """Forward pass: try node activation, fallback to catch."""
        act = self.try_node.forward(context) if self.try_node else 0.0
        if act < 0.1 and self.catch_node:  # Low activation = likely failure
            return self.catch_node.forward(context)
        return act

    def backward(self, grad: float) -> float:
        if self.try_node:
            return self.try_node.backward(grad)
        return grad

    def tokens(self) -> list[Token]:
        result = []
        if self.try_node:
            result.extend(self.try_node.tokens())
        if self.catch_node:
            result.extend(self.catch_node.tokens())
        return result

    def depth(self) -> int:
        d = 0
        if self.try_node:
            d = max(d, self.try_node.depth())
        if self.catch_node:
            d = max(d, self.catch_node.depth())
        return 1 + d

    def to_dict(self) -> dict:
        d = {"type": "guard"}
        if self.try_node:
            d["try"] = self.try_node.to_dict()
        if self.catch_node:
            d["catch"] = self.catch_node.to_dict()
        return d


@dataclass
class LoopNode:
    """Repeated execution until condition met."""
    body: Any = None
    until: str = "max_iterations"
    max_iterations: int = 10

    def forward(self, context: dict) -> float:
        """Forward pass: average activation over iterations."""
        if not self.body:
            return 0.0
        total = 0.0
        for i in range(self.max_iterations):
            act = self.body.forward(context)
            total += act
            if act > 0.95:  # Convergence
                return total / (i + 1)
        return total / self.max_iterations

    def backward(self, grad: float) -> float:
        if self.body:
            return self.body.backward(grad)
        return grad

    def tokens(self) -> list[Token]:
        return self.body.tokens() if self.body else []

    def depth(self) -> int:
        return 1 + (self.body.depth() if self.body else 0)

    def to_dict(self) -> dict:
        d = {"type": "loop", "until": self.until, "max_iterations": self.max_iterations}
        if self.body:
            d["body"] = self.body.to_dict()
        return d


# ── Sequence (the top-level procedural program) ──────────────────────────────

@dataclass
class Sequence:
    """A complete procedural program — the unit of generation in a Skillm.

    Analogous to nn.Sequential: a container of nodes with forward/backward.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    goal: str = ""
    root: Any = None  # The root node (PipelineNode, ChoiceNode, etc.)
    context: dict = field(default_factory=lambda: {"connectors": [], "variables": {}})
    endocrine: EndocrineState = field(default_factory=EndocrineState)

    # Training metadata
    source: str = ""
    source_id: str = ""
    outcome: str = ""
    weight: float = 1.0

    def forward(self) -> float:
        """Forward pass through the entire sequence.

        Returns the sequence activation — a scalar in [0, 1] representing
        the model's confidence that this sequence will succeed.
        """
        if self.root is None:
            return 0.0

        # Apply endocrine modulation to all cognitive tokens
        attention_bias = self.endocrine.attention_bias()
        for token in self.tokens():
            if token.is_cognitive:
                token.salience = max(0.0, min(1.0,
                    token.salience + (1.0 - attention_bias) * 0.1))

        return self.root.forward(self.context)

    def backward(self, target: float = 1.0) -> float:
        """Backward pass: propagate gradient from outcome to all tokens.

        target=1.0 for successful sequences, 0.0 for failures.
        """
        if self.root is None:
            return 0.0
        output = self.forward()
        grad = output - target  # MSE gradient
        return self.root.backward(grad)

    def tokens(self) -> list[Token]:
        """Return all tokens in the sequence (flattened)."""
        return self.root.tokens() if self.root else []

    def parameters(self) -> tuple[list[float], list[float]]:
        """Return (weights, gradients) for all execution-layer tokens.

        Follows the nn Module API: parameters() → {weights}, {gradWeights}.
        """
        weights = []
        grads = []
        for token in self.tokens():
            if token.layer == Layer.EXECUTION:
                weights.extend([token.weight, token.bias])
                grads.extend([0.0, 0.0])  # Placeholder
        return weights, grads

    def depth(self) -> int:
        return self.root.depth() if self.root else 0

    def verb_distribution(self) -> dict[str, int]:
        """Count occurrences of each token type."""
        dist = {}
        for token in self.tokens():
            key = token.type.value
            dist[key] = dist.get(key, 0) + 1
        return dist

    def layer_distribution(self) -> dict[str, int]:
        """Count tokens per layer."""
        dist = {}
        for token in self.tokens():
            layer = token.layer
            key = layer.name if layer else "UNIVERSAL"
            dist[key] = dist.get(key, 0) + 1
        return dist

    def to_dict(self) -> dict:
        return {
            "version": "2.0.0",
            "id": self.id,
            "goal": self.goal,
            "context": self.context,
            "endocrine": self.endocrine.to_dict(),
            "root": self.root.to_dict() if self.root else None,
            "source": self.source,
            "source_id": self.source_id,
            "outcome": self.outcome,
            "weight": self.weight,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_mermaid(self) -> str:
        """Render the sequence as a Mermaid flowchart."""
        lines = ["graph TD"]
        counter = [0]

        def nid():
            counter[0] += 1
            return f"N{counter[0]}"

        def render(node, parent=None):
            n = nid()
            if isinstance(node, ActionNode):
                t = node.token
                label = f"{t.type.value}\\n{t.description or t.tool}"
                act = t.activation()
                if act > 0.7:
                    lines.append(f'    {n}["{label}"]:::high')
                elif act > 0.4:
                    lines.append(f'    {n}["{label}"]:::mid')
                else:
                    lines.append(f'    {n}["{label}"]:::low')
            elif isinstance(node, PipelineNode):
                lines.append(f'    {n}(["⊗ Pipeline"])')
                prev = n
                for step in node.steps:
                    child = render(step, n)
                    lines.append(f"    {prev} --> {child}")
                    prev = child
                return prev
            elif isinstance(node, ChoiceNode):
                lines.append(f'    {n}{{"⊕ Choice"}}')
                for label, cond, branch in node.branches:
                    child = render(branch, n)
                    lines.append(f"    {n} -->|{label}| {child}")
            elif isinstance(node, GuardNode):
                lines.append(f'    {n}["Guard"]')
                if node.try_node:
                    tc = render(node.try_node, n)
                    lines.append(f"    {n} -->|try| {tc}")
                if node.catch_node:
                    cc = render(node.catch_node, n)
                    lines.append(f"    {n} -->|catch| {cc}")
            elif isinstance(node, LoopNode):
                lines.append(f'    {n}["Loop: {node.until}"]')
                if node.body:
                    bc = render(node.body, n)
                    lines.append(f"    {n} --> {bc}")
                    lines.append(f"    {bc} -.->|repeat| {n}")
            return n

        if self.root:
            render(self.root)

        lines.append("")
        lines.append("    classDef high fill:#2d6a4f,stroke:#1b4332,color:#fff")
        lines.append("    classDef mid fill:#e9c46a,stroke:#f4a261,color:#000")
        lines.append("    classDef low fill:#e76f51,stroke:#264653,color:#fff")
        return "\n".join(lines)

    def __repr__(self) -> str:
        n = len(self.tokens())
        d = self.depth()
        return f"Sequence(goal='{self.goal}', tokens={n}, depth={d})"


# ── Builder helpers ───────────────────────────────────────────────────────────

def action(token_type: TokenType, tool: str = "", description: str = "",
           **kwargs) -> ActionNode:
    """Create an ActionNode from a token type."""
    return ActionNode(token=Token(type=token_type, tool=tool,
                                  description=description, **kwargs))


def pipeline(*steps) -> PipelineNode:
    """Create a PipelineNode (⊗) from steps."""
    return PipelineNode(steps=list(steps))


def choice(*branches, strategy: str = "highest_activation") -> ChoiceNode:
    """Create a ChoiceNode (⊕) from (label, condition, node) tuples."""
    return ChoiceNode(branches=list(branches), strategy=strategy)


def guard(try_node, catch_node=None) -> GuardNode:
    """Create a GuardNode (try/catch)."""
    return GuardNode(try_node=try_node, catch_node=catch_node)


def loop(body, until: str = "convergence", max_iterations: int = 10) -> LoopNode:
    """Create a LoopNode."""
    return LoopNode(body=body, until=until, max_iterations=max_iterations)
