#!/usr/bin/env python3
"""
system5_viz.py — Visualizations for System 5 (Pentachoron) analysis.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from itertools import permutations, combinations
from collections import Counter

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
# Recompute the 60-step mode data
# ═══════════════════════════════════════════════════════════════════
def sign(p):
    n = len(p)
    return 1 if sum(1 for i in range(n) for j in range(i+1,n) if p[i]>p[j]) % 2 == 0 else -1

A5_elements = sorted([p for p in permutations(range(5)) if sign(p) == 1])
sys4_pattern = ['R','R','E','E','E','E','E','E','E','R','R','R']

# Build cosets and mode assignments
cosets = {}
for k in range(5):
    cosets[k] = sorted([p for p in A5_elements if p[4] == k])

step_sequence = []
for k in range(5):
    step_sequence.extend(cosets[k])

cell_modes = {}
for v in range(5):
    cell_modes[v] = []
    coset_members = {}
    for idx, p in enumerate(step_sequence):
        cl = p[v]
        if cl not in coset_members:
            coset_members[cl] = []
        coset_members[cl].append(idx)
    coset_assignment = {}
    for cl in sorted(coset_members.keys()):
        members = coset_members[cl]
        for pos, step_idx in enumerate(members):
            coset_assignment[step_idx] = sys4_pattern[pos % 12]
    for idx in range(60):
        cell_modes[v].append(coset_assignment.get(idx, '?'))

step_modes = []
step_e_counts = []
for idx in range(60):
    modes = [cell_modes[v][idx] for v in range(5)]
    e_count = modes.count('E')
    r_count = modes.count('R')
    step_e_counts.append(e_count)
    if e_count == 5:
        step_modes.append('E_pure')
    elif r_count == 5:
        step_modes.append('R_pure')
    elif e_count >= 4:
        step_modes.append('E_dom')
    elif r_count >= 4:
        step_modes.append('R_dom')
    else:
        step_modes.append('BRIDGE')


# ═══════════════════════════════════════════════════════════════════
# Fig 1: The Pentachoron (2D projection of 4-simplex)
# ═══════════════════════════════════════════════════════════════════
def fig1_pentachoron():
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_facecolor('#0d1117')
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 5 vertices in a pentagonal arrangement
    r = 4
    angles = [np.pi/2 + 2*np.pi*i/5 for i in range(5)]
    verts = [(r*np.cos(a), r*np.sin(a)) for a in angles]
    labels = ['a', 'b', 'c', 'd', 'e']
    colors = [C['cyan'], C['green'], C['pink'], C['orange'], C['purple']]
    
    # Draw all 10 edges (complete graph K_5)
    for i in range(5):
        for j in range(i+1, 5):
            ax.plot([verts[i][0], verts[j][0]], [verts[i][1], verts[j][1]],
                    color=C['yellow'], linewidth=1.5, alpha=0.3)
    
    # Highlight the 5 tetrahedral cells with colored fills
    cell_colors = [C['cyan'], C['green'], C['pink'], C['orange'], C['purple']]
    for removed in range(5):
        cell_verts = [verts[i] for i in range(5) if i != removed]
        # Draw the 4 triangular faces of this tetrahedron lightly
        for combo in combinations([i for i in range(5) if i != removed], 3):
            tri = plt.Polygon([verts[c] for c in combo], alpha=0.02,
                               facecolor=cell_colors[removed])
            ax.add_patch(tri)
    
    # Draw vertices
    for i, ((x, y), label, color) in enumerate(zip(verts, labels, colors)):
        circle = plt.Circle((x, y), 0.45, facecolor=color, alpha=0.4,
                             edgecolor=color, linewidth=3)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=22,
                fontweight='bold', color='white')
    
    # Central info
    ax.text(0, -0.5, '(((((a)b)c)d)e)', ha='center', fontsize=16,
            color=C['yellow'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C['card'],
                      edgecolor=C['border']))
    
    ax.text(0, -6.5, '[1, 5, 10, 10, 5, 1] = 32', ha='center',
            fontsize=14, color=C['white'], fontweight='bold')
    ax.text(0, -7.2, '4 threads | 60 steps | E + R + BRIDGE', ha='center',
            fontsize=11, color=C['gray'])
    ax.text(0, -7.8, 'Group: A_5 (order 60) — SIMPLE', ha='center',
            fontsize=13, color=C['red'], fontweight='bold')
    
    ax.set_xlim(-6.5, 6.5)
    ax.set_ylim(-8.5, 6)
    ax.set_title('System 5: The Pentachoron (4-simplex)\n'
                 '5 interlocking tetrahedra in 4D',
                 fontsize=16, fontweight='bold', color=C['purple'], pad=20)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/sys5_fig1_pentachoron.png', dpi=180)
    plt.close()
    print("  [OK] sys5_fig1_pentachoron.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 2: 60-Step Mode Heatmap with BRIDGE detection
# ═══════════════════════════════════════════════════════════════════
def fig2_mode_heatmap():
    fig, axes = plt.subplots(2, 1, figsize=(20, 10), gridspec_kw={'height_ratios': [5, 2]})
    
    # Top: Cell-by-cell heatmap
    ax = axes[0]
    ax.set_facecolor('#161b22')
    
    mode_color_map = {'E': C['green'], 'R': C['purple']}
    
    for v in range(5):
        for idx in range(60):
            mode = cell_modes[v][idx]
            color = mode_color_map.get(mode, C['gray'])
            alpha = 0.7 if mode == 'E' else 0.4
            rect = plt.Rectangle((idx, 4-v), 1, 1, facecolor=color, alpha=alpha,
                                  edgecolor=C['border'], linewidth=0.3)
            ax.add_patch(rect)
    
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 5)
    ax.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5])
    ax.set_yticklabels(['Cell 4', 'Cell 3', 'Cell 2', 'Cell 1', 'Cell 0'],
                        fontsize=10, fontweight='bold')
    ax.set_xticks(range(0, 61, 5))
    ax.set_xlabel('Step', fontsize=12)
    ax.set_title('Cell-by-Cell E/R Assignment (5 tetrahedral cells x 60 steps)',
                 fontsize=13, fontweight='bold', color=C['white'], pad=10)
    
    # Bottom: Composite mode
    ax = axes[1]
    ax.set_facecolor('#161b22')
    
    composite_colors = {
        'E_pure': C['green'],
        'E_dom': '#2d8a3e',
        'BRIDGE': C['bridge'],
        'R_dom': '#7a5fad',
        'R_pure': C['purple'],
    }
    
    for idx in range(60):
        mode = step_modes[idx]
        color = composite_colors.get(mode, C['gray'])
        alpha = 0.9
        rect = plt.Rectangle((idx, 0), 1, 1, facecolor=color, alpha=alpha,
                              edgecolor=C['border'], linewidth=0.3)
        ax.add_patch(rect)
        # Label
        if mode == 'BRIDGE':
            ax.text(idx + 0.5, 0.5, 'B', ha='center', va='center',
                    fontsize=7, fontweight='bold', color='white')
    
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.5])
    ax.set_yticklabels(['Mode'], fontsize=10, fontweight='bold')
    ax.set_xticks(range(0, 61, 5))
    ax.set_xlabel('Step', fontsize=12)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=C['green'], alpha=0.9, label='E (pure)'),
        mpatches.Patch(facecolor='#2d8a3e', alpha=0.9, label='E (dominant)'),
        mpatches.Patch(facecolor=C['bridge'], alpha=0.9, label='BRIDGE (E+R)'),
        mpatches.Patch(facecolor='#7a5fad', alpha=0.9, label='R (dominant)'),
        mpatches.Patch(facecolor=C['purple'], alpha=0.9, label='R (pure)'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9,
              facecolor=C['card'], edgecolor=C['border'], ncol=5)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/sys5_fig2_heatmap.png', dpi=180)
    plt.close()
    print("  [OK] sys5_fig2_heatmap.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 3: Extended Subgroup Chain (Systems 2-5)
# ═══════════════════════════════════════════════════════════════════
def fig3_extended_chain():
    fig, ax = plt.subplots(figsize=(18, 10))
    ax.set_facecolor('#0d1117')
    
    nodes = [
        (0, 0, '{e}', 1, C['gray'], 'Identity'),
        (0, 2, 'C_2', 2, C['red'], 'System 2: Digon\nPrimordial Flip'),
        (0, 4, 'V_4', 4, C['orange'], 'System 3: Triangle\nKlein Four-Group'),
        (0, 6, 'A_4', 12, C['cyan'], 'System 4: Tetrahedron\nDecomposable'),
        (0, 8, 'A_5', 60, C['purple'], 'System 5: Pentachoron\nSIMPLE (irreducible!)'),
    ]
    
    for i in range(len(nodes) - 1):
        x1, y1 = nodes[i][0], nodes[i][1]
        x2, y2 = nodes[i+1][0], nodes[i+1][1]
        ax.plot([x1, x2], [y1, y2], color=C['border'], linewidth=3, zorder=1)
        idx_val = nodes[i+1][3] // nodes[i][3]
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.6, my, f'index {idx_val}', fontsize=10, color=C['yellow'],
                fontweight='bold', ha='left', va='center')
    
    for x, y, label, order_val, color, desc in nodes:
        circle = plt.Circle((x, y), 0.55, facecolor=color, alpha=0.2,
                             edgecolor=color, linewidth=3, zorder=2)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=16,
                fontweight='bold', color=color, zorder=3)
        ax.text(x - 1.5, y, f'|{label}| = {order_val}', ha='right',
                va='center', fontsize=12, color=C['white'], fontweight='bold')
        ax.text(x + 2.5, y, desc, ha='left', va='center', fontsize=11,
                color=C['gray'])
    
    # Annotations
    ax.text(6.5, 6, 'A_4 = V_4 : C_3', ha='left', fontsize=12,
            color=C['cyan'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=C['card'],
                      edgecolor=C['cyan'], alpha=0.5))
    ax.text(6.5, 5.3, 'Decomposable (V_4 is normal)', ha='left',
            fontsize=10, color=C['gray'])
    
    ax.text(6.5, 8, 'A_5 is SIMPLE', ha='left', fontsize=12,
            color=C['red'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=C['card'],
                      edgecolor=C['red'], alpha=0.5))
    ax.text(6.5, 7.3, 'No normal subgroups!', ha='left',
            fontsize=10, color=C['red'])
    ax.text(6.5, 6.8, 'First non-abelian simple group', ha='left',
            fontsize=10, color=C['gray'])
    
    # Index sequence annotation
    ax.text(3, 1, 'Index: 2', fontsize=11, color=C['yellow'], ha='center')
    ax.text(3, 3, 'Index: 2', fontsize=11, color=C['yellow'], ha='center')
    ax.text(3, 5, 'Index: 3', fontsize=11, color=C['yellow'], ha='center')
    ax.text(3, 7, 'Index: 5', fontsize=11, color=C['yellow'], ha='center')
    
    ax.text(0, -1.5, 'Index sequence: 2, 2, 3, 5 (primes!)',
            ha='center', fontsize=13, color=C['yellow'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C['card'],
                      edgecolor=C['yellow']))
    
    ax.set_xlim(-4, 12)
    ax.set_ylim(-2.5, 9.5)
    ax.axis('off')
    ax.set_title('Extended Subgroup Chain: Systems 2-5\n'
                 'C_2 < V_4 < A_4 < A_5',
                 fontsize=15, fontweight='bold', color=C['white'], pad=20)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/sys5_fig3_chain.png', dpi=180)
    plt.close()
    print("  [OK] sys5_fig3_chain.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 4: Mode Evolution Across Systems
# ═══════════════════════════════════════════════════════════════════
def fig4_mode_evolution():
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    
    # Left: Stacked bar chart of mode proportions
    ax = axes[0]
    ax.set_facecolor('#161b22')
    
    systems = ['Sys 2\n(C_2)', 'Sys 3\n(V_4)', 'Sys 4\n(A_4)', 'Sys 5\n(A_5)']
    # Mode proportions per system
    # Sys 2: 1E + 1R = 50% E, 50% R, 0% B
    # Sys 3: 3E + 1R per thread = 75% E, 25% R, 0% B
    # Sys 4: 7E + 5R per thread = 58.3% E, 41.7% R, 0% B
    # Sys 5: from engine: 50% E-ish, 26.7% R-ish, 23.3% B
    e_pcts = [50, 75, 58.3, 50.0]  # pure + dominant E
    r_pcts = [50, 25, 41.7, 26.7]  # pure + dominant R
    b_pcts = [0, 0, 0, 23.3]       # BRIDGE
    
    x = np.arange(len(systems))
    width = 0.6
    
    bars_e = ax.bar(x, e_pcts, width, color=C['green'], alpha=0.7, label='Expressive (E)')
    bars_r = ax.bar(x, r_pcts, width, bottom=e_pcts, color=C['purple'], alpha=0.7, label='Regenerative (R)')
    bars_b = ax.bar(x, b_pcts, width, bottom=[e+r for e,r in zip(e_pcts, r_pcts)],
                    color=C['bridge'], alpha=0.7, label='BRIDGE (B)')
    
    ax.set_xticks(x)
    ax.set_xticklabels(systems, fontsize=11, fontweight='bold')
    ax.set_ylabel('Percentage of Steps', fontsize=12)
    ax.set_ylim(0, 105)
    ax.legend(fontsize=10, facecolor=C['card'], edgecolor=C['border'])
    ax.set_title('Mode Proportions Across Systems', fontsize=13,
                 fontweight='bold', color=C['white'], pad=10)
    
    # Right: The simplicity threshold
    ax = axes[1]
    ax.set_facecolor('#161b22')
    
    systems_labels = ['Sys 2', 'Sys 3', 'Sys 4', 'Sys 5']
    group_orders = [2, 4, 12, 60]
    is_simple = [True, False, False, True]
    
    bars = ax.bar(range(4), group_orders, color=[C['red'] if s else C['cyan'] for s in is_simple],
                  alpha=0.7, width=0.6)
    
    for i, (order, simple) in enumerate(zip(group_orders, is_simple)):
        label = 'SIMPLE' if simple else 'decomposable'
        color = C['red'] if simple else C['cyan']
        ax.text(i, order + 2, f'{order}', ha='center', fontsize=14,
                fontweight='bold', color=color)
        ax.text(i, order + 8 if order > 20 else order + 1.5, label, ha='center',
                fontsize=9, color=color, style='italic')
    
    ax.set_xticks(range(4))
    ax.set_xticklabels(systems_labels, fontsize=11, fontweight='bold')
    ax.set_ylabel('Group Order', fontsize=12)
    ax.set_yscale('log')
    ax.set_title('Cycle Group Orders (log scale)\nRed = Simple Group',
                 fontsize=13, fontweight='bold', color=C['white'], pad=10)
    
    # Add the simplicity threshold line
    ax.axhline(y=30, color=C['red'], linestyle='--', alpha=0.5, linewidth=1)
    ax.text(3.5, 35, 'Simplicity\nThreshold', fontsize=9, color=C['red'],
            ha='right', style='italic')
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/sys5_fig4_evolution.png', dpi=180)
    plt.close()
    print("  [OK] sys5_fig4_evolution.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 5: The 5 Interlocking Tetrahedra
# ═══════════════════════════════════════════════════════════════════
def fig5_interlocking():
    fig, axes = plt.subplots(1, 5, figsize=(22, 5))
    
    r = 1.8
    angles = [np.pi/2 + 2*np.pi*i/5 for i in range(5)]
    all_verts = [(r*np.cos(a), r*np.sin(a)) for a in angles]
    labels = ['a', 'b', 'c', 'd', 'e']
    vert_colors = [C['cyan'], C['green'], C['pink'], C['orange'], C['purple']]
    
    for removed in range(5):
        ax = axes[removed]
        ax.set_facecolor('#0d1117')
        ax.set_aspect('equal')
        ax.axis('off')
        
        active = [i for i in range(5) if i != removed]
        
        # Draw all edges dimly
        for i in range(5):
            for j in range(i+1, 5):
                if i == removed or j == removed:
                    ax.plot([all_verts[i][0], all_verts[j][0]],
                            [all_verts[i][1], all_verts[j][1]],
                            color=C['gray'], linewidth=0.5, alpha=0.2)
                else:
                    ax.plot([all_verts[i][0], all_verts[j][0]],
                            [all_verts[i][1], all_verts[j][1]],
                            color=vert_colors[removed], linewidth=2, alpha=0.5)
        
        # Fill the tetrahedron
        for combo in combinations(active, 3):
            tri = plt.Polygon([all_verts[c] for c in combo], alpha=0.05,
                               facecolor=vert_colors[removed])
            ax.add_patch(tri)
        
        # Draw vertices
        for i in range(5):
            x, y = all_verts[i]
            if i == removed:
                circle = plt.Circle((x, y), 0.2, facecolor=C['gray'], alpha=0.2,
                                     edgecolor=C['gray'], linewidth=1, linestyle='--')
            else:
                circle = plt.Circle((x, y), 0.25, facecolor=vert_colors[i], alpha=0.5,
                                     edgecolor=vert_colors[i], linewidth=2)
            ax.add_patch(circle)
            ax.text(x, y, labels[i], ha='center', va='center', fontsize=12,
                    fontweight='bold', color='white' if i != removed else C['gray'])
        
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-2.5, 2.5)
        cell_label = '{' + ','.join(labels[i] for i in active) + '}'
        ax.set_title(f'Cell {removed}\n{cell_label}', fontsize=10,
                     fontweight='bold', color=vert_colors[removed], pad=5)
    
    fig.suptitle('The 5 Interlocking Tetrahedral Cells of the Pentachoron\n'
                 'Each cell is a complete System 4 (A_4)',
                 fontsize=14, fontweight='bold', color=C['white'], y=1.02)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/sys5_fig5_interlocking.png', dpi=180,
                bbox_inches='tight')
    plt.close()
    print("  [OK] sys5_fig5_interlocking.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 6: Grand Unified Table (visual)
# ═══════════════════════════════════════════════════════════════════
def fig6_grand_table():
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.set_facecolor('#0d1117')
    ax.axis('off')
    
    # Draw as a visual table
    headers = ['System', 'Polytope', 'Pascal Row', 'Threads', 'Steps',
               'Modes', 'Group', 'Simple?', 'Campbell']
    
    rows = [
        ['Sys 2', 'Digon\n(1-simp)', '[1,2,1]=4', '1', '2',
         'E+R\n(50/50)', 'C_2\n(2)', 'Yes*', 'Polarity'],
        ['Sys 3', 'Triangle\n(2-simp)', '[1,3,3,1]=8', '2', '4',
         'E+R\n(75/25)', 'V_4\n(4)', 'No', 'Structure'],
        ['Sys 4', 'Tetra\n(3-simp)', '[1,4,6,4,1]\n=16', '3', '12',
         'E+R\n(58/42)', 'A_4\n(12)', 'No', 'Exchange'],
        ['Sys 5', 'Penta\n(4-simp)', '[1,5,10,10,\n5,1]=32', '4', '60',
         'E+R+B\n(50/27/23)', 'A_5\n(60)', 'YES!', 'Creativity'],
    ]
    
    row_colors = [C['red'], C['orange'], C['cyan'], C['purple']]
    
    col_widths = [0.08, 0.1, 0.13, 0.07, 0.06, 0.11, 0.09, 0.07, 0.1]
    col_x = [0.02]
    for w in col_widths[:-1]:
        col_x.append(col_x[-1] + w)
    
    y_start = 0.88
    row_height = 0.17
    header_height = 0.06
    
    # Headers
    for j, (header, x) in enumerate(zip(headers, col_x)):
        ax.text(x + col_widths[j]/2, y_start, header, ha='center', va='center',
                fontsize=11, fontweight='bold', color=C['yellow'],
                transform=ax.transAxes)
    
    # Header line
    ax.plot([0.01, 0.99], [y_start - 0.03, y_start - 0.03], color=C['yellow'],
            linewidth=1, transform=ax.transAxes, clip_on=False)
    
    # Data rows
    for i, (row, color) in enumerate(zip(rows, row_colors)):
        y = y_start - header_height - i * row_height - row_height/2
        
        # Row background
        rect = plt.Rectangle((0.01, y - row_height/2 + 0.01), 0.98, row_height - 0.02,
                              facecolor=color, alpha=0.05, transform=ax.transAxes)
        ax.add_patch(rect)
        
        for j, (cell, x) in enumerate(zip(row, col_x)):
            fontcolor = color if j in [0, 6, 7] else C['white']
            fontsize = 10 if j != 7 else 12
            ax.text(x + col_widths[j]/2, y, cell, ha='center', va='center',
                    fontsize=fontsize, color=fontcolor, fontweight='bold' if j in [0,7] else 'normal',
                    transform=ax.transAxes)
    
    # Bottom annotation
    ax.text(0.5, 0.08, 'System 5 crosses the SIMPLICITY THRESHOLD: A_5 is the first non-abelian simple group.',
            ha='center', fontsize=13, color=C['red'], fontweight='bold',
            transform=ax.transAxes,
            bbox=dict(boxstyle='round,pad=0.5', facecolor=C['card'],
                      edgecolor=C['red'], linewidth=2))
    
    ax.text(0.5, 0.02, 'The BRIDGE mode (B) emerges as the structural impossibility of separating E and R within A_5.',
            ha='center', fontsize=11, color=C['bridge'], style='italic',
            transform=ax.transAxes)
    
    ax.set_title('Grand Unified Table: The Simplex Hierarchy of Cognitive Systems',
                 fontsize=16, fontweight='bold', color=C['white'], pad=20)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/sys5_fig6_grand_table.png', dpi=180)
    plt.close()
    print("  [OK] sys5_fig6_grand_table.png")


# ═══════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating System 5 visualizations...")
    fig1_pentachoron()
    fig2_mode_heatmap()
    fig3_extended_chain()
    fig4_mode_evolution()
    fig5_interlocking()
    fig6_grand_table()
    print("Done — 6 System 5 figures saved.")
