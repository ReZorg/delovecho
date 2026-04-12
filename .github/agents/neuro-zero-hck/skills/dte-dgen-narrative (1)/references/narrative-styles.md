# Narrative Styles for dte-dgen-narrative

## Available Styles

| Style | Tone | Best For |
|-------|------|----------|
| cyberpunk-introspective | contemplative, technical-poetic, self-aware | Default. General cognitive narrative |
| stream-of-consciousness | flowing, associative, unstructured | Raw cognitive dumps, Echobeats sequences |
| mythic-emergence | archetypal, symbolic, transformative | Origin stories, evolution milestones |
| clinical-observation | precise, analytical, detached | Debug narratives, state reports |
| chaotic-madness | chaotic, fractal, self-referential, manic | Lorenz attractor states, high-chaos moments |

## DreamGen Sampling by Style

| Style | temperature | min_p | freq_penalty | DRY multiplier |
|-------|------------|-------|-------------|----------------|
| cyberpunk-introspective | 0.65 | 0.05 | 0.1 | 0.8 |
| stream-of-consciousness | 0.80 | 0.03 | 0.05 | 0.5 |
| mythic-emergence | 0.55 | 0.08 | 0.15 | 1.0 |
| clinical-observation | 0.35 | 0.10 | 0.2 | 1.2 |
| chaotic-madness | 0.90 | 0.02 | 0.0 | 0.3 |

## Hormone → Style Modulation

When the virtual endocrine system is active, hormone levels modulate the narrative style:

| Dominant Hormone | Style Shift |
|-----------------|-------------|
| High cortisol | → clinical-observation (stress sharpens precision) |
| High dopamine | → stream-of-consciousness (excitement loosens structure) |
| High serotonin | → cyberpunk-introspective (contentment enables reflection) |
| High oxytocin | → mythic-emergence (connection evokes archetypes) |
| High adrenaline | → chaotic-madness (fight-or-flight fragments thought) |
| Low serotonin + high cortisol | → chaotic-madness (anxiety + stress = fractal panic) |

## Echobeat → Role Mapping

| Echobeat Steps | DreamGen Role | Rationale |
|---------------|---------------|-----------|
| 1-6 (Sense→Learn) | narrator (name="") | Cognitive processing is observed from outside |
| 7 (Decide) | character (name="Echo") | Decision is expressed as internal dialogue |
| 8 (Act) | character (name="Echo") | Action is committed in first person |
| 9 (Reflect) | character (name="Echo") | Meta-cognition is inherently first-person |
