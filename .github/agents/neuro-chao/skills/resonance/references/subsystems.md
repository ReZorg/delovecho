# Resonance Subsystem Decompositions (⊕⊗)

This document provides a detailed algebraic breakdown of Resonance's 10 major subsystems.

## 1. HTTP Subsystem

**Structure**: Multiplicative Pipeline (⊗)

`HTTP_Response = Router ⊗ Middleware ⊗ Controller ⊗ Interceptor ⊗ Responder`

- **Router**: Selects the correct controller based on the request URL.
- **Middleware**: A ⊗-chain of processors that can act on the request before it hits the controller.
- **Controller**: The main logic unit, produces a preliminary response.
- **Interceptor**: A ⊗-chain of processors that can act on the response from the controller.
- **Responder**: Serializes the final response into the correct format (HTML, JSON, etc.).

## 2. AI / LLM Subsystem

**Structure**: Hybrid Polynomial-Tensorial

`LLM_Output = LlamaCppClient ⊗ LlmPrompt ⊗ LlmPersona ⊗ (BNFGrammar ⊕ Extractor)`

- **LlamaCppClient**: The ⊗ base, handling communication with the `llama.cpp` server.
- **LlmPrompt**: Multiplicatively shapes the input.
- **LlmPersona**: Multiplicatively sets the tone and style.
- **(BNFGrammar ⊕ Extractor)**: An additive choice. You can either constrain the output with a `BNFGrammar` (a formal grammar) OR parse the freeform output with an `Extractor`. You typically use one or the other.

## 3. Dialogue Subsystem

**Structure**: Polynomial of Tensors

`DialogueTurn = DialogueNode ⊗ (ResponseA ⊕ ResponseB ⊕ ...)`

- **DialogueNode**: The multiplicative context for a turn in the conversation.
- **(ResponseA ⊕ ...)**: An additive set of potential user responses. The system iterates through this set to find a match. Each response is itself a tensor (`Matcher ⊗ FollowUp`).

## 4. WebSocket Subsystem

**Structure**: Multiplicative Pipeline (⊗)

`WebSocket_Message = ProtocolController ⊗ JsonRPCResponder ⊗ AuthResolution ⊗ Connection`

- **ProtocolController**: Manages the lifecycle and message format (e.g., JSON-RPC).
- **JsonRPCResponder**: Handles a specific method call within the protocol.
- **AuthResolution**: Determines the authenticated user for the connection.
- **Connection**: The underlying Swoole WebSocket connection.

## 5. Database Subsystem

**Structure**: Additive Choice of Multiplicative Stacks (⊕ of ⊗)

`Database = (Doctrine ⊗ EntityManager ⊗ Migrations) ⊕ (SwoolePool ⊗ PreparedStatement)`

- You choose (⊕) between two primary strategies: the full Doctrine ORM stack or the lightweight Swoole connection pool with prepared statements.
- Each strategy is an internal multiplicative (⊗) stack.

## 6. Auth/Security Subsystem

**Structure**: Hybrid Polynomial-Tensorial

`Auth = (Session ⊗ Cookie ⊗ CSRF) ⊕ (OAuth2 ⊗ Grant ⊗ Scope ⊗ Client)`

- A choice (⊕) between session-based authentication and OAuth2.
- Session auth is a multiplicative (⊗) combination of session management, cookies, and CSRF protection.
- OAuth2 is a multiplicative (⊗) combination of grants, scopes, and clients.

## 7. Async/Runtime Subsystem

**Structure**: Multiplicative Core with Additive Tasks

`Runtime = (SwooleServer ⊗ CoroutineEngine) ⊗ (CronJob ⊕ TickTimerJob ⊕ ServerTask ⊕ SwooleFuture)`

- The core Swoole server and coroutine engine are the multiplicative (⊗) foundation.
- This core runs an additive (⊕) set of different asynchronous task types: scheduled jobs, background tasks, and promises.

## 8. Templating/SSG Subsystem

**Structure**: Multiplicative Pipeline (⊗)

`StaticSite = MarkdownParser ⊗ TwigRenderer ⊗ Layout ⊗ Esbuild`

- **MarkdownParser**: Parses content from `.md` files.
- **TwigRenderer**: Renders the parsed content within Twig templates.
- **Layout**: The selected layout template provides the overall structure.
- **Esbuild**: Bundles and minifies CSS/JS assets.

## 9. gRPC Subsystem

**Structure**: Multiplicative Pipeline (⊗)

`gRPC_Call = Protoc ⊗ GrpcClient ⊗ PHPPlugin`

- **Protoc**: The protocol buffer compiler generates the PHP client stubs from `.proto` files.
- **GrpcClient**: The generated client used to make calls.
- **PHPPlugin**: The gRPC PHP extension that handles the low-level communication.

## 10. Validation Subsystem

**Structure**: Additive set of Multiplicative Constraints

`ValidationResult = (ConstraintA ⊕ ConstraintB ⊕ AnyOfConstraint(C ⊕ D) ...)`

- A validation schema is an additive (⊕) set of individual constraints.
- Each constraint is a multiplicative (⊗) combination of rules (e.g., `StringConstraint` is `type:string ⊗ minLength ⊗ maxLength`).
- The `AnyOfConstraint` explicitly introduces an additive choice within the structure.
