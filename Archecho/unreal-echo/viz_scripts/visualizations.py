#!/usr/bin/env python3
"""Generate visualizations for the Ontelecho skill demo."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Style ──
plt.rcParams.update({
    'figure.facecolor': '#0d1117',
    'axes.facecolor': '#161b22',
    'text.color': '#c9d1d9',
    'axes.labelcolor': '#c9d1d9',
    'xtick.color': '#8b949e',
    'ytick.color': '#8b949e',
    'axes.edgecolor': '#30363d',
    'grid.color': '#21262d',
    'font.family': 'monospace',
    'font.size': 11,
})

COLORS = {
    'cyan': '#58a6ff',
    'green': '#3fb950',
    'orange': '#d29922',
    'red': '#f85149',
    'purple': '#bc8cff',
    'pink': '#f778ba',
    'gray': '#8b949e',
    'white': '#c9d1d9',
}

# ═══════════════════════════════════════════════════════════════════
# 1. A000081 Growth — Rooted Tree Counts per System Level
# ═══════════════════════════════════════════════════════════════════
def fig1_a000081():
    levels = ['s0\nVoid', 's1\nSource', 's2\nPolarity', 's3\nStructure',
              's4\nExchange', 's5\nCreativity', 's6\nDynamics', 's7\nRhythm']
    counts = [1, 1, 2, 4, 9, 20, 48, 115]
    colors = ['#8b949e', '#8b949e', '#58a6ff', '#58a6ff',
              '#d29922', '#3fb950', '#bc8cff', '#f778ba']

    fig, ax = plt.subplots(figsize=(14, 6))
    bars = ax.bar(range(len(levels)), counts, color=colors, edgecolor='#30363d',
                  linewidth=1.2, width=0.7, zorder=3)
    for bar, c in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                str(c), ha='center', va='bottom', fontsize=13, fontweight='bold',
                color='#c9d1d9')
    ax.set_xticks(range(len(levels)))
    ax.set_xticklabels(levels, fontsize=10)
    ax.set_ylabel('Rooted Trees  a(N+1)', fontsize=12)
    ax.set_title('OEIS A000081 — Rooted Tree Counts per Autonomy Level',
                 fontsize=15, fontweight='bold', color='#58a6ff', pad=15)
    ax.set_ylim(0, 135)
    ax.grid(axis='y', alpha=0.3, zorder=0)

    # Annotate the "autogenesis gap"
    ax.annotate('', xy=(4, 9), xytext=(7, 115),
                arrowprops=dict(arrowstyle='<->', color='#f85149', lw=2))
    ax.text(5.5, 65, '106 trees\n(autogenesis gap)', ha='center',
            fontsize=11, color='#f85149', fontweight='bold')

    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/fig1_a000081.png', dpi=180)
    plt.close()
    print("  [OK] fig1_a000081.png")


# ═══════════════════════════════════════════════════════════════════
# 2. Topology Distribution across s0–s6
# ═══════════════════════════════════════════════════════════════════
def fig2_topology():
    # Counts from the triple enumeration
    topo_data = {
        's0': {'ROOT': 1, 'NEST': 0, 'BRANCH': 0, 'BRIDGE': 0},
        's1': {'ROOT': 0, 'NEST': 1, 'BRANCH': 0, 'BRIDGE': 0},
        's2': {'ROOT': 0, 'NEST': 1, 'BRANCH': 1, 'BRIDGE': 0},
        's3': {'ROOT': 0, 'NEST': 1, 'BRANCH': 1, 'BRIDGE': 2},
        's4': {'ROOT': 0, 'NEST': 1, 'BRANCH': 1, 'BRIDGE': 7},
        's5': {'ROOT': 0, 'NEST': 1, 'BRANCH': 1, 'BRIDGE': 18},
        's6': {'ROOT': 0, 'NEST': 1, 'BRANCH': 1, 'BRIDGE': 46},
    }
    levels = list(topo_data.keys())
    topos = ['ROOT', 'NEST', 'BRANCH', 'BRIDGE']
    topo_colors = {'ROOT': '#8b949e', 'NEST': '#58a6ff', 'BRANCH': '#3fb950', 'BRIDGE': '#d29922'}

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(levels))
    width = 0.18
    for i, topo in enumerate(topos):
        vals = [topo_data[l][topo] for l in levels]
        ax.bar(x + i*width - 1.5*width, vals, width, label=topo,
               color=topo_colors[topo], edgecolor='#30363d', linewidth=0.8, zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(levels, fontsize=11)
    ax.set_ylabel('Model Count', fontsize=12)
    ax.set_title('Topology Distribution: ROOT / NEST / BRANCH / BRIDGE',
                 fontsize=14, fontweight='bold', color='#58a6ff', pad=15)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.8,
              facecolor='#161b22', edgecolor='#30363d')
    ax.grid(axis='y', alpha=0.3, zorder=0)
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/fig2_topology.png', dpi=180)
    plt.close()
    print("  [OK] fig2_topology.png")


# ═══════════════════════════════════════════════════════════════════
# 3. Energy Flow Simulation (48 steps = 4 cycles)
# ═══════════════════════════════════════════════════════════════════
def fig3_energy():
    TWELVE_STEPS = [
        (1,  "Performance", "T9", "U"), (2,  "Performance", "T1", "E"),
        (3,  "Performance", "T8", "R"), (4,  "Performance", "T4", "E"),
        (5,  "Potential",   "T9", "U"), (6,  "Potential",   "T2", "E"),
        (7,  "Potential",   "T8", "R"), (8,  "Potential",   "T8", "E"),
        (9,  "Commitment",  "T9", "U"), (10, "Commitment",  "T5", "E"),
        (11, "Commitment",  "T8", "R"), (12, "Commitment",  "T7", "E"),
    ]
    energy = {"T9": 1.0, "T1": 0.5, "T2": 0.5, "T4": 0.5,
              "T5": 0.5, "T7": 0.5, "T8": 0.8}
    history = {k: [] for k in energy}
    n = 48
    for i in range(n):
        step_idx = i % 12
        _, dim, term, mode = TWELVE_STEPS[step_idx]
        if mode == "E":
            energy[term] = min(1.0, energy[term] + 0.05)
            energy["T9"] = max(0.1, energy["T9"] - 0.02)
        else:
            energy[term] = max(0.1, energy[term] - 0.03)
            energy["T9"] = min(1.0, energy["T9"] + 0.01)
        for k in history:
            history[k].append(energy[k])

    fig, ax = plt.subplots(figsize=(14, 6))
    term_colors = {
        'T9': '#f778ba', 'T1': '#58a6ff', 'T2': '#3fb950',
        'T4': '#d29922', 'T5': '#bc8cff', 'T7': '#f85149', 'T8': '#8b949e'
    }
    term_labels = {
        'T9': 'T9 CoreSelf', 'T1': 'T1 EchoBeats', 'T2': 'T2 autoresearch',
        'T4': 'T4 Memory', 'T5': 'T5 git commit', 'T7': 'T7 echo-garden',
        'T8': 'T8 Coherence'
    }
    for term in ['T9', 'T8', 'T1', 'T2', 'T4', 'T5', 'T7']:
        ax.plot(range(n), history[term], color=term_colors[term],
                label=term_labels[term], linewidth=1.8, alpha=0.9)

    # Mark cycle boundaries
    for c in [12, 24, 36]:
        ax.axvline(c, color='#30363d', linestyle='--', linewidth=1, alpha=0.6)
        ax.text(c, 1.02, f'Cycle {c//12+1}', ha='center', fontsize=8, color='#8b949e')

    # Shade dimensions
    for cycle in range(4):
        base = cycle * 12
        ax.axvspan(base, base+4, alpha=0.06, color='#58a6ff')     # Performance
        ax.axvspan(base+4, base+8, alpha=0.06, color='#3fb950')   # Potential
        ax.axvspan(base+8, base+12, alpha=0.06, color='#bc8cff')  # Commitment

    ax.set_xlabel('Step', fontsize=12)
    ax.set_ylabel('Energy Level', fontsize=12)
    ax.set_title('Ontelecho Energy Flow — 4 Creative Cycles (48 Steps)',
                 fontsize=14, fontweight='bold', color='#58a6ff', pad=15)
    ax.legend(loc='lower left', fontsize=9, ncol=4, framealpha=0.8,
              facecolor='#161b22', edgecolor='#30363d')
    ax.set_ylim(0, 1.1)
    ax.grid(alpha=0.2, zorder=0)
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/fig3_energy.png', dpi=180)
    plt.close()
    print("  [OK] fig3_energy.png")


# ═══════════════════════════════════════════════════════════════════
# 4. Experiment Log — Coherence vs Metric Delta
# ═══════════════════════════════════════════════════════════════════
def fig4_experiments():
    experiments = [
        ("Boundary detection", 0.15, 0.785, 'keep'),
        ("Gradient memory", 0.22, 0.792, 'keep'),
        ("Spectral radius", -0.08, 0.742, 'discard'),
        ("Interlock", 0.10, 0.770, 'keep'),
        ("Roughness sampling", 0.05, 0.775, 'keep'),
    ]

    fig, ax = plt.subplots(figsize=(10, 7))
    for name, delta, coh, status in experiments:
        color = '#3fb950' if status == 'keep' else '#f85149'
        marker = 'o' if status == 'keep' else 'X'
        ax.scatter(delta, coh, c=color, s=200, marker=marker, zorder=5,
                   edgecolors='#c9d1d9', linewidth=1.2)
        ax.annotate(name, (delta, coh), textcoords="offset points",
                    xytext=(10, 8), fontsize=10, color='#c9d1d9')

    # Safety zone
    ax.axhline(0.60, color='#f85149', linestyle='--', linewidth=1.5, alpha=0.6)
    ax.axvline(0.0, color='#f85149', linestyle='--', linewidth=1.5, alpha=0.6)
    ax.fill_between([-0.15, 0.0], 0.5, 0.6, alpha=0.08, color='#f85149')
    ax.fill_between([0.0, 0.30], 0.6, 0.85, alpha=0.08, color='#3fb950')
    ax.text(0.15, 0.62, 'KEEP zone', fontsize=11, color='#3fb950', fontweight='bold')
    ax.text(-0.10, 0.52, 'DISCARD', fontsize=11, color='#f85149', fontweight='bold')

    keep_patch = mpatches.Patch(color='#3fb950', label='Keep')
    disc_patch = mpatches.Patch(color='#f85149', label='Discard')
    ax.legend(handles=[keep_patch, disc_patch], loc='upper left', fontsize=10,
              framealpha=0.8, facecolor='#161b22', edgecolor='#30363d')

    ax.set_xlabel('Metric Delta', fontsize=12)
    ax.set_ylabel('Coherence Score', fontsize=12)
    ax.set_title('Autogenesis Experiment Log — Coherence vs. Metric Delta',
                 fontsize=14, fontweight='bold', color='#58a6ff', pad=15)
    ax.set_xlim(-0.15, 0.30)
    ax.set_ylim(0.50, 0.85)
    ax.grid(alpha=0.2, zorder=0)
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/fig4_experiments.png', dpi=180)
    plt.close()
    print("  [OK] fig4_experiments.png")


# ═══════════════════════════════════════════════════════════════════
# 5. Symmetry Compression Ratio
# ═══════════════════════════════════════════════════════════════════
def fig5_compression():
    levels = ['L3.5\nExchange', 'L4\nCreativity', 'L4.5\nDynamics', 'L5\nRhythm']
    realized = [9, 20, 48, 115]
    catalan = [5, 14, 42, 132]
    ratios = [r/c for r, c in zip(realized, catalan)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: bar comparison
    x = np.arange(len(levels))
    w = 0.35
    ax1.bar(x - w/2, realized, w, label='Realized (A000081)', color='#58a6ff',
            edgecolor='#30363d', zorder=3)
    ax1.bar(x + w/2, catalan, w, label='Catalan Fold C(n-1)', color='#d29922',
            edgecolor='#30363d', zorder=3)
    ax1.set_xticks(x)
    ax1.set_xticklabels(levels, fontsize=10)
    ax1.set_ylabel('Count', fontsize=12)
    ax1.set_title('Realized Trees vs. Catalan Fold Space',
                  fontsize=13, fontweight='bold', color='#58a6ff', pad=10)
    ax1.legend(fontsize=10, framealpha=0.8, facecolor='#161b22', edgecolor='#30363d')
    ax1.grid(axis='y', alpha=0.3, zorder=0)

    # Right: compression ratio line
    ax2.plot(range(len(levels)), ratios, 'o-', color='#f778ba', linewidth=2.5,
             markersize=12, markeredgecolor='#c9d1d9', markeredgewidth=1.5, zorder=3)
    for i, r in enumerate(ratios):
        ax2.text(i, r + 0.08, f'{r:.2f}x', ha='center', fontsize=12,
                 fontweight='bold', color='#f778ba')
    ax2.set_xticks(range(len(levels)))
    ax2.set_xticklabels(levels, fontsize=10)
    ax2.set_ylabel('Compression Ratio', fontsize=12)
    ax2.set_title('Symmetry Compression Ratio (Autogenesis Pressure)',
                  fontsize=13, fontweight='bold', color='#f778ba', pad=10)
    ax2.set_ylim(0.5, 3.5)
    ax2.grid(alpha=0.3, zorder=0)

    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/fig5_compression.png', dpi=180)
    plt.close()
    print("  [OK] fig5_compression.png")


# ═══════════════════════════════════════════════════════════════════
# 6. The 12-Step Cycle Wheel
# ═══════════════════════════════════════════════════════════════════
def fig6_cycle_wheel():
    steps = [
        ("T9 (U)\nDirection", "Performance"),
        ("T1 (E)\nSense Need", "Performance"),
        ("T8 (R)\nBudget", "Performance"),
        ("T4 (E)\nRetrieve", "Performance"),
        ("T9 (U)\nReview", "Potential"),
        ("T2 (E)\nHypothesis", "Potential"),
        ("T8 (R)\nAllocate", "Potential"),
        ("T8 (E)\nBalance", "Potential"),
        ("T9 (U)\nCommit", "Commitment"),
        ("T5 (E)\ngit commit", "Commitment"),
        ("T8 (R)\nTrack", "Commitment"),
        ("T7 (E)\nEncode", "Commitment"),
    ]
    dim_colors = {'Performance': '#58a6ff', 'Potential': '#3fb950', 'Commitment': '#bc8cff'}

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
    ax.set_facecolor('#0d1117')
    fig.patch.set_facecolor('#0d1117')

    n = len(steps)
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    # Rotate so step 1 is at top
    angles = angles - np.pi/2

    for i, (label, dim) in enumerate(steps):
        color = dim_colors[dim]
        # Wedge
        theta1 = angles[i] - np.pi/n
        theta2 = angles[i] + np.pi/n
        ax.bar(angles[i], 1, width=2*np.pi/n, bottom=0.3, color=color,
               alpha=0.25, edgecolor=color, linewidth=1.5)
        # Label
        ax.text(angles[i], 1.55, label, ha='center', va='center',
                fontsize=8, color=color, fontweight='bold')
        # Step number
        ax.text(angles[i], 0.65, str(i+1), ha='center', va='center',
                fontsize=14, color='#c9d1d9', fontweight='bold')

    # Center label
    ax.text(0, 0, 'Ontelecho\n12-Step\nCycle', ha='center', va='center',
            fontsize=12, color='#c9d1d9', fontweight='bold',
            transform=ax.transData)

    ax.set_ylim(0, 2)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines['polar'].set_visible(False)

    # Legend
    patches = [mpatches.Patch(color=c, label=d, alpha=0.6) for d, c in dim_colors.items()]
    ax.legend(handles=patches, loc='lower right', fontsize=10,
              bbox_to_anchor=(1.15, -0.05), framealpha=0.8,
              facecolor='#161b22', edgecolor='#30363d')

    ax.set_title('The 12-Step Creative Cycle', fontsize=16, fontweight='bold',
                 color='#58a6ff', pad=30, y=1.05)
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/fig6_cycle_wheel.png', dpi=180)
    plt.close()
    print("  [OK] fig6_cycle_wheel.png")


# ═══════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import os
    os.makedirs('/home/ubuntu/demo', exist_ok=True)
    print("Generating Ontelecho demo visualizations...")
    fig1_a000081()
    fig2_topology()
    fig3_energy()
    fig4_experiments()
    fig5_compression()
    fig6_cycle_wheel()
    print("Done — 6 figures saved to /home/ubuntu/demo/")
