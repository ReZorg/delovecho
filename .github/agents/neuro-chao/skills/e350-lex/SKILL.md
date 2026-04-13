---
name: e350-lex
description: The unified legal cognitive kernel. Composes e350-mlp with the LEX legal framework (lex-case-analysis, super-sleuth, hyper-holmes, provable-foreknowledge) under the skill-infinity architecture. Provides both a practical LoRA fine-tuning pipeline to train OPT-350M-Erebus on legal data, and a skill-nn cognitive training loop where legal skills act as training signals. Use when fine-tuning models for legal reasoning, building cognitive architectures for case analysis, or applying the skill-infinity fixed-point equation to legal frameworks. Triggers on mentions of e350-lex, legal cognitive kernel, legal LoRA fine-tuning, or skill-nn legal loop.
---

# e350-lex: The Legal Cognitive Kernel

The unified legal cognitive kernel derived from the composition of the `e350-mlp` architecture with the LEX legal framework, closed under the `skill-infinity` fixed-point equation.

## Composition

```
e350-lex = skill∞(
  e350-mlp ⊗ nn ⊗ (
    lex-case-analysis ⊕ 
    super-sleuth ⊕ 
    hyper-holmes ⊕ 
    provable-foreknowledge
  )
)
```

## Three-Layer Architecture

This skill operates simultaneously across three architectural layers:

### Layer A: Practical LoRA Fine-Tuning
A concrete pipeline for fine-tuning the `KoboldAI/OPT-350M-Erebus` model on legal data using PEFT/LoRA.
- **Base Model**: 331M parameters (frozen)
- **LoRA Adapter**: ~1.6M trainable parameters (rank 16, alpha 32) targeting `q_proj` and `v_proj`
- **Training Data**: Instruction-response pairs synthesized from the four legal skills

### Layer B: skill-nn Cognitive Loop
A differentiable skill framework where the legal skills act as training signals for the model:
1. **LexCaseAnalysis**: Provides the legal framework (knowledge base)
2. **SuperSleuth**: Generates investigative leads (divergent forward pass)
3. **e350-mlp**: Generates narrative analysis (model forward pass)
4. **HyperHolmes**: Validates the analysis (convergent backward pass)
5. **ProvableForeknowledge**: Audits temporal consistency (verification)

### Layer C: skill∞ Fixed Point
The self-referential closure where the system converges. The fixed-point equation:
```
B(K, F(K, "analyze legal case")) = K
```
Convergence is guaranteed by geometric attenuation of the meta-feedback signal, typically reaching the fixed point at depth ~5.

## Usage

### 1. Prepare Training Data

Extract instruction-response pairs from the legal framework into JSONL format:

```bash
python /home/ubuntu/skills/e350-lex/scripts/prepare_legal_data.py \
  --all \
  --output-dir ./training_data
```

### 2. Run LoRA Fine-Tuning

Train the adapter on the prepared data:

```bash
python /home/ubuntu/skills/e350-lex/scripts/train_lora.py \
  --train-file ./training_data/train_instruction.jsonl \
  --output-dir ./e350-lex-lora \
  --epochs 3
```

### 3. Run the Cognitive Training Loop

Execute the skill-nn cognitive loop to observe the architecture and convergence:

```bash
# View architecture
python /home/ubuntu/skills/e350-lex/scripts/cognitive_training_loop.py --architecture

# Run a training iteration
python /home/ubuntu/skills/e350-lex/scripts/cognitive_training_loop.py --run
```

## Bundled Resources

- **`scripts/prepare_legal_data.py`**: Extracts 10 distinct legal reasoning tasks from the framework into Erebus, Instruction, and Chat formats.
- **`scripts/train_lora.py`**: Complete HuggingFace PEFT/LoRA training pipeline with merging and GGUF conversion support.
- **`scripts/cognitive_training_loop.py`**: Executable implementation of the Layer B/C architecture with all legal skill modules.
- **`references/training_data.md`**: Documentation of the training corpus structure, task distribution, and data formats.

## Parent Skills

| Skill | Role in Composition |
|---|---|
| **e350-mlp** | The core cognitive kernel architecture (24-layer MLP) |
| **nn** | The differentiable module framework |
| **lex-case-analysis** | Domain rules, entity-relation models |
| **super-sleuth** | Divergent investigation, pattern detection |
| **hyper-holmes** | Convergent validation, burden of proof |
| **provable-foreknowledge** | Temporal consistency, agent classification |
| **skill-infinity** | The fixed-point closure guarantee |
