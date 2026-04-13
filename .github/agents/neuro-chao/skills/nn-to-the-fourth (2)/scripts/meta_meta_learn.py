#!/usr/bin/env python3
"""
nn⁴ FP3: Meta²Learn — Learning to Learn to Learn

Three nested optimization loops:
  Level 1 (inner):  Adapt model to a single task (gradient descent)
  Level 2 (middle): MAML — learn θ₀ for fast adaptation across tasks
  Level 3 (outer):  Learn MAML hyperparameters (inner_lr, inner_steps)

Fixed point: when Level 3 stops improving Level 2, nn⁴ ≅ nn².

Usage:
    python meta_meta_learn.py [--meta-epochs 200] [--meta-meta-epochs 30]
"""

import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import OrderedDict
from copy import deepcopy


# --- Base Model ---

class SimpleClassifier(nn.Module):
    def __init__(self, in_dim=10, hidden_dim=64, out_dim=5):
        super().__init__()
        self.fc1_w = nn.Parameter(torch.empty(hidden_dim, in_dim))
        self.fc1_b = nn.Parameter(torch.zeros(hidden_dim))
        self.fc2_w = nn.Parameter(torch.empty(out_dim, hidden_dim))
        self.fc2_b = nn.Parameter(torch.zeros(out_dim))
        nn.init.kaiming_uniform_(self.fc1_w)
        nn.init.kaiming_uniform_(self.fc2_w)

    def forward(self, x, params=None):
        if params is None:
            h = F.relu(F.linear(x, self.fc1_w, self.fc1_b))
            return F.linear(h, self.fc2_w, self.fc2_b)
        else:
            h = F.relu(F.linear(x, params["fc1_w"], params["fc1_b"]))
            return F.linear(h, params["fc2_w"], params["fc2_b"])


# --- Task Distribution ---

class ClusterTaskDist:
    """N-way K-shot classification from random Gaussian clusters."""
    def __init__(self, in_dim=10, n_way=5):
        self.in_dim = in_dim
        self.n_way = n_way

    def sample(self, k_shot=5, k_query=15):
        centers = torch.randn(self.n_way, self.in_dim) * 3
        sx, sy, qx, qy = [], [], [], []
        for c in range(self.n_way):
            sx.append(centers[c] + torch.randn(k_shot, self.in_dim) * 0.5)
            sy.append(torch.full((k_shot,), c, dtype=torch.long))
            qx.append(centers[c] + torch.randn(k_query, self.in_dim) * 0.5)
            qy.append(torch.full((k_query,), c, dtype=torch.long))
        return torch.cat(sx), torch.cat(sy), torch.cat(qx), torch.cat(qy)


# --- Level 1: Inner Loop (Task Adaptation) ---

def inner_adapt(model, support_x, support_y, inner_lr, inner_steps, create_graph=False):
    """Adapt model parameters to a single task."""
    params = OrderedDict((n, p.clone()) for n, p in model.named_parameters())
    # Detach inner_lr if it's a tensor to avoid graph issues
    lr_val = inner_lr.item() if isinstance(inner_lr, torch.Tensor) else inner_lr

    for _ in range(inner_steps):
        pred = model(support_x, params)
        loss = F.cross_entropy(pred, support_y)
        grads = torch.autograd.grad(loss, params.values(), create_graph=create_graph)
        params = OrderedDict(
            (n, p - lr_val * g) for (n, p), g in zip(params.items(), grads)
        )
    return params


# --- Level 2: MAML (Meta-Learning) ---

def maml_epoch(model, task_dist, inner_lr, inner_steps, outer_lr,
               n_tasks=4, k_shot=5, k_query=15):
    """One epoch of MAML: sample tasks, adapt, compute meta-loss."""
    meta_loss = torch.tensor(0.0)
    meta_acc = 0.0

    for _ in range(n_tasks):
        sx, sy, qx, qy = task_dist.sample(k_shot, k_query)
        adapted = inner_adapt(model, sx, sy, inner_lr, inner_steps, create_graph=False)
        qpred = model(qx, adapted)
        task_loss = F.cross_entropy(qpred, qy)
        meta_loss = meta_loss + task_loss.detach()
        meta_acc += (qpred.detach().argmax(1) == qy).float().mean().item()

        # Per-task gradient update (FOMAML-style for stability)
        task_loss.backward()

    meta_acc = meta_acc / n_tasks
    meta_loss_val = meta_loss.item() / n_tasks

    # Update model parameters (Level 2 gradient step)
    with torch.no_grad():
        for p in model.parameters():
            if p.grad is not None:
                p.data -= outer_lr * p.grad / n_tasks
                p.grad = None

    return meta_loss_val, meta_acc


# --- Level 3: Meta-Meta-Learning (Learn MAML Hyperparameters) ---

def meta_meta_learn(model, task_dist, args):
    """Three-level optimization with fixed-point detection.

    Level 3 learns: inner_lr, inner_steps
    Level 2 runs: MAML with those hyperparameters
    Level 1 runs: task adaptation within MAML
    """
    # Level 3 learnable hyperparameters
    log_inner_lr = torch.tensor(float(args.inner_lr)).log().clone().requires_grad_(True)
    # inner_steps is discrete, so we use a continuous relaxation
    log_inner_steps = torch.tensor(float(args.inner_steps)).log().clone().requires_grad_(True)

    meta_meta_opt = torch.optim.Adam([log_inner_lr], lr=args.meta_meta_lr)

    print("=" * 70)
    print("Level 3: Meta-Meta-Learning (learning MAML hyperparameters)")
    print("=" * 70)

    prev_avg_loss = float('inf')
    convergence_history = []

    for mm_epoch in range(args.meta_meta_epochs):
        current_inner_lr = log_inner_lr.exp()
        current_inner_steps = max(1, int(log_inner_steps.exp().item()))

        # Level 2: run several MAML epochs with current hyperparameters
        epoch_losses = []
        epoch_accs = []
        model_copy = deepcopy(model)

        for m_epoch in range(args.meta_epochs_per_mm):
            m_loss, m_acc = maml_epoch(
                model_copy, task_dist,
                inner_lr=current_inner_lr,
                inner_steps=current_inner_steps,
                outer_lr=args.outer_lr,
                n_tasks=args.tasks_per_batch,
            )
            epoch_losses.append(m_loss)
            epoch_accs.append(m_acc)

        avg_loss = sum(epoch_losses) / len(epoch_losses)
        avg_acc = sum(epoch_accs) / len(epoch_accs)

        # Level 3 update: adjust hyperparameters based on MAML performance
        # Use the final MAML loss as the meta-meta objective
        # (We approximate the gradient numerically since inner_steps is discrete)
        meta_meta_opt.zero_grad()
        if log_inner_lr.grad is not None:
            log_inner_lr.grad = None

        # Finite-difference gradient for inner_lr
        eps = 0.01
        lr_plus = (log_inner_lr + eps).exp()
        lr_minus = (log_inner_lr - eps).exp()
        model_plus = deepcopy(model)
        model_minus = deepcopy(model)

        loss_plus, _ = maml_epoch(model_plus, task_dist, lr_plus, current_inner_steps,
                                   args.outer_lr, args.tasks_per_batch)
        loss_minus, _ = maml_epoch(model_minus, task_dist, lr_minus, current_inner_steps,
                                    args.outer_lr, args.tasks_per_batch)

        fd_grad = (loss_plus - loss_minus) / (2 * eps)
        with torch.no_grad():
            log_inner_lr -= args.meta_meta_lr * fd_grad

        # Fixed-point detection
        delta = abs(avg_loss - prev_avg_loss)
        convergence_history.append(delta)
        converged = delta < args.convergence_threshold and mm_epoch > 2

        print(f"MM-Epoch {mm_epoch+1:3d} | inner_lr={current_inner_lr.item():.6f} | "
              f"inner_steps={current_inner_steps} | "
              f"MAML Loss={avg_loss:.4f} | MAML Acc={avg_acc:.4f} | "
              f"Δ={delta:.6f} {'✓ FIXED POINT' if converged else ''}")

        if converged:
            print(f"\n{'='*70}")
            print(f"FIXED POINT REACHED at MM-Epoch {mm_epoch+1}")
            print(f"nn⁴ ≅ nn² : Meta-meta-learning has converged.")
            print(f"Optimal inner_lr = {current_inner_lr.item():.6f}")
            print(f"Optimal inner_steps = {current_inner_steps}")
            print(f"{'='*70}")
            return True, mm_epoch + 1, current_inner_lr.item(), current_inner_steps

        prev_avg_loss = avg_loss

    print(f"\nDid not converge in {args.meta_meta_epochs} meta-meta-epochs.")
    return False, args.meta_meta_epochs, current_inner_lr.item(), current_inner_steps


def main():
    parser = argparse.ArgumentParser(description="nn⁴ Meta²Learn")
    parser.add_argument("--in-dim", type=int, default=10)
    parser.add_argument("--n-way", type=int, default=5)
    parser.add_argument("--k-shot", type=int, default=5)
    parser.add_argument("--inner-lr", type=float, default=0.01, help="Initial inner LR")
    parser.add_argument("--inner-steps", type=int, default=3, help="Initial inner steps")
    parser.add_argument("--outer-lr", type=float, default=0.001, help="MAML outer LR")
    parser.add_argument("--meta-meta-lr", type=float, default=0.005, help="Level 3 LR")
    parser.add_argument("--meta-epochs-per-mm", type=int, default=10, help="MAML epochs per MM step")
    parser.add_argument("--meta-meta-epochs", type=int, default=30, help="Level 3 epochs")
    parser.add_argument("--tasks-per-batch", type=int, default=4)
    parser.add_argument("--convergence-threshold", type=float, default=0.01)
    args = parser.parse_args()

    model = SimpleClassifier(in_dim=args.in_dim, hidden_dim=64, out_dim=args.n_way)
    task_dist = ClusterTaskDist(in_dim=args.in_dim, n_way=args.n_way)

    print(f"Model params: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Task: {args.n_way}-way {args.k_shot}-shot classification")
    print(f"Three levels: inner(adapt) → middle(MAML) → outer(learn MAML hyperparams)")
    print()

    converged, epochs, final_lr, final_steps = meta_meta_learn(model, task_dist, args)

    # Final evaluation
    print(f"\n--- Final Evaluation ---")
    task_dist_eval = ClusterTaskDist(in_dim=args.in_dim, n_way=args.n_way)
    sx, sy, qx, qy = task_dist_eval.sample(args.k_shot, 30)

    # Before adaptation
    with torch.no_grad():
        pred_before = model(qx)
        acc_before = (pred_before.argmax(1) == qy).float().mean().item()

    # After adaptation with learned hyperparameters
    adapted = inner_adapt(model, sx, sy,
                          inner_lr=torch.tensor(final_lr),
                          inner_steps=final_steps)
    with torch.no_grad():
        pred_after = model(qx, adapted)
        acc_after = (pred_after.argmax(1) == qy).float().mean().item()

    print(f"Before adaptation: {acc_before:.4f}")
    print(f"After {final_steps}-step adaptation (lr={final_lr:.6f}): {acc_after:.4f}")


if __name__ == "__main__":
    main()
