# Meshwork Patterns Reference

Attention integration strategies for connecting attention mechanisms to MLP topologies.

## Table of Contents

1. [Core Meshwork Concepts](#core-meshwork-concepts)
2. [Standard Integration Patterns](#standard-integration-patterns)
3. [Advanced Meshwork Patterns](#advanced-meshwork-patterns)
4. [Seed Grammar Extensions](#seed-grammar-extensions)

## Core Meshwork Concepts

A **meshwork** is a structured network of attention connections that weaves through the MLP topology. Unlike simple sequential attention, meshworks allow for:

- **Multi-scale connections**: Attention at different granularities
- **Cross-layer communication**: Skip connections via attention
- **Dynamic routing**: Content-dependent information flow

### Meshwork Anatomy

```
┌─────────────────────────────────────────────────┐
│                   MESHWORK                       │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│  │ Anchor  │───▶│  Head   │───▶│ Anchor  │     │
│  │ (Input) │    │ (Attn)  │    │(Output) │     │
│  └────┬────┘    └────┬────┘    └────┬────┘     │
│       │              │              │           │
│       ▼              ▼              ▼           │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│  │   MLP   │    │   MLP   │    │   MLP   │     │
│  │ Block i │    │Block i+1│    │Block i+2│     │
│  └─────────┘    └─────────┘    └─────────┘     │
└─────────────────────────────────────────────────┘
```

### Anchor Types

| Anchor Type | Function | Connects To |
|-------------|----------|-------------|
| `query_field` | Generates queries | MLP output, position encoding |
| `key_field` | Generates keys | MLP output, position encoding |
| `value_field` | Generates values | MLP output, content stream |
| `output_field` | Projects attention output | Next layer input, residual |

## Standard Integration Patterns

### Pattern 1: Pre-LN Transformer (GPT-2 Style)

```yaml
pattern: pre_ln_transformer
description: LayerNorm before attention and MLP

flow:
  - input: residual_stream
  - layer_norm_1
  - attention_meshwork:
      anchors: [query_field, key_field, value_field]
      output: attention_output
  - residual_add_1: input + attention_output
  - layer_norm_2
  - mlp_block:
      integration_points: [pre_mlp, post_fc, post_mlp]
  - residual_add_2: residual_add_1 + mlp_output
  - output: residual_stream

integration_points:
  pre_mlp:
    type: wave_input
    source: layer_norm_2_output
    
  post_mlp:
    type: wave_output
    target: residual_add_2
```

### Pattern 2: Post-LN Transformer (Original)

```yaml
pattern: post_ln_transformer
description: LayerNorm after attention and MLP

flow:
  - input: residual_stream
  - attention_meshwork
  - residual_add_1
  - layer_norm_1
  - mlp_block
  - residual_add_2
  - layer_norm_2
  - output: residual_stream
```

### Pattern 3: Parallel Attention-MLP

```yaml
pattern: parallel_attention_mlp
description: Attention and MLP computed in parallel (PaLM style)

flow:
  - input: residual_stream
  - layer_norm
  - parallel:
      branch_a: attention_meshwork
      branch_b: mlp_block
  - merge: branch_a + branch_b
  - residual_add: input + merge
  - output: residual_stream

integration_points:
  parallel_branch:
    type: parallel_wave
    connects_to: [attention_output, mlp_output]
```

## Advanced Meshwork Patterns

### Pattern 4: Cross-Layer Attention

Connect attention across non-adjacent layers:

```yaml
pattern: cross_layer_attention
description: Attention that spans multiple layers

meshwork:
  - anchor: layer_i.output
    connects_to: layer_j.query_field  # j > i + 1
    
  - anchor: layer_k.key_field
    connects_from: [layer_i.output, layer_j.output]
    
grammar_extension: |
  <cross_layer_attn> ::= <source_layer> "-->" <target_layer>
  <source_layer> ::= "layer_" INTEGER
  <target_layer> ::= "layer_" INTEGER
```

### Pattern 5: Hierarchical Meshwork

Nested attention at different scales:

```yaml
pattern: hierarchical_meshwork
description: Multi-scale attention hierarchy

levels:
  token_level:
    granularity: 1
    attention: local_window
    
  phrase_level:
    granularity: 4
    attention: pooled_attention
    aggregates: token_level
    
  clause_level:
    granularity: 16
    attention: global_attention
    aggregates: phrase_level

integration:
  - token_mlp receives phrase_context
  - phrase_mlp receives clause_context
  - clause_mlp receives global_context
```

### Pattern 6: Gated Meshwork

Learnable gates control information flow:

```yaml
pattern: gated_meshwork
description: Gating mechanism for attention routing

gates:
  attention_gate:
    input: [query, key]
    output: gate_value  # [0, 1]
    
  mlp_gate:
    input: hidden_state
    output: gate_value
    
flow:
  attention_output = gate_a * attention(Q, K, V)
  mlp_output = gate_m * mlp(x)
  
grammar_extension: |
  <gated_block> ::= <gate> "*" <block>
  <gate> ::= "sigmoid" "(" <gate_input> ")"
```

### Pattern 7: Sparse Meshwork

Attention only at selected positions:

```yaml
pattern: sparse_meshwork
description: Sparse attention patterns

sparsity_patterns:
  local_window:
    window_size: 256
    
  strided:
    stride: 64
    
  random:
    num_random: 32
    
  learned:
    top_k: 64

integration_points:
  sparse_anchor:
    type: sparse_connection
    pattern: local_window + strided
```

## Seed Grammar Extensions

Extend the base grammar for meshwork patterns:

```bnf
# === MESHWORK EXTENSIONS ===

<meshwork> ::= <meshwork_type> <anchor>+ <connection>*

<meshwork_type> ::= "standard" | "parallel" | "cross_layer" 
                  | "hierarchical" | "gated" | "sparse"

<anchor> ::= <anchor_name> ":" <anchor_type> <anchor_config>
<anchor_config> ::= "{" <config_item>* "}"
<config_item> ::= <key> ":" <value>

<connection> ::= <source_anchor> "-->" <target_anchor> <connection_type>?
<connection_type> ::= "[" ("residual" | "gated" | "sparse") "]"

# === HIERARCHICAL EXTENSIONS ===

<hierarchy_level> ::= "level_" INTEGER ":" <level_config>
<level_config> ::= <granularity> <attention_type> <aggregation>?
<granularity> ::= "granularity" "=" INTEGER
<attention_type> ::= "local" | "global" | "pooled"
<aggregation> ::= "aggregates" ":" <level_ref>

# === GATING EXTENSIONS ===

<gated_component> ::= <gate> "*" <component>
<gate> ::= "gate" "(" <gate_input> ")"
<gate_input> ::= <tensor_ref> ("," <tensor_ref>)*

# === SPARSE EXTENSIONS ===

<sparse_pattern> ::= <pattern_type> <pattern_params>
<pattern_type> ::= "local_window" | "strided" | "random" | "learned"
<pattern_params> ::= "(" <param>+ ")"
```

### Evolution Rules for Meshworks

```
# Add cross-layer connection
CROSS_CONNECT: meshwork + (layer_i --> layer_j) -> meshwork'

# Increase hierarchy depth
DEEPEN: hierarchy(n_levels) -> hierarchy(n_levels + 1)

# Add gating
GATE: component -> gate(input) * component

# Sparsify attention
SPARSIFY: dense_attention -> sparse_attention(pattern)

# Merge parallel branches
MERGE_PARALLEL: [branch_a, branch_b] -> branch_a + branch_b
```
