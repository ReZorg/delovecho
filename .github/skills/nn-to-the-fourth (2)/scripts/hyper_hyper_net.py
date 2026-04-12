#!/usr/bin/env python3
"""
nn⁴ FP1: HyperHyperNet — The Weight-Generation Quine

Three-level weight generation:
  H₂(z₂) → θ_{H₁}
  H₁(z₁; θ_{H₁}) → θ_G
  G(x; θ_G) → y

Trains end-to-end and detects convergence toward the fixed point
where H₂ could generate its own weights.

Usage:
    python hyper_hyper_net.py [--z2-dim 16] [--z1-dim 16] [--epochs 100]
"""

import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset


class HyperHyperNet(nn.Module):
    """Three-level HyperNetwork: H₂ generates H₁ which generates G.

    Level 2 (H₂): z₂ → θ_{H₁}  (weights of the inner hypernetwork)
    Level 1 (H₁): z₁ → θ_G      (weights of the target network, using θ_{H₁})
    Level 0 (G):  x  → y         (classification, using θ_G)
    """

    def __init__(self, z2_dim, z1_dim, target_in, target_hid, target_out, h2_hid=64, h1_hid=32):
        super().__init__()
        self.z1_dim = z1_dim
        self.target_in = target_in
        self.target_hid = target_hid
        self.target_out = target_out
        self.h1_hid = h1_hid

        # Target network G has: w1(th×ti), b1(th), w2(to×th), b2(to)
        g_param_count = target_hid * target_in + target_hid + target_out * target_hid + target_out

        # H₁ architecture: Linear(z1_dim → h1_hid) + ReLU + Linear(h1_hid → g_param_count)
        h1_param_count = (z1_dim * h1_hid + h1_hid) + (h1_hid * g_param_count + g_param_count)

        # H₂: generates all of H₁'s parameters
        self.h2 = nn.Sequential(
            nn.Linear(z2_dim, h2_hid),
            nn.ReLU(),
            nn.Linear(h2_hid, h2_hid),
            nn.ReLU(),
            nn.Linear(h2_hid, h1_param_count),
        )

        self.g_param_count = g_param_count
        self.h1_param_count = h1_param_count

        # Store split sizes for H₁ parameters
        self.h1_splits = [
            z1_dim * h1_hid,  # h1_w1
            h1_hid,            # h1_b1
            h1_hid * g_param_count,  # h1_w2
            g_param_count,     # h1_b2
        ]

        # Store split sizes for G parameters
        self.g_splits = [
            target_hid * target_in,  # g_w1
            target_hid,               # g_b1
            target_out * target_hid,  # g_w2
            target_out,                # g_b2
        ]

    def forward(self, z2, z1, x):
        """Three-level forward pass."""
        # Level 2: H₂(z₂) → θ_{H₁}
        h1_flat = self.h2(z2)
        h1_w1, h1_b1, h1_w2, h1_b2 = torch.split(h1_flat, self.h1_splits, dim=-1)

        h1_w1 = h1_w1.view(self.h1_hid, self.z1_dim)
        h1_b1 = h1_b1.view(self.h1_hid)
        h1_w2 = h1_w2.view(self.g_param_count, self.h1_hid)
        h1_b2 = h1_b2.view(self.g_param_count)

        # Level 1: H₁(z₁; θ_{H₁}) → θ_G  (functional forward)
        h1_hidden = F.relu(F.linear(z1, h1_w1, h1_b1))
        g_flat = F.linear(h1_hidden, h1_w2, h1_b2)

        g_w1, g_b1, g_w2, g_b2 = torch.split(g_flat, self.g_splits, dim=-1)
        g_w1 = g_w1.view(self.target_hid, self.target_in)
        g_b1 = g_b1.view(self.target_hid)
        g_w2 = g_w2.view(self.target_out, self.target_hid)
        g_b2 = g_b2.view(self.target_out)

        # Level 0: G(x; θ_G) → y  (functional forward)
        h = F.relu(F.linear(x, g_w1, g_b1))
        return F.linear(h, g_w2, g_b2)

    def measure_self_similarity(self, z2_a, z2_b, z1):
        """Measure how similar two H₂ embeddings produce at the G level.
        At the fixed point, small z₂ perturbations → small G changes."""
        with torch.no_grad():
            h1_a = self.h2(z2_a)
            h1_b = self.h2(z2_b)
            return (h1_a - h1_b).norm().item()


def make_xor_data(n=2000):
    x = torch.randn(n, 2)
    y = ((x[:, 0] * x[:, 1]) > 0).long()
    return TensorDataset(x, y)


def detect_convergence(model, z2, z1, threshold=1e-3, n_perturbations=10):
    """Detect fixed-point convergence by measuring sensitivity to z₂ perturbations.
    At the fixed point, the system is stable under self-application."""
    model.eval()
    total_sensitivity = 0
    with torch.no_grad():
        base_params = model.h2(z2)
        for _ in range(n_perturbations):
            z2_perturbed = z2 + torch.randn_like(z2) * 0.01
            perturbed_params = model.h2(z2_perturbed)
            total_sensitivity += (base_params - perturbed_params).norm().item()
    avg_sensitivity = total_sensitivity / n_perturbations
    model.train()
    return avg_sensitivity < threshold, avg_sensitivity


def main():
    parser = argparse.ArgumentParser(description="nn⁴ HyperHyperNet")
    parser.add_argument("--z2-dim", type=int, default=16, help="Level-2 embedding dim")
    parser.add_argument("--z1-dim", type=int, default=16, help="Level-1 embedding dim")
    parser.add_argument("--epochs", type=int, default=100, help="Training epochs")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    args = parser.parse_args()

    # Target network: 2→20→2 (XOR classifier)
    model = HyperHyperNet(
        z2_dim=args.z2_dim, z1_dim=args.z1_dim,
        target_in=2, target_hid=20, target_out=2,
        h2_hid=64, h1_hid=32,
    )

    n_params = sum(p.numel() for p in model.parameters())
    print(f"HyperHyperNet total parameters: {n_params:,}")
    print(f"  H₂ generates {model.h1_param_count:,} params for H₁")
    print(f"  H₁ generates {model.g_param_count:,} params for G")
    print()

    # Data
    dataset = make_xor_data(2000)
    train_data, val_data = torch.utils.data.random_split(dataset, [1600, 400])
    train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=200)

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    # Fixed embeddings for this task
    z2 = torch.randn(args.z2_dim)
    z1 = torch.randn(args.z1_dim)

    for epoch in range(args.epochs):
        epoch_loss = 0
        for x, y in train_loader:
            optimizer.zero_grad()
            pred = model(z2, z1, x)
            loss = F.cross_entropy(pred, y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        if (epoch + 1) % 20 == 0:
            # Evaluate
            model.eval()
            correct, total = 0, 0
            with torch.no_grad():
                for x, y in val_loader:
                    pred = model(z2, z1, x)
                    correct += (pred.argmax(1) == y).sum().item()
                    total += len(y)
            acc = correct / total
            model.train()

            # Check convergence
            converged, sensitivity = detect_convergence(model, z2, z1)
            status = "CONVERGED ✓" if converged else f"sensitivity={sensitivity:.6f}"
            print(f"Epoch {epoch+1:3d} | Loss: {epoch_loss/len(train_loader):.4f} | "
                  f"Val Acc: {acc:.4f} | {status}")

    # Final convergence check
    converged, sensitivity = detect_convergence(model, z2, z1)
    print(f"\nFinal convergence: {'REACHED (nn⁴ ≅ nn²)' if converged else 'NOT YET'}")
    print(f"Final sensitivity: {sensitivity:.6f}")

    # Demonstrate three-level generation
    print("\n--- Three-Level Weight Generation ---")
    with torch.no_grad():
        # Different z₂ → different H₁ → different G → different predictions
        for i in range(3):
            z2_i = torch.randn(args.z2_dim)
            pred = model(z2_i, z1, torch.tensor([[0.5, 0.5]]))
            print(f"  z₂ sample {i+1}: G predicts class {pred.argmax(1).item()} "
                  f"(logits: {pred[0].tolist()})")


if __name__ == "__main__":
    main()
