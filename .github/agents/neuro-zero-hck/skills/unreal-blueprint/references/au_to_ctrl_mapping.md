# FACS AU to MetaHuman CTRL_ Morph Target Mapping

This table maps each FACS Action Unit used by the DTE expression system to the corresponding MetaHuman `CTRL_expressions_` morph target names. These are the exact names used in the UE5 Skeletal Mesh Component's `SetMorphTarget` function.

## Primary Mapping Table

| FACS AU | AU Name | MetaHuman CTRL_ Morph Target(s) | Decomposition |
|---------|---------|--------------------------------|---------------|
| AU1 | Inner brow raise | `CTRL_expressions_browRaiseInnerL`, `CTRL_expressions_browRaiseInnerR` | Direct 1:1 |
| AU2 | Outer brow raise | `CTRL_expressions_browRaiseOuterL`, `CTRL_expressions_browRaiseOuterR` | Direct 1:1 |
| AU4 | Brow lowerer | `CTRL_expressions_browDownL`, `CTRL_expressions_browDownR`, `CTRL_expressions_browLateralL`, `CTRL_expressions_browLateralR` | Split: v*0.7 to browDown, v*0.3 to browLateral |
| AU5 | Upper lid raiser | `CTRL_expressions_eyeUpperLidUpL`, `CTRL_expressions_eyeUpperLidUpR`, `CTRL_expressions_eyeWidenL`, `CTRL_expressions_eyeWidenR` | Split: v*0.6 to UpperLidUp, v*0.4 to Widen |
| AU6 | Cheek raiser | `CTRL_expressions_eyeCheekRaiseL`, `CTRL_expressions_eyeCheekRaiseR` | Direct 1:1 |
| AU7 | Lid tightener | `CTRL_expressions_eyeSquintInnerL`, `CTRL_expressions_eyeSquintInnerR` | Direct 1:1 |
| AU9 | Nose wrinkler | `CTRL_expressions_noseWrinkleL`, `CTRL_expressions_noseWrinkleR` | Direct 1:1 |
| AU10 | Upper lip raiser | `CTRL_expressions_mouthUpperLipRaiseL`, `CTRL_expressions_mouthUpperLipRaiseR` | Direct 1:1 |
| AU12 | Lip corner puller | `CTRL_expressions_mouthCornerPullL`, `CTRL_expressions_mouthCornerPullR` | Direct 1:1 |
| AU14 | Dimpler | `CTRL_expressions_mouthDimpleL`, `CTRL_expressions_mouthDimpleR` | Direct 1:1 |
| AU15 | Lip corner depressor | `CTRL_expressions_mouthCornerDepressL`, `CTRL_expressions_mouthCornerDepressR` | Direct 1:1 |
| AU17 | Chin raiser | `CTRL_expressions_jawChinRaiseDL`, `CTRL_expressions_jawChinRaiseDR` | Direct 1:1 |
| AU18 | Lip pucker | `CTRL_expressions_mouthLipsPurseUL`, `CTRL_expressions_mouthLipsPurseDL`, `CTRL_expressions_mouthLipsTowardsUL`, `CTRL_expressions_mouthLipsTowardsDL` | Split: v*0.5 to Purse, v*0.3 to Towards |
| AU20 | Lip stretcher | `CTRL_expressions_mouthStretchL`, `CTRL_expressions_mouthStretchR` | Direct 1:1 |
| AU22 | Lip funneler | `CTRL_expressions_mouthFunnelDL`, `CTRL_expressions_mouthFunnelUL` | Split: v*0.5 each |
| AU23 | Lip tightener | `CTRL_expressions_mouthLipsTightenUL`, `CTRL_expressions_mouthLipsTightenUR` | Direct 1:1 |
| AU24 | Lip pressor | `CTRL_expressions_mouthPressDL`, `CTRL_expressions_mouthPressDR` | Direct 1:1 |
| AU25 | Lips part | `CTRL_expressions_mouthLipsPartL`, `CTRL_expressions_mouthLipsPartR` | Direct 1:1 |
| AU26 | Jaw drop | `CTRL_expressions_jawOpen` | Single control (bilateral) |
| AU43 | Eyes closed | `CTRL_expressions_eyeBlinkL`, `CTRL_expressions_eyeBlinkR` | Direct 1:1 |

## Blueprint Usage Pattern

```cpp
// In BP_ExpressionBridge::ApplyToMesh
void ApplyAUToMesh(USkeletalMeshComponent* Mesh, int32 AU, float Value)
{
    switch (AU)
    {
    case 12: // Lip corner puller (smile)
        Mesh->SetMorphTarget("CTRL_expressions_mouthCornerPullL", Value);
        Mesh->SetMorphTarget("CTRL_expressions_mouthCornerPullR", Value);
        break;
    case 4: // Brow lowerer (decomposed)
        Mesh->SetMorphTarget("CTRL_expressions_browDownL", Value * 0.7f);
        Mesh->SetMorphTarget("CTRL_expressions_browDownR", Value * 0.7f);
        Mesh->SetMorphTarget("CTRL_expressions_browLateralL", Value * 0.3f);
        Mesh->SetMorphTarget("CTRL_expressions_browLateralR", Value * 0.3f);
        break;
    // ... etc
    }
}
```

## Asymmetric Expression Support

For asymmetric expressions (e.g., smirk), set L and R morph targets to different values:

```
AU12L = 0.6, AU12R = 0.2  →  Asymmetric smile (smirk)
CTRL_expressions_mouthCornerPullL = 0.6
CTRL_expressions_mouthCornerPullR = 0.2
```
