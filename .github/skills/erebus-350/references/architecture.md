# OPT-350M-Erebus Architecture Reference

## Model Identity

| Property | Value |
|---|---|
| Full Name | KoboldAI/OPT-350M-Erebus |
| Base Model | facebook/opt-350m |
| Architecture | OPT (Decoder-only Transformer) |
| Creator | Mr. Seeker (KoboldAI community) |
| Generation | 2nd gen (successor to Shinen) |
| HuggingFace | `KoboldAI/OPT-350M-Erebus` |
| Paper | arxiv:2205.01068 |
| License | OPT-175B license (Meta Platforms, Inc.) |

## Architecture Parameters

| Parameter | Value |
|---|---|
| Total Parameters | ~331M (0.3B) |
| Safetensors Size | 662 MB |
| Tensor Type | F16 (float16) |
| Decoder Layers | 24 |
| Hidden Dimension | 1024 (internal) |
| Embedding Dimension | 512 |
| Attention Heads | 16 |
| Head Dimension | 64 (1024/16) |
| FFN Dimension | 4096 |
| Vocabulary Size | 50,265 |
| Max Positions | 2,050 (~2048 token context) |
| Activation | ReLU |
| Normalization | Pre-LayerNorm |

## Projection Layers

OPT-350M uses separate embedding and internal dimensions, bridged by projection layers:

- `model.decoder.project_in.weight` — [1024, 512] — projects 512-dim embeddings to 1024-dim internal
- `model.decoder.project_out.weight` — [512, 1024] — projects 1024-dim internal back to 512-dim

## Per-Layer Weight Map (Layer N, repeated 24x for N=0..23)

| Tensor | Shape | Dtype |
|---|---|---|
| `layers.N.self_attn.q_proj.weight` | [1024, 1024] | F16 |
| `layers.N.self_attn.q_proj.bias` | [1024] | F16 |
| `layers.N.self_attn.k_proj.weight` | [1024, 1024] | F16 |
| `layers.N.self_attn.k_proj.bias` | [1024] | F16 |
| `layers.N.self_attn.v_proj.weight` | [1024, 1024] | F16 |
| `layers.N.self_attn.v_proj.bias` | [1024] | F16 |
| `layers.N.self_attn.out_proj.weight` | [1024, 1024] | F16 |
| `layers.N.self_attn.out_proj.bias` | [1024] | F16 |
| `layers.N.self_attn_layer_norm.weight` | [1024] | F16 |
| `layers.N.self_attn_layer_norm.bias` | [1024] | F16 |
| `layers.N.fc1.weight` | (inferred [4096, 1024]) | F16 |
| `layers.N.fc1.bias` | (inferred [4096]) | F16 |
| `layers.N.fc2.weight` | (inferred [1024, 4096]) | F16 |
| `layers.N.fc2.bias` | (inferred [1024]) | F16 |
| `layers.N.final_layer_norm.weight` | [1024] | F16 |
| `layers.N.final_layer_norm.bias` | [1024] | F16 |

## Global Tensors

| Tensor | Shape | Dtype |
|---|---|---|
| `model.decoder.embed_tokens.weight` | [50265, 512] | F16 |
| `model.decoder.embed_positions.weight` | [2050, 1024] | F16 |
| `model.decoder.project_in.weight` | [1024, 512] | F16 |
| `model.decoder.project_out.weight` | [512, 1024] | F16 |

## Erebus Model Family

| Model | Base | Parameters | Context |
|---|---|---|---|
| OPT-350M-Erebus | OPT-350M | 0.3B | 2048 |
| OPT-2.7B-Erebus | OPT-2.7B | 2.7B | 2048 |
| OPT-6.7B-Erebus | OPT-6.7B | 6.7B | 2048 |
| OPT-13B-Erebus | OPT-13B | 13B | 2048 |
| OPT-30B-Erebus | OPT-30B | 30B | 2048 |
| GPT-NeoX-20B-Erebus | GPT-NeoX-20B | 20B | 2048 |
| Mistral-7B-Erebus-V3 | Mistral-7B | 7B | 8192+ |
