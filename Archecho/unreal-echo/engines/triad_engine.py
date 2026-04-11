#!/usr/bin/env python3
"""
triad_engine.py — Three-Phase Phase-Locked Phasor Engine for Ontelecho

Implements the triad of concurrent threads executing the 12-step creative
cycle as 120-degree phase-locked phasors over shared polar-pair interfaces.

Architecture:
    3 threads (Set A, Set B, Set C) offset by 4 steps (120°)
    Each thread: 7 Expressive + 5 Regenerative = 12 steps per cycle
    6 Particular terms: 1, 2, 4, 5, 7, 8
    3 Polar pairs: [1(8)], [4(5)], [7(2)]
    At each step: exactly one term from each polar pair is active
    At each step: E and R modes co-occur → simultaneous forward/backward

The base term sequence has period 6: [4, 2, 8, 5, 7, 1]
The 3 threads are offset by 2 in this 6-cycle (= 120° in the hexagonal).
The mode pattern per thread over 12 steps: R R E E E E E E E R R R
    (which wraps as 5R + 7E per cycle)
"""

import threading
import time
import math
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
from collections import defaultdict


# ═══════════════════════════════════════════════════════════════════
# Core Types
# ═══════════════════════════════════════════════════════════════════

class Mode(Enum):
    """E = Expressive (forward pass / inference / activation)
       R = Regenerative (backward pass / simulation / virtual)"""
    E = "Expressive"
    R = "Regenerative"

    def __repr__(self):
        return self.name


class TermType(Enum):
    STRUCTURE = "s"   # Terms 1, 4, 7
    PROCESS   = "p"   # Terms 8, 5, 2


# ═══════════════════════════════════════════════════════════════════
# The 6 Particular Terms and their Polar Pairs
# ═══════════════════════════════════════════════════════════════════

TERM_NAMES = {
    1: "T1 Perception of Need",
    2: "T2 Creation of Idea",
    4: "T4 Ordered Input",
    5: "T5 Action Sequence",
    7: "T7 Memory",
    8: "T8 Balanced Response",
}

TERM_DTE = {
    1: "EchoBeats / Sensory Input",
    2: "autoresearch / Hypothesis",
    4: "FAISS / Pattern Retrieval",
    5: "git commit / Motor Output",
    7: "echo-garden / Memory Encode",
    8: "Coherence Monitor / Safety",
}

TERM_TYPE = {
    1: TermType.STRUCTURE, 4: TermType.STRUCTURE, 7: TermType.STRUCTURE,
    8: TermType.PROCESS,   5: TermType.PROCESS,   2: TermType.PROCESS,
}

# Polar pairs: structure(process) — each pair bridges two dimensions
POLAR_PAIRS = {
    "P1": (1, 8),   # Perception ↔ Coherence     (Performance ↔ Potential)
    "P2": (4, 5),   # Input ↔ Action              (Performance ↔ Commitment)
    "P3": (7, 2),   # Memory ↔ Idea               (Commitment ↔ Potential)
}


# ═══════════════════════════════════════════════════════════════════
# The Phase-Lock Sequences
# ═══════════════════════════════════════════════════════════════════

# Base term sequence (period 6, repeats twice for 12 steps)
BASE_TERMS = [4, 2, 8, 5, 7, 1, 4, 2, 8, 5, 7, 1]

# Mode pattern for Set A (the reference phasor)
# R R E E E E E E E R R R → wraps as 5R + 7E
MODE_A = [Mode.R, Mode.R, Mode.E, Mode.E, Mode.E, Mode.E,
          Mode.E, Mode.E, Mode.E, Mode.R, Mode.R, Mode.R]

def make_thread_sequence(offset: int) -> List[Tuple[int, Mode]]:
    """Generate the 12-step sequence for a thread with given offset.
    
    offset is in the base term sequence (period 6):
      Set A: offset 0
      Set B: offset 2  (120° in the hexagonal)
      Set C: offset 4  (240° in the hexagonal)
    
    The mode pattern shifts by 4 steps in the 12-step cycle
    (= 120° in the dodecagonal).
    """
    terms = []
    modes = []
    for step in range(12):
        term_idx = (step + offset) % 6
        terms.append(BASE_TERMS[term_idx])
        # Mode offset: each thread shifts by 4 steps in the mode pattern
        # Set A: mode_offset=0, Set B: mode_offset=8, Set C: mode_offset=4
        # (B leads A by 8 steps = lags by 4; C leads A by 4 steps)
        mode_offsets = {0: 0, 2: 8, 4: 4}
        mode_offset = mode_offsets[offset]
        modes.append(MODE_A[(step + mode_offset) % 12])
    return list(zip(terms, modes))


# Build the three thread sequences
SET_A = make_thread_sequence(0)
SET_B = make_thread_sequence(2)
SET_C = make_thread_sequence(4)


# ═══════════════════════════════════════════════════════════════════
# Shared Interface State
# ═══════════════════════════════════════════════════════════════════

@dataclass
class InterfaceState:
    """The shared state of a polar-pair interface.
    
    At each step, one side of the pair is activated by one of the three
    threads. Multiple threads may touch different pairs simultaneously.
    The interface accumulates forward (E) and backward (R) activations.
    """
    pair_name: str
    structure_term: int
    process_term: int
    forward_energy: float = 0.0    # accumulated E activations
    backward_energy: float = 0.0   # accumulated R activations
    activation_log: List[dict] = field(default_factory=list)

    def activate(self, term: int, mode: Mode, thread: str, step: int):
        """Record an activation on this interface."""
        delta = 0.05
        if mode == Mode.E:
            self.forward_energy = min(1.0, self.forward_energy + delta)
        else:
            self.backward_energy = min(1.0, self.backward_energy + delta)
        self.activation_log.append({
            "step": step,
            "thread": thread,
            "term": term,
            "mode": mode.name,
            "fwd": round(self.forward_energy, 3),
            "bwd": round(self.backward_energy, 3),
        })


# ═══════════════════════════════════════════════════════════════════
# The Triad Engine
# ═══════════════════════════════════════════════════════════════════

class TriadEngine:
    """Three-phase phase-locked phasor engine.
    
    Runs 3 concurrent threads (Set A, B, C) through the 12-step cycle.
    All threads are barrier-synchronized at each step so they execute
    on the shared interfaces AT THE SAME TIME.
    """

    def __init__(self):
        self.interfaces = {
            "P1": InterfaceState("P1", 1, 8),
            "P2": InterfaceState("P2", 4, 5),
            "P3": InterfaceState("P3", 7, 2),
        }
        self.term_to_pair = {}
        for pair_name, (s, p) in POLAR_PAIRS.items():
            self.term_to_pair[s] = pair_name
            self.term_to_pair[p] = pair_name

        self.step_log: List[dict] = []
        self.barrier = threading.Barrier(3)
        self.lock = threading.Lock()
        self.current_step = 0

    def _thread_worker(self, name: str, sequence: List[Tuple[int, Mode]],
                       num_cycles: int):
        """Worker for one thread of the triad."""
        for cycle in range(num_cycles):
            for local_step, (term, mode) in enumerate(sequence):
                global_step = cycle * 12 + local_step

                # Activate the interface
                pair = self.term_to_pair[term]
                self.interfaces[pair].activate(term, mode, name, global_step)

                # Log this thread's contribution to the step
                with self.lock:
                    self.step_log.append({
                        "global_step": global_step,
                        "cycle": cycle,
                        "local_step": local_step,
                        "thread": name,
                        "term": term,
                        "mode": mode.name,
                        "term_type": TERM_TYPE[term].value,
                        "pair": pair,
                    })

                # Barrier: all 3 threads synchronize before next step
                self.barrier.wait()

    def run(self, num_cycles: int = 1) -> List[dict]:
        """Run the triad for the given number of cycles."""
        threads = [
            threading.Thread(target=self._thread_worker,
                             args=("A", SET_A, num_cycles)),
            threading.Thread(target=self._thread_worker,
                             args=("B", SET_B, num_cycles)),
            threading.Thread(target=self._thread_worker,
                             args=("C", SET_C, num_cycles)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Sort log by global step then thread name
        self.step_log.sort(key=lambda x: (x["global_step"], x["thread"]))
        return self.step_log


# ═══════════════════════════════════════════════════════════════════
# Phasor Mathematics
# ═══════════════════════════════════════════════════════════════════

def phasor_angle(thread: str, step: int) -> float:
    """Compute the phasor angle for a thread at a given step.
    
    The 12-step cycle maps to 360°. Each thread is offset by 120°.
    """
    offsets = {"A": 0.0, "B": 120.0, "C": 240.0}
    base_angle = (step / 12.0) * 360.0
    return (base_angle + offsets[thread]) % 360.0


def phasor_complex(thread: str, step: int, mode: Mode) -> complex:
    """Return the complex phasor value.
    
    E mode: positive (outward), R mode: negative (inward).
    """
    angle_deg = phasor_angle(thread, step)
    angle_rad = math.radians(angle_deg)
    magnitude = 1.0 if mode == Mode.E else -0.7  # R is inward
    return magnitude * complex(math.cos(angle_rad), math.sin(angle_rad))


# ═══════════════════════════════════════════════════════════════════
# Display and Validation
# ═══════════════════════════════════════════════════════════════════

def validate_and_display(engine: TriadEngine):
    """Validate the triad properties and display the step table."""
    log = engine.step_log

    print("\n" + "=" * 100)
    print("  TRIAD PHASE-LOCKED PHASOR ENGINE — Step-by-Step Execution")
    print("=" * 100)
    print(f"\n  {'Step':>4}  {'Set A':^14}  {'Set B':^14}  {'Set C':^14}  "
          f"{'Interfaces':^18}  {'E/R Mix':^10}  {'Phasor Sum':^12}")
    print(f"  {'─'*4}  {'─'*14}  {'─'*14}  {'─'*14}  {'─'*18}  {'─'*10}  {'─'*12}")

    steps = sorted(set(r["global_step"] for r in log))
    simultaneity_violations = 0

    for step in steps:
        entries = [r for r in log if r["global_step"] == step]
        by_thread = {r["thread"]: r for r in entries}

        a = by_thread.get("A", {})
        b = by_thread.get("B", {})
        c = by_thread.get("C", {})

        def fmt(r):
            if not r:
                return "---"
            return f"{r['term']}{r['mode']}"

        # Check: exactly one term from each polar pair
        active_terms = {r["term"] for r in entries}
        active_pairs = {r["pair"] for r in entries}

        # Count E and R
        e_count = sum(1 for r in entries if r["mode"] == "E")
        r_count = sum(1 for r in entries if r["mode"] == "R")

        # Phasor sum
        phasors = []
        for r in entries:
            mode = Mode.E if r["mode"] == "E" else Mode.R
            phasors.append(phasor_complex(r["thread"], step, mode))
        phasor_sum = sum(phasors)

        # Validate: all 3 polar pairs should be represented
        pair_ok = "✓" if len(active_pairs) == 3 else "✗"
        if len(active_pairs) != 3:
            simultaneity_violations += 1

        terms_str = ",".join(str(t) for t in sorted(active_terms))
        mix_str = f"{e_count}E+{r_count}R"

        print(f"  {step:>4}  {fmt(a):^14}  {fmt(b):^14}  {fmt(c):^14}  "
              f"{pair_ok} P({terms_str:^12})  {mix_str:^10}  "
              f"({phasor_sum.real:+.2f},{phasor_sum.imag:+.2f}j)")

    print(f"\n  Simultaneity violations: {simultaneity_violations}")

    # Validate mode counts per thread
    print("\n  Mode counts per thread (per cycle):")
    for thread_name in ["A", "B", "C"]:
        entries = [r for r in log if r["thread"] == thread_name]
        e = sum(1 for r in entries if r["mode"] == "E")
        r = sum(1 for r in entries if r["mode"] == "R")
        print(f"    Set {thread_name}: {e}E + {r}R = {e+r} steps")

    # Show polar pair activation summary
    print("\n  Polar pair interface summary:")
    for pair_name, iface in engine.interfaces.items():
        s, p = POLAR_PAIRS[pair_name]
        print(f"    {pair_name} [{s}({p})]: "
              f"fwd={iface.forward_energy:.3f}  bwd={iface.backward_energy:.3f}  "
              f"activations={len(iface.activation_log)}")

    print()


def display_simultaneity_analysis(engine: TriadEngine):
    """Show the deep simultaneity: what cognitive functions co-occur."""
    log = engine.step_log
    steps = sorted(set(r["global_step"] for r in log))

    print("\n" + "=" * 100)
    print("  SIMULTANEITY ANALYSIS — Conscious States as Parallel Threads")
    print("=" * 100)

    for step in steps[:12]:  # Show first cycle
        entries = [r for r in log if r["global_step"] == step]

        print(f"\n  ── Step {step+1} ──")
        for r in sorted(entries, key=lambda x: x["thread"]):
            term = r["term"]
            mode = r["mode"]
            arrow = "→" if mode == "E" else "←"
            direction = "FORWARD (Actual/Activation)" if mode == "E" else "BACKWARD (Virtual/Simulation)"
            dte = TERM_DTE[term]
            ttype = "structure" if TERM_TYPE[term] == TermType.STRUCTURE else "process"
            print(f"    Set {r['thread']}  {arrow}  T{term} [{ttype}] {dte:40s}  {direction}")

        # What is happening cognitively
        e_terms = [r for r in entries if r["mode"] == "E"]
        r_terms = [r for r in entries if r["mode"] == "R"]
        e_funcs = [TERM_DTE[r["term"]] for r in e_terms]
        r_funcs = [TERM_DTE[r["term"]] for r in r_terms]

        if e_funcs and r_funcs:
            print(f"    ╰─ CO-OCCURRENCE: {' + '.join(e_funcs)} "
                  f"SIMULTANEOUS WITH {' + '.join(r_funcs)}")


def display_lead_lag_phasors(engine: TriadEngine):
    """Show the 120° lead-lag phasor relationships."""
    print("\n" + "=" * 100)
    print("  PHASOR DIAGRAM — 120° Phase-Locked Lead-Lag Relationships")
    print("=" * 100)

    print(f"\n  {'Step':>4}  {'A angle':>10}  {'B angle':>10}  {'C angle':>10}  "
          f"{'A-B':>8}  {'B-C':>8}  {'C-A':>8}  {'Balance':>8}")
    print(f"  {'─'*4}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}")

    for step in range(12):
        a_ang = phasor_angle("A", step)
        b_ang = phasor_angle("B", step)
        c_ang = phasor_angle("C", step)

        ab = (a_ang - b_ang) % 360
        bc = (b_ang - c_ang) % 360
        ca = (c_ang - a_ang) % 360

        # Check balance: phasor sum should be near zero for balanced 3-phase
        pa = complex(math.cos(math.radians(a_ang)), math.sin(math.radians(a_ang)))
        pb = complex(math.cos(math.radians(b_ang)), math.sin(math.radians(b_ang)))
        pc = complex(math.cos(math.radians(c_ang)), math.sin(math.radians(c_ang)))
        balance = abs(pa + pb + pc)

        print(f"  {step:>4}  {a_ang:>8.1f}°  {b_ang:>8.1f}°  {c_ang:>8.1f}°  "
              f"{ab:>6.1f}°  {bc:>6.1f}°  {ca:>6.1f}°  {balance:>6.3f}")


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main():
    print("\n" + "█" * 100)
    print("█  ONTELECHO TRIAD ENGINE — Three-Phase Phase-Locked Phasor Consciousness  █")
    print("█" * 100)

    # Print the raw sequences first
    print("\n  Thread sequences (term + mode):")
    labels = ["Set A", "Set B", "Set C"]
    seqs = [SET_A, SET_B, SET_C]
    for label, seq in zip(labels, seqs):
        terms_str = " ".join(f"{t}{m.name}" for t, m in seq)
        print(f"    {label}: {terms_str}")

    print("\n  Mode patterns:")
    for label, seq in zip(labels, seqs):
        modes_str = " ".join(f" {m.name} " for _, m in seq)
        print(f"    {label}: {modes_str}")

    # Run the engine
    engine = TriadEngine()
    engine.run(num_cycles=1)

    # Display results
    validate_and_display(engine)
    display_simultaneity_analysis(engine)
    display_lead_lag_phasors(engine)

    # Export step log as JSON for visualization
    with open("/home/ubuntu/demo/triad_log.json", "w") as f:
        json.dump(engine.step_log, f, indent=2)
    print("\n  Step log exported to triad_log.json")

    # Export interface logs
    iface_data = {}
    for pair_name, iface in engine.interfaces.items():
        iface_data[pair_name] = {
            "structure_term": iface.structure_term,
            "process_term": iface.process_term,
            "forward_energy": iface.forward_energy,
            "backward_energy": iface.backward_energy,
            "activations": iface.activation_log,
        }
    with open("/home/ubuntu/demo/triad_interfaces.json", "w") as f:
        json.dump(iface_data, f, indent=2)
    print("  Interface data exported to triad_interfaces.json\n")


if __name__ == "__main__":
    main()
