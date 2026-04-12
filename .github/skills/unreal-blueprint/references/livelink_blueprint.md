# Live Link Face Capture Blueprint Patterns

## Overview

Live Link enables real-time face capture from ARKit (iPhone/iPad), MetaHuman Animator, or third-party capture systems to drive MetaHuman facial animation in UE5. This document provides Blueprint patterns for integrating Live Link with the DTE cognitive avatar.

## Setup Blueprint

```
Event BeginPlay
├─ Create Live Link Source (type: ARKit or MetaHuman Animator)
├─ SET → LiveLinkSource
├─ Get Live Link Subject Names → Filter for face subjects
├─ SET → FaceSubjectName
└─ Enable Live Link on MetaHuman Face Component
```

## Capture-to-DTE Bridge

Live Link provides raw blend shape values (ARKit 52 blend shapes). These must be converted to FACS AUs before feeding into the DTE expression pipeline:

| ARKit Blend Shape | FACS AU | Conversion |
|-------------------|---------|------------|
| browInnerUp | AU1 | Direct |
| browOuterUpLeft/Right | AU2 | Direct (per side) |
| browDownLeft/Right | AU4 | Direct (per side) |
| eyeWideLeft/Right | AU5 | Direct (per side) |
| cheekSquintLeft/Right | AU6 | Direct (per side) |
| eyeSquintLeft/Right | AU7 | Direct (per side) |
| noseSneerLeft/Right | AU9 | Direct (per side) |
| mouthSmileLeft/Right | AU12 | Direct (per side) |
| mouthFrownLeft/Right | AU15 | Direct (per side) |
| mouthPucker | AU18 | Direct |
| mouthFunnel | AU22 | Direct |
| mouthPressLeft/Right | AU24 | Direct (per side) |
| jawOpen | AU26 | Direct |
| eyeBlinkLeft/Right | AU43 | Direct (per side) |

## Hybrid Mode: Capture + Cognitive

The DTE system can blend live capture data with cognitive-driven expression:

```
Event Tick
├─ Get Live Link AU values (from capture)
├─ Get Cognitive AU values (from BP_ExpressionBridge)
├─ Blend: AU_final = AU_capture * CaptureWeight + AU_cognitive * (1 - CaptureWeight)
│   └─ CaptureWeight: 0.0 = full cognitive, 1.0 = full capture, 0.5 = hybrid
└─ Apply blended AUs to MetaHuman
```

This allows a human performer to drive the avatar while the cognitive system fills in emotional nuance and micro-expressions.

## Performance Notes

Live Link runs at the capture device's frame rate (typically 30-60 Hz). The DTE cognitive cycle runs at 10-30 Hz. Use interpolation to smooth the difference when blending.
