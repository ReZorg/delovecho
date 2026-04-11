The wizardman skill has been evolved from R&D to R⊕D⊗E. Here is what changed:
New algebraic layer: Every model now has a quadruple instead of a triple — (Matula, parens, differential, ⊕⊗ algebra). The conversion rules are exactly as you specified:
(1)(2) → 1 ⊕ 1 — siblings are additive (choice/independence)
((1)2) → 1 ⊗ 1 — nesting is multiplicative (pipeline/dependency)
The topology ↔ algebra correspondence is clean:
Topology
Algebra
Example (s3)
NEST
Pure ⊗
1⊗1⊗1⊗1 (Matula 5)
BRANCH
Pure ⊕
1⊕1⊕1 (Matula 8)
BRIDGE
Mixed
1⊗(1⊕1) (Matula 7) or (1⊗1)⊕1 (Matula 6)
R⊕D⊗E framework: ( /development ⊗ /evolution ) ⊕ /research — the ⊗ maps development phases onto evolution steps as a pipeline, while ⊕ inserts research sub-loops at any measurable checkpoint. Distributivity governs the interaction: R ⊗ (D₁ ⊕ D₂) ≅ (R⊗D₁) ⊕ (R⊗D₂).
Model composition now uses ⊕⊗ explicitly: FADA ⊗ FFDA (pipeline), FFA ⊕ FTSA (choice), R ⊕ (FDIA ⊗ FFA ⊗ FPOA) (research loop around a pipeline).
New script: scripts/paren_to_algebra.py converts any parenthesis notation to ⊕⊗ algebra.