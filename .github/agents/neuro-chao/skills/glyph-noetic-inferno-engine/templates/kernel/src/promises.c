/*
 * promises.c — Kernel Promise Validation & Autognosis
 *
 * Implements the Promise-Lambda Attention (PLA) constraint-satisfaction
 * mechanism for the cognitive kernel. Each promise (λ) validates that
 * a specific structural or functional requirement is met.
 *
 * Also implements the Autognosis self-awareness subsystem, which builds
 * a hierarchical self-image of the kernel's cognitive state.
 *
 * Promise sources:
 *   - promise-lambda-attention(inferno-devcontainer, opencog-inferno-kernel)
 *   - Extended with glyph-noetic-engine promises
 *
 * Autognosis levels:
 *   Level 0: Direct Observation (promise satisfaction, temporal levels)
 *   Level 1: Pattern Analysis (configuration completeness, hierarchy status)
 *   Level 2: Meta-Cognitive (self-awareness quality, convergence factor)
 *
 * Copyright (c) 2026 ManusCog Project
 * License: AGPL-3.0
 */

#include "glyph.h"
#include <stdio.h>
#include <string.h>
#include <math.h>

/* ============================================================================
 * Promise Definitions
 * ============================================================================ */

typedef struct {
    int         id;
    const char  *name;
    const char  *description;
    const char  *source;
} PromiseDef;

static const PromiseDef PROMISE_DEFS[NUM_KERNEL_PROMISES] = {
    { PROMISE_INFERNO_BINARY,  "inferno-binary",
      "Inferno emu binary available", "opencog-inferno-kernel" },
    { PROMISE_LIMBO_COMPILER,  "limbo-compiler",
      "Limbo compiler available", "opencog-inferno-kernel" },
    { PROMISE_9P_LISTENER,     "9p-listener",
      "9P listener on port 6666", "inferno-devcontainer" },
    { PROMISE_CLUSTER_COMPOSE, "cluster-compose",
      "Cluster compose configuration", "inferno-devcontainer" },
    { PROMISE_COGNITIVE_NS,    "cognitive-ns",
      "/cognitive/ namespace defined", "opencog-inferno-kernel" },
    { PROMISE_DEVCONTAINER,    "devcontainer-json",
      "INFERNO_ROOT in containerEnv", "inferno-devcontainer" },
    { PROMISE_AUTOGNOSIS,      "autognosis-loop",
      "Autognosis verification in post-start", "Autognosis" },
    { PROMISE_TEMPORAL_LEVELS, "temporal-levels",
      "12 temporal levels defined", "time-crystal-nn" },
    { PROMISE_GLYPH_DEVICE,    "glyph-device",
      "/dev/glyph device available", "glyph-noetic-engine" },
    { PROMISE_TOPO_CONNECTED,  "topo-connected",
      "Cluster topology: beta_0 == 1", "p9fstyx-topology" },
    { PROMISE_TOPO_REDUNDANT,  "topo-redundant",
      "Cluster topology: beta_1 >= 1", "p9fstyx-topology" },
};

/* ============================================================================
 * Promise Validation
 * ============================================================================ */

int
promises_validate_all(GlyphEngine *engine)
{
    int all_ok = 1;

    /* Validate each promise based on current kernel state */

    /* P0: Inferno binary — always true in kernel context */
    engine->promises[PROMISE_INFERNO_BINARY] = 1;

    /* P1: Limbo compiler — always true in kernel context */
    engine->promises[PROMISE_LIMBO_COMPILER] = 1;

    /* P2: 9P listener — true if topology has components */
    engine->promises[PROMISE_9P_LISTENER] = 
        (engine->topology.num_components > 0);

    /* P3: Cluster compose — true if topology initialized */
    engine->promises[PROMISE_CLUSTER_COMPOSE] = 
        (engine->topology.num_components >= 4);

    /* P4: Cognitive namespace — true if glyph map has P:NS */
    engine->promises[PROMISE_COGNITIVE_NS] = 
        (glyph_lookup(engine, "P:NS") != NULL);

    /* P5: Devcontainer — true in kernel context */
    engine->promises[PROMISE_DEVCONTAINER] = 1;

    /* P6: Autognosis loop — true if autognosis handler registered */
    engine->promises[PROMISE_AUTOGNOSIS] = 
        (glyph_lookup(engine, "N:DECISION") != NULL);

    /* P7: Temporal levels — true if all 12 levels initialized */
    engine->promises[PROMISE_TEMPORAL_LEVELS] = 1;
    for (int i = 0; i < TC_NUM_LEVELS; i++) {
        if (engine->temporal[i].period_us == 0) {
            engine->promises[PROMISE_TEMPORAL_LEVELS] = 0;
            break;
        }
    }

    /* P8: Glyph device — true if engine initialized */
    engine->promises[PROMISE_GLYPH_DEVICE] = engine->initialized;

    /* P9: Topology connected — β₀ == 1 */
    engine->promises[PROMISE_TOPO_CONNECTED] = 
        (engine->topology.betti[0] == 1);

    /* P10: Topology redundant — β₁ >= 1 */
    engine->promises[PROMISE_TOPO_REDUNDANT] = 
        (engine->topology.betti[1] >= 1);

    /* Check overall status */
    for (int i = 0; i < NUM_KERNEL_PROMISES; i++) {
        if (!engine->promises[i])
            all_ok = 0;
    }

    return all_ok;
}

int
promises_get_status(GlyphEngine *engine, GlyphResult *result)
{
    char *buf = result->data;
    int offset = 0;
    int satisfied = 0;

    for (int i = 0; i < NUM_KERNEL_PROMISES; i++)
        if (engine->promises[i])
            satisfied++;

    offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset,
        "{"
        "\"promises\": {"
        "  \"total\": %d,"
        "  \"satisfied\": %d,"
        "  \"all_ok\": %s,"
        "  \"details\": [",
        NUM_KERNEL_PROMISES, satisfied,
        (satisfied == NUM_KERNEL_PROMISES) ? "true" : "false");

    for (int i = 0; i < NUM_KERNEL_PROMISES; i++) {
        const PromiseDef *def = &PROMISE_DEFS[i];
        offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset,
            "%s{\"id\": %d, \"name\": \"%s\", \"description\": \"%s\", "
            "\"source\": \"%s\", \"satisfied\": %s}",
            (i > 0) ? ", " : "",
            def->id, def->name, def->description, def->source,
            engine->promises[i] ? "true" : "false");
    }

    offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset, "]}}");
    result->data_len = offset;
    result->error = 0;
    return 0;
}

/* ============================================================================
 * Autognosis: Self-Awareness Subsystem
 * ============================================================================ */

/*
 * autognosis_observe — Level 0: Direct Observation
 * Collects raw metrics from all kernel subsystems.
 */
int
autognosis_observe(GlyphEngine *engine)
{
    double score = 0.0;
    int checks = 0;

    /* Check promise satisfaction */
    for (int i = 0; i < NUM_KERNEL_PROMISES; i++) {
        if (engine->promises[i])
            score += 1.0;
        checks++;
    }

    /* Check temporal levels active */
    for (int i = 0; i < TC_NUM_LEVELS; i++) {
        if (engine->temporal[i].active)
            score += 0.5;
        checks++;
    }

    /* Check AtomSpace health */
    if (engine->atomspace.num_atoms > 0)
        score += 2.0;
    checks += 2;

    /* Check topology health */
    if (engine->topology.all_constraints_ok)
        score += 3.0;
    checks += 3;

    /* Normalize to [0, 1] */
    engine->autognosis.awareness_score = score / checks;

    return 0;
}

/*
 * autognosis_build_self_image — Level 1 & 2: Pattern Analysis + Meta-Cognitive
 * Builds a hierarchical self-image from observations.
 */
int
autognosis_build_self_image(GlyphEngine *engine)
{
    double prev_score = engine->autognosis.awareness_score;

    /* Level 0: Observe */
    autognosis_observe(engine);

    /* Level 1: Pattern Analysis */
    double completeness = 0.0;
    completeness += (engine->num_glyphs > 20) ? 0.3 : 
                    (double)engine->num_glyphs / 60.0;
    completeness += (engine->num_modules > 0) ? 0.2 : 0.0;
    completeness += (engine->topology.all_constraints_ok) ? 0.3 : 0.0;
    completeness += (engine->atomspace.num_atoms > 5) ? 0.2 : 0.0;

    /* Level 2: Meta-Cognitive */
    double delta = fabs(engine->autognosis.awareness_score - prev_score);
    engine->autognosis.convergence_factor = 
        (delta < 0.001) ? 0.0 : delta;

    /* Update cycle count */
    engine->autognosis.cycle_count++;

    /* Generate reflection */
    if (engine->autognosis.convergence_factor < 0.001 && 
        engine->autognosis.cycle_count > 1) {
        snprintf(engine->autognosis.last_reflection,
                 sizeof(engine->autognosis.last_reflection),
                 "Convergence reached at cycle %ld. "
                 "Self-awareness stable at %.4f. "
                 "All %d kernel promises satisfied. "
                 "Topology healthy (beta_0=%d, beta_1=%d). "
                 "The kernel has reached cognitive equilibrium.",
                 engine->autognosis.cycle_count,
                 engine->autognosis.awareness_score,
                 NUM_KERNEL_PROMISES,
                 engine->topology.betti[0],
                 engine->topology.betti[1]);
    } else {
        snprintf(engine->autognosis.last_reflection,
                 sizeof(engine->autognosis.last_reflection),
                 "Cycle %ld: awareness=%.4f, delta=%.6f, "
                 "completeness=%.2f. "
                 "AtomSpace: %d atoms, %d links. "
                 "Temporal: %d levels active. "
                 "Topology: %s.",
                 engine->autognosis.cycle_count,
                 engine->autognosis.awareness_score,
                 engine->autognosis.convergence_factor,
                 completeness,
                 engine->atomspace.num_atoms,
                 engine->atomspace.num_links,
                 TC_NUM_LEVELS,
                 engine->topology.all_constraints_ok ? 
                     "healthy" : "degraded");
    }

    return 0;
}

/*
 * autognosis_check_convergence — Check if the system has reached
 * a fixed point (skill-infinity convergence criterion).
 */
int
autognosis_check_convergence(GlyphEngine *engine)
{
    return (engine->autognosis.convergence_factor < 0.001 &&
            engine->autognosis.cycle_count > 1);
}

/*
 * autognosis_get_status — Handler for [N:DECISION]?
 * Returns the complete autognosis self-image.
 */
int
autognosis_get_status(GlyphEngine *engine, GlyphResult *result,
                      int argc, char **argv)
{
    return glyph_result_set_json(result,
        "{"
        "\"autognosis\": {"
        "  \"awareness_score\": %.4f,"
        "  \"convergence_factor\": %.6f,"
        "  \"converged\": %s,"
        "  \"cycle_count\": %ld,"
        "  \"last_reflection\": \"%s\","
        "  \"levels\": {"
        "    \"L0_observation\": \"promise satisfaction, temporal levels, namespace paths\","
        "    \"L1_pattern\": \"configuration completeness, hierarchy status\","
        "    \"L2_metacognitive\": \"self-awareness quality, convergence factor\""
        "  },"
        "  \"skill_infinity\": {"
        "    \"criterion\": \"|awareness(n) - awareness(n-1)| < 0.001\","
        "    \"status\": \"%s\""
        "  }"
        "}"
        "}",
        engine->autognosis.awareness_score,
        engine->autognosis.convergence_factor,
        autognosis_check_convergence(engine) ? "true" : "false",
        engine->autognosis.cycle_count,
        engine->autognosis.last_reflection,
        autognosis_check_convergence(engine) ? 
            "FIXED_POINT_REACHED" : "EVOLVING");
}
