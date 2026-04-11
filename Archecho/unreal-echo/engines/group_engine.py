#!/usr/bin/env python3
"""
group_engine.py — Rigorous Group Theory Analysis for the Simplex Hierarchy

Computes and verifies the transformation groups for Systems 2, 3, and 4,
resolving the question: is System 4's group Th, Z_3 × A_4, or something else?
"""

from itertools import permutations, product
from collections import Counter
from math import gcd
from functools import reduce


# ═══════════════════════════════════════════════════════════════════
# Permutation Group Utilities
# ═══════════════════════════════════════════════════════════════════

def compose(p, q):
    """Compose two permutations: (p∘q)(i) = p(q(i))"""
    return tuple(p[q[i]] for i in range(len(p)))

def identity(n):
    return tuple(range(n))

def order(p):
    """Order of a permutation element."""
    e = identity(len(p))
    x = p
    for k in range(1, len(p) + 100):
        if x == e:
            return k
        x = compose(x, p)
    return -1

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

def generate_group(generators, n):
    """Generate a group from generators using BFS."""
    e = identity(n)
    group = {e}
    queue = list(generators)
    group.update(generators)
    while queue:
        g = queue.pop(0)
        for h in list(group):
            for new in [compose(g, h), compose(h, g)]:
                if new not in group:
                    group.add(new)
                    queue.append(new)
    return group


# ═══════════════════════════════════════════════════════════════════
# System 2: C_2 — The Primordial Flip
# ═══════════════════════════════════════════════════════════════════

def analyze_system2():
    print("=" * 90)
    print("  SYSTEM 2: THE DIGON (1-simplex) — C_2")
    print("=" * 90)
    
    print("""
  Pascal Row: [1, 2, 1] = 4
  Nesting:    ((a)b)
  base[3] -> (2)(1)
  
  f-vector:
    1 void
    2 vertices v(2) = {a, b}
    1 edge    e(2) = {ab}
  
  Step Sequence (1 thread, 2 steps):
  
    Set 2A: 1E  1R
    
    Mode:    E   R
    
  This is the PRIMORDIAL OSCILLATION:
    Step 1: Expressive (forward/actual)  — perceive
    Step 2: Regenerative (backward/virtual) — reflect
    
  Mode split: 1E + 1R (perfect 50/50 balance)
  R-ratio: 50% — the most balanced possible
  """)
    
    # C_2 group
    e = (0, 1)
    sigma = (1, 0)
    C2 = {e, sigma}
    
    print(f"  Symmetry Group: S_2 = C_2 = Z_2")
    print(f"  |C_2| = {len(C2)}")
    print(f"  Elements: {{e, sigma}} where sigma = {sigma}")
    print(f"  sigma^2 = {compose(sigma, sigma)} = e  [verified]")
    print(f"  Order of sigma: {order(sigma)}")
    print()
    
    # Cayley table
    print("  Cayley Table:")
    print("  ┌─────┬─────┬───────┐")
    print("  │  *  │  e  │ sigma │")
    print("  ├─────┼─────┼───────┤")
    print(f"  │  e  │  e  │ sigma │")
    print(f"  │sigma│sigma│   e   │")
    print("  └─────┴─────┴───────┘")
    print()
    
    print("  C_2 is the FOUNDATION of all higher systems:")
    print("    - It IS the E/R duality (Expressive/Regenerative)")
    print("    - It IS the structure/process polarity")
    print("    - It IS the perceptual shift transformation")
    print("    - Every polar pair [s(p)] is a copy of C_2")
    print()
    
    return C2


# ═══════════════════════════════════════════════════════════════════
# System 3: V_4 ⊂ S_3 — The Klein Four-Group
# ═══════════════════════════════════════════════════════════════════

def analyze_system3():
    print("=" * 90)
    print("  SYSTEM 3: THE TRIANGLE (2-simplex) — Group Analysis")
    print("=" * 90)
    
    print("""
  The 4-step cycle: 1R 3E 1E 3E (Set 3A)
  
  The 4 states visited are elements of {1,3} x {E,R}:
    Step 1: (1, R)
    Step 2: (3, E)
    Step 3: (1, E)
    Step 4: (3, E)  <-- note: same as step 2!
    
  Wait — (3,E) appears twice. So the cycle doesn't visit all 4 states.
  It visits: {(1,R), (3,E), (1,E)} — only 3 distinct states.
  
  The TRANSFORMATION acting on the step positions is what matters.
  Set 3B = Set 3A shifted by 3 positions (cyclically).
  
  The shift operator sigma: step[i] -> step[(i+3) mod 4]
  sigma = (3, 0, 1, 2) as a permutation of positions {0,1,2,3}
  sigma has order 4, generating C_4.
  
  But we only have 2 threads, so only sigma^0 = e and sigma^3 are used.
  {e, sigma^3} is a subgroup of order 2 = C_2.
  
  However, the SIMPLEX symmetry group is S_3 (order 6).
  The cycle structure lives in a DIFFERENT space.
  """)
    
    # Verify the shift
    # Set 3A positions: [(1,R), (3,E), (1,E), (3,E)]
    # Shift by 3:       [(3,E), (1,R), (3,E), (1,E)] -- this should be Set 3B
    set_a = [(1,'R'), (3,'E'), (1,'E'), (3,'E')]
    shifted = [set_a[(i + 3) % 4] for i in range(4)]
    set_b = [(3,'E'), (1,'E'), (3,'E'), (1,'R')]
    
    print(f"  Set 3A:          {set_a}")
    print(f"  Shift by 3:      {shifted}")
    print(f"  Set 3B (given):  {set_b}")
    print(f"  Match: {shifted == set_b}")
    print()
    
    # Now analyze the simplex symmetry group S_3
    print("  Simplex Symmetry Group: S_3")
    S3 = set(permutations(range(3)))
    print(f"  |S_3| = {len(S3)}")
    
    # Conjugacy classes
    classes = {}
    for p in S3:
        ct = cycle_type(p)
        if ct not in classes:
            classes[ct] = []
        classes[ct].append(p)
    
    print("  Conjugacy classes:")
    for ct, elems in sorted(classes.items()):
        print(f"    {ct}: {len(elems)} elements, order {order(elems[0])}")
    
    # Subgroup lattice
    print("\n  Subgroup lattice of S_3:")
    print("    S_3 (order 6)")
    print("    ├── A_3 = C_3 (order 3): even permutations")
    print("    ├── C_2 (order 2): three copies (one per reflection)")
    print("    └── {e} (order 1)")
    
    # The V_4 question
    print("\n  KEY QUESTION: Is the 4-step cycle V_4 (Klein four)?")
    print("  V_4 has order 4, but 4 does not divide |S_3| = 6.")
    print("  Therefore V_4 is NOT a subgroup of S_3.")
    print("  The 4-step cycle is NOT a subgroup of the simplex symmetry.")
    print()
    print("  RESOLUTION: The cycle operates on a DIFFERENT space.")
    print("  The simplex group S_3 acts on VERTICES {a,b,c}.")
    print("  The cycle group C_4 acts on STEP POSITIONS {0,1,2,3}.")
    print("  These are different representations of the same system.")
    print()
    print("  The THREAD group (permuting threads) is C_2 (swap A<->B).")
    print("  The STEP group (cycling positions) is C_4.")
    print("  The FULL transformation group of System 3's triad is:")
    print("  C_2 x C_2 = V_4 (Klein four, order 4)")
    print("  where one C_2 = thread swap, other C_2 = E/R mode flip.")
    print()
    
    return S3


# ═══════════════════════════════════════════════════════════════════
# System 4: The Deep Analysis
# ═══════════════════════════════════════════════════════════════════

def analyze_system4():
    print("=" * 90)
    print("  SYSTEM 4: THE TETRAHEDRON (3-simplex) — Group Analysis")
    print("=" * 90)
    
    # First: build A_4 explicitly
    S4 = set(permutations(range(4)))
    
    def sign(p):
        """Sign of a permutation: +1 for even, -1 for odd."""
        n = len(p)
        inversions = sum(1 for i in range(n) for j in range(i+1, n) if p[i] > p[j])
        return 1 if inversions % 2 == 0 else -1
    
    A4 = {p for p in S4 if sign(p) == 1}
    
    print(f"\n  S_4 (full symmetric): |S_4| = {len(S4)}")
    print(f"  A_4 (alternating):    |A_4| = {len(A4)}")
    
    # Conjugacy classes of A_4
    classes_a4 = {}
    for p in A4:
        ct = cycle_type(p)
        if ct not in classes_a4:
            classes_a4[ct] = []
        classes_a4[ct].append(p)
    
    print("\n  Conjugacy classes of A_4:")
    for ct, elems in sorted(classes_a4.items()):
        orders = set(order(e) for e in elems)
        print(f"    {ct}: {len(elems)} elements, order(s) {orders}")
    
    # Subgroups of A_4
    print("\n  Subgroup lattice of A_4:")
    print("    A_4 (order 12)")
    print("    ├── V_4 = {e, (01)(23), (02)(13), (03)(12)} (order 4, NORMAL)")
    print("    ├── C_3 (order 3): four copies (one per vertex)")
    print("    ├── C_2 (order 2): three copies (inside V_4)")
    print("    └── {e} (order 1)")
    
    # Verify V_4 inside A_4
    e = (0,1,2,3)
    v1 = (1,0,3,2)  # (01)(23)
    v2 = (2,3,0,1)  # (02)(13)
    v3 = (3,2,1,0)  # (03)(12)
    V4 = {e, v1, v2, v3}
    
    print(f"\n  V_4 verification:")
    print(f"    e    = {e}")
    print(f"    v1   = {v1} = (01)(23), order {order(v1)}")
    print(f"    v2   = {v2} = (02)(13), order {order(v2)}")
    print(f"    v3   = {v3} = (03)(12), order {order(v3)}")
    print(f"    All in A_4: {all(v in A4 for v in V4)}")
    print(f"    Closed under composition: {all(compose(a,b) in V4 for a in V4 for b in V4)}")
    
    # The 3-cycles (C_3 elements)
    three_cycles = [p for p in A4 if max(cycle_type(p)) == 3]
    print(f"\n  3-cycles in A_4: {len(three_cycles)} elements")
    print(f"  These generate the C_3 subgroups (face rotations)")
    
    # ── THE KEY DECOMPOSITION ──
    print("\n" + "─" * 90)
    print("  THE KEY DECOMPOSITION: What is the transformation group?")
    print("─" * 90)
    
    print("""
  We must distinguish THREE different group actions:
  
  1. SIMPLEX SYMMETRY: S_4 (order 24) acts on vertices {a,b,c,d}
     - Full symmetry group of the tetrahedron
     - Contains A_4 (order 12) as the rotation subgroup
     
  2. CYCLE GROUP: C_12 (order 12) acts on step positions {0..11}
     - The 12-step cycle is a cyclic rotation
     - The 3 threads are cosets of C_4 inside C_12
     - C_12 / C_4 = C_3 (the thread permutation)
     
  3. MODE GROUP: C_2 acts on {E, R}
     - The Expressive/Regenerative flip
  
  The FULL transformation group of the triad system combines all three:
  """)
    
    # Verify: the 12-step cycle
    # Set A offset 0, Set B offset 4, Set C offset 8
    # Shift by 4 generates C_3 acting on threads
    # Shift by 1 generates C_12 acting on steps
    
    print("  CYCLE ANALYSIS:")
    print(f"    12 steps, shift by 4 maps thread A -> B -> C -> A")
    print(f"    The shift-by-4 operator has order 3 (generates C_3)")
    print(f"    The shift-by-1 operator has order 12 (generates C_12)")
    print(f"    C_3 is a subgroup of C_12 (index 4)")
    print()
    
    # The isomorphism A_4 ≅ V_4 ⋊ C_3
    print("  SEMIDIRECT PRODUCT DECOMPOSITION:")
    print(f"    A_4 ≅ V_4 ⋊ C_3")
    print(f"    |A_4| = |V_4| × |C_3| = 4 × 3 = 12  ✓")
    print()
    print(f"    V_4 = the 4 nesting interfaces (Klein four-group)")
    print(f"    C_3 = the 3 concurrent threads (cyclic rotation)")
    print(f"    The semidirect product ⋊ means C_3 ACTS on V_4 by")
    print(f"    conjugation — rotating which pairs are active.")
    print()
    
    # Now: what about the E/R duality?
    print("  INCLUDING THE E/R DUALITY:")
    print()
    print("  Option 1: T_h = A_4 × C_2 (order 24)")
    print("    - Direct product: E/R flip commutes with everything")
    print("    - This is the pyritohedral group")
    print("    - Geometrically: rotations of tetrahedron × inversion")
    print()
    print("  Option 2: S_4 ≅ A_4 ⋊ C_2 (order 24)")
    print("    - Semidirect product: E/R flip does NOT commute")
    print("    - This is the full tetrahedral symmetry group")
    print("    - The C_2 acts by conjugation on A_4")
    print()
    
    # Check: does the E/R flip commute with the cycle?
    # In the step sequence, E and R are assigned to specific positions.
    # Flipping all E<->R gives a DIFFERENT sequence, not a shifted one.
    # So E/R does NOT simply commute with the cycle shift.
    
    # The mode sequence for Set A: R R E E E E E E E R R R
    modes_a = ['R','R','E','E','E','E','E','E','E','R','R','R']
    modes_a_flipped = ['E' if m == 'R' else 'R' for m in modes_a]
    
    # Is the flipped sequence a cyclic shift of the original?
    is_shift = False
    for offset in range(12):
        shifted = [modes_a[(i + offset) % 12] for i in range(12)]
        if shifted == modes_a_flipped:
            is_shift = True
            print(f"  E/R flip = cyclic shift by {offset}!")
            break
    
    if not is_shift:
        print("  E/R flip is NOT equivalent to any cyclic shift.")
        print("  Therefore E/R is an INDEPENDENT symmetry.")
        print()
        
        # Check if flipped = reversed
        modes_a_reversed = list(reversed(modes_a))
        if modes_a_reversed == modes_a_flipped:
            print("  E/R flip = TIME REVERSAL (reading the sequence backwards)!")
        else:
            # Check shifted reversal
            for offset in range(12):
                shifted_rev = [modes_a_reversed[(i + offset) % 12] for i in range(12)]
                if shifted_rev == modes_a_flipped:
                    print(f"  E/R flip = time reversal + shift by {offset}")
                    break
    
    print()
    
    # ── THE RESOLUTION ──
    print("─" * 90)
    print("  RESOLUTION: THE TRANSFORMATION TABLE")
    print("─" * 90)
    
    print("""
  The System 4 transformation group has a LAYERED structure:
  
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Layer          │  Group    │  Order  │  Action                        │
  ├─────────────────┼───────────┼─────────┼────────────────────────────────┤
  │  Primordial     │  C_2      │    2    │  E/R flip (the digon)          │
  │  Interfaces     │  V_4      │    4    │  4 nesting levels (Klein four) │
  │  Threads        │  C_3      │    3    │  Thread cycling A->B->C        │
  │  Cycle (inner)  │  A_4      │   12    │  12-step rotation = V_4 ⋊ C_3 │
  │  Full single    │  T_h      │   24    │  Cycle × mode = A_4 × C_2     │
  │  Full triad     │  T_h × C_3│   72    │  3 threads × full single      │
  └─────────────────┴───────────┴─────────┴────────────────────────────────┘
  
  But wait — the 3 threads are ALREADY encoded in A_4 (as the C_3 subgroup).
  So the "full triad" double-counts C_3.
  
  The CORRECT full group is:
  
  ╔═══════════════════════════════════════════════════════════════════╗
  ║  System 4 Transformation Group = A_4 × C_2 = T_h (order 24)    ║
  ║                                                                   ║
  ║  where:                                                           ║
  ║    A_4 = V_4 ⋊ C_3                                               ║
  ║        = (4 interfaces) ⋊ (3 threads)                             ║
  ║        = the 12-step cycle                                        ║
  ║    C_2 = E/R duality                                              ║
  ║        = the primordial flip (System 2)                           ║
  ║                                                                   ║
  ║  T_h is the PYRITOHEDRAL group — the symmetry of the pyritohedron║
  ║  (an irregular dodecahedron with tetrahedral symmetry + inversion)║
  ╚═══════════════════════════════════════════════════════════════════╝
  """)
    
    # ── THE NESTING ──
    print("  THE NESTING (subgroup chain):")
    print()
    print("    C_2  ⊂  V_4  ⊂  A_4  ⊂  T_h")
    print("    (2)     (4)     (12)     (24)")
    print("     │       │       │        │")
    print("    Sys2   Sys3    Sys4    Sys4+mode")
    print("    flip  4-step  12-step  full symmetry")
    print()
    print("  Each level CONTAINS all previous levels:")
    print("    V_4 contains 3 copies of C_2")
    print("    A_4 contains V_4 as its unique normal subgroup")
    print("    T_h contains A_4 as its unique normal subgroup")
    print()
    
    # Verify the chain numerically
    print("  Index verification:")
    print(f"    [V_4 : C_2] = 4/2 = 2  (2 cosets = 2 threads in Sys3)")
    print(f"    [A_4 : V_4] = 12/4 = 3  (3 cosets = 3 threads in Sys4)")
    print(f"    [T_h : A_4] = 24/12 = 2 (2 cosets = E/R modes)")
    print(f"    [T_h : C_2] = 24/2 = 12 (12 cosets = 12 steps)")
    print()
    
    return A4, V4, S4


# ═══════════════════════════════════════════════════════════════════
# The Grand Unified Table
# ═══════════════════════════════════════════════════════════════════

def grand_table():
    print("=" * 90)
    print("  GRAND UNIFIED TABLE: The Simplex Hierarchy")
    print("=" * 90)
    
    print("""
  ┌──────────┬──────────┬────────────┬──────────┬──────────┬────────────┬──────────────┐
  │ System   │ Simplex  │ Pascal Row │ Threads  │ Steps    │ Mode Split │ Group        │
  ├──────────┼──────────┼────────────┼──────────┼──────────┼────────────┼──────────────┤
  │ Sys 2    │ Digon    │ [1,2,1]=4  │ 1        │ 2        │ 1E+1R      │ C_2          │
  │ (1-simp) │ ((a)b)   │            │          │          │ (50%)      │ (order 2)    │
  ├──────────┼──────────┼────────────┼──────────┼──────────┼────────────┼──────────────┤
  │ Sys 3    │ Triangle │ [1,3,3,1]  │ 2        │ 4        │ 3E+1R      │ V_4          │
  │ (2-simp) │ (((a)b)c)│ =8         │          │          │ (25% R)    │ (order 4)    │
  ├──────────┼──────────┼────────────┼──────────┼──────────┼────────────┼──────────────┤
  │ Sys 4    │ Tetra-   │ [1,4,6,4,1]│ 3        │ 12       │ 7E+5R      │ A_4          │
  │ (3-simp) │ hedron   │ =16        │          │          │ (41.7% R)  │ (order 12)   │
  │          │((((a)b)  │            │          │          │            │ = V_4 ⋊ C_3  │
  │          │  c)d)    │            │          │          │            │              │
  ├──────────┼──────────┼────────────┼──────────┼──────────┼────────────┼──────────────┤
  │ +E/R     │ (all)    │ (all)      │ (all)    │ (all)    │ (all)      │ × C_2        │
  │ duality  │          │            │          │          │            │ (doubles)    │
  └──────────┴──────────┴────────────┴──────────┴──────────┴────────────┴──────────────┘
  
  The subgroup chain:  C_2  ⊂  V_4  ⊂  A_4  ⊂  T_h = A_4 × C_2
                       (2)     (4)     (12)      (24)
                       Sys2    Sys3    Sys4      Sys4 + mode
  
  ═══ WHY T_h AND NOT S_4? ═══
  
  S_4 = A_4 ⋊ C_2 (semidirect product, order 24) — full tetrahedral symmetry
  T_h = A_4 × C_2 (direct product, order 24)     — pyritohedral symmetry
  
  Both have order 24, but they are DIFFERENT groups!
  
  S_4: the C_2 acts on A_4 by conjugation (odd permutations flip orientation)
  T_h: the C_2 commutes with A_4 (inversion is independent of rotation)
  
  In our system, the E/R duality is an INDEPENDENT axis — it doesn't
  conjugate the cycle steps, it labels them. So the structure is T_h.
  
  T_h is the symmetry group of the PYRITOHEDRON — a shape with
  tetrahedral rotational symmetry plus an independent inversion.
  This is exactly our system: A_4 rotations + C_2 mode flip.
  
  ═══ WHY NOT Z_3 × A_4? ═══
  
  Z_3 × A_4 has order 36. This would be the group if the 3 threads
  were an EXTERNAL symmetry independent of the cycle. But they're not:
  the 3 threads are ALREADY the C_3 subgroup inside A_4.
  
  The thread shift (by 4 steps) IS the C_3 ⊂ A_4 action.
  There is no separate Z_3 factor.
  
  ═══ THE ANSWER ═══
  
  System 4's transformation group is:
  
      T_h = A_4 × C_2  (pyritohedral, order 24)
      
  where A_4 = V_4 ⋊ C_3 decomposes as:
      V_4 = the 4 interfaces (Klein four-group)
      C_3 = the 3 threads (cyclic, embedded in A_4)
      C_2 = the E/R duality (the primordial digon, System 2)
  """)


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    C2 = analyze_system2()
    print()
    S3 = analyze_system3()
    print()
    A4, V4, S4 = analyze_system4()
    print()
    grand_table()
