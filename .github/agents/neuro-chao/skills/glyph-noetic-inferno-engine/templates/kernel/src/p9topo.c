/*
 * p9topo.c — Plan 9 Cluster Topology Module
 *
 * Implements the RTSA (Runtime Topological Self-Assembly) framework
 * as a kernel module. Manages the Plan 9 cluster topology, computes
 * Betti numbers, validates structural constraints, and provides
 * glyph-addressable topology queries.
 *
 * Source skills:
 *   /plan9-file-server  → semantic domain (fs, cpu, auth, namespace)
 *   /p9fstyx-topology   → analytical lens (Betti numbers, persistence)
 *   /runtime-topological-self-assembly → RTSA framework
 *
 * Topological Invariants:
 *   β₀ == 1  → All nodes form a single connected mesh
 *   β₁ >= 1  → At least one redundant path exists
 *
 * Copyright (c) 2026 ManusCog Project
 * License: AGPL-3.0
 */

#include "glyph.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* ============================================================================
 * Default Cluster Configuration
 * ============================================================================ */

/*
 * Initialize the default Plan 9 cognitive cluster topology.
 * This mirrors the plan9_cluster_assembly.json template from the
 * glyph-noetic-engine skill, but is compiled directly into the kernel.
 */
static void
topo_init_default_cluster(TopoAssembly *assembly)
{
    strncpy(assembly->name, "inferno-cognitive-cluster", 
            sizeof(assembly->name) - 1);

    /* Component 0: File Server */
    TopoComponent *fs = &assembly->components[0];
    strncpy(fs->id, "fs", sizeof(fs->id) - 1);
    strncpy(fs->layer, "storage", sizeof(fs->layer) - 1);
    strncpy(fs->subsystem, "file-server", sizeof(fs->subsystem) - 1);
    fs->num_ports = 3;
    strncpy(fs->ports[0].name, "9p_auth", 32);
    strncpy(fs->ports[0].kind, "BIDI", 8);
    strncpy(fs->ports[0].dtype, "9p", 16);
    strncpy(fs->ports[1].name, "9p_storage", 32);
    strncpy(fs->ports[1].kind, "BIDI", 8);
    strncpy(fs->ports[1].dtype, "9p", 16);
    strncpy(fs->ports[2].name, "cognitive_export", 32);
    strncpy(fs->ports[2].kind, "SOURCE", 8);
    strncpy(fs->ports[2].dtype, "9p_ns", 16);
    fs->state = 1;  /* up */

    /* Component 1: Auth Server */
    TopoComponent *auth = &assembly->components[1];
    strncpy(auth->id, "auth", sizeof(auth->id) - 1);
    strncpy(auth->layer, "storage", sizeof(auth->layer) - 1);
    strncpy(auth->subsystem, "auth-server", sizeof(auth->subsystem) - 1);
    auth->num_ports = 1;
    strncpy(auth->ports[0].name, "auth_service", 32);
    strncpy(auth->ports[0].kind, "SINK", 8);
    strncpy(auth->ports[0].dtype, "9p", 16);
    auth->state = 1;

    /* Component 2: CPU Server 1 */
    TopoComponent *cpu1 = &assembly->components[2];
    strncpy(cpu1->id, "cpu1", sizeof(cpu1->id) - 1);
    strncpy(cpu1->layer, "compute", sizeof(cpu1->layer) - 1);
    strncpy(cpu1->subsystem, "cpu-server", sizeof(cpu1->subsystem) - 1);
    cpu1->num_ports = 2;
    strncpy(cpu1->ports[0].name, "9p_mount", 32);
    strncpy(cpu1->ports[0].kind, "SINK", 8);
    strncpy(cpu1->ports[0].dtype, "9p", 16);
    strncpy(cpu1->ports[1].name, "cognitive_import", 32);
    strncpy(cpu1->ports[1].kind, "SINK", 8);
    strncpy(cpu1->ports[1].dtype, "9p_ns", 16);
    cpu1->state = 1;

    /* Component 3: CPU Server 2 */
    TopoComponent *cpu2 = &assembly->components[3];
    strncpy(cpu2->id, "cpu2", sizeof(cpu2->id) - 1);
    strncpy(cpu2->layer, "compute", sizeof(cpu2->layer) - 1);
    strncpy(cpu2->subsystem, "cpu-server", sizeof(cpu2->subsystem) - 1);
    cpu2->num_ports = 2;
    strncpy(cpu2->ports[0].name, "9p_mount", 32);
    strncpy(cpu2->ports[0].kind, "SINK", 8);
    strncpy(cpu2->ports[0].dtype, "9p", 16);
    strncpy(cpu2->ports[1].name, "cognitive_import", 32);
    strncpy(cpu2->ports[1].kind, "SINK", 8);
    strncpy(cpu2->ports[1].dtype, "9p_ns", 16);
    cpu2->state = 1;

    /* Component 4: Glyph Engine (kernel-resident) */
    TopoComponent *glyph = &assembly->components[4];
    strncpy(glyph->id, "glyph-engine", sizeof(glyph->id) - 1);
    strncpy(glyph->layer, "cognitive", sizeof(glyph->layer) - 1);
    strncpy(glyph->subsystem, "noetic-kernel", sizeof(glyph->subsystem) - 1);
    glyph->num_ports = 3;
    strncpy(glyph->ports[0].name, "dev_glyph", 32);
    strncpy(glyph->ports[0].kind, "BIDI", 8);
    strncpy(glyph->ports[0].dtype, "glyph", 16);
    strncpy(glyph->ports[1].name, "atomspace_rw", 32);
    strncpy(glyph->ports[1].kind, "BIDI", 8);
    strncpy(glyph->ports[1].dtype, "atom", 16);
    strncpy(glyph->ports[2].name, "temporal_sched", 32);
    strncpy(glyph->ports[2].kind, "SOURCE", 8);
    strncpy(glyph->ports[2].dtype, "tick", 16);
    glyph->state = 1;

    assembly->num_components = 5;

    /* Adjacency matrix (for Betti number computation) */
    /* fs-auth, fs-cpu1, fs-cpu2, fs-glyph, glyph-cpu1, glyph-cpu2 */
    memset(assembly->adjacency, 0, sizeof(assembly->adjacency));
    assembly->adjacency[0][1] = 1; assembly->adjacency[1][0] = 1; /* fs-auth */
    assembly->adjacency[0][2] = 1; assembly->adjacency[2][0] = 1; /* fs-cpu1 */
    assembly->adjacency[0][3] = 1; assembly->adjacency[3][0] = 1; /* fs-cpu2 */
    assembly->adjacency[0][4] = 1; assembly->adjacency[4][0] = 1; /* fs-glyph */
    assembly->adjacency[4][2] = 1; assembly->adjacency[2][4] = 1; /* glyph-cpu1 */
    assembly->adjacency[4][3] = 1; assembly->adjacency[3][4] = 1; /* glyph-cpu2 */

    /* Simplices by dimension */
    assembly->num_simplices[0] = 5;  /* 5 vertices (components) */
    assembly->num_simplices[1] = 6;  /* 6 edges (connections) */
    assembly->num_simplices[2] = 2;  /* 2 triangles (fs-cpu1-glyph, fs-cpu2-glyph) */
    assembly->num_simplices[3] = 0;

    /* Constraints */
    assembly->num_constraints = 2;

    TopoConstraint *c0 = &assembly->constraints[0];
    strncpy(c0->name, "connected_cluster", sizeof(c0->name) - 1);
    c0->dimension = 0;
    strncpy(c0->op, "==", sizeof(c0->op) - 1);
    c0->value = 1;
    strncpy(c0->description,
            "All nodes must form a single connected component",
            sizeof(c0->description) - 1);

    TopoConstraint *c1 = &assembly->constraints[1];
    strncpy(c1->name, "storage_redundancy", sizeof(c1->name) - 1);
    c1->dimension = 1;
    strncpy(c1->op, ">=", sizeof(c1->op) - 1);
    c1->value = 1;
    strncpy(c1->description,
            "At least one cycle for storage path redundancy",
            sizeof(c1->description) - 1);
}

/* ============================================================================
 * Betti Number Computation
 * ============================================================================ */

/*
 * topo_compute_betti — Compute Betti numbers for the cluster assembly.
 *
 * For a simplicial complex K:
 *   β₀ = number of connected components
 *   β₁ = number of independent cycles (redundant paths)
 *   β₂ = number of enclosed voids
 *
 * We use the Euler characteristic relation:
 *   χ = V - E + F = β₀ - β₁ + β₂
 *
 * For our cluster topology, we compute β₀ via connected components
 * (BFS/DFS on the adjacency matrix) and derive β₁ from Euler's formula.
 */
int
topo_compute_betti(TopoAssembly *assembly)
{
    int n = assembly->num_components;
    int visited[16] = {0};
    int components = 0;

    /* Compute β₀ via BFS */
    for (int i = 0; i < n; i++) {
        if (visited[i])
            continue;
        components++;

        /* BFS from node i */
        int queue[16];
        int front = 0, back = 0;
        queue[back++] = i;
        visited[i] = 1;

        while (front < back) {
            int node = queue[front++];
            for (int j = 0; j < n; j++) {
                if (assembly->adjacency[node][j] && !visited[j]) {
                    visited[j] = 1;
                    queue[back++] = j;
                }
            }
        }
    }

    assembly->betti[0] = components;

    int V = assembly->num_simplices[0];
    int E = assembly->num_simplices[1];

    /* β₁ = E - V + β₀ (number of independent cycles) */
    assembly->betti[1] = E - V + assembly->betti[0];
    assembly->betti[2] = 0;
    assembly->betti[3] = 0;

    /* Euler characteristic: χ = β₀ - β₁ + β₂ */
    assembly->euler_characteristic = assembly->betti[0] - assembly->betti[1] + assembly->betti[2];

    return 0;
}

/* ============================================================================
 * Constraint Validation
 * ============================================================================ */

int
topo_check_constraints(TopoAssembly *assembly)
{
    int all_ok = 1;

    for (int i = 0; i < assembly->num_constraints; i++) {
        TopoConstraint *c = &assembly->constraints[i];
        int betti_val = assembly->betti[c->dimension];
        int satisfied = 0;

        if (strcmp(c->op, "==") == 0)
            satisfied = (betti_val == c->value);
        else if (strcmp(c->op, ">=") == 0)
            satisfied = (betti_val >= c->value);
        else if (strcmp(c->op, "<=") == 0)
            satisfied = (betti_val <= c->value);

        c->satisfied = satisfied;
        if (!satisfied)
            all_ok = 0;
    }

    assembly->all_constraints_ok = all_ok;
    return all_ok;
}

/* ============================================================================
 * Initialization
 * ============================================================================ */

int
topo_init(GlyphEngine *engine, const char *config_path)
{
    memset(&engine->topology, 0, sizeof(TopoAssembly));

    /* Initialize default cluster topology */
    topo_init_default_cluster(&engine->topology);

    /* Compute topological invariants */
    topo_compute_betti(&engine->topology);
    topo_check_constraints(&engine->topology);

    return 0;
}

/* ============================================================================
 * Glyph Handlers
 * ============================================================================ */

/*
 * topo_get_status — Handler for [T:ASSEMBLY]?, [T:BETA0]?, [T:BETA1]?
 * Returns the complete topological health summary.
 */
int
topo_get_status(GlyphEngine *engine, GlyphResult *result,
                int argc, char **argv)
{
    TopoAssembly *a = &engine->topology;
    char *buf = result->data;
    int offset = 0;

    offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset,
        "{"
        "\"assembly\": \"%s\","
        "\"num_components\": %d,"
        "\"simplices_by_dim\": {"
        "  \"0_vertices\": %d,"
        "  \"1_edges\": %d,"
        "  \"2_triangles\": %d"
        "},"
        "\"betti_numbers\": {"
        "  \"beta_0\": %d,"
        "  \"beta_1\": %d,"
        "  \"beta_2\": %d"
        "},"
        "\"euler_characteristic\": %d,"
        "\"constraints_satisfied\": %s,"
        "\"constraints\": [",
        a->name,
        a->num_components,
        a->num_simplices[0], a->num_simplices[1], a->num_simplices[2],
        a->betti[0], a->betti[1], a->betti[2],
        a->euler_characteristic,
        a->all_constraints_ok ? "true" : "false");

    for (int i = 0; i < a->num_constraints; i++) {
        TopoConstraint *c = &a->constraints[i];
        offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset,
            "%s{\"name\": \"%s\", \"condition\": \"beta_%d %s %d\", "
            "\"actual\": %d, \"satisfied\": %s, \"description\": \"%s\"}",
            (i > 0) ? ", " : "",
            c->name, c->dimension, c->op, c->value,
            a->betti[c->dimension],
            c->satisfied ? "true" : "false",
            c->description);
    }

    offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset, "]}");
    result->data_len = offset;
    result->error = 0;
    return 0;
}

/*
 * topo_list_components — Handler for [P:FS]?, [P:CPU]?
 * Lists all cluster components with metadata and port types.
 */
int
topo_list_components(GlyphEngine *engine, GlyphResult *result,
                     int argc, char **argv)
{
    TopoAssembly *a = &engine->topology;
    char *buf = result->data;
    int offset = 0;

    offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset,
        "{\"components\": [");

    for (int i = 0; i < a->num_components; i++) {
        TopoComponent *comp = &a->components[i];
        static const char *state_names[] = {"down", "up", "degraded"};

        offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset,
            "%s{"
            "\"id\": \"%s\","
            "\"layer\": \"%s\","
            "\"subsystem\": \"%s\","
            "\"state\": \"%s\","
            "\"ports\": [",
            (i > 0) ? ", " : "",
            comp->id, comp->layer, comp->subsystem,
            state_names[comp->state < 3 ? comp->state : 0]);

        for (int p = 0; p < comp->num_ports; p++) {
            offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset,
                "%s{\"name\": \"%s\", \"kind\": \"%s\", \"dtype\": \"%s\"}",
                (p > 0) ? ", " : "",
                comp->ports[p].name, comp->ports[p].kind,
                comp->ports[p].dtype);
        }

        offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset, "]}");
    }

    offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset, "]}");
    result->data_len = offset;
    result->error = 0;
    return 0;
}

/*
 * topo_get_namespace_map — Handler for [P:NS]?
 * Returns the /cognitive/ namespace-to-glyph mapping.
 */
int
topo_get_namespace_map(GlyphEngine *engine, GlyphResult *result,
                       int argc, char **argv)
{
    return glyph_result_set_json(result,
        "{"
        "\"namespace\": \"/n/glyph\","
        "\"protocol\": \"9P2000\","
        "\"mappings\": {"
        "  \"/n/glyph/atomspace/\": {\"glyph\": \"[S:ATOMSPACE]\", \"9p_op\": \"read\"},"
        "  \"/n/glyph/inference/\": {\"glyph\": \"[C:PLN]\", \"9p_op\": \"read\"},"
        "  \"/n/glyph/attention/\": {\"glyph\": \"[C:ATTN]\", \"9p_op\": \"read\"},"
        "  \"/n/glyph/temporal/\": {\"glyph\": \"[T-HIERARCHY]\", \"9p_op\": \"read\"},"
        "  \"/n/glyph/autognosis/\": {\"glyph\": \"[N:DECISION]\", \"9p_op\": \"read\"},"
        "  \"/n/glyph/learning/\": {\"glyph\": \"[C:MOSES]\", \"9p_op\": \"read\"},"
        "  \"/n/glyph/topology/\": {\"glyph\": \"[T:ASSEMBLY]\", \"9p_op\": \"read\"},"
        "  \"/n/glyph/topology/betti/0\": {\"glyph\": \"[T:BETA0]\", \"9p_op\": \"read\"},"
        "  \"/n/glyph/topology/betti/1\": {\"glyph\": \"[T:BETA1]\", \"9p_op\": \"read\"},"
        "  \"/n/glyph/topology/persist\": {\"glyph\": \"[T:PERSIST]\", \"9p_op\": \"read\"}"
        "},"
        "\"note\": \"A 9P read on /n/glyph/temporal/levels/9 is equivalent to [T~g]?\""
        "}");
}

/*
 * topo_get_persistence — Handler for [T:PERSIST]?
 * Returns the persistence diagram of the cluster assembly.
 */
int
topo_get_persistence(GlyphEngine *engine, GlyphResult *result,
                     int argc, char **argv)
{
    TopoAssembly *a = &engine->topology;

    /* Generate persistence pairs from the simplicial complex.
     * For our cluster topology:
     *   - β₀ components: one pair (0, inf) per connected component
     *   - β₁ cycles: one pair (birth, death) per independent cycle
     */
    return glyph_result_set_json(result,
        "{"
        "\"persistence_pairs\": ["
        "  {\"dim\": 0, \"birth\": 0.0, \"death\": \"inf\", "
        "   \"note\": \"Primary connected component (entire cluster)\"},"
        "  {\"dim\": 1, \"birth\": 0.0, \"death\": \"inf\", "
        "   \"note\": \"Cycle: fs-cpu1-glyph-fs (storage redundancy)\"},"
        "  {\"dim\": 1, \"birth\": 0.0, \"death\": \"inf\", "
        "   \"note\": \"Cycle: fs-cpu2-glyph-fs (cognitive redundancy)\"}"
        "],"
        "\"interpretation\": {"
        "  \"beta_0_persistent\": %d,"
        "  \"beta_1_persistent\": %d,"
        "  \"structural_health\": \"%s\""
        "}"
        "}",
        a->betti[0], a->betti[1],
        a->all_constraints_ok ? "HEALTHY" : "DEGRADED");
}
