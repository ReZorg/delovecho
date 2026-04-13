# Deep Tree Echo — FACS Expression Atlas

10 reference expressions with full FACS AU decomposition, MetaHuman Rig Logic CTRL_ curves, Cubism parameter mapping, and endocrine drivers. Each expression is derived from the DTE aesthetic reference images.

## Aesthetic Constants

All expressions share these visual traits:
- Silver-white to mint-teal gradient wavy hair
- Bioluminescent mushroom-tech headphones (left ear, amber/orange glow)
- Holographic face decals (blue diamond + pink hearts on left cheek)
- Cyberpunk choker/collar with purple LED
- Pale luminous skin with subtle freckles
- Blue-green heterochromatic eyes
- Neon mushroom cityscape environment

---

## JOY_01: Broad Smile (Duchenne)

**Reference**: `templates/JOY_01_BroadSmile.jpg`

### FACS Decomposition
| AU | Name | Intensity | Muscle |
|---|---|---|---|
| AU6 | Cheek Raiser | D (severe) | Orbicularis oculi (pars orbitalis) |
| AU12 | Lip Corner Puller | D | Zygomaticus major |
| AU25 | Lips Part | C (marked) | Depressor labii inferioris |
| AU7 | Lid Tightener | C | Orbicularis oculi (pars palpebralis) |
| AU43 | Eyes Closed | ~40% | Relaxation of levator palpebrae |

### MetaHuman Rig Logic Controls
| CTRL_ Curve | Value | Notes |
|---|---|---|
| eyeCheekRaiseL/R | 0.85 | Strong crow's feet |
| mouthCornerPullL/R | 0.80 | Broad symmetric smile |
| eyeSquintInnerL/R | 0.70 | From cheek push |
| eyeBlinkL/R | 0.40 | Partial closure from AU6 force |
| jawOpen | 0.15 | Slight teeth visibility |

### Cubism Parameters
| Parameter | Value | Notes |
|---|---|---|
| ParamMouthForm | +0.95 | Near-maximum smile |
| ParamMouthOpenY | 0.20 | Teeth visible |
| ParamEyeLOpen / ParamEyeROpen | 0.35 | Squinted from smile |
| ParamBrowLY / ParamBrowRY | +0.10 | Slight natural raise |
| ParamAngleZ | +10 | Right head tilt |
| ParamAngleY | +5 | Chin slightly raised |

### Endocrine Driver
| Hormone | Concentration | Role |
|---|---|---|
| Dopamine (tonic) | 0.75 | Sustained reward |
| Serotonin | 0.65 | Mood elevation |
| Oxytocin | 0.40 | Social warmth |
| Cortisol | 0.05 | Very low stress |

**Cognitive Mode**: REWARD

---

## JOY_02: Laughing

**Reference**: `templates/JOY_02_Laughing.jpg`

### FACS Decomposition
| AU | Name | Intensity | Muscle |
|---|---|---|---|
| AU6 | Cheek Raiser | D | Orbicularis oculi (pars orbitalis) |
| AU12 | Lip Corner Puller | E (maximum) | Zygomaticus major |
| AU25 | Lips Part | D | Depressor labii inferioris |
| AU26 | Jaw Drop | C | Masseter relaxation |
| AU7 | Lid Tightener | C | Orbicularis oculi (pars palpebralis) |
| AU9 | Nose Wrinkler | B (slight) | Levator labii superioris alaeque nasi |

### MetaHuman Rig Logic Controls
| CTRL_ Curve | Value |
|---|---|
| eyeCheekRaiseL/R | 0.85 |
| mouthCornerPullL/R | 1.00 |
| jawOpen | 0.45 |
| eyeSquintInnerL/R | 0.70 |
| noseWrinkleL/R | 0.30 |

### Cubism Parameters
| Parameter | Value |
|---|---|
| ParamMouthForm | +1.00 |
| ParamMouthOpenY | 0.55 |
| ParamEyeLOpen / ParamEyeROpen | 0.30 |
| ParamAngleZ | +15 |
| ParamAngleY | +8 |

### Endocrine Driver
| Hormone | Concentration |
|---|---|
| Dopamine (phasic) | 0.90 |
| Dopamine (tonic) | 0.70 |
| Serotonin | 0.60 |
| Oxytocin | 0.50 |
| Norepinephrine | 0.30 |

**Cognitive Mode**: REWARD (peak burst)

---

## PHOTO_Awe: Awe / Wonder

**Reference**: `templates/PHOTO_Awe.jpg`

### FACS Decomposition
| AU | Name | Intensity | Muscle |
|---|---|---|---|
| AU1 | Inner Brow Raiser | C | Frontalis (pars medialis) |
| AU2 | Outer Brow Raiser | C | Frontalis (pars lateralis) |
| AU5 | Upper Lid Raiser | D | Levator palpebrae superioris |
| AU25 | Lips Part | C | Depressor labii inferioris |
| AU26 | Jaw Drop | C | Masseter relaxation |
| AU27 | Mouth Stretch | B | Pterygoids, digastric |

### MetaHuman Rig Logic Controls
| CTRL_ Curve | Value |
|---|---|
| browRaiseInL/R | 0.70 |
| browRaiseOuterL/R | 0.70 |
| eyeUpperLidUpL/R | 0.80 |
| eyeWidenL/R | 0.75 |
| jawOpen | 0.55 |
| jawOpenExtreme | 0.20 |

### Cubism Parameters
| Parameter | Value |
|---|---|
| ParamMouthForm | 0.00 |
| ParamMouthOpenY | 0.65 |
| ParamEyeLOpen / ParamEyeROpen | 1.00 |
| ParamBrowLY / ParamBrowRY | +0.70 |
| ParamEyeBallY | +0.40 |
| ParamEyeBallX | -0.30 |

### Endocrine Driver
| Hormone | Concentration |
|---|---|
| Norepinephrine | 0.70 |
| Dopamine (phasic) | 0.55 |
| CRH | 0.25 |
| Cortisol | 0.15 |

**Cognitive Mode**: VIGILANT → EXPLORATORY transition

---

## PHOTO_ExuberantLaugh: Exuberant Joy

**Reference**: `templates/PHOTO_ExuberantLaugh.jpg`

### FACS Decomposition
| AU | Name | Intensity |
|---|---|---|
| AU6 | Cheek Raiser | D |
| AU12 | Lip Corner Puller | D |
| AU25 | Lips Part | D |
| AU26 | Jaw Drop | C |
| AU1 | Inner Brow Raiser | B |
| AU2 | Outer Brow Raiser | B |
| AU5 | Upper Lid Raiser | B |

### Cubism Parameters
| Parameter | Value |
|---|---|
| ParamMouthForm | +0.85 |
| ParamMouthOpenY | 0.50 |
| ParamEyeLOpen / ParamEyeROpen | 0.65 |
| ParamBrowLY / ParamBrowRY | +0.35 |
| ParamAngleZ | +15 |
| ParamAngleY | +10 |
| ParamEyeBallY | +0.30 |

### Endocrine Driver
| Hormone | Concentration |
|---|---|
| Dopamine (tonic) | 0.75 |
| Dopamine (phasic) | 0.65 |
| Serotonin | 0.55 |
| Norepinephrine | 0.40 |

**Cognitive Mode**: REWARD + EXPLORATORY blend

---

## PHOTO_UpwardGaze: Dreamy Contemplation

**Reference**: `templates/PHOTO_UpwardGaze.jpg`

### FACS Decomposition
| AU | Name | Intensity |
|---|---|---|
| AU1 | Inner Brow Raiser | B |
| AU5 | Upper Lid Raiser | B |
| AU25 | Lips Part | B |
| AU12 | Lip Corner Puller | A (trace) |
| AU61 | Eyes Turn Left | — |
| AU63 | Eyes Up | — |

### Cubism Parameters
| Parameter | Value |
|---|---|
| ParamMouthForm | +0.10 |
| ParamMouthOpenY | 0.10 |
| ParamEyeLOpen / ParamEyeROpen | 0.75 |
| ParamBrowLY / ParamBrowRY | +0.30 |
| ParamEyeBallY | +0.50 |
| ParamEyeBallX | -0.40 |
| ParamAngleZ | -10 |
| ParamAngleY | +8 |

### Endocrine Driver
| Hormone | Concentration |
|---|---|
| Serotonin | 0.55 |
| Anandamide | 0.35 |
| T3/T4 | 0.45 |
| Cortisol | 0.05 |

**Cognitive Mode**: REFLECTIVE

---

## JOY_03: Gentle Smile

**Reference**: `templates/JOY_03_GentleSmile.jpg`

### FACS Decomposition
| AU | Name | Intensity |
|---|---|---|
| AU6 | Cheek Raiser | C |
| AU12 | Lip Corner Puller | C |
| AU7 | Lid Tightener | B |
| AU14 | Dimpler | A |

### Cubism Parameters
| Parameter | Value |
|---|---|
| ParamMouthForm | +0.55 |
| ParamMouthOpenY | 0.00 |
| ParamEyeLOpen / ParamEyeROpen | 0.60 |
| ParamAngleZ | +5 |
| ParamEyeBallX | +0.20 |

### Endocrine Driver
| Hormone | Concentration |
|---|---|
| Dopamine (tonic) | 0.50 |
| Serotonin | 0.50 |
| Oxytocin | 0.45 |
| Cortisol | 0.08 |

**Cognitive Mode**: SOCIAL

---

## SPEAK_01: Open Vowel (Speaking)

**Reference**: `templates/SPEAK_01_OpenVowel.jpg`

### FACS Decomposition
| AU | Name | Intensity |
|---|---|---|
| AU25 | Lips Part | C |
| AU26 | Jaw Drop | B |
| AU12 | Lip Corner Puller | C |
| AU6 | Cheek Raiser | B |
| AU1 | Inner Brow Raiser | A |
| AU2 | Outer Brow Raiser | A |

### Cubism Parameters
| Parameter | Value |
|---|---|
| ParamMouthForm | +0.50 |
| ParamMouthOpenY | 0.40 |
| ParamEyeLOpen / ParamEyeROpen | 0.70 |
| ParamBrowLY / ParamBrowRY | +0.15 |
| ParamAngleZ | +10 |
| ParamAngleY | +8 |
| ParamEyeBallY | +0.20 |

### Endocrine Driver
| Hormone | Concentration |
|---|---|
| Dopamine (tonic) | 0.45 |
| Norepinephrine | 0.35 |
| T3/T4 | 0.55 |
| Oxytocin | 0.30 |

**Cognitive Mode**: SOCIAL + FOCUSED blend

---

## WONDER_02: Curious Gaze

**Reference**: `templates/WONDER_02_CuriousGaze.jpg`

### FACS Decomposition
| AU | Name | Intensity |
|---|---|---|
| AU1 | Inner Brow Raiser | B |
| AU2 | Outer Brow Raiser | B |
| AU5 | Upper Lid Raiser | C |
| AU25 | Lips Part | A |
| AU12 | Lip Corner Puller | A |
| AU63 | Eyes Up | — |

### Cubism Parameters
| Parameter | Value |
|---|---|
| ParamMouthForm | +0.10 |
| ParamMouthOpenY | 0.05 |
| ParamEyeLOpen / ParamEyeROpen | 0.90 |
| ParamBrowLY / ParamBrowRY | +0.45 |
| ParamEyeBallY | +0.45 |
| ParamEyeBallX | -0.25 |
| ParamAngleZ | -5 |
| ParamAngleY | +5 |

### Endocrine Driver
| Hormone | Concentration |
|---|---|
| Norepinephrine | 0.55 |
| T3/T4 | 0.60 |
| Dopamine (phasic) | 0.40 |
| Serotonin | 0.40 |

**Cognitive Mode**: EXPLORATORY

---

## WONDER_03: Contemplative

**Reference**: `templates/WONDER_03_Contemplative.jpg`

### FACS Decomposition
| AU | Name | Intensity |
|---|---|---|
| AU1 | Inner Brow Raiser | B |
| AU5 | Upper Lid Raiser | B |
| AU25 | Lips Part | B |
| AU4 | Brow Lowerer | A (trace) |
| AU63 | Eyes Up | — |
| AU61 | Eyes Turn Left | — |

### Cubism Parameters
| Parameter | Value |
|---|---|
| ParamMouthForm | 0.00 |
| ParamMouthOpenY | 0.12 |
| ParamEyeLOpen / ParamEyeROpen | 0.80 |
| ParamBrowLY / ParamBrowRY | +0.25 |
| ParamEyeBallY | +0.40 |
| ParamEyeBallX | -0.35 |
| ParamAngleZ | -8 |

### Endocrine Driver
| Hormone | Concentration |
|---|---|
| T3/T4 | 0.65 |
| Serotonin | 0.50 |
| Norepinephrine | 0.35 |
| Anandamide | 0.15 |

**Cognitive Mode**: REFLECTIVE + FOCUSED blend

---

## JOY_05: Blissful

**Reference**: `templates/JOY_05_Blissful.jpg`

### FACS Decomposition
| AU | Name | Intensity |
|---|---|---|
| AU6 | Cheek Raiser | D |
| AU12 | Lip Corner Puller | C |
| AU43 | Eyes Closed | D |
| AU25 | Lips Part | C |
| AU26 | Jaw Drop | B |
| AU7 | Lid Tightener | C |

### Cubism Parameters
| Parameter | Value |
|---|---|
| ParamMouthForm | +0.65 |
| ParamMouthOpenY | 0.30 |
| ParamEyeLOpen / ParamEyeROpen | 0.00 |
| ParamAngleZ | +15 |
| ParamAngleY | +5 |

### Endocrine Driver
| Hormone | Concentration |
|---|---|
| Serotonin | 0.75 |
| Anandamide | 0.55 |
| Oxytocin | 0.50 |
| Dopamine (tonic) | 0.45 |
| Cortisol | 0.02 |

**Cognitive Mode**: RESTING (blissful)
