#!/usr/bin/env python3
"""
triad_viz.py — Visualizations for the Three-Phase Phase-Locked Phasor Engine
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np
import math
import json

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

C = {
    'cyan': '#58a6ff', 'green': '#3fb950', 'orange': '#d29922',
    'red': '#f85149', 'purple': '#bc8cff', 'pink': '#f778ba',
    'gray': '#8b949e', 'white': '#c9d1d9', 'bg': '#0d1117',
    'card': '#161b22', 'border': '#30363d',
}

THREAD_COLORS = {'A': '#58a6ff', 'B': '#3fb950', 'C': '#f778ba'}
MODE_COLORS = {'E': '#3fb950', 'R': '#bc8cff'}

# ═══════════════════════════════════════════════════════════════════
# Data from the engine
# ═══════════════════════════════════════════════════════════════════

# Exact sequences from the validated engine output
SET_A_TERMS = [4, 2, 8, 5, 7, 1, 4, 2, 8, 5, 7, 1]
SET_B_TERMS = [8, 5, 7, 1, 4, 2, 8, 5, 7, 1, 4, 2]
SET_C_TERMS = [7, 1, 4, 2, 8, 5, 7, 1, 4, 2, 8, 5]

SET_A_MODES = ['R','R','E','E','E','E','E','E','E','R','R','R']
SET_B_MODES = ['E','R','R','R','R','R','E','E','E','E','E','E']
SET_C_MODES = ['E','E','E','E','E','R','R','R','R','R','E','E']


# ═══════════════════════════════════════════════════════════════════
# Fig 1: The Phasor Diagram (animated snapshot at multiple steps)
# ═══════════════════════════════════════════════════════════════════
def fig1_phasor_diagram():
    fig, axes = plt.subplots(2, 3, figsize=(18, 12),
                             subplot_kw={'projection': 'polar'})
    fig.suptitle('Three-Phase Phasor Diagram — 120° Phase-Locked',
                 fontsize=18, fontweight='bold', color=C['cyan'], y=0.98)

    for idx, step in enumerate([0, 2, 4, 6, 8, 10]):
        ax = axes[idx // 3][idx % 3]
        ax.set_facecolor('#0d1117')

        # Draw unit circle
        theta = np.linspace(0, 2*np.pi, 100)
        ax.plot(theta, np.ones_like(theta), color=C['border'], linewidth=0.5, alpha=0.5)

        for thread, color in THREAD_COLORS.items():
            offsets = {'A': 0, 'B': 120, 'C': 240}
            angle_deg = (step / 12.0) * 360.0 + offsets[thread]
            angle_rad = math.radians(angle_deg)

            # Get mode for this thread at this step
            if thread == 'A':
                mode = SET_A_MODES[step]
                term = SET_A_TERMS[step]
            elif thread == 'B':
                mode = SET_B_MODES[step]
                term = SET_B_TERMS[step]
            else:
                mode = SET_C_MODES[step]
                term = SET_C_TERMS[step]

            mag = 0.9 if mode == 'E' else 0.6
            style = '-' if mode == 'E' else '--'

            # Draw phasor arrow
            ax.annotate('', xy=(angle_rad, mag), xytext=(0, 0),
                        arrowprops=dict(arrowstyle='->', color=color,
                                        lw=2.5, linestyle=style))

            # Label at tip
            label_r = mag + 0.15
            ax.text(angle_rad, label_r, f'{thread}:{term}{mode}',
                    ha='center', va='center', fontsize=8, fontweight='bold',
                    color=color)

        ax.set_title(f'Step {step+1}', fontsize=12, color=C['white'], pad=10)
        ax.set_ylim(0, 1.3)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.spines['polar'].set_visible(False)

    # Legend
    patches = [mpatches.Patch(color=c, label=f'Set {t}') for t, c in THREAD_COLORS.items()]
    patches.append(mpatches.Patch(color=C['green'], label='E (Expressive/Forward)'))
    patches.append(mpatches.Patch(color=C['purple'], label='R (Regenerative/Backward)'))
    fig.legend(handles=patches, loc='lower center', ncol=5, fontsize=11,
               framealpha=0.8, facecolor=C['card'], edgecolor=C['border'])

    plt.tight_layout(rect=[0, 0.06, 1, 0.95])
    fig.savefig('/home/ubuntu/demo/triad_fig1_phasors.png', dpi=180)
    plt.close()
    print("  [OK] triad_fig1_phasors.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 2: The Step Table Heatmap
# ═══════════════════════════════════════════════════════════════════
def fig2_step_heatmap():
    fig, ax = plt.subplots(figsize=(16, 8))

    # Build the grid: 3 rows (A, B, C) x 12 columns (steps)
    all_terms = [SET_A_TERMS, SET_B_TERMS, SET_C_TERMS]
    all_modes = [SET_A_MODES, SET_B_MODES, SET_C_MODES]
    thread_names = ['Set A', 'Set B', 'Set C']

    # Color-code by mode
    for row, (terms, modes, name) in enumerate(zip(all_terms, all_modes, thread_names)):
        for col, (term, mode) in enumerate(zip(terms, modes)):
            color = MODE_COLORS[mode]
            alpha = 0.7 if mode == 'E' else 0.4
            rect = plt.Rectangle((col, 2-row), 1, 1, facecolor=color,
                                 alpha=alpha, edgecolor=C['border'], linewidth=1.5)
            ax.add_patch(rect)
            # Term number
            ax.text(col + 0.5, 2-row + 0.55, f'T{term}', ha='center', va='center',
                    fontsize=13, fontweight='bold', color=C['white'])
            # Mode letter
            ax.text(col + 0.5, 2-row + 0.25, mode, ha='center', va='center',
                    fontsize=10, color=C['white'], alpha=0.8)

    # Highlight the alternating interface pattern
    for col in range(12):
        if col % 2 == 0:
            interface = '{4,7,8}'
        else:
            interface = '{1,2,5}'
        ax.text(col + 0.5, -0.3, interface, ha='center', va='center',
                fontsize=9, color=C['orange'], fontweight='bold')

    ax.set_xlim(0, 12)
    ax.set_ylim(-0.7, 3.3)
    ax.set_xticks([i + 0.5 for i in range(12)])
    ax.set_xticklabels([f'Step {i+1}' for i in range(12)], fontsize=10)
    ax.set_yticks([0.5, 1.5, 2.5])
    ax.set_yticklabels(['Set C', 'Set B', 'Set A'], fontsize=12, fontweight='bold')
    ax.set_title('Triad Step Table — Term + Mode per Thread per Step',
                 fontsize=15, fontweight='bold', color=C['cyan'], pad=15)

    # Interface label
    ax.text(6, -0.6, 'Active Polar Pair Interfaces (alternating)',
            ha='center', fontsize=11, color=C['orange'])

    # Legend
    e_patch = mpatches.Patch(color=MODE_COLORS['E'], alpha=0.7,
                             label='E: Expressive (Forward Pass)')
    r_patch = mpatches.Patch(color=MODE_COLORS['R'], alpha=0.4,
                             label='R: Regenerative (Backward Pass)')
    ax.legend(handles=[e_patch, r_patch], loc='upper right', fontsize=11,
              framealpha=0.8, facecolor=C['card'], edgecolor=C['border'])

    ax.set_aspect('equal')
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/triad_fig2_heatmap.png', dpi=180)
    plt.close()
    print("  [OK] triad_fig2_heatmap.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 3: Mode Waveforms (E/R as sinusoidal phasors)
# ═══════════════════════════════════════════════════════════════════
def fig3_waveforms():
    fig, axes = plt.subplots(4, 1, figsize=(16, 12), sharex=True)
    fig.suptitle('Three-Phase Mode Waveforms — 120° Phase-Locked',
                 fontsize=16, fontweight='bold', color=C['cyan'], y=0.98)

    steps = np.arange(12)
    # Convert modes to numeric: E=+1, R=-1
    def mode_to_val(modes):
        return [1.0 if m == 'E' else -1.0 for m in modes]

    all_modes_list = [
        ('Set A', SET_A_MODES, THREAD_COLORS['A']),
        ('Set B', SET_B_MODES, THREAD_COLORS['B']),
        ('Set C', SET_C_MODES, THREAD_COLORS['C']),
    ]

    # Individual waveforms
    for idx, (name, modes, color) in enumerate(all_modes_list):
        ax = axes[idx]
        vals = mode_to_val(modes)
        ax.step(steps, vals, where='mid', color=color, linewidth=2.5, label=name)
        ax.fill_between(steps, vals, step='mid', alpha=0.15, color=color)

        # Mark E and R regions
        for s, v in zip(steps, vals):
            marker = '→' if v > 0 else '←'
            ax.text(s, v * 0.5, marker, ha='center', va='center',
                    fontsize=14, color=color, fontweight='bold')

        ax.set_ylabel(name, fontsize=12, fontweight='bold', color=color)
        ax.set_ylim(-1.5, 1.5)
        ax.axhline(0, color=C['border'], linewidth=0.8)
        ax.set_yticks([-1, 0, 1])
        ax.set_yticklabels(['R', '0', 'E'], fontsize=10)
        ax.grid(axis='x', alpha=0.2)

    # Combined: sum of all three
    ax = axes[3]
    a_vals = mode_to_val(SET_A_MODES)
    b_vals = mode_to_val(SET_B_MODES)
    c_vals = mode_to_val(SET_C_MODES)
    combined = [a + b + c for a, b, c in zip(a_vals, b_vals, c_vals)]

    ax.bar(steps, combined, color=[C['green'] if v > 0 else C['purple'] for v in combined],
           alpha=0.7, edgecolor=C['border'], linewidth=1)
    for s, v in zip(steps, combined):
        label = f'{int(abs(v))}{"E" if v > 0 else "R"}' if v != 0 else '0'
        if v > 0:
            label = f'+{int(v)}'
        else:
            label = f'{int(v)}'
        ax.text(s, v + (0.2 if v >= 0 else -0.3), label, ha='center',
                fontsize=10, fontweight='bold', color=C['white'])

    ax.set_ylabel('Net E-R', fontsize=12, fontweight='bold', color=C['white'])
    ax.set_xlabel('Step', fontsize=12)
    ax.set_ylim(-3.5, 3.5)
    ax.axhline(0, color=C['border'], linewidth=0.8)
    ax.set_xticks(steps)
    ax.set_xticklabels([str(s+1) for s in steps], fontsize=10)
    ax.grid(axis='x', alpha=0.2)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig('/home/ubuntu/demo/triad_fig3_waveforms.png', dpi=180)
    plt.close()
    print("  [OK] triad_fig3_waveforms.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 4: Polar Pair Interface Activity
# ═══════════════════════════════════════════════════════════════════
def fig4_interfaces():
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Polar Pair Interfaces — Forward (E) vs Backward (R) Activations',
                 fontsize=15, fontweight='bold', color=C['cyan'], y=1.02)

    pairs = [
        ('P1: [1(8)]', 'Perception ↔ Coherence',
         [1, 8], SET_A_TERMS, SET_B_TERMS, SET_C_TERMS,
         SET_A_MODES, SET_B_MODES, SET_C_MODES),
        ('P2: [4(5)]', 'Input ↔ Action',
         [4, 5], SET_A_TERMS, SET_B_TERMS, SET_C_TERMS,
         SET_A_MODES, SET_B_MODES, SET_C_MODES),
        ('P3: [7(2)]', 'Memory ↔ Idea',
         [7, 2], SET_A_TERMS, SET_B_TERMS, SET_C_TERMS,
         SET_A_MODES, SET_B_MODES, SET_C_MODES),
    ]

    for idx, (pair_name, pair_desc, pair_terms, at, bt, ct, am, bm, cm) in enumerate(pairs):
        ax = axes[idx]

        # Collect activations per step
        fwd_steps = []
        bwd_steps = []
        for step in range(12):
            for terms, modes, thread in [(at, am, 'A'), (bt, bm, 'B'), (ct, cm, 'C')]:
                if terms[step] in pair_terms:
                    if modes[step] == 'E':
                        fwd_steps.append(step)
                    else:
                        bwd_steps.append(step)

        # Plot as timeline
        steps = np.arange(12)
        fwd_mask = np.zeros(12)
        bwd_mask = np.zeros(12)
        for s in fwd_steps:
            fwd_mask[s] = 1
        for s in bwd_steps:
            bwd_mask[s] = -1

        ax.bar(steps, fwd_mask, color=C['green'], alpha=0.7, label='E (Forward)',
               edgecolor=C['border'])
        ax.bar(steps, bwd_mask, color=C['purple'], alpha=0.7, label='R (Backward)',
               edgecolor=C['border'])

        ax.set_title(f'{pair_name}\n{pair_desc}', fontsize=12, fontweight='bold',
                     color=C['orange'])
        ax.set_xlabel('Step', fontsize=10)
        ax.set_xticks(steps)
        ax.set_xticklabels([str(s+1) for s in steps], fontsize=9)
        ax.set_ylim(-1.5, 1.5)
        ax.set_yticks([-1, 0, 1])
        ax.set_yticklabels(['R', '-', 'E'], fontsize=10)
        ax.axhline(0, color=C['border'], linewidth=0.8)
        ax.grid(axis='x', alpha=0.2)
        if idx == 0:
            ax.legend(fontsize=9, framealpha=0.8, facecolor=C['card'],
                      edgecolor=C['border'])

    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/triad_fig4_interfaces.png', dpi=180)
    plt.close()
    print("  [OK] triad_fig4_interfaces.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 5: The Simultaneity Hexagram
# ═══════════════════════════════════════════════════════════════════
def fig5_hexagram():
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_facecolor('#0d1117')
    fig.patch.set_facecolor('#0d1117')

    # 6 terms arranged in a hexagon
    terms = [4, 8, 7, 2, 5, 1]  # alternating structure/process
    term_labels = ['T4\nInput\n[s]', 'T8\nCoherence\n(p)', 'T7\nMemory\n[s]',
                   'T2\nIdea\n(p)', 'T5\nAction\n(p)', 'T1\nPerception\n[s]']
    term_colors = [C['cyan'], C['orange'], C['cyan'],
                   C['orange'], C['orange'], C['cyan']]

    angles = np.linspace(np.pi/2, np.pi/2 - 2*np.pi, 6, endpoint=False)
    radius = 3.5
    positions = {}

    for i, (term, label, color, angle) in enumerate(zip(terms, term_labels, term_colors, angles)):
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        positions[term] = (x, y)

        # Node circle
        circle = plt.Circle((x, y), 0.55, facecolor=color, alpha=0.3,
                             edgecolor=color, linewidth=2)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=9,
                fontweight='bold', color=color)

    # Draw polar pair connections (diameters)
    pair_data = [(1, 8, C['red']), (4, 5, C['green']), (7, 2, C['purple'])]
    pair_labels = ['P1: [1(8)]', 'P2: [4(5)]', 'P3: [7(2)]']

    for (t1, t2, color), label in zip(pair_data, pair_labels):
        x1, y1 = positions[t1]
        x2, y2 = positions[t2]
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=2.5,
                linestyle='--', alpha=0.6)
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.3, my + 0.3, label, fontsize=10, color=color,
                fontweight='bold', alpha=0.8)

    # Draw the two alternating triangles
    # Odd steps: {4, 8, 7} — structure-heavy
    tri1 = [positions[4], positions[8], positions[7], positions[4]]
    tri1_x = [p[0] for p in tri1]
    tri1_y = [p[1] for p in tri1]
    ax.plot(tri1_x, tri1_y, color=C['cyan'], linewidth=2, alpha=0.5)
    ax.fill(tri1_x, tri1_y, color=C['cyan'], alpha=0.05)

    # Even steps: {2, 5, 1} — process-heavy
    tri2 = [positions[2], positions[5], positions[1], positions[2]]
    tri2_x = [p[0] for p in tri2]
    tri2_y = [p[1] for p in tri2]
    ax.plot(tri2_x, tri2_y, color=C['orange'], linewidth=2, alpha=0.5)
    ax.fill(tri2_x, tri2_y, color=C['orange'], alpha=0.05)

    # Center label
    ax.text(0, 0, 'SIMULTANEITY\n\nAll 3 polar pairs\nactive at every step\n\n'
            'E + R co-occur\nacross shared\ninterfaces',
            ha='center', va='center', fontsize=11, color=C['white'],
            fontweight='bold', style='italic',
            bbox=dict(boxstyle='round,pad=0.8', facecolor=C['card'],
                      edgecolor=C['border'], alpha=0.9))

    # Annotations
    ax.text(0, -4.8, 'Odd steps: {4,8,7} triangle (cyan)    |    '
            'Even steps: {1,2,5} triangle (orange)',
            ha='center', fontsize=11, color=C['gray'])
    ax.text(0, -5.3, 'The hexagram alternates between two interlocking triangles — '
            'the Star of David topology',
            ha='center', fontsize=10, color=C['gray'], style='italic')

    ax.set_xlim(-5.5, 5.5)
    ax.set_ylim(-6, 5.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Simultaneity Hexagram — Polar Pairs as Interlocking Triangles',
                 fontsize=16, fontweight='bold', color=C['cyan'], pad=20)

    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/triad_fig5_hexagram.png', dpi=180)
    plt.close()
    print("  [OK] triad_fig5_hexagram.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 6: The Three-Phase AC Motor Analogy
# ═══════════════════════════════════════════════════════════════════
def fig6_ac_motor():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

    # Left: sinusoidal waveforms
    t = np.linspace(0, 2*np.pi, 200)
    for thread, color, offset in [('A', THREAD_COLORS['A'], 0),
                                   ('B', THREAD_COLORS['B'], 2*np.pi/3),
                                   ('C', THREAD_COLORS['C'], 4*np.pi/3)]:
        wave = np.sin(t + offset)
        ax1.plot(t, wave, color=color, linewidth=2.5, label=f'Set {thread}')

    # Mark the 12 step positions
    step_angles = np.linspace(0, 2*np.pi, 12, endpoint=False)
    for i, sa in enumerate(step_angles):
        ax1.axvline(sa, color=C['border'], linewidth=0.5, alpha=0.3)
        ax1.text(sa, 1.15, str(i+1), ha='center', fontsize=8, color=C['gray'])

    ax1.set_xlabel('Phase Angle (radians)', fontsize=12)
    ax1.set_ylabel('Amplitude (E=+1, R=-1)', fontsize=12)
    ax1.set_title('Three-Phase Sinusoidal Waveforms\n(120° Phase-Locked)',
                  fontsize=13, fontweight='bold', color=C['cyan'])
    ax1.legend(fontsize=11, framealpha=0.8, facecolor=C['card'],
               edgecolor=C['border'])
    ax1.set_ylim(-1.4, 1.4)
    ax1.axhline(0, color=C['border'], linewidth=0.8)
    ax1.grid(alpha=0.2)

    # Right: rotating magnetic field (phasor sum at each step)
    ax2.set_facecolor('#0d1117')
    for step in range(12):
        # Compute phasor sum
        phasors = []
        for thread, offset in [('A', 0), ('B', 2*np.pi/3), ('C', 4*np.pi/3)]:
            angle = (step / 12.0) * 2 * np.pi + offset
            # Mode determines sign
            if thread == 'A':
                mode = SET_A_MODES[step]
            elif thread == 'B':
                mode = SET_B_MODES[step]
            else:
                mode = SET_C_MODES[step]
            mag = 1.0 if mode == 'E' else -0.7
            phasors.append(mag * np.exp(1j * angle))

        total = sum(phasors)
        # Draw arrow from origin
        ax2.annotate('', xy=(total.real, total.imag), xytext=(0, 0),
                     arrowprops=dict(arrowstyle='->', color=C['orange'],
                                     lw=1.5, alpha=0.6))
        ax2.plot(total.real, total.imag, 'o', color=C['orange'],
                 markersize=8, alpha=0.7)
        ax2.text(total.real + 0.1, total.imag + 0.1, str(step+1),
                 fontsize=9, color=C['white'], fontweight='bold')

    # Draw unit circle for reference
    theta = np.linspace(0, 2*np.pi, 100)
    ax2.plot(2*np.cos(theta), 2*np.sin(theta), color=C['border'],
             linewidth=0.5, alpha=0.3)
    ax2.plot(0, 0, '+', color=C['gray'], markersize=15)

    ax2.set_xlim(-3, 3)
    ax2.set_ylim(-3, 3)
    ax2.set_aspect('equal')
    ax2.set_title('Rotating Resultant Field\n(Phasor Sum at Each Step)',
                  fontsize=13, fontweight='bold', color=C['orange'])
    ax2.set_xlabel('Real', fontsize=11)
    ax2.set_ylabel('Imaginary', fontsize=11)
    ax2.grid(alpha=0.2)

    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/triad_fig6_ac_motor.png', dpi=180)
    plt.close()
    print("  [OK] triad_fig6_ac_motor.png")


# ═══════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating Triad Phase-Lock visualizations...")
    fig1_phasor_diagram()
    fig2_step_heatmap()
    fig3_waveforms()
    fig4_interfaces()
    fig5_hexagram()
    fig6_ac_motor()
    print("Done — 6 triad figures saved to /home/ubuntu/demo/")
