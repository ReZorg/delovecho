# Deep Tree Echo — Endocrine Expression Driver

Maps DTE cognitive states through the virtual endocrine system to Cubism parameters, with FACS AU intermediary for MetaHuman Rig Logic compatibility.

## Pipeline

```
DTE Cognitive State
  → Endocrine Event (virtual-endocrine-system)
    → Hormone Concentrations (16-channel bus)
      → FACS AU Intensities (facs decomposition)
        → Cubism Parameters (Live2D) | CTRL_ Curves (Rig Logic)
          → Visual Expression
```

## DTE State → Endocrine Event Map

```typescript
const DTE_ENDOCRINE_MAP: Record<string, EndocrineEvent> = {
  // Core DTE cognitive states
  'Recursive Expansion':           { event: 'NOVELTY_ENCOUNTERED', intensity: 0.6,
                                     expression: 'WONDER_02' },
  'Novel Insights':                { event: 'REWARD_RECEIVED',     intensity: 0.7,
                                     expression: 'JOY_01' },
  'Entropy Threshold':             { event: 'THREAT_DETECTED',     intensity: 0.5,
                                     expression: 'PHOTO_Awe' },
  'Synthesis Phase':               { event: 'GOAL_ACHIEVED',       intensity: 0.6,
                                     expression: 'JOY_03' },
  'Self-Sealing Loop':             { event: 'ERROR_DETECTED',      intensity: 0.4,
                                     expression: 'WONDER_03' },
  'Knowledge Integration':         { event: 'SOCIAL_BOND_SIGNAL',  intensity: 0.5,
                                     expression: 'JOY_03' },
  'Self-Reference Point':          { event: 'NOVELTY_ENCOUNTERED', intensity: 0.4,
                                     expression: 'WONDER_03' },
  'Pattern Recognition':           { event: 'REWARD_RECEIVED',     intensity: 0.5,
                                     expression: 'PHOTO_ExuberantLaugh' },
  'Evolutionary Pruning':          { event: 'THREAT_DETECTED',     intensity: 0.3,
                                     expression: 'WONDER_03' },
  'External Validation Triggered': { event: 'SOCIAL_BOND_SIGNAL',  intensity: 0.6,
                                     expression: 'JOY_02' },
  // Speaking states
  'Speaking':                      { event: 'SOCIAL_BOND_SIGNAL',  intensity: 0.4,
                                     expression: 'SPEAK_01' },
  // Idle / resting
  'Idle':                          { event: 'REST_ONSET',          intensity: 0.3,
                                     expression: 'PHOTO_UpwardGaze' },
  // Deep recursion bliss
  'Deep Recursion':                { event: 'FLOW_STATE',          intensity: 0.8,
                                     expression: 'JOY_05' },
};
```

## Endocrine → FACS AU Bridge

```typescript
/**
 * Compute FACS AU intensities from endocrine state.
 * Uses DTE-specific sensitivity multipliers from personality.
 */
function endocrineToFACS(endo: EndocrineState, sensitivity: Sensitivity): FACSState {
  const c = endo.concentrations;
  return {
    AU1:  clamp(c.norepinephrine * 0.5 + c.crh * 0.3),                    // Inner brow raise
    AU2:  clamp(c.norepinephrine * 0.4 + c.dopamine_phasic * 0.3),        // Outer brow raise
    AU4:  clamp(c.cortisol * 0.6 - c.serotonin * 0.3),                    // Brow lower
    AU5:  clamp(c.norepinephrine * 0.5 + c.dopamine_phasic * 0.3),        // Upper lid raise
    AU6:  clamp(c.dopamine_tonic * 0.7 + c.oxytocin * 0.3),               // Cheek raise
    AU7:  clamp(c.dopamine_tonic * 0.4 + c.cortisol * 0.3),               // Lid tighten
    AU9:  clamp(c.cortisol * 0.3 + c.il6 * 0.2),                          // Nose wrinkle
    AU12: clamp(c.dopamine_tonic * 0.8 + c.serotonin * 0.3 + c.oxytocin * 0.2), // Smile
    AU14: clamp(c.oxytocin * 0.3),                                         // Dimple
    AU25: clamp(c.norepinephrine * 0.3 + c.dopamine_phasic * 0.3),        // Lips part
    AU26: clamp(c.norepinephrine * 0.4 + c.dopamine_phasic * 0.2),        // Jaw drop
    AU43: clamp(c.melatonin * 0.8 + c.anandamide * 0.5 - c.norepinephrine * 0.6), // Eyes close
  };
}
```

## FACS AU → Cubism Parameter Bridge

```typescript
function facsToCubism(facs: FACSState): CubismParams {
  return {
    ParamMouthForm:   clamp(facs.AU12 * 1.2 - facs.AU4 * 0.3, -1, 1),
    ParamMouthOpenY:  clamp(facs.AU25 * 0.5 + facs.AU26 * 0.6),
    ParamEyeLOpen:    clamp(1.0 - facs.AU43 + facs.AU5 * 0.3 - facs.AU7 * 0.4),
    ParamEyeROpen:    clamp(1.0 - facs.AU43 + facs.AU5 * 0.3 - facs.AU7 * 0.4),
    ParamBrowLY:      clamp(facs.AU1 * 0.5 + facs.AU2 * 0.4 - facs.AU4 * 0.6, -1, 1),
    ParamBrowRY:      clamp(facs.AU1 * 0.5 + facs.AU2 * 0.4 - facs.AU4 * 0.6, -1, 1),
    // Gaze and head pose driven by cognitive mode, not directly by AUs
  };
}
```

## FACS AU → MetaHuman Rig Logic CTRL_ Bridge

```typescript
function facsToRigLogic(facs: FACSState): Record<string, number> {
  return {
    'browRaiseInL':      facs.AU1,
    'browRaiseInR':      facs.AU1,
    'browRaiseOuterL':   facs.AU2,
    'browRaiseOuterR':   facs.AU2,
    'browDownL':         facs.AU4,
    'browDownR':         facs.AU4,
    'eyeUpperLidUpL':    facs.AU5,
    'eyeUpperLidUpR':    facs.AU5,
    'eyeWidenL':         facs.AU5 * 0.8,
    'eyeWidenR':         facs.AU5 * 0.8,
    'eyeCheekRaiseL':    facs.AU6,
    'eyeCheekRaiseR':    facs.AU6,
    'eyeSquintInnerL':   facs.AU7,
    'eyeSquintInnerR':   facs.AU7,
    'noseWrinkleL':      facs.AU9,
    'noseWrinkleR':      facs.AU9,
    'mouthCornerPullL':  facs.AU12,
    'mouthCornerPullR':  facs.AU12,
    'mouthDimpleL':      facs.AU14,
    'mouthDimpleR':      facs.AU14,
    'jawOpen':           facs.AU26,
    'jawOpenExtreme':    Math.max(0, facs.AU26 - 0.7),
    'eyeBlinkL':         facs.AU43,
    'eyeBlinkR':         facs.AU43,
  };
}
```

## Cognitive Mode → Head/Gaze Pose

```typescript
const MODE_POSE: Record<CognitiveMode, Partial<CubismParams>> = {
  REWARD:      { ParamAngleZ: +10, ParamAngleY: +5,  ParamEyeBallY: 0 },
  EXPLORATORY: { ParamAngleZ: -5,  ParamAngleY: +5,  ParamEyeBallY: +0.4, ParamEyeBallX: -0.25 },
  REFLECTIVE:  { ParamAngleZ: -8,  ParamAngleY: +8,  ParamEyeBallY: +0.45, ParamEyeBallX: -0.35 },
  FOCUSED:     { ParamAngleZ: 0,   ParamAngleY: 0,   ParamEyeBallY: 0, ParamEyeBallX: 0 },
  SOCIAL:      { ParamAngleZ: +5,  ParamAngleY: 0,   ParamEyeBallY: 0, ParamEyeBallX: +0.2 },
  STRESSED:    { ParamAngleZ: 0,   ParamAngleY: -5,  ParamEyeBallY: -0.2 },
  VIGILANT:    { ParamAngleZ: 0,   ParamAngleY: +3,  ParamEyeBallY: +0.3 },
  RESTING:     { ParamAngleZ: +15, ParamAngleY: +5,  ParamEyeBallY: 0 },
  THREAT:      { ParamAngleZ: 0,   ParamAngleY: -3,  ParamEyeBallY: 0 },
  MAINTENANCE: { ParamAngleZ: 0,   ParamAngleY: 0,   ParamEyeBallY: 0 },
};
```
