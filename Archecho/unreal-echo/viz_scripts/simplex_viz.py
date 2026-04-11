#!/usr/bin/env python3
"""
simplex_viz.py — Visualizations for the Simplex Polytope Hierarchy
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import math

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
    'yellow': '#e3b341', 'gray': '#8b949e', 'white': '#c9d1d9',
    'bg': '#0d1117', 'card': '#161b22', 'border': '#30363d',
}


# ═══════════════════════════════════════════════════════════════════
# Fig 1: System 3 Triangle + System 4 Tetrahedron side by side
# ═══════════════════════════════════════════════════════════════════
def fig1_simplices():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))

    # ── System 3: Triangle ──
    ax1.set_facecolor('#0d1117')
    # Equilateral triangle vertices
    angles_3 = [np.pi/2, np.pi/2 + 2*np.pi/3, np.pi/2 + 4*np.pi/3]
    r = 3.0
    verts_3 = [(r*np.cos(a), r*np.sin(a)) for a in angles_3]
    labels_3 = ['a', 'b', 'c']
    colors_3 = [C['cyan'], C['green'], C['pink']]

    # Draw edges
    for i in range(3):
        j = (i + 1) % 3
        ax1.plot([verts_3[i][0], verts_3[j][0]],
                 [verts_3[i][1], verts_3[j][1]],
                 color=C['orange'], linewidth=2.5, alpha=0.7)
        # Edge label
        mx = (verts_3[i][0] + verts_3[j][0]) / 2
        my = (verts_3[i][1] + verts_3[j][1]) / 2
        edge_labels = ['ab', 'bc', 'ca']
        ax1.text(mx * 1.15, my * 1.15, edge_labels[i], fontsize=10,
                 ha='center', va='center', color=C['orange'], fontweight='bold')

    # Draw face (filled)
    tri = plt.Polygon(verts_3, alpha=0.08, facecolor=C['purple'],
                       edgecolor='none')
    ax1.add_patch(tri)

    # Draw vertices
    for (x, y), label, color in zip(verts_3, labels_3, colors_3):
        circle = plt.Circle((x, y), 0.35, facecolor=color, alpha=0.4,
                             edgecolor=color, linewidth=2)
        ax1.add_patch(circle)
        ax1.text(x, y, label, ha='center', va='center', fontsize=16,
                 fontweight='bold', color='white')

    # Nesting annotation
    ax1.text(0, -0.5, '(((a)b)c)', ha='center', va='center', fontsize=14,
             color=C['yellow'], fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.5', facecolor=C['card'],
                       edgecolor=C['border']))

    # f-vector
    ax1.text(0, -4.5, '[1, 3, 3, 1] = 8', ha='center', fontsize=13,
             color=C['white'], fontweight='bold')
    ax1.text(0, -5.1, '1 void + 3 vertices + 3 edges + 1 face',
             ha='center', fontsize=10, color=C['gray'])

    ax1.set_xlim(-5, 5)
    ax1.set_ylim(-5.8, 5)
    ax1.set_aspect('equal')
    ax1.axis('off')
    ax1.set_title('System 3: Triangle (2-simplex)\nbase[5] -> (4)(2)(1,3)',
                  fontsize=14, fontweight='bold', color=C['cyan'], pad=15)

    # ── System 4: Tetrahedron (2D projection) ──
    ax2.set_facecolor('#0d1117')
    # Tetrahedron projected to 2D
    verts_4 = [(0, 3.5), (-3, -1.5), (3, -1.5), (0, 0.5)]
    labels_4 = ['a', 'b', 'c', 'd']
    colors_4 = [C['cyan'], C['green'], C['pink'], C['orange']]

    # Draw all 6 edges
    edge_pairs = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
    edge_labels_4 = ['ab', 'ac', 'ad', 'bc', 'bd', 'cd']
    for (i, j), elabel in zip(edge_pairs, edge_labels_4):
        style = '-' if i != 3 and j != 3 else '--'
        ax2.plot([verts_4[i][0], verts_4[j][0]],
                 [verts_4[i][1], verts_4[j][1]],
                 color=C['orange'], linewidth=2, alpha=0.6, linestyle=style)

    # Draw 4 faces (semi-transparent)
    face_indices = [(0,1,2), (0,1,3), (0,2,3), (1,2,3)]
    face_colors = [C['purple'], C['cyan'], C['green'], C['pink']]
    face_labels = ['abc', 'abd', 'acd', 'bcd']
    for indices, fcolor in zip(face_indices, face_colors):
        tri = plt.Polygon([verts_4[i] for i in indices], alpha=0.05,
                           facecolor=fcolor, edgecolor='none')
        ax2.add_patch(tri)

    # Draw vertices
    for (x, y), label, color in zip(verts_4, labels_4, colors_4):
        circle = plt.Circle((x, y), 0.35, facecolor=color, alpha=0.4,
                             edgecolor=color, linewidth=2)
        ax2.add_patch(circle)
        ax2.text(x, y, label, ha='center', va='center', fontsize=16,
                 fontweight='bold', color='white')

    # Nesting annotation
    ax2.text(0, -3.5, '((((a)b)c)d)', ha='center', va='center', fontsize=14,
             color=C['yellow'], fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.5', facecolor=C['card'],
                       edgecolor=C['border']))

    # f-vector
    ax2.text(0, -4.5, '[1, 4, 6, 4, 1] = 16', ha='center', fontsize=13,
             color=C['white'], fontweight='bold')
    ax2.text(0, -5.1, '1 void + 4 vertices + 6 edges + 4 faces + 1 cell',
             ha='center', fontsize=10, color=C['gray'])

    ax2.set_xlim(-5, 5)
    ax2.set_ylim(-5.8, 5)
    ax2.set_aspect('equal')
    ax2.axis('off')
    ax2.set_title('System 4: Tetrahedron (3-simplex)\nbase[10] -> (9)(3,6)(1,2,4,5,7,8)',
                  fontsize=14, fontweight='bold', color=C['orange'], pad=15)

    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/simplex_fig1_polytopes.png', dpi=180)
    plt.close()
    print("  [OK] simplex_fig1_polytopes.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 2: System 3 Step Heatmap (like the System 4 one)
# ═══════════════════════════════════════════════════════════════════
def fig2_sys3_heatmap():
    fig, ax = plt.subplots(figsize=(10, 6))

    MODE_COLORS = {'E': '#3fb950', 'R': '#bc8cff'}

    # System 3 data
    terms_a = [1, 3, 1, 3]
    modes_a = ['R', 'E', 'E', 'E']
    terms_b = [3, 1, 3, 1]
    modes_b = ['E', 'E', 'E', 'R']

    all_terms = [terms_a, terms_b]
    all_modes = [modes_a, modes_b]
    thread_names = ['Set 3A', 'Set 3B']

    for row, (terms, modes, name) in enumerate(zip(all_terms, all_modes, thread_names)):
        for col, (term, mode) in enumerate(zip(terms, modes)):
            color = MODE_COLORS[mode]
            alpha = 0.7 if mode == 'E' else 0.4
            rect = plt.Rectangle((col, 1-row), 1, 1, facecolor=color,
                                 alpha=alpha, edgecolor=C['border'], linewidth=2)
            ax.add_patch(rect)
            ax.text(col + 0.5, 1-row + 0.6, f'T{term}', ha='center', va='center',
                    fontsize=16, fontweight='bold', color=C['white'])
            ax.text(col + 0.5, 1-row + 0.3, mode, ha='center', va='center',
                    fontsize=12, color=C['white'], alpha=0.8)

    # Neutron markers
    for col in range(4):
        a_mode = modes_a[col]
        b_mode = modes_b[col]
        has_r = 'R' in [a_mode, b_mode]
        if has_r:
            ax.text(col + 0.5, -0.3, '★ NEUTRON', ha='center', va='center',
                    fontsize=10, color=C['purple'], fontweight='bold')
        else:
            ax.text(col + 0.5, -0.3, 'PURE E', ha='center', va='center',
                    fontsize=10, color=C['green'], fontweight='bold')

    ax.set_xlim(0, 4)
    ax.set_ylim(-0.7, 2.3)
    ax.set_xticks([i + 0.5 for i in range(4)])
    ax.set_xticklabels([f'Step {i+1}' for i in range(4)], fontsize=12)
    ax.set_yticks([0.5, 1.5])
    ax.set_yticklabels(['Set 3B', 'Set 3A'], fontsize=13, fontweight='bold')
    ax.set_title('System 3: Triangular Simplex — 4-Step Cycle (3E + 1R per thread)',
                 fontsize=14, fontweight='bold', color=C['cyan'], pad=15)
    ax.set_aspect('equal')

    e_patch = mpatches.Patch(color=MODE_COLORS['E'], alpha=0.7,
                             label='E: Expressive (Forward)')
    r_patch = mpatches.Patch(color=MODE_COLORS['R'], alpha=0.4,
                             label='R: Regenerative (Neutron)')
    ax.legend(handles=[e_patch, r_patch], loc='upper right', fontsize=11,
              framealpha=0.8, facecolor=C['card'], edgecolor=C['border'])

    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/simplex_fig2_sys3_heatmap.png', dpi=180)
    plt.close()
    print("  [OK] simplex_fig2_sys3_heatmap.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 3: Pascal Triangle with f-vector highlighting
# ═══════════════════════════════════════════════════════════════════
def fig3_pascal():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor('#0d1117')

    # Draw Pascal's triangle rows 0-6
    max_row = 6
    for n in range(max_row + 1):
        row = []
        for k in range(n + 1):
            val = math.comb(n, k)
            row.append(val)

        for k, val in enumerate(row):
            x = k - n / 2.0
            y = -n

            # Highlight System 3 row (n=3) and System 4 row (n=4)
            if n == 3:
                color = C['cyan']
                alpha = 0.8
                size = 16
            elif n == 4:
                color = C['orange']
                alpha = 0.8
                size = 16
            else:
                color = C['gray']
                alpha = 0.5
                size = 13

            ax.text(x, y, str(val), ha='center', va='center',
                    fontsize=size, fontweight='bold', color=color, alpha=alpha)

    # System labels
    ax.text(3.5, -3, 'System 3\n[1,3,3,1]=8\nTriangle',
            fontsize=11, color=C['cyan'], fontweight='bold',
            ha='left', va='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C['card'],
                      edgecolor=C['cyan'], alpha=0.8))

    ax.text(4.0, -4, 'System 4\n[1,4,6,4,1]=16\nTetrahedron',
            fontsize=11, color=C['orange'], fontweight='bold',
            ha='left', va='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=C['card'],
                      edgecolor=C['orange'], alpha=0.8))

    # Column headers
    col_labels = ['void', 'vertices', 'edges', 'faces', 'cells', 'hyper', '6-faces']
    for k in range(max_row + 1):
        x = k - max_row / 2.0
        if k < len(col_labels):
            ax.text(x, -max_row - 0.8, col_labels[k], ha='center',
                    fontsize=9, color=C['gray'], style='italic')

    # Row sums on the right
    for n in range(max_row + 1):
        total = 2 ** n
        x = n / 2.0 + 1.0
        ax.text(x, -n, f'= {total}', ha='left', fontsize=11,
                color=C['yellow'], fontweight='bold')

    ax.set_xlim(-4, 6)
    ax.set_ylim(-max_row - 1.5, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Pascal's Triangle as the Simplex f-vector Generator\n"
                 "Row N = f-vector of the (N-1)-simplex = System N base polytope",
                 fontsize=14, fontweight='bold', color=C['white'], pad=20)

    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/simplex_fig3_pascal.png', dpi=180)
    plt.close()
    print("  [OK] simplex_fig3_pascal.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 4: Neutron Mode comparison (E/R ratios across systems)
# ═══════════════════════════════════════════════════════════════════
def fig4_neutron():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Left: E/R split per system
    systems = ['System 2\n(Line)', 'System 3\n(Triangle)',
               'System 4\n(Tetrahedron)', 'System 5\n(Pentachoron)']

    # System 2: 1-simplex, 2 vertices, 1 edge
    # Hypothetical: 1 thread, 2 steps, 1E+1R? or 2E+0R?
    # System 3: 3E+1R per thread
    # System 4: 7E+5R per thread
    # System 5: extrapolation

    e_counts = [1, 3, 7, 15]  # 2^(N-1) - 1?
    r_counts = [1, 1, 5, 11]  # total - E
    totals = [2, 4, 12, 26]   # hypothetical cycle lengths

    x = np.arange(len(systems))
    width = 0.35

    bars_e = ax1.bar(x - width/2, e_counts, width, color=C['green'],
                     alpha=0.7, label='Expressive (E)', edgecolor=C['border'])
    bars_r = ax1.bar(x + width/2, r_counts, width, color=C['purple'],
                     alpha=0.7, label='Regenerative (R)', edgecolor=C['border'])

    for bar, val in zip(bars_e, e_counts):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 str(val), ha='center', fontsize=12, fontweight='bold',
                 color=C['green'])
    for bar, val in zip(bars_r, r_counts):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 str(val), ha='center', fontsize=12, fontweight='bold',
                 color=C['purple'])

    ax1.set_xticks(x)
    ax1.set_xticklabels(systems, fontsize=10)
    ax1.set_ylabel('Steps per Thread', fontsize=12)
    ax1.set_title('E/R Mode Split Across Systems', fontsize=14,
                  fontweight='bold', color=C['cyan'])
    ax1.legend(fontsize=11, framealpha=0.8, facecolor=C['card'],
               edgecolor=C['border'])
    ax1.grid(axis='y', alpha=0.2)

    # Right: Neutron density (R ratio)
    r_ratios = [r / t * 100 for r, t in zip(r_counts, totals)]
    colors = [C['purple'] if ratio > 30 else C['green'] for ratio in r_ratios]

    bars = ax2.bar(x, r_ratios, 0.5, color=colors, alpha=0.7,
                   edgecolor=C['border'])
    for bar, ratio in zip(bars, r_ratios):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                 f'{ratio:.1f}%', ha='center', fontsize=12, fontweight='bold',
                 color=C['white'])

    ax2.set_xticks(x)
    ax2.set_xticklabels(systems, fontsize=10)
    ax2.set_ylabel('Regenerative Ratio (%)', fontsize=12)
    ax2.set_title('Neutron Mode Density\n(Higher = more virtual/simulative)',
                  fontsize=14, fontweight='bold', color=C['orange'])
    ax2.axhline(50, color=C['red'], linewidth=1, linestyle='--', alpha=0.5)
    ax2.text(3.5, 51, 'Balance line', fontsize=9, color=C['red'], alpha=0.7)
    ax2.set_ylim(0, 60)
    ax2.grid(axis='y', alpha=0.2)

    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/simplex_fig4_neutron.png', dpi=180)
    plt.close()
    print("  [OK] simplex_fig4_neutron.png")


# ═══════════════════════════════════════════════════════════════════
# Fig 5: The f-vector → cognitive mapping diagram
# ═══════════════════════════════════════════════════════════════════
def fig5_fvector_mapping():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_facecolor('#0d1117')

    # System 4 mapping as the detailed example
    # [1, 4, 6, 4, 1]
    levels = [
        (0, 'c(4) = 1 cell', '{abcd}', 'The tetrad: simultaneous\nholding of all 4 vertices',
         C['yellow'], 'CELL'),
        (1, 'f(4) = 4 faces', '{abc, abd, acd, bcd}',
         '4 triads: 3 concurrent threads\n+ 1 external view', C['pink'], 'FACES'),
        (2, 'e(4) = 6 edges', '{ab, ac, ad, bc, bd, cd}',
         '6 particular terms with E+R\n= 6 dyad configurations', C['orange'], 'EDGES'),
        (3, 'v(4) = 4 vertices', '{a, b, c, d}',
         '4 dual surface interfaces\n((((a)b)c)d) nesting', C['cyan'], 'VERTICES'),
        (4, 'void = 1 ground', '{empty set}',
         'Self-grounding: no external\nground needed', C['gray'], 'VOID'),
    ]

    y_spacing = 1.8
    for i, (idx, label, elements, description, color, category) in enumerate(levels):
        y = (2 - i) * y_spacing

        # Category box
        rect = plt.Rectangle((-7, y - 0.5), 3, 1, facecolor=color, alpha=0.15,
                              edgecolor=color, linewidth=2, linestyle='-')
        ax.add_patch(rect)
        ax.text(-5.5, y, category, ha='center', va='center', fontsize=13,
                fontweight='bold', color=color)

        # Label
        ax.text(-3, y, label, ha='left', va='center', fontsize=12,
                color=color, fontweight='bold')

        # Elements
        ax.text(1.5, y, elements, ha='left', va='center', fontsize=11,
                color=C['white'])

        # Description
        ax.text(6, y, description, ha='left', va='center', fontsize=10,
                color=C['gray'])

    # Pascal row annotation
    ax.text(0, -5.5, 'Pascal Row [1, 4, 6, 4, 1] = 2^4 = 16 total elements',
            ha='center', fontsize=13, fontweight='bold', color=C['yellow'])
    ax.text(0, -6.2, 'The simplex is self-dual: reading the f-vector forwards or backwards gives the same structure',
            ha='center', fontsize=10, color=C['gray'], style='italic')

    ax.set_xlim(-8, 12)
    ax.set_ylim(-7, 6)
    ax.axis('off')
    ax.set_title('System 4: Tetrahedral f-vector to Cognitive Architecture Mapping\n'
                 '[1, 4, 6, 4, 1] — Vertices, Edges, Faces, Cells',
                 fontsize=15, fontweight='bold', color=C['white'], pad=20)

    plt.tight_layout()
    fig.savefig('/home/ubuntu/demo/simplex_fig5_fvector.png', dpi=180)
    plt.close()
    print("  [OK] simplex_fig5_fvector.png")


# ═══════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating Simplex Polytope visualizations...")
    fig1_simplices()
    fig2_sys3_heatmap()
    fig3_pascal()
    fig4_neutron()
    fig5_fvector_mapping()
    print("Done — 5 simplex figures saved to /home/ubuntu/demo/")
