#!/usr/bin/env python3
"""
cli.py — Unified CLI for the Skillm procedural language model.

Commands:
  harvest   Pull training data from all four Neon database layers
  train     Run the training loop over a corpus
  infer     Generate an action sequence from a natural language goal
  stats     Show corpus statistics
  diagram   Render a sequence as a Mermaid diagram
  demo      Run a full harvest → train → infer demonstration
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.tokens import Token, TokenType, EndocrineState, SkillMetrics, Layer
from engine.sequence import (Sequence, ActionNode, PipelineNode, ChoiceNode,
                             action, pipeline, choice, guard, loop)
from engine.harvesters import SkillmHarvester
from engine.trainer import Corpus, SkillmTrainer, SkillmInference, TrainingConfig


DEFAULT_CORPUS = str(Path.home() / "skillm-corpus-v2.jsonl")
DEFAULT_HISTORY = str(Path.home() / "skillm-training-history.json")


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_harvest(args):
    """Harvest training data from Neon databases."""
    print("Skillm Harvester v2.0")
    print("=" * 60)

    harvester = SkillmHarvester()

    if args.layer:
        layer = Layer[args.layer.upper()]
        sequences = harvester.harvest_layer(layer, limit=args.limit)
    else:
        sequences = harvester.harvest_all(limit_per_layer=args.limit)

    # Also harvest from existing skills (v1 compatibility)
    if not args.no_skills:
        print("\nHarvesting skill workflows (63 skills)...")
        skill_seqs = _harvest_skills()
        print(f"  → {len(skill_seqs)} skill sequences")
        sequences.extend(skill_seqs)

    corpus = Corpus(sequences=sequences)
    path = corpus.save(args.output or DEFAULT_CORPUS)

    stats = corpus.stats()
    print(f"\nCorpus saved to: {path}")
    print(f"  Total sequences: {stats['total_sequences']}")
    print(f"  Total tokens: {stats['total_tokens']}")
    print(f"  Avg tokens/seq: {stats['avg_tokens_per_sequence']:.1f}")
    print(f"\n  Layer distribution:")
    for layer, count in stats["layer_distribution"].items():
        print(f"    {layer:15s} {count:5d}")
    print(f"\n  Source distribution:")
    for source, count in stats["source_distribution"].items():
        print(f"    {source:30s} {count:5d}")


def cmd_train(args):
    """Train the Skillm on a corpus."""
    corpus_path = args.corpus or DEFAULT_CORPUS
    if not os.path.exists(corpus_path):
        print(f"Error: corpus not found at {corpus_path}", file=sys.stderr)
        print("Run 'harvest' first to create a training corpus.", file=sys.stderr)
        sys.exit(1)

    corpus = Corpus.load(corpus_path)
    print(f"Loaded corpus: {len(corpus.sequences)} sequences from {corpus_path}")

    config = TrainingConfig(
        epochs=args.epochs,
        learning_rate=args.lr,
        weight_decay=args.weight_decay,
    )

    trainer = SkillmTrainer(config=config)
    history = trainer.train(corpus)

    # Save updated corpus (with trained weights)
    corpus.save()

    # Save training history
    history_path = trainer.save_history(args.history or DEFAULT_HISTORY)
    print(f"\nTraining history saved to: {history_path}")

    # Save skill registry
    registry_path = trainer.save_registry()
    print(f"Skill registry saved to: {registry_path}")

    # Print convergence summary
    if len(history) >= 2:
        first = history[0]
        last = history[-1]
        loss_delta = last.avg_loss - first.avg_loss
        act_delta = last.avg_activation - first.avg_activation
        print(f"\nConvergence:")
        print(f"  Loss:       {first.avg_loss:.6f} → {last.avg_loss:.6f} ({loss_delta:+.6f})")
        print(f"  Activation: {first.avg_activation:.4f} → {last.avg_activation:.4f} ({act_delta:+.4f})")


def cmd_infer(args):
    """Generate an action sequence from a goal."""
    goal = args.goal
    if not goal:
        print("Error: provide a goal with --goal", file=sys.stderr)
        sys.exit(1)

    # Load corpus if available
    corpus = None
    corpus_path = args.corpus or DEFAULT_CORPUS
    if os.path.exists(corpus_path):
        corpus = Corpus.load(corpus_path)
        print(f"Loaded corpus: {len(corpus.sequences)} sequences")

    inference = SkillmInference(
        corpus=corpus,
        use_llm=not args.no_llm,
    )

    print(f"\nGoal: {goal}")
    print(f"Connector: {args.connector or 'auto-detect'}")
    print("-" * 60)

    seq = inference.infer(goal, connector=args.connector)

    if args.format == "json":
        print(seq.to_json())
    elif args.format == "mermaid":
        print(seq.to_mermaid())
    elif args.format == "summary":
        _print_summary(seq)
    elif args.format == "all":
        _print_summary(seq)
        print("\n--- JSON ---")
        print(seq.to_json())
        print("\n--- Mermaid ---")
        print(seq.to_mermaid())

    if args.output:
        Path(args.output).write_text(seq.to_json())
        print(f"\nSaved to: {args.output}")


def cmd_stats(args):
    """Show corpus statistics."""
    corpus_path = args.corpus or DEFAULT_CORPUS
    if not os.path.exists(corpus_path):
        print(f"Error: corpus not found at {corpus_path}", file=sys.stderr)
        sys.exit(1)

    corpus = Corpus.load(corpus_path)
    stats = corpus.stats()

    print("Skillm Corpus Statistics")
    print("=" * 60)
    print(f"  Total sequences:     {stats['total_sequences']}")
    print(f"  Total tokens:        {stats['total_tokens']}")
    print(f"  Avg tokens/sequence: {stats['avg_tokens_per_sequence']:.1f}")

    print(f"\n  Verb Distribution:")
    for verb, count in stats["verb_distribution"].items():
        bar = "█" * min(40, int(count / max(1, stats['total_tokens']) * 200))
        print(f"    {verb:18s} {count:5d} {bar}")

    print(f"\n  Layer Distribution:")
    for layer, count in stats["layer_distribution"].items():
        pct = count / max(1, stats['total_tokens']) * 100
        print(f"    {layer:15s} {count:5d} ({pct:.1f}%)")

    print(f"\n  Source Distribution:")
    for source, count in stats["source_distribution"].items():
        print(f"    {source:30s} {count:5d}")

    print(f"\n  Outcome Distribution:")
    for outcome, count in stats["outcome_distribution"].items():
        print(f"    {outcome:15s} {count:5d}")

    # Show activation distribution
    activations = []
    for seq in corpus.sequences:
        try:
            act = seq.forward()
            activations.append(act)
        except Exception:
            pass

    if activations:
        avg_act = sum(activations) / len(activations)
        min_act = min(activations)
        max_act = max(activations)
        print(f"\n  Activation Distribution:")
        print(f"    Min: {min_act:.4f}  Avg: {avg_act:.4f}  Max: {max_act:.4f}")

        # Histogram
        buckets = [0] * 10
        for a in activations:
            idx = min(9, int(a * 10))
            buckets[idx] += 1
        print(f"    Histogram (0.0 → 1.0):")
        for i, count in enumerate(buckets):
            bar = "█" * min(40, count * 2)
            print(f"      [{i/10:.1f}-{(i+1)/10:.1f}) {count:4d} {bar}")


def cmd_diagram(args):
    """Render a sequence as a Mermaid diagram."""
    if args.input:
        d = json.loads(Path(args.input).read_text())
        from engine.trainer import _dict_to_sequence
        seq = _dict_to_sequence(d)
    elif args.goal:
        corpus = None
        corpus_path = args.corpus or DEFAULT_CORPUS
        if os.path.exists(corpus_path):
            corpus = Corpus.load(corpus_path)
        inference = SkillmInference(corpus=corpus, use_llm=not args.no_llm)
        seq = inference.infer(args.goal, connector=args.connector)
    else:
        print("Error: provide --input or --goal", file=sys.stderr)
        sys.exit(1)

    mermaid = seq.to_mermaid()

    if args.output:
        mmd_path = args.output.replace(".png", ".mmd")
        Path(mmd_path).write_text(mermaid)
        if args.output.endswith(".png"):
            os.system(f"manus-render-diagram {mmd_path} {args.output}")
            print(f"Diagram saved to: {args.output}")
        else:
            print(f"Mermaid saved to: {mmd_path}")
    else:
        print(mermaid)


def cmd_demo(args):
    """Run a full harvest → train → infer demonstration."""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  SKILLM v2.0 — Procedural Language Model Demo          ║")
    print("║  skill + LLM = a vocabulary of action sequences        ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    # Phase 1: Harvest
    print("Phase 1: HARVEST — Pulling training data from 4 Neon layers")
    print("-" * 60)
    harvester = SkillmHarvester()
    sequences = harvester.harvest_all(limit_per_layer=args.limit)

    # Also harvest skills
    print("\nHarvesting skill workflows...")
    skill_seqs = _harvest_skills()
    print(f"  → {len(skill_seqs)} skill sequences")
    sequences.extend(skill_seqs)

    corpus = Corpus(sequences=sequences)
    corpus_path = corpus.save(DEFAULT_CORPUS)
    stats = corpus.stats()

    print(f"\nCorpus: {stats['total_sequences']} sequences, {stats['total_tokens']} tokens")

    # Phase 2: Train
    print(f"\nPhase 2: TRAIN — {args.epochs} epochs with lr={args.lr}")
    print("-" * 60)
    config = TrainingConfig(
        epochs=args.epochs,
        learning_rate=args.lr,
        report_every=max(1, args.epochs // 10),
    )
    trainer = SkillmTrainer(config=config)
    history = trainer.train(corpus)
    corpus.save()
    trainer.save_history()
    trainer.save_registry()

    # Phase 3: Infer
    print(f"\nPhase 3: INFER — Generating sequences from goals")
    print("-" * 60)

    demo_goals = [
        "Find the latest customer invoices and sync to the database",
        "Analyze campaign performance and generate a report",
        "Build a knowledge base from skincare research papers",
        "Run a cognitive reflection on today's decisions",
    ]

    inference = SkillmInference(corpus=corpus, use_llm=not args.no_llm)

    for goal in demo_goals:
        print(f"\n  Goal: {goal}")
        seq = inference.infer(goal)
        _print_summary(seq, indent=4)

    # Phase 4: Visualize
    print(f"\nPhase 4: VISUALIZE — Rendering diagrams")
    print("-" * 60)

    # Render the first demo goal as a diagram
    seq = inference.infer(demo_goals[0])
    mermaid = seq.to_mermaid()
    mmd_path = str(Path.home() / "skillm-demo.mmd")
    png_path = str(Path.home() / "skillm-demo.png")
    Path(mmd_path).write_text(mermaid)
    os.system(f"manus-render-diagram {mmd_path} {png_path}")
    print(f"  Diagram: {png_path}")

    # Summary
    print(f"\n{'='*60}")
    print(f"  DEMO COMPLETE")
    print(f"  Corpus:   {corpus_path}")
    print(f"  History:  {DEFAULT_HISTORY}")
    print(f"  Diagram:  {png_path}")
    print(f"  Registry: ~/skillm-skill-registry.json")
    print(f"{'='*60}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _print_summary(seq: Sequence, indent: int = 2):
    """Print a human-readable summary of a sequence."""
    prefix = " " * indent
    print(f"{prefix}Source: {seq.source or 'generated'}")
    print(f"{prefix}Tokens: {len(seq.tokens())}  Depth: {seq.depth()}")
    try:
        act = seq.forward()
        print(f"{prefix}Activation: {act:.4f}")
    except Exception:
        pass
    print(f"{prefix}Steps:")
    for i, token in enumerate(seq.tokens(), 1):
        desc = token.description or token.tool or token.type.value
        layer = token.layer.name if token.layer else "UNI"
        print(f"{prefix}  {i}. [{layer[:3]}] {token.type.value:18s} {desc[:60]}")


def _harvest_skills() -> list[Sequence]:
    """Harvest action sequences from existing SKILL.md files."""
    import re
    skills_dir = Path.home() / "skills"
    sequences = []

    STEP_PATTERN = re.compile(r"^\s*(\d+)\.\s+\*\*(.+?)\*\*\s*[-–:]?\s*(.*)", re.MULTILINE)
    STEP_SIMPLE = re.compile(r"^\s*(\d+)\.\s+(.+)", re.MULTILINE)

    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        try:
            content = skill_md.read_text()
        except OSError:
            continue

        # Extract skill name
        name_match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        skill_name = name_match.group(1).strip().strip('"\'') if name_match else skill_dir.name

        # Find steps
        steps = STEP_PATTERN.findall(content)
        if not steps:
            steps = STEP_SIMPLE.findall(content)
            steps = [(s[0], s[1], "") for s in steps]

        if len(steps) < 2:
            continue

        step_nodes = [ActionNode(Token(
            type=TokenType.WORKFLOW_START,
            description=f"Skill: {skill_name}",
        ))]

        for step_num, step_title, step_detail in steps[:20]:
            text = (step_title + " " + step_detail).lower()
            # Infer verb
            verb = TokenType.COMPOSE
            verb_keywords = {
                TokenType.DISCOVER: ["search", "find", "list", "scan", "locate"],
                TokenType.INSPECT: ["read", "fetch", "describe", "examine", "check"],
                TokenType.CREATE: ["create", "add", "new", "generate", "build", "write"],
                TokenType.MUTATE: ["update", "edit", "modify", "change", "set", "fix"],
                TokenType.DESTROY: ["delete", "remove", "drop", "clean"],
                TokenType.NAVIGATE: ["navigate", "go", "move", "open"],
                TokenType.COMPOSE: ["run", "execute", "send", "deploy", "install"],
                TokenType.OBSERVE: ["observe", "monitor", "measure", "capture"],
                TokenType.ORCHESTRATE: ["prepare", "complete", "migrate", "provision"],
                TokenType.CLASSIFY: ["label", "tag", "categorize", "classify"],
            }
            for v, keywords in verb_keywords.items():
                if any(kw in text for kw in keywords):
                    verb = v
                    break

            step_nodes.append(ActionNode(Token(
                type=verb,
                tool=f"skill:{skill_name}:step{step_num}",
                description=step_title.strip()[:100],
                salience=0.7,
            )))

        step_nodes.append(ActionNode(Token(
            type=TokenType.WORKFLOW_END,
            description=f"End: {skill_name}",
        )))

        desc_match = re.search(r"^description:\s*(.+?)$", content, re.MULTILINE)
        goal = desc_match.group(1).strip().strip('"\'') if desc_match else f"Execute {skill_name}"

        seq = Sequence(
            goal=goal[:200],
            root=PipelineNode(steps=step_nodes),
            source="skill",
            source_id=skill_name,
            outcome="success",
            weight=2.0,  # Expert-curated
        )
        sequences.append(seq)

    return sequences


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Skillm v2.0 — Procedural Language Model CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m engine.cli harvest                    # Pull data from Neon
  python -m engine.cli train --epochs 20          # Train the model
  python -m engine.cli infer --goal "Find invoices"  # Generate a sequence
  python -m engine.cli stats                      # Show corpus statistics
  python -m engine.cli demo                       # Full demonstration
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # harvest
    p_harvest = subparsers.add_parser("harvest", help="Harvest training data")
    p_harvest.add_argument("--layer", choices=["cognitive", "domain", "execution", "meta"])
    p_harvest.add_argument("--limit", type=int, default=50)
    p_harvest.add_argument("--output", help="Output corpus path")
    p_harvest.add_argument("--no-skills", action="store_true")

    # train
    p_train = subparsers.add_parser("train", help="Train the model")
    p_train.add_argument("--corpus", help="Corpus JSONL path")
    p_train.add_argument("--epochs", type=int, default=10)
    p_train.add_argument("--lr", type=float, default=0.01)
    p_train.add_argument("--weight-decay", type=float, default=0.001)
    p_train.add_argument("--history", help="Training history output path")

    # infer
    p_infer = subparsers.add_parser("infer", help="Generate action sequence")
    p_infer.add_argument("--goal", required=True, help="Natural language goal")
    p_infer.add_argument("--connector", help="Override connector")
    p_infer.add_argument("--corpus", help="Corpus path for few-shot")
    p_infer.add_argument("--format", choices=["json", "mermaid", "summary", "all"],
                         default="summary")
    p_infer.add_argument("--output", help="Output file path")
    p_infer.add_argument("--no-llm", action="store_true")

    # stats
    p_stats = subparsers.add_parser("stats", help="Show corpus statistics")
    p_stats.add_argument("--corpus", help="Corpus path")

    # diagram
    p_diagram = subparsers.add_parser("diagram", help="Render sequence diagram")
    p_diagram.add_argument("--input", help="Input sequence JSON file")
    p_diagram.add_argument("--goal", help="Generate from goal")
    p_diagram.add_argument("--connector", help="Override connector")
    p_diagram.add_argument("--corpus", help="Corpus path")
    p_diagram.add_argument("--output", help="Output file (.mmd or .png)")
    p_diagram.add_argument("--no-llm", action="store_true")

    # demo
    p_demo = subparsers.add_parser("demo", help="Full demonstration")
    p_demo.add_argument("--limit", type=int, default=30)
    p_demo.add_argument("--epochs", type=int, default=10)
    p_demo.add_argument("--lr", type=float, default=0.01)
    p_demo.add_argument("--no-llm", action="store_true")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "harvest": cmd_harvest,
        "train": cmd_train,
        "infer": cmd_infer,
        "stats": cmd_stats,
        "diagram": cmd_diagram,
        "demo": cmd_demo,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
