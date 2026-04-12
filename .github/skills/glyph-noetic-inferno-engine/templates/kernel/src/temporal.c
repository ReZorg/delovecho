/*
 * temporal.c — Time-Crystal Temporal Hierarchy Scheduler
 *
 * Implements the 12-level time-crystal hierarchy as the kernel's
 * primary cognitive task scheduler. Each level has a biologically-
 * inspired period, and cognitive modules are registered to specific
 * levels for rhythmically synchronized execution.
 *
 * Hierarchy (from /time-crystal-neuron):
 *   L0:  1μs   — Quantum resonance
 *   L1:  8ms   — Protein dynamics (AtomSpace CRUD)
 *   L2:  26ms  — Ion channel gating (Pattern matching)
 *   L3:  52ms  — Membrane dynamics (PLN inference)
 *   L4:  110ms — Axon initial segment (ECAN attention)
 *   L5:  160ms — Dendritic integration (MOSES learning)
 *   L6:  250ms — Synaptic plasticity (Namespace sync)
 *   L7:  330ms — Soma processing (Cluster heartbeat)
 *   L8:  500ms — Network synchronization (Autognosis observe)
 *   L9:  1000ms — Global rhythm (Self-image rebuild)
 *   L10: 60s   — Circadian modulation
 *   L11: 3600s — Homeostatic regulation
 *
 * Copyright (c) 2026 ManusCog Project
 * License: AGPL-3.0
 */

#include "glyph.h"
#include <stdio.h>
#include <string.h>

/* ============================================================================
 * Temporal Level Definitions
 * ============================================================================ */

typedef struct {
    int         id;
    const char  *name;
    const char  *biological_analog;
    long        period_us;
} TemporalLevelDef;

static const TemporalLevelDef LEVEL_DEFS[TC_NUM_LEVELS] = {
    { 0,  "quantum_resonance",     "Quantum Resonance (Ax, Pr-Ch)",   1       },
    { 1,  "protein_dynamics",      "Protein Dynamics (Io-Ch, Li)",    8000    },
    { 2,  "ion_channel_gating",    "Ion Channel Gating",              26000   },
    { 3,  "membrane_dynamics",     "Membrane Dynamics (Me, Ac)",      52000   },
    { 4,  "axon_initial_segment",  "Axon Initial Segment (AIS)",      110000  },
    { 5,  "dendritic_integration", "Dendritic Integration (Ch-Co)",   160000  },
    { 6,  "synaptic_plasticity",   "Synaptic Plasticity (Ca, Fi-lo)", 250000  },
    { 7,  "soma_processing",       "Soma Processing (Rh, Soma)",      330000  },
    { 8,  "network_sync",          "Network Sync (Gl-S, El)",         500000  },
    { 9,  "global_rhythm",         "Global Rhythm (Me-Rh, Sy-c)",     1000000 },
    { 10, "circadian_modulation",  "Circadian Modulation",            60000000},
    { 11, "homeostatic_regulation","Homeostatic Regulation",          3600000000L},
};

/* ============================================================================
 * Initialization
 * ============================================================================ */

int
temporal_init(GlyphEngine *engine)
{
    for (int i = 0; i < TC_NUM_LEVELS; i++) {
        TemporalLevel *level = &engine->temporal[i];
        const TemporalLevelDef *def = &LEVEL_DEFS[i];

        level->id = def->id;
        strncpy(level->name, def->name, sizeof(level->name) - 1);
        strncpy(level->biological_analog, def->biological_analog,
                sizeof(level->biological_analog) - 1);
        level->period_us = def->period_us;
        level->phase = 0;
        level->num_modules = 0;
        level->active = 1;
    }

    engine->global_tick = 0;
    return 0;
}

/* ============================================================================
 * Module Registration
 * ============================================================================ */

int
temporal_register_module(GlyphEngine *engine, CogModule *module, int level)
{
    TemporalLevel *tl;

    if (level < 0 || level >= TC_NUM_LEVELS)
        return -1;

    tl = &engine->temporal[level];
    if (tl->num_modules >= 16)
        return -1;

    tl->modules[tl->num_modules] = module;
    tl->num_modules++;
    module->temporal_level = level;

    return 0;
}

/* ============================================================================
 * Temporal Tick — The Heartbeat of the Cognitive Kernel
 * ============================================================================ */

/*
 * temporal_tick — Advance the global tick counter and fire all temporal
 * levels whose phase has elapsed. This is the fundamental heartbeat
 * of the cognitive kernel, called from the kernel's main scheduler.
 *
 * The tick operates on a hierarchical cascade: faster levels fire more
 * frequently, and each level's modules are executed in registration order.
 * This mirrors the nested temporal structure of biological neural systems.
 */
int
temporal_tick(GlyphEngine *engine)
{
    engine->global_tick++;

    for (int i = 0; i < TC_NUM_LEVELS; i++) {
        TemporalLevel *level = &engine->temporal[i];

        if (!level->active)
            continue;

        level->phase++;

        /* Check if this level should fire based on its period ratio
         * relative to the base tick rate. For the kernel implementation,
         * we use a simplified ratio-based approach where each level
         * fires when its phase counter reaches the period ratio. */
        long ratio = level->period_us / (LEVEL_DEFS[0].period_us > 0 ? 
                     LEVEL_DEFS[0].period_us : 1);
        if (ratio == 0) ratio = 1;

        if (level->phase >= ratio) {
            level->phase = 0;

            /* Fire all modules registered at this level */
            for (int m = 0; m < level->num_modules; m++) {
                CogModule *mod = level->modules[m];
                if (mod && mod->active && mod->tick) {
                    mod->tick(mod, &engine->atomspace);
                    mod->invocations++;
                }
            }
        }
    }

    return 0;
}

/* ============================================================================
 * Glyph Handlers for Temporal Queries
 * ============================================================================ */

int
temporal_get_level_status(GlyphEngine *engine, int level_id, GlyphResult *result)
{
    TemporalLevel *level;

    if (level_id < 0 || level_id >= TC_NUM_LEVELS)
        return glyph_result_set_error(result, 400, "Invalid temporal level");

    level = &engine->temporal[level_id];

    return glyph_result_set_json(result,
        "{"
        "\"level\": %d,"
        "\"name\": \"%s\","
        "\"biological_analog\": \"%s\","
        "\"period_us\": %ld,"
        "\"phase\": %ld,"
        "\"active\": %d,"
        "\"num_modules\": %d,"
        "\"kernel_service_map\": {"
        "  \"L0\": \"AtomSpace CRUD\","
        "  \"L1\": \"Pattern matching\","
        "  \"L2\": \"PLN inference\","
        "  \"L3\": \"ECAN attention\","
        "  \"L4\": \"MOSES learning\","
        "  \"L5\": \"Namespace sync\","
        "  \"L6\": \"Cluster heartbeat\","
        "  \"L7\": \"Autognosis observe\","
        "  \"L8\": \"Self-image rebuild\""
        "}"
        "}",
        level->id, level->name, level->biological_analog,
        level->period_us, level->phase, level->active,
        level->num_modules);
}

int
temporal_get_hierarchy_status(GlyphEngine *engine, GlyphResult *result,
                              int argc, char **argv)
{
    char *buf = result->data;
    int offset = 0;

    offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset,
        "{\"hierarchy\": \"time-crystal-12-level\","
        "\"global_tick\": %ld,"
        "\"levels\": [",
        engine->global_tick);

    for (int i = 0; i < TC_NUM_LEVELS; i++) {
        TemporalLevel *level = &engine->temporal[i];
        offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset,
            "%s{"
            "\"id\": %d,"
            "\"name\": \"%s\","
            "\"biological_analog\": \"%s\","
            "\"period_us\": %ld,"
            "\"phase\": %ld,"
            "\"active\": %d,"
            "\"num_modules\": %d"
            "}",
            (i > 0) ? ", " : "",
            level->id, level->name, level->biological_analog,
            level->period_us, level->phase, level->active,
            level->num_modules);
    }

    offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset, "]}");
    result->data_len = offset;
    result->error = 0;
    return 0;
}
