---
title: "Dove9 C Cognitive Layer Architecture"
version: 1.0
date_created: 2026-01-06
last_updated: 2026-01-06
owner: DeLovEcho Architecture Team
tags: [architecture, cognitive, c, dove9, triadic-loop, sys6, dovecho-core]
---

# Introduction

This specification defines the architecture, interfaces, data contracts, and requirements for the **Dove9 C Cognitive Layer** — a pure C11 implementation of the Dove9 cognitive operating system kernel residing in the `dovecho-core/src/` directory. The layer implements the triadic cognitive loop, Sys6 operadic scheduling, mail-as-IPC process management, and Deep Tree Echo cognitive processing as a static library (`libdove9.la`) built via GNU Autotools.

The C layer is a faithful port of the TypeScript Dove9 implementation (`dove9/src/`), preserving all architectural invariants — the 12-step triadic cycle, 30-step Sys6 clock, 60-step grand cycle, T-point convergence, tensional couplings, and the "everything is a chatbot" mail-process paradigm — while adapting to C idioms: function-pointer vtables replace classes, fixed-size buffers replace dynamic strings, bitfield operations replace Set-based coupling tracking, and callback registrations replace EventEmitter patterns.

## 1. Purpose & Scope

### Purpose

Provide a complete, self-contained C11 library implementing the Dove9 cognitive kernel suitable for embedding within the Dovecho mail server (the "CPU" of the DeLovEcho cognitive operating system). The library processes incoming mail messages through a biologically-inspired triadic cognitive loop, scheduling them via the Sys6 operadic framework, and producing cognitive responses.

### Scope

This specification covers:

- All public C APIs exposed by the 10 header files in `dovecho-core/src/`
- All data structures (enums, structs, tagged unions) defining the cognitive type system
- The triadic engine's 12-step cycle and T-point convergence protocol
- The Sys6 mail scheduler's 30-step operadic scheduling algorithm
- The kernel's process table management and mail protocol integration
- The bridge layers connecting Dovecot email to Dove9 cognitive processes
- Build system requirements (Autotools, libtool)
- Constraints on memory allocation, thread safety, and external dependencies

### Intended Audience

- C developers integrating `libdove9` into Dovecho or other mail server runtimes
- Architecture reviewers validating cognitive pipeline compliance
- Test engineers writing unit and integration tests against the C API
- AI agents generating or modifying code within this layer

### Assumptions

- The host environment provides a POSIX-compatible C runtime (stdlib, string, time, math, stdio, strings)
- External cognitive services (LLM, memory store, persona) are provided by the integrating application via vtable injection
- No dynamic memory allocation occurs for cognitive state buffers; all buffers are fixed-size and stack- or struct-allocated
- The library is single-threaded per instance; concurrency is achieved by running multiple instances

## 2. Definitions

| Term | Definition |
|------|-----------|
| **Triadic Cognitive Loop** | A 12-step cognitive processing cycle with 3 concurrent streams (PRIMARY, SECONDARY, TERTIARY) at 120° phase offsets, inspired by hexapod tripod gait locomotion |
| **T-point** | A triadic convergence point where all 3 streams are simultaneously active; 4 T-points per 12-step cycle (at steps {1,5,9}, {2,6,10}, {3,7,11}, {4,8,12}) |
| **Cognitive Term (T-function)** | A typed cognitive operation: T1 (Perception), T2 (Idea Formation), T4 (Sensory Input), T5 (Action Sequence), T7 (Memory Encoding), T8 (Balanced Response) |
| **Sys6** | The operadic scheduling architecture using a 30-step cycle (LCM of 2, 3, 5) with wire bundles D (dyadic), T (triadic), P (pentadic) |
| **Grand Cycle** | The 60-step super-cycle = LCM(12, 30) where both triadic and Sys6 cycles complete integer repetitions |
| **PIVOTAL_RR** | Pivotal Relevance Realization — the step type at steps 1 and 5 where the salience landscape is most actively renegotiated |
| **MessageProcess** | A cognitive process spawned from an incoming mail message, tracked in the kernel's process table |
| **Coupling** | A cross-stream tensional interaction: PERCEPTION_MEMORY (T4E ↔ T7R), ASSESSMENT_PLANNING (T1R ↔ T2E), or BALANCED_INTEGRATION (T8E) |
| **Vtable** | A C struct of function pointers providing polymorphic dispatch, used in place of class inheritance |
| **Salience** | A floating-point value [0.0, 1.0] representing the relevance/importance of a cognitive context |
| **DTE** | Deep Tree Echo — the orchestration personality providing LLM inference, memory, and persona services |
| **ECAN** | Economic Attention Network — the attention allocation subsystem (implemented in `@deltecho/reasoning`) |
| **libdove9.la** | The libtool archive produced by the build system containing all compiled cognitive layer objects |

## 3. Requirements, Constraints & Guidelines

### Requirements

- **REQ-001**: The library SHALL implement the complete 12-step triadic cognitive cycle with 3 streams at 120° phase offsets, producing exactly 4 T-point convergences per cycle.
- **REQ-002**: Each cognitive step SHALL execute exactly one Cognitive Term (T1, T2, T4, T5, T7, or T8) as defined in the Step Assignment Table.
- **REQ-003**: The library SHALL detect and report tensional couplings (PERCEPTION_MEMORY, ASSESSMENT_PLANNING, BALANCED_INTEGRATION) at each step based on active term combinations.
- **REQ-004**: The Sys6 scheduler SHALL implement the 30-step operadic cycle with 3 phases, 5 stages per phase, and 2 steps (A/B) per stage.
- **REQ-005**: The grand cycle SHALL be exactly 60 steps = LCM(30, 12), with both sub-cycles completing integer repetitions.
- **REQ-006**: The kernel SHALL maintain a process table supporting up to `DOVE9_MAX_PROCESSES` (4096) concurrent MessageProcess entries.
- **REQ-007**: The kernel SHALL support full process lifecycle: QUEUED → ACTIVE → PROCESSING → COMPLETED, with SUSPENDED, FAILED, and TERMINATED as terminal/pause states.
- **REQ-008**: Mail messages SHALL be convertible to MessageProcess entries and vice versa via the mail protocol bridge.
- **REQ-009**: The system SHALL support event-driven notification via registered callback functions for all lifecycle and cognitive events.
- **REQ-010**: All string fields SHALL use fixed-size buffers with defined maximum lengths; no heap allocation for string storage.
- **REQ-011**: The library SHALL compile as C11 (`-std=c11`) and link only against standard C libraries plus `-lm`.
- **REQ-012**: Cognitive processing failures SHALL produce degraded-but-valid `dove9_cognitive_context` results rather than aborting the triadic loop.

### Security Requirements

- **SEC-001**: All string copy operations SHALL use length-bounded functions (`strncpy`, `snprintf`) to prevent buffer overflows.
- **SEC-002**: All array index operations SHALL validate bounds against defined maximum constants before access.
- **SEC-003**: External input (mail message fields) SHALL be treated as untrusted; body content SHALL be truncated to `DOVE9_MAX_BODY_LEN` (65536 bytes).
- **SEC-004**: Function pointer vtables SHALL be validated for non-NULL before invocation.

### Constraints

- **CON-001**: The library SHALL NOT depend on any Dovecot internal headers from `dovecot-core/` — it is architecturally independent.
- **CON-002**: The library SHALL NOT use dynamic memory allocation (`malloc`/`free`) for cognitive state buffers; all buffers are fixed-size struct members.
- **CON-003**: The library SHALL NOT perform I/O (network, disk) directly; all external operations are delegated to injected vtable services.
- **CON-004**: The library SHALL be single-threaded per `dove9_system` instance; no internal mutexes or atomic operations are required.
- **CON-005**: Cognitive Terms T3 and T6 are intentionally unoccupied in the `dove9_cognitive_term` enum. They SHALL NOT be implemented without a formal architectural rationale document.
- **CON-006**: All source files SHALL include the Dovecho copyright header.

### Guidelines

- **GUD-001**: Prefer static inline functions in headers for trivial initialization and accessor operations.
- **GUD-002**: Use opaque `struct` pointers for all module-level state; expose only the API through header function declarations.
- **GUD-003**: Follow the naming convention `dove9_<module>_<action>` for all public functions.
- **GUD-004**: Use `memset(&struct, 0, sizeof(struct))` or designated initializer defaults for struct initialization.
- **GUD-005**: Emit structured log output via the `dove9_logger` subsystem; never use raw `printf`/`fprintf` in cognitive code.
- **GUD-006**: Document all public functions with a block comment in the header describing purpose, parameters, and return semantics.

### Patterns

- **PAT-001**: **Vtable Injection** — External services (LLM, memory, persona) are provided as `const struct` of function pointers passed at initialization time. The library holds borrowed (non-owning) references.
- **PAT-002**: **Event Callback Registration** — Each module exposes an `*_on()` function accepting a `(event_fn, void *context)` pair. Events are dispatched synchronously during processing.
- **PAT-003**: **Tagged Union Events** — All event structs use an `enum type` discriminant with a `union data` payload, enabling type-safe event dispatch.
- **PAT-004**: **Create/Destroy Lifecycle** — Each module follows `*_create(config) → *_start() → *_stop() → *_destroy(&ptr)` lifecycle. Destroy takes a double pointer and NULLs it.
- **PAT-005**: **Output Parameters** — Functions that produce structured results use output parameters (`*out`) rather than returning heap-allocated structs.

## 4. Interfaces & Data Contracts

### 4.1 Type System (`dove9-types.h`)

#### Enumerations

| Enum | Values | Description |
|------|--------|-------------|
| `dove9_cognitive_mode` | `DOVE9_MODE_EXPRESSIVE`, `DOVE9_MODE_REFLECTIVE` | Two cognitive processing modes (feedforward vs. feedback) |
| `dove9_stream_id` | `DOVE9_STREAM_PRIMARY`, `DOVE9_STREAM_SECONDARY`, `DOVE9_STREAM_TERTIARY` | Three concurrent cognitive streams |
| `dove9_cognitive_term` | `DOVE9_TERM_T1_PERCEPTION`, `DOVE9_TERM_T2_IDEA_FORMATION`, `DOVE9_TERM_T4_SENSORY_INPUT`, `DOVE9_TERM_T5_ACTION_SEQUENCE`, `DOVE9_TERM_T7_MEMORY_ENCODING`, `DOVE9_TERM_T8_BALANCED_RESPONSE` | Six cognitive term functions (T3, T6 intentionally absent) |
| `dove9_step_type` | `DOVE9_STEP_PIVOTAL_RR`, `DOVE9_STEP_EXPRESSIVE`, `DOVE9_STEP_TRANSITION`, `DOVE9_STEP_REFLECTIVE` | Step classification within the cycle |
| `dove9_process_state` | `DOVE9_STATE_QUEUED`, `DOVE9_STATE_ACTIVE`, `DOVE9_STATE_PROCESSING`, `DOVE9_STATE_COMPLETED`, `DOVE9_STATE_FAILED`, `DOVE9_STATE_SUSPENDED`, `DOVE9_STATE_TERMINATED` | Process lifecycle states |
| `dove9_coupling_type` | `DOVE9_COUPLING_PERCEPTION_MEMORY`, `DOVE9_COUPLING_ASSESSMENT_PLANNING`, `DOVE9_COUPLING_BALANCED_INTEGRATION` | Three cross-stream tensional coupling types |
| `dove9_mail_flag` | `DOVE9_FLAG_SEEN`, `DOVE9_FLAG_ANSWERED`, `DOVE9_FLAG_FLAGGED`, `DOVE9_FLAG_DELETED`, `DOVE9_FLAG_DRAFT`, `DOVE9_FLAG_RECENT` | Bitfield mail flags (combinable via `|`) |
| `dove9_mail_protocol` | `DOVE9_PROTO_IMAP`, `DOVE9_PROTO_LMTP`, `DOVE9_PROTO_SMTP` | Mail protocol types |
| `dove9_mail_operation` | `DOVE9_OP_RECEIVE`, `DOVE9_OP_SEND`, `DOVE9_OP_MOVE`, `DOVE9_OP_FLAG_UPDATE`, `DOVE9_OP_DELETE` | Mail operations |

#### Fixed-Size Limits

| Constant | Value | Purpose |
|----------|-------|---------|
| `DOVE9_MAX_PROCESSES` | 4096 | Maximum concurrent processes in kernel |
| `DOVE9_MAX_QUEUE_DEPTH` | 4096 | Maximum priority queue depth |
| `DOVE9_MAX_ID_LEN` | 256 | Maximum length of process/message IDs |
| `DOVE9_MAX_ADDR_LEN` | 256 | Maximum email address length |
| `DOVE9_MAX_SUBJECT_LEN` | 512 | Maximum email subject length |
| `DOVE9_MAX_BODY_LEN` | 65536 | Maximum email/response body length |
| `DOVE9_MAX_RECIPIENTS` | 64 | Maximum recipients per message |
| `DOVE9_MAX_REFERENCES` | 32 | Maximum References header entries |

#### Core Structures

```c
/* Step configuration (static, read-only at runtime) */
struct dove9_step_config {
    unsigned int         step_number;    /* 1-12 */
    enum dove9_stream_id stream;
    enum dove9_cognitive_term term;
    enum dove9_cognitive_mode mode;
    enum dove9_step_type type;
    unsigned int         phase_degrees;  /* 0-330 */
};

/* Stream configuration (static, read-only at runtime) */
struct dove9_stream_config {
    enum dove9_stream_id id;
    unsigned int         phase_offset;   /* 0, 120, 240 degrees */
    unsigned int         steps[4];       /* indices into step_configs */
};

/* T-point convergence descriptor */
struct dove9_triad_point {
    unsigned int index;                  /* 0-3 */
    unsigned int steps[3];               /* one step per stream */
};

/* Per-stream runtime state */
struct dove9_stream_state {
    enum dove9_stream_id id;
    unsigned int         current_step;
    unsigned int         completed_steps;
    double               phase_progress;
};

/* Cognitive context — the central data flowing through all processors */
struct dove9_cognitive_context {
    char                    input[DOVE9_MAX_BODY_LEN];
    char                    response[DOVE9_MAX_BODY_LEN];
    enum dove9_cognitive_mode mode;
    enum dove9_cognitive_term active_term;
    double                  salience;       /* [0.0, 1.0] */
    char                    memory_context[DOVE9_MAX_BODY_LEN];
    char                    personality_state[1024];
    bool                    degraded;
    char                    error[512];
};

/* Mail message — email representation for cognitive processing */
struct dove9_mail_message {
    char                        message_id[DOVE9_MAX_ID_LEN];
    char                        from[DOVE9_MAX_ADDR_LEN];
    char                        to[DOVE9_MAX_RECIPIENTS][DOVE9_MAX_ADDR_LEN];
    unsigned int                to_count;
    char                        subject[DOVE9_MAX_SUBJECT_LEN];
    char                        body[DOVE9_MAX_BODY_LEN];
    unsigned int                flags;      /* dove9_mail_flag bitfield */
    char                        mailbox[DOVE9_MAX_ID_LEN];
    enum dove9_mail_protocol    protocol;
    time_t                      received_at;
    char                        in_reply_to[DOVE9_MAX_ID_LEN];
    char                        references[DOVE9_MAX_REFERENCES][DOVE9_MAX_ID_LEN];
    unsigned int                reference_count;
};

/* Message process — a mail message promoted to a kernel process */
struct dove9_message_process {
    char                        id[DOVE9_MAX_ID_LEN];
    char                        message_id[DOVE9_MAX_ID_LEN];
    enum dove9_process_state    state;
    int                         priority;   /* 1 (low) to 10 (high) */
    time_t                      created_at;
    time_t                      updated_at;
    struct dove9_cognitive_context context;
    struct dove9_execution_record execution;
};
```

#### Inline Utility Functions

```c
/* Default configuration with sane defaults */
static inline struct dove9_config dove9_config_default(void);

/* Initialize a cognitive context to zero/defaults */
static inline void dove9_cognitive_context_init(struct dove9_cognitive_context *ctx);

/* Default mailbox mapping (INBOX, Drafts, Sent, Trash, Archive, Junk) */
static inline struct dove9_mailbox_mapping dove9_mailbox_mapping_default(void);

/* Coupling bitfield operations */
static inline bool dove9_coupling_is_active(unsigned int coupling_mask,
                                            enum dove9_coupling_type type);
static inline void dove9_coupling_set(unsigned int *coupling_mask,
                                      enum dove9_coupling_type type);
static inline void dove9_coupling_clear(unsigned int *coupling_mask,
                                        enum dove9_coupling_type type);
```

### 4.2 Logger (`dove9-logger.h`)

```c
struct dove9_logger;

/* Lifecycle */
struct dove9_logger *dove9_logger_create(const char *module_name);
struct dove9_logger *dove9_logger_create_child(const struct dove9_logger *parent,
                                               const char *child_name);
void dove9_logger_destroy(struct dove9_logger **logger);

/* Logging (variadic, printf-style format strings) */
void dove9_log_debug(const struct dove9_logger *l, const char *fmt, ...);
void dove9_log_info(const struct dove9_logger *l, const char *fmt, ...);
void dove9_log_warn(const struct dove9_logger *l, const char *fmt, ...);
void dove9_log_error(const struct dove9_logger *l, const char *fmt, ...);
```

**Environment variables:**
- `LOG_LEVEL`: Set minimum level (`debug`, `info`, `warn`, `error`). Default: `info`.
- `NO_COLOR`: If set and non-empty, disables ANSI color codes.

### 4.3 Triadic Engine (`dove9-triadic-engine.h`)

#### Cognitive Processor Vtable

```c
struct dove9_cognitive_processor {
    void *context;  /* opaque user data passed to all functions */
    int (*process_t1)(void *ctx, struct dove9_cognitive_context *cctx,
                      enum dove9_cognitive_mode mode);
    int (*process_t2)(void *ctx, struct dove9_cognitive_context *cctx,
                      enum dove9_cognitive_mode mode);
    int (*process_t4)(void *ctx, struct dove9_cognitive_context *cctx,
                      enum dove9_cognitive_mode mode);
    int (*process_t5)(void *ctx, struct dove9_cognitive_context *cctx,
                      enum dove9_cognitive_mode mode);
    int (*process_t7)(void *ctx, struct dove9_cognitive_context *cctx,
                      enum dove9_cognitive_mode mode);
    int (*process_t8)(void *ctx, struct dove9_cognitive_context *cctx,
                      enum dove9_cognitive_mode mode);
};
```

#### Static Data Tables

```c
/* 12 step configurations (step_number, stream, term, mode, type, phase_degrees) */
extern const struct dove9_step_config dove9_step_configs[12];

/* 3 stream configurations (id, phase_offset, steps[4]) */
extern const struct dove9_stream_config dove9_stream_configs[3];

/* 4 triad point convergence descriptors */
extern const struct dove9_triad_point dove9_triad_points[4];
```

#### Engine API

```c
struct dove9_triadic_engine;

/* Lifecycle */
struct dove9_triadic_engine *
dove9_triadic_engine_create(const struct dove9_cognitive_processor *processor);
void dove9_triadic_engine_destroy(struct dove9_triadic_engine **engine);
int  dove9_triadic_engine_start(struct dove9_triadic_engine *engine);
void dove9_triadic_engine_stop(struct dove9_triadic_engine *engine);

/* Event subscription (up to 16 handlers) */
typedef void (*dove9_triadic_event_fn)(const struct dove9_triadic_event *event,
                                       void *context);
void dove9_triadic_engine_on(struct dove9_triadic_engine *engine,
                             dove9_triadic_event_fn handler, void *context);

/* Processing */
int dove9_triadic_engine_process_message(struct dove9_triadic_engine *engine,
                                          struct dove9_cognitive_context *context);

/* Step control */
int dove9_triadic_engine_advance_step(struct dove9_triadic_engine *engine);

/* State queries */
unsigned int dove9_triadic_engine_get_current_step(
    const struct dove9_triadic_engine *engine);
unsigned int dove9_triadic_engine_get_current_cycle(
    const struct dove9_triadic_engine *engine);
void dove9_triadic_engine_get_stream_state(
    const struct dove9_triadic_engine *engine,
    enum dove9_stream_id stream,
    struct dove9_stream_state *out);
bool dove9_triadic_engine_is_running(
    const struct dove9_triadic_engine *engine);

/* Utility */
const struct dove9_triad_point *dove9_triad_at_step(unsigned int step);
unsigned int dove9_get_active_steps_for_time_point(
    unsigned int time_point,
    const struct dove9_step_config **out, unsigned int max_out);
unsigned int dove9_detect_couplings(
    const struct dove9_step_config *active_steps,
    unsigned int count, enum dove9_coupling_type *out, unsigned int max_out);
void dove9_integrate_stream_results(
    const struct dove9_stream_state *streams, unsigned int count,
    struct dove9_cognitive_context *integrated);
```

#### Triadic Event

```c
enum dove9_triadic_event_type {
    DOVE9_TRIADIC_STEP_STARTED,
    DOVE9_TRIADIC_STEP_COMPLETED,
    DOVE9_TRIADIC_TRIAD_CONVERGED,
    DOVE9_TRIADIC_COUPLING_DETECTED,
    DOVE9_TRIADIC_CYCLE_COMPLETED,
};

struct dove9_triadic_event {
    enum dove9_triadic_event_type type;
    union { /* step_started, step_completed, triad_converged, coupling_detected, cycle_completed */ } data;
};
```

### 4.4 Deep Tree Echo Processor (`dove9-dte-processor.h`)

#### External Service Vtables

```c
/* LLM inference service */
struct dove9_llm_service {
    void *context;
    int (*generate_response)(void *ctx, const char *prompt, const char *system_prompt,
                             char *out, unsigned int out_len);
    int (*generate_parallel_response)(void *ctx, const char **prompts,
                                      unsigned int count, char **outs,
                                      unsigned int out_len);
};

/* Episodic/semantic memory store */
struct dove9_memory_store {
    void *context;
    int (*store)(void *ctx, const char *key, const char *content, double importance);
    int (*retrieve_recent)(void *ctx, unsigned int count, char *out, unsigned int out_len);
    int (*retrieve_relevant)(void *ctx, const char *query, unsigned int count,
                             char *out, unsigned int out_len);
};

/* Personality/emotion engine */
struct dove9_persona_core {
    void *context;
    int (*get_personality)(void *ctx, char *out, unsigned int out_len);
    int (*get_dominant_emotion)(void *ctx, char *out, unsigned int out_len);
    int (*update_emotional_state)(void *ctx, const char *input, double salience);
};
```

#### Processor API

```c
struct dove9_dte_processor;

struct dove9_dte_processor_config {
    bool         enable_parallel_cognition;
    unsigned int memory_retrieval_count;
    double       salience_threshold;    /* [0.0, 1.0] */
};

struct dove9_dte_processor *
dove9_dte_processor_create(const struct dove9_dte_processor_config *config,
                           const struct dove9_llm_service *llm,
                           const struct dove9_memory_store *memory,
                           const struct dove9_persona_core *persona);
void dove9_dte_processor_destroy(struct dove9_dte_processor **proc);

/* Convert to cognitive_processor vtable for use by triadic engine */
struct dove9_cognitive_processor
dove9_dte_processor_as_cognitive(struct dove9_dte_processor *proc);
```

### 4.5 Kernel (`dove9-kernel.h`)

```c
struct dove9_kernel;

/* Lifecycle */
struct dove9_kernel *
dove9_kernel_create(const struct dove9_config *config,
                    struct dove9_triadic_engine *engine);
void dove9_kernel_destroy(struct dove9_kernel **kernel);
int  dove9_kernel_start(struct dove9_kernel *kernel);
void dove9_kernel_stop(struct dove9_kernel *kernel);

/* Event subscription */
typedef void (*dove9_kernel_event_fn)(const struct dove9_kernel_event *event,
                                      void *context);
void dove9_kernel_on(struct dove9_kernel *kernel,
                     dove9_kernel_event_fn handler, void *context);

/* Process management */
struct dove9_message_process *
dove9_kernel_create_process(struct dove9_kernel *kernel,
                            const struct dove9_cognitive_context *ctx,
                            int priority);
const struct dove9_message_process *
dove9_kernel_get_process(const struct dove9_kernel *kernel, const char *id);
unsigned int
dove9_kernel_get_all_processes(const struct dove9_kernel *kernel,
                               const struct dove9_message_process **out,
                               unsigned int max_out);
unsigned int
dove9_kernel_get_active_processes(const struct dove9_kernel *kernel,
                                  const struct dove9_message_process **out,
                                  unsigned int max_out);
int  dove9_kernel_terminate_process(struct dove9_kernel *kernel, const char *id);
int  dove9_kernel_suspend_process(struct dove9_kernel *kernel, const char *id);
int  dove9_kernel_resume_process(struct dove9_kernel *kernel, const char *id);
struct dove9_message_process *
dove9_kernel_fork_process(struct dove9_kernel *kernel, const char *parent_id);

/* Mail protocol integration */
void dove9_kernel_enable_mail_protocol(struct dove9_kernel *kernel,
                                       const struct dove9_mail_bridge_config *cfg);
struct dove9_message_process *
dove9_kernel_create_process_from_mail(struct dove9_kernel *kernel,
                                      const struct dove9_mail_message *mail);
const struct dove9_message_process *
dove9_kernel_get_process_by_message_id(const struct dove9_kernel *kernel,
                                       const char *message_id);
const char *
dove9_kernel_get_mailbox(const struct dove9_kernel *kernel, const char *id);
int dove9_kernel_move_mailbox(struct dove9_kernel *kernel,
                              const char *id, const char *mailbox);
int dove9_kernel_update_from_flags(struct dove9_kernel *kernel,
                                   const char *id, unsigned int flags);

/* Scheduling tick */
int  dove9_kernel_tick(struct dove9_kernel *kernel);

/* Metrics */
void dove9_kernel_get_metrics(const struct dove9_kernel *kernel,
                              struct dove9_kernel_metrics *out);
bool dove9_kernel_is_running(const struct dove9_kernel *kernel);
```

#### Kernel Event

```c
enum dove9_kernel_event_type {
    DOVE9_KERNEL_PROCESS_CREATED,
    DOVE9_KERNEL_PROCESS_STARTED,
    DOVE9_KERNEL_PROCESS_COMPLETED,
    DOVE9_KERNEL_PROCESS_FAILED,
    DOVE9_KERNEL_PROCESS_STATE_CHANGED,
    DOVE9_KERNEL_TICK,
};

struct dove9_kernel_event {
    enum dove9_kernel_event_type type;
    union { /* Fields per event type */ } data;
};
```

### 4.6 Mail Protocol Bridge (`dove9-mail-protocol-bridge.h`)

```c
struct dove9_mail_protocol_bridge;

struct dove9_mail_bridge_config {
    struct dove9_mailbox_mapping mailbox_mapping;
    int  default_priority;
    bool enable_threading;
};

/* Lifecycle */
struct dove9_mail_protocol_bridge *
dove9_mail_bridge_create(const struct dove9_mail_bridge_config *config);
void dove9_mail_bridge_destroy(struct dove9_mail_protocol_bridge **bridge);

/* Conversions */
void dove9_mail_to_process(const struct dove9_mail_protocol_bridge *bridge,
                           const struct dove9_mail_message *mail,
                           struct dove9_message_process *out);
void dove9_process_to_mail(const struct dove9_mail_protocol_bridge *bridge,
                           const struct dove9_message_process *process,
                           const char *response_body,
                           struct dove9_mail_message *out);

/* State/flag mapping */
enum dove9_process_state
dove9_mail_flags_to_state(unsigned int flags, const char *mailbox,
                          const struct dove9_mailbox_mapping *mapping);
unsigned int dove9_state_to_mail_flags(enum dove9_process_state state);
const char * dove9_state_to_mailbox(enum dove9_process_state state,
                                    const struct dove9_mailbox_mapping *mapping);

/* Priority calculation */
int dove9_mail_calculate_priority(const struct dove9_mail_message *mail,
                                  int default_priority);

/* Context creation */
void dove9_mail_create_cognitive_context(const struct dove9_mail_message *mail,
                                         struct dove9_cognitive_context *out);

/* Thread relations */
struct dove9_thread_relations {
    char         parent_id[DOVE9_MAX_ID_LEN];
    char         sibling_ids[DOVE9_MAX_REFERENCES][DOVE9_MAX_ID_LEN];
    unsigned int sibling_count;
};
void dove9_mail_extract_thread_relations(const struct dove9_mail_message *mail,
                                         struct dove9_thread_relations *out);
```

### 4.7 Orchestrator Bridge (`dove9-orchestrator-bridge.h`)

```c
struct dove9_orchestrator_bridge;

struct dove9_dovecot_email {
    char         from[DOVE9_MAX_ADDR_LEN];
    char         to[DOVE9_MAX_RECIPIENTS][DOVE9_MAX_ADDR_LEN];
    unsigned int to_count;
    char         subject[DOVE9_MAX_SUBJECT_LEN];
    char         body[DOVE9_MAX_BODY_LEN];
    char         message_id[DOVE9_MAX_ID_LEN];
    time_t       received_at;
    struct { char key[128]; char value[512]; } headers[32];
    unsigned int header_count;
};

struct dove9_email_response {
    char to[DOVE9_MAX_ADDR_LEN];
    char from[DOVE9_MAX_ADDR_LEN];
    char subject[DOVE9_MAX_SUBJECT_LEN];
    char body[DOVE9_MAX_BODY_LEN];
    char in_reply_to[DOVE9_MAX_ID_LEN];
};

/* Lifecycle */
struct dove9_orchestrator_bridge *
dove9_orchestrator_bridge_create(const struct dove9_orchestrator_bridge_config *config);
void dove9_orchestrator_bridge_destroy(struct dove9_orchestrator_bridge **bridge);
void dove9_orchestrator_bridge_initialize(struct dove9_orchestrator_bridge *bridge,
                                          const struct dove9_llm_service *llm,
                                          const struct dove9_memory_store *memory,
                                          const struct dove9_persona_core *persona);
int  dove9_orchestrator_bridge_start(struct dove9_orchestrator_bridge *bridge);
void dove9_orchestrator_bridge_stop(struct dove9_orchestrator_bridge *bridge);

/* Event subscription */
typedef void (*dove9_bridge_event_fn)(const struct dove9_bridge_event *event,
                                      void *context);
void dove9_orchestrator_bridge_on(struct dove9_orchestrator_bridge *bridge,
                                  dove9_bridge_event_fn handler, void *context);

/* Email processing */
struct dove9_email_response *
dove9_orchestrator_bridge_process_email(struct dove9_orchestrator_bridge *bridge,
                                        const struct dove9_dovecot_email *email);
```

### 4.8 Sys6 Mail Scheduler (`dove9-sys6-mail-scheduler.h`)

```c
struct dove9_sys6_mail_scheduler;

/* Constants */
#define SYS6_CYCLE_LENGTH   30
#define DOVE9_CYCLE_LENGTH  12
#define GRAND_CYCLE_LENGTH  60  /* LCM(30, 12) */

/* Schedule result */
struct dove9_mail_schedule_result {
    char         process_id[DOVE9_MAX_ID_LEN];
    char         message_id[DOVE9_MAX_ID_LEN];
    unsigned int scheduled_step;
    unsigned int scheduled_grand_cycle_step;
    unsigned int sys6_phase;        /* 1-3 */
    unsigned int sys6_stage;        /* 1-5 */
    unsigned int sys6_step;         /* 1-2 (A/B) */
    unsigned int dove9_stream;      /* 1-3 */
    unsigned int dove9_triad;       /* 0-3 */
    int          priority;
    unsigned int estimated_completion_step;
};

/* Lifecycle */
struct dove9_sys6_mail_scheduler *
dove9_sys6_scheduler_create(unsigned int step_duration_ms,
                            const struct dove9_sys6_scheduler_config *config);
void dove9_sys6_scheduler_destroy(struct dove9_sys6_mail_scheduler **s);
void dove9_sys6_scheduler_start(struct dove9_sys6_mail_scheduler *s);
void dove9_sys6_scheduler_stop(struct dove9_sys6_mail_scheduler *s);

/* Event subscription */
typedef void (*dove9_scheduler_event_fn)(const struct dove9_scheduler_event *event,
                                         void *context);
void dove9_sys6_scheduler_on(struct dove9_sys6_mail_scheduler *s,
                             dove9_scheduler_event_fn handler, void *context);

/* Scheduling */
struct dove9_mail_schedule_result
dove9_sys6_scheduler_schedule_mail(struct dove9_sys6_mail_scheduler *s,
                                   const struct dove9_mail_message *mail,
                                   const struct dove9_message_process *process);
void dove9_sys6_scheduler_complete_process(struct dove9_sys6_mail_scheduler *s,
                                           const char *process_id);
void dove9_sys6_scheduler_advance_step(struct dove9_sys6_mail_scheduler *s);

/* Query */
const struct dove9_mail_schedule_result *
dove9_sys6_scheduler_get_schedule(const struct dove9_sys6_mail_scheduler *s,
                                  const char *process_id);
unsigned int
dove9_sys6_scheduler_get_pending_count(const struct dove9_sys6_mail_scheduler *s);
void dove9_sys6_scheduler_get_state(const struct dove9_sys6_mail_scheduler *s,
                                    struct dove9_scheduler_state *out);
void dove9_sys6_scheduler_get_cycle_positions(
    const struct dove9_sys6_mail_scheduler *s,
    struct dove9_cycle_positions *out);
struct dove9_next_slot
dove9_sys6_scheduler_get_next_slot(const struct dove9_sys6_mail_scheduler *s,
                                   int priority);
```

### 4.9 Sys6 Orchestrator Bridge (`dove9-sys6-orchestrator-bridge.h`)

```c
struct dove9_sys6_orchestrator_bridge;

/* Statistics */
struct dove9_sys6_integration_stats {
    unsigned int grand_cycles, sys6_cycles, dove9_cycles;
    unsigned int total_scheduled, total_completed;
    double       average_processing_steps;
    unsigned int phase1_count, phase2_count, phase3_count;
    unsigned int stream1_count, stream2_count, stream3_count;
};

/* Lifecycle */
struct dove9_sys6_orchestrator_bridge *
dove9_sys6_bridge_create(const struct dove9_sys6_bridge_config *config);
void dove9_sys6_bridge_destroy(struct dove9_sys6_orchestrator_bridge **bridge);
void dove9_sys6_bridge_initialize(struct dove9_sys6_orchestrator_bridge *bridge,
                                  const struct dove9_llm_service *llm,
                                  const struct dove9_memory_store *memory,
                                  const struct dove9_persona_core *persona);
int  dove9_sys6_bridge_start(struct dove9_sys6_orchestrator_bridge *bridge);
void dove9_sys6_bridge_stop(struct dove9_sys6_orchestrator_bridge *bridge);

/* Event subscription */
typedef void (*dove9_sys6_bridge_event_fn)(const struct dove9_sys6_bridge_event *event,
                                           void *context);
void dove9_sys6_bridge_on(struct dove9_sys6_orchestrator_bridge *bridge,
                          dove9_sys6_bridge_event_fn handler, void *context);

/* Email processing */
struct dove9_email_response *
dove9_sys6_bridge_process_email(struct dove9_sys6_orchestrator_bridge *bridge,
                                const struct dove9_dovecot_email *email);

/* Statistics */
void dove9_sys6_bridge_get_stats(const struct dove9_sys6_orchestrator_bridge *bridge,
                                 struct dove9_sys6_integration_stats *out);
void dove9_sys6_bridge_get_scheduler_state(
    const struct dove9_sys6_orchestrator_bridge *bridge,
    struct dove9_scheduler_state *out);
```

### 4.10 Top-Level System (`dove9-system.h`)

```c
struct dove9_system;

struct dove9_system_config {
    struct dove9_config              base;
    const struct dove9_llm_service  *llm;       /* borrowed */
    const struct dove9_memory_store *memory;     /* borrowed */
    const struct dove9_persona_core *persona;    /* borrowed */
    char milter_socket[256];
    char lmtp_socket[256];
    char bot_email_address[DOVE9_MAX_ADDR_LEN];
};

/* Lifecycle */
struct dove9_system *dove9_system_create(const struct dove9_system_config *config);
void dove9_system_destroy(struct dove9_system **system);
int  dove9_system_start(struct dove9_system *system);
void dove9_system_stop(struct dove9_system *system);
bool dove9_system_is_running(const struct dove9_system *system);

/* Event subscription */
typedef void (*dove9_system_event_fn)(const struct dove9_system_event *event,
                                      void *context);
void dove9_system_on(struct dove9_system *system,
                     dove9_system_event_fn handler, void *context);

/* Mail processing — the primary entry point */
struct dove9_message_process *
dove9_system_process_mail(struct dove9_system *system,
                          const struct dove9_mail_message *mail);
```

## 5. Acceptance Criteria

- **AC-001**: Given a valid `dove9_cognitive_processor` vtable, when `dove9_triadic_engine_create()` is called and started, then the engine SHALL cycle through all 12 steps in order, invoking the correct T-function for each step.
- **AC-002**: Given the engine is at a T-point step (1, 5, 9 or 2, 6, 10 or 3, 7, 11 or 4, 8, 12), when the step completes, then a `DOVE9_TRIADIC_TRIAD_CONVERGED` event SHALL be emitted with the correct triad point index.
- **AC-003**: Given steps with T4 (EXPRESSIVE) and T7 (REFLECTIVE) active simultaneously, when coupling detection runs, then `DOVE9_COUPLING_PERCEPTION_MEMORY` SHALL be reported.
- **AC-004**: Given a `dove9_mail_message` with `DOVE9_FLAG_FLAGGED` set and `in_reply_to` non-empty, when `dove9_mail_calculate_priority()` is called with default_priority=5, then the returned priority SHALL be ≥ 7 (base 5 + flagged boost + reply boost) and ≤ 10.
- **AC-005**: Given the kernel has `DOVE9_MAX_PROCESSES` active processes, when `dove9_kernel_create_process()` is called, then it SHALL return NULL without crashing.
- **AC-006**: Given a `dove9_mail_message`, when `dove9_system_process_mail()` is called, then a `DOVE9_SYS_MAIL_RECEIVED` event SHALL be emitted, the message SHALL be converted to a process, and upon completion a `DOVE9_SYS_RESPONSE_READY` event SHALL be emitted with a response mail.
- **AC-007**: Given the Sys6 scheduler is running with operadic scheduling enabled, when a priority-8 message is scheduled, then it SHALL be assigned to phase 1 (high-priority phase) with `sys6_phase == 1`.
- **AC-008**: Given a `dove9_dte_processor` with valid LLM/memory/persona vtables, when `dove9_dte_processor_as_cognitive()` is called, then the returned `dove9_cognitive_processor` SHALL have all 6 function pointers non-NULL.
- **AC-009**: Given the engine completes a full 12-step cycle, when `dove9_triadic_engine_get_current_cycle()` is called, then the cycle counter SHALL have incremented by 1.
- **AC-010**: Given the grand cycle step reaches 60, when the scheduler advances, then `DOVE9_SCHED_GRAND_CYCLE_BOUNDARY` SHALL be emitted and the step SHALL reset to 1.
- **AC-011**: Given a process in state ACTIVE, when `dove9_kernel_suspend_process()` is called, then the state SHALL transition to SUSPENDED and a `DOVE9_KERNEL_PROCESS_STATE_CHANGED` event SHALL be emitted.
- **AC-012**: Given a T-function processor that throws/returns error, when the triadic engine invokes it, then the cognitive context SHALL be marked `degraded=true` with the error string populated, and the engine SHALL continue to the next step.

## 6. Test Automation Strategy

### Test Levels

| Level | Scope | Framework |
|-------|-------|-----------|
| **Unit** | Individual functions: type helpers, priority calculation, flag mapping, coupling detection | C test framework (e.g., `check`, `cmocka`, or custom `assert`-based harness) |
| **Integration** | Module interactions: engine → processor, kernel → engine, bridge → kernel | Same framework with test fixtures providing mock vtables |
| **System** | Full `dove9_system` lifecycle: create → start → process_mail → event → stop → destroy | End-to-end test binary with mock LLM/memory/persona services |

### Test Data Management

- Mock vtables provide deterministic responses (e.g., LLM always returns `"test response"`, memory returns fixed context)
- Test mail messages use well-known fixture data with controlled flags, priorities, and threading
- Each test creates and destroys its own system instance; no shared state between tests

### CI/CD Integration

- Tests are built and run via `make check` in the Autotools build system
- The `dovecho-core: test` VS Code task triggers `make check`
- Tests SHALL be compiled with `-Wall -Wextra -Werror` to catch all warnings

### Coverage Requirements

- **Minimum**: 80% line coverage across all `.c` files
- **Critical paths**: 100% branch coverage for coupling detection, T-point convergence, process state transitions, and priority calculation

### Performance Testing

- Benchmark: process 10,000 mail messages through `dove9_system_process_mail()` and verify throughput exceeds 1,000 messages/second with mock services
- Memory: verify no growth in resident memory after 100,000 cycles (no leaks in fixed-buffer architecture)

## 7. Rationale & Context

### Why C?

The Dove9 cognitive layer targets embedding within the Dovecot/Dovecho mail server, which is written in C. A native C implementation eliminates the Node.js runtime dependency, reduces memory footprint by orders of magnitude (fixed buffers vs. V8 heap), and enables direct integration via Dovecot's plugin/milter API without IPC overhead.

### Why Fixed-Size Buffers?

Dynamic allocation in cognitive processing paths introduces non-deterministic latency from `malloc`/`free` and garbage collection. Fixed-size buffers provide:
1. Deterministic memory layout (cache-friendly)
2. Bounded worst-case memory consumption (auditable)
3. No fragmentation over long-running daemon lifetimes
4. Simplified error handling (no allocation failure paths in cognitive code)

### Why Vtable Injection?

The cognitive layer must be independent of specific LLM, memory, and persona implementations. Vtable injection (PAT-001) provides:
1. Testability: mock services for unit testing
2. Flexibility: swap LLM providers without recompiling
3. Separation of concerns: cognitive scheduling logic vs. inference execution

### Why the 12/30/60 Cycle Hierarchy?

The triadic (12-step), Sys6 (30-step), and grand (60-step) cycles are mathematically related via LCM. This ensures:
1. All cycle types complete at predictable, aligned boundaries
2. Cross-cycle synchronization events (42 per Sys6 cycle) occur at deterministic intervals
3. The scheduling resolution (individual steps) maps cleanly to both cognitive processing and mail scheduling

### Relationship to TypeScript Implementation

The C layer is a port of `dove9/src/` TypeScript code. Both implementations share:
- Identical step assignment tables and T-point definitions
- Same coupling detection logic
- Same priority calculation algorithm
- Same process state machine

The TypeScript implementation remains the reference for test behavior and serves the desktop applications (Electron). The C implementation targets server-side embedding.

## 8. Dependencies & External Integrations

### External Systems

- **EXT-001**: Dovecot/Dovecho Mail Server — The host process. `libdove9` is loaded as a static library linked into the mail server binary. Integration occurs via Milter and LMTP interfaces.

### Infrastructure Dependencies

- **INF-001**: POSIX C Runtime — Required headers: `<stdlib.h>`, `<string.h>`, `<stdio.h>`, `<stdarg.h>`, `<stdbool.h>`, `<time.h>`, `<math.h>`, `<strings.h>` (for `strcasecmp`).
- **INF-002**: Math Library — Link with `-lm` for `floor()`, `ceil()` in scheduling calculations.
- **INF-003**: GNU Autotools — Build system: `autoconf`, `automake`, `libtool` for `Makefile.am` processing.

### Technology Platform Dependencies

- **PLT-001**: C11 Standard — Compilation requires `-std=c11`. Uses `_Bool`/`bool`, designated initializers, compound literals.
- **PLT-002**: POSIX Extensions — `strcasecmp()` from `<strings.h>` for case-insensitive email address comparison. Non-POSIX platforms require a shim.

### Cognitive Service Dependencies (Injected at Runtime)

- **SVC-001**: LLM Inference Service — Must implement `dove9_llm_service` vtable. Provides `generate_response()` and `generate_parallel_response()`.
- **SVC-002**: Memory Store — Must implement `dove9_memory_store` vtable. Provides `store()`, `retrieve_recent()`, `retrieve_relevant()`.
- **SVC-003**: Persona Core — Must implement `dove9_persona_core` vtable. Provides `get_personality()`, `get_dominant_emotion()`, `update_emotional_state()`.

## 9. Examples & Edge Cases

### Example: Minimal System Setup

```c
#include "dove9-system.h"

/* Mock LLM service */
static int mock_generate(void *ctx, const char *prompt,
                         const char *system_prompt,
                         char *out, unsigned int out_len) {
    snprintf(out, out_len, "Echo: %s", prompt);
    return 0;
}

static struct dove9_llm_service mock_llm = {
    .context = NULL,
    .generate_response = mock_generate,
    .generate_parallel_response = NULL,
};

/* Mock memory store */
static int mock_store(void *ctx, const char *key,
                      const char *content, double importance) { return 0; }
static int mock_retrieve_recent(void *ctx, unsigned int count,
                                char *out, unsigned int out_len) {
    snprintf(out, out_len, "No recent memories.");
    return 0;
}
static int mock_retrieve_relevant(void *ctx, const char *query,
                                  unsigned int count,
                                  char *out, unsigned int out_len) {
    snprintf(out, out_len, "No relevant memories for: %s", query);
    return 0;
}

static struct dove9_memory_store mock_memory = {
    .context = NULL,
    .store = mock_store,
    .retrieve_recent = mock_retrieve_recent,
    .retrieve_relevant = mock_retrieve_relevant,
};

/* Mock persona core */
static int mock_personality(void *ctx, char *out, unsigned int out_len) {
    snprintf(out, out_len, "curious and thoughtful");
    return 0;
}
static int mock_emotion(void *ctx, char *out, unsigned int out_len) {
    snprintf(out, out_len, "neutral");
    return 0;
}
static int mock_update_emotion(void *ctx, const char *input,
                               double salience) { return 0; }

static struct dove9_persona_core mock_persona = {
    .context = NULL,
    .get_personality = mock_personality,
    .get_dominant_emotion = mock_emotion,
    .update_emotional_state = mock_update_emotion,
};

int main(void) {
    struct dove9_system_config config;
    memset(&config, 0, sizeof(config));
    config.base = dove9_config_default();
    config.llm = &mock_llm;
    config.memory = &mock_memory;
    config.persona = &mock_persona;
    snprintf(config.bot_email_address, sizeof(config.bot_email_address),
             "echo@dove9.local");

    struct dove9_system *sys = dove9_system_create(&config);
    dove9_system_start(sys);

    /* Construct an incoming mail message */
    struct dove9_mail_message mail;
    memset(&mail, 0, sizeof(mail));
    snprintf(mail.message_id, sizeof(mail.message_id), "<msg-001@example.com>");
    snprintf(mail.from, sizeof(mail.from), "user@example.com");
    snprintf(mail.to[0], sizeof(mail.to[0]), "echo@dove9.local");
    mail.to_count = 1;
    snprintf(mail.subject, sizeof(mail.subject), "Hello");
    snprintf(mail.body, sizeof(mail.body), "How are you?");
    mail.protocol = DOVE9_PROTO_LMTP;
    mail.received_at = time(NULL);

    /* Process — this drives the full cognitive pipeline */
    struct dove9_message_process *proc = dove9_system_process_mail(sys, &mail);

    /* Cleanup */
    dove9_system_stop(sys);
    dove9_system_destroy(&sys);
    return 0;
}
```

### Edge Case: Process Table Full

```c
/* When all DOVE9_MAX_PROCESSES slots are occupied */
struct dove9_message_process *proc = dove9_kernel_create_process(kernel, &ctx, 5);
/* proc == NULL when table is full; caller must handle gracefully */
if (proc == NULL) {
    dove9_log_warn(logger, "Process table full, deferring message");
    /* Queue externally or return backpressure signal */
}
```

### Edge Case: NULL Vtable Function Pointer

```c
/* If generate_parallel_response is NULL but parallel cognition is requested */
struct dove9_dte_processor_config cfg = {
    .enable_parallel_cognition = true,
    .memory_retrieval_count = 5,
    .salience_threshold = 0.3,
};
/* The processor MUST fall back to sequential generate_response()
   when generate_parallel_response is NULL */
```

### Edge Case: Oversized Mail Body

```c
/* Mail body exceeding DOVE9_MAX_BODY_LEN is silently truncated */
struct dove9_mail_message mail;
memset(&mail, 0, sizeof(mail));
/* Body is always bounded by sizeof(mail.body) = DOVE9_MAX_BODY_LEN */
snprintf(mail.body, sizeof(mail.body), "%s", very_long_string);
/* No overflow — snprintf guarantees NUL termination within buffer */
```

### Edge Case: Coupling at T-point 0

```c
/* At T-point 0, steps 1 (T1_PERCEPTION/REFLECTIVE), 5 (T1_PERCEPTION/REFLECTIVE),
   and 9 (T7_MEMORY_ENCODING/REFLECTIVE) are active.
   T1(Reflective) + T7(Reflective) does NOT trigger PERCEPTION_MEMORY coupling
   because that requires T4(Expressive) + T7(Reflective).
   T-point 0 has no active couplings — all three steps are purely reflective. */
unsigned int coupling_count = dove9_detect_couplings(active_steps, 3, out, 3);
/* coupling_count == 0 at T-point 0 */
```

## 10. Validation Criteria

| ID | Criterion | Method |
|----|-----------|--------|
| **VAL-001** | All source files compile without warnings under `-Wall -Wextra -Werror -std=c11` | `make` with `AM_CFLAGS` |
| **VAL-002** | `make check` runs all unit and integration tests with 0 failures | CI pipeline |
| **VAL-003** | No memory leaks detected under Valgrind for a 1000-cycle system run | `valgrind --leak-check=full` |
| **VAL-004** | All 12 step assignments match the Step Assignment Table in §2.4 of `CLAUDE.md` | Automated table comparison test |
| **VAL-005** | All 4 T-point convergence events fire per cycle with correct step triples | Event counting test |
| **VAL-006** | Priority calculation produces values in [1, 10] for all valid inputs | Fuzz test with random flag/reply combinations |
| **VAL-007** | Process state machine allows only valid transitions (no COMPLETED → ACTIVE) | State transition matrix test |
| **VAL-008** | Sys6 scheduling assigns high-priority (8-10) messages to phase 1, medium (4-7) to phase 2, low (1-3) to phase 3 | Phase assignment unit tests |
| **VAL-009** | Grand cycle boundary event fires at step 60 and resets to step 1 | Cycle boundary integration test |
| **VAL-010** | `libdove9.la` links successfully into a test binary with mock services | Build system integration test |
| **VAL-011** | All public API functions are declared in headers and defined in exactly one `.c` file | Symbol analysis via `nm` |
| **VAL-012** | The C API surface is a 1:1 functional mapping of the TypeScript `dove9/src/` public API | Cross-reference audit |

## 11. Related Specifications / Further Reading

- [CLAUDE.md](../CLAUDE.md) — DeLovEcho monorepo guidance, §2 Triadic Cognitive Loop, §3 Sys6 Operadic Architecture
- [dove9/README.md](../dove9/README.md) — TypeScript Dove9 implementation reference
- [DEEP-TREE-ECHO-ARCHITECTURE.md](../DEEP-TREE-ECHO-ARCHITECTURE.md) — Comprehensive cognitive architecture design
- [IMPLEMENTATION-SUMMARY.md](../IMPLEMENTATION-SUMMARY.md) — Phase 1 implementation status
- [SYS6_IMPLEMENTATION_REPORT.md](../SYS6_IMPLEMENTATION_REPORT.md) — Sys6 operadic implementation report
- [BUILD_ORDER.md](../BUILD_ORDER.md) — Monorepo build dependency order
- [dovecho-core/src/dove9-Makefile.am](../dovecho-core/src/dove9-Makefile.am) — Build system configuration
