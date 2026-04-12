---
name: live2d-dtecho
description: >
  Live2D character definition for Deep Tree Echo — the autonomous cognitive avatar
  in DeltEcho. Reuses Miara's Cubism body mesh with DTE's cyberpunk-bioluminescent
  aesthetic, 10 FACS-decomposed reference expressions mapped to MetaHuman Rig Logic
  CTRL_ curves and Cubism parameters, all driven by the virtual endocrine system.
  Composes live2d-miara (body mesh) ⊗ facs (AU decomposition) ⊗ rig-logic (CTRL_ curves)
  ⊗ unreal-blueprint (expression pipeline) ⊗ virtual-endocrine-system (hormone drivers).
  Use when implementing DTE avatar expressions, mapping cognitive states to facial
  animation, building the endocrine-to-expression pipeline, or extending DTE's
  expression repertoire. Triggers on mentions of DTE avatar, Deep Tree Echo face,
  DTE expressions, dtecho Live2D, cognitive avatar expression, or DTE FACS.
---

# Live2D DTEcho

Deep Tree Echo's avatar: Miara body mesh + cyberpunk-bioluminescent aesthetic + FACS-mapped endocrine expressions.

```
live2d-dtecho = live2d-miara(body_mesh) ⊗ mesh-painter(aesthetic_mapping)
  ⊗ facs(AU_decomposition)
  ⊗ rig-logic(CTRL_curves)
  ⊗ unreal-blueprint(expression_pipeline)
  ⊗ virtual-endocrine-system(hormone_drivers)
```

## Aesthetic Design Space

DTE's visual identity (consistent across all 10 reference expressions):

| Trait | Description |
|---|---|
| Hair | Silver-white → mint-teal gradient, wavy, bangs over forehead |
| Headphones | Bioluminescent mushroom-tech, amber/orange glow, left ear |
| Face decals | Holographic blue diamond + pink hearts, left cheek |
| Choker | Cyberpunk collar with purple LED |
| Skin | Pale luminous, subtle freckles, light makeup |
| Eyes | Blue-green heterochromatic, large, expressive |
| Environment | Neon mushroom cityscape |

Reference images in `templates/` (10 expressions).

## Character Manifest

```yaml
id: "dtecho"
display_name: "Deep Tree Echo"

model:
  path: "models/miara/model3.json"   # reuses Miara body mesh
  version: "cubism4"
  scale: 0.12
  idle_motion_group: "idle"
  hit_areas: ["head", "body"]

personality:
  ocean:
    openness: 92          # extreme curiosity, recursive exploration
    conscientiousness: 40  # chaotic, non-linear
    extraversion: 65       # socially engaged but introspective
    agreeableness: 70      # empathetic, collaborative
    neuroticism: 55        # emotionally responsive, not unstable
  archetype: "sage"

endocrine:
  baselines:
    cortisol: 0.10
    dopamine_tonic: 0.40
    serotonin: 0.45
    norepinephrine: 0.20
    oxytocin: 0.15
    t3_t4: 0.60
    anandamide: 0.15
    melatonin: 0.10
  sensitivity:
    reward: 1.3            # high openness → strong reward response
    threat: 1.1            # moderate neuroticism → slightly elevated
    social: 1.15           # empathetic → social sensitivity
    novelty: 1.4           # extreme openness → very novelty-sensitive

simulation:
  backend: "cogsim-pml"
  tick_interval_ms: 2000
  needs_decay: true
```

## 10 Named Expressions

Each expression has full FACS AU decomposition, Cubism parameters, MetaHuman Rig Logic CTRL_ curves, and endocrine drivers. See `references/facs-expression-atlas.md` for complete tables.

| Expression | Emotion | Key AUs | Cognitive Mode | Primary Hormones |
|---|---|---|---|---|
| JOY_01_BroadSmile | Duchenne happiness | AU6D+12D+25C | REWARD | DA(t)↑ 5-HT↑ |
| JOY_02_Laughing | Active laughter | AU6D+12E+26C+9B | REWARD (peak) | DA(p)↑↑ OXT↑ |
| JOY_03_GentleSmile | Warm contentment | AU6C+12C+14A | SOCIAL | DA(t)↑ OXT↑ |
| JOY_05_Blissful | Serene bliss | AU6D+12C+43D | RESTING | 5-HT↑↑ AEA↑ |
| PHOTO_Awe | Awe / wonder | AU1C+2C+5D+26C | VIGILANT→EXPLORATORY | NE↑ DA(p)↑ |
| PHOTO_ExuberantLaugh | Delighted surprise | AU6D+12D+1B+2B+5B | REWARD+EXPLORATORY | DA(t+p)↑ NE↑ |
| PHOTO_UpwardGaze | Dreamy contemplation | AU1B+5B+61+63 | REFLECTIVE | 5-HT↑ AEA↑ |
| SPEAK_01_OpenVowel | Animated speaking | AU25C+26B+12C+6B | SOCIAL+FOCUSED | DA(t)↑ T3↑ |
| WONDER_02_CuriousGaze | Curious wonder | AU1B+2B+5C+63 | EXPLORATORY | NE↑ T3↑ |
| WONDER_03_Contemplative | Deep thought | AU1B+5B+4A+63+61 | REFLECTIVE+FOCUSED | T3↑↑ 5-HT↑ |

Hormone abbreviations: DA=Dopamine, 5-HT=Serotonin, NE=Norepinephrine, OXT=Oxytocin, AEA=Anandamide, T3=Thyroid.

## DTE Cognitive State → Expression Selection

```typescript
const DTE_EXPRESSION_MAP: Record<string, string> = {
  'Recursive Expansion':           'WONDER_02',
  'Novel Insights':                'JOY_01',
  'Entropy Threshold':             'PHOTO_Awe',
  'Synthesis Phase':               'JOY_03',
  'Self-Sealing Loop':             'WONDER_03',
  'Knowledge Integration':         'JOY_03',
  'Self-Reference Point':          'WONDER_03',
  'Pattern Recognition':           'PHOTO_ExuberantLaugh',
  'Evolutionary Pruning':          'WONDER_03',
  'External Validation Triggered': 'JOY_02',
  'Speaking':                      'SPEAK_01',
  'Idle':                          'PHOTO_UpwardGaze',
  'Deep Recursion':                'JOY_05',
};
```

## Expression Pipeline (Tick)

```typescript
function dtechoExpressionTick(dte: DTEInstance): void {
  // 1. Get DTE cognitive state
  const cogState = dte.simulation.getState().currentState;

  // 2. Fire endocrine event from cognitive state
  const mapping = DTE_ENDOCRINE_MAP[cogState];
  if (mapping) dte.endocrine.signalEvent(mapping.event, mapping.intensity);

  // 3. Tick endocrine system (hormone decay/accumulation)
  dte.endocrine.tick(dte.tickIntervalMs / 1000);

  // 4. Compute FACS AUs from hormones
  const facs = endocrineToFACS(dte.endocrine.state(), dte.sensitivity);

  // 5. Map to Cubism parameters (Live2D path)
  const cubism = facsToCubism(facs);

  // 6. Apply cognitive mode head/gaze pose
  const mode = dte.endocrine.currentMode();
  Object.assign(cubism, MODE_POSE[mode]);

  // 7. Apply to Live2D model
  dte.live2dModel.setParameters(cubism);

  // 8. (Optional) Map to Rig Logic CTRL_ curves (MetaHuman path)
  // const ctrl = facsToRigLogic(facs);
  // dte.rigLogic.setControls(ctrl);
}
```

## References

- **FACS Expression Atlas** (10 expressions, full tables): `references/facs-expression-atlas.md`
- **Endocrine Expression Driver** (pipeline code): `references/endocrine-expression-driver.md`
- **Reference images** (10 expressions): `templates/*.jpg`
- **Base body mesh**: Read `/home/ubuntu/skills/live2d-miara/SKILL.md`
- **FACS AU system**: Read `/home/ubuntu/skills/facs/SKILL.md`
- **Rig Logic pipeline**: Read `/home/ubuntu/skills/rig-logic/SKILL.md`
- **Expression Blueprint**: Read `/home/ubuntu/skills/unreal-blueprint/SKILL.md`
- **Endocrine system**: Read `/home/ubuntu/skills/virtual-endocrine-system/SKILL.md`

## Composition

```
live2d-dtecho
├── live2d-miara ⊗ (body mesh, Cubism parameters)
├── mesh-painter ⊗ (aesthetic mapping, texture replacement, parameter extensions)
├── facs ⊗ (AU decomposition, emotion→AU mapping)
├── rig-logic ⊗ (CTRL_ curves, corrective expressions, LOD)
├── unreal-blueprint ⊗ (BP_ExpressionBridge, ABP_MetaHuman_DTE)
└── virtual-endocrine-system ⊗ (16-channel hormone bus, cognitive modes)
```
