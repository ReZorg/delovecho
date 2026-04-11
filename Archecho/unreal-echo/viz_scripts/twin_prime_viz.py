#!/usr/bin/env python3
"""
twin_prime_viz.py — Visualizations for the twin prime architecture of Systems 4 and 5.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

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
    'yellow': '#e3b341', 'gray': '#8b949e', 'white': '#c9d1d9',
    'bg': '#0d1117', 'card': '#161b22', 'border': '#30363d',
    'bridge': '#ff6b6b', 'teal': '#39d353',
}


# ═══════════════════════════════════════════════════════════════════
# Fig 1: The Landmark Sequence on a Number Line
# ═══════════════════════════════════════════════════════════════════
def fig1_landmarks():
    fig, axes = plt.subplots(2, 1, figsize=(22, 10), gridspec_kw={'height_ratios': [1, 1.5]})

    # Top: System 4 landmarks
    ax = axes[0]
    ax.set_facecolor('#0d1117')
    ax.set_xlim(-0.5, 13)
    ax.set_ylim(-1.5, 2.5)
    ax.axis('off')
    ax.set_title('System 4: Twin Primes {5, 7}  |  Cycle = 12  |  Pattern [5][2][5]',
                 fontsize=14, fontweight='bold', color=C['cyan'], pad=10)

    # Number line
    ax.plot([0, 12], [0, 0], color=C['border'], linewidth=2)
    for i in range(13):
        ax.plot([i, i], [-0.15, 0.15], color=C['border'], linewidth=1)
        ax.text(i, -0.5, str(i), ha='center', fontsize=8, color=C['gray'])

    # Landmarks: 0, 5, 7, 12
    s4_landmarks = [0, 5, 7, 12]
    s4_colors = [C['green'], C['orange'], C['orange'], C['green']]
    s4_labels = ['Start', '5E end', '5R start', 'End']
    for lm, col, lab in zip(s4_landmarks, s4_colors, s4_labels):
        ax.plot(lm, 0, 'o', color=col, markersize=14, zorder=5)
        ax.text(lm, 0.6, lab, ha='center', fontsize=9, color=col, fontweight='bold')

    # Segments
    ax.annotate('', xy=(5, 1.5), xytext=(0, 1.5),
                arrowprops=dict(arrowstyle='<->', color=C['green'], lw=2))
    ax.text(2.5, 1.8, '5E (body)', ha='center', fontsize=11, color=C['green'], fontweight='bold')

    ax.annotate('', xy=(7, 1.5), xytext=(5, 1.5),
                arrowprops=dict(arrowstyle='<->', color=C['yellow'], lw=2))
    ax.text(6, 1.8, '2P', ha='center', fontsize=11, color=C['yellow'], fontweight='bold')

    ax.annotate('', xy=(12, 1.5), xytext=(7, 1.5),
                arrowprops=dict(arrowstyle='<->', color=C['purple'], lw=2))
    ax.text(9.5, 1.8, '5R (body)', ha='center', fontsize=11, color=C['purple'], fontweight='bold')

    # Bottom: System 5 landmarks
    ax = axes[1]
    ax.set_facecolor('#0d1117')
    ax.set_xlim(-1, 32)
    ax.set_ylim(-2, 4)
    ax.axis('off')
    ax.set_title('System 5: Twin Primes {11,13} & {17,19}  |  Half-cycle = 30  |  Pattern [5,5,2,2,2,2,5,5]',
                 fontsize=14, fontweight='bold', color=C['pink'], pad=10)

    # Number line
    ax.plot([0, 30], [0, 0], color=C['border'], linewidth=2)
    for i in range(31):
        h = 0.2 if i % 5 == 0 else 0.1
        ax.plot([i, i], [-h, h], color=C['border'], linewidth=1)
        if i % 5 == 0:
            ax.text(i, -0.6, str(i), ha='center', fontsize=8, color=C['gray'])

    # Landmarks: 1, 6, 11, 13, 17, 19, 24, 30
    s5_landmarks = [1, 6, 11, 13, 17, 19, 24, 30]
    s5_colors = [C['green'], C['green'], C['orange'], C['orange'],
                 C['pink'], C['pink'], C['purple'], C['purple']]
    s5_labels = ['1', '6', '11', '13', '17', '19', '24', '30']

    for lm, col, lab in zip(s5_landmarks, s5_colors, s5_labels):
        ax.plot(lm, 0, 'o', color=col, markersize=12, zorder=5)
        ax.text(lm, 0.5, lab, ha='center', fontsize=10, color=col, fontweight='bold')

    # Gap annotations
    gaps = [5, 5, 2, 2, 2, 2, 5, 5]
    gap_colors = [C['green'], C['green'], C['bridge'], C['bridge'],
                  C['bridge'], C['bridge'], C['purple'], C['purple']]
    for i in range(len(gaps)):
        x1 = s5_landmarks[i]
        x2 = s5_landmarks[i + 1] if i + 1 < len(s5_landmarks) else 30
        mid = (x1 + x2) / 2
        ax.annotate('', xy=(x2, 1.5), xytext=(x1, 1.5),
                    arrowprops=dict(arrowstyle='<->', color=gap_colors[i], lw=1.5))
        ax.text(mid, 1.8, str(gaps[i]), ha='center', fontsize=11,
                color=gap_colors[i], fontweight='bold')

    # Label the zones
    ax.text(3.5, 2.8, 'Somatic E', ha='center', fontsize=12, color=C['green'],
            fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor=C['card'],
                                         edgecolor=C['green']))
    ax.text(15, 2.8, 'Twin Prime\nCentral Zone', ha='center', fontsize=11, color=C['bridge'],
            fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor=C['card'],
                                         edgecolor=C['bridge']))
    ax.text(27, 2.8, 'Autonomic R', ha='center', fontsize=12, color=C['purple'],
            fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor=C['card'],
                                         edgecolor=C['purple']))

    # Mirror pair annotations
    ax.text(15.5, -1.5, 'Mirror pairs sum to 31 = 2^5 - 1', ha='center',
            fontsize=12, color=C['yellow'], fontweight='bold')

    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/tp_fig1_landmarks.png', dpi=180)
    plt.close()
    print("  [OK] tp_fig1_landmarks.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 2: The Twin Prime Cross-Pairing Diagram
# ═══════════════════════════════════════════════════════════════════
def fig2_cross_pairing():
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_facecolor('#0d1117')
    ax.axis('off')

    ax.text(8, 11, 'Twin Prime Cross-Pairing', ha='center',
            fontsize=20, fontweight='bold', color=C['white'])
    ax.text(8, 10.3, 'Orthogonal sums: 11+19 = 13+17 = 30', ha='center',
            fontsize=13, color=C['yellow'])

    # Four primes arranged in a rectangle
    positions = {
        11: (3, 7), 13: (13, 7),
        17: (3, 3), 19: (13, 3),
    }
    labels = {
        11: ('11', 'R (Autonomic)', C['purple']),
        13: ('13', 'R (Somatic)', C['pink']),
        17: ('17', 'E (Autonomic)', C['orange']),
        19: ('19', 'E (Somatic)', C['green']),
    }

    for p, (x, y) in positions.items():
        name, role, color = labels[p]
        circle = plt.Circle((x, y), 0.8, facecolor=color, alpha=0.15,
                             edgecolor=color, linewidth=3)
        ax.add_patch(circle)
        ax.text(x, y + 0.1, name, ha='center', va='center', fontsize=22,
                fontweight='bold', color=color)
        ax.text(x, y - 0.5, role, ha='center', fontsize=9, color=C['gray'])

    # Cross-pairing lines
    # 11 + 19 = 30
    ax.plot([3.8, 12.2], [6.5, 3.5], color=C['bridge'], linewidth=2.5,
            linestyle='--', alpha=0.7)
    ax.text(8, 4.5, '11 + 19 = 30', ha='center', fontsize=13, color=C['bridge'],
            fontweight='bold', rotation=-20)

    # 13 + 17 = 30
    ax.plot([12.2, 3.8], [6.5, 3.5], color=C['bridge'], linewidth=2.5,
            linestyle='--', alpha=0.7)
    ax.text(8, 5.5, '13 + 17 = 30', ha='center', fontsize=13, color=C['bridge'],
            fontweight='bold', rotation=20)

    # Horizontal pairs (twin primes)
    ax.annotate('', xy=(4.2, 7), xytext=(11.8, 7),
                arrowprops=dict(arrowstyle='<->', color=C['yellow'], lw=2))
    ax.text(8, 7.4, 'gap = 2 (twin primes)', ha='center', fontsize=11, color=C['yellow'])

    ax.annotate('', xy=(4.2, 3), xytext=(11.8, 3),
                arrowprops=dict(arrowstyle='<->', color=C['yellow'], lw=2))
    ax.text(8, 2.4, 'gap = 2 (twin primes)', ha='center', fontsize=11, color=C['yellow'])

    # Vertical pairs (cross-gap = 6)
    ax.annotate('', xy=(3, 6), xytext=(3, 4),
                arrowprops=dict(arrowstyle='<->', color=C['teal'], lw=2))
    ax.text(1.5, 5, 'gap = 6', ha='center', fontsize=11, color=C['teal'], fontweight='bold')

    ax.annotate('', xy=(13, 6), xytext=(13, 4),
                arrowprops=dict(arrowstyle='<->', color=C['teal'], lw=2))
    ax.text(14.5, 5, 'gap = 6', ha='center', fontsize=11, color=C['teal'], fontweight='bold')

    # Pentad assignments
    ax.text(8, 8.8, 'Somatic Pentad: 19E + 13R = 32?  or  19E + 11R = 30',
            ha='center', fontsize=12, color=C['green'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor=C['card'], edgecolor=C['green']))
    ax.text(8, 1.2, 'Autonomic Pentad: 17E + 11R = 28?  or  17E + 13R = 30',
            ha='center', fontsize=12, color=C['orange'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor=C['card'], edgecolor=C['orange']))

    # The 6 = 2 × 3 identity
    ax.text(8, 0.3, '6 = 2 × 3 = S2_cycle × S3_threads = C(4,2) = edges of tetrahedron',
            ha='center', fontsize=11, color=C['teal'], fontweight='bold')

    ax.set_xlim(-1, 17)
    ax.set_ylim(-0.5, 12)
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/tp_fig2_crosspairing.png', dpi=180)
    plt.close()
    print("  [OK] tp_fig2_crosspairing.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 3: The Palindromic Gap Pattern
# ═══════════════════════════════════════════════════════════════════
def fig3_palindrome():
    fig, ax = plt.subplots(figsize=(20, 8))
    ax.set_facecolor('#0d1117')
    ax.axis('off')

    ax.text(10, 7, 'The Palindromic Gap Pattern', ha='center',
            fontsize=18, fontweight='bold', color=C['white'])

    gaps_s4 = [5, 2, 5]
    gaps_s5 = [5, 5, 2, 2, 2, 2, 5, 5]

    # System 4
    ax.text(10, 6, 'System 4: [5, 2, 5]', ha='center', fontsize=14,
            fontweight='bold', color=C['cyan'])

    x_start = 4
    for i, g in enumerate(gaps_s4):
        color = C['green'] if g == 5 else C['yellow']
        rect = plt.Rectangle((x_start, 4.8), g * 0.8, 0.8, facecolor=color, alpha=0.2,
                              edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x_start + g * 0.4, 5.2, str(g), ha='center', va='center',
                fontsize=16, fontweight='bold', color=color)
        x_start += g * 0.8 + 0.2

    # System 5
    ax.text(10, 4, 'System 5: [5, 5, 2, 2, 2, 2, 5, 5]', ha='center', fontsize=14,
            fontweight='bold', color=C['pink'])

    x_start = 2
    for i, g in enumerate(gaps_s5):
        color = C['green'] if g == 5 and i < 2 else (C['purple'] if g == 5 else C['bridge'])
        rect = plt.Rectangle((x_start, 2.8), g * 0.8, 0.8, facecolor=color, alpha=0.2,
                              edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x_start + g * 0.4, 3.2, str(g), ha='center', va='center',
                fontsize=16, fontweight='bold', color=color)
        x_start += g * 0.8 + 0.2

    # Mirror symmetry line
    ax.plot([10, 10], [2.5, 6.5], color=C['yellow'], linewidth=1, linestyle=':', alpha=0.5)
    ax.text(10, 2.2, 'axis of symmetry', ha='center', fontsize=10, color=C['yellow'])

    # Pattern evolution
    ax.text(10, 1.2, 'S4: [5] [2] [5]  ->  S5: [5,5] [2,2,2,2] [5,5]',
            ha='center', fontsize=13, color=C['white'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C['card'],
                      edgecolor=C['white'], linewidth=1.5))
    ax.text(10, 0.4, 'Each segment DOUBLES: the 5-body splits into two 5-bodies,\nthe 2-pivot expands into four 2-pivots',
            ha='center', fontsize=11, color=C['gray'])

    ax.set_xlim(0, 20)
    ax.set_ylim(-0.5, 8)
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/tp_fig3_palindrome.png', dpi=180)
    plt.close()
    print("  [OK] tp_fig3_palindrome.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 4: The Double Primorial Scaling Law
# ═══════════════════════════════════════════════════════════════════
def fig4_primorial():
    fig, axes = plt.subplots(1, 2, figsize=(22, 9))

    # Left: Cycle lengths on log scale
    ax = axes[0]
    systems = [2, 3, 4, 5, 6, 7]
    cycles = [2, 4, 12, 60, 420, 4620]
    ratios = ['-', '2', '3', '5', '7', '11']
    colors = [C['gray'], C['cyan'], C['green'], C['pink'], C['orange'], C['purple']]

    ax.semilogy(systems, cycles, 'o-', color=C['cyan'], markersize=10, linewidth=2)
    for s, c, r, col in zip(systems, cycles, ratios, colors):
        ax.plot(s, c, 'o', color=col, markersize=14, zorder=5)
        ax.text(s + 0.15, c * 1.3, f'{c}', fontsize=11, color=col, fontweight='bold')
        if r != '-':
            ax.text(s - 0.3, c * 0.5, f'×{r}', fontsize=10, color=C['yellow'])

    # Mark predicted values
    for s in [6, 7]:
        ax.plot(s, cycles[s-2], 'o', color=colors[s-2], markersize=14,
                markerfacecolor='none', markeredgewidth=2, linestyle='--')

    ax.set_xlabel('System N', fontsize=13)
    ax.set_ylabel('Cycle Length (log scale)', fontsize=13)
    ax.set_title('Cycle Lengths = 2 × Primorial', fontsize=14,
                 fontweight='bold', color=C['white'])
    ax.set_xticks(systems)
    ax.grid(True, alpha=0.2)

    # Right: The scaling table
    ax = axes[1]
    ax.set_facecolor('#0d1117')
    ax.axis('off')

    ax.text(0.5, 0.95, 'Cross-System Scaling Law', ha='center', va='top',
            fontsize=16, fontweight='bold', color=C['white'], transform=ax.transAxes)

    table_data = [
        ['System', 'Cycle', 'Twin Primes', 'E', 'R', 'E/R', 'Ratio'],
        ['S2', '2', '—', '1', '1', '1.00', '—'],
        ['S3', '4', '(3)', '3', '1', '3.00', '×2'],
        ['S4', '12', '{5,7}', '7', '5', '1.40', '×3'],
        ['S5', '60', '{11,13}{17,19}', '36', '24', '1.50', '×5'],
        ['S6*', '420', '{p,p+2}...', '?', '?', '?', '×7'],
        ['S7*', '4620', '{p,p+2}...', '?', '?', '?', '×11'],
    ]

    row_colors = [C['white'], C['gray'], C['cyan'], C['green'], C['pink'],
                  C['orange'], C['purple']]

    for i, row in enumerate(table_data):
        y = 0.82 - i * 0.1
        color = row_colors[i]
        alpha = 1.0 if i <= 4 else 0.5
        for j, cell in enumerate(row):
            x = 0.05 + j * 0.135
            weight = 'bold' if i == 0 else 'normal'
            ax.text(x, y, cell, fontsize=11, color=color, alpha=alpha,
                    fontweight=weight, transform=ax.transAxes)

    # Formula
    ax.text(0.5, 0.1, 'Cycle(N) = 2 × p(N-2)#\nwhere p(k)# = primorial of k-th prime',
            ha='center', fontsize=13, color=C['yellow'], fontweight='bold',
            transform=ax.transAxes,
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C['card'],
                      edgecolor=C['yellow'], linewidth=2))

    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/tp_fig4_primorial.png', dpi=180)
    plt.close()
    print("  [OK] tp_fig4_primorial.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 5: The Convolution Switch Mechanism
# ═══════════════════════════════════════════════════════════════════
def fig5_convolution_switch():
    fig, ax = plt.subplots(figsize=(22, 10))
    ax.set_facecolor('#0d1117')
    ax.axis('off')

    ax.text(11, 9.5, 'The Convolution Switch: How S5 Pentads Embed S4 Cycles',
            ha='center', fontsize=18, fontweight='bold', color=C['white'])

    # S4 cycle: 7E + 5R = 12
    # Tiled 5 times = 60
    s4_modes = ['E'] * 5 + ['P'] + ['R'] * 5 + ['P']

    # Show the 5 S4 cycles tiled
    y_base = 7.5
    for cycle_num in range(5):
        x_start = 0.5 + cycle_num * 4.2
        for step in range(12):
            m = s4_modes[step]
            color = C['green'] if m in ('E', 'P') else C['purple']
            if m == 'P':
                color = C['yellow']
            rect = plt.Rectangle((x_start + step * 0.33, y_base), 0.3, 0.6,
                                 facecolor=color, alpha=0.3, edgecolor=color, linewidth=0.5)
            ax.add_patch(rect)
        ax.text(x_start + 2, y_base - 0.3, f'S4 cycle {cycle_num + 1}',
                ha='center', fontsize=8, color=C['gray'])

    ax.text(11, y_base + 1, 'Thread A: 5 complete S4 cycles = 35E + 25R = 60 steps',
            ha='center', fontsize=11, color=C['cyan'])

    # Show the fold at step 30
    ax.plot([10.9, 10.9], [y_base - 0.5, y_base + 0.8], color=C['bridge'],
            linewidth=2, linestyle='--')
    ax.text(10.9, y_base - 0.7, 'FOLD (step 30)', ha='center', fontsize=9,
            color=C['bridge'], fontweight='bold')

    # Somatic pentad breakdown
    y_som = 5
    ax.text(5.5, y_som + 1.2, 'SOMATIC PENTAD (Thread A, first 30 steps)',
            ha='center', fontsize=13, fontweight='bold', color=C['green'])

    # 2 complete S4 cycles + half cycle
    segments = [
        ('S4 cycle 1', 12, C['green'], '7E+5R'),
        ('S4 cycle 2', 12, C['green'], '7E+5R'),
        ('Half S4', 6, C['yellow'], '5E+1R'),
    ]
    x = 0.5
    for label, width, color, split in segments:
        w = width * 0.33
        rect = plt.Rectangle((x, y_som), w, 0.8, facecolor=color, alpha=0.1,
                              edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + w / 2, y_som + 0.4, label, ha='center', fontsize=10,
                color=color, fontweight='bold')
        ax.text(x + w / 2, y_som - 0.3, split, ha='center', fontsize=9, color=C['gray'])
        x += w + 0.2

    ax.text(5.5, y_som - 0.8, 'Total: 2×(7E+5R) + (5E+1R) = 19E + 11R = 30 steps',
            ha='center', fontsize=12, color=C['green'], fontweight='bold')

    # Autonomic pentad breakdown
    y_aut = 2
    ax.text(16.5, y_aut + 1.2, 'AUTONOMIC PENTAD (Thread C, offset by 180°)',
            ha='center', fontsize=13, fontweight='bold', color=C['purple'])

    segments_aut = [
        ('Half S4', 6, C['yellow'], '2E+4R'),
        ('S4 cycle 4', 12, C['purple'], '7E+5R'),
        ('S4 cycle 5', 12, C['purple'], '7E+5R'),
    ]
    x = 11
    for label, width, color, split in segments_aut:
        w = width * 0.33
        rect = plt.Rectangle((x, y_aut), w, 0.8, facecolor=color, alpha=0.1,
                              edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + w / 2, y_aut + 0.4, label, ha='center', fontsize=10,
                color=color, fontweight='bold')
        ax.text(x + w / 2, y_aut - 0.3, split, ha='center', fontsize=9, color=C['gray'])
        x += w + 0.2

    ax.text(16.5, y_aut - 0.8, 'Total: (2E+4R) + 2×(7E+5R) = 16E + 14R  ->  adjusted by switch: 17E + 13R',
            ha='center', fontsize=12, color=C['purple'], fontweight='bold')

    # The switch mechanism
    ax.text(11, 0.5, 'The BRIDGE mode at the fold boundary (step 30) transfers 1E from Somatic to Autonomic',
            ha='center', fontsize=11, color=C['bridge'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C['card'],
                      edgecolor=C['bridge'], linewidth=2))

    ax.set_xlim(-0.5, 22)
    ax.set_ylim(-0.5, 10.5)
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/tp_fig5_switch.png', dpi=180)
    plt.close()
    print("  [OK] tp_fig5_switch.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 6: The 4-Thread Step Heatmap for 60 Steps
# ═══════════════════════════════════════════════════════════════════
def fig6_heatmap():
    fig, ax = plt.subplots(figsize=(24, 6))

    # Generate the mode data
    s4_modes = [1]*5 + [1] + [0]*5 + [1]  # 1=E/P, 0=R
    full_60 = s4_modes * 5

    offsets = {'A': 0, 'B': 3, 'C': 6, 'D': 9}
    thread_names = ['A (0 deg)', 'B (90 deg)', 'C (180 deg)', 'D (270 deg)']

    data = np.zeros((4, 60))
    for i, (name, offset) in enumerate(offsets.items()):
        for step in range(60):
            data[i, step] = full_60[(step + offset) % 60]

    # Custom colormap: R=purple, E=green
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap([C['purple'], C['green']])

    im = ax.imshow(data, aspect='auto', cmap=cmap, interpolation='nearest')
    ax.set_yticks(range(4))
    ax.set_yticklabels(thread_names, fontsize=11)
    ax.set_xlabel('Step (1-60)', fontsize=12)
    ax.set_title('4-Thread Mode Heatmap: 60-Step Cycle (Green=E, Purple=R)',
                 fontsize=14, fontweight='bold', color=C['white'])

    # Mark the fold at step 30
    ax.axvline(x=29.5, color=C['bridge'], linewidth=2, linestyle='--')
    ax.text(29.5, -0.8, 'FOLD', ha='center', fontsize=10, color=C['bridge'],
            fontweight='bold')

    # Mark pentad boundaries
    ax.axhline(y=1.5, color=C['yellow'], linewidth=1.5, linestyle=':')
    ax.text(-2, 0.5, 'Somatic', ha='right', fontsize=11, color=C['green'], fontweight='bold')
    ax.text(-2, 2.5, 'Autonomic', ha='right', fontsize=11, color=C['purple'], fontweight='bold')

    # Tick marks every 5 steps
    ax.set_xticks(range(0, 60, 5))
    ax.set_xticklabels(range(1, 61, 5))

    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/tp_fig6_heatmap.png', dpi=180)
    plt.close()
    print("  [OK] tp_fig6_heatmap.png")


# ═══════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating twin prime visualizations...")
    fig1_landmarks()
    fig2_cross_pairing()
    fig3_palindrome()
    fig4_primorial()
    fig5_convolution_switch()
    fig6_heatmap()
    print("Done — 6 twin prime figures saved.")
