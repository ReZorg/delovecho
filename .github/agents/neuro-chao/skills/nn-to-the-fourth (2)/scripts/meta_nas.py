#!/usr/bin/env python3
"""
nn⁴ FP2: MetaNAS — Search that Searches for Search

Two-level architecture search:
  Outer level: search over NAS configurations (search_lr, regularization, op_set)
  Inner level: run DARTS with each configuration

The fixed point is the NAS configuration that would discover itself.

Usage:
    python meta_nas.py [--n-configs 4] [--inner-epochs 15] [--outer-epochs 20]
"""

import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import OrderedDict


# --- Inner-Level: Simplified DARTS Search ---

class SimpleDARTS(nn.Module):
    """A minimal DARTS cell for inner-level search."""

    def __init__(self, C, n_ops, n_edges):
        super().__init__()
        self.n_ops = n_ops
        self.n_edges = n_edges
        self.C = C

        # Operations: identity, conv3x3, conv5x5, avgpool
        self.ops = nn.ModuleList()
        for _ in range(n_edges):
            edge_ops = nn.ModuleList([
                nn.Identity(),
                nn.Sequential(nn.Conv2d(C, C, 3, padding=1, bias=False), nn.BatchNorm2d(C), nn.ReLU()),
                nn.Sequential(nn.Conv2d(C, C, 5, padding=2, bias=False), nn.BatchNorm2d(C), nn.ReLU()),
                nn.Sequential(nn.AvgPool2d(3, stride=1, padding=1), nn.BatchNorm2d(C)),
            ])
            self.ops.append(edge_ops)

        # Architecture parameters
        self.alphas = nn.Parameter(torch.randn(n_edges, n_ops) * 0.01)

    def forward(self, x):
        out = 0
        for i in range(self.n_edges):
            weights = F.softmax(self.alphas[i], dim=0)
            edge_out = sum(w * op(x) for w, op in zip(weights, self.ops[i]))
            out = out + edge_out
        return out

    def derive(self):
        """Derive discrete architecture."""
        op_names = ["identity", "conv3x3", "conv5x5", "avgpool"]
        arch = []
        for i in range(self.n_edges):
            best = self.alphas[i].argmax().item()
            arch.append(op_names[best])
        return arch


class InnerSearchNetwork(nn.Module):
    """Complete network for inner DARTS search."""

    def __init__(self, C=8, n_ops=4, n_edges=4, n_classes=4, in_channels=3, img_size=8):
        super().__init__()
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, C, 3, padding=1, bias=False),
            nn.BatchNorm2d(C),
        )
        self.cell = SimpleDARTS(C, n_ops, n_edges)
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(C, n_classes),
        )

    def forward(self, x):
        s = self.stem(x)
        h = self.cell(s)
        return self.classifier(h)

    def arch_parameters(self):
        return [self.cell.alphas]

    def weight_parameters(self):
        arch_ids = {id(p) for p in self.arch_parameters()}
        return [p for p in self.parameters() if id(p) not in arch_ids]


def run_inner_search(config, train_x, train_y, val_x, val_y, inner_epochs, C=8, n_ops=4, n_edges=4):
    """Run one inner DARTS search with given configuration.
    Returns validation loss as the quality metric."""
    search_lr = config[0].item()
    arch_lr = config[1].item()
    weight_decay = config[2].abs().item()

    model = InnerSearchNetwork(C=C, n_ops=n_ops, n_edges=n_edges,
                                n_classes=4, in_channels=3, img_size=8)

    w_opt = torch.optim.SGD(model.weight_parameters(), lr=max(search_lr, 1e-4),
                             weight_decay=max(weight_decay, 1e-6))
    a_opt = torch.optim.Adam(model.arch_parameters(), lr=max(arch_lr, 1e-5))

    bs = 32
    for epoch in range(inner_epochs):
        # Architecture step (validation)
        idx_v = torch.randperm(len(val_x))[:bs]
        a_opt.zero_grad()
        v_pred = model(val_x[idx_v])
        v_loss = F.cross_entropy(v_pred, val_y[idx_v])
        v_loss.backward()
        a_opt.step()

        # Weight step (training)
        idx_t = torch.randperm(len(train_x))[:bs]
        w_opt.zero_grad()
        t_pred = model(train_x[idx_t])
        t_loss = F.cross_entropy(t_pred, train_y[idx_t])
        t_loss.backward()
        w_opt.step()

    # Final validation loss
    with torch.no_grad():
        final_pred = model(val_x)
        final_loss = F.cross_entropy(final_pred, val_y)

    return final_loss, model.cell.derive()


# --- Outer-Level: MetaNAS ---

class MetaNAS(nn.Module):
    """Outer-level search over NAS configurations.

    Each configuration specifies: [search_lr, arch_lr, weight_decay]
    The outer level learns which configuration produces the best inner search.
    """

    def __init__(self, n_configs=4):
        super().__init__()
        self.n_configs = n_configs
        # Learnable NAS configurations
        self.configs = nn.ParameterList([
            nn.Parameter(torch.tensor([0.025, 3e-4, 3e-4]) + torch.randn(3) * 0.01)
            for _ in range(n_configs)
        ])
        # Weights over configurations (which config to prefer)
        self.config_weights = nn.Parameter(torch.zeros(n_configs))

    def get_weighted_config(self):
        """Get the weighted combination of configurations."""
        weights = F.softmax(self.config_weights, dim=0)
        combined = sum(w * cfg for w, cfg in zip(weights, self.configs))
        return combined

    def get_best_config(self):
        """Get the single best configuration."""
        best_idx = self.config_weights.argmax().item()
        return self.configs[best_idx], best_idx


def main():
    parser = argparse.ArgumentParser(description="nn⁴ MetaNAS")
    parser.add_argument("--n-configs", type=int, default=4, help="Number of NAS configs")
    parser.add_argument("--inner-epochs", type=int, default=10, help="Inner search epochs")
    parser.add_argument("--outer-epochs", type=int, default=15, help="Outer search epochs")
    parser.add_argument("--outer-lr", type=float, default=0.01, help="Outer learning rate")
    args = parser.parse_args()

    # Synthetic data
    n_train, n_val = 128, 64
    img_size, in_channels, n_classes = 8, 3, 4
    train_x = torch.randn(n_train, in_channels, img_size, img_size)
    train_y = torch.randint(0, n_classes, (n_train,))
    val_x = torch.randn(n_val, in_channels, img_size, img_size)
    val_y = torch.randint(0, n_classes, (n_val,))

    # Build MetaNAS
    meta_nas = MetaNAS(n_configs=args.n_configs)
    outer_opt = torch.optim.Adam(meta_nas.parameters(), lr=args.outer_lr)

    print(f"MetaNAS: {args.n_configs} candidate NAS configurations")
    print(f"Inner search: {args.inner_epochs} epochs each")
    print(f"Outer search: {args.outer_epochs} epochs")
    print()

    prev_best_loss = float('inf')
    for outer_epoch in range(args.outer_epochs):
        outer_opt.zero_grad()

        # Evaluate each configuration via inner search
        config_losses = []
        config_archs = []
        for i in range(args.n_configs):
            cfg = meta_nas.configs[i]
            loss, arch = run_inner_search(
                cfg, train_x, train_y, val_x, val_y,
                inner_epochs=args.inner_epochs,
            )
            config_losses.append(loss)
            config_archs.append(arch)

        # Weighted loss across configurations
        weights = F.softmax(meta_nas.config_weights, dim=0)
        total_loss = sum(w * l for w, l in zip(weights, config_losses))

        # Outer update
        total_loss.backward()
        outer_opt.step()

        best_idx = meta_nas.config_weights.argmax().item()
        best_loss = config_losses[best_idx].item()

        # Fixed-point detection
        delta = abs(best_loss - prev_best_loss)
        converged = delta < 1e-3 and outer_epoch > 3
        status = "CONVERGED ✓" if converged else f"Δ={delta:.4f}"
        prev_best_loss = best_loss

        if (outer_epoch + 1) % 3 == 0 or converged:
            print(f"Outer Epoch {outer_epoch+1:2d} | Best Config: {best_idx} | "
                  f"Loss: {best_loss:.4f} | {status}")
            if converged:
                break

    # Report final results
    best_cfg, best_idx = meta_nas.get_best_config()
    print(f"\n--- MetaNAS Results ---")
    print(f"Best configuration #{best_idx}:")
    print(f"  search_lr:    {best_cfg[0].item():.6f}")
    print(f"  arch_lr:      {best_cfg[1].item():.6f}")
    print(f"  weight_decay: {best_cfg[2].abs().item():.6f}")
    print(f"  Architecture: {config_archs[best_idx]}")

    print(f"\nAll configuration weights: {F.softmax(meta_nas.config_weights, dim=0).tolist()}")


if __name__ == "__main__":
    main()
