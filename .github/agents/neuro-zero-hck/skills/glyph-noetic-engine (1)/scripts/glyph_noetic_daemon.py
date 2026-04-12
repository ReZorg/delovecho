#!/usr/bin/env python3
"""
Glyph-Noetic Daemon

This is the core executable for the Glyph-Noetic Engine. It composes the
neuro-symbolic, time-crystal, and daemon skills into a single, self-weaving
cognitive fabric that is addressable through a glyph-based language.

Composition:
/neuro-symbolic-engine ( /time-crystal-nn ( /time-crystal-neuron ) [ /time-crystal-daemon ] )

Extended with 9P glyphs via:
/glyph-noetic-engine ( /plan9-file-server [ /p9fstyx-topology ] )
"""

import json
import os
import sys
import time
import socket
import threading
import logging
from typing import Dict, List, Optional, Any

# Add skill templates to path for imports
sys.path.insert(0, '/home/ubuntu/skills/time-crystal-daemon/templates/')
sys.path.insert(0, '/home/ubuntu/skills/runtime-topological-self-assembly/scripts')

from composed.self_weaving_daemon import SelfWeavingDaemon, save_topology
from rtsa import Assembly, Component, Port, PortKind, TopoConstraint

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('glyph_noetic_daemon')

# ============================================================================
# Plan 9 Topology Module
# ============================================================================

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_P9_CONFIG = os.path.join(SKILL_DIR, 'templates', 'plan9_cluster_assembly.json')


class Plan9TopologyModule:
    """
    Manages and analyzes a Plan 9 file server cluster as a topological
    assembly using the RTSA framework. Provides IDL-callable methods
    for the glyph daemon.

    Source skills:
      - /plan9-file-server  → semantic domain (fs, cpu, auth, namespace)
      - /p9fstyx-topology   → analytical lens (Betti numbers, persistence)
    """

    def __init__(self, config_path: str = DEFAULT_P9_CONFIG):
        self.config_path = config_path
        self.assembly = self._load_assembly(config_path)
        logger.info(
            f"Plan9TopologyModule loaded: {self.assembly.name} "
            f"({len(self.assembly.components)} components)"
        )

    def _load_assembly(self, config_path: str) -> Assembly:
        """Load the Plan 9 cluster assembly from a JSON config."""
        with open(config_path) as f:
            data = json.load(f)
        return Assembly.from_dict(data)

    # -- IDL methods (callable via glyph RPC) --------------------------------

    def get_topology_status(self) -> dict:
        """Return the topological health summary of the cluster."""
        betti = self.assembly.betti_numbers()
        violated = self.assembly.violated_constraints()
        return {
            "assembly": self.assembly.name,
            "num_components": len(self.assembly.components),
            "simplices_by_dim": {
                d: len(self.assembly.simplices(d))
                for d in range(self.assembly.max_dim() + 1)
            },
            "betti_numbers": {f"beta_{k}": v for k, v in betti.items()},
            "euler_characteristic": self.assembly.euler_characteristic(),
            "constraints_satisfied": len(violated) == 0,
            "violated_constraints": [c.name for c in violated],
        }

    def list_p9_components(self) -> dict:
        """List all cluster components with their metadata and port types."""
        result = {}
        for cid, comp in self.assembly.components.items():
            result[cid] = {
                "metadata": comp.metadata,
                "ports": {
                    pname: {"kind": p.kind.name, "dtype": p.dtype}
                    for pname, p in comp.ports.items()
                },
                "state": comp.state,
            }
        return result

    def get_component(self, component_id: str) -> dict:
        """Get details for a specific cluster component."""
        comp = self.assembly.components.get(component_id)
        if not comp:
            return {"error": f"Component '{component_id}' not found"}
        return {
            "cid": comp.cid,
            "metadata": comp.metadata,
            "ports": {
                pname: {"kind": p.kind.name, "dtype": p.dtype}
                for pname, p in comp.ports.items()
            },
            "state": comp.state,
        }

    def get_namespace_map(self) -> dict:
        """
        Return the mapping between /cognitive/ namespace paths and
        engine glyphs, based on the cognitive namespace binding patterns
        from /plan9-file-server.
        """
        return {
            "/cognitive/atomspace/":   {"glyph": "[S:ATOMSPACE]", "protocol": "9P2000", "port": 5640},
            "/cognitive/inference/":    {"glyph": "[C:PLN]",       "protocol": "9P2000", "port": 5640},
            "/cognitive/attention/":    {"glyph": "[C:ATTN]",      "protocol": "9P2000", "port": 5640},
            "/cognitive/temporal/":     {"glyph": "[T-HIERARCHY]", "protocol": "9P2000", "port": 5640},
            "/cognitive/autognosis/":   {"glyph": "[N:DECISION]",  "protocol": "9P2000", "port": 5640},
            "/cognitive/learning/":     {"glyph": "[C:MOSES]",     "protocol": "9P2000", "port": 5640},
        }

    def simulate_reconfigure(self, plan: list) -> dict:
        """
        Dry-run a reconfiguration plan against the cluster assembly.
        Returns whether the plan would succeed without violating constraints.
        """
        return self.assembly.reconfigure(plan, dry_run=True)

    def get_persistence_diagram(self) -> list:
        """Return the persistence pairs for the cluster assembly."""
        pairs = self.assembly.persistence_pairs()
        # Convert inf to string for JSON serialization
        for p in pairs:
            if p["death"] == float("inf"):
                p["death"] = "inf"
        return pairs


# ============================================================================
# Glyph-Noetic Daemon (extended with 9P glyphs)
# ============================================================================

class GlyphNoeticDaemon(SelfWeavingDaemon):
    """
    Extends the SelfWeavingDaemon with a glyph-based RPC interface.
    Includes the Plan9TopologyModule for 9P and topology glyphs.
    """

    def __init__(self, socket_path: str = "/tmp/glyph_noetic_daemon.sock"):
        super().__init__(socket_path)

        # Initialize the Plan 9 topology module
        self.p9_topology = Plan9TopologyModule()

        # Register Plan 9 / topology IDL handlers
        self.rpc_handlers['get_topology_status'] = self.p9_topology.get_topology_status
        self.rpc_handlers['list_p9_components'] = self.p9_topology.list_p9_components
        self.rpc_handlers['get_p9_component'] = self.p9_topology.get_component
        self.rpc_handlers['get_namespace_map'] = self.p9_topology.get_namespace_map
        self.rpc_handlers['simulate_reconfigure'] = self.p9_topology.simulate_reconfigure
        self.rpc_handlers['get_persistence_diagram'] = self.p9_topology.get_persistence_diagram

        # Build the full glyph map
        self.glyph_map = self._load_glyph_map()

    def _load_glyph_map(self) -> Dict[str, Dict]:
        """Load the complete glyph specification including 9P glyphs."""
        return {
            # ---- Temporal Glyphs (Blue) ----
            "T-HIERARCHY": {"command": "get_tc_hierarchy"},
            "T~q":         {"command": "get_level", "params": {"level_id": 0}},
            "T~p":         {"command": "get_level", "params": {"level_id": 1}},
            "T~d":         {"command": "get_level", "params": {"level_id": 5}},
            "T~g":         {"command": "get_level", "params": {"level_id": 9}},
            "T~h":         {"command": "get_level", "params": {"level_id": 11}},

            # ---- Cognitive Glyphs (Purple) ----
            "C:PLN":       {"command": "get_module", "params": {"module_id": "pln"}},
            "C:MOSES":     {"command": "get_module", "params": {"module_id": "moses"}},
            "C:PATTERN":   {"command": "get_module", "params": {"module_id": "pattern"}},
            "C:ATTN":      {"command": "get_module", "params": {"module_id": "attention"}},

            # ---- Structural Glyphs (Green) ----
            "S:ATOMSPACE": {"command": "get_status"},
            "S:atom":      {"command": "get_status"},
            "S:link":      {"command": "get_status"},
            "S:H-ATTN":    {"command": "get_status"},

            # ---- Noetic Glyphs (Orange) ----
            "N:TV":        {"command": "get_status"},
            "N:AV":        {"command": "get_status"},
            "N:DECISION":  {"command": "explain_decision"},
            "N:ANOMALY":   {"command": "get_status"},

            # ---- Protocol Glyphs (Cyan) — from /plan9-file-server ----
            "P:FS":        {"command": "get_p9_component", "params": {"component_id": "fs"}},
            "P:CPU":       {"command": "list_p9_components"},
            "P:NS":        {"command": "get_namespace_map"},
            "P:AUTH":      {"command": "get_p9_component", "params": {"component_id": "auth"}},
            "P:READ":      {"command": "get_namespace_map"},
            "P:WRITE":     {"command": "get_namespace_map"},

            # ---- Topology Glyphs (Cyan) — from /p9fstyx-topology ----
            "T:ASSEMBLY":  {"command": "get_topology_status"},
            "T:BETA0":     {"command": "get_topology_status"},
            "T:BETA1":     {"command": "get_topology_status"},
            "T:SIMPLEX":   {"command": "get_topology_status"},
            "T:PERSIST":   {"command": "get_persistence_diagram"},
        }

    def handle_rpc_request(self, data: bytes) -> bytes:
        """
        Override the default RPC handler to process glyph-based commands.
        Parses noetic sentences and dispatches to IDL handlers.
        """
        try:
            request = json.loads(data.decode('utf-8'))
            logger.info(f"Received glyph request: {request}")

            glyph_sentence = request.get("sentence", [])
            if not glyph_sentence:
                return json.dumps({"error": "Invalid sentence"}).encode('utf-8')

            # --- Glyph to IDL Translation ---
            primary_glyph_id = glyph_sentence[0]

            # Strip operator suffixes (? for query, ! for action)
            query_op = '?' in primary_glyph_id
            action_op = '!' in primary_glyph_id
            primary_glyph_id = primary_glyph_id.replace('?', '').replace('!', '')

            glyph_action = self.glyph_map.get(primary_glyph_id)
            if not glyph_action:
                return json.dumps({"error": f"Glyph '{primary_glyph_id}' not found in map"}).encode('utf-8')

            method = glyph_action["command"]
            params = dict(glyph_action.get("params", {}))

            # Handle inline parameters (e.g., [N:DECISION:12345])
            if len(glyph_sentence) > 1:
                extra = glyph_sentence[1]
                if ':' in extra:
                    param_key, param_val = extra.split(':', 1)
                    if method == 'explain_decision':
                        params['decision_id'] = param_val
                    elif method == 'get_p9_component':
                        params['component_id'] = param_val

            # --- Execute IDL Command ---
            handler = self.rpc_handlers.get(method)
            if not handler:
                return json.dumps({"error": f"Unknown IDL method: {method}"}).encode('utf-8')

            result = handler(**params)
            response = {"glyph": primary_glyph_id, "operator": "?" if query_op else ("!" if action_op else "->"), "result": result}

        except json.JSONDecodeError:
            response = {"error": "Invalid JSON request"}
        except Exception as e:
            logger.error(f"RPC Error: {e}", exc_info=True)
            response = {"error": str(e)}

        return json.dumps(response, default=str).encode('utf-8')


# ============================================================================
# Entry point
# ============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Glyph-Noetic Daemon (with 9P glyphs)")
    parser.add_argument("--save-topology", type=str, help="Save the evolved topology to a file and exit.")
    parser.add_argument("--p9-config", type=str, default=DEFAULT_P9_CONFIG,
                        help="Path to the Plan 9 cluster assembly JSON config.")
    parser.add_argument("--test-9p", action="store_true",
                        help="Run a quick test of the 9P topology module and exit.")
    args = parser.parse_args()

    if args.test_9p:
        logger.info("Testing Plan9TopologyModule...")
        mod = Plan9TopologyModule(args.p9_config)
        print("\n=== Topology Status ===")
        print(json.dumps(mod.get_topology_status(), indent=2))
        print("\n=== Cluster Components ===")
        print(json.dumps(mod.list_p9_components(), indent=2))
        print("\n=== Namespace Map ===")
        print(json.dumps(mod.get_namespace_map(), indent=2))
        print("\n=== Persistence Diagram ===")
        print(json.dumps(mod.get_persistence_diagram(), indent=2))
        return

    daemon = GlyphNoeticDaemon()

    if args.save_topology:
        logger.info("Weaving and evolving topology...")
        topology = daemon.weave_and_evolve()
        save_topology(topology, args.save_topology)
        logger.info(f"Topology saved to {args.save_topology}")
        return

    try:
        daemon.start()
        logger.info("Glyph-Noetic Daemon started successfully.")
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down daemon...")
        daemon.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
