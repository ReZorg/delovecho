#!/usr/bin/env python3
"""
Plan9Cog Cognitive DevKernel — Unified Orchestrator

Plan 9 from Bell Labs analogue of the ManusCog cognitive development kernel.
Synthesized from: function-creator(inferno-devcontainer(manuscog-cognitive-devkernel) => plan9-analogue)

Layers:
  - Time Crystal Hierarchy (temporal scheduling via Plan 9 sleep/alarm)
  - Promise-Lambda Attention (constraint satisfaction for Plan 9 config)
  - Cognitive File System (tc → 9P2000 namespace operations)
  - Autognosis (hierarchical self-image via /proc introspection)
  - skill-infinity (self-referential convergence)

Usage:
  python cognitive_plan9kernel.py status          — Show kernel self-image
  python cognitive_plan9kernel.py validate <path> — Validate a kernel configuration
  python cognitive_plan9kernel.py promise <path>  — Run promise-lambda analysis
  python cognitive_plan9kernel.py transform       — Show available transforms
  python cognitive_plan9kernel.py cycle           — Run autognosis cycles
"""

import json
import os
import sys
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Any
from pathlib import Path


# ============================================================================
# Layer 1: Time Crystal Temporal Hierarchy (time-crystal-nn → Plan 9 services)
# ============================================================================

@dataclass
class TemporalLevel:
    """A single level in the time crystal hierarchy."""
    level: int
    name: str
    period_ms: float
    plan9_mechanism: str
    phase: float = 0.0
    amplitude: float = 1.0

    def step(self, dt_ms: float):
        import math
        self.phase = (self.phase + (dt_ms / self.period_ms) * 2 * math.pi) % (2 * math.pi)

    def activation(self) -> float:
        import math
        return self.amplitude * math.sin(self.phase)


class TimeCrystalHierarchy:
    """9-level temporal hierarchy mapped to Plan 9 cognitive kernel services."""
    LEVELS = [
        (0, "atom-ops",       8,    "AtomSpace CRUD",           "/srv file read/write"),
        (1, "pattern-match",  26,   "Pattern matching",         "grep over /cognitive/atomspace"),
        (2, "inference-step", 52,   "PLN inference",            "/cognitive/inference file server"),
        (3, "attention-tick", 110,  "ECAN attention",           "/cognitive/attention agents"),
        (4, "learning-batch", 160,  "MOSES learning",           "/cognitive/learning populations"),
        (5, "namespace-sync", 250,  "9P2000 namespace sync",    "mount/bind across CPU servers"),
        (6, "grid-pulse",     330,  "Grid heartbeat",           "/net/tcp keepalive"),
        (7, "autognosis-obs", 500,  "Autognosis observation",   "/proc introspection"),
        (8, "self-image",     1000, "Full self-image rebuild",  "Full namespace walk"),
    ]

    def __init__(self):
        self.levels = [
            TemporalLevel(level=l, name=n, period_ms=p, plan9_mechanism=m)
            for l, n, p, _, m in self.LEVELS
        ]
        self.time_ms = 0.0

    def step(self, dt_ms: float = 1.0):
        self.time_ms += dt_ms
        for level in self.levels:
            level.step(dt_ms)

    def status(self) -> list[dict]:
        return [
            {
                "level": l.level,
                "name": l.name,
                "period_ms": l.period_ms,
                "plan9_mechanism": l.plan9_mechanism,
                "phase": round(l.phase, 4),
                "activation": round(l.activation(), 4),
            }
            for l in self.levels
        ]


# ============================================================================
# Layer 2: Promise-Lambda Attention (constraint satisfaction for Plan 9)
# ============================================================================

@dataclass
class Promise:
    """A lambda constraint on the Plan 9 cognitive kernel configuration."""
    name: str
    constraint: str
    required: bool = True
    satisfied: bool = False
    evidence: str = ""


class PromiseLambdaEngine:
    """Validates Plan 9 kernel configurations against promise constraints."""

    KERNEL_PROMISES = [
        Promise("plan9-kernel",    "Plan 9 kernel image or QEMU config exists"),
        Promise("plan9-cc",        "Plan 9 C compiler (6c/8c) is available or configured"),
        Promise("9p-listener",     "9P2000 port 564 is configured for forwarding"),
        Promise("grid-compose",    "grid-compose.yml defines plan9-registry service"),
        Promise("cognitive-ns",    "/cognitive/ namespace is defined in configuration"),
        Promise("devenv-config",   "devcontainer.json or plan9-devenv contains PLAN9 root"),
        Promise("autognosis-loop", "termrc includes environment verification"),
        Promise("temporal-levels", "At least 9 temporal processing levels are defined"),
    ]

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.promises = [Promise(**asdict(p)) for p in self.KERNEL_PROMISES]

    def evaluate(self) -> list[dict]:
        """Evaluate all promises against the project."""
        devenv = self.project_path / ".plan9-devenv"
        compose = self.project_path / "grid-compose.yml"
        dcjson = devenv / "devcontainer.json"

        for p in self.promises:
            if p.name == "plan9-kernel":
                dockerfile = devenv / "Dockerfile"
                if dockerfile.exists() and ("qemu" in dockerfile.read_text().lower()
                        or "plan9" in dockerfile.read_text().lower()
                        or "9front" in dockerfile.read_text().lower()):
                    p.satisfied = True
                    p.evidence = "Dockerfile configures Plan 9 / 9front QEMU image"

            elif p.name == "plan9-cc":
                dockerfile = devenv / "Dockerfile"
                if dockerfile.exists():
                    content = dockerfile.read_text()
                    if any(cc in content for cc in ["6c", "8c", "5c", "plan9port", "9front"]):
                        p.satisfied = True
                        p.evidence = "Plan 9 C compiler referenced in Dockerfile"

            elif p.name == "9p-listener":
                if dcjson.exists() and "564" in dcjson.read_text():
                    p.satisfied = True
                    p.evidence = "Port 564 in devcontainer.json forwardPorts"

            elif p.name == "grid-compose":
                if compose.exists() and "plan9-registry" in compose.read_text():
                    p.satisfied = True
                    p.evidence = "plan9-registry service defined in grid-compose.yml"

            elif p.name == "cognitive-ns":
                found = False
                for check_file in [compose, dcjson]:
                    if check_file and check_file.exists() and "cognitive" in check_file.read_text().lower():
                        found = True
                        p.evidence = f"Cognitive namespace referenced in {check_file.name}"
                        break
                scripts_dir = devenv / "scripts"
                if not found and scripts_dir.exists():
                    for script in scripts_dir.iterdir():
                        if script.is_file() and "cognitive" in script.read_text().lower():
                            found = True
                            p.evidence = f"Cognitive namespace in {script.name}"
                            break
                p.satisfied = found

            elif p.name == "devenv-config":
                if dcjson.exists() and "PLAN9" in dcjson.read_text():
                    p.satisfied = True
                    p.evidence = "PLAN9 root in containerEnv"

            elif p.name == "autognosis-loop":
                termrc = devenv / "scripts" / "termrc"
                if termrc.exists() and "verif" in termrc.read_text().lower():
                    p.satisfied = True
                    p.evidence = "Verification in termrc"

            elif p.name == "temporal-levels":
                p.satisfied = True
                p.evidence = f"{len(TimeCrystalHierarchy.LEVELS)} levels defined"

        return [asdict(p) for p in self.promises]

    def all_satisfied(self) -> bool:
        return all(p.satisfied for p in self.promises if p.required)


# ============================================================================
# Layer 3: Cognitive File System (tc → 9P2000 namespace operations)
# ============================================================================

class CognitiveNamespace:
    """TC file operations transformed to Plan 9 cognitive 9P2000 namespace operations.

    In Plan 9, every resource is a file server. The cognitive namespace
    maps cognitive services to 9P2000 file trees that can be mounted,
    bound, and composed across CPU servers using Plan 9's namespace primitives.
    """

    NAMESPACE_MAP = {
        "/cognitive/atomspace/atoms":     "Atom storage (ConceptNode, PredicateNode, etc.)",
        "/cognitive/atomspace/types":     "Type hierarchy definitions",
        "/cognitive/atomspace/indices":   "Lookup indices for pattern matching",
        "/cognitive/inference/rules":     "PLN inference rules",
        "/cognitive/inference/queue":     "Inference task queue",
        "/cognitive/inference/results":   "Inference results cache",
        "/cognitive/attention/bank":      "Attention bank (STI/LTI values)",
        "/cognitive/attention/agents":    "Attention allocation agents",
        "/cognitive/learning/populations":"MOSES population storage",
        "/cognitive/learning/fitness":    "Fitness evaluator configurations",
        "/cognitive/temporal/levels":     "Time crystal hierarchy levels",
        "/cognitive/temporal/phases":     "Phase state for each temporal level",
        "/cognitive/autognosis/images":   "Hierarchical self-images",
        "/cognitive/autognosis/insights": "Meta-cognitive insights",
        "/cognitive/autognosis/metrics":  "Self-monitoring metrics",
    }

    # Plan 9 namespace operations (analogues of tc file operations)
    P9_OPS = {
        "tree":    "ls -lR /cognitive/",
        "search":  "grep -r <pattern> /cognitive/",
        "copy":    "cp /cognitive/src /mnt/remote/cognitive/dst",
        "move":    "mv /cognitive/src /cognitive/dst",
        "bind":    "bind /mnt/cpu1/cognitive/atomspace /cognitive/atomspace",
        "mount":   "mount /srv/cogfs /cognitive",
        "union":   "bind -a /mnt/cpu2/cognitive /cognitive",
        "stat":    "stat /cognitive/atomspace/atoms/concept_cat",
        "snapshot":"fossil/flchk -v /dev/sdC0/fossil",
        "restore": "fossil/conf -w /dev/sdC0/fossil < snapshot.conf",
    }

    @classmethod
    def tree(cls) -> str:
        """Display the cognitive namespace tree (tc tree → ls -lR)."""
        lines = ["/cognitive/"]
        prev_parts = []
        for path, desc in sorted(cls.NAMESPACE_MAP.items()):
            parts = path.strip("/").split("/")
            indent = "    " * (len(parts) - 1)
            name = parts[-1]
            lines.append(f"{indent}├── {name}/  — {desc}")
        return "\n".join(lines)

    @classmethod
    def search(cls, pattern: str) -> list[tuple[str, str]]:
        """Search cognitive namespace (tc search → grep -r)."""
        import re
        regex = re.compile(pattern, re.IGNORECASE)
        return [
            (path, desc)
            for path, desc in cls.NAMESPACE_MAP.items()
            if regex.search(path) or regex.search(desc)
        ]

    @classmethod
    def plan9_ops(cls) -> str:
        """Display Plan 9 namespace operation equivalents."""
        lines = []
        for op, cmd in cls.P9_OPS.items():
            lines.append(f"  {op:12s} → {cmd}")
        return "\n".join(lines)


# ============================================================================
# Layer 4: Autognosis Self-Image (via Plan 9 /proc introspection)
# ============================================================================

@dataclass
class SelfImage:
    """A single level of the Autognosis hierarchical self-image."""
    level: int
    confidence: float
    reflections: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    hash: str = ""

    def compute_hash(self):
        content = json.dumps(asdict(self), sort_keys=True, default=str)
        self.hash = hashlib.sha256(content.encode()).hexdigest()[:16]


class AutognosisEngine:
    """Hierarchical self-image building for the Plan 9 cognitive devkernel.

    In Plan 9, /proc exposes process state as files. Autognosis extends
    this to the cognitive kernel: /cognitive/autognosis/ exposes the
    kernel's self-model as readable/writable 9P2000 files.
    """

    def __init__(self, temporal: TimeCrystalHierarchy, promises: PromiseLambdaEngine):
        self.temporal = temporal
        self.promises = promises
        self.self_images: list[SelfImage] = []
        self.insights: list[dict] = []
        self.cycle_count = 0

    def build_level0(self) -> SelfImage:
        """Direct observation: raw system state (Plan 9 /proc analogue)."""
        promise_results = self.promises.evaluate()
        satisfied = sum(1 for p in promise_results if p["satisfied"])
        total = len(promise_results)

        img = SelfImage(
            level=0,
            confidence=satisfied / total if total > 0 else 0.0,
            reflections=[],
            metrics={
                "promises_satisfied": satisfied,
                "promises_total": total,
                "temporal_levels": len(self.temporal.levels),
                "temporal_time_ms": self.temporal.time_ms,
                "namespace_paths": len(CognitiveNamespace.NAMESPACE_MAP),
            },
        )
        img.compute_hash()
        return img

    def build_level1(self, level0: SelfImage) -> SelfImage:
        """Pattern analysis: behavioral patterns from level 0."""
        reflections = []
        if level0.metrics["promises_satisfied"] == level0.metrics["promises_total"]:
            reflections.append("All kernel promises satisfied — Plan 9 system fully configured")
        else:
            missing = level0.metrics["promises_total"] - level0.metrics["promises_satisfied"]
            reflections.append(f"{missing} kernel promise(s) unsatisfied — configuration incomplete")

        if level0.metrics["temporal_levels"] >= 9:
            reflections.append("Full 9-level temporal hierarchy active")

        reflections.append(
            f"Cognitive namespace: {level0.metrics['namespace_paths']} 9P2000 paths mounted"
        )

        img = SelfImage(
            level=1,
            confidence=level0.confidence * 0.9,
            reflections=reflections,
            metrics={
                "pattern_count": len(reflections),
                "base_confidence": level0.confidence,
            },
        )
        img.compute_hash()
        return img

    def build_level2(self, level0: SelfImage, level1: SelfImage) -> SelfImage:
        """Meta-cognitive: analysis of self-understanding quality."""
        reflections = []
        avg_confidence = (level0.confidence + level1.confidence) / 2

        if avg_confidence > 0.8:
            reflections.append("High self-awareness: kernel understands its Plan 9 configuration well")
        elif avg_confidence > 0.5:
            reflections.append("Moderate self-awareness: some Plan 9 namespace bindings unclear")
        else:
            reflections.append("Low self-awareness: significant Plan 9 configuration gaps detected")

        reflections.append(
            f"Self-model depth: 3 levels, convergence factor: {avg_confidence:.3f}"
        )

        img = SelfImage(
            level=2,
            confidence=avg_confidence * 0.85,
            reflections=reflections,
            metrics={
                "self_awareness_score": avg_confidence,
                "model_depth": 3,
                "convergence_factor": avg_confidence,
            },
        )
        img.compute_hash()
        return img

    def run_cycle(self) -> dict:
        """Run one complete autognosis cycle (skill-infinity backward pass)."""
        self.cycle_count += 1

        l0 = self.build_level0()
        l1 = self.build_level1(l0)
        l2 = self.build_level2(l0, l1)
        self.self_images = [l0, l1, l2]

        insights = []
        if l0.confidence == 1.0:
            insights.append({
                "type": "system_ready",
                "severity": "info",
                "message": "Plan 9 cognitive devkernel fully configured and operational",
            })
        else:
            insights.append({
                "type": "configuration_gap",
                "severity": "warning",
                "message": f"Plan 9 kernel configuration {l0.confidence*100:.0f}% complete",
            })

        # skill-infinity fixed point check
        if self.cycle_count > 1 and len(self.insights) > 0:
            prev_score = self.insights[-1].get("self_awareness", 0)
            curr_score = l2.metrics["self_awareness_score"]
            delta = abs(curr_score - prev_score)
            if delta < 0.001:
                insights.append({
                    "type": "fixed_point",
                    "severity": "info",
                    "message": f"Self-improvement converged (delta={delta:.6f} < epsilon=0.001)",
                })

        insights.append({"self_awareness": l2.metrics["self_awareness_score"]})
        self.insights.extend(insights)

        self.temporal.step(1000)

        return {
            "cycle": self.cycle_count,
            "self_images": [asdict(img) for img in self.self_images],
            "insights": insights,
            "temporal_state": self.temporal.status(),
        }


# ============================================================================
# CLI Interface
# ============================================================================

BANNER = """
+==============================================================+
|  Plan9Cog Cognitive DevKernel                                 |
|  Plan 9 from Bell Labs :: Cognitive Architecture              |
|  function-creator(inferno-devcontainer(manuscog) => plan9)    |
+==============================================================+
"""

def cmd_status():
    """Display kernel self-image status."""
    temporal = TimeCrystalHierarchy()
    promises = PromiseLambdaEngine(".")
    engine = AutognosisEngine(temporal, promises)
    result = engine.run_cycle()

    print(BANNER)
    print("  Self-Image Hierarchy:")
    print()

    for img_data in result["self_images"]:
        level = img_data["level"]
        conf = img_data["confidence"]
        refs = img_data["reflections"]
        h = img_data["hash"]
        bar = "=" * int(conf * 20) + "-" * (20 - int(conf * 20))
        print(f"  Level {level}: [{bar}] {conf:.3f}  [{h}]")
        for r in refs:
            print(f"         -> {r}")

    print()
    print("  Temporal Hierarchy (time-crystal-nn -> Plan 9 services):")
    for ts in result["temporal_state"]:
        act = ts["activation"]
        bar = "#" * max(0, int((act + 1) * 5)) + "." * max(0, 10 - int((act + 1) * 5))
        print(f"    L{ts['level']} {ts['name']:20s} {ts['period_ms']:>6.0f}ms [{bar}] {act:+.3f}  {ts['plan9_mechanism']}")

    print()
    print("  Insights:")
    for ins in result["insights"]:
        if "message" in ins:
            sev = ins.get("severity", "info")
            icon = {"info": "i", "warning": "!", "error": "X"}.get(sev, ".")
            print(f"    [{icon}] [{ins['type']}] {ins['message']}")


def cmd_validate(path: str):
    """Validate a Plan 9 kernel configuration via promise-lambda attention."""
    engine = PromiseLambdaEngine(path)
    results = engine.evaluate()

    print(BANNER)
    print("  Promise-Lambda Attention -- Kernel Validation")
    print()

    for p in results:
        icon = "+" if p["satisfied"] else "X"
        req = "REQ" if p["required"] else "OPT"
        print(f"  {icon} [{req}] {p['name']}: {p['constraint']}")
        if p["evidence"]:
            print(f"         Evidence: {p['evidence']}")

    print()
    satisfied = sum(1 for p in results if p["satisfied"])
    total = len(results)
    if engine.all_satisfied():
        print(f"  + All {total} promises satisfied. Plan 9 kernel configuration valid.")
    else:
        print(f"  X {satisfied}/{total} promises satisfied. Configuration incomplete.")


def cmd_promise(path: str):
    """Run full promise-lambda analysis with KV space exploration."""
    engine = PromiseLambdaEngine(path)
    results = engine.evaluate()
    print(json.dumps(results, indent=2))


def cmd_transform():
    """Show available function-creator transforms."""
    print(BANNER)
    print("  Function-Creator Transforms: tc | time-crystal-nn")
    print()

    print("  [tc -> Cognitive 9P2000 Namespace]")
    print()
    print(CognitiveNamespace.tree())
    print()
    print("  Plan 9 namespace operations:")
    print(CognitiveNamespace.plan9_ops())
    print()

    print("  [time-crystal-nn -> Temporal Hierarchy]")
    print()
    for l, n, p, desc, mech in TimeCrystalHierarchy.LEVELS:
        print(f"    Level {l}: {n:20s} {p:>6}ms -- {desc:30s} [{mech}]")


def cmd_cycle():
    """Run autognosis cycles with convergence check."""
    temporal = TimeCrystalHierarchy()
    promises = PromiseLambdaEngine(".")
    engine = AutognosisEngine(temporal, promises)

    print(BANNER)
    print("  Running 5 autognosis cycles...")
    print()

    for i in range(5):
        result = engine.run_cycle()
        score = result["self_images"][2]["metrics"]["self_awareness_score"]
        print(f"  Cycle {result['cycle']}: self-awareness = {score:.6f}")

    print()
    for ins in engine.insights:
        if isinstance(ins, dict) and ins.get("type") == "fixed_point":
            print(f"  -> {ins['message']}")
            break
    else:
        print("  -> Convergence not yet reached (more cycles needed)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "status":
        cmd_status()
    elif cmd == "validate":
        path = sys.argv[2] if len(sys.argv) > 2 else "."
        cmd_validate(path)
    elif cmd == "promise":
        path = sys.argv[2] if len(sys.argv) > 2 else "."
        cmd_promise(path)
    elif cmd == "transform":
        cmd_transform()
    elif cmd == "cycle":
        cmd_cycle()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
