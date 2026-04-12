"""
harvesters.py — Four-layer data harvesters for Neon database content.

Each harvester converts database rows into Sequence objects that can be
used for training the Skillm.

Layer 1: CognitiveHarvester  (deltecho-cognitive)
Layer 2: DomainHarvester     (fincosys hypergraph)
Layer 3: ExecutionHarvester  (cipc-assistant workflows)
Layer 4: MetaHarvester       (regima-rag-knowledge)
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Optional

from .tokens import (Token, TokenType, EndocrineState, SkillMetrics, Layer)
from .sequence import (Sequence, ActionNode, PipelineNode, ChoiceNode,
                       GuardNode, LoopNode, action, pipeline, choice, guard)


# ── MCP SQL Helper ────────────────────────────────────────────────────────────

def run_neon_sql(project_id: str, sql: str) -> list[dict]:
    """Execute SQL via the Neon MCP server and return parsed results."""
    input_json = json.dumps({"projectId": project_id, "sql": sql})
    cmd = ["manus-mcp-cli", "tool", "call", "run_sql",
           "--server", "neon", "--input", input_json]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout.strip()
        # Find JSON array in output
        for line in output.split("\n"):
            line = line.strip()
            if line.startswith("["):
                return json.loads(line)
        # Try parsing the saved result file
        import glob
        files = sorted(glob.glob("/home/ubuntu/.mcp/tool-results/*neon_run_sql*"))
        if files:
            content = open(files[-1]).read().strip()
            if content.startswith("["):
                return json.loads(content)
        return []
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as e:
        print(f"  [warn] Neon SQL failed: {e}", file=sys.stderr)
        return []


# ── Neon Project IDs ──────────────────────────────────────────────────────────

NEON_PROJECTS = {
    "deltecho-cognitive": "little-breeze-47283522",
    "regima-rag-knowledge": "summer-silence-47312919",
    "fincosys": "winter-darkness-12213758",
    "cipc-assistant": "weathered-frost-61770245",
}


# ── Layer 1: Cognitive Harvester ──────────────────────────────────────────────

class CognitiveHarvester:
    """Harvest thought-action cycles from deltecho-cognitive.

    Converts dte_thoughts + dte_endocrine_snapshots + dte_conversations
    into cognitive-layer Sequences.
    """

    PROJECT = NEON_PROJECTS["deltecho-cognitive"]

    def harvest(self, limit: int = 100) -> list[Sequence]:
        """Pull cognitive sequences from the database."""
        sequences = []

        # Harvest thought sequences grouped by session
        thoughts = run_neon_sql(self.PROJECT,
            f"SELECT t.id, t.session_id, t.phase, t.content, "
            f"t.valence, t.arousal, t.salience, t.externalized, t.created_at "
            f"FROM dte_thoughts t ORDER BY t.session_id, t.created_at "
            f"LIMIT {limit}")

        # Group by session
        sessions: dict[str, list[dict]] = {}
        for row in thoughts:
            sid = str(row.get("session_id", "unknown"))
            sessions.setdefault(sid, []).append(row)

        # Harvest endocrine snapshots
        endocrine_rows = run_neon_sql(self.PROJECT,
            "SELECT session_id, cognitive_mode, cortisol, dopamine, serotonin, "
            "oxytocin, norepinephrine, endorphin, melatonin, gaba "
            "FROM dte_endocrine_snapshots ORDER BY created_at DESC LIMIT 50")

        endocrine_by_session: dict[str, EndocrineState] = {}
        for row in endocrine_rows:
            sid = str(row.get("session_id", ""))
            if sid and sid not in endocrine_by_session:
                endocrine_by_session[sid] = EndocrineState(
                    cognitive_mode=row.get("cognitive_mode", "NEUTRAL"),
                    cortisol=float(row.get("cortisol", 0.15)),
                    dopamine=float(row.get("dopamine", 0.30)),
                    serotonin=float(row.get("serotonin", 0.40)),
                    oxytocin=float(row.get("oxytocin", 0.10)),
                    norepinephrine=float(row.get("norepinephrine", 0.10)),
                    endorphin=float(row.get("endorphin", 0.10)),
                    melatonin=float(row.get("melatonin", 0.00)),
                    gaba=float(row.get("gaba", 0.30)),
                )

        # Build sequences
        for sid, thought_rows in sessions.items():
            steps = []

            # Session start
            steps.append(ActionNode(Token(
                type=TokenType.SESSION_START,
                description=f"Session {sid}",
                source_id=sid,
            )))

            for row in thought_rows:
                steps.append(ActionNode(Token(
                    type=TokenType.THINK,
                    description=str(row.get("content", ""))[:200],
                    valence=float(row.get("valence", 0.0)),
                    arousal=float(row.get("arousal", 0.0)),
                    salience=float(row.get("salience", 0.5)),
                    params={"phase": row.get("phase", 0)},
                    timestamp=str(row.get("created_at", "")),
                    source_id=str(row.get("id", "")),
                )))

                # If thought was externalized, add a SAY token
                if row.get("externalized"):
                    steps.append(ActionNode(Token(
                        type=TokenType.SAY,
                        description="Externalized thought",
                        valence=float(row.get("valence", 0.0)),
                        salience=float(row.get("salience", 0.5)),
                    )))

            # Session end
            steps.append(ActionNode(Token(
                type=TokenType.SESSION_END,
                description=f"End session {sid}",
            )))

            endocrine = endocrine_by_session.get(sid, EndocrineState())

            seq = Sequence(
                goal=f"Cognitive processing session {sid}",
                root=PipelineNode(steps=steps),
                endocrine=endocrine,
                source="deltecho-cognitive",
                source_id=sid,
                outcome="success",
                weight=1.5,  # Cognitive data is high-quality
            )
            sequences.append(seq)

        return sequences


# ── Layer 2: Domain Harvester ─────────────────────────────────────────────────

class DomainHarvester:
    """Harvest graph traversal patterns from fincosys hypergraph.

    Converts hypergraph nodes + edges + symbolic_rules + state_machines
    into domain-layer Sequences.
    """

    PROJECT = NEON_PROJECTS["fincosys"]

    def harvest(self, limit: int = 50) -> list[Sequence]:
        """Pull domain sequences from the financial hypergraph."""
        sequences = []

        # Harvest symbolic rules as canonical patterns
        rules = run_neon_sql(self.PROJECT,
            "SELECT rule_id, rule_name, confidence FROM hypergraph.symbolic_rules")

        for rule in rules:
            rule_name = rule.get("rule_name", "unknown")
            confidence = float(rule.get("confidence", 1.0))

            # Each rule defines a traversal pattern
            steps = [
                ActionNode(Token(
                    type=TokenType.DISCOVER,
                    tool="hypergraph.nodes",
                    description=f"Find entities matching {rule_name}",
                    salience=confidence,
                )),
                ActionNode(Token(
                    type=TokenType.TRAVERSE,
                    tool="hypergraph.hyperedges",
                    description=f"Traverse transaction edges for {rule_name}",
                    salience=confidence,
                )),
                ActionNode(Token(
                    type=TokenType.DETECT,
                    tool=f"symbolic_rules.{rule_name}",
                    description=f"Apply rule: {rule_name}",
                    salience=confidence,
                )),
            ]

            seq = Sequence(
                goal=f"Apply financial rule: {rule_name}",
                root=PipelineNode(steps=steps),
                source="fincosys",
                source_id=rule.get("rule_id", ""),
                outcome="success",
                weight=2.0,  # Rules are high-confidence patterns
            )
            sequences.append(seq)

        # Harvest state machine transitions
        machines = run_neon_sql(self.PROJECT,
            f"SELECT machine_id, entity_id, current_state, properties "
            f"FROM event_timeline.state_machines LIMIT {limit}")

        for machine in machines:
            entity = machine.get("entity_id", "unknown")
            state = machine.get("current_state", "UNKNOWN")
            props = machine.get("properties", {})
            if isinstance(props, str):
                try:
                    props = json.loads(props)
                except json.JSONDecodeError:
                    props = {}

            tx_count = props.get("total_transactions", 0)
            salience = min(1.0, tx_count / 100.0)  # More transactions = more salient

            steps = [
                ActionNode(Token(
                    type=TokenType.DISCOVER,
                    tool="state_machines",
                    description=f"Locate entity: {entity}",
                    salience=salience,
                )),
                ActionNode(Token(
                    type=TokenType.TRANSITION,
                    tool="state_machines",
                    description=f"State: {state}",
                    params={"entity": entity, "state": state,
                            "total_transactions": tx_count},
                    salience=salience,
                )),
            ]

            if state == "UNKNOWN":
                steps.append(ActionNode(Token(
                    type=TokenType.DETECT,
                    tool="forensic.discrepancies",
                    description=f"Flag unknown state for {entity}",
                    salience=0.8,
                )))

            seq = Sequence(
                goal=f"Track entity state: {entity}",
                root=PipelineNode(steps=steps),
                source="fincosys",
                source_id=machine.get("machine_id", ""),
                outcome="success" if state != "UNKNOWN" else "pending",
                weight=1.0 + salience,
            )
            sequences.append(seq)

        # Harvest node type distribution as a classification pattern
        node_types = run_neon_sql(self.PROJECT,
            "SELECT node_type, COUNT(*) as cnt FROM hypergraph.nodes "
            "GROUP BY node_type ORDER BY cnt DESC LIMIT 10")

        if node_types:
            branches = []
            for nt in node_types:
                ntype = nt.get("node_type", "UNKNOWN")
                count = int(nt.get("cnt", 0))
                branches.append((
                    ntype,
                    f"node_type == '{ntype}'",
                    ActionNode(Token(
                        type=TokenType.TRAVERSE,
                        tool="hypergraph.nodes",
                        description=f"Navigate {ntype} nodes ({count})",
                        salience=min(1.0, count / 500.0),
                    ))
                ))

            seq = Sequence(
                goal="Navigate hypergraph by node type",
                root=ChoiceNode(branches=branches, strategy="highest_activation"),
                source="fincosys",
                source_id="node_type_distribution",
                outcome="success",
                weight=1.5,
            )
            sequences.append(seq)

        return sequences


# ── Layer 3: Execution Harvester ──────────────────────────────────────────────

class ExecutionHarvester:
    """Harvest neural workflow patterns from cipc-assistant.

    Converts workflow_sessions + workflow_steps + skill_metrics
    into execution-layer Sequences with trainable weights.
    """

    PROJECT = NEON_PROJECTS["cipc-assistant"]

    def harvest(self, limit: int = 50) -> list[Sequence]:
        """Pull workflow sequences with neural parameters."""
        sequences = []

        # Harvest skill metrics (the neural parameters)
        metrics_rows = run_neon_sql(self.PROJECT,
            "SELECT * FROM skill_metrics LIMIT 100")

        skill_metrics: dict[str, SkillMetrics] = {}
        for row in metrics_rows:
            name = row.get("skill_name", "")
            if name:
                skill_metrics[name] = SkillMetrics(
                    skill_name=name,
                    workflow_type=row.get("workflow_type", ""),
                    execution_count=int(row.get("execution_count", 0)),
                    success_count=int(row.get("success_count", 0)),
                    failure_count=int(row.get("failure_count", 0)),
                    avg_duration_ms=float(row.get("avg_duration_ms", 0)),
                    weight=float(row.get("weight", 1.0)),
                    bias=float(row.get("bias", 0.0)),
                    learning_rate=float(row.get("learning_rate", 0.01)),
                    gradient_accum=float(row.get("gradient_accum", 0.0)),
                    last_forward_output=row.get("last_forward_output"),
                    last_backward_grad=row.get("last_backward_grad"),
                )

        # Harvest workflow sessions
        sessions = run_neon_sql(self.PROJECT,
            f"SELECT * FROM workflow_sessions ORDER BY started_at DESC LIMIT {limit}")

        for session in sessions:
            sid = session.get("id", 0)
            wtype = session.get("workflow_type", "unknown")
            status = session.get("status", "unknown")
            total = int(session.get("total_steps", 0))
            completed = int(session.get("completed_steps", 0))

            # Get steps for this session
            steps_rows = run_neon_sql(self.PROJECT,
                f"SELECT * FROM workflow_steps WHERE session_id = {sid} "
                f"ORDER BY step_index")

            if not steps_rows:
                # Create a synthetic workflow from session metadata
                steps_rows = [{"step_name": wtype, "status": status,
                               "step_index": 1}]

            step_nodes = []
            step_nodes.append(ActionNode(Token(
                type=TokenType.WORKFLOW_START,
                description=f"Workflow: {wtype}",
                params={"workflow_type": wtype, "total_steps": total},
            )))

            for step_row in steps_rows:
                step_name = step_row.get("step_name", "step")
                step_status = step_row.get("status", "started")
                duration = float(step_row.get("duration_ms", 0) or 0)
                retry = int(step_row.get("retry_count", 0))

                # Look up skill metrics for this step
                metrics = skill_metrics.get(step_name)
                w = metrics.weight if metrics else 1.0
                b = metrics.bias if metrics else 0.0

                salience = 0.5
                if step_status == "completed":
                    salience = 0.8
                elif step_status == "failed":
                    salience = 0.9  # Failures are highly salient

                step_nodes.append(ActionNode(Token(
                    type=TokenType.STEP,
                    tool=step_name,
                    description=f"{step_name} [{step_status}]",
                    weight=w,
                    bias=b,
                    salience=salience,
                    params={
                        "status": step_status,
                        "duration_ms": duration,
                        "retry_count": retry,
                        "input_data": step_row.get("input_data"),
                        "output_data": step_row.get("output_data"),
                    },
                )))

            step_nodes.append(ActionNode(Token(
                type=TokenType.WORKFLOW_END,
                description=f"End workflow: {wtype} [{status}]",
                params={"completed_steps": completed, "total_steps": total},
            )))

            success = status in ("completed", "success")
            seq = Sequence(
                goal=f"Execute {wtype} workflow",
                root=PipelineNode(steps=step_nodes),
                source="cipc-assistant",
                source_id=str(sid),
                outcome="success" if success else "failure",
                weight=2.0 if success else 0.5,
            )
            sequences.append(seq)

        # If no workflow data, create synthetic sequences from skill metrics
        if not sessions and skill_metrics:
            for name, metrics in skill_metrics.items():
                steps = [
                    ActionNode(Token(
                        type=TokenType.WORKFLOW_START,
                        description=f"Skill: {name}",
                    )),
                    ActionNode(Token(
                        type=TokenType.STEP,
                        tool=name,
                        description=f"{name} (w={metrics.weight:.3f}, b={metrics.bias:.3f})",
                        weight=metrics.weight,
                        bias=metrics.bias,
                        salience=metrics.success_rate,
                    )),
                    ActionNode(Token(
                        type=TokenType.WORKFLOW_END,
                        description=f"End: {name}",
                    )),
                ]
                seq = Sequence(
                    goal=f"Execute skill: {name}",
                    root=PipelineNode(steps=steps),
                    source="cipc-assistant",
                    source_id=name,
                    outcome="success" if metrics.success_rate > 0.5 else "pending",
                    weight=1.0 + metrics.success_rate,
                )
                sequences.append(seq)

        return sequences


# ── Layer 4: Meta Harvester ───────────────────────────────────────────────────

class MetaHarvester:
    """Harvest knowledge training patterns from regima-rag-knowledge.

    Converts knowledge_sources + training_jobs into meta-layer Sequences
    that represent the skill-creation pipeline itself.
    """

    PROJECT = NEON_PROJECTS["regima-rag-knowledge"]

    def harvest(self, limit: int = 50) -> list[Sequence]:
        """Pull meta-learning sequences from the RAG knowledge base."""
        sequences = []

        # Harvest training jobs
        jobs = run_neon_sql(self.PROJECT,
            f"SELECT * FROM training_jobs ORDER BY created_at DESC LIMIT {limit}")

        for job in jobs:
            job_type = job.get("job_type", "initial")
            status = job.get("status", "queued")
            total = int(job.get("total_sources", 0) or 0)
            processed = int(job.get("processed_sources", 0) or 0)
            chunks = int(job.get("total_chunks", 0) or 0)

            progress = processed / total if total > 0 else 0.0

            steps = [
                ActionNode(Token(
                    type=TokenType.INGEST,
                    description=f"Ingest {total} sources ({job_type})",
                    salience=0.7,
                    params={"job_type": job_type, "total_sources": total},
                )),
                ActionNode(Token(
                    type=TokenType.EMBED,
                    description=f"Embed {chunks} chunks",
                    salience=progress,
                    params={"total_chunks": chunks, "processed": processed},
                )),
                ActionNode(Token(
                    type=TokenType.TRAIN,
                    description=f"Train ({status}): {processed}/{total} sources",
                    salience=progress,
                    params={"status": status, "progress": progress},
                )),
            ]

            seq = Sequence(
                goal=f"RAG training job: {job_type}",
                root=PipelineNode(steps=steps),
                source="regima-rag-knowledge",
                source_id=str(job.get("id", "")),
                outcome="success" if status == "completed" else "pending",
                weight=2.5 if status == "completed" else 1.0,
            )
            sequences.append(seq)

        # Harvest knowledge sources as INGEST patterns
        sources = run_neon_sql(self.PROJECT,
            f"SELECT id, source_type, title, category, status "
            f"FROM knowledge_sources ORDER BY created_at DESC LIMIT {limit}")

        # Group by category
        by_category: dict[str, list[dict]] = {}
        for src in sources:
            cat = src.get("category", "general")
            by_category.setdefault(cat, []).append(src)

        for category, src_list in by_category.items():
            steps = []
            for src in src_list[:10]:  # Cap per category
                title = src.get("title", "untitled")
                stype = src.get("source_type", "text")
                status = src.get("status", "pending")

                steps.append(ActionNode(Token(
                    type=TokenType.INGEST,
                    tool=f"knowledge_sources.{stype}",
                    description=f"Ingest: {title}",
                    salience=0.8 if status == "trained" else 0.4,
                    params={"source_type": stype, "title": title,
                            "status": status},
                )))

            if steps:
                # Add retrieval step
                steps.append(ActionNode(Token(
                    type=TokenType.RETRIEVE,
                    description=f"Retrieve from {category} knowledge",
                    salience=0.6,
                )))

                seq = Sequence(
                    goal=f"Build {category} knowledge base",
                    root=PipelineNode(steps=steps),
                    source="regima-rag-knowledge",
                    source_id=category,
                    outcome="success",
                    weight=1.5,
                )
                sequences.append(seq)

        return sequences


# ── Unified Harvester ─────────────────────────────────────────────────────────

class SkillmHarvester:
    """Unified harvester that pulls from all four layers."""

    def __init__(self):
        self.cognitive = CognitiveHarvester()
        self.domain = DomainHarvester()
        self.execution = ExecutionHarvester()
        self.meta = MetaHarvester()

    def harvest_all(self, limit_per_layer: int = 50) -> list[Sequence]:
        """Harvest from all four layers and return combined sequences."""
        all_sequences = []

        print("Layer 1: Harvesting cognitive sequences (deltecho-cognitive)...")
        cog = self.cognitive.harvest(limit=limit_per_layer)
        print(f"  → {len(cog)} cognitive sequences")
        all_sequences.extend(cog)

        print("Layer 2: Harvesting domain sequences (fincosys)...")
        dom = self.domain.harvest(limit=limit_per_layer)
        print(f"  → {len(dom)} domain sequences")
        all_sequences.extend(dom)

        print("Layer 3: Harvesting execution sequences (cipc-assistant)...")
        exe = self.execution.harvest(limit=limit_per_layer)
        print(f"  → {len(exe)} execution sequences")
        all_sequences.extend(exe)

        print("Layer 4: Harvesting meta sequences (regima-rag-knowledge)...")
        met = self.meta.harvest(limit=limit_per_layer)
        print(f"  → {len(met)} meta sequences")
        all_sequences.extend(met)

        print(f"\nTotal: {len(all_sequences)} sequences across 4 layers")
        return all_sequences

    def harvest_layer(self, layer: Layer, limit: int = 50) -> list[Sequence]:
        """Harvest from a single layer."""
        harvester = {
            Layer.COGNITIVE: self.cognitive,
            Layer.DOMAIN: self.domain,
            Layer.EXECUTION: self.execution,
            Layer.META: self.meta,
        }[layer]
        return harvester.harvest(limit=limit)
