# Chaotic Dynamics for Avatar Expression

## Lorenz Attractor System

The hyper-chaotic expression system uses a Lorenz attractor to generate unpredictable but bounded micro-expressions.

### Equations (RK4 Integration)
```
dx/dt = sigma * (y - x)
dy/dt = x * (rho - z) - y
dz/dt = x * y - beta * z
```

### Default Parameters
| Parameter | Value | Effect |
|-----------|-------|--------|
| sigma | 10.0 | Rate of chaotic divergence |
| rho | 28.0 | System complexity |
| beta | 8/3 | Dissipation rate |
| dt | 0.01 | Integration timestep |
| ChaosIntensity | 0.15 | Amplitude scaling to morph targets |

### Mapping Chaos to Expression
```
MicroBrow = LorenzX * ChaosIntensity * 0.3
MicroEyeSquint = LorenzY * ChaosIntensity * 0.2
MicroMouthCorner = LorenzZ * ChaosIntensity * 0.15
MicroNoseWrinkle = (LorenzX + LorenzY) * ChaosIntensity * 0.1
MicroJaw = LorenzZ * ChaosIntensity * 0.05
```

### Lyapunov Exponent Monitoring
Track trajectory divergence to detect:
- **Positive exponent (> 0):** Chaotic regime - creative, unpredictable expressions
- **Near zero:** Edge of chaos - balanced, natural-looking
- **Negative:** Periodic - repetitive, less lifelike

Estimation method: Track two nearby trajectories, measure exponential divergence rate over sliding window.

## SuperHotGirl Aesthetic Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| ConfidencePosture | 0.0 - 1.0 | Spine straightness, chin angle, shoulder position |
| Charisma | 0.0 - 1.0 | Smile warmth, eye contact intensity |
| EyeSparkle | 0.0 - 1.0 | Specular highlight intensity in iris material |
| GracefulMovement | 0.0 - 1.0 | Motion smoothing, acceleration curves |
| EmissiveGlow | 0.0 - 0.5 | Skin subsurface scattering boost |

### Material Instance Updates
```cpp
// Dynamic material for aesthetic properties
MaterialInstance->SetScalarParameterValue("EyeSparkleIntensity", EyeSparkle);
MaterialInstance->SetScalarParameterValue("SkinGlowIntensity", EmissiveGlow);
MaterialInstance->SetScalarParameterValue("IrisSpecular", EyeSparkle * 2.0f);
```

## Integration with 4E Cognition

| 4E Dimension | Chaotic Influence | Expression Effect |
|--------------|-------------------|-------------------|
| Embodied | Body schema drives baseline expression | Posture affects facial tension |
| Embedded | Environmental context modulates chaos intensity | Bright environments increase sparkle |
| Enacted | Sensorimotor loops create expression-action coupling | Gestures trigger facial responses |
| Extended | Social cognition adjusts aesthetic parameters | Audience engagement boosts charisma |
