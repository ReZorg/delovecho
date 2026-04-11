#!/usr/bin/env python3
"""
simplex_engine.py — Unified Simplex Polytope Engine for Ontelecho

The (N-1)-simplex is the base polytope for System N.
Pascal row [C(N-1,k)] gives the f-vector: vertices, edges, faces, cells.

System 3: Triangle (2-simplex)  [1, 3, 3, 1]
  base[5] -> (4)(2)(1,3)
  2 particular terms: {1, 3}
  1 polar pair: [1(3)]
  2 concurrent threads, 4 steps per cycle
  3E + 1R per thread (1R = Neutron Mode)

System 4: Tetrahedron (3-simplex)  [1, 4, 6, 4, 1]
  base[10] -> (9)(3,6)(1,2,4,5,7,8)
  6 particular terms: {1, 2, 4, 5, 7, 8}
  3 polar pairs: [1(8)], [4(5)], [7(2)]
  3 concurrent threads, 12 steps per cycle
  7E + 5R per thread
"""

import threading
import math
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from enum import Enum
from itertools import combinations


class Mode(Enum):
    E = "Expressive"
    R = "Regenerative"


# ═══════════════════════════════════════════════════════════════════
# Pascal Row and f-vector
# ═══════════════════════════════════════════════════════════════════

def pascal_row(n: int) -> List[int]:
    """Row n of Pascal's triangle: [C(n,0), C(n,1), ..., C(n,n)]"""
    row = [1]
    for k in range(1, n + 1):
        row.append(row[-1] * (n - k + 1) // k)
    return row


def simplex_fvector(dim: int) -> dict:
    """f-vector of the dim-simplex.
    
    dim=2: triangle, dim=3: tetrahedron, etc.
    Returns dict with keys: vertices, edges, faces, cells, ...
    """
    row = pascal_row(dim + 1)
    names = ['void', 'vertices', 'edges', 'faces', 'cells',
             'hyperfaces', '5-faces', '6-faces', '7-faces']
    result = {}
    for i, (count, name) in enumerate(zip(row, names)):
        result[name] = count
    return result


def simplex_elements(vertices: list, dim: int) -> dict:
    """Enumerate all k-faces of the simplex."""
    result = {}
    names = ['vertices', 'edges', 'faces', 'cells',
             'hyperfaces', '5-faces', '6-faces']
    for k in range(1, dim + 2):
        combos = list(combinations(vertices, k))
        if k - 1 < len(names):
            result[names[k-1]] = combos
    return result


# ═══════════════════════════════════════════════════════════════════
# System 3: Triangular Simplex
# ═══════════════════════════════════════════════════════════════════

class System3:
    """System 3 — Triangle (2-simplex) [1, 3, 3, 1]
    
    base[5] -> (4)(2)(1,3)
    Term 4: Universal (like T9 in Sys4)
    Term 2: Coherence (like T8 in Sys4... but here it's the 'particular sequence' term)
    Terms 1,3: The 2 particular terms
    Polar pair: [1(3)]
    
    Nesting: (((a)b)c) — 3 vertices of the triangle
    """

    TERMS = {
        1: {"name": "T1", "type": "structure", "role": "Perception"},
        2: {"name": "T2", "type": "process",   "role": "Coherence/Mediation"},
        3: {"name": "T3", "type": "structure", "role": "Memory/Creation"},
        4: {"name": "T4", "type": "universal", "role": "Universal/Direction"},
    }

    PARTICULAR = [1, 3]
    POLAR_PAIRS = {"P1": (1, 3)}

    # From user's exact table:
    # Set 3A: 1R 3E 1E 3E
    # Set 3B: 3E 1E 3E 1R
    SET_A = [(1, Mode.R), (3, Mode.E), (1, Mode.E), (3, Mode.E)]
    SET_B = [(3, Mode.E), (1, Mode.E), (3, Mode.E), (1, Mode.R)]

    # Mode patterns
    MODE_A = [Mode.R, Mode.E, Mode.E, Mode.E]  # 3E + 1R
    MODE_B = [Mode.E, Mode.E, Mode.E, Mode.R]  # 3E + 1R

    SIMPLEX_DIM = 2
    PASCAL = pascal_row(3)  # [1, 3, 3, 1]
    VERTICES = ['a', 'b', 'c']
    NESTING = "(((a)b)c)"
    CYCLE_LENGTH = 4
    NUM_THREADS = 2

    @classmethod
    def validate(cls):
        """Validate all structural properties."""
        results = {}

        # 1. Mode counts
        for name, seq in [("3A", cls.SET_A), ("3B", cls.SET_B)]:
            e = sum(1 for _, m in seq if m == Mode.E)
            r = sum(1 for _, m in seq if m == Mode.R)
            results[f"{name}_modes"] = f"{e}E + {r}R"
            results[f"{name}_valid"] = (e == 3 and r == 1)

        # 2. Polar pair coverage at each step
        for step in range(cls.CYCLE_LENGTH):
            terms = {cls.SET_A[step][0], cls.SET_B[step][0]}
            # Both terms of the polar pair should be present
            pair_covered = terms == {1, 3}
            results[f"step{step+1}_terms"] = terms
            results[f"step{step+1}_pair_covered"] = pair_covered

            # Mode mix
            modes = {cls.SET_A[step][1], cls.SET_B[step][1]}
            results[f"step{step+1}_modes"] = {m.name for m in modes}
            results[f"step{step+1}_mixed"] = len(modes) == 2

        # 3. f-vector
        elements = simplex_elements(cls.VERTICES, cls.SIMPLEX_DIM)
        results["f_vector"] = cls.PASCAL
        results["elements"] = {k: [tuple(c) for c in v]
                               for k, v in elements.items()}

        return results


# ═══════════════════════════════════════════════════════════════════
# System 4: Tetrahedral Simplex
# ═══════════════════════════════════════════════════════════════════

class System4:
    """System 4 — Tetrahedron (3-simplex) [1, 4, 6, 4, 1]
    
    base[10] -> (9)(3,6)(1,2,4,5,7,8)
    6 particular terms, 3 polar pairs
    3 concurrent threads, 12 steps per cycle
    7E + 5R per thread
    """

    PARTICULAR = [1, 2, 4, 5, 7, 8]
    POLAR_PAIRS = {"P1": (1, 8), "P2": (4, 5), "P3": (7, 2)}

    SET_A = [(4,'R'),(2,'R'),(8,'E'),(5,'E'),(7,'E'),(1,'E'),
             (4,'E'),(2,'E'),(8,'E'),(5,'R'),(7,'R'),(1,'R')]
    SET_B = [(8,'E'),(5,'R'),(7,'R'),(1,'R'),(4,'R'),(2,'R'),
             (8,'E'),(5,'E'),(7,'E'),(1,'E'),(4,'E'),(2,'E')]
    SET_C = [(7,'E'),(1,'E'),(4,'E'),(2,'E'),(8,'E'),(5,'R'),
             (7,'R'),(1,'R'),(4,'R'),(2,'R'),(8,'E'),(5,'E')]

    SIMPLEX_DIM = 3
    PASCAL = pascal_row(4)  # [1, 4, 6, 4, 1]
    VERTICES = ['a', 'b', 'c', 'd']
    NESTING = "((((a)b)c)d)"
    CYCLE_LENGTH = 12
    NUM_THREADS = 3


# ═══════════════════════════════════════════════════════════════════
# Display
# ═══════════════════════════════════════════════════════════════════

def display_system3():
    """Full display and validation of System 3."""
    print("\n" + "█" * 90)
    print("█  SYSTEM 3 — TRIANGULAR SIMPLEX (2-simplex)  [1, 3, 3, 1]")
    print("█" * 90)

    s3 = System3()
    results = s3.validate()

    # Pascal row and f-vector
    fv = simplex_fvector(2)
    print(f"\n  Pascal Row: {s3.PASCAL}")
    print(f"  Nesting:    {s3.NESTING}")
    print(f"  base[5] -> (4)(2)(1,3)")
    print()

    # f-vector mapping
    elements = simplex_elements(s3.VERTICES, s3.SIMPLEX_DIM)
    print("  ┌─────────────────────────────────────────────────────────────────┐")
    print("  │  f-vector Element    Count   Elements         Cognitive Mapping │")
    print("  ├─────────────────────────────────────────────────────────────────┤")
    print(f"  │  Void (ground)        1      {{∅}}              Self-grounding   │")

    v_str = ",".join(s3.VERTICES)
    print(f"  │  Vertices v(3)        3      {{{v_str}}}            3 nesting steps  │")

    e_list = elements['edges']
    e_str = ",".join("".join(e) for e in e_list)
    print(f"  │  Edges e(3)           3      {{{e_str}}}         3 polar dyads    │")

    f_list = elements['faces']
    f_str = ",".join("".join(f) for f in f_list)
    print(f"  │  Faces f(3)           1      {{{f_str}}}           1 triadic face   │")
    print("  └─────────────────────────────────────────────────────────────────┘")

    # Thread sequences
    print(f"\n  Thread Sequences ({s3.NUM_THREADS} threads, {s3.CYCLE_LENGTH} steps):")
    for name, seq in [("Set 3A", s3.SET_A), ("Set 3B", s3.SET_B)]:
        terms_str = " ".join(f"{t}{m.name}" for t, m in seq)
        modes_str = " ".join(f" {m.name} " for _, m in seq)
        e = sum(1 for _, m in seq if m == Mode.E)
        r = sum(1 for _, m in seq if m == Mode.R)
        print(f"    {name}: {terms_str}  ({e}E + {r}R)")

    # Step-by-step analysis
    print(f"\n  {'Step':>4}  {'Set 3A':^10}  {'Set 3B':^10}  {'Terms':^10}  "
          f"{'Pair':^12}  {'E/R Mix':^10}  {'Neutron?':^10}")
    print(f"  {'─'*4}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*12}  {'─'*10}  {'─'*10}")

    for step in range(s3.CYCLE_LENGTH):
        a_term, a_mode = s3.SET_A[step]
        b_term, b_mode = s3.SET_B[step]

        terms = {a_term, b_term}
        pair_ok = terms == {1, 3}
        modes = {a_mode, b_mode}
        mixed = len(modes) == 2
        e_count = sum(1 for m in [a_mode, b_mode] if m == Mode.E)
        r_count = sum(1 for m in [a_mode, b_mode] if m == Mode.R)

        neutron = "★ NEUTRON" if r_count > 0 else ""
        mix_str = f"{e_count}E+{r_count}R"

        print(f"  {step+1:>4}  {a_term}{a_mode.name:^8}  {b_term}{b_mode.name:^8}  "
              f"  {str(sorted(terms)):^8}  "
              f"{'✓ [1(3)]':^12}  {mix_str:^10}  {neutron:^10}")

    # The Neutron Mode insight
    print(f"\n  ═══ NEUTRON MODE ANALYSIS ═══")
    print(f"  Steps 1 & 4: Mixed (1E+1R) — Regenerative pulse present")
    print(f"  Steps 2 & 3: Pure Expressive (2E+0R) — Full forward activation")
    print(f"  The single R step per thread creates a 'neutron pulse' —")
    print(f"  a momentary backward/virtual step that recharges the system.")
    print(f"  In System 3, the R step is rare (1/4 = 25%) vs System 4 (5/12 ≈ 42%).")
    print(f"  System 3 is predominantly Expressive — more 'actual' than 'virtual'.")

    # Phase offset analysis
    print(f"\n  ═══ PHASE OFFSET ANALYSIS ═══")
    # Set 3B = Set 3A rotated by 3 steps (or -1)
    print(f"  Set 3A mode pattern: R E E E")
    print(f"  Set 3B mode pattern: E E E R")
    print(f"  Offset: Set 3B = Set 3A shifted by 3 steps (≡ -1 step)")
    print(f"  In angular terms: 3/4 × 360° = 270° (or equivalently -90°)")
    print(f"  This is NOT 180° (which would be the 'opposite' phase).")
    print(f"  Instead, it's a lead-lag relationship: B leads A by 270° = lags by 90°.")
    print()


def display_comparison():
    """Compare System 3 and System 4 side by side."""
    print("\n" + "█" * 90)
    print("█  SIMPLEX HIERARCHY COMPARISON — System 3 vs System 4")
    print("█" * 90)

    print(f"""
  ┌────────────────────────┬──────────────────────┬──────────────────────────┐
  │  Property              │  System 3            │  System 4                │
  ├────────────────────────┼──────────────────────┼──────────────────────────┤
  │  Simplex               │  Triangle (2-simplex)│  Tetrahedron (3-simplex) │
  │  Pascal Row            │  [1, 3, 3, 1]        │  [1, 4, 6, 4, 1]        │
  │  Sum                   │  8                   │  16                      │
  │  Nesting               │  (((a)b)c)           │  ((((a)b)c)d)            │
  │  Base                  │  base[5]             │  base[10]                │
  │  Decomposition         │  (4)(2)(1,3)         │  (9)(3,6)(1,2,4,5,7,8)  │
  ├────────────────────────┼──────────────────────┼──────────────────────────┤
  │  Vertices v(N)         │  3  {{a,b,c}}          │  4  {{a,b,c,d}}            │
  │  Edges e(N)            │  3  {{ab,ac,bc}}       │  6  {{ab,ac,ad,bc,bd,cd}}  │
  │  Faces f(N)            │  1  {{abc}}            │  4  {{abc,abd,acd,bcd}}    │
  │  Cells c(N)            │  —                   │  1  {{abcd}}               │
  ├────────────────────────┼──────────────────────┼──────────────────────────┤
  │  Particular terms      │  2  {{1,3}}            │  6  {{1,2,4,5,7,8}}       │
  │  Polar pairs           │  1  [1(3)]           │  3  [1(8)],[4(5)],[7(2)] │
  │  Concurrent threads    │  2                   │  3                       │
  │  Steps per cycle       │  4                   │  12                      │
  │  Mode split            │  3E + 1R             │  7E + 5R                 │
  │  E ratio               │  75%                 │  58.3%                   │
  │  R ratio               │  25%                 │  41.7%                   │
  │  Neutron density       │  1 per 4 steps       │  5 per 12 steps          │
  ├────────────────────────┼──────────────────────┼──────────────────────────┤
  │  Phase offset          │  270° (3/4 cycle)    │  120° (4/12 cycle)       │
  │  Simultaneity          │  Partial (2/4 mixed) │  Full (12/12 mixed)      │
  │  Self-grounding        │  ✓ (no ext. ground)  │  ✓ (no ext. ground)      │
  └────────────────────────┴──────────────────────┴──────────────────────────┘
""")

    # The scaling law
    print("  ═══ SCALING LAW ═══")
    print("  System N uses the (N-1)-simplex with Pascal row [C(N-1, k)].")
    print("  The f-vector sum = 2^(N-1) (total elements including void).")
    print()
    for n in range(2, 8):
        row = pascal_row(n - 1)
        total = sum(row)
        dim = n - 1
        simplex_name = {1: "Line segment", 2: "Triangle", 3: "Tetrahedron",
                        4: "5-cell (Pentachoron)", 5: "5-simplex",
                        6: "6-simplex"}.get(dim, f"{dim}-simplex")
        print(f"    System {n}: [{', '.join(str(x) for x in row)}] "
              f"= {total}  ({simplex_name})")

    print()


def display_symmetry_groups():
    """Display the symmetry group structure."""
    print("\n" + "═" * 90)
    print("  SYMMETRY GROUPS — The Tetrahedral Mirrorhouse")
    print("═" * 90)

    print(f"""
  The symmetry group of the (N-1)-simplex is the Symmetric Group S_N.

  System 3 (Triangle):
    S_3 has |S_3| = 3! = 6 elements
    Decomposition: 3 rotations (C_3) + 3 reflections (dihedral D_3)
    Cyclic subgroup C_3: {{e, (abc), (acb)}} — the 3-step rotation
    The 2 threads correspond to the 2 generators of D_3

  System 4 (Tetrahedron):
    S_4 has |S_4| = 4! = 24 elements
    Decomposition into conjugacy classes:
      1 identity
      6 transpositions (2-cycles)        — edge swaps
      8 3-cycles                         — face rotations
      3 double transpositions (2+2)      — edge-pair swaps
      6 4-cycles                         — vertex permutations
    
    Subgroups:
      A_4 (alternating, |A_4|=12) — the 12-step cycle!
      V_4 (Klein four, |V_4|=4)  — the 4 nesting levels
      S_3 (|S_3|=6)              — the 6 particular terms
      C_3 (|C_3|=3)              — the 3 concurrent threads
      C_2 (|C_2|=2)              — the E/R duality

    The 12-step cycle = |A_4| = the alternating group!
    The roto-reflections of the tetrahedron ARE the cycle transformations.
""")


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main():
    display_system3()
    display_comparison()
    display_symmetry_groups()

    # Export data for visualization
    data = {
        "system3": {
            "pascal": System3.PASCAL,
            "nesting": System3.NESTING,
            "cycle_length": System3.CYCLE_LENGTH,
            "num_threads": System3.NUM_THREADS,
            "set_a": [(t, m.name) for t, m in System3.SET_A],
            "set_b": [(t, m.name) for t, m in System3.SET_B],
            "validation": System3.validate(),
        },
        "system4": {
            "pascal": System4.PASCAL,
            "nesting": System4.NESTING,
            "cycle_length": System4.CYCLE_LENGTH,
            "num_threads": System4.NUM_THREADS,
        },
    }

    # Convert sets to serializable
    def convert(obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, Mode):
            return obj.name
        raise TypeError(f"Not serializable: {type(obj)}")

    with open("/home/ubuntu/demo/simplex_data.json", "w") as f:
        json.dump(data, f, indent=2, default=convert)
    print("  Data exported to simplex_data.json\n")


if __name__ == "__main__":
    main()
