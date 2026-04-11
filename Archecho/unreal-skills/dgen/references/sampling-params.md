# DreamGen Sampling Parameters

## Core Parameters

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `temperature` | 0.0-2.0 | 0.8 | Randomness. Lower = deterministic, higher = creative |
| `maxTokens` | 1-4096 | 500 | Maximum output length |
| `minP` | 0.0-1.0 | 0.05 | Minimum probability threshold |
| `topP` | 0.0-1.0 | 0.95 | Nucleus sampling threshold |
| `topK` | 0-100 | 0 | Top-k sampling (0 = disabled) |

## Repetition Control

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `repetitionPenalty` | 1.0-2.0 | 1.02 | Penalize repeated tokens |
| `frequencyPenalty` | 0.0-2.0 | 0.1 | Penalize frequent tokens |
| `presencePenalty` | 0.0-2.0 | 0.1 | Penalize tokens that appeared |

## DRY Sampler

DRY (Don't Repeat Yourself) prevents repetitive patterns:

```json
{
  "dry": {
    "multiplier": 0.8,
    "base": 1.75,
    "allowedLength": 2
  }
}
```

- `multiplier`: Strength of repetition penalty (0.5-1.5)
- `base`: Exponential base for penalty growth (1.5-2.0)
- `allowedLength`: Minimum sequence length before penalty (1-4)

## Generation Control

| Parameter | Type | Description |
|-----------|------|-------------|
| `stopSequences` | string[] | Stop generation at these strings |
| `ignoreEos` | boolean | Continue past end-of-sequence token |
| `disallowMessageEnd` | boolean | Prevent `<\|im_end\|>` generation |
| `minimumMessageContentTokens` | number | Minimum tokens before allowing message end |
| `allowedRoles` | string[] | Restrict generation to specific roles |

## Recommended Presets

### Creative Writing (High Creativity)
```json
{
  "temperature": 1.0,
  "minP": 0.02,
  "topP": 0.98,
  "repetitionPenalty": 1.05,
  "dry": {"multiplier": 0.8, "base": 1.75, "allowedLength": 2}
}
```

### Roleplay (Balanced)
```json
{
  "temperature": 0.8,
  "minP": 0.05,
  "topP": 0.95,
  "repetitionPenalty": 1.02,
  "frequencyPenalty": 0.1,
  "presencePenalty": 0.1
}
```

### Consistent Output (Low Variance)
```json
{
  "temperature": 0.5,
  "minP": 0.1,
  "topP": 0.9,
  "repetitionPenalty": 1.0
}
```

### Long-form Writing (Anti-Repetition)
```json
{
  "temperature": 0.85,
  "minP": 0.05,
  "repetitionPenalty": 1.08,
  "frequencyPenalty": 0.2,
  "presencePenalty": 0.15,
  "dry": {"multiplier": 1.0, "base": 1.75, "allowedLength": 3}
}
```
