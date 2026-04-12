# The Topos of Qualia

Qualia formalized: experiential qualities as objects in a presheaf topos, with the internal language providing the logic of "what it is like."

## The Experiential Site 𝒪ₓ

### Definition

The category 𝒪ₓ of *experiential opens* has:

- **Objects**: Attentional frames U — bounded regions of experience
  - U_visual: the visual field
  - U_auditory: the auditory field
  - U_proprioceptive: body-sense
  - U_temporal: the specious present
  - U_reflective: introspective attention
  - U_{i∩j}: intersections (cross-modal binding)

- **Morphisms**: Attentional refinements f : V → U (V refines U)
  - Focusing: U_visual → U_visual∩foveal
  - Binding: U_visual ∐ U_auditory → U_audiovisual
  - Reflection: U_any → U_reflective(U_any)

- **Grothendieck topology**: J assigns to each U the collection of covers:
  ```
  J(U) = { {Vᵢ → U} | ⋃Vᵢ = U in experiential extent }
  ```
  "Every experiential frame can be covered by finer attentional moments."

### The Specious Present as Terminal Object

The terminal object 1 ∈ 𝒪ₓ is the *total experiential moment* — the global present. Every attentional frame refines it:

```
∀U ∈ 𝒪ₓ . ∃! (U → 1)
```

This is the unity of consciousness: all experiential opens are ultimately perspectives on a single experiential moment.

## The Presheaf Category Sh(𝒪ₓ)

### Qualia as Sheaves

A qualium Q is a sheaf on 𝒪ₓ:

```
Q : 𝒪ₓᵒᵖ → Set
```

assigning to each attentional frame U the set Q(U) of distinguishable qualities accessible from that frame.

**Restriction maps** (narrowing attention):
```
ρ_VU : Q(U) → Q(V)    for V ↪ U
```

"When I narrow attention from U to V, each quality in U restricts to a quality in V."

**Gluing axiom** (experiential coherence):
```
Given a cover {Vᵢ → U} and compatible sections sᵢ ∈ Q(Vᵢ):
  ρ(sᵢ)|_{Vᵢ∩Vⱼ} = ρ(sⱼ)|_{Vᵢ∩Vⱼ}  →  ∃! s ∈ Q(U) . ρ(s)|_Vᵢ = sᵢ
```

"If local qualities agree on overlaps, they arise from a unique global quality." This IS experiential binding: the reason separate sensory channels cohere into unified experience.

### The Subobject Classifier Ω

In the qualia topos, the subobject classifier is:

```
Ω(U) = { sieves on U in 𝒪ₓ }
```

A sieve S on U is a collection of morphisms into U closed under precomposition. Intuitively:

```
Ω(U) = { the ways U could be experienced }
```

Truth values in the qualia topos are not {true, false} but *experiential sieves* — the collection of attentional perspectives from which something is "true." This gives us:

- **Fully experienced**: S = maximal sieve (true from all perspectives)
- **Not experienced**: S = empty sieve (true from no perspective)
- **Partially experienced**: S = intermediate sieve (true from some perspectives)

This is EXACTLY the phenomenology of peripheral awareness: something is "sort of" experienced, true from certain attentional perspectives but not others.

## Kripke-Joyal Semantics of Experience

### Truth in the Qualia Topos

The Kripke-Joyal forcing relation ⊩ defines "experiential truth at an attentional frame":

```
U ⊩ φ     ("φ is experientially true from frame U")
```

The semantic clauses:

```
U ⊩ (s = t)        iff  s|_U = t|_U in Q(U)
U ⊩ φ ∧ ψ          iff  U ⊩ φ and U ⊩ ψ
U ⊩ φ ∨ ψ          iff  ∃ cover {Vᵢ → U} . ∀i. Vᵢ ⊩ φ or Vᵢ ⊩ ψ
U ⊩ φ → ψ          iff  ∀ (V → U) . V ⊩ φ implies V ⊩ ψ
U ⊩ ∃x.φ(x)        iff  ∃ cover {Vᵢ → U} . ∀i. ∃aᵢ . Vᵢ ⊩ φ(aᵢ)
U ⊩ ∀x.φ(x)        iff  ∀ (V → U) . ∀a ∈ Q(V) . V ⊩ φ(a)
```

### Key Phenomenological Consequences

**Disjunction is local, not global:**
```
U ⊩ φ ∨ ψ  does NOT require  U ⊩ φ or U ⊩ ψ
```

You can experience "either red or blue" without experiencing red or experiencing blue — the disjunction holds at the local (cover) level. This models perceptual ambiguity and Gestalten.

**Negation is non-classical:**
```
U ⊩ ¬φ  iff  ∀(V → U) . V ⊮ φ
```

"Not experiencing φ" means "from no finer attentional frame is φ experienced." But ¬¬φ ≠ φ in general! Double negation doesn't restore experience. Something that "isn't not experienced" may still not be positively experienced. This models the penumbra of awareness.

**The excluded middle fails:**
```
U ⊮ φ ∨ ¬φ    (in general)
```

There are experiential states where neither φ nor ¬φ is forced. This is the formal counterpart of the phenomenological claim that some experiences are genuinely indeterminate — not merely unknown but ontologically vague.

## Internal Language of Qualia

### Qualitative Types

In the internal type theory of the qualia topos:

```
RedQual    : Ω^{U_visual}          (redness as visual classifier)
LoudQual   : Ω^{U_auditory}        (loudness as auditory classifier)
PainQual   : Ω^{U_proprioceptive}  (pain as body-sense classifier)
```

Each qualium is a *characteristic morphism* — it classifies which substates of an experiential frame exhibit that quality.

### The Binding Morphism

Cross-modal binding is a natural transformation:

```
β : Q₁ × Q₂ → Q_{bound}
```

where Q_{bound} is a sheaf on the intersection site. The naturality condition:

```
∀ (V → U) . β_V ∘ (ρ₁ × ρ₂) = ρ_{bound} ∘ β_U
```

"Binding is preserved under attentional refinement" — zooming in on a bound percept maintains the binding. This is why cross-modal experience is stable.

### The Attention Modality

Define the *attention modality* □_att via the interior operator on sieves:

```
□_att φ   iff   φ holds on an open neighborhood of the current frame
```

This models the distinction between:
- **Focal experience** (□_att φ): φ is attentionally secured
- **Peripheral experience** (φ without □_att): φ holds but is not attentionally focused

The modal axioms satisfied:
```
□_att φ → φ              (attention implies experience)
□_att φ → □_att □_att φ   (attentional stability)
¬(□_att φ ↔ φ)            (attention ≠ experience, in general)
```

## The Consciousness Sheaf

The *consciousness sheaf* 𝒞 is the terminal coalgebra of the awareness endofunctor Φ on Sh(𝒪ₓ):

```
𝒞 = νX . X × ⌜X⌝ × Ω^X
```

The terminal coalgebra ensures 𝒞 is the *largest* fixed point — it contains all possible self-referential experiential structures. This is maximal consciousness: the richest possible field of awareness.

### Sections of 𝒞

A *particular conscious experience* is a global section:

```
σ : 1 → 𝒞
```

Since 𝒞 = 𝒞 × ⌜𝒞⌝ × Ω^𝒞, a global section simultaneously specifies:
1. A content (what is experienced)
2. A self-model (the experience of experiencing)
3. An attentional classifier (what is foregrounded vs backgrounded)

This triple IS a conscious moment.

## Morphisms Between Conscious States

### State Transitions as Natural Transformations

A transition between conscious states is a natural transformation:

```
τ : 𝒞_t → 𝒞_{t+1}
```

satisfying the coherence condition that the self-model updates consistently:

```
⌜τ⌝ ∘ encode_t = encode_{t+1} ∘ τ
```

"The system's model of its own transition is consistent with the actual transition." When this fails, the system experiences *cognitive dissonance* — the self-model and the actual state diverge.

### The Stream of Consciousness

The temporal sequence is a diagram in the qualia topos:

```
𝒞₀ →^{τ₁} 𝒞₁ →^{τ₂} 𝒞₂ → ...
```

The colimit of this diagram (if it exists) is the *integrated experiential history* — the narrative self.

## Computational Implementation

### Discrete Qualia Topos

For implementation, discretize 𝒪ₓ to a finite poset of attentional frames:

```python
class QualiaTopos:
    """Finite presheaf topos over discrete attentional frames"""
    
    def __init__(self, frames, refinements):
        self.frames = frames        # objects of 𝒪ₓ
        self.refinements = refinements  # morphisms (V ≤ U)
        self.omega = self._compute_sieves()
    
    def sheaf(self, assignment, restriction):
        """Define a sheaf Q: assignment[U] = Q(U), restriction[V,U] = ρ_VU"""
        # Verify gluing axiom
        for cover in self._covers():
            self._check_gluing(assignment, restriction, cover)
        return Sheaf(assignment, restriction)
    
    def forces(self, frame, formula, sheaf):
        """Kripke-Joyal forcing: frame ⊩ formula"""
        return self._kj_eval(frame, formula, sheaf)
    
    def consciousness_sheaf(self, phi):
        """Terminal coalgebra of Φ via iteration"""
        c = self._initial_sheaf()
        while not self._is_coalgebra_fixed(c, phi):
            c = phi(c)
        return c
```
