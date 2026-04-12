"""
trainer.py — Training loop and inference engine for the Skillm.

Implements:
  1. Corpus management (save/load JSONL)
  2. Training loop with forward/backward passes (nn-style)
  3. LLM-augmented inference for goal → sequence generation
  4. Evaluation metrics and reporting
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from .tokens import Token, TokenType, EndocrineState, SkillMetrics, Layer
from .sequence import (Sequence, ActionNode, PipelineNode, ChoiceNode,
                       GuardNode, LoopNode, action, pipeline, choice, guard, loop)
from .harvesters import SkillmHarvester


# ── Corpus ────────────────────────────────────────────────────────────────────

@dataclass
class Corpus:
    """A collection of training sequences."""
    sequences: list[Sequence] = field(default_factory=list)
    path: str = ""

    def add(self, seq: Sequence):
        self.sequences.append(seq)

    def save(self, path: str = ""):
        path = path or self.path or str(Path.home() / "skillm-corpus-v2.jsonl")
        self.path = path
        with open(path, "w") as f:
            for seq in self.sequences:
                f.write(json.dumps(seq.to_dict()) + "\n")
        return path

    @classmethod
    def load(cls, path: str) -> Corpus:
        sequences = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                seq = _dict_to_sequence(d)
                sequences.append(seq)
        return cls(sequences=sequences, path=path)

    def filter_by_layer(self, layer: Layer) -> list[Sequence]:
        result = []
        for seq in self.sequences:
            tokens = seq.tokens()
            if any(t.layer == layer for t in tokens):
                result.append(seq)
        return result

    def filter_by_outcome(self, outcome: str) -> list[Sequence]:
        return [s for s in self.sequences if s.outcome == outcome]

    def stats(self) -> dict:
        total_tokens = sum(len(s.tokens()) for s in self.sequences)
        verb_dist = {}
        layer_dist = {}
        source_dist = {}
        outcome_dist = {}
        for seq in self.sequences:
            source_dist[seq.source] = source_dist.get(seq.source, 0) + 1
            outcome_dist[seq.outcome] = outcome_dist.get(seq.outcome, 0) + 1
            for token in seq.tokens():
                verb_dist[token.type.value] = verb_dist.get(token.type.value, 0) + 1
                layer_name = token.layer.name if token.layer else "UNIVERSAL"
                layer_dist[layer_name] = layer_dist.get(layer_name, 0) + 1

        return {
            "total_sequences": len(self.sequences),
            "total_tokens": total_tokens,
            "avg_tokens_per_sequence": total_tokens / max(1, len(self.sequences)),
            "verb_distribution": dict(sorted(verb_dist.items(), key=lambda x: -x[1])),
            "layer_distribution": dict(sorted(layer_dist.items(), key=lambda x: -x[1])),
            "source_distribution": dict(sorted(source_dist.items(), key=lambda x: -x[1])),
            "outcome_distribution": outcome_dist,
        }


def _dict_to_sequence(d: dict) -> Sequence:
    """Reconstruct a Sequence from a dict (v2 format)."""
    root_d = d.get("root")
    root = _dict_to_node(root_d) if root_d else None
    endo_d = d.get("endocrine", {})
    endocrine = EndocrineState.from_dict(endo_d) if endo_d else EndocrineState()
    return Sequence(
        id=d.get("id", ""),
        goal=d.get("goal", ""),
        root=root,
        context=d.get("context", {"connectors": [], "variables": {}}),
        endocrine=endocrine,
        source=d.get("source", ""),
        source_id=d.get("source_id", ""),
        outcome=d.get("outcome", ""),
        weight=float(d.get("weight", 1.0)),
    )


def _dict_to_node(d: dict):
    """Reconstruct a node from a dict."""
    if d is None:
        return None
    ntype = d.get("type", "action")
    if ntype == "action":
        token_d = d.get("token", d)
        token = Token.from_dict(token_d)
        return ActionNode(token=token, bind=d.get("bind", ""))
    elif ntype == "pipeline":
        steps = [_dict_to_node(s) for s in d.get("steps", [])]
        return PipelineNode(steps=[s for s in steps if s])
    elif ntype == "choice":
        branches = []
        for b in d.get("branches", []):
            node = _dict_to_node(b.get("node"))
            if node:
                branches.append((b.get("label", ""), b.get("when", ""), node))
        return ChoiceNode(branches=branches, strategy=d.get("strategy", "highest_activation"))
    elif ntype == "guard":
        return GuardNode(
            try_node=_dict_to_node(d.get("try")),
            catch_node=_dict_to_node(d.get("catch")),
        )
    elif ntype == "loop":
        return LoopNode(
            body=_dict_to_node(d.get("body")),
            until=d.get("until", "convergence"),
            max_iterations=d.get("max_iterations", 10),
        )
    return None


# ── Training Loop ─────────────────────────────────────────────────────────────

@dataclass
class TrainingConfig:
    """Configuration for the training loop."""
    epochs: int = 10
    learning_rate: float = 0.01
    momentum: float = 0.9
    weight_decay: float = 0.001
    batch_size: int = 8
    success_target: float = 1.0
    failure_target: float = 0.0
    report_every: int = 1
    save_every: int = 5


@dataclass
class TrainingMetrics:
    """Metrics collected during training."""
    epoch: int = 0
    total_loss: float = 0.0
    avg_loss: float = 0.0
    avg_activation: float = 0.0
    success_sequences: int = 0
    failure_sequences: int = 0
    total_tokens_processed: int = 0
    weight_norm: float = 0.0
    gradient_norm: float = 0.0
    elapsed_ms: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


class SkillmTrainer:
    """Training loop for the Skillm procedural language model.

    Follows the nn training pattern:
      for each epoch:
        for each sequence in corpus:
          output = sequence.forward()
          loss = criterion(output, target)
          sequence.backward(target)
    """

    def __init__(self, config: TrainingConfig = None):
        self.config = config or TrainingConfig()
        self.history: list[TrainingMetrics] = []
        self.skill_registry: dict[str, SkillMetrics] = {}

    def train(self, corpus: Corpus) -> list[TrainingMetrics]:
        """Run the full training loop over the corpus."""
        print(f"\n{'='*60}")
        print(f"  SKILLM TRAINING")
        print(f"  Sequences: {len(corpus.sequences)}")
        print(f"  Epochs: {self.config.epochs}")
        print(f"  Learning rate: {self.config.learning_rate}")
        print(f"{'='*60}\n")

        self.history = []

        for epoch in range(1, self.config.epochs + 1):
            metrics = self._train_epoch(corpus, epoch)
            self.history.append(metrics)

            if epoch % self.config.report_every == 0:
                self._report(metrics)

        print(f"\n{'='*60}")
        print(f"  TRAINING COMPLETE")
        print(f"  Final loss: {self.history[-1].avg_loss:.6f}")
        print(f"  Final activation: {self.history[-1].avg_activation:.4f}")
        print(f"{'='*60}\n")

        return self.history

    def _train_epoch(self, corpus: Corpus, epoch: int) -> TrainingMetrics:
        """Train one epoch over all sequences."""
        t0 = time.time()
        total_loss = 0.0
        total_activation = 0.0
        total_tokens = 0
        weight_sum_sq = 0.0
        grad_sum_sq = 0.0
        success_count = 0
        failure_count = 0

        for seq in corpus.sequences:
            # Determine target from outcome
            if seq.outcome == "success":
                target = self.config.success_target
                success_count += 1
            elif seq.outcome == "failure":
                target = self.config.failure_target
                failure_count += 1
            else:
                target = 0.5  # Uncertain
                success_count += 1  # Count as partial

            # Forward pass
            activation = seq.forward()
            total_activation += activation

            # Compute loss (MSE)
            loss = 0.5 * (activation - target) ** 2
            total_loss += loss * seq.weight  # Weighted loss

            # Backward pass
            grad = seq.backward(target)

            # Track parameter norms
            for token in seq.tokens():
                total_tokens += 1
                if token.layer == Layer.EXECUTION:
                    weight_sum_sq += token.weight ** 2 + token.bias ** 2

                    # Apply learning rate and weight decay
                    token.weight *= (1.0 - self.config.weight_decay)
                    token.bias *= (1.0 - self.config.weight_decay)

            # Update skill registry
            self._update_registry(seq)

        n = max(1, len(corpus.sequences))
        elapsed = (time.time() - t0) * 1000

        return TrainingMetrics(
            epoch=epoch,
            total_loss=total_loss,
            avg_loss=total_loss / n,
            avg_activation=total_activation / n,
            success_sequences=success_count,
            failure_sequences=failure_count,
            total_tokens_processed=total_tokens,
            weight_norm=math.sqrt(weight_sum_sq),
            gradient_norm=0.0,  # Computed during backward
            elapsed_ms=elapsed,
        )

    def _update_registry(self, seq: Sequence):
        """Update the skill registry with execution outcomes."""
        for token in seq.tokens():
            if token.type == TokenType.STEP and token.tool:
                name = token.tool
                if name not in self.skill_registry:
                    self.skill_registry[name] = SkillMetrics(
                        skill_name=name,
                        weight=token.weight,
                        bias=token.bias,
                    )
                metrics = self.skill_registry[name]
                success = seq.outcome == "success"
                duration = token.params.get("duration_ms", 0) or 0
                metrics.record_execution(success, float(duration))

    def _report(self, m: TrainingMetrics):
        """Print a training progress report."""
        bar_len = 30
        progress = m.epoch / self.config.epochs
        filled = int(bar_len * progress)
        bar = "█" * filled + "░" * (bar_len - filled)

        print(f"  Epoch {m.epoch:3d}/{self.config.epochs} [{bar}] "
              f"loss={m.avg_loss:.6f} act={m.avg_activation:.4f} "
              f"tokens={m.total_tokens_processed} "
              f"w_norm={m.weight_norm:.3f} "
              f"{m.elapsed_ms:.0f}ms")

    def save_history(self, path: str = "") -> str:
        """Save training history to JSON."""
        path = path or str(Path.home() / "skillm-training-history.json")
        with open(path, "w") as f:
            json.dump({
                "config": asdict(self.config),
                "history": [m.to_dict() for m in self.history],
                "skill_registry": {
                    name: m.to_dict()
                    for name, m in self.skill_registry.items()
                },
            }, f, indent=2)
        return path

    def save_registry(self, path: str = "") -> str:
        """Save the skill registry to JSON."""
        path = path or str(Path.home() / "skillm-skill-registry.json")
        with open(path, "w") as f:
            json.dump({
                name: m.to_dict()
                for name, m in self.skill_registry.items()
            }, f, indent=2)
        return path


# ── LLM-Augmented Inference ──────────────────────────────────────────────────

class SkillmInference:
    """Generate action sequences from natural language goals.

    Uses the trained corpus as few-shot examples and optionally
    calls an LLM for sequence synthesis.
    """

    def __init__(self, corpus: Corpus = None, use_llm: bool = True):
        self.corpus = corpus or Corpus()
        self.use_llm = use_llm
        self._client = None

    def infer(self, goal: str, connector: str = None) -> Sequence:
        """Generate a Sequence from a natural language goal.

        Strategy:
          1. Search corpus for similar goals (keyword matching)
          2. If found, adapt the best match
          3. If not found and LLM enabled, synthesize via LLM
          4. Fallback to rule-based template
        """
        # Step 1: Corpus search
        best_match = self._search_corpus(goal)
        if best_match and best_match.weight > 1.5:
            return self._adapt_sequence(best_match, goal)

        # Step 2: LLM synthesis
        if self.use_llm:
            llm_seq = self._llm_synthesize(goal, connector, best_match)
            if llm_seq:
                return llm_seq

        # Step 3: Rule-based fallback
        return self._rule_based(goal, connector)

    def _search_corpus(self, goal: str) -> Optional[Sequence]:
        """Find the most similar sequence in the corpus."""
        goal_words = set(goal.lower().split())
        best_score = 0
        best_seq = None

        for seq in self.corpus.sequences:
            seq_words = set(seq.goal.lower().split())
            overlap = len(goal_words & seq_words)
            score = overlap / max(1, len(goal_words | seq_words))
            # Weight by sequence weight and outcome
            if seq.outcome == "success":
                score *= seq.weight
            if score > best_score:
                best_score = score
                best_seq = seq

        return best_seq

    def _adapt_sequence(self, template: Sequence, goal: str) -> Sequence:
        """Adapt a corpus sequence to a new goal."""
        import copy
        seq = copy.deepcopy(template)
        seq.goal = goal
        seq.id = str(__import__("uuid").uuid4())
        seq.outcome = ""  # Not yet executed
        return seq

    def _llm_synthesize(self, goal: str, connector: str = None,
                        example: Sequence = None) -> Optional[Sequence]:
        """Use an LLM to synthesize an action sequence."""
        try:
            from openai import OpenAI
        except ImportError:
            return None

        if self._client is None:
            self._client = OpenAI()

        # Build the prompt with vocabulary and example
        vocab_desc = "\n".join([
            f"  {tt.value}: {tt.name}" for tt in TokenType
            if tt not in (TokenType.NOOP, TokenType.IMPOSSIBLE)
        ])

        example_json = ""
        if example:
            example_json = f"\n\nExample sequence for similar goal:\n```json\n{example.to_json()}\n```"

        prompt = f"""You are a Skillm — a procedural language model that generates action sequences.

Given a goal, produce a JSON action sequence using these token types:
{vocab_desc}

The sequence must be a valid JSON object with this structure:
{{
  "goal": "<the goal>",
  "root": {{
    "type": "pipeline",
    "steps": [
      {{"type": "action", "token": {{"type": "<TOKEN_TYPE>", "tool": "<tool_name>", "description": "<what this step does>", "salience": 0.5}}}}
    ]
  }},
  "source": "llm",
  "outcome": "",
  "weight": 1.0
}}

Connector hint: {connector or 'auto-detect'}
{example_json}

Goal: {goal}

Respond with ONLY the JSON object, no markdown fencing."""

        try:
            response = self._client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000,
            )
            content = response.choices[0].message.content.strip()
            # Strip markdown fencing if present
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                if content.endswith("```"):
                    content = content[:-3]
            d = json.loads(content)
            return _dict_to_sequence(d)
        except Exception as e:
            print(f"  [warn] LLM inference failed: {e}", file=sys.stderr)
            return None

    def _rule_based(self, goal: str, connector: str = None) -> Sequence:
        """Generate a sequence using rule-based templates."""
        # Import the existing infer_sequence logic
        goal_lower = goal.lower()

        # Detect primary verb
        verb_map = {
            "find": TokenType.DISCOVER, "search": TokenType.DISCOVER,
            "list": TokenType.DISCOVER, "get": TokenType.DISCOVER,
            "create": TokenType.CREATE, "add": TokenType.CREATE,
            "build": TokenType.CREATE, "make": TokenType.CREATE,
            "update": TokenType.MUTATE, "edit": TokenType.MUTATE,
            "change": TokenType.MUTATE, "modify": TokenType.MUTATE,
            "delete": TokenType.DESTROY, "remove": TokenType.DESTROY,
            "run": TokenType.COMPOSE, "execute": TokenType.COMPOSE,
            "send": TokenType.COMPOSE, "deploy": TokenType.COMPOSE,
            "monitor": TokenType.OBSERVE, "analyze": TokenType.OBSERVE,
            "report": TokenType.OBSERVE, "track": TokenType.OBSERVE,
            "migrate": TokenType.ORCHESTRATE, "sync": TokenType.ORCHESTRATE,
            "prepare": TokenType.ORCHESTRATE,
            "label": TokenType.CLASSIFY, "tag": TokenType.CLASSIFY,
            "categorize": TokenType.CLASSIFY,
            "think": TokenType.THINK, "reflect": TokenType.THINK,
            "train": TokenType.TRAIN, "learn": TokenType.TRAIN,
            "ingest": TokenType.INGEST, "embed": TokenType.EMBED,
        }

        primary_verb = TokenType.COMPOSE
        for word in goal_lower.split():
            clean = word.strip(".,;:!?\"'()[]")
            if clean in verb_map:
                primary_verb = verb_map[clean]
                break

        steps = [
            ActionNode(Token(
                type=TokenType.DISCOVER,
                tool=f"{connector or 'auto'}:discover",
                description=f"Find relevant entities for: {goal}",
                salience=0.6,
            )),
            ActionNode(Token(
                type=primary_verb,
                tool=f"{connector or 'auto'}:{primary_verb.value.lower()}",
                description=f"Execute {primary_verb.value}: {goal}",
                salience=0.7,
            )),
        ]

        return Sequence(
            goal=goal,
            root=PipelineNode(steps=steps),
            source="rule-based",
            outcome="",
            weight=0.5,
        )
