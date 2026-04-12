# FACS Action Unit to MetaHuman CTRL_ Morph Target Mapping

## Core Expression Action Units

| FACS AU | Description | MetaHuman Morph Target | Intensity Range |
|---------|-------------|----------------------|-----------------|
| AU1 | Inner Brow Raise | CTRL_brow_inner_UP | 0.0 - 1.0 |
| AU2 | Outer Brow Raise | CTRL_brow_outer_UP | 0.0 - 1.0 |
| AU4 | Brow Lowerer | CTRL_brow_down | 0.0 - 1.0 |
| AU5 | Upper Lid Raise | CTRL_eye_upperLid_UP | 0.0 - 1.0 |
| AU6 | Cheek Raise | CTRL_cheek_raise | 0.0 - 1.0 |
| AU7 | Lid Tightener | CTRL_eye_squint | 0.0 - 1.0 |
| AU9 | Nose Wrinkle | CTRL_nose_wrinkle | 0.0 - 1.0 |
| AU10 | Upper Lip Raise | CTRL_mouth_upperLip_UP | 0.0 - 1.0 |
| AU12 | Lip Corner Pull (Smile) | CTRL_mouth_cornerPull | 0.0 - 1.0 |
| AU14 | Dimpler | CTRL_mouth_dimple | 0.0 - 1.0 |
| AU15 | Lip Corner Depress | CTRL_mouth_cornerDepress | 0.0 - 1.0 |
| AU17 | Chin Raise | CTRL_chin_raise | 0.0 - 1.0 |
| AU20 | Lip Stretch | CTRL_mouth_stretch | 0.0 - 1.0 |
| AU23 | Lip Tightener | CTRL_mouth_tighten | 0.0 - 1.0 |
| AU25 | Lips Part | CTRL_mouth_lipsPart | 0.0 - 1.0 |
| AU26 | Jaw Drop | CTRL_jaw_open | 0.0 - 1.0 |
| AU28 | Lip Suck | CTRL_mouth_lipSuck | 0.0 - 1.0 |
| AU43 | Eyes Closed | CTRL_eye_blink | 0.0 - 1.0 |
| AU45 | Blink | CTRL_eye_blink | 0.0 - 1.0 (rapid) |
| AU46 | Wink | CTRL_eye_blink_L or _R | 0.0 - 1.0 |

## Composite Expressions

| Expression | Action Units | Aesthetic Modifier |
|------------|-------------|-------------------|
| Genuine Smile | AU6 + AU12 | ConfidencePosture boost |
| Flirtatious | AU12 + AU6 + AU46 | Charisma amplification |
| Curious | AU1 + AU2 + AU5 | EyeSparkle increase |
| Confident | AU2 + AU12 + AU17 | ConfidencePosture max |
| Playful | AU12 + AU25 + AU6 | Charisma + Sparkle |

## Micro-Expression Channels (Chaotic Modulation)

These channels receive noise from the Lorenz attractor:
- `CTRL_brow_inner_UP` - Subtle brow micro-movements
- `CTRL_eye_squint` - Eye tension micro-fluctuations
- `CTRL_mouth_cornerPull` - Mouth corner micro-twitches
- `CTRL_nose_wrinkle` - Nose micro-wrinkles
- `CTRL_jaw_open` - Jaw micro-movements

## DNA File Structure

MetaHuman DNA files contain:
- **Descriptor:** Name, archetype, gender, age, metadata
- **Definition:** Joints, blend shapes, animated maps, meshes per LOD
- **Behavior:** Joint animations, blend shape animations, animated map parameters
- **Geometry:** Mesh vertex positions, topology, texture coordinates per LOD

### Key DNA Operations (via DNACalib C++ API)
- `RenameJointCommand` - Rename joints
- `RemoveJointCommand` - Remove joints
- `SetNeutralJointTranslationsCommand` - Modify neutral pose
- `SetBlendShapeTargetDeltasCommand` - Modify blend shape deltas
- `PruneBlendShapeTargetsCommand` - Remove small deltas
- `RotateCommand` / `ScaleCommand` / `TranslateCommand` - Transform rig
- `RemoveMeshCommand` - Remove meshes by LOD
- `ClearBlendShapesCommand` - Clear all blend shape data
