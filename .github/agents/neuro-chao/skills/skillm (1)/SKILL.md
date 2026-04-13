---
name: skillm
description: "Procedural Language Model framework that treats action sequences as its vocabulary. Use when synthesizing multi-step workflows from natural language goals, training on MCP connector execution traces, harvesting action patterns from databases and existing skills, generating action sequence ASTs with semiring composition (⊕ choice, ⊗ pipeline), or visualizing procedural programs as Mermaid diagrams. Composes with circled-operators (algebra), function-creator (domain transfer), cragbase (RAG embeddings), nn (network architecture), and Autognosis (self-monitoring). Triggers on mentions of skillm, procedural language model, action sequence, workflow synthesis, action vocabulary, connector training, or procedural program generation."
---

# Skillm v2.0 — Trainable Procedural Language Model

A **Skillm** (Skill + LLM) is a procedural language model where the unit of generation is an **action sequence**, not a text token. Given a natural language goal, it synthesizes an executable program composed from a vocabulary of action verb categories observed across MCP connectors and four Neon database layers.

```
Skillm = (Vocabulary, ⊕, ⊗, ∅, ε)

where  Vocabulary = Layer1 ∪ Layer2 ∪ Layer3 ∪ Layer4 ∪ Universal
       Layer1     = {THINK, MODULATE, SAY, NARRATE, RECALL, SESSION_START, SESSION_END}
       Layer2     = {TRAVERSE, TRANSITION, DETECT, SIMULATE, RECONCILE, MAP_ENTITY}
       Layer3     = {WORKFLOW_START, STEP, WORKFLOW_END}
       Layer4     = {INGEST, EMBED, RETRIEVE, TRAIN}
       Universal  = {DISCOVER, INSPECT, CREATE, MUTATE, DESTROY,
                     NAVIGATE, COMPOSE, OBSERVE, ORCHESTRATE, CLASSIFY}
       A ⊗ B      = "execute A then B"  (pipeline)
       A ⊕ B      = "execute A or B"    (choice)
       ∅          = impossible action
       ε          = identity / no-op
```

## Architecture

The engine implements a four-layer stack backed by live Neon databases:

| Layer | Name | Neon Project | Token Types | Training Signal |
|-------|------|-------------|-------------|-----------------|
| 1 | Cognitive | deltecho-cognitive | THINK, MODULATE, SAY | valence, arousal, salience |
| 2 | Domain | fincosys | TRAVERSE, TRANSITION, DETECT | confidence, state |
| 3 | Execution | cipc-assistant | WORKFLOW_START, STEP, WORKFLOW_END | weight, bias, gradient |
| 4 | Meta | regima-rag-knowledge | INGEST, EMBED, RETRIEVE, TRAIN | progress, status |

Each token carries continuous parameters (valence, arousal, salience, weight, bias) and supports forward/backward passes following the `nn` skill's Module API.

## Quick Start

```bash
# Full demonstration: harvest → train → infer → visualize
cd /home/ubuntu/skills/skillm/scripts
python3 -m engine.cli demo

# Individual commands
python3 -m engine.cli harvest                              # Pull from Neon + skills
python3 -m engine.cli train --epochs 20 --lr 0.01          # Train the model
python3 -m engine.cli infer --goal "Find invoices"          # Generate a sequence
python3 -m engine.cli stats                                 # Show corpus statistics
python3 -m engine.cli diagram --goal "Sync accounts" --output diagram.png
```

## Step 1: Harvest Training Data

Pull action sequences from four Neon database layers plus 63 existing skills:

```bash
# All sources (recommended)
python3 -m engine.cli harvest

# Single layer only
python3 -m engine.cli harvest --layer cognitive
python3 -m engine.cli harvest --layer domain
python3 -m engine.cli harvest --layer execution
python3 -m engine.cli harvest --layer meta

# Skip skill harvesting (Neon only)
python3 -m engine.cli harvest --no-skills --limit 100
```

The v1 harvester is still available for backward compatibility:

```bash
python3 /home/ubuntu/skills/skillm/scripts/train_skillm.py --source all
```

## Step 2: Train

Run the training loop with forward/backward passes over the corpus:

```bash
python3 -m engine.cli train --epochs 20 --lr 0.01 --weight-decay 0.001
```

Training produces three outputs:
- Updated corpus (weights adjusted in-place): `~/skillm-corpus-v2.jsonl`
- Training history (loss, activation, norms per epoch): `~/skillm-training-history.json`
- Skill registry (per-skill neural parameters): `~/skillm-skill-registry.json`

The training loop follows the `nn` pattern: `forward() → loss → backward() → update()`.

## Step 3: Infer

Generate action sequences from natural language goals:

```bash
# Summary format (human-readable)
python3 -m engine.cli infer --goal "Find campaign insights on Meta" --format summary

# JSON AST format (machine-readable)
python3 -m engine.cli infer --goal "Migrate the database schema" --format json

# Mermaid diagram format
python3 -m engine.cli infer --goal "Search emails and label them" --format mermaid

# All formats at once
python3 -m engine.cli infer --goal "Trace fund flows" --format all

# Override connector detection
python3 -m engine.cli infer --goal "Create a report" --connector meta-marketing

# Disable LLM (rule-based only)
python3 -m engine.cli infer --goal "Sync accounts" --no-llm
```

Inference uses a three-stage strategy:
1. **Corpus search** — find similar goals in the trained corpus
2. **LLM synthesis** — use gpt-4.1-nano to generate novel sequences
3. **Rule-based fallback** — keyword-to-verb template matching

## Step 4: Visualize

```bash
python3 -m engine.cli diagram --goal "Analyze campaigns" --output diagram.png
```

## AST Node Types

| Node Type | Operator | Meaning |
|-----------|----------|---------|
| `action` | (leaf) | Single token invocation |
| `pipeline` | ⊗ | Sequential execution |
| `choice` | ⊕ | Branch selection |
| `loop` | repeat | Iterate until condition |
| `guard` | try/catch | Error handling |

## Engine API (Python)

```python
from engine.tokens import Token, TokenType, EndocrineState, SkillMetrics
from engine.sequence import Sequence, action, pipeline, choice, guard, loop
from engine.harvesters import SkillmHarvester
from engine.trainer import Corpus, SkillmTrainer, SkillmInference, TrainingConfig

# Build a sequence programmatically
seq = Sequence(
    goal="Cognitive reflection loop",
    root=pipeline(
        action(TokenType.SESSION_START, description="Begin"),
        action(TokenType.THINK, description="Reflect", valence=0.7, salience=0.9),
        action(TokenType.MODULATE, description="Adjust hormones"),
        action(TokenType.SAY, description="Externalize insight"),
        action(TokenType.SESSION_END, description="End"),
    ),
    endocrine=EndocrineState(dopamine=0.6, serotonin=0.5),
)

# Forward pass
activation = seq.forward()

# Backward pass (train toward success)
seq.backward(target=1.0)

# Render
print(seq.to_mermaid())
```

## File Structure

```
skillm/
├── SKILL.md                          # This file
├── scripts/
│   ├── engine/                       # v2 trainable engine
│   │   ├── __init__.py               # Package init
│   │   ├── tokens.py                 # Token types, EndocrineState, SkillMetrics
│   │   ├── sequence.py               # Sequence model with forward/backward
│   │   ├── harvesters.py             # Four-layer Neon database harvesters
│   │   ├── trainer.py                # Training loop, corpus, LLM inference
│   │   └── cli.py                    # Unified CLI runner
│   ├── train_skillm.py               # v1 harvester (backward compatible)
│   └── infer_sequence.py             # v1 inference (backward compatible)
├── references/
│   ├── vocabulary.yaml               # Verb categories and tool mappings
│   └── training-sources.md           # Training data source documentation
└── templates/
    └── sequence_ast.json             # AST JSON Schema
```

## Composition with Other Skills

| Skill | Composition | Effect |
|-------|------------|--------|
| `circled-operators` | Semiring algebra | ⊕ and ⊗ govern all sequence composition |
| `nn` | Module API | forward/backward/parameters pattern |
| `virtual-endocrine-system` | EndocrineState | Modulates token selection via hormones |
| `regima-cognitive-ai` | Layer 1 source | Cognitive thought sequences |
| `Autognosis` | Self-monitoring | Track inference success hierarchically |
| `function-creator` | Domain transfer | `F: Skillm_A → Skillm_B` |
| `cragbase` | Layer 4 source | RAG pipeline as training data |
