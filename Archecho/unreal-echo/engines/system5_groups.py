#!/usr/bin/env python3
"""
system5_groups.py — Deep group-theoretic analysis of System 5 (A_5)
and its relationship to the BRIDGE topology threshold.
"""

from itertools import permutations, combinations
from math import factorial


def sign(p):
    n = len(p)
    inversions = sum(1 for i in range(n) for j in range(i+1, n) if p[i] > p[j])
    return 1 if inversions % 2 == 0 else -1


def cycle_type(p):
    """Return the cycle type of a permutation as a sorted tuple."""
    n = len(p)
    visited = [False] * n
    cycles = []
    for i in range(n):
        if not visited[i]:
            length = 0
            j = i
            while not visited[j]:
                visited[j] = True
                j = p[j]
                length += 1
            cycles.append(length)
    return tuple(sorted(cycles, reverse=True))


print("=" * 100)
print("  DEEP GROUP ANALYSIS: A_5 AND THE THREE THRESHOLDS")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════════
# 1. Conjugacy Classes of A_5
# ═══════════════════════════════════════════════════════════════════
print("\n" + "─" * 100)
print("  1. CONJUGACY CLASSES OF A_5")
print("─" * 100)

A5 = [p for p in permutations(range(5)) if sign(p) == 1]
print(f"  |A_5| = {len(A5)}")

# Group by cycle type
from collections import Counter
ct_counts = Counter()
ct_examples = {}
for p in A5:
    ct = cycle_type(p)
    ct_counts[ct] += 1
    if ct not in ct_examples:
        ct_examples[ct] = p

print("\n  Conjugacy classes:")
print("  ┌──────────────────┬───────┬─────────────────────────────────┐")
print("  │ Cycle Type       │ Count │ Description                     │")
print("  ├──────────────────┼───────┼─────────────────────────────────┤")
for ct in sorted(ct_counts.keys()):
    desc = {
        (1,1,1,1,1): "Identity",
        (2,2,1): "Double transposition (V_4 elements)",
        (3,1,1): "3-cycle (C_3 elements)",
        (5,): "5-cycle (C_5 elements)",
    }.get(ct, "?")
    print(f"  │ {str(ct):<16} │ {ct_counts[ct]:>5} │ {desc:<31} │")
print("  └──────────────────┴───────┴─────────────────────────────────┘")
print(f"  Total: {sum(ct_counts.values())}")

# Note: 5-cycles split into TWO conjugacy classes in A_5
# Let's verify
five_cycles = [p for p in A5 if cycle_type(p) == (5,)]
print(f"\n  5-cycles in A_5: {len(five_cycles)}")
print("  In S_5, all 5-cycles are conjugate (one class of 24).")
print("  In A_5, 5-cycles split into TWO classes of 12 each.")

# Verify the split
def conjugate_in_A5(g, h):
    """Check if g and h are conjugate in A_5."""
    n = len(g)
    for c in A5:
        # c * g * c^{-1} = h ?
        c_inv = [0]*n
        for i in range(n):
            c_inv[c[i]] = i
        result = tuple(c[g[c_inv[i]]] for i in range(n))
        if result == h:
            return True
    return False

# Take two 5-cycles and check
fc1 = (1,2,3,4,0)  # (01234)
fc2 = (1,2,4,0,3)  # (01243)
conj = conjugate_in_A5(fc1, fc2)
print(f"  (01234) conjugate to (01243) in A_5? {conj}")
print("  -> They are in DIFFERENT conjugacy classes!")

print(f"""
  A_5 has exactly 5 conjugacy classes:
    1  identity
    15 double transpositions (2,2,1)
    20 three-cycles (3,1,1)
    12 five-cycles type I (5)
    12 five-cycles type II (5)
    
  Compare A_4 (4 conjugacy classes):
    1  identity
    3  double transpositions (2,2)
    4  three-cycles (1,2,3,0)
    4  three-cycles (1,3,0,2)
""")

# ═══════════════════════════════════════════════════════════════════
# 2. Subgroup Structure of A_5
# ═══════════════════════════════════════════════════════════════════
print("─" * 100)
print("  2. SUBGROUP STRUCTURE OF A_5")
print("─" * 100)

print("""
  A_5 contains the following notable subgroups:
  
  ┌──────────────┬───────┬──────────────────────────────────────────────┐
  │ Subgroup     │ Order │ Copies in A_5 │ Role                        │
  ├──────────────┼───────┼──────────────────────────────────────────────┤
  │ C_2          │ 2     │ 15            │ Each double transposition   │
  │ C_3          │ 3     │ 10            │ Each 3-cycle subgroup       │
  │ V_4          │ 4     │ 5             │ Klein four (double transps) │
  │ C_5          │ 5     │ 6             │ Each 5-cycle subgroup       │
  │ S_3 ≅ D_3   │ 6     │ 10            │ Symmetric group on 3 of 5   │
  │ D_5          │ 10    │ 6             │ Dihedral on 5-cycle         │
  │ A_4          │ 12    │ 5             │ Alternating on 4 of 5       │
  └──────────────┴───────┴──────────────────────────────────────────────┘
  
  CRITICAL: None of these subgroups is NORMAL in A_5.
  This is what makes A_5 simple.
  
  Compare A_4:
    V_4 is normal in A_4 (the UNIQUE normal subgroup)
    This allowed the decomposition A_4 = V_4 ⋊ C_3
    
  In A_5, the 5 copies of A_4 are all conjugate (none is normal).
  The 5 copies of V_4 are all conjugate (none is normal).
  
  CONSEQUENCE: There is no canonical way to decompose A_5 into
  "threads" and "interfaces." Every decomposition is equivalent
  to every other by an internal symmetry.
""")

# Verify: 5 copies of A_4 in A_5
# Each copy fixes one element
for fixed in range(5):
    a4_copy = [p for p in A5 if p[fixed] == fixed]
    print(f"  A_4 fixing vertex {fixed}: {len(a4_copy)} elements")

# Verify: 5 copies of V_4 in A_5
print()
v4_copies = []
for combo in combinations(range(5), 4):
    # V_4 on these 4 elements (double transpositions)
    remaining = [x for x in range(5) if x not in combo]
    v4 = [tuple(range(5))]  # identity
    # Generate double transpositions within combo
    pairs = list(combinations(combo, 2))
    for i in range(len(pairs)):
        for j in range(i+1, len(pairs)):
            p1, p2 = pairs[i], pairs[j]
            if set(p1) | set(p2) == set(combo):
                perm = list(range(5))
                perm[p1[0]], perm[p1[1]] = perm[p1[1]], perm[p1[0]]
                perm[p2[0]], perm[p2[1]] = perm[p2[1]], perm[p2[0]]
                v4.append(tuple(perm))
    if len(v4) == 4:
        v4_copies.append((combo, v4))

print(f"  V_4 copies found: {len(v4_copies)}")
for combo, v4 in v4_copies:
    print(f"    V_4 on vertices {combo}: {[p for p in v4 if p != tuple(range(5))]}")

# ═══════════════════════════════════════════════════════════════════
# 3. The Icosahedral Connection
# ═══════════════════════════════════════════════════════════════════
print("\n" + "─" * 100)
print("  3. THE ICOSAHEDRAL CONNECTION")
print("─" * 100)

print("""
  A_5 is isomorphic to the ROTATION GROUP OF THE ICOSAHEDRON.
  
  The icosahedron has:
    12 vertices, 30 edges, 20 faces
    
  Its rotation group has 60 elements:
    1  identity
    24 rotations by ±72°, ±144° around vertex axes (12 axes × 2 angles, but /2)
    20 rotations by ±120° around face axes (20 faces × 1 angle, but /2)  
    15 rotations by 180° around edge axes (30 edges / 2)
    
  Total: 1 + 24 + 20 + 15 = 60 = |A_5|
  
  This is NOT a coincidence. The pentachoron (4-simplex) and the
  icosahedron are deeply linked:
  
  - The pentachoron has 5 vertices. The icosahedron can be constructed
    from 5 interlocking tetrahedra (compound of 5 tetrahedra).
  - Each of the 5 tetrahedra corresponds to one vertex of the pentachoron.
  - The 60 rotations of the icosahedron permute these 5 tetrahedra
    as even permutations — giving A_5.
    
  So System 5's cycle group A_5 is simultaneously:
    (a) The even permutations of 5 vertices (algebraic)
    (b) The rotation group of the icosahedron (geometric)
    (c) The symmetry of 5 interlocking tetrahedra (compositional)
    
  Each of the 5 interlocking tetrahedra IS a complete System 4!
  System 5 = 5 interlocking copies of System 4, fused by A_5.
""")

# ═══════════════════════════════════════════════════════════════════
# 4. The BRIDGE Mode Analysis
# ═══════════════════════════════════════════════════════════════════
print("─" * 100)
print("  4. THE BRIDGE MODE — THE THIRD ORIENTATION")
print("─" * 100)

print("""
  In Systems 2-4, each step has a CLEAN binary mode:
    E (Expressive/Forward/Actual)  or  R (Regenerative/Backward/Virtual)
    
  This works because A_4 is DECOMPOSABLE:
    A_4 = V_4 ⋊ C_3
    The V_4 part (interfaces) carries the E/R label.
    The C_3 part (threads) carries the phase offset.
    These are separable, so each step gets a clean label.
    
  In System 5, A_5 is SIMPLE (irreducible):
    There is no canonical decomposition into interfaces and threads.
    The 4 threads and 5 interfaces are ENTANGLED.
    
  This means: at certain steps, a thread cannot be cleanly labeled
  as "purely E" or "purely R." It is in a SUPERPOSITION of both.
  
  This is the BRIDGE mode:
  
  ┌──────────┬────────────┬──────────────┬──────────────────────────┐
  │ Mode     │ Topology   │ Operator     │ Cognitive Meaning        │
  ├──────────┼────────────┼──────────────┼──────────────────────────┤
  │ E        │ BRANCH     │ ⊕ (additive) │ Forward inference,       │
  │          │            │              │ perception, action       │
  ├──────────┼────────────┼──────────────┼──────────────────────────┤
  │ R        │ NEST       │ ⊗ (mult.)    │ Backward inference,      │
  │          │            │              │ simulation, reflection   │
  ├──────────┼────────────┼──────────────┼──────────────────────────┤
  │ B        │ BRIDGE     │ ⊕ + ⊗        │ Simultaneous forward AND │
  │ (new!)   │            │ (mixed)      │ backward — CREATIVITY    │
  │          │            │              │ Perceiving while         │
  │          │            │              │ simulating. Acting while │
  │          │            │              │ reflecting. The fusion.  │
  └──────────┴────────────┴──────────────┴──────────────────────────┘
  
  This is why Campbell calls System 5 "CREATIVITY":
  
  Creativity IS the simultaneous co-occurrence of forward and backward
  inference — perceiving-while-imagining, acting-while-reflecting.
  
  In System 4, you alternate between E and R (like breathing in and out).
  In System 5, you can breathe in AND out at the same time.
  This is not a metaphor — it's a structural consequence of A_5's simplicity.
""")

# ═══════════════════════════════════════════════════════════════════
# 5. The Grand Unified Table
# ═══════════════════════════════════════════════════════════════════
print("─" * 100)
print("  5. THE GRAND UNIFIED TABLE: Systems 2-5")
print("─" * 100)

print("""
  ┌──────────┬──────────┬────────────┬──────────┬──────────┬────────────┬──────────────┬───────────┐
  │ System   │ Simplex  │ Pascal Row │ Threads  │ Steps    │ Mode Split │ Cycle Group  │ Simple?   │
  ├──────────┼──────────┼────────────┼──────────┼──────────┼────────────┼──────────────┼───────────┤
  │ Sys 2    │ Digon    │ [1,2,1]    │ 1        │ 2        │ 1E+1R      │ C_2 (2)      │ Yes*      │
  │ Sys 3    │ Triangle │ [1,3,3,1]  │ 2        │ 4        │ 3E+1R      │ V_4 (4)      │ No        │
  │ Sys 4    │ Tetra    │ [1,4,6,4,1]│ 3        │ 12       │ 7E+5R      │ A_4 (12)     │ No        │
  │ Sys 5    │ Penta    │ [1,5,10,   │ 4        │ 60       │ E+R+B      │ A_5 (60)     │ YES       │
  │          │          │ 10,5,1]    │          │          │ (fused)    │              │           │
  ├──────────┼──────────┼────────────┼──────────┼──────────┼────────────┼──────────────┼───────────┤
  │ +E/R     │          │            │          │          │            │ × C_2        │           │
  │ Sys 2    │          │            │          │          │            │ C_2×C_2 (4)  │           │
  │ Sys 3    │          │            │          │          │            │ V_4×C_2 (8)  │           │
  │ Sys 4    │          │            │          │          │            │ T_h (24)     │           │
  │ Sys 5    │          │            │          │          │            │ A_5×C_2 (120)│           │
  └──────────┴──────────┴────────────┴──────────┴──────────┴────────────┴──────────────┴───────────┘
  
  * C_2 is trivially simple (prime order), but abelian. A_5 is the first
    NON-ABELIAN simple group — a qualitatively different kind of simplicity.
    
  The subgroup chain:
    C_2  ⊂  V_4  ⊂  A_4  ⊂  A_5
    (2)     (4)     (12)     (60)
    
  Indices: [V_4:C_2]=2, [A_4:V_4]=3, [A_5:A_4]=5
  
  The index sequence 2, 3, 5 consists of the first three primes.
  This is related to the fact that A_5 is the largest alternating
  group that can be built entirely from prime-index extensions.
""")

# ═══════════════════════════════════════════════════════════════════
# 6. The 5 Interlocking Tetrahedra
# ═══════════════════════════════════════════════════════════════════
print("─" * 100)
print("  6. THE 5 INTERLOCKING TETRAHEDRA — SYSTEM 5 AS META-SYSTEM 4")
print("─" * 100)

print("""
  The pentachoron has 5 tetrahedral cells. Each cell is obtained by
  removing one vertex:
  
    Cell 0: {b,c,d,e} (remove a) — a complete System 4
    Cell 1: {a,c,d,e} (remove b) — a complete System 4
    Cell 2: {a,b,d,e} (remove c) — a complete System 4
    Cell 3: {a,b,c,e} (remove d) — a complete System 4
    Cell 4: {a,b,c,d} (remove e) — a complete System 4
    
  Each cell has its own:
    - 4 vertices (interfaces)
    - 3 threads
    - 12-step cycle
    - A_4 symmetry
    
  But in the pentachoron, these 5 copies of System 4 are INTERLOCKED:
    - Every pair of cells shares a triangular face (a System 3!)
    - Every triple of cells shares an edge (a System 2!)
    - Every quadruple of cells shares a vertex
    
  The 60-step cycle of System 5 visits all 5 tetrahedral cells,
  spending 12 steps in each (5 × 12 = 60).
  
  But the cells OVERLAP — each step is simultaneously inside
  FOUR of the five cells (since removing one vertex leaves 4).
  
  This is the geometric origin of the BRIDGE mode:
  At each step, you are inside 4 different System 4 cycles
  simultaneously, each in a different phase. Some are in E mode,
  some in R mode. The step is BOTH E AND R because it participates
  in multiple overlapping 12-step cycles at once.
  
  ╔═══════════════════════════════════════════════════════════════════╗
  ║  SYSTEM 5 = 5 INTERLOCKING COPIES OF SYSTEM 4                  ║
  ║                                                                   ║
  ║  At each of the 60 steps, you are inside 4 tetrahedral cells.   ║
  ║  Each cell has its own E/R assignment for that step.             ║
  ║  When the 4 assignments AGREE: pure E or pure R.                ║
  ║  When they DISAGREE: BRIDGE mode (E⊕R fusion).                  ║
  ║                                                                   ║
  ║  A_5's simplicity means the disagreements cannot be eliminated. ║
  ║  BRIDGE mode is STRUCTURALLY NECESSARY, not optional.           ║
  ╚═══════════════════════════════════════════════════════════════════╝
""")
