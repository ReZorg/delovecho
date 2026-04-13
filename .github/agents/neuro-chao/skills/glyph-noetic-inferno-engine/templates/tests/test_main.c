/*
 * test_main.c — Glyph-Noetic Inferno Kernel Test Suite
 *
 * Comprehensive tests for the cognitive kernel, covering:
 *   - Engine initialization and shutdown
 *   - Glyph parsing and dispatch
 *   - Temporal hierarchy
 *   - Topology module (Betti numbers, constraints)
 *   - AtomSpace operations
 *   - Kernel promises
 *   - Autognosis self-image
 *
 * Build: make test (from kernel/ directory)
 * Run:   ./build/glyph_kernel_test
 *
 * Copyright (c) 2026 ManusCog Project
 * License: AGPL-3.0
 */

#include "glyph.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>

/* Simple test framework */
static int tests_passed = 0;
static int tests_failed = 0;

#define TEST(name) \
    static void test_##name(void); \
    static void run_test_##name(void) { \
        printf("  %-50s ", #name); \
        test_##name(); \
        tests_passed++; \
        printf("[PASS]\n"); \
    } \
    static void test_##name(void)

#define ASSERT_EQ(a, b) do { \
    if ((a) != (b)) { \
        printf("[FAIL] %s:%d: %d != %d\n", __FILE__, __LINE__, (int)(a), (int)(b)); \
        tests_failed++; \
        return; \
    } \
} while(0)

#define ASSERT_STR_EQ(a, b) do { \
    if (strcmp((a), (b)) != 0) { \
        printf("[FAIL] %s:%d: '%s' != '%s'\n", __FILE__, __LINE__, (a), (b)); \
        tests_failed++; \
        return; \
    } \
} while(0)

#define ASSERT_TRUE(x) do { \
    if (!(x)) { \
        printf("[FAIL] %s:%d: assertion failed\n", __FILE__, __LINE__); \
        tests_failed++; \
        return; \
    } \
} while(0)

/* ============================================================================
 * Tests: Engine Lifecycle
 * ============================================================================ */

TEST(engine_init)
{
    GlyphEngine *engine = glyph_engine_init();
    ASSERT_TRUE(engine != NULL);
    ASSERT_TRUE(engine->initialized);
    ASSERT_STR_EQ(engine->version, GLYPH_VERSION);
    ASSERT_TRUE(engine->num_glyphs > 0);
}

TEST(engine_has_glyphs)
{
    GlyphEngine *engine = glyph_engine_get();
    ASSERT_TRUE(engine->num_glyphs >= 28);  /* At least 28 default glyphs */
}

/* ============================================================================
 * Tests: Glyph Parsing
 * ============================================================================ */

TEST(parse_simple_query)
{
    GlyphSentence sentence;
    int rc = glyph_parse_sentence("[C:PLN]?", &sentence);
    ASSERT_EQ(rc, 0);
    ASSERT_STR_EQ(sentence.primary_glyph, "C:PLN");
    ASSERT_EQ(sentence.op, '?');
}

TEST(parse_topology_query)
{
    GlyphSentence sentence;
    int rc = glyph_parse_sentence("[T:ASSEMBLY]?", &sentence);
    ASSERT_EQ(rc, 0);
    ASSERT_STR_EQ(sentence.primary_glyph, "T:ASSEMBLY");
    ASSERT_EQ(sentence.op, '?');
}

TEST(parse_temporal_query)
{
    GlyphSentence sentence;
    int rc = glyph_parse_sentence("[T~g]?", &sentence);
    ASSERT_EQ(rc, 0);
    ASSERT_STR_EQ(sentence.primary_glyph, "T~g");
    ASSERT_EQ(sentence.op, '?');
}

TEST(parse_kernel_status)
{
    GlyphSentence sentence;
    int rc = glyph_parse_sentence("[K:STATUS]?", &sentence);
    ASSERT_EQ(rc, 0);
    ASSERT_STR_EQ(sentence.primary_glyph, "K:STATUS");
}

/* ============================================================================
 * Tests: Glyph Dispatch
 * ============================================================================ */

TEST(dispatch_engine_status)
{
    GlyphEngine *engine = glyph_engine_get();
    GlyphSentence sentence;
    GlyphResult *result = glyph_result_new();

    glyph_parse_sentence("[K:STATUS]?", &sentence);
    int rc = glyph_dispatch(engine, &sentence, result);
    ASSERT_EQ(rc, 0);
    ASSERT_EQ(result->error, 0);
    ASSERT_TRUE(result->data_len > 0);
    ASSERT_TRUE(strstr(result->data, "glyph-noetic-inferno-kernel") != NULL);

    glyph_result_free(result);
}

TEST(dispatch_glyph_list)
{
    GlyphEngine *engine = glyph_engine_get();
    GlyphSentence sentence;
    GlyphResult *result = glyph_result_new();

    glyph_parse_sentence("[K:GLYPHS]?", &sentence);
    int rc = glyph_dispatch(engine, &sentence, result);
    ASSERT_EQ(rc, 0);
    ASSERT_TRUE(strstr(result->data, "num_glyphs") != NULL);

    glyph_result_free(result);
}

TEST(dispatch_unknown_glyph)
{
    GlyphEngine *engine = glyph_engine_get();
    GlyphSentence sentence;
    GlyphResult *result = glyph_result_new();

    glyph_parse_sentence("[X:UNKNOWN]?", &sentence);
    glyph_dispatch(engine, &sentence, result);
    ASSERT_TRUE(result->error != 0);

    glyph_result_free(result);
}

/* ============================================================================
 * Tests: Temporal Hierarchy
 * ============================================================================ */

TEST(temporal_levels_initialized)
{
    GlyphEngine *engine = glyph_engine_get();
    for (int i = 0; i < TC_NUM_LEVELS; i++) {
        ASSERT_TRUE(engine->temporal[i].period_us > 0);
        ASSERT_TRUE(engine->temporal[i].active);
    }
}

TEST(temporal_hierarchy_query)
{
    GlyphEngine *engine = glyph_engine_get();
    GlyphSentence sentence;
    GlyphResult *result = glyph_result_new();

    glyph_parse_sentence("[T-HIERARCHY]?", &sentence);
    int rc = glyph_dispatch(engine, &sentence, result);
    ASSERT_EQ(rc, 0);
    ASSERT_TRUE(strstr(result->data, "time-crystal-12-level") != NULL);

    glyph_result_free(result);
}

/* ============================================================================
 * Tests: Topology Module
 * ============================================================================ */

TEST(topology_initialized)
{
    GlyphEngine *engine = glyph_engine_get();
    ASSERT_TRUE(engine->topology.num_components >= 4);
}

TEST(topology_betti_numbers)
{
    GlyphEngine *engine = glyph_engine_get();
    ASSERT_EQ(engine->topology.betti[0], 1);  /* Single connected component */
    ASSERT_TRUE(engine->topology.betti[1] >= 1);  /* At least one cycle */
}

TEST(topology_constraints_satisfied)
{
    GlyphEngine *engine = glyph_engine_get();
    ASSERT_TRUE(engine->topology.all_constraints_ok);
}

TEST(topology_assembly_query)
{
    GlyphEngine *engine = glyph_engine_get();
    GlyphSentence sentence;
    GlyphResult *result = glyph_result_new();

    glyph_parse_sentence("[T:ASSEMBLY]?", &sentence);
    int rc = glyph_dispatch(engine, &sentence, result);
    ASSERT_EQ(rc, 0);
    ASSERT_TRUE(strstr(result->data, "inferno-cognitive-cluster") != NULL);
    ASSERT_TRUE(strstr(result->data, "beta_0") != NULL);

    glyph_result_free(result);
}

TEST(topology_namespace_query)
{
    GlyphEngine *engine = glyph_engine_get();
    GlyphSentence sentence;
    GlyphResult *result = glyph_result_new();

    glyph_parse_sentence("[P:NS]?", &sentence);
    int rc = glyph_dispatch(engine, &sentence, result);
    ASSERT_EQ(rc, 0);
    ASSERT_TRUE(strstr(result->data, "/n/glyph") != NULL);

    glyph_result_free(result);
}

/* ============================================================================
 * Tests: AtomSpace
 * ============================================================================ */

TEST(atomspace_initialized)
{
    GlyphEngine *engine = glyph_engine_get();
    ASSERT_TRUE(engine->atomspace.num_atoms > 0);
    ASSERT_TRUE(engine->atomspace.capacity > 0);
}

TEST(atomspace_has_seed_atoms)
{
    GlyphEngine *engine = glyph_engine_get();
    Atom *a = atomspace_get(&engine->atomspace, 0);
    ASSERT_TRUE(a != NULL);
    ASSERT_STR_EQ(a->name, "glyph-noetic-engine");
}

TEST(atomspace_query)
{
    GlyphEngine *engine = glyph_engine_get();
    GlyphSentence sentence;
    GlyphResult *result = glyph_result_new();

    glyph_parse_sentence("[S:ATOMSPACE]?", &sentence);
    int rc = glyph_dispatch(engine, &sentence, result);
    ASSERT_EQ(rc, 0);
    ASSERT_TRUE(strstr(result->data, "atomspace") != NULL);

    glyph_result_free(result);
}

/* ============================================================================
 * Tests: Kernel Promises
 * ============================================================================ */

TEST(promises_validated)
{
    GlyphEngine *engine = glyph_engine_get();
    /* At minimum, temporal levels and glyph device should be satisfied */
    ASSERT_TRUE(engine->promises[PROMISE_TEMPORAL_LEVELS]);
    ASSERT_TRUE(engine->promises[PROMISE_TOPO_CONNECTED]);
}

TEST(promises_query)
{
    GlyphEngine *engine = glyph_engine_get();
    GlyphSentence sentence;
    GlyphResult *result = glyph_result_new();

    glyph_parse_sentence("[K:PROMISES]?", &sentence);
    int rc = glyph_dispatch(engine, &sentence, result);
    ASSERT_EQ(rc, 0);
    ASSERT_TRUE(strstr(result->data, "promises") != NULL);

    glyph_result_free(result);
}

/* ============================================================================
 * Tests: Autognosis
 * ============================================================================ */

TEST(autognosis_cycle)
{
    GlyphEngine *engine = glyph_engine_get();
    double prev = engine->autognosis.awareness_score;
    autognosis_build_self_image(engine);
    ASSERT_TRUE(engine->autognosis.cycle_count > 0);
    ASSERT_TRUE(engine->autognosis.awareness_score >= 0.0);
    ASSERT_TRUE(engine->autognosis.awareness_score <= 1.0);
}

TEST(autognosis_query)
{
    GlyphEngine *engine = glyph_engine_get();
    GlyphSentence sentence;
    GlyphResult *result = glyph_result_new();

    glyph_parse_sentence("[N:DECISION]?", &sentence);
    int rc = glyph_dispatch(engine, &sentence, result);
    ASSERT_EQ(rc, 0);
    ASSERT_TRUE(strstr(result->data, "autognosis") != NULL);

    glyph_result_free(result);
}

/* ============================================================================
 * Main Test Runner
 * ============================================================================ */

int main(void)
{
    printf("\n");
    printf("============================================================\n");
    printf("  Glyph-Noetic Inferno Kernel — Test Suite\n");
    printf("============================================================\n\n");

    /* Engine Lifecycle */
    printf("Engine Lifecycle:\n");
    run_test_engine_init();
    run_test_engine_has_glyphs();

    /* Glyph Parsing */
    printf("\nGlyph Parsing:\n");
    run_test_parse_simple_query();
    run_test_parse_topology_query();
    run_test_parse_temporal_query();
    run_test_parse_kernel_status();

    /* Glyph Dispatch */
    printf("\nGlyph Dispatch:\n");
    run_test_dispatch_engine_status();
    run_test_dispatch_glyph_list();
    run_test_dispatch_unknown_glyph();

    /* Temporal Hierarchy */
    printf("\nTemporal Hierarchy:\n");
    run_test_temporal_levels_initialized();
    run_test_temporal_hierarchy_query();

    /* Topology Module */
    printf("\nTopology Module:\n");
    run_test_topology_initialized();
    run_test_topology_betti_numbers();
    run_test_topology_constraints_satisfied();
    run_test_topology_assembly_query();
    run_test_topology_namespace_query();

    /* AtomSpace */
    printf("\nAtomSpace:\n");
    run_test_atomspace_initialized();
    run_test_atomspace_has_seed_atoms();
    run_test_atomspace_query();

    /* Kernel Promises */
    printf("\nKernel Promises:\n");
    run_test_promises_validated();
    run_test_promises_query();

    /* Autognosis */
    printf("\nAutognosis:\n");
    run_test_autognosis_cycle();
    run_test_autognosis_query();

    /* Summary */
    printf("\n============================================================\n");
    printf("  Results: %d passed, %d failed, %d total\n",
           tests_passed, tests_failed, tests_passed + tests_failed);
    printf("============================================================\n");

    /* Cleanup */
    glyph_engine_shutdown(glyph_engine_get());

    return tests_failed > 0 ? 1 : 0;
}
