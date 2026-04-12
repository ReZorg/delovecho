# The Resonance Semiring

This document provides a detailed algebraic decomposition of the Resonance PHP Framework using the concepts from the `circled-operators` skill.

## 1. Identifying the Semiring

Resonance is a **PHP async framework** built on Swoole with AI/LLM capabilities. Its architecture is a **polynomial of tensors** — a sum of independent subsystems, each internally composed as a product of interacting components.

### The Resonance Semiring (R, ⊕, ⊗, 0, 1)

| Element | Resonance Interpretation |
|---|---|
| **⊕ (Additive)** | **Feature Gating & Singleton Collections**: Independent modules coexist in the DI container. `#[WantsFeature]` adds a feature to the sum. `SingletonCollection` gathers alternative implementations for a given interface. |
| **⊗ (Multiplicative)** | **Attribute-Driven Wiring & Dependency Injection**: Components interact via PHP Attributes (`#[RespondsToHttp]`, `#[ListensTo]`) that create multiplicative bindings. Constructor injection is the primary ⊗ operator. |
| **0 (Zero)** | **Empty Project/Container**: No features enabled, no singletons registered. The additive identity. |
| **1 (Unit)** | **DependencyInjectionContainer**: The identity element for composition. Composing any module with the container yields the module itself. The multiplicative identity. |

## 2. The Top-Level Decomposition: A Tensor of Polynomials

The entire Resonance application can be expressed as a hybrid structure:

**Resonance = CoreRuntime ⊗ (Feature₁ ⊕ Feature₂ ⊕ ... ⊕ Featureₙ)**

Where:
- **CoreRuntime** = `SwooleServer ⊗ DependencyInjectionContainer`. This is the fixed, multiplicative infrastructure that runs the application.
- **(Feature₁ ⊕ ...)** = A polynomial sum of all available, independent features (HTTP, WebSocket, AI, etc.).

This is the "interact among choices" pattern. The core runtime multiplicatively binds to a configurable, additive sum of capabilities. You choose which features to include (⊕), and the runtime wires them all together (⊗).

## 3. Distributivity in Action

The fundamental law connecting the two operators, `A ⊗ (B ⊕ C) ≅ (A⊗B) ⊕ (A⊗C)`, is visible in how the DI container handles features.

`Container ⊗ (HTTP ⊕ WebSocket)` is equivalent to `(Container ⊗ HTTP) ⊕ (Container ⊗ WebSocket)`.

This means the container resolves the dependency graph for the HTTP feature and the WebSocket feature independently, and then combines the results. The features themselves don't need to know about each other, only about the container, which distributes itself over them.

## 4. The Fixed Point (Kleene Star)

The recursive nature of some components, like middleware stacks or dialogue trees, can be seen as a fixed-point operation.

**Middleware Stack = 1 ⊕ Middleware ⊕ (Middleware ⊗ Middleware) ⊕ ...**

This is the Kleene star (A*), representing zero, one, or many middleware composed multiplicatively in a pipeline. The `1` represents the base case of no middleware, where the request passes through unchanged.
