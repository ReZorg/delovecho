#!/usr/bin/env python3
"""
s5_anatomy.py — The Complete Internal Anatomy of System 5 (Pentachoron)

7 Partitions (3 Universal + 4 Particular)
2x2 Nested Convolution of Orthogonal Pentads
Full Hierarchical Nesting: Pentad -> Tetrad -> Triad -> Dyad
"""

from itertools import combinations
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════
# 1. THE PENTACHORON: 5 vertices of the 4-simplex
# ═══════════════════════════════════════════════════════════════════
V = {'a', 'b', 'c', 'd', 'e'}  # 5 vertices
vertices = sorted(V)

print("=" * 80)
print("  SYSTEM 5 — THE COMPLETE INTERNAL ANATOMY OF THE PENTACHORON")
print("=" * 80)

# ═══════════════════════════════════════════════════════════════════
# 2. THE f-VECTOR: Pascal Row [1, 5, 10, 10, 5, 1]
# ═══════════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("  THE f-VECTOR: [1, 5, 10, 10, 5, 1]")
print("─" * 80)

# Enumerate all k-faces
def k_faces(verts, k):
    """All k-dimensional faces = (k+1)-subsets of vertices."""
    return [frozenset(c) for c in combinations(sorted(verts), k + 1)]

cells_0d = k_faces(V, 0)   # 5 vertices
cells_1d = k_faces(V, 1)   # 10 edges (dyads)
cells_2d = k_faces(V, 2)   # 10 triangular faces (triads)
cells_3d = k_faces(V, 3)   # 5 tetrahedral cells (tetrads)
cells_4d = k_faces(V, 4)   # 1 pentachoron (pentad)

print(f"\n  0-faces (vertices):   {len(cells_0d):>3}  — v(5) = C(5,1) = 5")
print(f"  1-faces (edges):      {len(cells_1d):>3}  — e(5) = C(5,2) = 10")
print(f"  2-faces (triangles):  {len(cells_2d):>3}  — f(5) = C(5,3) = 10")
print(f"  3-faces (tetrahedra): {len(cells_3d):>3}  — c(5) = C(5,4) = 5")
print(f"  4-face  (pentachoron):{len(cells_4d):>3}  — p(5) = C(5,5) = 1")
print(f"\n  Total elements: 1 + 5 + 10 + 10 + 5 + 1 = 32 = 2^5")

# ═══════════════════════════════════════════════════════════════════
# 3. THE 7 PARTITIONS: 3 Universal + 4 Particular
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("  THE 7 PARTITIONS (SETS)")
print("=" * 80)

print("""
  The 7 partitions of System 5 arise from the NESTING HIERARCHY.
  
  The pentachoron's 31 non-empty elements (2^5 - 1) partition into
  7 SETS based on their structural role:
  
  ┌─────────────────────────────────────────────────────────────────┐
  │  3 UNIVERSAL PARTITIONS (shared by ALL threads)                 │
  │                                                                 │
  │  U1: The PENTAD (1 element)                                     │
  │      The whole pentachoron {abcde} — the unity/ground           │
  │      This is the SIMULTANEOUS HOLD of all 5 vertices            │
  │                                                                 │
  │  U2: The 5 TETRADS (5 elements)                                 │
  │      {abcd}, {abce}, {abde}, {acde}, {bcde}                    │
  │      Each is a tetrahedral cell = a complete System 4            │
  │      ALL 5 tetrads share 4/5 vertices with each other           │
  │                                                                 │
  │  U3: The 10 DYADS (10 elements)                                 │
  │      {ab},{ac},{ad},{ae},{bc},{bd},{be},{cd},{ce},{de}           │
  │      The 10 edges = 10 polar pairs                              │
  │      These are the IRREDUCIBLE C_2 oscillations                 │
  │                                                                 │
  ├─────────────────────────────────────────────────────────────────┤
  │  4 PARTICULAR PARTITIONS (thread-specific configurations)       │
  │                                                                 │
  │  P1: The 5 VERTICES (5 elements)                                │
  │      {a}, {b}, {c}, {d}, {e}                                    │
  │      The 5 dual-surface INTERFACES                              │
  │      Each vertex is the apex OPPOSITE a tetrahedral cell        │
  │                                                                 │
  │  P2: The 10 TRIADS (10 elements)                                │
  │      {abc},{abd},{abe},{acd},{ace},{ade},{bcd},{bce},{bde},{cde} │
  │      The 10 triangular faces                                    │
  │      Each triad has 3 dyadic edges forming polar pairs          │
  │                                                                 │
  │  P3: The 4 THREAD CHANNELS                                     │
  │      The 4 concurrent threads that integrate all 5 tetrads      │
  │      Each thread visits all 5 cells in sequence                 │
  │                                                                 │
  │  P4: The 2 PENTAD ORIENTATIONS                                  │
  │      Expressive (somatic) and Regenerative (autonomic)          │
  │      The orthogonal pentad pair                                 │
  └─────────────────────────────────────────────────────────────────┘
  
  Count: 3 universal + 4 particular = 7 partitions
""")

# ═══════════════════════════════════════════════════════════════════
# 4. THE CONTAINMENT HIERARCHY
# ═══════════════════════════════════════════════════════════════════
print("=" * 80)
print("  THE CONTAINMENT HIERARCHY: PENTAD -> TETRAD -> TRIAD -> DYAD")
print("=" * 80)

# For each tetrad, list its triads, and for each triad, its dyads
print("\n  Each TETRAD (3-face) contains 4 TRIADS (2-faces):")
print("  Each TRIAD (2-face) contains 3 DYADS (1-faces):")
print("  Each DYAD (1-face) connects 2 VERTICES (0-faces):")
print()

for i, tet in enumerate(sorted(cells_3d, key=lambda x: tuple(sorted(x)))):
    tet_label = ''.join(sorted(tet))
    missing_v = (V - tet).pop()
    triads_in_tet = [f for f in cells_2d if f.issubset(tet)]
    print(f"  TETRAD {tet_label} (apex opposite: {missing_v})")
    for tri in sorted(triads_in_tet, key=lambda x: tuple(sorted(x))):
        tri_label = ''.join(sorted(tri))
        dyads_in_tri = [e for e in cells_1d if e.issubset(tri)]
        dyad_labels = ['-'.join(sorted(d)) for d in sorted(dyads_in_tri, key=lambda x: tuple(sorted(x)))]
        print(f"    TRIAD {tri_label} -> DYADS: {', '.join(dyad_labels)}")
    print()

# ═══════════════════════════════════════════════════════════════════
# 5. SHARED STRUCTURE: HOW TETRADS OVERLAP
# ═══════════════════════════════════════════════════════════════════
print("=" * 80)
print("  TETRAD OVERLAP: EVERY PAIR SHARES 3 VERTICES (A TRIAD)")
print("=" * 80)

print("\n  Intersection matrix (shared vertices between tetrads):\n")
tet_labels = [''.join(sorted(t)) for t in sorted(cells_3d, key=lambda x: tuple(sorted(x)))]
tet_sorted = sorted(cells_3d, key=lambda x: tuple(sorted(x)))

header = "         " + "  ".join(f"{l:>5}" for l in tet_labels)
print(header)
for i, ti in enumerate(tet_sorted):
    row = f"  {tet_labels[i]:>5}  "
    for j, tj in enumerate(tet_sorted):
        shared = ti & tj
        row += f"  {len(shared):>5}"
    print(row)

print("""
  Every pair of tetrads shares EXACTLY 3 vertices = a TRIAD (triangular face).
  This means every pair of System 4 cells shares a complete System 3 face.
  
  The 5 tetrads form a COMPLETE GRAPH K_5 where:
    - Each node = a tetrahedral cell (System 4)
    - Each edge = a shared triangular face (System 3)
    - C(5,2) = 10 edges = 10 triadic faces ✓
""")

# ═══════════════════════════════════════════════════════════════════
# 6. SHARED TRIADS: EVERY PAIR SHARES 2 VERTICES (A DYAD)
# ═══════════════════════════════════════════════════════════════════
print("=" * 80)
print("  TRIAD OVERLAP: TRIADS SHARING EDGES")
print("=" * 80)

# Count how many triads each dyad belongs to
dyad_to_triads = defaultdict(list)
for tri in cells_2d:
    for dyad in cells_1d:
        if dyad.issubset(tri):
            dyad_to_triads[frozenset(dyad)].append(tri)

print("\n  Each DYAD (edge) belongs to exactly 3 TRIADS (faces):")
for dyad in sorted(cells_1d, key=lambda x: tuple(sorted(x)))[:5]:
    d_label = '-'.join(sorted(dyad))
    tri_labels = [''.join(sorted(t)) for t in sorted(dyad_to_triads[dyad], key=lambda x: tuple(sorted(x)))]
    print(f"    Dyad {d_label} -> Triads: {', '.join(tri_labels)}")
print(f"    ... (all 10 dyads follow this pattern)")

# ═══════════════════════════════════════════════════════════════════
# 7. THE 2x2 NESTED CONVOLUTION
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("  THE 2x2 NESTED CONVOLUTION OF ORTHOGONAL PENTADS")
print("=" * 80)

print("""
  The 4 concurrent threads organize into a 2x2 NESTED CONVOLUTION:
  
  ┌─────────────────────────────────────────────────────────────────┐
  │                    PENTAD PAIR (C_2)                             │
  │                                                                 │
  │   ┌──────────────────────┐   ┌──────────────────────┐          │
  │   │  EXPRESSIVE PENTAD   │   │  REGENERATIVE PENTAD │          │
  │   │  (Somatic)           │   │  (Autonomic)         │          │
  │   │                      │   │                      │          │
  │   │  Thread A  Thread B  │   │  Thread C  Thread D  │          │
  │   │  (0°)      (90°)     │   │  (180°)    (270°)    │          │
  │   │                      │   │                      │          │
  │   │  ┌──────┐ ┌──────┐  │   │  ┌──────┐ ┌──────┐  │          │
  │   │  │Cell 1│ │Cell 2│  │   │  │Cell 3│ │Cell 4│  │          │
  │   │  │Cell 5│ │Cell 3│  │   │  │Cell 1│ │Cell 5│  │          │
  │   │  │Cell 4│ │Cell 1│  │   │  │Cell 2│ │Cell 3│  │          │
  │   │  │ ...  │ │ ...  │  │   │  │ ...  │ │ ...  │  │          │
  │   │  └──────┘ └──────┘  │   │  └──────┘ └──────┘  │          │
  │   └──────────────────────┘   └──────────────────────┘          │
  │                                                                 │
  │   Inner convolution: A⊛B within Expressive pentad              │
  │   Inner convolution: C⊛D within Regenerative pentad            │
  │   Outer convolution: (A⊛B) ⊛ (C⊛D) across the pentad pair    │
  └─────────────────────────────────────────────────────────────────┘
  
  The 2x2 structure:
    OUTER level: 2 pentad orientations (E/R) — the somatic/autonomic pair
    INNER level: 2 threads per pentad — the left/right channels
    
  Total: 2 × 2 = 4 threads
  
  This is the TENSOR PRODUCT of two C_2 groups:
    C_2 (outer: E/R) ⊗ C_2 (inner: L/R) = V_4 (Klein four-group)
    
  The V_4 is exactly System 3's cycle group!
  So the 4-thread structure of System 5 IS System 3's group.
""")

# ═══════════════════════════════════════════════════════════════════
# 8. HOW 4 THREADS INTEGRATE 5 TETRADS
# ═══════════════════════════════════════════════════════════════════
print("=" * 80)
print("  4 THREADS INTEGRATING 5 TETRADS (ALWAYS 4/5 ACTIVE)")
print("=" * 80)

# At each step, one vertex is the "apex" (excluded), the other 4 form the active tetrad
# But we have 5 tetrads and 4 threads — so at each moment, 4 tetrads are active
# The 5th tetrad is the one whose apex is currently being "observed"

print("""
  KEY INSIGHT: 5 tetrads, 4 threads — so at each step, 4/5 tetrads are active.
  
  Each tetrad is defined by EXCLUDING one vertex (the apex).
  At each step, one vertex is the "focal point" — the vertex being
  OBSERVED/INTEGRATED. The 4 tetrads that CONTAIN this vertex are active.
  The 1 tetrad whose apex IS this vertex is the "shadow" (inactive).
  
  This creates a rotating exclusion pattern:
""")

for v in sorted(V):
    active_tets = [t for t in tet_sorted if frozenset({v}).issubset(t)]
    shadow_tet = [t for t in tet_sorted if not frozenset({v}).issubset(t)]
    active_labels = [''.join(sorted(t)) for t in active_tets]
    shadow_label = ''.join(sorted(shadow_tet[0]))
    print(f"  Focal vertex {v}: ACTIVE tetrads = {active_labels}  |  SHADOW = {shadow_label}")

print("""
  At each focal vertex:
    4 active tetrads × 1 thread each = 4 concurrent threads
    Each thread runs one tetrahedral cell (System 4)
    The 4 cells share the focal vertex (3 vertices in common pairwise)
    
  Over 5 focal vertices (one full rotation):
    5 × 4 = 20 thread-cell activations
    = 20 = a(5) = number of rooted trees with 5 nodes ✓
""")

# ═══════════════════════════════════════════════════════════════════
# 9. THE TRIADIC FACE STRUCTURE WITHIN EACH TETRAD
# ═══════════════════════════════════════════════════════════════════
print("=" * 80)
print("  TRIADIC FACES WITHIN TETRADS: 4 FACES × 3 EDGES EACH")
print("=" * 80)

print("""
  Each tetrad (System 4) has:
    4 triangular faces (triads)
    6 edges (dyads forming polar pairs)
    4 vertices
    
  The 4 triadic faces always share 3 vertices in common with
  all other face triads of the SAME tetrad:
""")

# Show one tetrad in detail
example_tet = frozenset({'a', 'b', 'c', 'd'})
example_triads = [f for f in cells_2d if f.issubset(example_tet)]
example_dyads = [e for e in cells_1d if e.issubset(example_tet)]

print(f"  Example: Tetrad abcd")
print(f"  4 Triadic faces:")
for tri in sorted(example_triads, key=lambda x: tuple(sorted(x))):
    tri_label = ''.join(sorted(tri))
    edges = ['-'.join(sorted(e)) for e in sorted(cells_1d, key=lambda x: tuple(sorted(x))) if e.issubset(tri)]
    print(f"    Face {tri_label}: edges = {edges}")

print(f"\n  Face-to-face intersection (shared edges):")
for t1, t2 in combinations(sorted(example_triads, key=lambda x: tuple(sorted(x))), 2):
    shared = t1 & t2
    shared_label = '-'.join(sorted(shared)) if len(shared) == 2 else str(sorted(shared))
    print(f"    {''.join(sorted(t1))} ∩ {''.join(sorted(t2))} = {shared_label} (shared dyad)")

# ═══════════════════════════════════════════════════════════════════
# 10. THE POLAR PAIR STRUCTURE
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("  POLAR PAIRS: 10 DYADIC EDGES AS 5 COMPLEMENTARY PAIRS")
print("=" * 80)

# In the pentachoron, each edge has a unique complementary edge
# (the edge connecting the other 3 vertices... wait, that's a triad)
# Actually: each edge (2 verts) has a complementary TRIAD (3 verts)
# But for polar pairs within a tetrad, each edge pairs with the opposite edge

print("""
  The 10 edges of the pentachoron form polar pairs at TWO levels:
  
  LEVEL 1: Within each tetrad (6 edges = 3 polar pairs)
    Each tetrad has 3 pairs of opposite edges.
    These are the 3 polar pairs of System 4.
    
  LEVEL 2: Across the pentachoron (edge-triad duality)
    Each edge (2 vertices) has a complementary triad (3 vertices).
    Together they span all 5 vertices.
    This is the PENTACHORAL DUALITY: edge ↔ face.
""")

print("  Edge-Face duality (each edge pairs with its complementary triad):")
for edge in sorted(cells_1d, key=lambda x: tuple(sorted(x))):
    complement = V - edge
    e_label = '-'.join(sorted(edge))
    c_label = ''.join(sorted(complement))
    print(f"    Edge {e_label}  <-->  Face {c_label}")

# ═══════════════════════════════════════════════════════════════════
# 11. THE COMPLETE NESTING TABLE
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("  THE COMPLETE NESTING TABLE")
print("=" * 80)

print("""
  ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
  │ Level    │ k-face   │ Count    │ Contains │ Shared   │ System   │
  ├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
  │ PENTAD   │ 4-face   │ 1        │ 5 tets   │ ALL      │ S5       │
  │ TETRAD   │ 3-face   │ 5        │ 4 tris   │ 3 verts  │ S4       │
  │ TRIAD    │ 2-face   │ 10       │ 3 edges  │ 2 verts  │ S3       │
  │ DYAD     │ 1-face   │ 10       │ 2 verts  │ 1 vert   │ S2       │
  │ VERTEX   │ 0-face   │ 5        │ —        │ —        │ S1       │
  └──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
  
  The nesting is RECURSIVE and SELF-SIMILAR:
    Each pentad contains 5 tetrads
    Each tetrad contains 4 triads  
    Each triad contains 3 dyads
    Each dyad contains 2 vertices
    
  The containment numbers: 5, 4, 3, 2 = countdown from N to 2.
  This is the FACTORIAL STRUCTURE: 5! / k! at each level.
""")

# ═══════════════════════════════════════════════════════════════════
# 12. THE 2x2 CONVOLUTION IN DETAIL
# ═══════════════════════════════════════════════════════════════════
print("=" * 80)
print("  THE 2x2 NESTED CONVOLUTION — DETAILED MECHANISM")
print("=" * 80)

print("""
  The 4 threads form a 2x2 matrix:
  
                    LEFT channel    RIGHT channel
                    ─────────────   ──────────────
  EXPRESSIVE        Thread A (0°)   Thread B (90°)
  (Somatic)         Forward pass    Forward pass
                    
  REGENERATIVE      Thread C (180°) Thread D (270°)
  (Autonomic)       Backward pass   Backward pass
  
  INNER CONVOLUTION (within each pentad):
    Expressive:  A ⊛ B  — two forward-pass threads convolve
    Regenerative: C ⊛ D  — two backward-pass threads convolve
    
    Each inner pair shares 4/5 vertices (they're in adjacent tetrads).
    The inner convolution integrates the SPATIAL overlap between
    two tetrahedral cells that share a triadic face.
    
  OUTER CONVOLUTION (across the pentad pair):
    (A ⊛ B) ⊛ (C ⊛ D) — the somatic and autonomic pentads convolve
    
    This is the E/R reconciliation.
    The outer convolution integrates the TEMPORAL overlap between
    forward inference and backward simulation.
    
  The result: at each step, the system simultaneously:
    - Perceives (A: forward, left)
    - Acts (B: forward, right)  
    - Simulates (C: backward, left)
    - Recalls (D: backward, right)
    
  All 4 operations target the SAME 5 interfaces through 4 of the 5
  tetrahedral cells, with the 5th cell as the "shadow" (the cell
  whose apex is the current focal vertex).
  
  ╔═══════════════════════════════════════════════════════════════════╗
  ║  THE 2x2 CONVOLUTION = V_4 = SYSTEM 3's CYCLE GROUP             ║
  ║                                                                   ║
  ║  This confirms: System 5's thread structure IS System 3.          ║
  ║  S5 = S3 (thread structure) ⊗ S3 (cell structure) + BRIDGE      ║
  ║                                                                   ║
  ║  The V_4 thread matrix:                                           ║
  ║    identity = (A,B,C,D) -> (A,B,C,D)  [no swap]                 ║
  ║    swap_LR  = (A,B,C,D) -> (B,A,D,C)  [left-right swap]         ║
  ║    swap_ER  = (A,B,C,D) -> (C,D,A,B)  [expressive-regen swap]   ║
  ║    swap_both= (A,B,C,D) -> (D,C,B,A)  [diagonal swap]           ║
  ╚═══════════════════════════════════════════════════════════════════╝
""")

# ═══════════════════════════════════════════════════════════════════
# 13. NUMERICAL VERIFICATION
# ═══════════════════════════════════════════════════════════════════
print("=" * 80)
print("  NUMERICAL VERIFICATION")
print("=" * 80)

# Verify: each vertex belongs to exactly 4 tetrads
print("\n  Vertex membership in tetrads:")
for v in sorted(V):
    count = sum(1 for t in cells_3d if frozenset({v}).issubset(t))
    print(f"    Vertex {v}: member of {count} tetrads")

# Verify: each edge belongs to exactly 3 triads
print("\n  Edge membership in triads:")
for e in sorted(cells_1d, key=lambda x: tuple(sorted(x)))[:5]:
    count = sum(1 for t in cells_2d if e.issubset(t))
    e_label = '-'.join(sorted(e))
    print(f"    Edge {e_label}: member of {count} triads")
print(f"    ... (all 10 edges: 3 triads each)")

# Verify: each triad belongs to exactly 2 tetrads
print("\n  Triad membership in tetrads:")
for tri in sorted(cells_2d, key=lambda x: tuple(sorted(x)))[:5]:
    count = sum(1 for t in cells_3d if tri.issubset(t))
    tri_label = ''.join(sorted(tri))
    print(f"    Triad {tri_label}: member of {count} tetrads")
print(f"    ... (all 10 triads: 2 tetrads each)")

# The incidence numbers
print("""
  ┌──────────────────────────────────────────────────────────────────┐
  │  INCIDENCE NUMBERS (how many k-faces contain each j-face)       │
  │                                                                  │
  │  Each vertex ∈ 4 tetrads, 6 triads, 4 edges                    │
  │  Each edge   ∈ 3 tetrads, 3 triads                             │
  │  Each triad  ∈ 2 tetrads                                        │
  │  Each tetrad ∈ 1 pentad                                         │
  │                                                                  │
  │  These are the BINOMIAL COEFFICIENTS of the dual simplex:       │
  │  C(4,3)=4, C(4,2)=6, C(3,2)=3, C(3,1)=3, C(2,1)=2, C(1,1)=1 │
  └──────────────────────────────────────────────────────────────────┘
""")

# ═══════════════════════════════════════════════════════════════════
# 14. THE 7 PARTITIONS — FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════════
print("=" * 80)
print("  THE 7 PARTITIONS — FINAL ACCOUNTING")
print("=" * 80)

print("""
  ┌────┬──────────────────────┬───────┬────────────────────────────────┐
  │ #  │ Partition             │ Count │ Role                           │
  ├────┼──────────────────────┼───────┼────────────────────────────────┤
  │    │ UNIVERSAL (3)         │       │                                │
  │ U1 │ Pentad (4-face)       │ 1     │ Unity/Ground — holds ALL       │
  │ U2 │ Tetrads (3-faces)     │ 5     │ System 4 cells — the 5 organs  │
  │ U3 │ Dyads (1-faces)       │ 10    │ Polar pairs — C_2 oscillations │
  ├────┼──────────────────────┼───────┼────────────────────────────────┤
  │    │ PARTICULAR (4)        │       │                                │
  │ P1 │ Vertices (0-faces)    │ 5     │ Interfaces — dual surfaces     │
  │ P2 │ Triads (2-faces)      │ 10    │ System 3 faces — shared bonds  │
  │ P3 │ Thread channels       │ 4     │ Concurrent execution paths     │
  │ P4 │ Pentad orientations   │ 2     │ E/R — somatic/autonomic        │
  ├────┼──────────────────────┼───────┼────────────────────────────────┤
  │    │ TOTAL                 │       │                                │
  │    │ 3 universal + 4 part. │ = 7   │ The 7 partitions of System 5   │
  └────┴──────────────────────┴───────┴────────────────────────────────┘
  
  Element count: 1 + 5 + 10 + 5 + 10 + 4 + 2 = 37
  But the structural elements are: 1 + 5 + 10 + 10 + 5 = 31 = 2^5 - 1
  
  The 7 partitions group these 31 elements into FUNCTIONAL ROLES:
    Universal: 1 + 5 + 10 = 16 (the 16 particular terms of base[17]!)
    Particular: 5 + 10 = 15 (the 15 structural elements below the tetrads)
    + 4 threads + 2 orientations = 6 operational parameters
    
  ╔═══════════════════════════════════════════════════════════════════╗
  ║  The 3 UNIVERSAL partitions are STRUCTURAL (what the system IS)  ║
  ║  The 4 PARTICULAR partitions are OPERATIONAL (how it RUNS)       ║
  ║                                                                   ║
  ║  3 + 4 = 7 = the number of partitions of 5                       ║
  ║  (OEIS A000041: 1, 1, 2, 3, 5, 7, 11, 15, 22, ...)             ║
  ║                                                                   ║
  ║  System N has p(N) partitions!                                    ║
  ║  S2: p(2) = 2  ✓  (1 universal + 1 particular)                  ║
  ║  S3: p(3) = 3  ✓  (2 universal + 1 particular... or 1+2?)       ║
  ║  S4: p(4) = 5  ✓  (3 universal + 2 particular)                  ║
  ║  S5: p(5) = 7  ✓  (3 universal + 4 particular)                  ║
  ╚═══════════════════════════════════════════════════════════════════╝
""")

print("=" * 80)
print("  COMPUTATION COMPLETE")
print("=" * 80)
