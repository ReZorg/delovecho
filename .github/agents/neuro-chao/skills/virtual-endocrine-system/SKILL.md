---
name: virtual-endocrine-system
description: >
  Implement biologically-inspired virtual endocrine systems for cognitive architectures.
  Use when building emotional/affective systems with hormone-based signaling, valence memory,
  moral perception, or cognitive mode detection. Covers 10 virtual glands (HPA axis, dopaminergic,
  serotonergic, noradrenergic, oxytocinergic, thyroid, circadian, pancreatic, immune, endocannabinoid),
  a SIMD-optimized hormone bus, valence-arousal tagging, and adapters for ECAN attention and PLN inference.
  Triggers on mentions of endocrine system, hormone bus, affective computing, valence memory,
  cognitive modes, emotional architecture, or neuroendocrine modeling.
---

# Virtual Endocrine System

Biologically-grounded emotional architecture using virtual neuroendocrine signaling. Replaces simplistic sentiment labels with a dynamical system of 10 virtual glands producing 16 hormone channels that modulate cognition, attention, and reasoning.

## Architecture

```
Events → Glands → HormoneBus → [ECAN Adapter, PLN Adapter]
                      ↓
              ValenceMemory → AffectiveIntegration → MoralPerception
```

## Core Components

### Hormone Bus

Central broadcast bus with 16 SIMD-aligned channels. Lock-free atomic reads on hot path, AVX2-optimized exponential decay toward baselines.

For full C++ header with SIMD decay, mode detection, and history ring buffer, read `references/hormone_bus.hpp`.

**16 Hormone Channels:**

| ID | Hormone | Half-Life | Baseline | Function |
|----|---------|-----------|----------|----------|
| 0 | CRH | 5 ticks | 0.05 | Hypothalamic stress signal |
| 1 | ACTH | 10 | 0.05 | Pituitary stress relay |
| 2 | Cortisol | 30 | 0.15 | Resource mobilization |
| 3 | Dopamine (tonic) | 20 | 0.3 | Baseline motivation |
| 4 | Dopamine (phasic) | 3 | 0.0 | Reward prediction error |
| 5 | Serotonin | 50 | 0.4 | Mood / patience tradeoff |
| 6 | Norepinephrine | 8 | 0.1 | Arousal / vigilance |
| 7 | Oxytocin | 15 | 0.1 | Trust / bonding |
| 8 | T3/T4 | 100 | 0.5 | Global processing rate |
| 9 | Melatonin | 12 | 0.0 | Circadian maintenance |
| 10 | Insulin | 10 | 0.2 | Energy conservation |
| 11 | Glucagon | 8 | 0.1 | Energy mobilization |
| 12 | IL-6 | 20 | 0.05 | System health signal |
| 13 | Anandamide | 6 | 0.1 | Noise reduction |
| 14-15 | Reserved | 10 | 0.0 | Extension slots |

### 10 Virtual Glands

Each gland produces hormones in response to cognitive events:

| Gland | Hormones Produced | Trigger Events |
|-------|-------------------|----------------|
| HPA Axis | CRH → ACTH → Cortisol | `THREAT_DETECTED`, `CONFLICT_DETECTED` |
| Dopaminergic | Dopamine (tonic + phasic) | `REWARD_RECEIVED`, `GOAL_ACHIEVED` |
| Serotonergic | Serotonin | Sustained positive states |
| Noradrenergic | Norepinephrine | `NOVELTY_ENCOUNTERED`, threats |
| Oxytocinergic | Oxytocin | `SOCIAL_BOND_SIGNAL` |
| Thyroid | T3/T4 | Metabolic demand changes |
| Circadian | Melatonin | `LIGHT_SIGNAL` (inverse) |
| Pancreatic | Insulin / Glucagon | `RESOURCE_DEPLETED` |
| Immune | IL-6 | `ERROR_DETECTED` |
| Endocannabinoid | Anandamide | `NOISE_EXCESSIVE` |

### Cognitive Mode Detection

10 emergent modes classified by nearest-centroid in 16D hormone space:

```
RESTING → EXPLORATORY → FOCUSED → STRESSED → SOCIAL
REFLECTIVE → VIGILANT → MAINTENANCE → REWARD → THREAT
```

Mode transitions fire callbacks. Not set explicitly — they emerge from the coupled gland dynamics.

### Valence Memory

Russell's circumplex model: `ValenceSignature { valence: [-1,+1], arousal: [0,1] }` (8 bytes, matches TruthValue pattern). Tags atoms and episodes with felt-quality for fuzzy retrieval.

### Moral Perception Engine

Combines raw affective signal, morally-tagged episode associations, empathic inference, and novelty detection into actionable moral perception that precedes deliberative reasoning.

For full type definitions (ValenceSignature, EndocrineState, CognitiveMode, MoralPerception, FeltSense), read `references/types.hpp`.

## Integration Pattern

```cpp
// Initialize
EndocrineSystem endo(atomspace);
endo.connect_attention(attention_bank);  // ECAN adapter
endo.connect_pln(pln_engine);           // PLN adapter

// Per-tick update
endo.tick(dt);  // glands → bus decay → adapters → valence

// Signal events
endo.signal_event(EndocrineEvent::REWARD_RECEIVED, 0.8f);
endo.signal_event(EndocrineEvent::NOVELTY_ENCOUNTERED, 0.5f);

// Read state
CognitiveMode mode = endo.bus().current_mode();
float cortisol = endo.bus().concentration(HormoneId::CORTISOL);
float avg_dopamine = endo.bus().average_concentration(HormoneId::DOPAMINE_TONIC, 10);

// Callbacks
endo.bus().on_mode_change([](CognitiveMode old_m, CognitiveMode new_m) {
    // React to mode transitions
});
```

For the full EndocrineSystem facade with all gland access and lifecycle, read `references/endocrine_system.hpp`.

## Adapter Modulation

**ECAN Adapter** — Modulates attention spreading based on hormone state:
- High norepinephrine → narrow attention focus (increased hebbian link strength)
- High dopamine (tonic) → broad exploratory attention
- High cortisol → threat-biased attention allocation
- High anandamide → dampened noise, smoother attention flow

**PLN Adapter** — Modulates inference confidence:
- High serotonin → increased confidence in established patterns
- High cortisol → decreased confidence, more cautious reasoning
- High dopamine (phasic) → increased weight on novel evidence

## Composition

| Skill | Integration |
|-------|-------------|
| `meta-echo-dna` | Hormone state → FACS AU modulation (cortisol → AU4, dopamine → AU12) |
| `unreal-echo` | Endocrine system as emotional layer in cognitive cycle |
| `echo-introspect` | Valence memory and moral perception for self-analysis |
| `deep-tree-echo-core-self` | Endocrine state as part of identity mesh |
| `nn` | Reservoir dynamics coupled with hormone decay curves |
| `time-crystal-nn` | Circadian gland maps to temporal hierarchy scales |
