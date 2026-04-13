# Transformation Theory

## Table of Contents

1. [The Functor Model](#the-functor-model)
2. [Skill Decomposition](#skill-decomposition)
3. [Domain Morphisms](#domain-morphisms)
4. [Composition Laws](#composition-laws)
5. [Template Algebra](#template-algebra)

## The Functor Model

A skill transformation is a **functor** `F: Skill_A → Skill_B` that maps:
- **Structure** (invariant) — sections, workflow steps, script architecture, composition interface
- **Bindings** (variant) — domain terms, API endpoints, data formats, external services

The functor preserves structural relationships while replacing domain-specific content:

```
F(skill) = structure(skill) ⊕ new_bindings
```

Where `⊕` denotes the binding operation that fills parameterized slots with new domain values.

## Skill Decomposition

Every skill `S` decomposes into a pair `(T, B)`:

| Component | Symbol | Description | Example |
|-----------|--------|-------------|---------|
| Template | `T` | Invariant structure | Workflow: extract → validate → transform → load |
| Bindings | `B` | Domain-specific values | FNB, bank statement, PDF, transaction |

The decomposition satisfies: `S = T(B)` — applying bindings to template recovers the original skill.

### Binding Categories

| Category | What Changes | Example |
|----------|-------------|---------|
| **Terminology** | Domain nouns and verbs | "bank" → "exchange", "statement" → "report" |
| **APIs** | Endpoints and protocols | Graph API → REST API, SMTP → WebSocket |
| **Data Formats** | Input/output schemas | PDF → CSV, JSON → XML |
| **Services** | External integrations | Exchange Online → Gmail, Neon → Supabase |
| **Validation** | Business rules | Balance reconciliation → Hash verification |

## Domain Morphisms

A **domain morphism** `m: D_A → D_B` maps one domain's concepts to another's:

```
m(term_A) = term_B
m(api_A) = api_B
m(format_A) = format_B
```

### Morphism Quality

Not all morphisms are equal. A **good morphism** preserves semantic relationships:

```
If relation(a, b) in D_A, then relation(m(a), m(b)) in D_B
```

Example: If "transaction" is-part-of "statement" in banking, then "trade" should be-part-of "report" in the target domain.

### Morphism Types

| Type | Description | Fidelity |
|------|-------------|----------|
| **Isomorphism** | 1:1 mapping, fully reversible | Perfect |
| **Homomorphism** | Structure-preserving, may lose detail | High |
| **Analogy** | Approximate mapping, requires human review | Medium |
| **Metaphor** | Loose mapping, creative interpretation | Low |

For automated transformation, target **homomorphism** or better. For creative domain leaps, **analogy** is acceptable with human review.

## Composition Laws

Transformations compose:

```
F: Skill_A → Skill_B
G: Skill_B → Skill_C
G ∘ F: Skill_A → Skill_C
```

### Chain Composition

Sequential application of transformations:

```
chain([F₁, F₂, F₃])(S) = F₃(F₂(F₁(S)))
```

### Parallel Composition

Independent transformations from the same source:

```
fork([F₁, F₂, F₃])(S) = [F₁(S), F₂(S), F₃(S)]
```

This generates a **skill family** — a set of analogous skills across domains.

### Identity Law

The identity transformation preserves the skill unchanged:

```
id(S) = S
```

### Associativity

Chaining is associative:

```
(F ∘ G) ∘ H = F ∘ (G ∘ H)
```

## Template Algebra

Templates form an algebra under composition:

| Operation | Symbol | Description |
|-----------|--------|-------------|
| **Apply** | `T(B)` | Fill template with bindings → skill |
| **Compose** | `T₁ ∘ T₂` | Chain templates → pipeline template |
| **Fork** | `T ⊗ [B₁, B₂]` | One template, many bindings → skill family |
| **Merge** | `T₁ ⊕ T₂` | Combine template structures → hybrid template |
| **Refine** | `T ↑ ΔB` | Incrementally update bindings |

### The Template Fixed Point

Applying function-creator to itself:

```
FC = function-creator
FC(FC) = meta-function-creator  (transforms transformation skills)
FC(FC(FC)) → FC∞              (the transformation attractor)
```

At the fixed point, `FC∞` is a universal skill transformer that can map any skill to any domain.
