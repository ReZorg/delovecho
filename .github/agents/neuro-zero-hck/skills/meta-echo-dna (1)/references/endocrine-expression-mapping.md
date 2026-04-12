# Endocrine System to Facial Expression Mapping

## Hormone → FACS Action Unit Modulation

Each hormone channel modulates specific FACS action units, creating biologically-grounded facial expressions that emerge from the endocrine state rather than being explicitly programmed.

### Direct Mappings

| Hormone | AU | Effect | Intensity Formula |
|---------|-----|--------|-------------------|
| Cortisol | AU4 (Brow Lowerer) | Worry/concern | `cortisol * 0.8` |
| Cortisol | AU1 (Inner Brow Raise) | Distress | `cortisol * 0.5` |
| Cortisol | AU15 (Lip Corner Depress) | Sadness/stress | `cortisol * 0.4` |
| Dopamine (phasic) | AU12 (Lip Corner Pull) | Smile/reward | `dopamine_phasic * 0.9` |
| Dopamine (phasic) | AU6 (Cheek Raise) | Genuine smile | `dopamine_phasic * 0.7` |
| Dopamine (tonic) | AU12 (Lip Corner Pull) | Baseline contentment | `dopamine_tonic * 0.3` |
| Serotonin | AU6 (Cheek Raise) | Warm contentment | `serotonin * 0.4` |
| Serotonin | AU12 (Lip Corner Pull) | Gentle smile | `serotonin * 0.3` |
| Norepinephrine | AU5 (Upper Lid Raise) | Alertness/surprise | `norepinephrine * 0.8` |
| Norepinephrine | AU7 (Lid Tightener) | Focus/vigilance | `norepinephrine * 0.5` |
| Norepinephrine | AU20 (Lip Stretcher) | Tension | `norepinephrine * 0.3` |
| Oxytocin | AU6 (Cheek Raise) | Warmth | `oxytocin * 0.6` |
| Oxytocin | AU12 (Lip Corner Pull) | Social smile | `oxytocin * 0.5` |
| Oxytocin | AU25 (Lips Part) | Openness | `oxytocin * 0.3` |
| Melatonin | AU43 (Eyes Closed) | Drowsiness | `melatonin * 0.7` |
| Melatonin | AU7 (Lid Tightener) | Heavy lids | `melatonin * 0.4` |
| IL-6 | AU4 (Brow Lowerer) | Discomfort | `il6 * 0.5` |
| IL-6 | AU10 (Upper Lip Raise) | Disgust/illness | `il6 * 0.4` |
| Anandamide | AU6 (Cheek Raise) | Relaxed contentment | `anandamide * 0.5` |
| Anandamide | AU25 (Lips Part) | Relaxed jaw | `anandamide * 0.3` |

### Cognitive Mode → Expression Preset

| Mode | Dominant Expression | Key AUs |
|------|-------------------|---------|
| RESTING | Neutral, relaxed | Low all |
| EXPLORATORY | Curious, open | AU5+AU25 moderate |
| FOCUSED | Concentrated | AU4+AU7 high |
| STRESSED | Tense, worried | AU1+AU4+AU15 high |
| SOCIAL | Warm, engaged | AU6+AU12 high |
| REFLECTIVE | Thoughtful | AU4 moderate, AU7 low |
| VIGILANT | Alert, scanning | AU5+AU7 high |
| MAINTENANCE | Drowsy, peaceful | AU43+AU7 moderate |
| REWARD | Joyful | AU6+AU12 very high |
| THREAT | Fear/anger | AU1+AU4+AU5+AU20 high |

### Blending Rules

1. Sum all hormone contributions per AU
2. Clamp to [0.0, 1.0]
3. Apply Lorenz attractor micro-expression noise (scale by ChaosIntensity)
4. Apply SuperHotGirl aesthetic bias (shifts toward confident expressions)
5. Map to MetaHuman CTRL_ morph targets via FACS-MetaHuman table
