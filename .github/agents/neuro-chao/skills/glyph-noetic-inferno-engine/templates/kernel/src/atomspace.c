/*
 * atomspace.c — Kernel-Resident AtomSpace Hypergraph
 *
 * A simplified but functional AtomSpace implementation that runs
 * entirely within the Inferno kernel. Provides the fundamental
 * knowledge representation for all cognitive operations.
 *
 * The AtomSpace is the shared substrate accessed by all cognitive
 * modules (PLN, MOSES, ECAN, Pattern Matcher). It is synchronized
 * with the temporal hierarchy at Level 1 (8ms protein dynamics).
 *
 * Copyright (c) 2026 ManusCog Project
 * License: AGPL-3.0
 */

#include "glyph.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* ============================================================================
 * AtomSpace Lifecycle
 * ============================================================================ */

int
atomspace_init(AtomSpace *as, int capacity)
{
    if (as == NULL || capacity <= 0)
        return -1;

    as->atoms = (Atom *)calloc(capacity, sizeof(Atom));
    if (as->atoms == NULL)
        return -1;

    as->num_atoms = 0;
    as->num_links = 0;
    as->capacity = capacity;
    as->version = 0;

    /* Seed the AtomSpace with foundational cognitive atoms */
    /* These represent the kernel's self-knowledge */
    atomspace_add_node(as, "ConceptNode", "glyph-noetic-engine");
    atomspace_add_node(as, "ConceptNode", "inferno-kernel");
    atomspace_add_node(as, "ConceptNode", "time-crystal-hierarchy");
    atomspace_add_node(as, "ConceptNode", "plan9-cluster");
    atomspace_add_node(as, "ConceptNode", "atomspace");
    atomspace_add_node(as, "ConceptNode", "pln-inference");
    atomspace_add_node(as, "ConceptNode", "moses-learning");
    atomspace_add_node(as, "ConceptNode", "ecan-attention");
    atomspace_add_node(as, "ConceptNode", "pattern-matching");
    atomspace_add_node(as, "ConceptNode", "autognosis");

    /* Create links representing kernel architecture */
    long ids[2];
    ids[0] = 0; ids[1] = 1;  /* engine -> kernel */
    atomspace_add_link(as, "InheritanceLink", ids, 2);
    ids[0] = 0; ids[1] = 2;  /* engine -> temporal */
    atomspace_add_link(as, "MemberLink", ids, 2);
    ids[0] = 0; ids[1] = 3;  /* engine -> cluster */
    atomspace_add_link(as, "MemberLink", ids, 2);
    ids[0] = 0; ids[1] = 4;  /* engine -> atomspace */
    atomspace_add_link(as, "MemberLink", ids, 2);
    ids[0] = 0; ids[1] = 9;  /* engine -> autognosis */
    atomspace_add_link(as, "MemberLink", ids, 2);

    /* Set truth values for foundational atoms */
    atomspace_set_tv(as, 0, 1.0, 0.99);  /* engine: high confidence */
    atomspace_set_tv(as, 1, 1.0, 0.99);  /* kernel: high confidence */
    atomspace_set_tv(as, 9, 0.5, 0.3);   /* autognosis: initially uncertain */

    return 0;
}

void
atomspace_destroy(AtomSpace *as)
{
    if (as && as->atoms) {
        free(as->atoms);
        as->atoms = NULL;
        as->num_atoms = 0;
        as->num_links = 0;
        as->capacity = 0;
    }
}

/* ============================================================================
 * Atom Operations
 * ============================================================================ */

long
atomspace_add_node(AtomSpace *as, const char *type, const char *name)
{
    if (as->num_atoms >= as->capacity)
        return -1;

    Atom *atom = &as->atoms[as->num_atoms];
    atom->id = as->num_atoms;
    strncpy(atom->type, type, sizeof(atom->type) - 1);
    strncpy(atom->name, name, sizeof(atom->name) - 1);
    atom->tv_strength = 0.0;
    atom->tv_confidence = 0.0;
    atom->av_sti = 0;
    atom->av_lti = 0;
    atom->num_outgoing = 0;

    as->num_atoms++;
    as->version++;
    return atom->id;
}

long
atomspace_add_link(AtomSpace *as, const char *type,
                   long *outgoing, int num_outgoing)
{
    if (as->num_atoms >= as->capacity)
        return -1;
    if (num_outgoing > 16)
        num_outgoing = 16;

    Atom *atom = &as->atoms[as->num_atoms];
    atom->id = as->num_atoms;
    strncpy(atom->type, type, sizeof(atom->type) - 1);
    atom->name[0] = '\0';  /* Links don't have names */
    atom->tv_strength = 1.0;
    atom->tv_confidence = 0.5;
    atom->av_sti = 0;
    atom->av_lti = 0;
    atom->num_outgoing = num_outgoing;
    for (int i = 0; i < num_outgoing; i++)
        atom->outgoing[i] = outgoing[i];

    as->num_atoms++;
    as->num_links++;
    as->version++;
    return atom->id;
}

Atom *
atomspace_get(AtomSpace *as, long id)
{
    if (id < 0 || id >= as->num_atoms)
        return NULL;
    return &as->atoms[id];
}

int
atomspace_set_tv(AtomSpace *as, long id, double strength, double confidence)
{
    Atom *atom = atomspace_get(as, id);
    if (atom == NULL)
        return -1;
    atom->tv_strength = strength;
    atom->tv_confidence = confidence;
    as->version++;
    return 0;
}

int
atomspace_set_av(AtomSpace *as, long id, long sti, long lti)
{
    Atom *atom = atomspace_get(as, id);
    if (atom == NULL)
        return -1;
    atom->av_sti = sti;
    atom->av_lti = lti;
    as->version++;
    return 0;
}

/* ============================================================================
 * Glyph Handler: [S:ATOMSPACE]?
 * ============================================================================ */

int
atomspace_get_status(GlyphEngine *engine, GlyphResult *result,
                      int argc, char **argv)
{
    AtomSpace *as = &engine->atomspace;
    char *buf = result->data;
    int offset = 0;

    /* Count atoms by type */
    int num_nodes = 0, num_links = 0;
    int type_counts[8] = {0};
    const char *type_names[8] = {
        "ConceptNode", "PredicateNode", "NumberNode", "SchemaNode",
        "InheritanceLink", "MemberLink", "EvaluationLink", "other"
    };

    for (int i = 0; i < as->num_atoms; i++) {
        Atom *a = &as->atoms[i];
        if (a->num_outgoing > 0)
            num_links++;
        else
            num_nodes++;

        int found = 0;
        for (int t = 0; t < 7; t++) {
            if (strcmp(a->type, type_names[t]) == 0) {
                type_counts[t]++;
                found = 1;
                break;
            }
        }
        if (!found)
            type_counts[7]++;
    }

    offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset,
        "{"
        "\"atomspace\": {"
        "  \"total_atoms\": %d,"
        "  \"nodes\": %d,"
        "  \"links\": %d,"
        "  \"capacity\": %d,"
        "  \"version\": %ld,"
        "  \"utilization\": %.2f,"
        "  \"types\": {",
        as->num_atoms, num_nodes, num_links,
        as->capacity, as->version,
        (double)as->num_atoms / as->capacity);

    int first = 1;
    for (int t = 0; t < 8; t++) {
        if (type_counts[t] > 0) {
            offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset,
                "%s\"%s\": %d",
                first ? "" : ", ",
                type_names[t], type_counts[t]);
            first = 0;
        }
    }

    offset += snprintf(buf + offset, GLYPH_MAX_RESPONSE - offset,
        "  },"
        "  \"kernel_resident\": true,"
        "  \"9p_path\": \"/n/glyph/atomspace/\""
        "}}");

    result->data_len = offset;
    result->error = 0;
    return 0;
}
