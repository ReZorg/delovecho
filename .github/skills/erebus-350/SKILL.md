---
name: erebus-350
description: Comprehensive reference and operational skill for the KoboldAI Erebus 350M (OPT-based) creative writing model. Use when deploying, converting, or generating text with the OPT-350M-Erebus model, or when analyzing its architecture and training data.
license: Complete terms in LICENSE.txt
---

# Erebus 350M Skill

This skill provides operational scripts and architectural references for the **KoboldAI/OPT-350M-Erebus** model. Erebus is a specialized, fine-tuned version of Meta's OPT-350M decoder-only transformer, designed specifically for creative writing and adult-themed storytelling.

## Model Overview

The Erebus 350M model is the second generation of the original "Shinen" model created by Mr. Seeker and the KoboldAI community. It is trained on a curated dataset of six different sources focused on adult themes and creative writing.

**Key Characteristics:**
- **Base Architecture:** Meta OPT-350M (Decoder-only Transformer)
- **Parameters:** ~331 Million (0.3B)
- **Context Window:** 2048 tokens
- **Vocabulary:** 50,265 tokens
- **License:** OPT-175B license (Meta Platforms, Inc.)

> **Warning:** This model has a very strong NSFW bias and is not suitable for minors. It will output X-rated content.

## Usage Guidelines

### 1. Text Generation and Inference

To run inference with the model using HuggingFace Transformers, use the provided Python script. It supports both single-prompt generation and an interactive chat-like mode.

**Run a single prompt:**
```bash
python /home/ubuntu/skills/erebus-350/scripts/erebus_inference.py --prompt "[Genre: fantasy, romance]\nThe knight entered the chamber"
```

**Run in interactive mode:**
```bash
python /home/ubuntu/skills/erebus-350/scripts/erebus_inference.py --interactive
```

**Recommended Sampling Parameters:**
- **Temperature:** 0.9 to 2.0 (higher values increase creativity but may reduce coherence)
- **Top-P:** 0.90 to 0.99 (do not set to 1.0 as it disables nucleus sampling)
- **Repetition Penalty:** 1.1 to 1.15

### 2. Prompt Formatting and Tags

Erebus is trained to recognize specific bracketed tags to guide the generation style, tone, and genre. Always place these at the very beginning of your prompt.

**Supported Tag Formats:**
- `[Genre: <comma-separated list of genres>]` (e.g., `[Genre: sci-fi, thriller]`)
- `[Tone: <description>]` (e.g., `[Tone: Focus on people, interactions.]`)
- `[Writing style: <description>]` (e.g., `[Writing style: Give vivid, detailed descriptions.]`)

### 3. GGUF Conversion for KoboldCpp

For efficient CPU inference or deployment via KoboldCpp, the model can be converted to the GGUF format and quantized.

**Run the conversion script:**
```bash
bash /home/ubuntu/skills/erebus-350/scripts/convert_to_gguf.sh ./output_dir
```
*Note: This script requires `llama.cpp` to be cloned and compiled on your system.*

## Bundled Resources

- **`references/architecture.md`**: Detailed breakdown of the OPT-350M architecture, including layer dimensions, tensor shapes, and the full weight map. Read this when analyzing the model's internal structure or planning fine-tuning.
- **`scripts/erebus_inference.py`**: A ready-to-use Python script for loading the model via HuggingFace Transformers and generating text.
- **`scripts/convert_to_gguf.sh`**: A bash script to download the model, convert it to GGUF format, and apply Q4_K_M quantization for optimized CPU inference.
