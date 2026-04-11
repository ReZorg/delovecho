#!/usr/bin/env python3
"""
hierarchy_viz.py — Visualizations for the full Simplex Hierarchy
System 2 (Digon) -> System 3 (Triangle) -> System 4 (Tetrahedron)
Including subgroup chain and group decomposition diagrams.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
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
}


# ═══════════════════════════════════════════════════════════════════
# Fig 1: The Three Simplices Side by Side
# ═══════════════════════════════════════════════════════════════════
def fig1_three_simplices():
    fig, axes = plt.subplots(1, 3, figsize=(21, 8))
    
    for ax in axes:
        ax.set_facecolor('#0d1117')
        ax.set_aspect('equal')
        ax.axis('off')
    
    # ── System 2: Digon (line segment) ──
    ax = axes[0]
    # Two vertices connected by an edge
    ax.plot([-2, 2], [0, 0], color=C['orange'], linewidth=4, alpha=0.7)
    
    for x, label, color in [(-2, 'a', C['cyan']), (2, 'b', C['green'])]:
        circle = plt.Circle((x, 0), 0.4, facecolor=color, alpha=0.4,
                             edgecolor=color, linewidth=2.5)
        ax.add_patch(circle)
        ax.text(x, 0, label, ha='center', va='center', fontsize=20,
                fontweight='bold', color='white')
    
    # Edge label
    ax.text(0, 0.5, 'ab', ha='center', fontsize=12, color=C['orange'],
            fontweight='bold')
    
    # Nesting
    ax.text(0, -1.5, '((a)b)', ha='center', fontsize=15, color=C['yellow'],
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C['card'],
                      edgecolor=C['border']))
    
    # Mode arrows
    ax.annotate('E', xy=(0.5, -0.6), fontsize=14, color=C['green'],
                fontweight='bold', ha='center')
    ax.annotate('', xy=(1.3, -0.6), xytext=(-1.3, -0.6),
                arrowprops=dict(arrowstyle='->', color=C['green'], lw=2))
    ax.annotate('R', xy=(0.5, -1.0), fontsize=14, color=C['purple'],
                fontweight='bold', ha='center')
    ax.annotate('', xy=(-1.3, -1.0), xytext=(1.3, -1.0),
                arrowprops=dict(arrowstyle='->', color=C['purple'], lw=2))
    
    # Info
    ax.text(0, -2.8, '[1, 2, 1] = 4', ha='center', fontsize=13,
            color=C['white'], fontweight='bold')
    ax.text(0, -3.4, '1 thread | 2 steps | 1E+1R', ha='center',
            fontsize=10, color=C['gray'])
    ax.text(0, -3.9, 'Group: C_2 (order 2)', ha='center',
            fontsize=11, color=C['red'], fontweight='bold')
    
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4.5, 2.5)
    ax.set_title('System 2: Digon\n(1-simplex)', fontsize=14,
                 fontweight='bold', color=C['red'], pad=15)
    
    # ── System 3: Triangle ──
    ax = axes[1]
    r = 2.5
    angles_3 = [np.pi/2, np.pi/2 + 2*np.pi/3, np.pi/2 + 4*np.pi/3]
    verts_3 = [(r*np.cos(a), r*np.sin(a)) for a in angles_3]
    labels_3 = ['a', 'b', 'c']
    colors_3 = [C['cyan'], C['green'], C['pink']]
    
    for i in range(3):
        j = (i + 1) % 3
        ax.plot([verts_3[i][0], verts_3[j][0]],
                [verts_3[i][1], verts_3[j][1]],
                color=C['orange'], linewidth=3, alpha=0.7)
    
    tri = plt.Polygon(verts_3, alpha=0.06, facecolor=C['purple'])
    ax.add_patch(tri)
    
    for (x, y), label, color in zip(verts_3, labels_3, colors_3):
        circle = plt.Circle((x, y), 0.35, facecolor=color, alpha=0.4,
                             edgecolor=color, linewidth=2.5)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=18,
                fontweight='bold', color='white')
    
    ax.text(0, -0.3, '(((a)b)c)', ha='center', fontsize=14, color=C['yellow'],
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C['card'],
                      edgecolor=C['border']))
    
    ax.text(0, -3.2, '[1, 3, 3, 1] = 8', ha='center', fontsize=13,
            color=C['white'], fontweight='bold')
    ax.text(0, -3.8, '2 threads | 4 steps | 3E+1R', ha='center',
            fontsize=10, color=C['gray'])
    ax.text(0, -4.3, 'Group: V_4 (order 4)', ha='center',
            fontsize=11, color=C['orange'], fontweight='bold')
    
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4.9, 4)
    ax.set_title('System 3: Triangle\n(2-simplex)', fontsize=14,
                 fontweight='bold', color=C['orange'], pad=15)
    
    # ── System 4: Tetrahedron ──
    ax = axes[2]
    verts_4 = [(0, 3), (-2.5, -1.2), (2.5, -1.2), (0, 0.5)]
    labels_4 = ['a', 'b', 'c', 'd']
    colors_4 = [C['cyan'], C['green'], C['pink'], C['orange']]
    
    edges = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
    for i, j in edges:
        style = '-' if 3 not in (i,j) else '--'
        ax.plot([verts_4[i][0], verts_4[j][0]],
                [verts_4[i][1], verts_4[j][1]],
                color=C['orange'], linewidth=2.5, alpha=0.6, linestyle=style)
    
    faces = [(0,1,2), (0,1,3), (0,2,3), (1,2,3)]
    fcolors = [C['purple'], C['cyan'], C['green'], C['pink']]
    for indices, fc in zip(faces, fcolors):
        tri = plt.Polygon([verts_4[i] for i in indices], alpha=0.04,
                           facecolor=fc)
        ax.add_patch(tri)
    
    for (x, y), label, color in zip(verts_4, labels_4, colors_4):
        circle = plt.Circle((x, y), 0.3, facecolor=color, alpha=0.4,
                             edgecolor=color, linewidth=2.5)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=16,
                fontweight='bold', color='white')
    
    ax.text(0, -2.5, '((((a)b)c)d)', ha='center', fontsize=14, color=C['yellow'],
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C['card'],
                      edgecolor=C['border']))
    
    ax.text(0, -3.5, '[1, 4, 6, 4, 1] = 16', ha='center', fontsize=13,
            color=C['white'], fontweight='bold')
    ax.text(0, -4.1, '3 threads | 12 steps | 7E+5R', ha='center',
            fontsize=10, color=C['gray'])
    ax.text(0, -4.6, 'Group: A_4 (order 12)', ha='center',
            fontsize=11, color=C['cyan'], fontweight='bold')
    
    ax.set_xlim(-4, 4)
    ax.set_ylim(-5.2, 4.5)
    ax.set_title('System 4: Tetrahedron\n(3-simplex)', fontsize=14,
                 fontweight='bold', color=C['cyan'], pad=15)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/hier_fig1_three_simplices.png', dpi=180)
    plt.close()
    print("  [OK] hier_fig1_three_simplices.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 2: Subgroup Chain Diagram
# ═══════════════════════════════════════════════════════════════════
def fig2_subgroup_chain():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_facecolor('#0d1117')
    
    # Nodes: {e}, C_2, V_4, A_4, T_h
    nodes = [
        (0, 0, '{e}', 1, C['gray'], 'Identity'),
        (0, 2, 'C_2', 2, C['red'], 'System 2: Digon\nThe Primordial Flip'),
        (0, 4, 'V_4', 4, C['orange'], 'System 3: Triangle\nKlein Four-Group'),
        (0, 6, 'A_4', 12, C['cyan'], 'System 4: Tetrahedron\nAlternating Group'),
        (0, 8, 'T_h', 24, C['purple'], 'System 4 + E/R\nPyritohedral Group'),
    ]
    
    # Draw connecting lines
    for i in range(len(nodes) - 1):
        x1, y1 = nodes[i][0], nodes[i][1]
        x2, y2 = nodes[i+1][0], nodes[i+1][1]
        ax.plot([x1, x2], [y1, y2], color=C['border'], linewidth=3, zorder=1)
        
        # Index label on the line
        idx = nodes[i+1][3] // nodes[i][3]
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.6, my, f'index {idx}', fontsize=10, color=C['yellow'],
                fontweight='bold', ha='left', va='center')
    
    # Draw nodes
    for x, y, label, order_val, color, desc in nodes:
        circle = plt.Circle((x, y), 0.55, facecolor=color, alpha=0.2,
                             edgecolor=color, linewidth=3, zorder=2)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=16,
                fontweight='bold', color=color, zorder=3)
        
        # Order
        ax.text(x - 1.5, y, f'|{label}| = {order_val}', ha='right',
                va='center', fontsize=12, color=C['white'], fontweight='bold')
        
        # Description
        ax.text(x + 2.5, y, desc, ha='left', va='center', fontsize=11,
                color=C['gray'])
    
    # Decomposition annotations on the right
    annotations = [
        (6.5, 6, 'A_4 = V_4 >' + ' C_3', C['cyan']),
        (6.5, 5.4, '(4 interfaces) >' + ' (3 threads)', C['gray']),
        (6.5, 8, 'T_h = A_4 x C_2', C['purple']),
        (6.5, 7.4, '(12-step cycle) x (E/R flip)', C['gray']),
    ]
    # Use simpler text to avoid font issues
    ax.text(6.5, 6, 'A_4 = V_4 : C_3', ha='left', va='center',
            fontsize=12, color=C['cyan'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=C['card'],
                      edgecolor=C['cyan'], alpha=0.5))
    ax.text(6.5, 5.3, '= (4 interfaces) : (3 threads)', ha='left',
            va='center', fontsize=10, color=C['gray'])
    
    ax.text(6.5, 8, 'T_h = A_4 x C_2', ha='left', va='center',
            fontsize=12, color=C['purple'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=C['card'],
                      edgecolor=C['purple'], alpha=0.5))
    ax.text(6.5, 7.3, '= (12-step cycle) x (E/R flip)', ha='left',
            va='center', fontsize=10, color=C['gray'])
    
    ax.set_xlim(-4, 12)
    ax.set_ylim(-1, 9.5)
    ax.axis('off')
    ax.set_title('Subgroup Chain: The Nesting of Cognitive Symmetries\n'
                 'C_2  <  V_4  <  A_4  <  T_h',
                 fontsize=15, fontweight='bold', color=C['white'], pad=20)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/hier_fig2_subgroup_chain.png', dpi=180)
    plt.close()
    print("  [OK] hier_fig2_subgroup_chain.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 3: System 2 Digon — The Primordial Oscillation
# ═══════════════════════════════════════════════════════════════════
def fig3_digon():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_facecolor('#0d1117')
    
    # The two states as large circles
    # Step 1: Expressive
    circle_e = plt.Circle((-3, 0), 1.5, facecolor=C['green'], alpha=0.15,
                           edgecolor=C['green'], linewidth=3)
    ax.add_patch(circle_e)
    ax.text(-3, 0.3, 'Step 1', ha='center', fontsize=14, color=C['green'],
            fontweight='bold')
    ax.text(-3, -0.3, 'EXPRESSIVE', ha='center', fontsize=12, color=C['green'])
    ax.text(-3, -0.8, 'Forward / Actual', ha='center', fontsize=10, color=C['gray'])
    ax.text(-3, -1.2, 'Perceive', ha='center', fontsize=10, color=C['gray'],
            style='italic')
    
    # Step 2: Regenerative
    circle_r = plt.Circle((3, 0), 1.5, facecolor=C['purple'], alpha=0.15,
                           edgecolor=C['purple'], linewidth=3)
    ax.add_patch(circle_r)
    ax.text(3, 0.3, 'Step 2', ha='center', fontsize=14, color=C['purple'],
            fontweight='bold')
    ax.text(3, -0.3, 'REGENERATIVE', ha='center', fontsize=12, color=C['purple'])
    ax.text(3, -0.8, 'Backward / Virtual', ha='center', fontsize=10, color=C['gray'])
    ax.text(3, -1.2, 'Reflect', ha='center', fontsize=10, color=C['gray'],
            style='italic')
    
    # Arrows between them
    ax.annotate('', xy=(1.2, 0.5), xytext=(-1.2, 0.5),
                arrowprops=dict(arrowstyle='->', color=C['green'], lw=3,
                                connectionstyle='arc3,rad=0.2'))
    ax.text(0, 1.5, 'sigma', ha='center', fontsize=14, color=C['yellow'],
            fontweight='bold')
    
    ax.annotate('', xy=(-1.2, -0.5), xytext=(1.2, -0.5),
                arrowprops=dict(arrowstyle='->', color=C['purple'], lw=3,
                                connectionstyle='arc3,rad=0.2'))
    ax.text(0, -1.8, 'sigma', ha='center', fontsize=14, color=C['yellow'],
            fontweight='bold')
    
    # Central label
    ax.text(0, 0, 'C_2', ha='center', va='center', fontsize=20,
            color=C['red'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C['card'],
                      edgecolor=C['red'], linewidth=2))
    
    # Bottom annotations
    ax.text(0, -3.5, 'The Primordial Oscillation', ha='center', fontsize=16,
            color=C['white'], fontweight='bold')
    ax.text(0, -4.2, 'sigma^2 = e  |  1E + 1R  |  50% balance  |  ((a)b)',
            ha='center', fontsize=12, color=C['gray'])
    ax.text(0, -4.8, 'Every polar pair [s(p)] in every system is a copy of this C_2 flip',
            ha='center', fontsize=11, color=C['yellow'], style='italic')
    
    ax.set_xlim(-6, 6)
    ax.set_ylim(-5.5, 3)
    ax.axis('off')
    ax.set_title('System 2: The Digon — Perceptual Shift Transformation\n'
                 '1-simplex | [1, 2, 1] | base[3] -> (2)(1)',
                 fontsize=15, fontweight='bold', color=C['red'], pad=20)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/hier_fig3_digon.png', dpi=180)
    plt.close()
    print("  [OK] hier_fig3_digon.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 4: Group Decomposition Tree
# ═══════════════════════════════════════════════════════════════════
def fig4_decomposition():
    fig, ax = plt.subplots(figsize=(18, 10))
    ax.set_facecolor('#0d1117')
    
    # T_h at top, decomposing down
    # T_h = A_4 x C_2
    #   A_4 = V_4 : C_3
    #     V_4 = C_2 x C_2
    
    def draw_node(x, y, text, order_val, color, size=0.6):
        circle = plt.Circle((x, y), size, facecolor=color, alpha=0.15,
                             edgecolor=color, linewidth=2.5)
        ax.add_patch(circle)
        ax.text(x, y + 0.1, text, ha='center', va='center', fontsize=14,
                fontweight='bold', color=color)
        ax.text(x, y - 0.3, f'|{order_val}|', ha='center', va='center',
                fontsize=10, color=C['gray'])
    
    def draw_edge(x1, y1, x2, y2, label='', color=C['border']):
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=2, zorder=1)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx + 0.3, my, label, fontsize=10, color=C['yellow'],
                    fontweight='bold', ha='left', va='center')
    
    # Level 0: T_h
    draw_node(0, 8, 'T_h', 24, C['purple'], 0.7)
    ax.text(2, 8, 'Pyritohedral Group', ha='left', fontsize=12,
            color=C['purple'], fontweight='bold')
    ax.text(2, 7.5, 'Full System 4 + E/R', ha='left', fontsize=10,
            color=C['gray'])
    
    # Level 1: A_4 and C_2
    draw_edge(0, 7.3, -3, 6.2, 'x')
    draw_edge(0, 7.3, 3, 6.2, 'x')
    
    draw_node(-3, 5.5, 'A_4', 12, C['cyan'], 0.6)
    ax.text(-5.5, 5.5, 'Alternating Group', ha='left', fontsize=11,
            color=C['cyan'], fontweight='bold')
    ax.text(-5.5, 5.0, '12-step cycle', ha='left', fontsize=10,
            color=C['gray'])
    
    draw_node(3, 5.5, 'C_2', 2, C['red'], 0.5)
    ax.text(4.5, 5.5, 'E/R Duality', ha='left', fontsize=11,
            color=C['red'], fontweight='bold')
    ax.text(4.5, 5.0, 'System 2 (Digon)', ha='left', fontsize=10,
            color=C['gray'])
    
    # Level 2: V_4 and C_3
    draw_edge(-3, 4.9, -5, 3.7, ':')
    draw_edge(-3, 4.9, -1, 3.7, ':')
    
    draw_node(-5, 3, 'V_4', 4, C['orange'], 0.55)
    ax.text(-7.5, 3, 'Klein Four', ha='left', fontsize=11,
            color=C['orange'], fontweight='bold')
    ax.text(-7.5, 2.5, '4 interfaces', ha='left', fontsize=10,
            color=C['gray'])
    
    draw_node(-1, 3, 'C_3', 3, C['green'], 0.5)
    ax.text(0.5, 3, 'Cyclic (3)', ha='left', fontsize=11,
            color=C['green'], fontweight='bold')
    ax.text(0.5, 2.5, '3 threads', ha='left', fontsize=10,
            color=C['gray'])
    
    # Level 3: V_4 = C_2 x C_2
    draw_edge(-5, 2.45, -6.5, 1.2)
    draw_edge(-5, 2.45, -3.5, 1.2)
    
    draw_node(-6.5, 0.5, 'C_2', 2, C['red'], 0.45)
    ax.text(-6.5, -0.2, 'Pair [1(8)]', ha='center', fontsize=9,
            color=C['gray'])
    
    draw_node(-3.5, 0.5, 'C_2', 2, C['red'], 0.45)
    ax.text(-3.5, -0.2, 'Pair [4(5)]', ha='center', fontsize=9,
            color=C['gray'])
    
    # Note: V_4 has 3 copies of C_2, show the third
    ax.text(-5, -0.8, '(V_4 contains 3 copies of C_2,', ha='center',
            fontsize=9, color=C['gray'], style='italic')
    ax.text(-5, -1.2, 'one per polar pair: [1(8)], [4(5)], [7(2)])',
            ha='center', fontsize=9, color=C['gray'], style='italic')
    
    # The key equation at the bottom
    ax.text(0, -2.5, 'T_h  =  ( V_4  :  C_3 )  x  C_2  =  A_4  x  C_2',
            ha='center', fontsize=16, color=C['white'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=C['card'],
                      edgecolor=C['yellow'], linewidth=2))
    ax.text(0, -3.3, '24  =  ( 4  x  3 )  x  2  =  12  x  2',
            ha='center', fontsize=13, color=C['yellow'], fontweight='bold')
    
    ax.set_xlim(-9, 8)
    ax.set_ylim(-4, 9.5)
    ax.axis('off')
    ax.set_title('Group Decomposition Tree\n'
                 'T_h = (V_4 : C_3) x C_2 = A_4 x C_2',
                 fontsize=15, fontweight='bold', color=C['white'], pad=20)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/hier_fig4_decomposition.png', dpi=180)
    plt.close()
    print("  [OK] hier_fig4_decomposition.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 5: All Three Step Sequences Stacked
# ═══════════════════════════════════════════════════════════════════
def fig5_all_sequences():
    fig, axes = plt.subplots(3, 1, figsize=(18, 12))
    
    MODE_COLORS = {'E': '#3fb950', 'R': '#bc8cff'}
    
    # System 2
    ax = axes[0]
    ax.set_facecolor('#161b22')
    terms_2a = [1, 1]
    modes_2a = ['E', 'R']
    
    for col in range(2):
        color = MODE_COLORS[modes_2a[col]]
        alpha = 0.7 if modes_2a[col] == 'E' else 0.4
        rect = plt.Rectangle((col, 0), 1, 1, facecolor=color, alpha=alpha,
                              edgecolor=C['border'], linewidth=2)
        ax.add_patch(rect)
        ax.text(col + 0.5, 0.6, f'T{terms_2a[col]}', ha='center', va='center',
                fontsize=16, fontweight='bold', color=C['white'])
        ax.text(col + 0.5, 0.3, modes_2a[col], ha='center', va='center',
                fontsize=13, color=C['white'], alpha=0.8)
    
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.3, 1.5)
    ax.set_yticks([0.5])
    ax.set_yticklabels(['Set 2A'], fontsize=12, fontweight='bold')
    ax.set_xticks([i + 0.5 for i in range(2)])
    ax.set_xticklabels([f'{i+1}' for i in range(2)], fontsize=10)
    ax.set_title('System 2: Digon | C_2 | 1 thread x 2 steps | 1E+1R (50% R)',
                 fontsize=13, fontweight='bold', color=C['red'], pad=10)
    
    # System 3
    ax = axes[1]
    ax.set_facecolor('#161b22')
    
    sys3_data = {
        'Set 3A': ([1, 3, 1, 3], ['R', 'E', 'E', 'E']),
        'Set 3B': ([3, 1, 3, 1], ['E', 'E', 'E', 'R']),
    }
    
    for row, (name, (terms, modes)) in enumerate(sys3_data.items()):
        for col in range(4):
            color = MODE_COLORS[modes[col]]
            alpha = 0.7 if modes[col] == 'E' else 0.4
            rect = plt.Rectangle((col, 1-row), 1, 1, facecolor=color, alpha=alpha,
                                  edgecolor=C['border'], linewidth=2)
            ax.add_patch(rect)
            ax.text(col + 0.5, 1-row + 0.6, f'T{terms[col]}', ha='center',
                    va='center', fontsize=14, fontweight='bold', color=C['white'])
            ax.text(col + 0.5, 1-row + 0.3, modes[col], ha='center',
                    va='center', fontsize=11, color=C['white'], alpha=0.8)
    
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.3, 2.3)
    ax.set_yticks([0.5, 1.5])
    ax.set_yticklabels(['Set 3B', 'Set 3A'], fontsize=12, fontweight='bold')
    ax.set_xticks([i + 0.5 for i in range(4)])
    ax.set_xticklabels([f'{i+1}' for i in range(4)], fontsize=10)
    ax.set_title('System 3: Triangle | V_4 | 2 threads x 4 steps | 3E+1R (25% R)',
                 fontsize=13, fontweight='bold', color=C['orange'], pad=10)
    
    # System 4
    ax = axes[2]
    ax.set_facecolor('#161b22')
    
    sys4_data = {
        'Set A': ([4,2,8,5,7,1,4,2,8,5,7,1], ['R','R','E','E','E','E','E','E','E','R','R','R']),
        'Set B': ([8,5,7,1,4,2,8,5,7,1,4,2], ['E','R','R','R','R','R','E','E','E','E','E','E']),
        'Set C': ([7,1,4,2,8,5,7,1,4,2,8,5], ['E','E','E','E','E','R','R','R','R','R','E','E']),
    }
    
    for row, (name, (terms, modes)) in enumerate(sys4_data.items()):
        for col in range(12):
            color = MODE_COLORS[modes[col]]
            alpha = 0.7 if modes[col] == 'E' else 0.4
            rect = plt.Rectangle((col, 2-row), 1, 1, facecolor=color, alpha=alpha,
                                  edgecolor=C['border'], linewidth=1.5)
            ax.add_patch(rect)
            ax.text(col + 0.5, 2-row + 0.6, f'{terms[col]}', ha='center',
                    va='center', fontsize=12, fontweight='bold', color=C['white'])
            ax.text(col + 0.5, 2-row + 0.3, modes[col], ha='center',
                    va='center', fontsize=9, color=C['white'], alpha=0.8)
    
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.3, 3.3)
    ax.set_yticks([0.5, 1.5, 2.5])
    ax.set_yticklabels(['Set C', 'Set B', 'Set A'], fontsize=12, fontweight='bold')
    ax.set_xticks([i + 0.5 for i in range(12)])
    ax.set_xticklabels([f'{i+1}' for i in range(12)], fontsize=10)
    ax.set_title('System 4: Tetrahedron | A_4 | 3 threads x 12 steps | 7E+5R (42% R)',
                 fontsize=13, fontweight='bold', color=C['cyan'], pad=10)
    
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/hier_fig5_all_sequences.png', dpi=180)
    plt.close()
    print("  [OK] hier_fig5_all_sequences.png")


# ═══════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating Hierarchy visualizations...")
    fig1_three_simplices()
    fig2_subgroup_chain()
    fig3_digon()
    fig4_decomposition()
    fig5_all_sequences()
    print("Done — 5 hierarchy figures saved.")
