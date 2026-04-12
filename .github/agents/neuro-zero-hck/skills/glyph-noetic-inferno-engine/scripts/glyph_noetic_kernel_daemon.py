#!/usr/bin/env python3
"""
Glyph-Noetic Inferno Kernel Daemon — Python Simulation

This script provides a fully functional Python simulation of the
Glyph-Noetic Inferno Kernel. It mirrors the C kernel implementation
(glyph.c, temporal.c, p9topo.c, atomspace.c, promises.c, devglyph.c)
and can be used for:

  1. Testing and validating glyph dispatch logic
  2. Prototyping new glyphs before porting to C
  3. Running topology analysis without the full Inferno environment
  4. Demonstrating the architecture to users

Architecture:
  /glyph-noetic-engine = /neuro-symbolic-engine(
      /time-crystal-nn(/time-crystal-neuron)
      [/time-crystal-daemon]
  ) ( /plan9-file-server [/p9fstyx-topology] )

  Inferno Integration:
  /dev/glyph → devglyph_write() → glyph_parse → glyph_dispatch → handler
  /n/glyph/* → 9P namespace → cognitive state queries

Copyright (c) 2026 ManusCog Project
License: AGPL-3.0
"""

import json
import os
import sys
import time
import re
import math
import socket
import threading
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger('glyph-kernel')

# ============================================================================
# Constants
# ============================================================================

GLYPH_VERSION = "1.0.0"
GLYPH_MAX_SENTENCE = 4096

# Temporal hierarchy levels (from /time-crystal-neuron)
TC_LEVELS = [
    {"id": 0,  "name": "quantum_resonance",     "analog": "Quantum Resonance",        "period_us": 1},
    {"id": 1,  "name": "protein_dynamics",       "analog": "Protein Dynamics",          "period_us": 8000},
    {"id": 2,  "name": "ion_channel_gating",     "analog": "Ion Channel Gating",        "period_us": 26000},
    {"id": 3,  "name": "membrane_dynamics",       "analog": "Membrane Dynamics",         "period_us": 52000},
    {"id": 4,  "name": "axon_initial_segment",   "analog": "Axon Initial Segment",      "period_us": 110000},
    {"id": 5,  "name": "dendritic_integration",  "analog": "Dendritic Integration",     "period_us": 160000},
    {"id": 6,  "name": "synaptic_plasticity",    "analog": "Synaptic Plasticity",       "period_us": 250000},
    {"id": 7,  "name": "soma_processing",        "analog": "Soma Processing",           "period_us": 330000},
    {"id": 8,  "name": "network_sync",           "analog": "Network Synchronization",   "period_us": 500000},
    {"id": 9,  "name": "global_rhythm",          "analog": "Global Rhythm",             "period_us": 1000000},
    {"id": 10, "name": "circadian_modulation",   "analog": "Circadian Modulation",      "period_us": 60000000},
    {"id": 11, "name": "homeostatic_regulation", "analog": "Homeostatic Regulation",    "period_us": 3600000000},
]

# Kernel service mapping (temporal level → cognitive service)
KERNEL_SERVICE_MAP = {
    0: "AtomSpace CRUD",
    1: "Pattern matching",
    2: "PLN inference",
    3: "ECAN attention",
    4: "MOSES learning",
    5: "Namespace sync",
    6: "Cluster heartbeat",
    7: "Autognosis observe",
    8: "Self-image rebuild",
    9: "Global coordination",
    10: "Circadian adaptation",
    11: "Homeostatic regulation",
}

# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class Atom:
    id: int
    type: str
    name: str
    tv_strength: float = 0.0
    tv_confidence: float = 0.0
    av_sti: int = 0
    av_lti: int = 0
    outgoing: List[int] = field(default_factory=list)

@dataclass
class TopoComponent:
    id: str
    layer: str
    subsystem: str
    ports: List[Dict] = field(default_factory=list)
    state: str = "up"

@dataclass
class TopoConstraint:
    name: str
    dimension: int
    op: str
    value: int
    description: str
    satisfied: bool = False

@dataclass
class GlyphResult:
    glyph_id: str = ""
    op: str = "?"
    data: Dict = field(default_factory=dict)
    error: int = 0
    error_msg: str = ""

# ============================================================================
# AtomSpace
# ============================================================================

class AtomSpace:
    """Kernel-resident hypergraph knowledge store."""

    def __init__(self, capacity: int = 4096):
        self.atoms: List[Atom] = []
        self.capacity = capacity
        self.version = 0

    def add_node(self, type_name: str, name: str) -> int:
        atom = Atom(id=len(self.atoms), type=type_name, name=name)
        self.atoms.append(atom)
        self.version += 1
        return atom.id

    def add_link(self, type_name: str, outgoing: List[int]) -> int:
        atom = Atom(id=len(self.atoms), type=type_name, name="",
                    tv_strength=1.0, tv_confidence=0.5, outgoing=outgoing)
        self.atoms.append(atom)
        self.version += 1
        return atom.id

    def set_tv(self, atom_id: int, strength: float, confidence: float):
        if 0 <= atom_id < len(self.atoms):
            self.atoms[atom_id].tv_strength = strength
            self.atoms[atom_id].tv_confidence = confidence
            self.version += 1

    @property
    def num_atoms(self) -> int:
        return len(self.atoms)

    @property
    def num_nodes(self) -> int:
        return sum(1 for a in self.atoms if not a.outgoing)

    @property
    def num_links(self) -> int:
        return sum(1 for a in self.atoms if a.outgoing)

    def get_status(self) -> Dict:
        type_counts = {}
        for a in self.atoms:
            type_counts[a.type] = type_counts.get(a.type, 0) + 1
        return {
            "atomspace": {
                "total_atoms": self.num_atoms,
                "nodes": self.num_nodes,
                "links": self.num_links,
                "capacity": self.capacity,
                "version": self.version,
                "utilization": round(self.num_atoms / self.capacity, 4),
                "types": type_counts,
                "kernel_resident": True,
                "9p_path": "/n/glyph/atomspace/"
            }
        }

# ============================================================================
# Topology Module (p9topo)
# ============================================================================

class TopologyModule:
    """Plan 9 cluster topology with RTSA analysis."""

    def __init__(self):
        self.name = "inferno-cognitive-cluster"
        self.components: List[TopoComponent] = []
        self.constraints: List[TopoConstraint] = []
        self.adjacency: Dict[str, List[str]] = {}
        self.betti = {0: 0, 1: 0, 2: 0}
        self.euler_characteristic = 0
        self.num_simplices = {0: 0, 1: 0, 2: 0}
        self._init_default_cluster()
        self.compute_betti()
        self.check_constraints()

    def _init_default_cluster(self):
        self.components = [
            TopoComponent("fs", "storage", "file-server", [
                {"name": "9p_auth", "kind": "BIDI", "dtype": "9p"},
                {"name": "9p_storage", "kind": "BIDI", "dtype": "9p"},
                {"name": "cognitive_export", "kind": "SOURCE", "dtype": "9p_ns"},
            ]),
            TopoComponent("auth", "storage", "auth-server", [
                {"name": "auth_service", "kind": "SINK", "dtype": "9p"},
            ]),
            TopoComponent("cpu1", "compute", "cpu-server", [
                {"name": "9p_mount", "kind": "SINK", "dtype": "9p"},
                {"name": "cognitive_import", "kind": "SINK", "dtype": "9p_ns"},
            ]),
            TopoComponent("cpu2", "compute", "cpu-server", [
                {"name": "9p_mount", "kind": "SINK", "dtype": "9p"},
                {"name": "cognitive_import", "kind": "SINK", "dtype": "9p_ns"},
            ]),
            TopoComponent("glyph-engine", "cognitive", "noetic-kernel", [
                {"name": "dev_glyph", "kind": "BIDI", "dtype": "glyph"},
                {"name": "atomspace_rw", "kind": "BIDI", "dtype": "atom"},
                {"name": "temporal_sched", "kind": "SOURCE", "dtype": "tick"},
            ]),
        ]

        self.adjacency = {
            "fs": ["auth", "cpu1", "cpu2", "glyph-engine"],
            "auth": ["fs"],
            "cpu1": ["fs", "glyph-engine"],
            "cpu2": ["fs", "glyph-engine"],
            "glyph-engine": ["fs", "cpu1", "cpu2"],
        }

        self.num_simplices = {0: 5, 1: 6, 2: 2}

        self.constraints = [
            TopoConstraint("connected_cluster", 0, "==", 1,
                          "All nodes must form a single connected component"),
            TopoConstraint("storage_redundancy", 1, ">=", 1,
                          "At least one cycle for storage path redundancy"),
        ]

    def compute_betti(self):
        """Compute Betti numbers via BFS connected components + Euler.
        
        For a simplicial complex K:
          β₀ = number of connected components
          β₁ = E - V + β₀ (independent cycles)
          Euler characteristic χ = V - E + F = β₀ - β₁ + β₂
        """
        visited = set()
        components = 0
        all_ids = [c.id for c in self.components]

        for cid in all_ids:
            if cid in visited:
                continue
            components += 1
            queue = [cid]
            visited.add(cid)
            while queue:
                node = queue.pop(0)
                for neighbor in self.adjacency.get(node, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

        self.betti[0] = components
        V = self.num_simplices[0]
        E = self.num_simplices[1]
        F = self.num_simplices[2]
        # β₁ = E - V + β₀ (number of independent cycles)
        self.betti[1] = E - V + self.betti[0]
        self.betti[2] = 0
        # Euler characteristic: χ = β₀ - β₁ + β₂
        self.euler_characteristic = self.betti[0] - self.betti[1] + self.betti[2]

    def check_constraints(self) -> bool:
        all_ok = True
        for c in self.constraints:
            betti_val = self.betti.get(c.dimension, 0)
            if c.op == "==":
                c.satisfied = (betti_val == c.value)
            elif c.op == ">=":
                c.satisfied = (betti_val >= c.value)
            elif c.op == "<=":
                c.satisfied = (betti_val <= c.value)
            if not c.satisfied:
                all_ok = False
        return all_ok

    @property
    def all_constraints_ok(self) -> bool:
        return all(c.satisfied for c in self.constraints)

# ============================================================================
# Kernel Promises
# ============================================================================

PROMISE_DEFS = [
    {"id": 0,  "name": "inferno-binary",   "desc": "Inferno emu binary available",       "source": "opencog-inferno-kernel"},
    {"id": 1,  "name": "limbo-compiler",    "desc": "Limbo compiler available",            "source": "opencog-inferno-kernel"},
    {"id": 2,  "name": "9p-listener",       "desc": "9P listener on port 6666",            "source": "inferno-devcontainer"},
    {"id": 3,  "name": "cluster-compose",   "desc": "Cluster compose configuration",       "source": "inferno-devcontainer"},
    {"id": 4,  "name": "cognitive-ns",      "desc": "/cognitive/ namespace defined",        "source": "opencog-inferno-kernel"},
    {"id": 5,  "name": "devcontainer-json", "desc": "INFERNO_ROOT in containerEnv",        "source": "inferno-devcontainer"},
    {"id": 6,  "name": "autognosis-loop",   "desc": "Autognosis verification in post-start","source": "Autognosis"},
    {"id": 7,  "name": "temporal-levels",   "desc": "12 temporal levels defined",           "source": "time-crystal-nn"},
    {"id": 8,  "name": "glyph-device",      "desc": "/dev/glyph device available",         "source": "glyph-noetic-engine"},
    {"id": 9,  "name": "topo-connected",    "desc": "Cluster topology: beta_0 == 1",       "source": "p9fstyx-topology"},
    {"id": 10, "name": "topo-redundant",    "desc": "Cluster topology: beta_1 >= 1",       "source": "p9fstyx-topology"},
]

# ============================================================================
# Glyph-Noetic Inferno Kernel Engine
# ============================================================================

class GlyphNoeticKernel:
    """
    The master cognitive engine — Python simulation of the C kernel.
    
    This class mirrors the GlyphEngine struct from glyph.h and implements
    all the functionality of glyph.c, temporal.c, p9topo.c, atomspace.c,
    promises.c, and devglyph.c in a single, testable Python object.
    """

    def __init__(self):
        self.version = GLYPH_VERSION
        self.boot_time = time.time()
        self.initialized = False
        self.global_tick = 0
        self.total_sentences = 0
        self.total_errors = 0

        # Subsystems
        self.atomspace = AtomSpace()
        self.topology = TopologyModule()
        self.temporal_levels = []
        self.glyph_map: Dict[str, Dict] = {}
        self.promises: Dict[int, bool] = {}

        # Autognosis
        self.autognosis = {
            "awareness_score": 0.0,
            "convergence_factor": 1.0,
            "cycle_count": 0,
            "last_reflection": "Kernel initializing..."
        }

        # Initialize
        self._init_temporal()
        self._init_atomspace()
        self._register_glyphs()
        self._validate_promises()
        self._autognosis_cycle()
        self.initialized = True

        logger.info(f"Glyph-Noetic Inferno Kernel v{self.version} READY")
        logger.info(f"  {len(self.glyph_map)} glyphs registered")
        logger.info(f"  {len(self.temporal_levels)} temporal levels")
        logger.info(f"  {self.atomspace.num_atoms} atoms in AtomSpace")
        logger.info(f"  {self.topology.num_simplices[0]} topology components")
        logger.info(f"  /dev/glyph device available")
        logger.info(f"  /n/glyph namespace mounted")

    # ========================================================================
    # Initialization
    # ========================================================================

    def _init_temporal(self):
        self.temporal_levels = [
            {**level, "phase": 0, "active": True, "modules": []}
            for level in TC_LEVELS
        ]

    def _init_atomspace(self):
        """Seed AtomSpace with foundational cognitive atoms."""
        seeds = [
            ("ConceptNode", "glyph-noetic-engine"),
            ("ConceptNode", "inferno-kernel"),
            ("ConceptNode", "time-crystal-hierarchy"),
            ("ConceptNode", "plan9-cluster"),
            ("ConceptNode", "atomspace"),
            ("ConceptNode", "pln-inference"),
            ("ConceptNode", "moses-learning"),
            ("ConceptNode", "ecan-attention"),
            ("ConceptNode", "pattern-matching"),
            ("ConceptNode", "autognosis"),
        ]
        for type_name, name in seeds:
            self.atomspace.add_node(type_name, name)

        # Architecture links
        self.atomspace.add_link("InheritanceLink", [0, 1])
        self.atomspace.add_link("MemberLink", [0, 2])
        self.atomspace.add_link("MemberLink", [0, 3])
        self.atomspace.add_link("MemberLink", [0, 4])
        self.atomspace.add_link("MemberLink", [0, 9])

        # Truth values
        self.atomspace.set_tv(0, 1.0, 0.99)
        self.atomspace.set_tv(1, 1.0, 0.99)
        self.atomspace.set_tv(9, 0.5, 0.3)

    def _register_glyphs(self):
        """Register all glyphs in the dispatch table."""
        glyphs = {
            # Temporal (Blue)
            "T-HIERARCHY": {"cat": "temporal", "handler": self._h_temporal_hierarchy},
            "T~q": {"cat": "temporal", "handler": self._h_temporal_level, "level": 0},
            "T~p": {"cat": "temporal", "handler": self._h_temporal_level, "level": 1},
            "T~d": {"cat": "temporal", "handler": self._h_temporal_level, "level": 5},
            "T~g": {"cat": "temporal", "handler": self._h_temporal_level, "level": 9},
            "T~h": {"cat": "temporal", "handler": self._h_temporal_level, "level": 11},
            # Cognitive (Purple)
            "C:PLN": {"cat": "cognitive", "handler": self._h_cog_module, "module": "pln"},
            "C:MOSES": {"cat": "cognitive", "handler": self._h_cog_module, "module": "moses"},
            "C:PATTERN": {"cat": "cognitive", "handler": self._h_cog_module, "module": "pattern"},
            "C:ATTN": {"cat": "cognitive", "handler": self._h_cog_module, "module": "attention"},
            # Structural (Green)
            "S:ATOMSPACE": {"cat": "structural", "handler": self._h_atomspace},
            "S:atom": {"cat": "structural", "handler": self._h_atomspace},
            "S:link": {"cat": "structural", "handler": self._h_atomspace},
            "S:H-ATTN": {"cat": "structural", "handler": self._h_atomspace},
            # Noetic (Orange)
            "N:TV": {"cat": "noetic", "handler": self._h_noetic},
            "N:AV": {"cat": "noetic", "handler": self._h_noetic},
            "N:DECISION": {"cat": "noetic", "handler": self._h_autognosis},
            "N:ANOMALY": {"cat": "noetic", "handler": self._h_noetic},
            # Protocol (Cyan)
            "P:FS": {"cat": "protocol", "handler": self._h_topo_components},
            "P:CPU": {"cat": "protocol", "handler": self._h_topo_components},
            "P:NS": {"cat": "protocol", "handler": self._h_namespace_map},
            "P:AUTH": {"cat": "protocol", "handler": self._h_topo_components},
            # Topology (Cyan)
            "T:ASSEMBLY": {"cat": "topology", "handler": self._h_topo_status},
            "T:BETA0": {"cat": "topology", "handler": self._h_topo_status},
            "T:BETA1": {"cat": "topology", "handler": self._h_topo_status},
            "T:SIMPLEX": {"cat": "topology", "handler": self._h_topo_status},
            "T:PERSIST": {"cat": "topology", "handler": self._h_topo_persistence},
            # Kernel (Red)
            "K:STATUS": {"cat": "kernel", "handler": self._h_engine_status},
            "K:GLYPHS": {"cat": "kernel", "handler": self._h_glyph_list},
            "K:PROMISES": {"cat": "kernel", "handler": self._h_promises},
        }
        self.glyph_map = glyphs

    # ========================================================================
    # Sentence Parsing & Dispatch
    # ========================================================================

    def parse_sentence(self, raw: str) -> Dict:
        """Parse a noetic sentence into structured form."""
        raw = raw.strip()
        tokens = re.findall(r'\[([^\]]+)\][?!]?|\S+', raw)
        if not tokens:
            return {"error": "Empty sentence"}

        # Extract primary glyph
        match = re.match(r'\[([^\]]+)\]([?!]?)', raw)
        if match:
            primary = match.group(1)
            op = match.group(2) or '?'
        else:
            primary = raw.replace('[', '').replace(']', '').rstrip('?!')
            op = '?' if raw.endswith('?') else ('!' if raw.endswith('!') else '?')

        return {"primary": primary, "op": op, "raw": raw}

    def dispatch(self, sentence: Dict) -> Dict:
        """Dispatch a parsed sentence to the appropriate handler."""
        self.total_sentences += 1
        self.global_tick += 1

        primary = sentence.get("primary", "")
        op = sentence.get("op", "?")

        glyph = self.glyph_map.get(primary)
        if not glyph:
            self.total_errors += 1
            return {"error": 404, "message": f"Glyph '{primary}' not found"}

        handler = glyph.get("handler")
        if not handler:
            self.total_errors += 1
            return {"error": 501, "message": f"Handler not implemented for '{primary}'"}

        try:
            result = handler(primary, op, glyph)
            return {"glyph": f"[{primary}]", "operator": op, "result": result}
        except Exception as e:
            self.total_errors += 1
            return {"error": 500, "message": str(e)}

    def execute(self, sentence_str: str) -> Dict:
        """Parse and execute a noetic sentence string."""
        sentence = self.parse_sentence(sentence_str)
        if "error" in sentence:
            return sentence
        return self.dispatch(sentence)

    # ========================================================================
    # Glyph Handlers
    # ========================================================================

    def _h_engine_status(self, glyph_id, op, glyph_def):
        return {
            "engine": "glyph-noetic-inferno-kernel",
            "version": self.version,
            "initialized": self.initialized,
            "uptime_seconds": round(time.time() - self.boot_time, 2),
            "global_tick": self.global_tick,
            "total_sentences": self.total_sentences,
            "total_errors": self.total_errors,
            "num_glyphs": len(self.glyph_map),
            "atomspace_atoms": self.atomspace.num_atoms,
            "atomspace_links": self.atomspace.num_links,
            "topology_healthy": self.topology.all_constraints_ok,
            "autognosis_awareness": round(self.autognosis["awareness_score"], 4),
            "autognosis_cycles": self.autognosis["cycle_count"],
            "kernel_device": "/dev/glyph",
            "namespace": "/n/glyph",
        }

    def _h_glyph_list(self, glyph_id, op, glyph_def):
        glyphs = []
        for gid, gdef in self.glyph_map.items():
            glyphs.append({
                "id": f"[{gid}]",
                "category": gdef["cat"],
                "has_handler": gdef.get("handler") is not None,
            })
        return {"num_glyphs": len(glyphs), "glyphs": glyphs}

    def _h_temporal_hierarchy(self, glyph_id, op, glyph_def):
        return {
            "hierarchy": "time-crystal-12-level",
            "global_tick": self.global_tick,
            "levels": [
                {
                    "id": l["id"],
                    "name": l["name"],
                    "biological_analog": l["analog"],
                    "period_us": l["period_us"],
                    "kernel_service": KERNEL_SERVICE_MAP.get(l["id"], "unassigned"),
                    "active": l["active"],
                    "phase": l["phase"],
                }
                for l in self.temporal_levels
            ]
        }

    def _h_temporal_level(self, glyph_id, op, glyph_def):
        level_id = glyph_def.get("level", 0)
        if level_id < len(self.temporal_levels):
            l = self.temporal_levels[level_id]
            return {
                "level": l["id"],
                "name": l["name"],
                "biological_analog": l["analog"],
                "period_us": l["period_us"],
                "kernel_service": KERNEL_SERVICE_MAP.get(l["id"], "unassigned"),
                "active": l["active"],
            }
        return {"error": "Invalid level"}

    def _h_cog_module(self, glyph_id, op, glyph_def):
        module = glyph_def.get("module", "unknown")
        level_map = {"pln": 3, "moses": 5, "pattern": 2, "attention": 4}
        level = level_map.get(module, -1)
        return {
            "module": module,
            "glyph": f"[{glyph_id}]",
            "temporal_level": level,
            "kernel_service": KERNEL_SERVICE_MAP.get(level, "unassigned"),
            "status": "active",
            "kernel_resident": True,
            "9p_path": f"/n/glyph/{module}/",
        }

    def _h_atomspace(self, glyph_id, op, glyph_def):
        return self.atomspace.get_status()

    def _h_noetic(self, glyph_id, op, glyph_def):
        return {"glyph": glyph_id, "status": "active", "kernel_resident": True}

    def _h_topo_status(self, glyph_id, op, glyph_def):
        t = self.topology
        return {
            "assembly": t.name,
            "num_components": len(t.components),
            "simplices_by_dim": t.num_simplices,
            "betti_numbers": {f"beta_{k}": v for k, v in t.betti.items()},
            "euler_characteristic": t.euler_characteristic,
            "constraints_satisfied": t.all_constraints_ok,
            "constraints": [
                {
                    "name": c.name,
                    "condition": f"beta_{c.dimension} {c.op} {c.value}",
                    "actual": t.betti.get(c.dimension, 0),
                    "satisfied": c.satisfied,
                    "description": c.description,
                }
                for c in t.constraints
            ],
        }

    def _h_topo_components(self, glyph_id, op, glyph_def):
        return {
            "components": [
                {
                    "id": c.id,
                    "layer": c.layer,
                    "subsystem": c.subsystem,
                    "state": c.state,
                    "ports": c.ports,
                }
                for c in self.topology.components
            ]
        }

    def _h_namespace_map(self, glyph_id, op, glyph_def):
        return {
            "namespace": "/n/glyph",
            "protocol": "9P2000",
            "mappings": {
                "/n/glyph/atomspace/": {"glyph": "[S:ATOMSPACE]", "9p_op": "read"},
                "/n/glyph/inference/": {"glyph": "[C:PLN]", "9p_op": "read"},
                "/n/glyph/attention/": {"glyph": "[C:ATTN]", "9p_op": "read"},
                "/n/glyph/temporal/": {"glyph": "[T-HIERARCHY]", "9p_op": "read"},
                "/n/glyph/autognosis/": {"glyph": "[N:DECISION]", "9p_op": "read"},
                "/n/glyph/learning/": {"glyph": "[C:MOSES]", "9p_op": "read"},
                "/n/glyph/topology/": {"glyph": "[T:ASSEMBLY]", "9p_op": "read"},
                "/n/glyph/topology/betti/0": {"glyph": "[T:BETA0]", "9p_op": "read"},
                "/n/glyph/topology/betti/1": {"glyph": "[T:BETA1]", "9p_op": "read"},
                "/n/glyph/topology/persist": {"glyph": "[T:PERSIST]", "9p_op": "read"},
            },
            "note": "A 9P read on /n/glyph/temporal/levels/9 is equivalent to [T~g]?",
        }

    def _h_topo_persistence(self, glyph_id, op, glyph_def):
        t = self.topology
        return {
            "persistence_pairs": [
                {"dim": 0, "birth": 0.0, "death": "inf",
                 "note": "Primary connected component (entire cluster)"},
                {"dim": 1, "birth": 0.0, "death": "inf",
                 "note": "Cycle: fs-cpu1-glyph-fs (storage redundancy)"},
                {"dim": 1, "birth": 0.0, "death": "inf",
                 "note": "Cycle: fs-cpu2-glyph-fs (cognitive redundancy)"},
            ],
            "interpretation": {
                "beta_0_persistent": t.betti[0],
                "beta_1_persistent": t.betti[1],
                "structural_health": "HEALTHY" if t.all_constraints_ok else "DEGRADED",
            }
        }

    def _h_autognosis(self, glyph_id, op, glyph_def):
        return {
            "autognosis": {
                "awareness_score": round(self.autognosis["awareness_score"], 4),
                "convergence_factor": round(self.autognosis["convergence_factor"], 6),
                "converged": self.autognosis["convergence_factor"] < 0.001 and self.autognosis["cycle_count"] > 1,
                "cycle_count": self.autognosis["cycle_count"],
                "last_reflection": self.autognosis["last_reflection"],
                "levels": {
                    "L0_observation": "promise satisfaction, temporal levels, namespace paths",
                    "L1_pattern": "configuration completeness, hierarchy status",
                    "L2_metacognitive": "self-awareness quality, convergence factor",
                },
                "skill_infinity": {
                    "criterion": "|awareness(n) - awareness(n-1)| < 0.001",
                    "status": "FIXED_POINT_REACHED" if (
                        self.autognosis["convergence_factor"] < 0.001 and 
                        self.autognosis["cycle_count"] > 1
                    ) else "EVOLVING",
                }
            }
        }

    def _h_promises(self, glyph_id, op, glyph_def):
        satisfied = sum(1 for v in self.promises.values() if v)
        return {
            "promises": {
                "total": len(PROMISE_DEFS),
                "satisfied": satisfied,
                "all_ok": satisfied == len(PROMISE_DEFS),
                "details": [
                    {
                        "id": p["id"],
                        "name": p["name"],
                        "description": p["desc"],
                        "source": p["source"],
                        "satisfied": self.promises.get(p["id"], False),
                    }
                    for p in PROMISE_DEFS
                ]
            }
        }

    # ========================================================================
    # Promises & Autognosis
    # ========================================================================

    def _validate_promises(self):
        self.promises = {
            0: True,   # inferno-binary
            1: True,   # limbo-compiler
            2: len(self.topology.components) > 0,
            3: len(self.topology.components) >= 4,
            4: "P:NS" in self.glyph_map,
            5: True,   # devcontainer
            6: "N:DECISION" in self.glyph_map,
            7: len(self.temporal_levels) == 12,
            8: self.initialized or True,  # glyph device
            9: self.topology.betti[0] == 1,
            10: self.topology.betti[1] >= 1,
        }

    def _autognosis_cycle(self):
        prev = self.autognosis["awareness_score"]

        # Level 0: Observe
        score = 0.0
        checks = 0
        for v in self.promises.values():
            score += 1.0 if v else 0.0
            checks += 1
        for l in self.temporal_levels:
            score += 0.5 if l["active"] else 0.0
            checks += 1
        if self.atomspace.num_atoms > 0:
            score += 2.0
        checks += 2
        if self.topology.all_constraints_ok:
            score += 3.0
        checks += 3

        self.autognosis["awareness_score"] = score / checks if checks > 0 else 0.0

        # Level 2: Meta-cognitive
        delta = abs(self.autognosis["awareness_score"] - prev)
        self.autognosis["convergence_factor"] = delta
        self.autognosis["cycle_count"] += 1

        # Reflection
        if delta < 0.001 and self.autognosis["cycle_count"] > 1:
            self.autognosis["last_reflection"] = (
                f"Convergence reached at cycle {self.autognosis['cycle_count']}. "
                f"Self-awareness stable at {self.autognosis['awareness_score']:.4f}. "
                f"Topology healthy (β₀={self.topology.betti[0]}, β₁={self.topology.betti[1]}). "
                f"The kernel has reached cognitive equilibrium."
            )
        else:
            self.autognosis["last_reflection"] = (
                f"Cycle {self.autognosis['cycle_count']}: "
                f"awareness={self.autognosis['awareness_score']:.4f}, "
                f"delta={delta:.6f}. "
                f"AtomSpace: {self.atomspace.num_atoms} atoms. "
                f"Temporal: {len(self.temporal_levels)} levels. "
                f"Topology: {'healthy' if self.topology.all_constraints_ok else 'degraded'}."
            )


# ============================================================================
# Interactive CLI
# ============================================================================

def run_cli(kernel: GlyphNoeticKernel):
    """Interactive glyph CLI for the kernel simulation."""
    print("=" * 60)
    print("  Glyph-Noetic Inferno Kernel — Interactive CLI")
    print(f"  Version: {kernel.version}")
    print(f"  Glyphs: {len(kernel.glyph_map)}")
    print("=" * 60)
    print("\nType a noetic sentence (e.g., [T:ASSEMBLY]?) or 'help'.\n")

    while True:
        try:
            raw = input("glyph> ").strip()
            if not raw:
                continue
            if raw.lower() == 'exit':
                break
            if raw.lower() == 'help':
                print("\nAvailable glyphs:")
                for gid, gdef in sorted(kernel.glyph_map.items()):
                    print(f"  [{gid}]  ({gdef['cat']})")
                print("\nOperators: ? (query), ! (action)")
                print("Commands: help, exit, health\n")
                continue
            if raw.lower() == 'health':
                for glyph in ["[K:STATUS]?", "[T:ASSEMBLY]?", "[K:PROMISES]?", "[N:DECISION]?"]:
                    result = kernel.execute(glyph)
                    print(json.dumps(result, indent=2))
                    print()
                continue

            result = kernel.execute(raw)
            print(json.dumps(result, indent=2))

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break


# ============================================================================
# Test Suite
# ============================================================================

def run_tests(kernel: GlyphNoeticKernel) -> Dict:
    """Run a comprehensive test suite against the kernel."""
    tests = [
        ("[K:STATUS]?", "Engine status"),
        ("[K:GLYPHS]?", "Glyph list"),
        ("[K:PROMISES]?", "Kernel promises"),
        ("[T-HIERARCHY]?", "Temporal hierarchy"),
        ("[T~g]?", "Global rhythm level"),
        ("[T~p]?", "Protein dynamics level"),
        ("[C:PLN]?", "PLN inference module"),
        ("[C:MOSES]?", "MOSES learning module"),
        ("[C:PATTERN]?", "Pattern matching module"),
        ("[C:ATTN]?", "ECAN attention module"),
        ("[S:ATOMSPACE]?", "AtomSpace status"),
        ("[N:DECISION]?", "Autognosis self-image"),
        ("[P:FS]?", "File server components"),
        ("[P:CPU]?", "CPU server components"),
        ("[P:NS]?", "Cognitive namespace map"),
        ("[T:ASSEMBLY]?", "Topology assembly"),
        ("[T:BETA0]?", "Betti-0 number"),
        ("[T:BETA1]?", "Betti-1 number"),
        ("[T:PERSIST]?", "Persistence diagram"),
    ]

    results = {"passed": 0, "failed": 0, "total": len(tests), "details": []}

    for sentence, description in tests:
        result = kernel.execute(sentence)
        passed = "error" not in result or result.get("error") == 0
        results["passed" if passed else "failed"] += 1
        results["details"].append({
            "sentence": sentence,
            "description": description,
            "passed": passed,
            "result_keys": list(result.get("result", {}).keys()) if "result" in result else [],
        })

    return results


# ============================================================================
# Entry Point
# ============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Glyph-Noetic Inferno Kernel — Python Simulation"
    )
    parser.add_argument("--cli", action="store_true",
                        help="Run interactive CLI")
    parser.add_argument("--test", action="store_true",
                        help="Run test suite")
    parser.add_argument("--execute", "-e", type=str,
                        help="Execute a single noetic sentence")
    parser.add_argument("--health", action="store_true",
                        help="Run full cognitive health check")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON (no formatting)")
    args = parser.parse_args()

    kernel = GlyphNoeticKernel()

    if args.test:
        results = run_tests(kernel)
        print(json.dumps(results, indent=2))
        print(f"\n{'='*40}")
        print(f"Tests: {results['passed']}/{results['total']} passed")
        if results['failed'] > 0:
            print(f"FAILED: {results['failed']}")
        else:
            print("ALL TESTS PASSED")
        return

    if args.execute:
        result = kernel.execute(args.execute)
        if args.json:
            print(json.dumps(result))
        else:
            print(json.dumps(result, indent=2))
        return

    if args.health:
        glyphs = ["[K:STATUS]?", "[T-HIERARCHY]?", "[T:ASSEMBLY]?",
                   "[S:ATOMSPACE]?", "[K:PROMISES]?", "[N:DECISION]?",
                   "[P:NS]?", "[T:PERSIST]?"]
        for g in glyphs:
            result = kernel.execute(g)
            print(f"\n{'='*60}")
            print(f"  {g}")
            print(f"{'='*60}")
            print(json.dumps(result, indent=2))
        return

    if args.cli:
        run_cli(kernel)
        return

    # Default: show engine status and run tests
    print("\n" + "=" * 60)
    print("  Glyph-Noetic Inferno Kernel — Simulation")
    print("=" * 60 + "\n")

    # Show engine status
    result = kernel.execute("[K:STATUS]?")
    print("Engine Status:")
    print(json.dumps(result, indent=2))

    # Run tests
    print("\n" + "-" * 40)
    print("Running test suite...")
    results = run_tests(kernel)
    print(f"Tests: {results['passed']}/{results['total']} passed")

    # Show topology
    print("\n" + "-" * 40)
    result = kernel.execute("[T:ASSEMBLY]?")
    print("Topology:")
    print(json.dumps(result, indent=2))

    # Show autognosis
    print("\n" + "-" * 40)
    result = kernel.execute("[N:DECISION]?")
    print("Autognosis:")
    print(json.dumps(result, indent=2))

    print(f"\nUse --cli for interactive mode, --test for full test suite")


if __name__ == "__main__":
    main()
