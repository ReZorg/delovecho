#!/usr/bin/env python3
"""
s5_folding_viz.py — Visualizations for the S3-S5 resonance and folding.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from itertools import permutations, combinations

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
    'bridge': '#ff6b6b',
}


# ═══════════════════════════════════════════════════════════════════
# Fig 1: base[17] Decomposition Diagram
# ═══════════════════════════════════════════════════════════════════
def fig1_base17():
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.set_facecolor('#0d1117')
    ax.axis('off')
    
    # Draw 17 positions on a circle (0..16)
    r = 4
    cx, cy = 0, 0
    angles = [2 * np.pi * i / 17 - np.pi/2 for i in range(17)]
    positions = [(cx + r * np.cos(a), cy + r * np.sin(a)) for a in angles]
    
    # Color coding
    triad_colors = [C['cyan'], C['green'], C['pink'], C['orange']]
    triads = [(1,2,3), (5,6,7), (9,10,11), (13,14,15)]
    pivot_positions = {0: C['gray'], 16: C['red'], 8: C['yellow'], 4: C['purple'], 12: C['purple']}
    
    def get_color(i):
        if i in pivot_positions:
            return pivot_positions[i]
        for ti, triad in enumerate(triads):
            if i in triad:
                return triad_colors[ti]
        return C['gray']
    
    # Draw connecting arcs for triads
    for ti, triad in enumerate(triads):
        pts = [positions[t] for t in triad]
        tri = plt.Polygon(pts, fill=True, facecolor=triad_colors[ti], alpha=0.08,
                          edgecolor=triad_colors[ti], linewidth=2, linestyle='--')
        ax.add_patch(tri)
    
    # Draw the circle backbone
    theta = np.linspace(0, 2*np.pi, 200)
    ax.plot(cx + r * np.cos(theta), cy + r * np.sin(theta),
            color=C['border'], linewidth=1, alpha=0.3)
    
    # Draw positions
    for i in range(17):
        x, y = positions[i]
        color = get_color(i)
        size = 0.4 if i not in pivot_positions else 0.5
        circle = plt.Circle((x, y), size, facecolor=color, alpha=0.3,
                             edgecolor=color, linewidth=2.5)
        ax.add_patch(circle)
        ax.text(x, y, str(i), ha='center', va='center', fontsize=13,
                fontweight='bold', color='white')
    
    # Labels
    ax.text(0, 5.8, 'base[17] Decomposition', ha='center', fontsize=16,
            fontweight='bold', color=C['white'])
    ax.text(0, 5.2, '(16)(8)(4,12)((1,2,3),(5,6,7),(9,10,11),(13,14,15))',
            ha='center', fontsize=12, color=C['yellow'])
    
    # Legend
    legend_items = [
        (C['gray'], '0 = Ground'),
        (C['red'], '16 = Modal Pivot (E/R)'),
        (C['yellow'], '8 = Quarter Pivot'),
        (C['purple'], '4,12 = Dyad Pivots'),
        (C['cyan'], '(1,2,3) = Triad 0'),
        (C['green'], '(5,6,7) = Triad 1'),
        (C['pink'], '(9,10,11) = Triad 2'),
        (C['orange'], '(13,14,15) = Triad 3'),
    ]
    for i, (color, label) in enumerate(legend_items):
        y_pos = -3.5 - i * 0.5
        ax.plot(5.5, y_pos, 'o', color=color, markersize=10)
        ax.text(6.0, y_pos, label, fontsize=10, color=C['white'], va='center')
    
    # Annotation: 4 × S3
    ax.text(-7, -2, '4 Triads = 4 × S3', fontsize=14, fontweight='bold',
            color=C['bridge'],
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C['card'],
                      edgecolor=C['bridge']))
    ax.text(-7, -2.8, 'Each triad has S3 structure:', fontsize=10, color=C['gray'])
    ax.text(-7, -3.3, '(pivot)(half)(dyad)', fontsize=10, color=C['yellow'])
    ax.text(-7, -3.8, 'e.g. (1,2,3): pivot=2, dyad=(1,3)', fontsize=10, color=C['cyan'])
    
    ax.set_xlim(-8.5, 8.5)
    ax.set_ylim(-8, 6.5)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/fold_fig1_base17.png', dpi=180)
    plt.close()
    print("  [OK] fold_fig1_base17.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 2: S3-S5 Resonance — Side by Side
# ═══════════════════════════════════════════════════════════════════
def fig2_resonance():
    fig, axes = plt.subplots(1, 2, figsize=(20, 9))
    
    # Left: System 3 base[5]
    ax = axes[0]
    ax.set_facecolor('#0d1117')
    ax.axis('off')
    
    r = 2.5
    angles_5 = [2 * np.pi * i / 5 - np.pi/2 for i in range(5)]
    pos_5 = [(r * np.cos(a), r * np.sin(a)) for a in angles_5]
    
    colors_5 = [C['gray'], C['orange'], C['yellow'], C['orange'], C['red']]
    labels_5 = ['0\nGround', '1\nDyad', '2\nHalf', '3\nDyad', '4\nPivot']
    
    # Draw circle
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(r * np.cos(theta), r * np.sin(theta), color=C['border'], linewidth=1, alpha=0.3)
    
    # Highlight the dyad
    ax.plot([pos_5[1][0], pos_5[3][0]], [pos_5[1][1], pos_5[3][1]],
            color=C['orange'], linewidth=3, alpha=0.5)
    
    for i in range(5):
        x, y = pos_5[i]
        circle = plt.Circle((x, y), 0.45, facecolor=colors_5[i], alpha=0.3,
                             edgecolor=colors_5[i], linewidth=2.5)
        ax.add_patch(circle)
        ax.text(x, y, labels_5[i], ha='center', va='center', fontsize=9,
                fontweight='bold', color='white')
    
    ax.set_title('System 3: base[5]\n(4)(2)(1,3)', fontsize=14,
                 fontweight='bold', color=C['orange'], pad=15)
    ax.text(0, -4, '4 terms | 2 threads | 4 steps\nV_4 (order 4)',
            ha='center', fontsize=11, color=C['gray'])
    ax.set_xlim(-4, 4)
    ax.set_ylim(-5, 4)
    
    # Right: System 5 base[17] showing 4×S3 structure
    ax = axes[1]
    ax.set_facecolor('#0d1117')
    ax.axis('off')
    
    r = 3
    angles_17 = [2 * np.pi * i / 17 - np.pi/2 for i in range(17)]
    pos_17 = [(r * np.cos(a), r * np.sin(a)) for a in angles_17]
    
    triads = [(1,2,3), (5,6,7), (9,10,11), (13,14,15)]
    triad_colors = [C['cyan'], C['green'], C['pink'], C['orange']]
    
    # Draw triads as triangles
    for ti, triad in enumerate(triads):
        pts = [pos_17[t] for t in triad]
        tri = plt.Polygon(pts, fill=True, facecolor=triad_colors[ti], alpha=0.08,
                          edgecolor=triad_colors[ti], linewidth=2)
        ax.add_patch(tri)
    
    # Draw circle
    ax.plot(r * np.cos(theta), r * np.sin(theta), color=C['border'], linewidth=1, alpha=0.3)
    
    pivot_set = {0, 4, 8, 12, 16}
    for i in range(17):
        x, y = pos_17[i]
        if i in pivot_set:
            color = C['red'] if i == 16 else (C['yellow'] if i == 8 else (C['purple'] if i in (4,12) else C['gray']))
            circle = plt.Circle((x, y), 0.35, facecolor=color, alpha=0.3,
                                edgecolor=color, linewidth=2.5)
        else:
            for ti, triad in enumerate(triads):
                if i in triad:
                    color = triad_colors[ti]
                    break
            circle = plt.Circle((x, y), 0.3, facecolor=color, alpha=0.3,
                                edgecolor=color, linewidth=2)
        ax.add_patch(circle)
        ax.text(x, y, str(i), ha='center', va='center', fontsize=10,
                fontweight='bold', color='white')
    
    ax.set_title('System 5: base[17]\n(16)(8)(4,12)(4 x S3)', fontsize=14,
                 fontweight='bold', color=C['purple'], pad=15)
    ax.text(0, -4.5, '16 terms | 4 threads | 60 steps\nA_5 (order 60)',
            ha='center', fontsize=11, color=C['gray'])
    ax.text(0, -5.2, 'S5 = S3 ⊗ S3 + BRIDGE', ha='center', fontsize=12,
            fontweight='bold', color=C['bridge'])
    ax.set_xlim(-4.5, 4.5)
    ax.set_ylim(-6, 4.5)
    
    fig.suptitle('The S3-S5 Resonance: System 5 Contains 4 Copies of System 3',
                 fontsize=15, fontweight='bold', color=C['white'], y=0.98)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/fold_fig2_resonance.png', dpi=180)
    plt.close()
    print("  [OK] fold_fig2_resonance.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 3: The Universal Folding Law
# ═══════════════════════════════════════════════════════════════════
def fig3_folding_law():
    fig, ax = plt.subplots(figsize=(18, 10))
    ax.set_facecolor('#0d1117')
    ax.axis('off')
    
    systems = ['S2', 'S3', 'S4', 'S5']
    groups = ['C_2', 'V_4', 'A_4', 'A_5']
    orders = [2, 4, 12, 60]
    steps = [2, 4, 12, 60]
    threads = [1, 2, 3, 4]
    folded = [1, 2, 6, 30]
    mechanisms = ['Direct\nFlip', 'Alternation\n(180°)', 'Rotation\n(120°)', 'Convolution\n(90°)']
    colors = [C['red'], C['orange'], C['cyan'], C['purple']]
    
    # Draw as a flowing diagram
    for i in range(4):
        x = i * 4.5
        y = 0
        
        # System box
        rect = plt.Rectangle((x - 1.5, y + 2), 3, 4, facecolor=colors[i], alpha=0.1,
                              edgecolor=colors[i], linewidth=2, 
                              transform=ax.transData)
        ax.add_patch(rect)
        
        ax.text(x, y + 5.5, systems[i], ha='center', fontsize=18,
                fontweight='bold', color=colors[i])
        ax.text(x, y + 4.8, groups[i], ha='center', fontsize=13,
                color=colors[i])
        ax.text(x, y + 4.0, f'|G| = {orders[i]}', ha='center', fontsize=12,
                color=C['white'])
        ax.text(x, y + 3.3, f'{threads[i]} threads', ha='center', fontsize=11,
                color=C['gray'])
        ax.text(x, y + 2.5, mechanisms[i], ha='center', fontsize=10,
                color=C['yellow'])
        
        # Arrow down
        ax.annotate('', xy=(x, y + 1.5), xytext=(x, y + 2),
                    arrowprops=dict(arrowstyle='->', color=C['white'], lw=2))
        
        # Division by 2
        ax.text(x + 1.8, y + 1.7, '÷ 2', fontsize=12, fontweight='bold',
                color=C['red'], ha='center')
        ax.text(x + 1.8, y + 1.2, '(C_2)', fontsize=9, color=C['red'], ha='center')
        
        # Folded result
        rect2 = plt.Rectangle((x - 1.2, y - 0.5), 2.4, 1.5, facecolor=C['bridge'], alpha=0.1,
                               edgecolor=C['bridge'], linewidth=2)
        ax.add_patch(rect2)
        ax.text(x, y + 0.5, f'{folded[i]}', ha='center', fontsize=22,
                fontweight='bold', color=C['bridge'])
        ax.text(x, y - 0.1, 'moments', ha='center', fontsize=10,
                color=C['gray'])
        
        # Arrow to next
        if i < 3:
            ax.annotate('', xy=(x + 2.5, y + 4), xytext=(x + 2, y + 4),
                        arrowprops=dict(arrowstyle='->', color=C['border'], lw=1.5))
    
    # The folded sequence
    ax.text(6.75, -2, 'Folded moments: 1, 2, 6, 30 = |G_N| / 2',
            ha='center', fontsize=16, fontweight='bold', color=C['bridge'],
            bbox=dict(boxstyle='round,pad=0.5', facecolor=C['card'],
                      edgecolor=C['bridge'], linewidth=2))
    
    ax.text(6.75, -3.2, 'The factor of 2 is ALWAYS the primordial C_2 (System 2\'s Digon)',
            ha='center', fontsize=12, color=C['yellow'], style='italic')
    
    ax.set_xlim(-2.5, 16)
    ax.set_ylim(-4, 7)
    ax.set_title('The Universal Folding Law: |G_N| / |C_2| = Folded Moments',
                 fontsize=16, fontweight='bold', color=C['white'], pad=20)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/fold_fig3_law.png', dpi=180)
    plt.close()
    print("  [OK] fold_fig3_law.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 4: The Convolution Diagram
# ═══════════════════════════════════════════════════════════════════
def fig4_convolution():
    fig, axes = plt.subplots(2, 1, figsize=(20, 12), gridspec_kw={'height_ratios': [3, 2]})
    
    # Top: 4 thread waveforms showing 90° phase lock
    ax = axes[0]
    ax.set_facecolor('#161b22')
    
    t = np.linspace(0, 4*np.pi, 500)
    thread_colors = [C['cyan'], C['green'], C['pink'], C['orange']]
    thread_labels = ['Thread A (0°)', 'Thread B (90°)', 'Thread C (180°)', 'Thread D (270°)']
    
    for i in range(4):
        phase = i * np.pi / 2  # 90° apart
        wave = np.sin(t - phase)
        ax.plot(t, wave + i * 2.5, color=thread_colors[i], linewidth=2, alpha=0.8)
        ax.fill_between(t, i * 2.5, wave + i * 2.5,
                        where=(wave > 0), color=C['green'], alpha=0.1)
        ax.fill_between(t, i * 2.5, wave + i * 2.5,
                        where=(wave < 0), color=C['purple'], alpha=0.1)
        ax.text(-0.3, i * 2.5, thread_labels[i], fontsize=10, fontweight='bold',
                color=thread_colors[i], ha='right', va='center')
        ax.axhline(y=i * 2.5, color=C['border'], linewidth=0.5, alpha=0.3)
    
    # Mark the 90° phase offset
    for i in range(4):
        phase = i * np.pi / 2
        ax.axvline(x=phase, color=thread_colors[i], linewidth=1, alpha=0.3, linestyle='--')
    
    ax.set_xlim(-2, 4*np.pi + 0.5)
    ax.set_ylim(-1.5, 9)
    ax.set_xlabel('Phase', fontsize=12)
    ax.set_title('4 Threads Phase-Locked at 90° — The Orthogonal Tetrad',
                 fontsize=14, fontweight='bold', color=C['white'], pad=10)
    
    # E/R labels
    ax.text(4*np.pi + 0.3, 8, 'E (above)', fontsize=10, color=C['green'], fontweight='bold')
    ax.text(4*np.pi + 0.3, 7.3, 'R (below)', fontsize=10, color=C['purple'], fontweight='bold')
    
    # Bottom: The convolution result — folded moments
    ax = axes[1]
    ax.set_facecolor('#161b22')
    
    # Show 30 folded moments as a bar chart
    # Each moment combines the states of 4 threads
    moments = np.arange(30)
    # Simulate: at each moment, count how many threads are in E vs R
    e_per_moment = []
    for m in moments:
        # 4 threads at 90° phase, sampled at moment m
        e_count = sum(1 for i in range(4) if np.sin(2*np.pi*m/30 - i*np.pi/2) > 0)
        e_per_moment.append(e_count)
    
    bar_colors = []
    for e in e_per_moment:
        if e == 4:
            bar_colors.append(C['green'])
        elif e == 0:
            bar_colors.append(C['purple'])
        elif e == 3:
            bar_colors.append('#2d8a3e')
        elif e == 1:
            bar_colors.append('#7a5fad')
        else:
            bar_colors.append(C['bridge'])
    
    ax.bar(moments, [e/4 for e in e_per_moment], color=bar_colors, alpha=0.7, width=0.8)
    ax.axhline(y=0.5, color=C['yellow'], linewidth=1, linestyle='--', alpha=0.5)
    ax.text(30.5, 0.5, 'E/R\nbalance', fontsize=9, color=C['yellow'], va='center')
    
    ax.set_xlabel('Folded Moment (0-29)', fontsize=12)
    ax.set_ylabel('E fraction', fontsize=12)
    ax.set_title('30 Folded Moments (60 steps / C_2)',
                 fontsize=14, fontweight='bold', color=C['bridge'], pad=10)
    
    legend_elements = [
        mpatches.Patch(facecolor=C['green'], alpha=0.7, label='Pure E'),
        mpatches.Patch(facecolor='#2d8a3e', alpha=0.7, label='Dominant E'),
        mpatches.Patch(facecolor=C['bridge'], alpha=0.7, label='BRIDGE'),
        mpatches.Patch(facecolor='#7a5fad', alpha=0.7, label='Dominant R'),
        mpatches.Patch(facecolor=C['purple'], alpha=0.7, label='Pure R'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9,
              facecolor=C['card'], edgecolor=C['border'], ncol=5)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/fold_fig4_convolution.png', dpi=180)
    plt.close()
    print("  [OK] fold_fig4_convolution.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 5: The Tensor Square S3 ⊗ S3
# ═══════════════════════════════════════════════════════════════════
def fig5_tensor_square():
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_facecolor('#0d1117')
    ax.axis('off')
    
    # Draw S3's 4 terms as a column
    s3_terms = ['(4)\nPivot', '(2)\nHalf', '(1)\nDyad-L', '(3)\nDyad-R']
    s3_colors = [C['red'], C['yellow'], C['orange'], C['orange']]
    
    # S3 column (left)
    ax.text(-5, 8, 'S3 terms', ha='center', fontsize=14, fontweight='bold', color=C['orange'])
    for i, (term, color) in enumerate(zip(s3_terms, s3_colors)):
        y = 6 - i * 2
        rect = plt.Rectangle((-6.2, y - 0.5), 2.4, 1, facecolor=color, alpha=0.15,
                              edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        ax.text(-5, y, term, ha='center', va='center', fontsize=10,
                fontweight='bold', color=color)
    
    # S3 row (top)
    ax.text(2, 9, 'S3 terms (×)', ha='center', fontsize=14, fontweight='bold', color=C['orange'])
    for j, (term, color) in enumerate(zip(s3_terms, s3_colors)):
        x = -1 + j * 3
        rect = plt.Rectangle((x - 1, 7.5), 2, 1, facecolor=color, alpha=0.15,
                              edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x, 8, term, ha='center', va='center', fontsize=9,
                fontweight='bold', color=color)
    
    # 4×4 tensor product grid
    product_labels = [
        ['(16)\nPivot²', '(8)\nP×H', '(4)\nP×DL', '(12)\nP×DR'],
        ['(8)\nH×P', '(4)\nHalf²', '(2)\nH×DL', '(6)\nH×DR'],
        ['(4)\nDL×P', '(2)\nDL×H', '(1)\nDyad²L', '(3)\nDL×DR'],
        ['(12)\nDR×P', '(6)\nDR×H', '(3)\nDR×DL', '(9)\nDyad²R'],
    ]
    
    # Color the products
    for i in range(4):
        for j in range(4):
            x = -1 + j * 3
            y = 6 - i * 2
            
            # Determine if this is a pivot, triad member, or dyad
            label = product_labels[i][j]
            num = int(label.split(')')[0].split('(')[1])
            
            if num in (16,):
                color = C['red']
            elif num in (8,):
                color = C['yellow']
            elif num in (4, 12):
                color = C['purple']
            elif num in (1, 2, 3):
                color = C['cyan']
            elif num in (5, 6, 7):
                color = C['green']
            elif num in (9, 10, 11):
                color = C['pink']
            elif num in (13, 14, 15):
                color = C['orange']
            else:
                color = C['gray']
            
            rect = plt.Rectangle((x - 1.2, y - 0.7), 2.4, 1.4, facecolor=color, alpha=0.08,
                                  edgecolor=color, linewidth=1.5)
            ax.add_patch(rect)
            ax.text(x, y, label, ha='center', va='center', fontsize=8,
                    color=color, fontweight='bold')
    
    # Arrow and label
    ax.text(2, -2.5, 'S3 ⊗ S3 generates the 16 terms of base[17]',
            ha='center', fontsize=14, fontweight='bold', color=C['bridge'],
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C['card'],
                      edgecolor=C['bridge'], linewidth=2))
    ax.text(2, -3.5, 'Diagonal: (16)(4)(1)(9) = pivots + self-products',
            ha='center', fontsize=11, color=C['yellow'])
    ax.text(2, -4.2, 'Off-diagonal: cross-products fill the 4 triads',
            ha='center', fontsize=11, color=C['gray'])
    
    ax.set_xlim(-7.5, 11.5)
    ax.set_ylim(-5, 10)
    ax.set_title('S5 = S3 ⊗ S3 + BRIDGE Corrections\nThe Tensor Square of System 3',
                 fontsize=16, fontweight='bold', color=C['white'], pad=20)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/fold_fig5_tensor.png', dpi=180)
    plt.close()
    print("  [OK] fold_fig5_tensor.png")


# ═══════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating S3-S5 resonance visualizations...")
    fig1_base17()
    fig2_resonance()
    fig3_folding_law()
    fig4_convolution()
    fig5_tensor_square()
    print("Done — 5 folding figures saved.")
