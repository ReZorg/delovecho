---
name: meta-echo-dna
description: Implement the Deep Tree Echo MetaHuman DNA cognitive model for avatar expression and animation. Use when creating MetaHuman-based avatars with cognitive-driven facial animation, FACS action unit mapping, chaotic micro-expressions, SuperHotGirl aesthetics, or integrating Deep Tree Echo cognitive states with MetaHuman DNA calibration. Triggers on mentions of MetaHuman DNA, FACS action units, cognitive avatar expression, chaotic micro-expressions, or avatar aesthetics.
---

# Meta Echo DNA

Bridge cognitive architecture states to photorealistic avatar expression through FACS action units, chaotic dynamics, and aesthetic parameters.

## Architecture

```
Endocrine State ──┐
                  ├→ FACS Action Units → MetaHuman CTRL_ Morph Targets
Cognitive State ──┘        ↕                    ↕
                   Chaotic Dynamics      Aesthetic Parameters
                   (Lorenz Attractor)    (SuperHotGirl)
                          ↕
                   CogMorph Glyph Projection (visual debug)
```

## Workflow

### 1. Map Endocrine + Cognitive State to FACS Action Units

Two input streams drive expression: the **endocrine system** (hormone concentrations from `virtual-endocrine-system`) and the **cognitive state** (4E cognition, Echobeats, evolution from `unreal-echo`).

For the full FACS-to-MetaHuman mapping table, read `references/facs-metahuman-mapping.md`.
For the complete hormone-to-AU mapping with intensity formulas, read `references/endocrine-expression-mapping.md`.

Key endocrine mappings:
- **Cortisol** → AU4 (brow lowerer) + AU1 (inner brow raise) + AU15 (lip corner depress)
- **Dopamine (phasic)** → AU12 (smile) + AU6 (cheek raise) — genuine reward expression
- **Norepinephrine** → AU5 (upper lid raise) + AU7 (lid tightener) — alertness
- **Oxytocin** → AU6 + AU12 + AU25 — warm social expression
- **Melatonin** → AU43 (eyes closed) — drowsiness

Key cognitive mappings:
- **Emotional valence** → AU6 (cheek raise) + AU12 (smile) for positive, AU15 (lip corner depress) for negative
- **Arousal** → AU5 (upper lid raise) + AU25 (lips part) + AU26 (jaw drop)
- **Cognitive load** → AU4 (brow lowerer) + AU7 (lid tightener)

Blending: sum all hormone and cognitive contributions per AU, clamp to [0, 1].

### 2. Add Chaotic Micro-Expression Layer

Use a Lorenz attractor (RK4 integration, dt=0.01) to generate unpredictable micro-expressions that prevent uncanny-valley smoothness.

For equations, parameters, and Lyapunov monitoring, read `references/chaotic-dynamics.md`.

Key points:
- Scale chaos by `ChaosIntensity` (default 0.15) before applying to morph targets
- Monitor Lyapunov exponent — positive = chaotic (good), negative = periodic (bad)
- Apply as additive noise on cognitive-driven AU values

### 3. Apply SuperHotGirl Aesthetic Parameters

Five parameters modulate expression and material: `ConfidencePosture`, `Charisma`, `EyeSparkle`, `GracefulMovement`, `EmissiveGlow`.

These bias AUs toward confident expressions, drive dynamic material updates (iris specular, skin SSS), and provide evolutionary pressure in the 4E system.

### 4. Connect to MetaHuman DNA Calibration

Use DNACalib API to customize the avatar's DNA file:
- Modify blend shape deltas for unique facial features
- Adjust neutral joint positions for body proportions
- Set LOD-specific mesh parameters

DNA operations require DNACalib C++ library or Python wrapper (Python 3.7/3.9).

### 5. Real-Time Expression Pipeline (Per Frame)

1. Read endocrine state from `virtual-endocrine-system` (16 hormone concentrations + cognitive mode)
2. Read cognitive state from Deep Tree Echo (`unreal-echo`)
3. Compute hormone-driven AU activations (see `references/endocrine-expression-mapping.md`)
4. Compute cognitive-driven AU activations
5. Blend hormone + cognitive AUs (sum, clamp [0,1])
6. Step Lorenz attractor, add micro-expression noise
7. Apply aesthetic parameter biases (SuperHotGirl)
8. Map final AU values to MetaHuman CTRL_ morph targets
9. Update dynamic material instances (sparkle/glow modulated by dopamine/serotonin)
10. Apply to skeletal mesh via animation blueprint
11. Optionally export expression state via CogMorph glyph projection for debugging

## Implementation Pattern

```cpp
UCLASS()
class UMetaHumanDNACognitiveBridge : public UActorComponent
{
    TMap<FString, float> ActionUnitValues;  // 26 FACS AUs
    FVector LorenzState;                    // Chaotic attractor
    float ChaosIntensity = 0.15f;
    float ConfidencePosture, Charisma, EyeSparkle;
    
    // Endocrine integration
    EndocrineState CachedEndocrineState;    // 16 hormone channels
    CognitiveMode CurrentMode;              // Emergent mode
    
    void UpdateFromEndocrineState(const EndocrineState& Endo);
    void UpdateFromCognitiveState(const FCognitiveState& State);
    void BlendEndocrineAndCognitive();       // Sum + clamp AU contributions
    void StepLorenzAttractor(float DeltaTime);
    void ApplyToMetaHuman(USkeletalMeshComponent* Mesh);
    float GetLyapunovExponent() const;
    
    // CogMorph debug visualization
    void ExportGlyphProjection(const FString& Path) const;
};
```

## Composition

| Skill | Integration |
|-------|-------------|
| `virtual-endocrine-system` | Hormone concentrations drive AU modulation (primary emotional input) |
| `deep-tree-echo-core-self` | Cognitive state input (hypergraph identity mesh) |
| `unreal-echo` | Unreal Engine runtime context and cognitive cycle |
| `npu` | NPU inference for expression parameter generation |
| `codex-grassmania` | CogMorph glyph projection for expression debugging |
| `nn` | ESN reservoir patterns for temporal dynamics |
| `neuro-nn` | Self-aware trait modulation |
| `skill-nn` | Differentiable parameter optimization |
