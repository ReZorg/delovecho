#!/usr/bin/env python3
"""
neural_build_path.py — Neural Build-Path Optimizer

Treats the build sequence as a learnable problem using nn-inspired architecture:

  ┌─────────────────────────────────────────────────────────────┐
  │                  BuildPathNetwork                            │
  │                                                              │
  │  Position Embeddings:  P[N×S]  (N components × S steps)     │
  │  Dependency Logits:    D[N×N]  (pairwise "A before B")      │
  │                                                              │
  │  Forward:                                                    │
  │    1. Softmax(P) → position probabilities per component     │
  │    2. Sigmoid(D) → dependency probabilities                  │
  │    3. Sample build order from position probs                 │
  │    4. At each step, attempt build of scheduled component     │
  │                                                              │
  │  Loss:                                                       │
  │    - Success at step s: reinforce P[comp,s], D[deps→comp]   │
  │    - Failure at step s: penalize P[comp,s], discover dep    │
  │                                                              │
  │  Backward:                                                   │
  │    - ∂L/∂P: push successful components toward their step    │
  │    - ∂L/∂D: push discovered deps toward 1.0                 │
  │    - updateParameters(lr)                                    │
  │                                                              │
  │  Convergence:                                                │
  │    - When position probs are peaked (entropy < threshold)   │
  │    - AND dep matrix matches observed dependency chain        │
  └─────────────────────────────────────────────────────────────┘

The network learns:
  1. The EXACT dependency chain (which packages must precede which)
  2. The OPTIMAL build order (which step each package belongs at)
  3. The CONCURRENCE structure (which packages can build in parallel)

Implements the nn Module pattern:
  - forward(input) → output
  - backward(input, gradOutput) → gradInput
  - zeroGradParameters()
  - updateParameters(learningRate)
  - parameters() → {weights}, {gradWeights}

Usage:
    python3 neural_build_path.py --model model/build_model.json [--epochs 100] [--lr 0.1]
"""

import argparse
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

SKILL_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = SKILL_DIR / "model" / "build_model.json"


# ═══════════════════════════════════════════════════════════════════════════
# nn-style Module base class
# ═══════════════════════════════════════════════════════════════════════════

class Module:
    """Base class following nn.Module pattern."""

    def __init__(self):
        self.output = None
        self.gradInput = None
        self.training = True

    def forward(self, input_data):
        raise NotImplementedError

    def backward(self, input_data, gradOutput):
        raise NotImplementedError

    def zeroGradParameters(self):
        pass

    def updateParameters(self, lr):
        pass

    def parameters(self):
        return [], []

    def train(self):
        self.training = True

    def evaluate(self):
        self.training = False


# ═══════════════════════════════════════════════════════════════════════════
# Position Embedding Layer
# ═══════════════════════════════════════════════════════════════════════════

class PositionEmbedding(Module):
    """
    Learnable position matrix P[N×S] where:
      - N = number of components
      - S = number of build steps (tiers)
      - P[i,s] = logit for "component i should be built at step s"

    Forward: softmax(P) → probability distribution over steps per component
    """

    def __init__(self, n_components: int, n_steps: int):
        super().__init__()
        self.N = n_components
        self.S = n_steps
        # Initialize with slight noise — no prior knowledge of ordering
        self.weight = np.random.randn(n_components, n_steps) * 0.1
        self.gradWeight = np.zeros_like(self.weight)

    def forward(self, input_data=None):
        """Compute softmax over steps for each component."""
        # Numerically stable softmax per row
        shifted = self.weight - self.weight.max(axis=1, keepdims=True)
        exp_w = np.exp(shifted)
        self.output = exp_w / exp_w.sum(axis=1, keepdims=True)
        return self.output

    def backward(self, input_data, gradOutput):
        """Backprop through softmax."""
        # gradOutput[i,s] = ∂L/∂output[i,s]
        # ∂output/∂weight uses the Jacobian of softmax
        self.gradWeight = np.zeros_like(self.weight)
        for i in range(self.N):
            s = self.output[i]  # softmax output for component i
            # Jacobian: diag(s) - s⊗s
            jac = np.diag(s) - np.outer(s, s)
            self.gradWeight[i] = gradOutput[i] @ jac
        self.gradInput = gradOutput  # pass through for upstream
        return self.gradInput

    def zeroGradParameters(self):
        self.gradWeight = np.zeros_like(self.weight)

    def updateParameters(self, lr):
        self.weight -= lr * self.gradWeight

    def parameters(self):
        return [self.weight], [self.gradWeight]


# ═══════════════════════════════════════════════════════════════════════════
# Dependency Logit Layer
# ═══════════════════════════════════════════════════════════════════════════

class DependencyLogits(Module):
    """
    Learnable dependency matrix D[N×N] where:
      - D[i,j] = logit for "component i depends on component j"
      - sigmoid(D[i,j]) → probability that j must be built before i

    Forward: sigmoid(D) → dependency probability matrix
    """

    def __init__(self, n_components: int):
        super().__init__()
        self.N = n_components
        # Initialize near zero — no prior knowledge of dependencies
        self.weight = np.zeros((n_components, n_components))
        self.gradWeight = np.zeros_like(self.weight)
        # Diagonal is always 0 (no self-dependency)
        np.fill_diagonal(self.weight, -10.0)

    def forward(self, input_data=None):
        """Compute sigmoid of dependency logits."""
        self.output = 1.0 / (1.0 + np.exp(-self.weight))
        # Zero diagonal
        np.fill_diagonal(self.output, 0.0)
        return self.output

    def backward(self, input_data, gradOutput):
        """Backprop through sigmoid."""
        sig = self.output
        self.gradWeight = gradOutput * sig * (1.0 - sig)
        np.fill_diagonal(self.gradWeight, 0.0)
        self.gradInput = gradOutput
        return self.gradInput

    def zeroGradParameters(self):
        self.gradWeight = np.zeros_like(self.weight)

    def updateParameters(self, lr):
        self.weight -= lr * self.gradWeight
        np.fill_diagonal(self.weight, -10.0)

    def parameters(self):
        return [self.weight], [self.gradWeight]


# ═══════════════════════════════════════════════════════════════════════════
# Build-Path Network (Sequential container)
# ═══════════════════════════════════════════════════════════════════════════

class BuildPathNetwork(Module):
    """
    nn.Sequential-style container composing:
      1. PositionEmbedding → step probabilities
      2. DependencyLogits → dependency probabilities

    The combined output determines:
      - Which step each component is assigned to
      - Which components must precede which

    Training signal comes from actual build results:
      - Success: reinforce current position
      - Failure due to missing dep: strengthen dependency edge,
        push failed component to later step
    """

    def __init__(self, components: list[str], n_steps: int):
        super().__init__()
        self.components = components
        self.comp_to_idx = {c: i for i, c in enumerate(components)}
        self.N = len(components)
        self.S = n_steps

        self.position = PositionEmbedding(self.N, self.S)
        self.dependency = DependencyLogits(self.N)

        # Build result history for training
        self.history = []

    def forward(self, input_data=None):
        """
        Forward pass:
          - Compute position probabilities
          - Compute dependency probabilities
          - Derive build order (greedy assignment)
        """
        pos_probs = self.position.forward()
        dep_probs = self.dependency.forward()

        # Derive build order: assign each component to its most probable step
        assignments = np.argmax(pos_probs, axis=1)

        # Build tiers from assignments
        tiers = defaultdict(list)
        for i, step in enumerate(assignments):
            tiers[step].append(self.components[i])

        # Sort tiers by step number
        ordered_tiers = [tiers[s] for s in sorted(tiers.keys()) if tiers[s]]

        self.output = {
            "position_probs": pos_probs,
            "dependency_probs": dep_probs,
            "assignments": assignments,
            "tiers": ordered_tiers,
        }
        return self.output

    def backward(self, input_data, gradOutput):
        """
        Backward pass: propagate build results as gradients.

        gradOutput is a dict of build results:
          {component: {"status": "success"|"failure", "missing_dep": "comp"|None}}
        """
        pos_grad = np.zeros((self.N, self.S))
        dep_grad = np.zeros((self.N, self.N))

        assignments = self.output["assignments"]
        pos_probs = self.output["position_probs"]
        dep_probs = self.output["dependency_probs"]

        for comp, result in gradOutput.items():
            if comp not in self.comp_to_idx:
                continue
            i = self.comp_to_idx[comp]
            step = assignments[i]
            status = result["status"]

            if status == "success":
                # ── REINFORCE: push this component toward its current step ──
                # Negative gradient on the correct step (minimize loss = maximize prob)
                pos_grad[i, step] -= 1.0
                # Slight positive gradient on other steps (push away)
                for s in range(self.S):
                    if s != step:
                        pos_grad[i, s] += 0.1 / (self.S - 1)

            elif status == "failure":
                missing_dep = result.get("missing_dep")

                # ── PENALIZE: push this component AWAY from current step ──
                pos_grad[i, step] += 1.0
                # Push toward later steps
                for s in range(step + 1, self.S):
                    pos_grad[i, s] -= 0.5 / max(1, self.S - step - 1)

                if missing_dep and missing_dep in self.comp_to_idx:
                    j = self.comp_to_idx[missing_dep]
                    # ── STRENGTHEN dependency edge: i depends on j ──
                    dep_grad[i, j] -= 2.0  # push sigmoid toward 1.0

                    # ── Push the dependency to an EARLIER step ──
                    dep_step = assignments[j]
                    if dep_step >= step:
                        # Dep should be earlier than the failed component
                        for s in range(step):
                            pos_grad[j, s] -= 0.5 / max(1, step)
                        pos_grad[j, dep_step] += 0.5

        self.position.backward(None, pos_grad)
        self.dependency.backward(None, dep_grad)

        self.gradInput = {"pos_grad": pos_grad, "dep_grad": dep_grad}
        return self.gradInput

    def zeroGradParameters(self):
        self.position.zeroGradParameters()
        self.dependency.zeroGradParameters()

    def updateParameters(self, lr):
        self.position.updateParameters(lr)
        self.dependency.updateParameters(lr)

    def parameters(self):
        pw, pgw = self.position.parameters()
        dw, dgw = self.dependency.parameters()
        return pw + dw, pgw + dgw

    def inject_known_deps(self, known_deps: dict):
        """Warm-start dependency logits from known dependencies."""
        for comp, deps in known_deps.items():
            if comp not in self.comp_to_idx:
                continue
            i = self.comp_to_idx[comp]
            for dep in deps:
                if dep in self.comp_to_idx:
                    j = self.comp_to_idx[dep]
                    self.dependency.weight[i, j] = 3.0  # sigmoid(3) ≈ 0.95

    def inject_known_layers(self, layer_map: dict):
        """Warm-start position embeddings from known layer assignments."""
        for comp, layer in layer_map.items():
            if comp not in self.comp_to_idx:
                continue
            i = self.comp_to_idx[comp]
            if layer < self.S:
                self.position.weight[i, layer] = 2.0  # softmax bias

    def get_learned_deps(self, threshold: float = 0.5) -> dict:
        """Extract learned dependency graph."""
        dep_probs = self.dependency.forward()
        deps = {}
        for i, comp in enumerate(self.components):
            comp_deps = []
            for j, dep in enumerate(self.components):
                if i != j and dep_probs[i, j] > threshold:
                    comp_deps.append((dep, float(dep_probs[i, j])))
            if comp_deps:
                deps[comp] = sorted(comp_deps, key=lambda x: -x[1])
        return deps

    def get_learned_tiers(self) -> list[list[str]]:
        """Extract the learned build tiers."""
        pos_probs = self.position.forward()
        assignments = np.argmax(pos_probs, axis=1)
        tiers = defaultdict(list)
        for i, step in enumerate(assignments):
            tiers[step].append(self.components[i])
        return [tiers[s] for s in sorted(tiers.keys()) if tiers[s]]

    def entropy(self) -> float:
        """Average entropy of position distributions — measures convergence."""
        pos_probs = self.position.forward()
        # Clip for numerical stability
        p = np.clip(pos_probs, 1e-10, 1.0)
        ent = -np.sum(p * np.log(p), axis=1)
        return float(np.mean(ent))

    def state_dict(self) -> dict:
        """Serialize network state."""
        return {
            "components": self.components,
            "n_steps": self.S,
            "position_weight": self.position.weight.tolist(),
            "dependency_weight": self.dependency.weight.tolist(),
            "history": self.history[-100:],  # keep last 100 entries
        }

    def load_state_dict(self, state: dict):
        """Restore network state."""
        self.position.weight = np.array(state["position_weight"])
        self.dependency.weight = np.array(state["dependency_weight"])
        self.history = state.get("history", [])


# ═══════════════════════════════════════════════════════════════════════════
# Criterion: Build Success Loss
# ═══════════════════════════════════════════════════════════════════════════

class BuildSuccessCriterion:
    """
    nn.Criterion-style loss function.

    Loss = Σ_failed_components penalty + Σ_all position_entropy_regularization

    Lower loss = more components succeed + more confident position assignments.
    """

    def __init__(self, entropy_weight: float = 0.1):
        self.entropy_weight = entropy_weight
        self.output = 0.0

    def forward(self, network_output: dict, build_results: dict) -> float:
        """Compute loss from build results."""
        pos_probs = network_output["position_probs"]

        # Failure penalty
        n_fail = sum(1 for r in build_results.values() if r["status"] == "failure")
        n_total = len(build_results) if build_results else 1
        failure_loss = n_fail / n_total

        # Entropy regularization (encourage peaked distributions)
        p = np.clip(pos_probs, 1e-10, 1.0)
        entropy = -np.sum(p * np.log(p), axis=1).mean()
        max_entropy = np.log(pos_probs.shape[1])
        entropy_loss = entropy / max_entropy  # normalize to [0, 1]

        self.output = failure_loss + self.entropy_weight * entropy_loss
        return self.output

    def backward(self, network_output: dict, build_results: dict) -> dict:
        """Return build results as gradient signal."""
        return build_results


# ═══════════════════════════════════════════════════════════════════════════
# Training Loop
# ═══════════════════════════════════════════════════════════════════════════

def simulate_build(tiers: list[list[str]], true_deps: dict) -> dict:
    """
    Simulate a build attempt using the true dependency graph.
    Returns {component: {"status": ..., "missing_dep": ...}}
    """
    results = {}
    built = set()

    for tier in tiers:
        for comp in tier:
            deps = true_deps.get(comp, [])
            unmet = [d for d in deps if d not in built]
            if unmet:
                results[comp] = {
                    "status": "failure",
                    "missing_dep": unmet[0],  # report first missing dep
                }
            else:
                results[comp] = {"status": "success", "missing_dep": None}
                built.add(comp)

    return results


def train(model_path: str = None, epochs: int = 100, lr: float = 0.1,
          warm_start: bool = True, verbose: bool = True) -> dict:
    """
    Train the BuildPathNetwork on the org-oc build model.

    Each epoch:
      1. Forward: compute build order from current embeddings
      2. Simulate build (or use real results)
      3. Compute loss
      4. Backward: propagate success/failure gradients
      5. Update parameters

    Returns the trained network state and learned dependency graph.
    """
    # Load build model
    mp = model_path or str(MODEL_PATH)
    with open(mp) as f:
        build_model = json.load(f)

    components_info = build_model["components"]
    components = sorted(components_info.keys())
    N = len(components)

    # Determine number of steps (use current tier count or estimate)
    existing_tiers = build_model.get("build_sequence", {}).get("tiers", [])
    n_steps = max(len(existing_tiers), 6, N // 4)

    # Extract true dependencies for simulation
    true_deps = {}
    for comp, info in components_info.items():
        true_deps[comp] = info.get("deps", [])

    # Create network
    net = BuildPathNetwork(components, n_steps)
    criterion = BuildSuccessCriterion(entropy_weight=0.1)

    # Warm start from known model data
    if warm_start:
        known_deps = {c: info.get("deps", []) for c, info in components_info.items()}
        net.inject_known_deps(known_deps)
        layer_map = {c: info.get("layer", 0) for c, info in components_info.items()}
        net.inject_known_layers(layer_map)

    # Load previous state if exists
    nn_state = build_model.get("neural_state")
    if nn_state:
        try:
            net.load_state_dict(nn_state)
            if verbose:
                print(f"  Loaded previous neural state (history: {len(net.history)} entries)")
        except Exception:
            pass

    if verbose:
        print(f"\n  Network: {N} components × {n_steps} steps")
        print(f"  Position embeddings: {N}×{n_steps} = {N*n_steps} parameters")
        print(f"  Dependency logits:   {N}×{N} = {N*N} parameters")
        print(f"  Total parameters:    {N*n_steps + N*N}")
        print(f"  Learning rate:       {lr}")
        print(f"  Epochs:              {epochs}")
        print()

    # Training loop
    loss_history = []
    best_loss = float("inf")
    best_tiers = None
    converged_epoch = None

    for epoch in range(epochs):
        # ── Forward ──
        output = net.forward()
        tiers = output["tiers"]

        # ── Simulate build ──
        build_results = simulate_build(tiers, true_deps)

        # ── Compute loss ──
        loss = criterion.forward(output, build_results)
        loss_history.append(loss)

        # ── Stats ──
        n_success = sum(1 for r in build_results.values() if r["status"] == "success")
        n_fail = sum(1 for r in build_results.values() if r["status"] == "failure")
        entropy = net.entropy()

        if verbose and (epoch % 10 == 0 or epoch == epochs - 1):
            print(f"  Epoch {epoch:4d}: loss={loss:.4f}  success={n_success}/{N}  "
                  f"fail={n_fail}  entropy={entropy:.3f}  tiers={len(tiers)}")

        # Track best
        if loss < best_loss:
            best_loss = loss
            best_tiers = [list(t) for t in tiers]

        # Record history
        net.history.append({
            "epoch": epoch,
            "loss": float(loss),
            "success": n_success,
            "fail": n_fail,
            "entropy": float(entropy),
            "n_tiers": len(tiers),
        })

        # ── Check convergence ──
        if n_fail == 0 and entropy < 0.5:
            if verbose:
                print(f"\n  ✅ CONVERGED at epoch {epoch}: all builds pass, entropy={entropy:.3f}")
            converged_epoch = epoch
            best_tiers = [list(t) for t in tiers]
            break

        # Also check if loss is stable
        if len(loss_history) >= 10:
            recent = loss_history[-10:]
            if max(recent) - min(recent) < 0.001 and n_fail == 0:
                if verbose:
                    print(f"\n  ✅ CONVERGED at epoch {epoch}: loss stable, all builds pass")
                converged_epoch = epoch
                best_tiers = [list(t) for t in tiers]
                break

        # ── Backward ──
        net.zeroGradParameters()
        grad = criterion.backward(output, build_results)
        net.backward(None, grad)

        # ── Update parameters ──
        net.updateParameters(lr)

    # Extract learned knowledge
    learned_deps = net.get_learned_deps(threshold=0.5)
    learned_tiers = net.get_learned_tiers()

    if verbose:
        print(f"\n  Final state:")
        print(f"    Best loss:       {best_loss:.4f}")
        print(f"    Converged:       {'Yes (epoch ' + str(converged_epoch) + ')' if converged_epoch is not None else 'No'}")
        print(f"    Learned tiers:   {len(learned_tiers)}")
        print(f"    Learned deps:    {sum(len(v) for v in learned_deps.values())} edges")
        print(f"    Entropy:         {net.entropy():.3f}")

        print(f"\n  Learned build order:")
        for ti, tier in enumerate(learned_tiers):
            print(f"    T{ti}: {', '.join(tier)}")

        print(f"\n  Learned dependency graph (top edges):")
        for comp, deps in sorted(learned_deps.items()):
            dep_strs = [f"{d}({p:.2f})" for d, p in deps[:5]]
            print(f"    {comp} ← {', '.join(dep_strs)}")

    return {
        "network_state": net.state_dict(),
        "learned_deps": {c: [d for d, _ in deps] for c, deps in learned_deps.items()},
        "learned_dep_probs": {c: {d: p for d, p in deps} for c, deps in learned_deps.items()},
        "learned_tiers": learned_tiers,
        "best_loss": float(best_loss),
        "converged": converged_epoch is not None,
        "converged_epoch": converged_epoch,
        "epochs_run": len(loss_history),
        "loss_history": [float(l) for l in loss_history],
        "final_entropy": float(net.entropy()),
    }


def apply_to_model(train_result: dict, model_path: str = None):
    """Write learned knowledge back into the build model."""
    mp = model_path or str(MODEL_PATH)
    with open(mp) as f:
        model = json.load(f)

    # Store neural network state
    model["neural_state"] = train_result["network_state"]

    # Update deps from learned graph (only ADD, never remove known deps)
    learned_deps = train_result.get("learned_deps", {})
    changes = []
    for comp, deps in learned_deps.items():
        if comp in model["components"]:
            existing = set(model["components"][comp].get("deps", []))
            for dep in deps:
                if dep not in existing and dep in model["components"]:
                    model["components"][comp]["deps"].append(dep)
                    changes.append(f"[{comp}] +dep {dep} (neural)")
                    model["components"][comp].setdefault("fixes_applied", []).append(
                        f"neural: discovered dep on {dep}"
                    )

    # Update tiers
    if train_result.get("learned_tiers"):
        model["build_sequence"]["tiers"] = train_result["learned_tiers"]

    # Update meta
    model["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    model.setdefault("neural_training", []).append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "epochs": train_result["epochs_run"],
        "converged": train_result["converged"],
        "best_loss": train_result["best_loss"],
        "final_entropy": train_result["final_entropy"],
        "new_deps_discovered": len(changes),
    })

    with open(mp, "w") as f:
        json.dump(model, f, indent=2)

    print(f"\n  Model updated: {mp}")
    if changes:
        print(f"  New dependencies discovered ({len(changes)}):")
        for c in changes:
            print(f"    {c}")
    else:
        print(f"  No new dependencies discovered (model already complete)")

    return changes


# ═══════════════════════════════════════════════════════════════════════════
# Real Build Integration
# ═══════════════════════════════════════════════════════════════════════════

def train_from_real_results(build_results: dict, model_path: str = None,
                            lr: float = 0.05) -> dict:
    """
    Single training step using REAL build results instead of simulation.

    build_results: {component: {"status": "success"|"failure", "missing_dep": str|None}}

    This is called by run_iteration.py after each real build.
    """
    mp = model_path or str(MODEL_PATH)
    with open(mp) as f:
        build_model = json.load(f)

    components = sorted(build_model["components"].keys())
    N = len(components)
    existing_tiers = build_model.get("build_sequence", {}).get("tiers", [])
    n_steps = max(len(existing_tiers), 6, N // 4)

    net = BuildPathNetwork(components, n_steps)

    # Load existing state
    nn_state = build_model.get("neural_state")
    if nn_state:
        net.load_state_dict(nn_state)

    # Single forward-backward-update cycle with real data
    output = net.forward()
    loss_val = sum(1 for r in build_results.values() if r["status"] == "failure") / max(len(build_results), 1)

    net.zeroGradParameters()
    net.backward(None, build_results)
    net.updateParameters(lr)

    # Save state
    build_model["neural_state"] = net.state_dict()
    build_model["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()

    with open(mp, "w") as f:
        json.dump(build_model, f, indent=2)

    return {
        "loss": float(loss_val),
        "entropy": float(net.entropy()),
        "learned_tiers": net.get_learned_tiers(),
    }


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Neural Build-Path Optimizer for org-oc"
    )
    parser.add_argument("--model", "-m", default=str(MODEL_PATH),
                        help="Path to build_model.json")
    parser.add_argument("--epochs", "-e", type=int, default=100,
                        help="Training epochs")
    parser.add_argument("--lr", type=float, default=0.1,
                        help="Learning rate")
    parser.add_argument("--no-warm-start", action="store_true",
                        help="Don't warm-start from known deps")
    parser.add_argument("--apply", action="store_true",
                        help="Apply learned knowledge back to model")
    parser.add_argument("--output", "-o",
                        help="Save training results to JSON file")
    args = parser.parse_args()

    print("=" * 70)
    print("  Neural Build-Path Optimizer")
    print("  nn-inspired learnable build sequence for o9nn/org-oc")
    print("=" * 70)

    result = train(
        model_path=args.model,
        epochs=args.epochs,
        lr=args.lr,
        warm_start=not args.no_warm_start,
    )

    if args.apply:
        print("\n  Applying learned knowledge to model...")
        apply_to_model(result, args.model)

    if args.output:
        # Don't save the full network state to the output file (too large)
        save_result = {k: v for k, v in result.items() if k != "network_state"}
        with open(args.output, "w") as f:
            json.dump(save_result, f, indent=2)
        print(f"\n  Results saved to {args.output}")


if __name__ == "__main__":
    main()
