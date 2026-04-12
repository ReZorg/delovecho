/*
 * glyph.c — Glyph-Noetic Engine: Core Kernel Implementation
 *
 * This file implements the core cognitive engine that runs as a native
 * Inferno kernel service. It provides:
 *   - Engine initialization and shutdown
 *   - Noetic sentence parsing and dispatch
 *   - Glyph map management (static dispatch table)
 *   - Result formatting (JSON output)
 *   - Integration with temporal scheduler, topology, and AtomSpace
 *
 * The engine is initialized once at kernel boot and persists for the
 * lifetime of the system. All cognitive state is kernel-resident.
 *
 * Copyright (c) 2026 ManusCog Project
 * License: AGPL-3.0
 */

#include "glyph.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <time.h>

/* ============================================================================
 * Global Engine Instance
 * ============================================================================ */

static GlyphEngine *g_engine = NULL;

/* ============================================================================
 * Glyph Result Management
 * ============================================================================ */

GlyphResult *
glyph_result_new(void)
{
    GlyphResult *r = (GlyphResult *)calloc(1, sizeof(GlyphResult));
    if (r == NULL)
        return NULL;
    r->data = (char *)calloc(1, GLYPH_MAX_RESPONSE);
    if (r->data == NULL) {
        free(r);
        return NULL;
    }
    r->data_len = 0;
    r->error = 0;
    return r;
}

void
glyph_result_free(GlyphResult *result)
{
    if (result) {
        if (result->data)
            free(result->data);
        free(result);
    }
}

int
glyph_result_set_json(GlyphResult *result, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    result->data_len = vsnprintf(result->data, GLYPH_MAX_RESPONSE, fmt, ap);
    va_end(ap);
    result->error = 0;
    return 0;
}

int
glyph_result_set_error(GlyphResult *result, int code, const char *msg)
{
    result->error = code;
    snprintf(result->error_msg, sizeof(result->error_msg), "%s", msg);
    result->data_len = snprintf(result->data, GLYPH_MAX_RESPONSE,
        "{\"error\": %d, \"message\": \"%s\"}", code, msg);
    return code;
}

/* ============================================================================
 * Noetic Sentence Parser
 * ============================================================================ */

/*
 * glyph_parse_sentence — Parse a raw noetic sentence string into a
 * structured GlyphSentence. The parser handles:
 *   - Bracketed glyph identifiers: [C:PLN], [T~g], [T:ASSEMBLY]
 *   - Operator suffixes: ?, !, ->
 *   - Additional parameters after the primary glyph
 *
 * Examples:
 *   "[C:PLN]?"           → primary="C:PLN", op='?'
 *   "[T:ASSEMBLY]?"      → primary="T:ASSEMBLY", op='?'
 *   "[T~g] -> [C:PLN]"   → primary="T~g", op='-', argv[0]="C:PLN"
 *   "pause [C:PATTERN]!" → primary="C:PATTERN", op='!'
 */
int
glyph_parse_sentence(const char *raw, GlyphSentence *sentence)
{
    const char *p;
    char *dst;
    int in_bracket = 0;
    int token_count = 0;
    char tokens[GLYPH_MAX_PARAMS + 1][GLYPH_MAX_ID_LEN];
    char ops[GLYPH_MAX_PARAMS + 1];
    int num_tokens = 0;

    if (raw == NULL || sentence == NULL)
        return -1;

    memset(sentence, 0, sizeof(GlyphSentence));
    strncpy(sentence->raw, raw, GLYPH_MAX_SENTENCE - 1);

    /* Tokenize: extract bracketed glyphs and their operators */
    p = raw;
    while (*p && num_tokens < GLYPH_MAX_PARAMS + 1) {
        /* Skip whitespace */
        while (*p == ' ' || *p == '\t' || *p == '\n')
            p++;
        if (*p == '\0')
            break;

        /* Skip keywords like "pause", "explain", "compose" */
        if (*p != '[' && *p != '-' && *p != '|') {
            /* Advance past the keyword */
            while (*p && *p != ' ' && *p != '[')
                p++;
            continue;
        }

        /* Skip flow operator '->' */
        if (*p == '-' && *(p + 1) == '>') {
            p += 2;
            continue;
        }

        /* Skip pipe operator */
        if (*p == '|') {
            p++;
            continue;
        }

        /* Parse bracketed glyph */
        if (*p == '[') {
            p++;  /* skip '[' */
            dst = tokens[num_tokens];
            ops[num_tokens] = '\0';
            while (*p && *p != ']') {
                *dst++ = *p++;
            }
            *dst = '\0';
            if (*p == ']')
                p++;  /* skip ']' */
            
            /* Check for trailing operator */
            if (*p == '?' || *p == '!') {
                ops[num_tokens] = *p;
                p++;
            }
            num_tokens++;
        }
    }

    if (num_tokens == 0)
        return -1;

    /* Primary glyph is the first token */
    strncpy(sentence->primary_glyph, tokens[0], GLYPH_MAX_ID_LEN - 1);
    sentence->op = ops[0] ? ops[0] : '?';  /* Default to query */

    /* Additional tokens become arguments */
    sentence->argc = 0;
    for (int i = 1; i < num_tokens && sentence->argc < GLYPH_MAX_PARAMS; i++) {
        sentence->argv[sentence->argc] = strdup(tokens[i]);
        sentence->argc++;
    }

    return 0;
}

/* ============================================================================
 * Glyph Map Management
 * ============================================================================ */

int
glyph_register(GlyphEngine *engine, const GlyphAction *action)
{
    if (engine->num_glyphs >= GLYPH_MAP_SIZE)
        return -1;
    memcpy(&engine->glyph_map[engine->num_glyphs], action, sizeof(GlyphAction));
    engine->num_glyphs++;
    return 0;
}

GlyphAction *
glyph_lookup(GlyphEngine *engine, const char *glyph_id)
{
    for (int i = 0; i < engine->num_glyphs; i++) {
        if (strcmp(engine->glyph_map[i].id, glyph_id) == 0)
            return &engine->glyph_map[i];
    }
    return NULL;
}

/* ============================================================================
 * Glyph Dispatch
 * ============================================================================ */

int
glyph_dispatch(GlyphEngine *engine, GlyphSentence *sentence, GlyphResult *result)
{
    GlyphAction *action;

    if (engine == NULL || sentence == NULL || result == NULL)
        return -1;

    engine->total_sentences++;

    /* Look up the glyph in the dispatch table */
    action = glyph_lookup(engine, sentence->primary_glyph);
    if (action == NULL) {
        engine->total_errors++;
        return glyph_result_set_error(result, 404,
            "Glyph not found in kernel map");
    }

    /* Set result metadata */
    strncpy(result->glyph_id, sentence->primary_glyph, GLYPH_MAX_ID_LEN - 1);
    result->op = sentence->op;

    /* Dispatch to the handler */
    if (action->handler == NULL) {
        engine->total_errors++;
        return glyph_result_set_error(result, 501,
            "Glyph handler not implemented");
    }

    return action->handler(engine, result, sentence->argc, sentence->argv);
}

/* ============================================================================
 * Built-in Glyph Handlers
 * ============================================================================ */

/*
 * handler_engine_status — Returns the overall engine status.
 * Glyph: [K:STATUS]?
 */
static int
handler_engine_status(GlyphEngine *engine, GlyphResult *result,
                      int argc, char **argv)
{
    return glyph_result_set_json(result,
        "{"
        "\"engine\": \"glyph-noetic-inferno-kernel\","
        "\"version\": \"%s\","
        "\"initialized\": %d,"
        "\"uptime_ticks\": %ld,"
        "\"total_sentences\": %ld,"
        "\"total_errors\": %ld,"
        "\"num_glyphs\": %d,"
        "\"num_modules\": %d,"
        "\"atomspace_atoms\": %d,"
        "\"atomspace_links\": %d,"
        "\"topology_healthy\": %d,"
        "\"autognosis_awareness\": %.4f,"
        "\"autognosis_cycles\": %ld"
        "}",
        engine->version,
        engine->initialized,
        engine->global_tick,
        engine->total_sentences,
        engine->total_errors,
        engine->num_glyphs,
        engine->num_modules,
        engine->atomspace.num_atoms,
        engine->atomspace.num_links,
        engine->topology.all_constraints_ok,
        engine->autognosis.awareness_score,
        engine->autognosis.cycle_count);
}

/*
 * handler_glyph_list — Lists all registered glyphs.
 * Glyph: [K:GLYPHS]?
 */
static int
handler_glyph_list(GlyphEngine *engine, GlyphResult *result,
                   int argc, char **argv)
{
    char *buf = result->data;
    int offset = 0;
    static const char *cat_names[] = {
        "unknown", "temporal", "cognitive", "structural",
        "noetic", "protocol", "topology", "kernel"
    };

    offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset,
        "{\"num_glyphs\": %d, \"glyphs\": [", engine->num_glyphs);

    for (int i = 0; i < engine->num_glyphs; i++) {
        GlyphAction *a = &engine->glyph_map[i];
        offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset,
            "%s{\"id\": \"[%s]\", \"category\": \"%s\", "
            "\"description\": \"%s\", \"temporal_level\": %d}",
            (i > 0) ? ", " : "",
            a->id,
            cat_names[a->category < 8 ? a->category : 0],
            a->description,
            a->temporal_level);
    }

    offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset, "]}");
    result->data_len = offset;
    result->error = 0;
    return 0;
}

/*
 * handler_promises — Returns kernel promise validation status.
 * Glyph: [K:PROMISES]?
 */
static int
handler_promises(GlyphEngine *engine, GlyphResult *result,
                 int argc, char **argv)
{
    return promises_get_status(engine, result);
}

/* ============================================================================
 * Default Glyph Registration
 * ============================================================================ */

static void
register_default_glyphs(GlyphEngine *engine)
{
    GlyphAction actions[] = {
        /* ---- Temporal Glyphs (Blue) ---- */
        {"T-HIERARCHY", GLYPH_CAT_TEMPORAL, "Complete time crystal hierarchy",
            (GlyphHandler)temporal_get_hierarchy_status, -1},
        {"T~q", GLYPH_CAT_TEMPORAL, "Quantum resonance (1us)",
            NULL, TC_LEVEL_QUANTUM},
        {"T~p", GLYPH_CAT_TEMPORAL, "Protein dynamics (8ms)",
            NULL, TC_LEVEL_PROTEIN},
        {"T~d", GLYPH_CAT_TEMPORAL, "Dendritic integration (160ms)",
            NULL, TC_LEVEL_DENDRITIC},
        {"T~g", GLYPH_CAT_TEMPORAL, "Global rhythm (1s)",
            NULL, TC_LEVEL_GLOBAL},
        {"T~h", GLYPH_CAT_TEMPORAL, "Homeostatic regulation (1hr)",
            NULL, TC_LEVEL_HOMEOSTATIC},

        /* ---- Cognitive Glyphs (Purple) ---- */
        {"C:PLN", GLYPH_CAT_COGNITIVE, "Probabilistic Logic Networks",
            NULL, TC_LEVEL_MEMBRANE},
        {"C:MOSES", GLYPH_CAT_COGNITIVE, "MOSES program evolution",
            NULL, TC_LEVEL_DENDRITIC},
        {"C:PATTERN", GLYPH_CAT_COGNITIVE, "Pattern matching engine",
            NULL, TC_LEVEL_ION_CHANNEL},
        {"C:ATTN", GLYPH_CAT_COGNITIVE, "Attention allocation (ECAN)",
            NULL, TC_LEVEL_AIS},

        /* ---- Structural Glyphs (Green) ---- */
        {"S:ATOMSPACE", GLYPH_CAT_STRUCTURAL, "AtomSpace hypergraph",
            (GlyphHandler)atomspace_get_status, TC_LEVEL_PROTEIN},
        {"S:atom", GLYPH_CAT_STRUCTURAL, "Single atom query",
            NULL, TC_LEVEL_PROTEIN},
        {"S:link", GLYPH_CAT_STRUCTURAL, "Link query",
            NULL, TC_LEVEL_PROTEIN},
        {"S:H-ATTN", GLYPH_CAT_STRUCTURAL, "Hypergraph attention",
            NULL, TC_LEVEL_AIS},

        /* ---- Noetic Glyphs (Orange) ---- */
        {"N:TV", GLYPH_CAT_NOETIC, "Truth value query",
            NULL, -1},
        {"N:AV", GLYPH_CAT_NOETIC, "Attention value query",
            NULL, -1},
        {"N:DECISION", GLYPH_CAT_NOETIC, "Decision explanation",
            (GlyphHandler)autognosis_get_status, TC_LEVEL_GLOBAL},
        {"N:ANOMALY", GLYPH_CAT_NOETIC, "Anomaly detection",
            NULL, TC_LEVEL_NETWORK},

        /* ---- Protocol Glyphs (Cyan) — from /plan9-file-server ---- */
        {"P:FS", GLYPH_CAT_PROTOCOL, "Plan 9 file server",
            NULL, -1},
        {"P:CPU", GLYPH_CAT_PROTOCOL, "Plan 9 CPU servers",
            (GlyphHandler)topo_list_components, -1},
        {"P:NS", GLYPH_CAT_PROTOCOL, "Cognitive namespace map",
            (GlyphHandler)topo_get_namespace_map, -1},
        {"P:AUTH", GLYPH_CAT_PROTOCOL, "Authentication server",
            NULL, -1},

        /* ---- Topology Glyphs (Cyan) — from /p9fstyx-topology ---- */
        {"T:ASSEMBLY", GLYPH_CAT_TOPOLOGY, "Topological assembly status",
            (GlyphHandler)topo_get_status, -1},
        {"T:BETA0", GLYPH_CAT_TOPOLOGY, "Betti-0 (connected components)",
            (GlyphHandler)topo_get_status, -1},
        {"T:BETA1", GLYPH_CAT_TOPOLOGY, "Betti-1 (redundant paths)",
            (GlyphHandler)topo_get_status, -1},
        {"T:SIMPLEX", GLYPH_CAT_TOPOLOGY, "Simplicial complex",
            (GlyphHandler)topo_get_status, -1},
        {"T:PERSIST", GLYPH_CAT_TOPOLOGY, "Persistence diagram",
            (GlyphHandler)topo_get_persistence, -1},

        /* ---- Kernel Glyphs (Red) — Inferno-specific ---- */
        {"K:STATUS", GLYPH_CAT_KERNEL, "Engine status",
            handler_engine_status, -1},
        {"K:GLYPHS", GLYPH_CAT_KERNEL, "List all registered glyphs",
            handler_glyph_list, -1},
        {"K:PROMISES", GLYPH_CAT_KERNEL, "Kernel promise status",
            handler_promises, -1},
    };

    int n = sizeof(actions) / sizeof(actions[0]);
    for (int i = 0; i < n; i++) {
        glyph_register(engine, &actions[i]);
    }
}

/* ============================================================================
 * Engine Lifecycle
 * ============================================================================ */

GlyphEngine *
glyph_engine_init(void)
{
    GlyphEngine *engine;

    if (g_engine != NULL)
        return g_engine;  /* Already initialized */

    engine = (GlyphEngine *)calloc(1, sizeof(GlyphEngine));
    if (engine == NULL)
        return NULL;

    strncpy(engine->version, GLYPH_VERSION, sizeof(engine->version) - 1);
    engine->boot_time = time(NULL);

    /* Initialize subsystems */
    printf("[glyph] Initializing Glyph-Noetic Inferno Kernel v%s\n",
           GLYPH_VERSION);

    /* 1. Register default glyphs */
    register_default_glyphs(engine);
    printf("[glyph]   Registered %d glyphs in dispatch table\n",
           engine->num_glyphs);

    /* 2. Initialize temporal hierarchy */
    temporal_init(engine);
    printf("[glyph]   Temporal hierarchy initialized (%d levels)\n",
           TC_NUM_LEVELS);

    /* 3. Initialize AtomSpace */
    atomspace_init(&engine->atomspace, 4096);
    printf("[glyph]   AtomSpace initialized (capacity=%d)\n",
           engine->atomspace.capacity);

    /* 4. Initialize topology */
    topo_init(engine, NULL);
    printf("[glyph]   Topology module initialized (%d components)\n",
           engine->topology.num_components);

    /* 5. Validate kernel promises */
    promises_validate_all(engine);
    printf("[glyph]   Kernel promises validated\n");

    /* 6. Initialize autognosis */
    engine->autognosis.awareness_score = 0.0;
    engine->autognosis.convergence_factor = 1.0;
    engine->autognosis.cycle_count = 0;
    snprintf(engine->autognosis.last_reflection,
             sizeof(engine->autognosis.last_reflection),
             "Kernel initialized. Awaiting first cognitive cycle.");

    engine->initialized = 1;
    g_engine = engine;

    printf("[glyph] Glyph-Noetic Inferno Kernel READY\n");
    printf("[glyph]   /dev/glyph device available\n");
    printf("[glyph]   /n/glyph namespace mounted\n");

    return engine;
}

void
glyph_engine_shutdown(GlyphEngine *engine)
{
    if (engine == NULL)
        return;

    printf("[glyph] Shutting down Glyph-Noetic Inferno Kernel\n");

    atomspace_destroy(&engine->atomspace);

    /* Free sentence argv allocations */
    engine->initialized = 0;
    g_engine = NULL;
    free(engine);

    printf("[glyph] Kernel shutdown complete\n");
}

/* ============================================================================
 * Global Engine Accessor
 * ============================================================================ */

GlyphEngine *
glyph_engine_get(void)
{
    return g_engine;
}
