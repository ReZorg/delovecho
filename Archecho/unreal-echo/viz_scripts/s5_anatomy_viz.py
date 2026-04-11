#!/usr/bin/env python3
"""
s5_anatomy_viz.py — Visualizations for System 5's 7 partitions,
2x2 nested convolution, and hierarchical nesting.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as FancyBboxPatch
import numpy as np
from itertools import combinations

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

V_labels = ['a', 'b', 'c', 'd', 'e']

# Pentachoron vertex positions (projected from 4D to 2D)
# Use a regular pentagon layout
angles = [2 * np.pi * i / 5 - np.pi / 2 for i in range(5)]
VPOS = {v: (3 * np.cos(a), 3 * np.sin(a)) for v, a in zip(V_labels, angles)}


# ═══════════════════════════════════════════════════════════════════
# Fig 1: The 7 Partitions Overview
# ═══════════════════════════════════════════════════════════════════
def fig1_partitions():
    fig, ax = plt.subplots(figsize=(22, 14))
    ax.set_facecolor('#0d1117')
    ax.axis('off')

    # Title
    ax.text(11, 13.5, 'The 7 Partitions of System 5', ha='center',
            fontsize=20, fontweight='bold', color=C['white'])
    ax.text(11, 12.8, '3 Universal (Structural) + 4 Particular (Operational)',
            ha='center', fontsize=13, color=C['yellow'])

    # Universal partitions (left column)
    ax.text(4, 11.5, 'UNIVERSAL', ha='center', fontsize=16, fontweight='bold',
            color=C['cyan'])
    ax.text(4, 11.0, '(What the system IS)', ha='center', fontsize=11, color=C['gray'])

    u_data = [
        ('U1', 'PENTAD', '4-face', '1', 'Unity — holds ALL 5 vertices', C['teal']),
        ('U2', 'TETRADS', '3-faces', '5', '5 System 4 cells (organs)', C['cyan']),
        ('U3', 'DYADS', '1-faces', '10', '10 polar pairs (C_2 oscillations)', C['purple']),
    ]

    for i, (code, name, kface, count, desc, color) in enumerate(u_data):
        y = 9.5 - i * 3
        rect = plt.Rectangle((0.5, y - 0.8), 7, 2.2, facecolor=color, alpha=0.08,
                              edgecolor=color, linewidth=2, 
                              linestyle='-')
        ax.add_patch(rect)
        ax.text(1.2, y + 0.8, f'{code}: {name}', fontsize=14, fontweight='bold', color=color)
        ax.text(1.2, y + 0.1, f'{kface}  |  Count: {count}', fontsize=11, color=C['white'])
        ax.text(1.2, y - 0.5, desc, fontsize=10, color=C['gray'])

    # Particular partitions (right column)
    ax.text(16, 11.5, 'PARTICULAR', ha='center', fontsize=16, fontweight='bold',
            color=C['orange'])
    ax.text(16, 11.0, '(How the system RUNS)', ha='center', fontsize=11, color=C['gray'])

    p_data = [
        ('P1', 'VERTICES', '0-faces', '5', 'Interfaces — dual surfaces', C['orange']),
        ('P2', 'TRIADS', '2-faces', '10', 'System 3 faces (shared bonds)', C['pink']),
        ('P3', 'THREADS', 'channels', '4', 'Concurrent execution paths', C['green']),
        ('P4', 'ORIENTATIONS', 'pentad pair', '2', 'E/R — somatic/autonomic', C['red']),
    ]

    for i, (code, name, kface, count, desc, color) in enumerate(p_data):
        y = 9.5 - i * 2.5
        rect = plt.Rectangle((12.5, y - 0.5), 7, 1.8, facecolor=color, alpha=0.08,
                              edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        ax.text(13.2, y + 0.7, f'{code}: {name}', fontsize=14, fontweight='bold', color=color)
        ax.text(13.2, y + 0.0, f'{kface}  |  Count: {count}', fontsize=11, color=C['white'])
        ax.text(13.2, y - 0.4, desc, fontsize=10, color=C['gray'])

    # Bottom: p(5) = 7
    ax.text(11, 1.5, 'p(5) = 7 = number of integer partitions of 5',
            ha='center', fontsize=14, fontweight='bold', color=C['bridge'],
            bbox=dict(boxstyle='round,pad=0.5', facecolor=C['card'],
                      edgecolor=C['bridge'], linewidth=2))
    ax.text(11, 0.7, 'S2: p(2)=2  |  S3: p(3)=3  |  S4: p(4)=5  |  S5: p(5)=7',
            ha='center', fontsize=12, color=C['yellow'])

    ax.set_xlim(-0.5, 22)
    ax.set_ylim(0, 14.5)
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/anat_fig1_partitions.png', dpi=180)
    plt.close()
    print("  [OK] anat_fig1_partitions.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 2: The 2x2 Nested Convolution
# ═══════════════════════════════════════════════════════════════════
def fig2_convolution():
    fig, ax = plt.subplots(figsize=(20, 14))
    ax.set_facecolor('#0d1117')
    ax.axis('off')

    ax.text(10, 13, 'The 2x2 Nested Convolution', ha='center',
            fontsize=20, fontweight='bold', color=C['white'])
    ax.text(10, 12.3, 'Orthogonal Pentad Pair: Somatic (E) | Autonomic (R)',
            ha='center', fontsize=13, color=C['yellow'])

    # Outer box
    outer = plt.Rectangle((1, 2), 18, 9.5, facecolor=C['white'], alpha=0.02,
                           edgecolor=C['white'], linewidth=2, linestyle='--')
    ax.add_patch(outer)
    ax.text(10, 11, 'PENTAD PAIR  (C_2: E/R duality)', ha='center',
            fontsize=12, color=C['white'], fontweight='bold')

    # Left pentad: Expressive (Somatic)
    left = plt.Rectangle((1.5, 2.5), 8, 8, facecolor=C['green'], alpha=0.04,
                          edgecolor=C['green'], linewidth=2)
    ax.add_patch(left)
    ax.text(5.5, 10, 'EXPRESSIVE PENTAD', ha='center', fontsize=14,
            fontweight='bold', color=C['green'])
    ax.text(5.5, 9.3, '(Somatic — Forward Pass)', ha='center',
            fontsize=11, color=C['green'], alpha=0.7)

    # Thread A
    ta = plt.Rectangle((2, 3), 3.2, 5.5, facecolor=C['cyan'], alpha=0.06,
                        edgecolor=C['cyan'], linewidth=1.5)
    ax.add_patch(ta)
    ax.text(3.6, 8, 'Thread A', ha='center', fontsize=13, fontweight='bold', color=C['cyan'])
    ax.text(3.6, 7.3, '0 deg', ha='center', fontsize=11, color=C['cyan'], alpha=0.7)
    ax.text(3.6, 6.2, 'Perceive', ha='center', fontsize=11, color=C['white'])
    ax.text(3.6, 5.4, 'Cell 1 -> 5', ha='center', fontsize=10, color=C['gray'])
    ax.text(3.6, 4.6, '-> 4 -> 2', ha='center', fontsize=10, color=C['gray'])
    ax.text(3.6, 3.8, '-> 3', ha='center', fontsize=10, color=C['gray'])

    # Thread B
    tb = plt.Rectangle((5.8, 3), 3.2, 5.5, facecolor=C['green'], alpha=0.06,
                        edgecolor=C['green'], linewidth=1.5)
    ax.add_patch(tb)
    ax.text(7.4, 8, 'Thread B', ha='center', fontsize=13, fontweight='bold', color=C['green'])
    ax.text(7.4, 7.3, '90 deg', ha='center', fontsize=11, color=C['green'], alpha=0.7)
    ax.text(7.4, 6.2, 'Act', ha='center', fontsize=11, color=C['white'])
    ax.text(7.4, 5.4, 'Cell 2 -> 1', ha='center', fontsize=10, color=C['gray'])
    ax.text(7.4, 4.6, '-> 5 -> 3', ha='center', fontsize=10, color=C['gray'])
    ax.text(7.4, 3.8, '-> 4', ha='center', fontsize=10, color=C['gray'])

    # Inner convolution arrow
    ax.annotate('', xy=(5.6, 5.5), xytext=(5.2, 5.5),
                arrowprops=dict(arrowstyle='<->', color=C['yellow'], lw=2))
    ax.text(5.4, 5.0, 'A ⊛ B', ha='center', fontsize=10, color=C['yellow'], fontweight='bold')

    # Right pentad: Regenerative (Autonomic)
    right = plt.Rectangle((10.5, 2.5), 8, 8, facecolor=C['purple'], alpha=0.04,
                           edgecolor=C['purple'], linewidth=2)
    ax.add_patch(right)
    ax.text(14.5, 10, 'REGENERATIVE PENTAD', ha='center', fontsize=14,
            fontweight='bold', color=C['purple'])
    ax.text(14.5, 9.3, '(Autonomic — Backward Pass)', ha='center',
            fontsize=11, color=C['purple'], alpha=0.7)

    # Thread C
    tc = plt.Rectangle((11, 3), 3.2, 5.5, facecolor=C['pink'], alpha=0.06,
                        edgecolor=C['pink'], linewidth=1.5)
    ax.add_patch(tc)
    ax.text(12.6, 8, 'Thread C', ha='center', fontsize=13, fontweight='bold', color=C['pink'])
    ax.text(12.6, 7.3, '180 deg', ha='center', fontsize=11, color=C['pink'], alpha=0.7)
    ax.text(12.6, 6.2, 'Simulate', ha='center', fontsize=11, color=C['white'])
    ax.text(12.6, 5.4, 'Cell 3 -> 2', ha='center', fontsize=10, color=C['gray'])
    ax.text(12.6, 4.6, '-> 1 -> 4', ha='center', fontsize=10, color=C['gray'])
    ax.text(12.6, 3.8, '-> 5', ha='center', fontsize=10, color=C['gray'])

    # Thread D
    td = plt.Rectangle((14.8, 3), 3.2, 5.5, facecolor=C['orange'], alpha=0.06,
                        edgecolor=C['orange'], linewidth=1.5)
    ax.add_patch(td)
    ax.text(16.4, 8, 'Thread D', ha='center', fontsize=13, fontweight='bold', color=C['orange'])
    ax.text(16.4, 7.3, '270 deg', ha='center', fontsize=11, color=C['orange'], alpha=0.7)
    ax.text(16.4, 6.2, 'Recall', ha='center', fontsize=11, color=C['white'])
    ax.text(16.4, 5.4, 'Cell 4 -> 3', ha='center', fontsize=10, color=C['gray'])
    ax.text(16.4, 4.6, '-> 2 -> 5', ha='center', fontsize=10, color=C['gray'])
    ax.text(16.4, 3.8, '-> 1', ha='center', fontsize=10, color=C['gray'])

    # Inner convolution arrow
    ax.annotate('', xy=(14.6, 5.5), xytext=(14.2, 5.5),
                arrowprops=dict(arrowstyle='<->', color=C['yellow'], lw=2))
    ax.text(14.4, 5.0, 'C ⊛ D', ha='center', fontsize=10, color=C['yellow'], fontweight='bold')

    # Outer convolution
    ax.annotate('', xy=(10.2, 6.5), xytext=(9.8, 6.5),
                arrowprops=dict(arrowstyle='<->', color=C['bridge'], lw=3))
    ax.text(10, 7.2, '(A⊛B) ⊛ (C⊛D)', ha='center', fontsize=12,
            color=C['bridge'], fontweight='bold')

    # Bottom: V_4 identity
    ax.text(10, 1.2, 'C_2 (E/R) ⊗ C_2 (L/R) = V_4 = System 3\'s cycle group',
            ha='center', fontsize=14, fontweight='bold', color=C['bridge'],
            bbox=dict(boxstyle='round,pad=0.5', facecolor=C['card'],
                      edgecolor=C['bridge'], linewidth=2))

    ax.set_xlim(0, 20)
    ax.set_ylim(0.5, 14)
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/anat_fig2_convolution.png', dpi=180)
    plt.close()
    print("  [OK] anat_fig2_convolution.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 3: The Hierarchical Nesting (Pentad -> Tetrad -> Triad -> Dyad)
# ═══════════════════════════════════════════════════════════════════
def fig3_nesting():
    fig, ax = plt.subplots(figsize=(20, 14))
    ax.set_facecolor('#0d1117')
    ax.axis('off')

    ax.text(10, 13.5, 'Hierarchical Nesting: Pentad -> Tetrad -> Triad -> Dyad',
            ha='center', fontsize=18, fontweight='bold', color=C['white'])

    levels = [
        ('PENTAD', '{abcde}', 1, C['teal'], 'S5: 4-simplex'),
        ('TETRADS', '{abcd} {abce} {abde} {acde} {bcde}', 5, C['cyan'], 'S4: 3-simplex'),
        ('TRIADS', '10 triangular faces', 10, C['pink'], 'S3: 2-simplex'),
        ('DYADS', '10 edges (polar pairs)', 10, C['purple'], 'S2: 1-simplex'),
        ('VERTICES', '{a} {b} {c} {d} {e}', 5, C['orange'], 'S1: 0-simplex'),
    ]

    for i, (name, elements, count, color, system) in enumerate(levels):
        y = 11.5 - i * 2.5
        w = 16 - i * 1.5
        x = 10 - w / 2

        rect = plt.Rectangle((x, y - 0.6), w, 1.8, facecolor=color, alpha=0.08,
                              edgecolor=color, linewidth=2)
        ax.add_patch(rect)

        ax.text(10, y + 0.7, f'{name} ({count})', ha='center', fontsize=14,
                fontweight='bold', color=color)
        ax.text(10, y + 0.0, elements, ha='center', fontsize=10, color=C['white'])
        ax.text(10, y - 0.5, system, ha='center', fontsize=10, color=C['gray'])

        # Containment arrows
        if i < 4:
            contains = [5, 4, 3, 2][i]
            ax.annotate('', xy=(10, y - 0.7), xytext=(10, y - 1.3),
                        arrowprops=dict(arrowstyle='->', color=C['white'], lw=1.5))
            ax.text(11.5, y - 1.1, f'contains {contains} each', fontsize=9,
                    color=C['yellow'], ha='left')

    # Right side: containment numbers
    ax.text(18, 11, 'Containment', ha='center', fontsize=13, fontweight='bold', color=C['yellow'])
    ax.text(18, 10.3, '1 pentad', ha='center', fontsize=11, color=C['teal'])
    ax.text(18, 9.6, 'contains 5 tetrads', ha='center', fontsize=11, color=C['cyan'])
    ax.text(18, 8.9, 'each has 4 triads', ha='center', fontsize=11, color=C['pink'])
    ax.text(18, 8.2, 'each has 3 dyads', ha='center', fontsize=11, color=C['purple'])
    ax.text(18, 7.5, 'each has 2 vertices', ha='center', fontsize=11, color=C['orange'])
    ax.text(18, 6.5, '5 x 4 x 3 x 2 = 120', ha='center', fontsize=13,
            fontweight='bold', color=C['bridge'])
    ax.text(18, 5.8, '= |S_5| = 5!', ha='center', fontsize=12, color=C['bridge'])

    ax.set_xlim(0, 20)
    ax.set_ylim(0, 14.5)
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/anat_fig3_nesting.png', dpi=180)
    plt.close()
    print("  [OK] anat_fig3_nesting.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 4: The 5 Tetrahedral Cells with Rotating Shadow
# ═══════════════════════════════════════════════════════════════════
def fig4_rotating_shadow():
    fig, axes = plt.subplots(1, 5, figsize=(25, 6))

    V_set = {'a', 'b', 'c', 'd', 'e'}
    colors_v = {'a': C['cyan'], 'b': C['green'], 'c': C['pink'],
                'd': C['orange'], 'e': C['purple']}

    for idx, focal in enumerate(V_labels):
        ax = axes[idx]
        ax.set_facecolor('#0d1117')
        ax.set_aspect('equal')
        ax.axis('off')

        shadow_tet = V_set - {focal}
        active_verts = list(V_set)

        # Draw all edges
        for v1, v2 in combinations(V_labels, 2):
            x1, y1 = VPOS[v1]
            x2, y2 = VPOS[v2]
            if v1 == focal or v2 == focal:
                # Edges to focal vertex: highlighted
                ax.plot([x1, x2], [y1, y2], color=C['yellow'], linewidth=2.5, alpha=0.6)
            else:
                # Shadow tetrad edges: dimmed
                ax.plot([x1, x2], [y1, y2], color=C['border'], linewidth=1, alpha=0.3)

        # Draw vertices
        for v in V_labels:
            x, y = VPOS[v]
            if v == focal:
                circle = plt.Circle((x, y), 0.45, facecolor=C['yellow'], alpha=0.5,
                                    edgecolor=C['yellow'], linewidth=3)
                ax.add_patch(circle)
                ax.text(x, y, v.upper(), ha='center', va='center', fontsize=14,
                        fontweight='bold', color='white')
            else:
                circle = plt.Circle((x, y), 0.35, facecolor=colors_v[v], alpha=0.3,
                                    edgecolor=colors_v[v], linewidth=2)
                ax.add_patch(circle)
                ax.text(x, y, v, ha='center', va='center', fontsize=12,
                        fontweight='bold', color='white')

        shadow_label = ''.join(sorted(shadow_tet))
        ax.set_title(f'Focal: {focal}\nShadow: {shadow_label}', fontsize=11,
                     fontweight='bold', color=C['yellow'], pad=10)
        ax.text(0, -4.2, f'4 active tetrads\n(contain {focal})', ha='center',
                fontsize=9, color=C['gray'])
        ax.set_xlim(-4.5, 4.5)
        ax.set_ylim(-5, 4.5)

    fig.suptitle('Rotating Shadow: 4/5 Tetrads Active at Each Focal Vertex',
                 fontsize=16, fontweight='bold', color=C['white'], y=1.02)
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/anat_fig4_shadow.png', dpi=180, bbox_inches='tight')
    plt.close()
    print("  [OK] anat_fig4_shadow.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 5: Edge-Face Duality (10 dyads <-> 10 triads)
# ═══════════════════════════════════════════════════════════════════
def fig5_duality():
    fig, ax = plt.subplots(figsize=(18, 12))
    ax.set_facecolor('#0d1117')
    ax.axis('off')

    ax.text(9, 11, 'Edge-Face Duality: Each Dyad Pairs with a Complementary Triad',
            ha='center', fontsize=16, fontweight='bold', color=C['white'])
    ax.text(9, 10.3, 'Together they span all 5 vertices: edge (2) + face (3) = pentad (5)',
            ha='center', fontsize=12, color=C['yellow'])

    V_set = frozenset(V_labels)
    edges = list(combinations(V_labels, 2))

    for i, (v1, v2) in enumerate(edges):
        edge_set = frozenset({v1, v2})
        complement = V_set - edge_set
        comp_label = ''.join(sorted(complement))

        row = i // 5
        col = i % 5
        x = 1.5 + col * 3.5
        y = 8 - row * 4.5

        # Edge box
        rect_e = plt.Rectangle((x - 0.8, y + 0.8), 1.6, 1.2, facecolor=C['purple'], alpha=0.12,
                                edgecolor=C['purple'], linewidth=1.5)
        ax.add_patch(rect_e)
        ax.text(x, y + 1.4, f'{v1}-{v2}', ha='center', fontsize=13,
                fontweight='bold', color=C['purple'])
        ax.text(x, y + 0.9, 'dyad', ha='center', fontsize=8, color=C['gray'])

        # Arrow
        ax.annotate('', xy=(x, y + 0.5), xytext=(x, y + 0.8),
                    arrowprops=dict(arrowstyle='<->', color=C['bridge'], lw=1.5))

        # Face box
        rect_f = plt.Rectangle((x - 0.8, y - 0.8), 1.6, 1.2, facecolor=C['pink'], alpha=0.12,
                                edgecolor=C['pink'], linewidth=1.5)
        ax.add_patch(rect_f)
        ax.text(x, y - 0.2, comp_label, ha='center', fontsize=13,
                fontweight='bold', color=C['pink'])
        ax.text(x, y - 0.7, 'triad', ha='center', fontsize=8, color=C['gray'])

    ax.text(9, 2.5, '10 dyads <-> 10 triads: perfect duality',
            ha='center', fontsize=14, fontweight='bold', color=C['bridge'],
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C['card'],
                      edgecolor=C['bridge'], linewidth=2))
    ax.text(9, 1.8, 'This is the pentachoral self-duality: the 4-simplex is self-dual',
            ha='center', fontsize=11, color=C['gray'])

    ax.set_xlim(-0.5, 18.5)
    ax.set_ylim(1, 12)
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/anat_fig5_duality.png', dpi=180)
    plt.close()
    print("  [OK] anat_fig5_duality.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 6: The Complete Pentachoron with all k-faces labeled
# ═══════════════════════════════════════════════════════════════════
def fig6_pentachoron():
    fig, ax = plt.subplots(figsize=(14, 14))
    ax.set_facecolor('#0d1117')
    ax.set_aspect('equal')
    ax.axis('off')

    ax.text(0, 5, 'The Pentachoron: Complete K_5 Graph',
            ha='center', fontsize=16, fontweight='bold', color=C['white'])
    ax.text(0, 4.4, '5 vertices, 10 edges, 10 faces, 5 cells, 1 hypercell',
            ha='center', fontsize=11, color=C['yellow'])

    colors_v = {'a': C['cyan'], 'b': C['green'], 'c': C['pink'],
                'd': C['orange'], 'e': C['purple']}

    # Draw all 10 triangular faces as filled polygons (very faint)
    for v1, v2, v3 in combinations(V_labels, 3):
        pts = [VPOS[v1], VPOS[v2], VPOS[v3]]
        tri = plt.Polygon(pts, fill=True, facecolor=C['white'], alpha=0.015,
                          edgecolor='none')
        ax.add_patch(tri)

    # Draw all 10 edges
    for v1, v2 in combinations(V_labels, 2):
        x1, y1 = VPOS[v1]
        x2, y2 = VPOS[v2]
        # Color by which tetrad they DON'T belong to
        ax.plot([x1, x2], [y1, y2], color=C['white'], linewidth=1.5, alpha=0.3)
        # Label at midpoint
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        # Offset label slightly outward
        cx, cy = 0, 0
        dx, dy = mx - cx, my - cy
        norm = np.sqrt(dx**2 + dy**2) + 0.001
        ox, oy = mx + dx / norm * 0.3, my + dy / norm * 0.3
        ax.text(ox, oy, f'{v1}{v2}', ha='center', va='center', fontsize=7,
                color=C['purple'], alpha=0.7)

    # Draw vertices
    for v in V_labels:
        x, y = VPOS[v]
        circle = plt.Circle((x, y), 0.4, facecolor=colors_v[v], alpha=0.4,
                             edgecolor=colors_v[v], linewidth=3)
        ax.add_patch(circle)
        ax.text(x, y, v.upper(), ha='center', va='center', fontsize=16,
                fontweight='bold', color='white')

    # Label the 5 tetrahedral cells around the outside
    for v in V_labels:
        x, y = VPOS[v]
        # The tetrad OPPOSITE this vertex
        opp = ''.join(sorted(set(V_labels) - {v}))
        ox, oy = x * 1.5, y * 1.5
        ax.text(ox, oy, f'Cell: {opp}', ha='center', va='center', fontsize=9,
                color=colors_v[v], fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor=C['card'],
                          edgecolor=colors_v[v], alpha=0.8))
        ax.annotate('', xy=(x * 1.15, y * 1.15), xytext=(ox * 0.85, oy * 0.85),
                    arrowprops=dict(arrowstyle='->', color=colors_v[v], lw=1, alpha=0.5))

    ax.set_xlim(-5.5, 5.5)
    ax.set_ylim(-5, 6)
    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/anat_fig6_pentachoron.png', dpi=180)
    plt.close()
    print("  [OK] anat_fig6_pentachoron.png")


# ═══════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating System 5 anatomy visualizations...")
    fig1_partitions()
    fig2_convolution()
    fig3_nesting()
    fig4_rotating_shadow()
    fig5_duality()
    fig6_pentachoron()
    print("Done — 6 anatomy figures saved.")
