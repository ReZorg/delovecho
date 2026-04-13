# LEX Legal Training Data Reference

This document outlines the structure and composition of the training data used to fine-tune OPT-350M-Erebus into the e350-lex cognitive kernel.

## Data Sources

The training corpus is synthesized from four primary legal skills:

1. **lex-case-analysis**: Entity-relation definitions, legal domain rules, and evidence chain structures.
2. **super-sleuth**: Forensic pattern detection, anomaly identification, and timeline reconstruction.
3. **hyper-holmes**: Burden of proof assessment, evidence weighting, and legal filing templates.
4. **provable-foreknowledge**: Temporal audit trails, agent classification, and knowledge event analysis.

## Task Distribution

The data preparation script (`scripts/prepare_legal_data.py`) extracts instruction-response pairs across 10 distinct legal reasoning tasks:

| Task | Source Skill | Description |
|---|---|---|
| `entity_analysis` | lex-case-analysis | Analyze entities (persons, companies, trusts) and their legal exposure. |
| `relation_analysis` | lex-case-analysis | Analyze legal duties and breaches in entity relations (e.g., director_of). |
| `pattern_detection` | super-sleuth | Detect forensic patterns (e.g., manufactured crisis, revenue hijacking). |
| `evidence_classification` | super-sleuth | Classify evidence reliability and admissibility. |
| `timeline_reconstruction` | super-sleuth | Reconstruct chronological events and detect anomalies. |
| `fund_flow_analysis` | super-sleuth | Trace financial transactions for layering, structuring, etc. |
| `burden_assessment` | hyper-holmes | Assess if evidence meets civil (50%) or criminal (95%) thresholds. |
| `evidence_weighting` | hyper-holmes | Calculate numerical weight of evidence based on reliability. |
| `foreknowledge_classification` | provable-foreknowledge | Classify agent knowledge into Tiers A-D. |
| `legal_filing` | hyper-holmes | Draft structured legal documents (CIPC complaints, affidavits). |

## Data Formats

The preparation script outputs data in three formats to support different training pipelines:

### 1. Erebus Format (`train_erebus.txt`)
Native format for KoboldAI fine-tuning, using genre and task tags:
```text
[Genre: legal analysis]
[Task: burden_assessment]
Assess burden of proof for: Fraud
Standard: civil (50%)
Required elements: misrepresentation, intent, reliance, damage
---
## Burden of Proof Assessment: Fraud
...
<|endoftext|>
```

### 2. Instruction Format (`train_instruction.jsonl`)
Standard format for HuggingFace SFTTrainer:
```json
{
  "instruction": "Assess burden of proof for: Fraud...",
  "response": "## Burden of Proof Assessment...",
  "task": "burden_assessment",
  "source": "hyper-holmes/burden_assessment",
  "genre_tag": "legal analysis"
}
```

### 3. Chat Format (`train_chat.jsonl`)
OpenAI-compatible format for chat-tuned models:
```json
{
  "messages": [
    {"role": "system", "content": "You are a legal analysis AI..."},
    {"role": "user", "content": "Assess burden of proof..."},
    {"role": "assistant", "content": "## Burden of Proof Assessment..."}
  ]
}
```

## LoRA Fine-Tuning Strategy

The `train_lora.py` script applies Parameter-Efficient Fine-Tuning (PEFT) to the base OPT-350M-Erebus model:

- **Target Modules**: `q_proj` and `v_proj` (Attention query and value projections)
- **Rank (r)**: 16
- **Alpha**: 32
- **Trainable Parameters**: ~1.57M (0.48% of total 331M)

This approach preserves the model's underlying creative writing capabilities while injecting structured legal reasoning patterns into the attention mechanism.
