---
name: dovecho-c-module
description: 'Build Dovecot C plugin modules that hook dove9 cognitive kernel into the live mail pipeline. USE FOR: creating Dovecot plugins, LMTP hooks, mail storage event handlers, milter filters, imap-notify cognitive triggers, writing C code that integrates dove9-system.h with Dovecot lib-storage and mail-user APIs. DO NOT USE FOR: TypeScript orchestrator work (use dovecho-mail-pipeline), NAPI bindings (use dovecho-napi-bridge), test harness (use dovecho-test-harness).'
---

# Dovecot C Module Development

Build C plugin modules that wire the dove9 cognitive kernel into Dovecot's live mail processing pipeline. This is the LOW-LEVEL FUSION LAYER where "mail server" meets "thinking machine."

## When to Use

- Creating a new Dovecot plugin that intercepts mail events
- Hooking dove9 cognitive processing into LMTP delivery
- Adding mail storage event handlers (new mail → cognitive process)
- Building milter filters that use cognitive context for filtering
- Wiring `dove9_system_process_mail()` into actual Dovecot mail flow
- Implementing the `dove9_llm_service` / `dove9_memory_store` vtable stubs for in-process C usage

## Architecture: Where Plugins Live

```
dovecot-core/src/
├── plugins/
│   └── dove9-cognitive/           ← NEW: Our cognitive plugin
│       ├── dove9-cognitive-plugin.c    Main plugin entry
│       ├── dove9-mail-hook.c           mail_user notify hooks
│       ├── dove9-lmtp-hook.c           LMTP local delivery hook
│       └── Makefile.am / CMakeLists.txt
├── lib-storage/                   Dovecot mail storage (we hook into this)
├── lmtp/                          LMTP server (we extend this)
└── imap/                          IMAP server (we add NOTIFY cognitive events)
```

## Dovecot Plugin Skeleton

Every Dovecot plugin follows this pattern:

```c
#include "lib.h"
#include "module-dir.h"
#include "mail-user.h"
#include "mail-storage-private.h"
#include "notify-plugin.h"

/* dove9 kernel */
#include "dove9-system.h"

static MODULE_CONTEXT_DEFINE_INIT(dove9_mail_user_module,
                                  &mail_user_module_register);

struct dove9_mail_user {
    union mail_user_module_context module_ctx;
    struct dove9_system *system;
};

/* Called when mail is saved to a mailbox */
static void dove9_mail_save(void *txn, struct mail *mail)
{
    struct dove9_mail_user *duser =
        DOVE9_MAIL_USER_CONTEXT(mail->box->storage->user);

    /* Extract envelope from Dovecot mail object */
    struct dove9_mail_message dmsg;
    memset(&dmsg, 0, sizeof(dmsg));

    const char *msgid;
    if (mail_get_first_header(mail, "Message-ID", &msgid) > 0)
        i_strlcpy(dmsg.message_id, msgid, sizeof(dmsg.message_id));

    /* ... extract from, to, subject, body ... */

    /* Fire cognitive processing */
    struct dove9_message_process *proc =
        dove9_system_process_mail(duser->system, &dmsg);

    if (proc != NULL) {
        i_info("dove9: cognitive process %s started for message %s",
               proc->id, dmsg.message_id);
    }
}

/* Plugin init — called by Dovecot module loader */
void dove9_cognitive_plugin_init(struct module *module)
{
    /* Register notify callbacks */
    /* Hook into mail_user_created */
    /* Initialize dove9_system */
}

void dove9_cognitive_plugin_deinit(void)
{
    /* Shutdown dove9_system */
}

const char dove9_cognitive_plugin_version[] = DOVECOT_ABI_VERSION;
```

## Critical Dovecot APIs to Use

### Mail User Lifecycle

```c
/* Hook into user session creation (IMAP login, LMTP delivery) */
static void dove9_mail_user_created(struct mail_user *user)
{
    struct dove9_mail_user *duser = p_new(user->pool, struct dove9_mail_user, 1);
    MODULE_CONTEXT_SET(user, dove9_mail_user_module, duser);

    /* Create per-user dove9 system instance */
    struct dove9_system_config config;
    /* ... populate from user's dovecot settings ... */
    duser->system = dove9_system_create(&config);
    dove9_system_start(duser->system);
}
```

### Mail Storage Notify Hooks

```c
/* These are the key integration points: */
static const struct notify_vfuncs dove9_vfuncs = {
    .mail_save      = dove9_mail_save,       /* New mail delivered */
    .mail_copy       = dove9_mail_copy,       /* Mail copied between mailboxes */
    .mail_expunge    = dove9_mail_expunge,    /* Mail deleted */
    .mail_update_flags = dove9_mail_flags,    /* Flags changed → state transition */
    .mailbox_create  = dove9_mailbox_create,  /* New mailbox → new process queue */
    .mailbox_delete  = dove9_mailbox_delete,  /* Mailbox removed */
};
```

### LMTP Delivery Hook

```c
/* Intercept at LMTP DATA phase for pre-delivery cognitive analysis */
static int dove9_lmtp_data_hook(struct client *client,
                                 struct smtp_server_cmd_ctx *cmd,
                                 struct istream *data_input)
{
    /* Read message from data_input */
    /* Run dove9_mail_calculate_priority() */
    /* Optionally classify into mailbox via cognitive context */
    /* Continue normal LMTP delivery */
    return 0;
}
```

## Build Integration

### CMake (recommended for dove9 standalone testing)

```cmake
# In dovecho-core/src/plugins/dove9-cognitive/CMakeLists.txt
add_library(dove9_cognitive_plugin MODULE
    dove9-cognitive-plugin.c
    dove9-mail-hook.c
    dove9-lmtp-hook.c
)
target_link_libraries(dove9_cognitive_plugin PRIVATE dove9)
target_include_directories(dove9_cognitive_plugin PRIVATE
    ${CMAKE_SOURCE_DIR}/../../lib        # Dovecot lib/
    ${CMAKE_SOURCE_DIR}/../../lib-storage # Dovecot storage
)
```

### Autotools (for integration with dovecot-core build)

```makefile
# In dovecho-core/src/plugins/dove9-cognitive/Makefile.am
dovecot_moduledir = $(moduledir)
dovecot_module_LTLIBRARIES = lib20_dove9_cognitive_plugin.la

lib20_dove9_cognitive_plugin_la_SOURCES = \
    dove9-cognitive-plugin.c \
    dove9-mail-hook.c \
    dove9-lmtp-hook.c
lib20_dove9_cognitive_plugin_la_LIBADD = \
    $(top_builddir)/src/dove9/libdove9.la
lib20_dove9_cognitive_plugin_la_LDFLAGS = -module -avoid-version
```

## Cognitive Event Flow Checklist

When implementing a new mail event handler:

1. Extract envelope data from Dovecot `struct mail` into `dove9_mail_message`
2. Call `dove9_mail_calculate_priority()` for scheduling
3. Call `dove9_system_process_mail()` to create cognitive process
4. Register event handler on `dove9_system_on()` for response events
5. On `DOVE9_SYS_RESPONSE_READY`: convert back via `dove9_process_to_mail()`
6. Deliver response through Dovecot's submission API or external SMTP

## Mailbox ↔ Process State Mapping Reference

| Mailbox | Process State | Trigger |
|---------|--------------|---------|
| INBOX | PENDING | New mail arrives |
| INBOX.Processing | PROCESSING | Cognitive engine working |
| Drafts | SUSPENDED | Awaiting user input |
| Sent | COMPLETED | Response delivered |
| Trash | TERMINATED | Discarded |
| Archive | COMPLETED | Long-term storage |

## Safety Rules

- NEVER block Dovecot's mail delivery path with synchronous LLM calls
- Use `dove9_system_on()` async event pattern for cognitive responses
- Keep plugin init/deinit idempotent (Dovecot reloads modules)
- Validate all mail headers before passing to dove9 (injection prevention)
- Set `DOVE9_MAX_BODY_LEN` limits to prevent OOM on large attachments
- Log via Dovecot's `i_info()`/`i_error()` not `printf()`/`console.log()`

## References

- Read [../../dovecho-core/src/dove9/dove9-system.h](../../dovecho-core/src/dove9/dove9-system.h) for the top-level C API
- Read [../../dovecho-core/src/dove9/integration/dove9-mail-protocol-bridge.h](../../dovecho-core/src/dove9/integration/dove9-mail-protocol-bridge.h) for mail↔process conversion
- Read [../../dovecot-core/src/plugins/](../../dovecot-core/src/plugins/) for existing Dovecot plugin examples
