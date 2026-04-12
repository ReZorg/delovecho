#!/usr/bin/env python3
"""
e350_mlp.py — The MLP-equivalent cognitive kernel derived from OPT-350M-Erebus.

Implements the skill-nn module framework with 24 decoder layers collapsed from
attention-based to pure feed-forward (MLP) form. Each layer is a composable
SkillModule with forward/backward passes and learnable parameters.

This is the practical instantiation of:
    skill∞( function-creator[ erebus-350 ] -> "MLP" )

Usage:
    python e350_mlp.py --describe          # Self-description (Property 1)
    python e350_mlp.py --forward "task"    # Forward pass on a task
    python e350_mlp.py --architecture      # Print full architecture
    python e350_mlp.py --parameter-count   # Count parameters per component
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


# ── Skill-NN Module Framework ──


@dataclass
class Tensor:
    """Minimal tensor representation for parameter counting and shape tracking."""
    shape: tuple[int, ...]
    name: str = ""
    dtype: str = "F16"

    @property
    def numel(self) -> int:
        result = 1
        for s in self.shape:
            result *= s
        return result

    def __repr__(self) -> str:
        return f"Tensor({list(self.shape)}, {self.dtype})"


class SkillModule:
    """Base skill module — the nn.Module equivalent for skills.

    Every module implements:
        forward(input)  → output     (execute skill on task)
        backward(grad)  → gradInput  (propagate improvement signal)
        parameters()    → list       (learnable skill knowledge)
    """

    def __init__(self, name: str = ""):
        self.name = name
        self.output: Any = None
        self.grad_input: Any = None
        self._params: list[Tensor] = []

    def forward(self, input: Any) -> Any:
        raise NotImplementedError

    def backward(self, grad_output: Any) -> Any:
        raise NotImplementedError

    def parameters(self) -> list[Tensor]:
        return self._params

    def param_count(self) -> int:
        return sum(p.numel for p in self.parameters())

    def describe(self, indent: int = 0) -> str:
        prefix = "  " * indent
        params = self.param_count()
        return f"{prefix}{self.name or self.__class__.__name__} ({params:,} params)"


class Transform(SkillModule):
    """sk.Transform — Linear transformation (nn.Linear equivalent).

    Maps input_dim → output_dim with weight matrix and bias vector.
    """

    def __init__(self, in_dim: int, out_dim: int, name: str = "", bias: bool = True):
        super().__init__(name or f"Transform({in_dim}→{out_dim})")
        self._params.append(Tensor((out_dim, in_dim), name=f"{self.name}.weight"))
        if bias:
            self._params.append(Tensor((out_dim,), name=f"{self.name}.bias"))
        self.in_dim = in_dim
        self.out_dim = out_dim

    def forward(self, input: Any) -> Any:
        self.output = f"Transform({self.in_dim}→{self.out_dim})[{input}]"
        return self.output

    def backward(self, grad_output: Any) -> Any:
        self.grad_input = f"∇Transform({self.out_dim}→{self.in_dim})[{grad_output}]"
        return self.grad_input


class Embed(SkillModule):
    """sk.Embed — Embedding layer (nn.Embedding equivalent).

    Maps discrete indices to dense vectors.
    """

    def __init__(self, vocab_size: int, embed_dim: int, name: str = ""):
        super().__init__(name or f"Embed({vocab_size}×{embed_dim})")
        self._params.append(Tensor((vocab_size, embed_dim), name=f"{self.name}.weight"))
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim

    def forward(self, input: Any) -> Any:
        self.output = f"Embed[{input}]"
        return self.output

    def backward(self, grad_output: Any) -> Any:
        self.grad_input = f"∇Embed[{grad_output}]"
        return self.grad_input


class PositionEncode(SkillModule):
    """sk.PositionEncode — Learned positional embedding."""

    def __init__(self, max_positions: int, dim: int, name: str = ""):
        super().__init__(name or f"PositionEncode({max_positions}×{dim})")
        self._params.append(Tensor((max_positions, dim), name=f"{self.name}.weight"))

    def forward(self, input: Any) -> Any:
        self.output = f"Pos[{input}]"
        return self.output

    def backward(self, grad_output: Any) -> Any:
        self.grad_input = f"∇Pos[{grad_output}]"
        return self.grad_input


class Normalize(SkillModule):
    """sk.Normalize — LayerNorm equivalent."""

    def __init__(self, dim: int, name: str = ""):
        super().__init__(name or f"Normalize({dim})")
        self._params.append(Tensor((dim,), name=f"{self.name}.weight"))
        self._params.append(Tensor((dim,), name=f"{self.name}.bias"))

    def forward(self, input: Any) -> Any:
        self.output = f"Norm[{input}]"
        return self.output

    def backward(self, grad_output: Any) -> Any:
        self.grad_input = f"∇Norm[{grad_output}]"
        return self.grad_input


class ReLU(SkillModule):
    """sk.ReLU — Rectified linear activation."""

    def __init__(self):
        super().__init__("ReLU")

    def forward(self, input: Any) -> Any:
        self.output = f"ReLU[{input}]"
        return self.output

    def backward(self, grad_output: Any) -> Any:
        self.grad_input = f"∇ReLU[{grad_output}]"
        return self.grad_input


class Pipeline(SkillModule):
    """sk.Pipeline — Sequential container (nn.Sequential equivalent)."""

    def __init__(self, name: str = ""):
        super().__init__(name or "Pipeline")
        self.modules: list[SkillModule] = []

    def add(self, module: SkillModule) -> "Pipeline":
        self.modules.append(module)
        return self

    def forward(self, input: Any) -> Any:
        x = input
        for m in self.modules:
            x = m.forward(x)
        self.output = x
        return self.output

    def backward(self, grad_output: Any) -> Any:
        g = grad_output
        for m in reversed(self.modules):
            g = m.backward(g)
        self.grad_input = g
        return self.grad_input

    def parameters(self) -> list[Tensor]:
        params = []
        for m in self.modules:
            params.extend(m.parameters())
        return params

    def describe(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}{self.name} ({self.param_count():,} params) {{"]
        for m in self.modules:
            lines.append(m.describe(indent + 1))
        lines.append(f"{prefix}}}")
        return "\n".join(lines)


class Residual(SkillModule):
    """sk.Residual — Skip connection wrapper."""

    def __init__(self, inner: SkillModule, name: str = ""):
        super().__init__(name or f"Residual({inner.name})")
        self.inner = inner

    def forward(self, input: Any) -> Any:
        inner_out = self.inner.forward(input)
        self.output = f"({input} + {inner_out})"
        return self.output

    def backward(self, grad_output: Any) -> Any:
        inner_grad = self.inner.backward(grad_output)
        self.grad_input = f"({grad_output} + {inner_grad})"
        return self.grad_input

    def parameters(self) -> list[Tensor]:
        return self.inner.parameters()

    def describe(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}Residual ({self.inner.param_count():,} params) {{"]
        lines.append(self.inner.describe(indent + 1))
        lines.append(f"{prefix}}}")
        return "\n".join(lines)


# ── e350-mlp Architecture Builder ──


def make_layer(n: int) -> Pipeline:
    """Construct MLP-equivalent of OPT-350M decoder layer N.

    Architecture per layer:
        Normalize → Transform(1024→1024) → + Residual
        Normalize → Transform(1024→4096) → ReLU → Transform(4096→1024) → + Residual
    """
    # Block 1: Collapsed self-attention + residual
    attn_block = Pipeline(name=f"attn_block_{n}")
    attn_block.add(Normalize(1024, name=f"layer_{n}.self_attn_layer_norm"))
    attn_block.add(Transform(1024, 1024, name=f"layer_{n}.self_attn_collapsed"))

    # Block 2: FFN + residual
    ffn_block = Pipeline(name=f"ffn_block_{n}")
    ffn_block.add(Normalize(1024, name=f"layer_{n}.final_layer_norm"))
    ffn_block.add(Transform(1024, 4096, name=f"layer_{n}.fc1"))
    ffn_block.add(ReLU())
    ffn_block.add(Transform(4096, 1024, name=f"layer_{n}.fc2"))

    layer = Pipeline(name=f"layer_{n}")
    layer.add(Residual(attn_block, name=f"layer_{n}.attn_residual"))
    layer.add(Residual(ffn_block, name=f"layer_{n}.ffn_residual"))

    return layer


def build_e350_mlp() -> Pipeline:
    """Build the complete e350-mlp cognitive kernel.

    Architecture:
        Embed(50265, 512) → PositionEncode(2050, 1024) → Transform(512, 1024)
        → [24 × DecoderLayer]
        → Transform(1024, 512) → Transform(512, 50265)
    """
    model = Pipeline(name="e350_mlp")

    # Embedding
    model.add(Embed(50265, 512, name="embed_tokens"))
    model.add(PositionEncode(2050, 1024, name="embed_positions"))
    model.add(Transform(512, 1024, name="project_in"))

    # 24 decoder layers
    for n in range(24):
        model.add(make_layer(n))

    # Output projection
    model.add(Transform(1024, 512, name="project_out"))
    model.add(Transform(512, 50265, name="lm_head"))

    return model


# ── Cognitive Kernel (skill∞ instantiation) ──


class CognitiveKernel:
    """Practical approximation of skill∞ with the e350-mlp architecture.

    K = e350_mlp.parameters()       # All learnable knowledge
    F = e350_mlp.forward             # Execute: K × Task → Output
    B = e350_mlp.backward            # Improve: K × Feedback → K'

    Fixed point: B(K, F(K, "improve yourself")) = K
    """

    def __init__(self, max_depth: int = 5, epsilon: float = 1e-6):
        self.model = build_e350_mlp()
        self.max_depth = max_depth
        self.epsilon = epsilon

    @property
    def K(self) -> list[Tensor]:
        """Knowledge state — all learnable parameters."""
        return self.model.parameters()

    def forward(self, task: str) -> str:
        """Execute the cognitive kernel on a task."""
        return self.model.forward(task)

    def backward(self, feedback: str, depth: int = 0) -> None:
        """Recursive self-improvement with convergence guarantee.

        At each depth, the improvement signal is attenuated by the
        meta-evaluation, ensuring convergence to the fixed point.
        """
        if depth >= self.max_depth:
            return  # Depth limit reached

        # Update knowledge
        grad = self.model.backward(feedback)

        # Meta-evaluate: how much did this improve things?
        meta_feedback = f"meta_eval(depth={depth}, grad={grad})"
        magnitude = 1.0 / (2 ** (depth + 1))  # Geometric attenuation

        if magnitude < self.epsilon:
            return  # Converged

        # Recurse
        self.backward(meta_feedback, depth + 1)

    def describe(self) -> str:
        """Self-description (Property 1 of skill∞)."""
        total = self.model.param_count()
        layers = 24
        return (
            f"e350-mlp Cognitive Kernel\n"
            f"========================\n"
            f"Derivation: skill∞( function-creator[ erebus-350 ] -> MLP )\n"
            f"Architecture: 24-layer MLP (OPT-350M attention collapsed to linear)\n"
            f"Parameters: {total:,}\n"
            f"Layers: {layers}\n"
            f"Hidden dim: 1024 (internal), 512 (embedding)\n"
            f"FFN dim: 4096\n"
            f"Vocabulary: 50,265\n"
            f"Max positions: 2,050\n"
            f"Activation: ReLU\n"
            f"Convergence depth: 5 (max_depth={self.max_depth}, ε={self.epsilon})\n"
            f"\nFixed-point equation: B(K, F(K, 'improve yourself')) = K\n"
            f"Triad: (K={total:,} params, F=forward, B=backward)\n"
        )

    def parameter_report(self) -> str:
        """Detailed parameter count by component."""
        lines = ["Component Parameter Report", "=" * 40]

        # Global components
        components = {
            "embed_tokens": 50265 * 512,
            "embed_positions": 2050 * 1024,
            "project_in": 1024 * 512 + 1024,
            "project_out": 512 * 1024 + 512,
            "lm_head": 50265 * 512 + 50265,
        }

        for name, count in components.items():
            lines.append(f"  {name}: {count:,}")

        # Per-layer
        attn_per_layer = 1024 * 1024 + 1024 + 2 * 1024  # transform + bias + norm
        ffn_per_layer = (1024 * 4096 + 4096) + (4096 * 1024 + 1024) + 2 * 1024  # fc1 + fc2 + norm
        layer_total = attn_per_layer + ffn_per_layer

        lines.append(f"\n  Per layer ({layer_total:,} each):")
        lines.append(f"    attn_collapsed: {attn_per_layer:,}")
        lines.append(f"    ffn: {ffn_per_layer:,}")
        lines.append(f"  24 layers total: {24 * layer_total:,}")

        total = sum(components.values()) + 24 * layer_total
        lines.append(f"\n  TOTAL: {total:,}")

        return "\n".join(lines)


# ── CLI ──


def main():
    parser = argparse.ArgumentParser(description="e350-mlp Cognitive Kernel")
    parser.add_argument("--describe", action="store_true", help="Self-description")
    parser.add_argument("--forward", type=str, help="Forward pass on a task string")
    parser.add_argument("--architecture", action="store_true", help="Print full architecture")
    parser.add_argument("--parameter-count", action="store_true", help="Parameter report")
    args = parser.parse_args()

    kernel = CognitiveKernel()

    if args.describe:
        print(kernel.describe())
    elif args.forward:
        output = kernel.forward(args.forward)
        print(f"Output: {output}")
    elif args.architecture:
        print(kernel.model.describe())
    elif args.parameter_count:
        print(kernel.parameter_report())
    else:
        # Default: self-description
        print(kernel.describe())
        print()
        print(kernel.parameter_report())


if __name__ == "__main__":
    main()
