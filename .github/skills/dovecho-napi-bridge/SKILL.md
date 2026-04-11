---
name: dovecho-napi-bridge
description: 'Build Node-API (NAPI) bindings bridging the dove9 C kernel to TypeScript cognitive services. USE FOR: creating NAPI wrappers for dove9_system, implementing C vtable callbacks that call into TypeScript LLM/memory/persona services, async cognitive processing across the C↔JS boundary, building native Node.js addons for dovecho-core, wiring dove9_llm_service to actual LLM providers. DO NOT USE FOR: pure C module work (use dovecho-c-module), TypeScript-only orchestrator changes (use dovecho-mail-pipeline), test mocking (use dovecho-test-harness).'
---

# NAPI Bridge: C Kernel ↔ TypeScript Cognition

Build the FFI bridge that connects the dove9 C cognitive kernel to TypeScript cognitive services (LLM, memory, persona). This is the CRITICAL SEAM where compiled speed meets AI flexibility.

## When to Use

- Creating NAPI bindings for `dove9_system_*` functions
- Implementing `dove9_llm_service` vtable callbacks that call TypeScript
- Implementing `dove9_memory_store` vtable callbacks that call TypeScript
- Implementing `dove9_persona_core` vtable callbacks that call TypeScript
- Async processing across C↔JS boundary (threadsafe functions)
- Building the native addon `.node` binary for dovecho-core
- Performance-critical paths where TS orchestrator calls into C kernel

## Architecture: The Bridge Layer

```
TypeScript World                    C World
─────────────────                   ───────────────
LLMService.ts ◄───┐                dove9_llm_service vtable
RAGMemoryStore.ts ◄┤   NAPI        dove9_memory_store vtable
PersonaCore.ts ◄───┤   Bridge      dove9_persona_core vtable
                   │                     │
Orchestrator.ts ───┤◄──────────────dove9_system.h
                   │   napi_*()          │
EventEmitter  ◄────┘◄──────────────dove9_system_on() callbacks
```

## File Structure

```
dovecho-core/
├── src/dove9/                  # C kernel (existing)
├── binding/                    # NEW: NAPI bridge layer
│   ├── dove9-napi.c            # Main NAPI module registration
│   ├── dove9-napi-system.c     # dove9_system_* bindings
│   ├── dove9-napi-kernel.c     # dove9_kernel_* bindings
│   ├── dove9-napi-callbacks.c  # TS→C vtable callback wrappers
│   ├── dove9-napi-async.c      # Threadsafe function helpers
│   └── CMakeLists.txt          # Build as .node addon
├── binding.gyp                 # node-gyp build config (alternative)
└── package.json                # "main": "./binding/dove9.node"
```

## Core Pattern: Wrapping dove9_system

### Module Registration

```c
/* dove9-napi.c */
#include <node_api.h>
#include "dove9-system.h"

/* Constructor: new Dove9System(config) */
static napi_value dove9_napi_system_new(napi_env env, napi_callback_info info)
{
    size_t argc = 1;
    napi_value args[1];
    napi_get_cb_info(env, info, &argc, args, NULL, NULL);

    /* Extract config from JS object */
    struct dove9_system_config config;
    memset(&config, 0, sizeof(config));

    napi_value val;
    /* config.bot_email_address */
    napi_get_named_property(env, args[0], "botEmail", &val);
    size_t len;
    napi_get_value_string_utf8(env, val, config.bot_email_address,
                                sizeof(config.bot_email_address), &len);

    /* Vtables will be set up via separate calls */
    struct dove9_system *sys = dove9_system_create(&config);

    /* Wrap native pointer in JS object */
    napi_value this_obj;
    napi_get_cb_info(env, info, NULL, NULL, &this_obj, NULL);
    napi_wrap(env, this_obj, sys, dove9_napi_system_destructor, NULL, NULL);

    return this_obj;
}

/* Module init */
static napi_value Init(napi_env env, napi_value exports)
{
    napi_value system_class;
    napi_property_descriptor props[] = {
        {"processMail", NULL, dove9_napi_process_mail, NULL, NULL, NULL, napi_default, NULL},
        {"start", NULL, dove9_napi_system_start, NULL, NULL, NULL, napi_default, NULL},
        {"stop", NULL, dove9_napi_system_stop, NULL, NULL, NULL, napi_default, NULL},
        {"on", NULL, dove9_napi_system_on, NULL, NULL, NULL, napi_default, NULL},
    };

    napi_define_class(env, "Dove9System", NAPI_AUTO_LENGTH,
                      dove9_napi_system_new, NULL,
                      sizeof(props)/sizeof(props[0]), props,
                      &system_class);

    napi_set_named_property(env, exports, "Dove9System", system_class);
    return exports;
}

NAPI_MODULE(NODE_GYP_MODULE_NAME, Init)
```

## Critical Pattern: TypeScript → C Vtable Callbacks

The dove9 C kernel calls `llm_service->generate_response()` which must invoke TypeScript.

### Threadsafe Function Pattern

```c
/* dove9-napi-callbacks.c */

struct napi_llm_bridge {
    napi_threadsafe_function tsfn_generate;
    napi_threadsafe_function tsfn_generate_parallel;
};

/* This runs on the C thread (dove9 kernel) */
static int napi_llm_generate(void *user_data,
                              const char *prompt,
                              const char **context_strs,
                              unsigned int context_count,
                              char *out_buf, size_t out_buf_size)
{
    struct napi_llm_bridge *bridge = user_data;

    /* Package args for JS thread */
    struct llm_call_data *data = calloc(1, sizeof(*data));
    data->prompt = strdup(prompt);
    data->out_buf = out_buf;
    data->out_buf_size = out_buf_size;

    /* Signal & wait pattern using condition variable */
    pthread_mutex_init(&data->mutex, NULL);
    pthread_cond_init(&data->cond, NULL);
    data->done = false;

    /* Call into JS thread */
    napi_call_threadsafe_function(bridge->tsfn_generate, data,
                                  napi_tsfn_blocking);

    /* Wait for JS to complete */
    pthread_mutex_lock(&data->mutex);
    while (!data->done)
        pthread_cond_wait(&data->cond, &data->mutex);
    pthread_mutex_unlock(&data->mutex);

    int result = data->result;
    free(data->prompt);
    free(data);
    return result;
}

/* This runs on the JS thread (Node.js event loop) */
static void napi_llm_generate_js(napi_env env, napi_value js_callback,
                                  void *context, void *raw_data)
{
    struct llm_call_data *data = raw_data;

    /* Call the TypeScript LLMService.generateResponse() */
    napi_value prompt_str;
    napi_create_string_utf8(env, data->prompt, NAPI_AUTO_LENGTH, &prompt_str);

    napi_value result;
    napi_call_function(env, /* this */ NULL, js_callback, 1, &prompt_str, &result);

    /* Copy JS string result back to C buffer */
    size_t copied;
    napi_get_value_string_utf8(env, result, data->out_buf,
                                data->out_buf_size, &copied);

    /* Signal C thread to continue */
    pthread_mutex_lock(&data->mutex);
    data->done = true;
    data->result = 0;
    pthread_cond_signal(&data->cond);
    pthread_mutex_unlock(&data->mutex);
}
```

### TypeScript Side: Registering Callbacks

```typescript
// binding/dove9-system.ts
import { Dove9System as NativeDove9System } from './dove9.node';

export class Dove9SystemBridge {
  private native: NativeDove9System;

  constructor(config: Dove9Config) {
    this.native = new NativeDove9System({
      botEmail: config.botEmail,
      milterSocket: config.milterSocket,
      lmtpSocket: config.lmtpSocket,
    });
  }

  /**
   * Register TS cognitive services as C vtable implementations.
   * The C kernel will call these via threadsafe functions.
   */
  registerLLM(llm: LLMService): void {
    this.native.setLLMCallback(async (prompt: string) => {
      return await llm.generateResponse(prompt);
    });
  }

  registerMemory(memory: RAGMemoryStore): void {
    this.native.setMemoryCallbacks({
      storeMemory: (chatId, msgId, sender, text) =>
        memory.storeMemory(chatId, msgId, sender, text),
      retrieveRecent: (count) => memory.retrieveRecent(count),
      retrieveRelevant: (query, count) => memory.retrieveRelevant(query, count),
    });
  }

  registerPersona(persona: PersonaCore): void {
    this.native.setPersonaCallbacks({
      getPersonality: () => persona.getPersonality(),
      getDominantEmotion: () => persona.getDominantEmotion(),
      updateEmotionalState: (keys, values) =>
        persona.updateEmotionalState(keys, values),
    });
  }

  /** Process an email through the C cognitive kernel */
  async processMail(email: EmailMessage): Promise<MessageProcess> {
    return this.native.processMail({
      messageId: email.messageId,
      from: email.from,
      to: email.to,
      subject: email.subject,
      body: email.body,
      timestamp: email.timestamp,
    });
  }
}
```

## CMake Build for NAPI Addon

```cmake
# dovecho-core/binding/CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(dove9_napi C)

# Find Node.js headers
execute_process(
    COMMAND node -p "require('node-addon-api').include_dir"
    OUTPUT_VARIABLE NODE_ADDON_API_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
execute_process(
    COMMAND node -p "require('node-api-headers').include_dir"
    OUTPUT_VARIABLE NODE_API_HEADERS_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

add_library(dove9_napi SHARED
    dove9-napi.c
    dove9-napi-system.c
    dove9-napi-kernel.c
    dove9-napi-callbacks.c
    dove9-napi-async.c
)

target_include_directories(dove9_napi PRIVATE
    ${NODE_ADDON_API_DIR}
    ${NODE_API_HEADERS_DIR}
    ${CMAKE_SOURCE_DIR}/../src/dove9  # dove9 headers
)

target_link_libraries(dove9_napi PRIVATE dove9)
set_target_properties(dove9_napi PROPERTIES
    PREFIX ""
    SUFFIX ".node"
    OUTPUT_NAME "dove9"
)
```

## Async Pattern Decision Tree

```
Is the C function blocking (LLM inference)?
├── YES → Use napi_threadsafe_function + condition variable
│         (napi_llm_generate pattern above)
│
└── NO → Is it a quick struct conversion?
    ├── YES → Synchronous napi_call (dove9_mail_to_process)
    └── NO → Is it event-driven (dove9_system_on)?
        └── YES → Use napi_threadsafe_function (fire-and-forget)
                   C callback → tsfn → JS EventEmitter.emit()
```

## Testing NAPI Bindings

```typescript
// binding/__tests__/dove9-napi.test.ts
import { Dove9SystemBridge } from '../dove9-system';

describe('NAPI Bridge', () => {
  it('processes mail through C kernel', async () => {
    const bridge = new Dove9SystemBridge({ botEmail: 'echo@test.local' });

    // Mock LLM that returns fixed response
    bridge.registerLLM({
      generateResponse: async (prompt) => `ECHO: ${prompt}`,
    });

    const result = await bridge.processMail({
      messageId: '<test@example.com>',
      from: 'user@example.com',
      to: ['echo@test.local'],
      subject: 'Hello',
      body: 'Hi there!',
      timestamp: Date.now(),
    });

    expect(result.state).toBe('PROCESSING');
    expect(result.processId).toBeDefined();
  });
});
```

## Safety Rules

- NEVER hold the GIL/V8 lock while waiting for LLM responses
- Always use `napi_threadsafe_function` for C→JS callbacks
- Set `napi_tsfn_blocking` mode to prevent dropped calls under load
- Validate all string lengths before copying across the boundary (buffer overflow prevention)
- Use `napi_wrap` destructor to guarantee `dove9_system_destroy()` on GC
- Test with `--expose-gc` and `global.gc()` to verify no leaks

## References

- Read [../../dovecho-core/src/dove9/dove9-system.h](../../dovecho-core/src/dove9/dove9-system.h) for system API
- Read [../../dovecho-core/src/dove9/cognitive/dove9-dte-processor.h](../../dovecho-core/src/dove9/cognitive/dove9-dte-processor.h) for vtable definitions
- Read [../../deep-tree-echo-core/src/](../../deep-tree-echo-core/src/) for TypeScript cognitive service implementations
- Node-API docs: https://nodejs.org/api/n-api.html
