---
name: topology-weaver
description: Generate neural network topology specifications using analogous reference terminology from a given conceptual context. Use when mapping domain concepts to transformer/MLP architectures, creating contextual tags for network components, defining attention meshwork integration points, or constructing seed grammars for architectural patterns.
---

# Topology Weaver

Generate MLP and attention topologies by weaving analogous terminology from a source context into architectural specifications. Start with the adjacent possible and evolve step-by-step.

## Core Workflow

1. **Extract Terminology** from source context
2. **Map to Architecture** using analogy patterns
3. **Generate Topology** with contextual tags
4. **Define Integration Points** for attention meshworks
5. **Emit Seed Grammar** for pattern evolution

## Step 1: Extract Terminology

Given a source context (text, code, or conceptual framework), extract key terms and their relationships:

```bash
python /home/ubuntu/skills/topology-weaver/scripts/extract_terminology.py <context_file>
```

Output: `terminology.json` with terms, relations, and semantic clusters.

## Step 2: Map to Architecture

Map extracted terms to GPT-2 MLP components using the analogy table:

| Source Domain | MLP Component | Contextual Tag |
|---------------|---------------|----------------|
| Particle/Point | Neuron/Unit | `discrete_feature` |
| Wave/Field | Activation Pattern | `distributed_field` |
| Interference | Weight Interaction | `coupling_point` |
| Collapse | Nonlinearity | `measurement_gate` |
| Superposition | Hidden State | `superposed_state` |
| Propagation | Forward Pass | `field_evolution` |

**Custom mappings**: See `references/analogy_patterns.md` for domain-specific patterns.

## Step 3: Generate Topology

Generate the MLP topology specification:

```bash
python /home/ubuntu/skills/topology-weaver/scripts/generate_topology.py \
    --terminology terminology.json \
    --architecture gpt2 \
    --output topology.yaml
```

### GPT-2 MLP Structure (Reference)

```
MLP Block:
  ├── c_fc (Linear: d_model → 4*d_model)  # W₁ projection
  │   └── Tag: particle_creation
  ├── gelu (Activation)                    # σ nonlinearity
  │   └── Tag: measurement_gate
  └── c_proj (Linear: 4*d_model → d_model) # W₂ projection
      └── Tag: particle_annihilation

Integration Points:
  ├── pre_mlp: residual_stream_input       # Wave enters
  ├── post_fc: hidden_activation           # Superposition state
  └── post_mlp: residual_stream_output     # Wave exits
```

## Step 4: Define Integration Points

Attention meshworks connect at tagged integration points:

```yaml
meshwork_anchors:
  - point: pre_mlp
    type: wave_input
    connects_to: [attention_output, residual]
    
  - point: post_fc
    type: superposition_state
    connects_to: [gating_mechanism, skip_connection]
    
  - point: post_mlp
    type: wave_output
    connects_to: [next_layer_input, residual]
```

**Meshwork patterns**: See `references/meshwork_patterns.md` for attention integration strategies.

## Step 5: Emit Seed Grammar

Generate a seed grammar for evolving the topology:

```bash
python /home/ubuntu/skills/topology-weaver/scripts/emit_grammar.py \
    --topology topology.yaml \
    --output grammar.bnf
```

### Seed Grammar Structure

```bnf
<topology>      ::= <layer>+
<layer>         ::= <attention_block> <mlp_block>
<mlp_block>     ::= <projection> <activation> <projection>
<projection>    ::= <linear> <tag>
<tag>           ::= "particle_creation" | "particle_annihilation" | <custom_tag>
<custom_tag>    ::= <terminology_term>
<attention_block> ::= <meshwork_anchor> <attention_head>+ <meshwork_anchor>
```

The grammar enables:
- **Composition**: Combine blocks following production rules
- **Evolution**: Mutate tags and connections
- **Validation**: Check architectural consistency

## Quick Start Example

```bash
# 1. Extract from wave-particle context
python scripts/extract_terminology.py /path/to/wave_particle_context.txt

# 2. Generate GPT-2 MLP topology with contextual tags
python scripts/generate_topology.py \
    --terminology terminology.json \
    --architecture gpt2 \
    --output my_topology.yaml

# 3. Emit seed grammar for evolution
python scripts/emit_grammar.py \
    --topology my_topology.yaml \
    --output my_grammar.bnf
```

## References

- **Analogy Patterns**: See `references/analogy_patterns.md` for domain-to-architecture mappings
- **Meshwork Patterns**: See `references/meshwork_patterns.md` for attention integration strategies
- **GPT-2 Architecture**: See `references/gpt2_architecture.md` for detailed component specs
