# Resonance Attributes: The ⊗ Operators

PHP 8 Attributes are the primary **multiplicative (⊗) binding mechanism** in Resonance. They declare how different components should be wired together by the `DependencyInjectionContainer`.

| Attribute | ⊗ Effect | Subsystem |
|---|---|---|
| `#[Singleton]` | Registers a class in the DI container. `__construct` injection performs `Class ⊗ Dependencies`. | DI |
| `#[Singleton(collection: X)]` | Adds a class to an additive collection, allowing for multiple implementations of an interface. | DI |
| `#[RespondsToHttp]` | Binds a controller/responder to a specific HTTP route and method. | HTTP |
| `#[RespondsToWebSocketJsonRPC]` | Binds a responder to a WebSocket JSON-RPC method. | WebSocket |
| `#[RespondsToPromptSubject]` | Binds a handler to a specific LLM-recognized user intent (action + subject). | AI/LLM |
| `#[ControlsWebSocketProtocol]` | Binds a controller to a WebSocket protocol, managing the connection lifecycle. | WebSocket |
| `#[ListensTo]` | Binds an event listener to a specific event class. | Events |
| `#[GraphQLRootField]` | Binds a resolver class to a root field (Query or Mutation) in the GraphQL schema. | GraphQL |
| `#[HandlesServerTask]` | Binds a handler to a specific server task type for background processing. | Async/Runtime |
| `#[ScheduledWithCron]` | Binds a `CronJobInterface` to a cron schedule. | Async/Runtime |
| `#[DecidesCrudAction]` | Binds a gate to a CRUD action on a subject, controlling authorization. | Auth/Security |
| `#[RequiresOAuth2Scope]` | Binds an OAuth2 scope requirement to a controller or method. | Auth/Security |
| `#[WantsFeature]` | Declares a dependency on a feature, performing `Container ⊗ Feature`. | DI |
| `#[GrantsFeature]` | Declares that a class provides a feature, enabling it for `#[WantsFeature]`. | DI |
| `#[SideEffect]` | Binds a provider to a feature, executing code when the feature is enabled. | DI |
