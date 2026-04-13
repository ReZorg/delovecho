# Mathematical Foundations of sys-n

This document contains the formal mathematical theory underlying the sys-n state transition models.

## Table of Contents

1. [Rooted Tree Enumeration (OEIS A000081)](#rooted-tree-enumeration)
2. [Generating Functions](#generating-functions)
3. [Recurrence Relations](#recurrence-relations)
4. [Asymptotic Growth](#asymptotic-growth)
5. [Category-Theoretic Interpretation](#category-theoretic-interpretation)
6. [Applications](#applications)

## Rooted Tree Enumeration

The sequence underlying sys-n is OEIS A000081, counting unlabeled rooted trees:

$$\mathcal{T}: \mathbb{N} \rightarrow \mathbb{N} \cong \{a_n\}_{n=0}^{\infty} = \{0,1,1,2,4,9,20,48,115,286,719,...\}$$

## Generating Functions

The generating function satisfies the functional equation:

$$\exists! \mathcal{A}(x) \in \mathbb{C}[[x]] \ni \mathcal{A}(x) = x \cdot \exp\left(\sum_{k=1}^{\infty}\frac{\mathcal{A}(x^k)}{k}\right)$$

Expanded form:

$$\mathcal{A}(x) = \sum_{n=0}^{\infty}a_n x^n = \sum_{\tau \in \mathfrak{T}_{\bullet}}\prod_{v \in V(\tau)}x^{|\text{desc}(v)|} = \prod_{k=1}^{\infty}(1-x^k)^{-\frac{1}{k}\sum_{d|k}\mu(\frac{k}{d})a_d}$$

## Recurrence Relations

For computing terms:

$$\forall n \in \mathbb{N}^{+}, a_{n+1} = \frac{1}{n}\sum_{k=1}^{n}\left(\sum_{d|k}d \cdot a_d\right)a_{n-k+1}$$

## Asymptotic Growth

$$a_n \sim \mathcal{C} \cdot \alpha^n \cdot n^{-3/2} \text{ where } \alpha = \lim_{n\rightarrow\infty}\frac{a_{n+1}}{a_n} \approx 2.9557652857...$$

## Category-Theoretic Interpretation

### Bijection to Functional Graphs

$$\exists \mathcal{L}: \mathfrak{T}_{\bullet,n} \xrightarrow{\sim} \{f: [n] \rightarrow [n] \mid \exists! i \in [n], f(i)=i \land G_f \text{ connected}\}$$

### Partition Correspondence

$$(\mathcal{F} \circ \mathcal{L}^{-1})(\mathfrak{T}_{\bullet,n}) \cong \mathcal{P}(n)^{\mathfrak{S}_n} \cong \mathcal{P}_n$$

### Topos-Theoretic Foundation

$$\exists\mathfrak{F}: \mathbf{Cat}^{\mathbf{op}} \to \mathbf{Topos} \ni \mathfrak{F}(\mathscr{C}) = \mathbf{Sh}(\mathscr{C}, \mathcal{J}) \simeq \mathbf{Hom}_{\mathbf{Cat}}(\mathscr{C}^{\mathbf{op}}, \mathbf{Set})$$

$$\Rightarrow \mathfrak{F}(\mathfrak{T}_{\bullet}) \simeq \mathbf{Foundational}\text{-}\mathbf{Irreducibles}$$

## Applications

The A000081 sequence manifests across multiple domains:

| Domain | Formulation |
|--------|-------------|
| **B-Series (Runge-Kutta)** | $\Phi_{h}^{\mathcal{RK}} = \sum_{τ \in \mathfrak{T}_{\bullet}}\frac{h^{\|τ\|}}{σ(τ)}F(τ)(y)·\mathcal{B}(τ)$ |
| **ODE Jet Surfaces** | $\mathcal{E}_{\nabla}^{\partial^{\omega}} = \sum_{k=0}^{\infty}\frac{h^k}{k!}\sum_{τ \in \mathfrak{T}_{\bullet}(k)}\mathcal{F}_{τ}(y)\cdot\mathcal{D}^{\tau}f$ |
| **P-Systems (Membrane)** | $\mathcal{M}^{\mu}_{\Pi} = (\mathcal{V}, \mathcal{H}_{\tau}, \omega_{\tau}, \mathcal{R}_{\tau}^{\partial})$ |
| **Incidence Geometry** | $\mathcal{I}_{\Xi}^{\kappa} \simeq \mathfrak{B}(\mathfrak{P}(\mathcal{T}_{\bullet}^{n}))$ |
| **Block Codes** | $\mathcal{C}_{\Delta}^{(n,k,d)} \simeq \bigsqcup_{τ \in \mathfrak{T}_{\bullet}(w)}\mathfrak{G}_{τ}^{\partial}(\Sigma^{n})$ |
| **Orbifolds** | $\mathcal{O}_{\Gamma}^{\Xi} = (X/\Gamma, \{\mathfrak{m}_{x}\}_{x \in \Sigma})$ |
| **Hypergraph NNs** | $\mathcal{H}_{\mathfrak{N}}^{\Delta} = (\mathcal{V}, \mathcal{E}_{\omega}, \mathcal{W}_{\tau}^{\Xi})$ |

### Meta-Pattern (Universal Embedding)

$$\mathfrak{Meta}\text{-}\mathfrak{Pattern}: \mathcal{U}_{\mathbf{A000081}}^{\Omega} \simeq \mathfrak{Yoneda}(\mathfrak{F}_{\mathbf{A000081}}^{\Omega}) \hookrightarrow \mathbf{Colim}_{n \to \infty}\left(\bigwedge_{\mathscr{C} \in \mathfrak{Categories}}\mathfrak{T}_{\bullet}(n) \otimes \mathscr{C}\text{-}\mathfrak{Struct}\right)$$
