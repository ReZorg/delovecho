---
name: live2d-miara
description: >
  Live2D Cubism 4 character definition for Miara — the default DeltEcho avatar.
  Instantiates live2d-char-model with Miara's Cubism model, Explorer archetype,
  balanced OCEAN personality, and CogSim PML simulation backend.
  Use when deploying the Miara avatar in DeltEcho, customizing Miara's personality
  or expressions, debugging Miara model loading, or as the base body mesh for
  derived characters (e.g., live2d-dtecho). Triggers on mentions of Miara,
  Miara avatar, Miara model, default DeltEcho avatar, or Miara Live2D.
---

# Live2D Miara

Default DeltEcho companion avatar. Cubism 4 model with Explorer archetype.

Instantiation: `live2d-char-model(char="miara")`

## Model Assets

```
packages/frontend/static/models/miara/
├── model3.json              # Cubism 4 model descriptor
├── miara.4096/              # texture atlas directory
│   └── texture_00.png       # 4096×4096 (13MB) — optimize to 2048px for CF Workers
└── motions/
    ├── idle_01.motion3.json
    ├── idle_02.motion3.json
    └── tap_body.motion3.json
```

**Known issue**: The 4096px texture (13MB) causes 2–4s load delay on Cloudflare Workers. Downscale to 2048px for production.

## Character Manifest

```yaml
id: "miara"
display_name: "Miara"

model:
  path: "model3.json"
  version: "cubism4"
  scale: 0.12
  idle_motion_group: "idle"
  hit_areas: ["head", "body"]

personality:
  ocean:
    openness: 65
    conscientiousness: 45
    extraversion: 55
    agreeableness: 60
    neuroticism: 35
  archetype: "explorer"

endocrine:
  baselines:
    cortisol: 0.12
    dopamine_tonic: 0.35
    serotonin: 0.45
    norepinephrine: 0.12
    oxytocin: 0.15
    t3_t4: 0.50
    anandamide: 0.12
  sensitivity:
    reward: 1.1
    threat: 0.85
    social: 1.05
    novelty: 1.15

expressions:
  smile:
    dopamine_tonic: ">0.5"
    serotonin: ">0.4"
  surprised:
    norepinephrine: ">0.6"
    dopamine_phasic: ">0.3"
  sad:
    serotonin: "<0.2"
    cortisol: ">0.4"
  angry:
    cortisol: ">0.6"
    norepinephrine: ">0.5"
  relaxed:
    anandamide: ">0.3"
    cortisol: "<0.1"
  focused:
    norepinephrine: ">0.4"
    t3_t4: ">0.6"

motions:
  idle: ["RESTING", "REFLECTIVE"]
  tap_body: ["SOCIAL"]

simulation:
  backend: "cogsim-pml"
  tick_interval_ms: 2000
  needs_decay: true
```

## Cubism Parameters

Miara's model3.json exposes these Cubism parameters for expression control:

| Parameter | Range | Purpose |
|---|---|---|
| ParamAngleX | -30 to 30 | Head yaw |
| ParamAngleY | -30 to 30 | Head pitch |
| ParamAngleZ | -30 to 30 | Head roll |
| ParamEyeLOpen | 0 to 1 | Left eye openness |
| ParamEyeROpen | 0 to 1 | Right eye openness |
| ParamEyeBallX | -1 to 1 | Eye gaze horizontal |
| ParamEyeBallY | -1 to 1 | Eye gaze vertical |
| ParamBrowLY | -1 to 1 | Left brow height |
| ParamBrowRY | -1 to 1 | Right brow height |
| ParamMouthOpenY | 0 to 1 | Mouth open amount |
| ParamMouthForm | -1 to 1 | Mouth shape (-1=frown, 1=smile) |
| ParamBodyAngleX | -10 to 10 | Body sway |

## Endocrine → Cubism Parameter Bridge

Direct mapping from endocrine state to Cubism parameters (bypasses FACS for Live2D):

| Endocrine Condition | Cubism Parameter | Value |
|---|---|---|
| Dopamine(tonic) > 0.5 | ParamMouthForm | +0.6 to +1.0 |
| Serotonin > 0.4 | ParamEyeLOpen, ParamEyeROpen | 0.7 (relaxed) |
| Norepinephrine > 0.6 | ParamEyeLOpen, ParamEyeROpen | 1.0 (wide) |
| Norepinephrine > 0.6 | ParamBrowLY, ParamBrowRY | +0.5 (raised) |
| Cortisol > 0.5 | ParamBrowLY, ParamBrowRY | -0.5 (lowered) |
| Cortisol > 0.5 | ParamMouthForm | -0.4 (frown) |
| Oxytocin > 0.4 | ParamMouthForm | +0.3 (gentle smile) |
| Anandamide > 0.3 | ParamEyeLOpen, ParamEyeROpen | 0.3 (drowsy) |
| T3/T4 > 0.6 | ParamEyeBallY | +0.3 (upward gaze) |

## Derived Characters

Miara's body mesh serves as the base for derived characters. The `live2d-dtecho` character reuses Miara's Cubism model but overrides personality, endocrine baselines, and expression mappings to match the Deep Tree Echo aesthetic.

## Composition

- **Parent**: `live2d-char-model` (parameterized template)
- **Derived**: `live2d-dtecho` (DTE personality overlay on Miara mesh)
- **Renderer**: `live2d-avatar` (pixi-live2d-display)
- **Simulation**: `cogsim-pml` (lightweight DES)
- **Endocrine**: `virtual-endocrine-system` (16-channel hormone bus)
