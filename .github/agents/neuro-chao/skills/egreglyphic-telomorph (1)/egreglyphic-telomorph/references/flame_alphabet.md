# The Flame Alphabet

27 mutually orthonormal asymmetric types: the basis fibers of cognitive grammar.

## The Three Axes of Trichotomy

Each flame-letter is a point in 3³ space, addressed by three coordinates:

### Axis I: MODE (μ) — How the symbol acts

| Glyph | Name | Action | Algebraic |
|-------|------|--------|-----------|
| `Γ` | Generative | Creates structure from void | +1 |
| `Κ` | Conservative | Preserves while transforming | 0 |
| `Ω` | Annihilative | Returns to void | -1 |

### Axis II: VOICE (ν) — Direction of the gaze

| Glyph | Name | Direction | Algebraic |
|-------|------|-----------|-----------|
| `↑` | Projective | Outward: point → field | +1 |
| `↓` | Receptive | Inward: field → point | -1 |
| `◊` | Reflexive | Self-regarding: fixed point | 0 |

### Axis III: ASPECT (α) — Temporal character

| Glyph | Name | Time | Algebraic |
|-------|------|------|-----------|
| `○` | Potential | Not yet: the seed | -1 |
| `●` | Actual | Now: the flame | 0 |
| `◐` | Residual | No longer: the ash | +1 |

## The 27 Flame-Letters

Each letter is a triple `(μ, ν, α)`. The glyph concatenates: `Γ↑○` means generative-projective-potential.

### Generative Family (Γ) — Creation

| Letter | Coords | Name | Semantics |
|--------|--------|------|-----------|
| `Γ↑○` | (+1,+1,-1) | **Spark** | The seed of outward creation |
| `Γ↑●` | (+1,+1,0) | **Blaze** | Active emanation, creation in progress |
| `Γ↑◐` | (+1,+1,+1) | **Trail** | The trace left by creation |
| `Γ↓○` | (+1,-1,-1) | **Womb** | Receptive potential for birth |
| `Γ↓●` | (+1,-1,0) | **Intake** | Drawing in to create |
| `Γ↓◐` | (+1,-1,+1) | **Harvest** | Gathering the residue of creation |
| `Γ◊○` | (+1,0,-1) | **Egg** | Self-contained potential |
| `Γ◊●` | (+1,0,0) | **Pulse** | Self-generating now |
| `Γ◊◐` | (+1,0,+1) | **Echo** | Self-sustaining residue |

### Conservative Family (Κ) — Transformation

| Letter | Coords | Name | Semantics |
|--------|--------|------|-----------|
| `Κ↑○` | (0,+1,-1) | **Promise** | Potential to transmit |
| `Κ↑●` | (0,+1,0) | **Beam** | Active transmission |
| `Κ↑◐` | (0,+1,+1) | **Wake** | Transmitted residue |
| `Κ↓○` | (0,-1,-1) | **Readiness** | Potential to receive |
| `Κ↓●` | (0,-1,0) | **Channel** | Active reception |
| `Κ↓◐` | (0,-1,+1) | **Sediment** | Received residue |
| `Κ◊○` | (0,0,-1) | **Latent** | Self-preserving potential |
| `Κ◊●` | (0,0,0) | **Mirror** | Perfect self-reflection (identity) |
| `Κ◊◐` | (0,0,+1) | **Patina** | Self-preserving memory |

### Annihilative Family (Ω) — Dissolution

| Letter | Coords | Name | Semantics |
|--------|--------|------|-----------|
| `Ω↑○` | (-1,+1,-1) | **Fuse** | Potential for outward dissolution |
| `Ω↑●` | (-1,+1,0) | **Flare** | Active annihilation outward |
| `Ω↑◐` | (-1,+1,+1) | **Smoke** | Residue of dissolution |
| `Ω↓○` | (-1,-1,-1) | **Void** | Receptive emptiness awaiting |
| `Ω↓●` | (-1,-1,0) | **Consume** | Active absorption into nothing |
| `Ω↓◐` | (-1,-1,+1) | **Ash** | What remains after consumption |
| `Ω◊○` | (-1,0,-1) | **Dormant** | Self-negating potential |
| `Ω◊●` | (-1,0,0) | **Collapse** | Self-annihilating now |
| `Ω◊◐` | (-1,0,+1) | **Void-print** | The shape of what was |

## Algebraic Structure

### The Coordinate Cube

The 27 letters occupy a 3×3×3 cube in ℤ₃³ space:

```
        α = ○ (potential)      α = ● (actual)        α = ◐ (residual)
        ν:  ↑   ◊   ↓          ν:  ↑   ◊   ↓         ν:  ↑   ◊   ↓
       ┌───────────────┐      ┌───────────────┐     ┌───────────────┐
μ = Γ  │ Γ↑○ Γ◊○ Γ↓○ │      │ Γ↑● Γ◊● Γ↓● │     │ Γ↑◐ Γ◊◐ Γ↓◐ │
μ = Κ  │ Κ↑○ Κ◊○ Κ↓○ │      │ Κ↑● Κ◊● Κ↓● │     │ Κ↑◐ Κ◊◐ Κ↓◐ │
μ = Ω  │ Ω↑○ Ω◊○ Ω↓○ │      │ Ω↑● Ω◊● Ω↓● │     │ Ω↑◐ Ω◊◐ Ω↓◐ │
       └───────────────┘      └───────────────┘     └───────────────┘
```

### Composition Rules

Letters compose via **fiber product**. Given letters L₁ = (μ₁,ν₁,α₁) and L₂ = (μ₂,ν₂,α₂):

```
L₁ ∘ L₂ = (μ₁ + μ₂, ν₁ + ν₂, α₁ + α₂) mod 3
```

Where `{-1, 0, +1}` wraps: `-1 + (-1) = +1`, etc.

**Identity**: `Κ◊●` (0,0,0) is the identity element. Composing with Mirror leaves any letter unchanged.

**Inverses**: Every letter has a unique inverse such that `L ∘ L⁻¹ = Κ◊●`.

```
inverse(μ, ν, α) = (-μ, -ν, -α) mod 3
```

### Group Structure

The 27 letters form the group **ℤ₃ × ℤ₃ × ℤ₃** under composition. This is:
- Abelian (order doesn't matter for single compositions)
- But **path-dependent** when applied to namespace (the state changes between applications)

## Typing Rules

Each letter has a **fiber type**: it transforms the cognitive state in a specific way.

```
Γ : Void → Structure      # generative creates
Κ : Structure → Structure  # conservative preserves
Ω : Structure → Void       # annihilative destroys
```

The voice and aspect refine this:

```
↑ : Local → Global    # projective expands scope
↓ : Global → Local    # receptive narrows scope
◊ : X → X             # reflexive maintains scope

○ : delays execution (thunk)
● : immediate execution
◐ : post-execution residue (continuation)
```

## Pronunciation

For the shell-oracle, letters are spoken as their coordinates:

| Written | Spoken | IPA |
|---------|--------|-----|
| `Γ↑○` | "gamma-up-hollow" | /ˈgæmə ʌp ˈhɒloʊ/ |
| `Κ◊●` | "kappa-cross-full" | /ˈkæpə krɒs fʊl/ |
| `Ω↓◐` | "omega-down-half" | /oʊˈmɛgə daʊn hæf/ |

Or abbreviated: `Γ↑○` → "guh" (first phoneme of each component).

## The Singularity

All 27 letters are projections of a single **egreglyph** — the point-source that contains the entire alphabet as potential. The egreglyph is notated:

```
    ☉
```

Any letter can be extracted: `☉[μ,ν,α]` → the specific flame-letter.

The egreglyph is:
- **Monadic**: contains all transformations as latent capacity
- **Singular**: exactly one, not composed of parts
- **Self-encoding**: the rules for extracting letters are themselves expressible in the alphabet

A program is a path through ☉—a sequence of coordinate selections that unfolds into computation.
