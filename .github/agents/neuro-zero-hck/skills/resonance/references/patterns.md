# Core Composition Patterns in Resonance

Resonance's architecture is built on a clear distinction between additive (⊕) and multiplicative (⊗) composition. Recognizing these patterns is key to using the framework effectively.

## Additive (⊕) Patterns: Choice & Alternatives

Use additive patterns when you need to provide alternatives, make a choice from a set of options, or have features that can exist independently of each other.

### Pattern 1: Feature Gating

*   **Mechanism**: `#[WantsFeature]` and `#[GrantsFeature]` attributes.
*   **Algebra**: `App = Core ⊗ (FeatureA ⊕ FeatureB ⊕ ...)`
*   **Use Case**: Enabling or disabling major parts of the framework. For example, you can build an application that is only a static site generator (`#[WantsFeature(Feature::StaticPages)]`) without loading the HTTP server, WebSockets, or Database subsystems.

### Pattern 2: Singleton Collections

*   **Mechanism**: `#[Singleton(collection: SingletonCollection::...)]` attribute.
*   **Algebra**: `Service = ImplementationA ⊕ ImplementationB ⊕ ...`
*   **Use Case**: Providing multiple implementations for a single interface, which are then injected as an array. For example, you can have multiple `HttpMiddlewareInterface` implementations in the `HttpMiddleware` collection, and they will all be processed.

### Pattern 3: Dialogue Responses

*   **Mechanism**: A `DialogueNode` holds a set of `DialogueResponseInterface` objects.
*   **Algebra**: `Node = MessageProducer ⊗ (ResponseA ⊕ ResponseB ⊕ CatchAll)`
*   **Use Case**: Defining the possible ways a user can reply at a certain point in a conversation. The system tries to match the user's input against each response in the additive set.

### Pattern 4: Constraint Alternatives

*   **Mechanism**: `AnyOfConstraint`.
*   **Algebra**: `Constraint = ConstraintA ⊕ ConstraintB`
*   **Use Case**: Validating input that can conform to one of several possible schemas. For example, a field could be either a string or an integer.

## Multiplicative (⊗) Patterns: Interaction & Pipelines

Use multiplicative patterns when components must interact in a specific sequence or when one component directly depends on another.

### Pattern 1: Constructor Injection

*   **Mechanism**: The DI container automatically resolving constructor parameters.
*   **Algebra**: `MyClass = DependencyA ⊗ DependencyB ⊗ ...`
*   **Use Case**: This is the most fundamental ⊗ pattern. A class is the multiplicative product of its dependencies. It cannot exist without them.

### Pattern 2: HTTP Request Pipeline

*   **Mechanism**: The flow of a request through the server.
*   **Algebra**: `FinalResponse = Router ⊗ Middleware ⊗ Controller ⊗ Interceptor ⊗ Responder`
*   **Use Case**: Handling an incoming HTTP request. Each stage in the pipeline takes the output of the previous one, transforms it, and passes it to the next, forming a multiplicative chain.

### Pattern 3: Attribute Stacking

*   **Mechanism**: Applying multiple attributes to a single class or method.
*   **Algebra**: `Component = BehaviorA ⊗ BehaviorB`
*   **Use Case**: A single class can be both a `#[Singleton]` and `#[ListensTo(MyEvent::class)]`. This means it is both a singleton in the container AND a listener for an event. The behaviors are multiplied.

### Pattern 4: LLM Processing Pipeline

*   **Mechanism**: The flow of generating a response from an LLM.
*   **Algebra**: `Completion = Client ⊗ Prompt ⊗ Grammar ⊗ Extractor`
*   **Use Case**: To get a structured response from an LLM, you must first connect to it (Client), send a formatted prompt (Prompt), optionally constrain its output (Grammar), and parse the result (Extractor). All steps are required and interact.
