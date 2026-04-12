# Expression State Machine Reference

## State Definitions

### Idle State

The default resting state. Only the Lorenz micro-expression layer is active, providing subtle, natural facial movement that prevents the uncanny valley of a perfectly still face.

**Active systems**: Lorenz attractor (ChaosIntensity=0.15), baseline AU values from resting endocrine state.

**Transition out**: When emotional valence exceeds 0.3, arousal exceeds 0.4, or speech input is detected.

### Speaking State

Driven by viseme data from text-to-speech or audio analysis. Mouth AUs (AU25, AU26, AU22, AU18) are primarily controlled by the viseme system, while upper face AUs remain under cognitive/endocrine control.

**Viseme-to-AU mapping:**

| Viseme | Primary AUs | Example Phonemes |
|--------|------------|-----------------|
| sil (silence) | None | Pauses |
| PP | AU24(0.6) + AU23(0.4) | p, b, m |
| FF | AU25(0.3) + AU10(0.2) | f, v |
| TH | AU25(0.4) + AU18(0.2) | th |
| DD | AU25(0.3) + AU26(0.2) | t, d, n |
| kk | AU26(0.3) | k, g |
| CH | AU22(0.4) + AU25(0.3) | sh, ch, j |
| SS | AU25(0.2) | s, z |
| nn | AU25(0.2) + AU26(0.1) | n, l |
| RR | AU22(0.3) | r |
| aa | AU26(0.6) + AU25(0.4) | a (open) |
| E | AU25(0.3) + AU20(0.2) | e |
| ih | AU25(0.2) + AU20(0.1) | i |
| oh | AU22(0.4) + AU26(0.4) | o |
| ou | AU22(0.5) + AU18(0.3) | u |

### Emoting State

Full expression mode. All AUs are active and driven by the combined hormone + cognitive pipeline. The Lorenz micro-expression layer continues but at reduced intensity (ChaosIntensity=0.08) to avoid competing with the primary expression.

**Entry threshold**: Emotional valence > 0.3 OR arousal > 0.4.

**Exit threshold**: Emotional valence < 0.15 AND arousal < 0.2 (hysteresis prevents flickering).

### Listening State

Active when another agent or user is speaking. Provides empathetic mirroring through subtle AU tracking:

| Mirrored AU | Source | Scale Factor |
|-------------|--------|-------------|
| AU12 (smile) | Speaker's detected valence | 0.3 |
| AU1 (inner brow) | Speaker's detected arousal | 0.2 |
| AU6 (cheek raise) | Speaker's detected happiness | 0.25 |
| AU4 (brow lower) | Speaker's detected concern | 0.2 |

### Transitioning State

A blend state that interpolates between any two states over 0.15-0.3 seconds. Uses cosine interpolation for smooth easing:

```
blend = 0.5 * (1 - cos(PI * t / duration))
AU_current = AU_source * (1 - blend) + AU_target * blend
```

**Minimum transition time**: 0.15s (prevents corrective expression "pops" in Rig Logic).

## State Transition Rules

```
Idle → Speaking:     OnSpeechInputDetected()
Idle → Emoting:      Valence > 0.3 OR Arousal > 0.4
Idle → Listening:    OnOtherAgentSpeaking()
Speaking → Emoting:  Valence > 0.5 (emotional speech)
Speaking → Idle:     OnSpeechComplete() AND Valence < 0.15
Emoting → Idle:      Valence < 0.15 AND Arousal < 0.2 (with 0.5s hold)
Emoting → Speaking:  OnSpeechInputDetected() (blend, don't cut)
Listening → Idle:    OnOtherAgentSilent() (after 1.0s)
Any → Transitioning: On any state change
Transitioning → Target: On blend complete
```

## Blueprint Implementation

In the Animation Blueprint, create an Enum `EExpressionState` with values: Idle, Speaking, Emoting, Listening, Transitioning. Use a State Machine node in the AnimGraph with these states and transition rules. Each state drives a different blend of the AU-to-morph-target pipeline.
