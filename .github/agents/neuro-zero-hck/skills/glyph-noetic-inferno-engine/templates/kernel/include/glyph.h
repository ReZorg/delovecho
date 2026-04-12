/*
 * glyph.h — Glyph-Noetic Engine: Kernel Interface
 *
 * This header defines the core data structures and function prototypes
 * for the Glyph-Noetic cognitive kernel. It provides the interface
 * between the /dev/glyph character device and the underlying cognitive
 * subsystems (AtomSpace, PLN, ECAN, temporal scheduler, topology).
 *
 * Architecture:
 *   /glyph-noetic-engine = /neuro-symbolic-engine(
 *       /time-crystal-nn(/time-crystal-neuron)
 *       [/time-crystal-daemon]
 *   ) ( /plan9-file-server [/p9fstyx-topology] )
 *
 * Inferno Kernel Integration:
 *   Glyphs are first-class kernel objects. The file system IS the API.
 *   Writing to /dev/glyph executes noetic sentences.
 *   Reading from /dev/glyph retrieves cognitive state.
 *   The /n/glyph namespace provides browsable cognitive state.
 *
 * Copyright (c) 2026 ManusCog Project
 * License: AGPL-3.0
 */

#ifndef _GLYPH_H_
#define _GLYPH_H_

#ifdef GLYPH_KERNEL_SIMULATION
/* Simulation build: use standard C headers */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#else
/* Inferno kernel build */
#include <lib9.h>
#include <kernel.h>
#endif

/* ============================================================================
 * Constants
 * ============================================================================ */

#define GLYPH_VERSION           "1.0.0"
#define GLYPH_MAX_SENTENCE      4096    /* Max noetic sentence length */
#define GLYPH_MAX_RESPONSE      65536   /* Max response buffer */
#define GLYPH_MAX_ID_LEN        64      /* Max glyph identifier length */
#define GLYPH_MAX_PARAMS        16      /* Max parameters per glyph action */
#define GLYPH_MAP_SIZE          64      /* Static glyph map capacity */

/* Temporal hierarchy levels (from time-crystal-neuron) */
#define TC_LEVEL_QUANTUM        0       /* 1μs  — Quantum resonance */
#define TC_LEVEL_PROTEIN        1       /* 8ms  — Protein dynamics */
#define TC_LEVEL_ION_CHANNEL    2       /* 26ms — Ion channel gating */
#define TC_LEVEL_MEMBRANE       3       /* 52ms — Membrane dynamics */
#define TC_LEVEL_AIS            4       /* 110ms — Axon initial segment */
#define TC_LEVEL_DENDRITIC      5       /* 160ms — Dendritic integration */
#define TC_LEVEL_SYNAPTIC       6       /* 250ms — Synaptic plasticity */
#define TC_LEVEL_SOMA           7       /* 330ms — Soma processing */
#define TC_LEVEL_NETWORK        8       /* 500ms — Network synchronization */
#define TC_LEVEL_GLOBAL         9       /* 1000ms — Global rhythm */
#define TC_LEVEL_CIRCADIAN      10      /* 60s   — Circadian modulation */
#define TC_LEVEL_HOMEOSTATIC    11      /* 3600s — Homeostatic regulation */
#define TC_NUM_LEVELS           12

/* Glyph categories */
#define GLYPH_CAT_TEMPORAL      0x01    /* Blue — time crystal levels */
#define GLYPH_CAT_COGNITIVE     0x02    /* Purple — cognitive processes */
#define GLYPH_CAT_STRUCTURAL    0x03    /* Green — architectural components */
#define GLYPH_CAT_NOETIC        0x04    /* Orange — knowledge/belief states */
#define GLYPH_CAT_PROTOCOL      0x05    /* Cyan — 9P protocol glyphs */
#define GLYPH_CAT_TOPOLOGY      0x06    /* Cyan — topological structure */
#define GLYPH_CAT_KERNEL        0x07    /* Red — kernel-specific glyphs */

/* Glyph operators */
#define GLYPH_OP_QUERY          '?'     /* Request information */
#define GLYPH_OP_ACTION         '!'     /* Trigger execution */
#define GLYPH_OP_FLOW           '-'     /* Data flow (part of ->) */
#define GLYPH_OP_PIPE           '|'     /* Pipe output */

/* Kernel promise IDs (from promise-lambda-attention) */
#define PROMISE_INFERNO_BINARY  0
#define PROMISE_LIMBO_COMPILER  1
#define PROMISE_9P_LISTENER     2
#define PROMISE_CLUSTER_COMPOSE 3
#define PROMISE_COGNITIVE_NS    4
#define PROMISE_DEVCONTAINER    5
#define PROMISE_AUTOGNOSIS      6
#define PROMISE_TEMPORAL_LEVELS 7
#define PROMISE_GLYPH_DEVICE    8       /* New: /dev/glyph exists */
#define PROMISE_TOPO_CONNECTED  9       /* New: β₀ == 1 */
#define PROMISE_TOPO_REDUNDANT  10      /* New: β₁ >= 1 */
#define NUM_KERNEL_PROMISES     11

/* ============================================================================
 * Data Structures
 * ============================================================================ */

/* Forward declarations */
typedef struct GlyphEngine    GlyphEngine;
typedef struct GlyphAction    GlyphAction;
typedef struct GlyphResult    GlyphResult;
typedef struct GlyphSentence  GlyphSentence;
typedef struct TemporalLevel  TemporalLevel;
typedef struct TopoAssembly   TopoAssembly;
typedef struct TopoComponent  TopoComponent;
typedef struct TopoConstraint TopoConstraint;
typedef struct AtomSpace      AtomSpace;
typedef struct Atom           Atom;
typedef struct CogModule      CogModule;

/*
 * GlyphResult — The return value from executing a glyph command.
 * Contains the glyph ID, operator, and a JSON-formatted result string.
 */
struct GlyphResult {
    char    glyph_id[GLYPH_MAX_ID_LEN];
    char    op;                         /* '?', '!', or '>' */
    char    *data;                      /* JSON result string (heap-allocated) */
    int     data_len;
    int     error;                      /* 0 = success, else error code */
    char    error_msg[256];
};

/*
 * GlyphAction — Maps a glyph identifier to a kernel function.
 * This is the fundamental unit of the glyph dispatch table.
 */
typedef int (*GlyphHandler)(GlyphEngine *engine, GlyphResult *result, 
                            int argc, char **argv);

struct GlyphAction {
    char            id[GLYPH_MAX_ID_LEN];   /* e.g., "C:PLN" */
    unsigned char   category;                 /* GLYPH_CAT_* */
    char            description[128];
    GlyphHandler    handler;                  /* Kernel function pointer */
    int             temporal_level;           /* TC_LEVEL_* for scheduling */
};

/*
 * GlyphSentence — A parsed noetic sentence.
 * Produced by the glyph parser from a raw string written to /dev/glyph.
 */
struct GlyphSentence {
    char    raw[GLYPH_MAX_SENTENCE];     /* Original sentence string */
    char    primary_glyph[GLYPH_MAX_ID_LEN]; /* Primary glyph ID */
    char    op;                          /* Operator: ?, !, -> */
    int     argc;                        /* Number of additional arguments */
    char    *argv[GLYPH_MAX_PARAMS];     /* Additional parameters */
};

/*
 * TemporalLevel — A single level in the time-crystal hierarchy.
 * Each level has a period, a list of registered cognitive modules,
 * and a phase counter for synchronization.
 */
struct TemporalLevel {
    int         id;                      /* TC_LEVEL_* */
    char        name[64];                /* Human-readable name */
    char        biological_analog[64];   /* Biological equivalent */
    long        period_us;               /* Period in microseconds */
    long        phase;                   /* Current phase counter */
    int         num_modules;             /* Number of registered modules */
    CogModule   *modules[16];            /* Registered cognitive modules */
    int         active;                  /* 1 if this level is running */
};

/*
 * CogModule — A cognitive processing module registered with the kernel.
 * Each module is bound to a temporal level and implements a specific
 * cognitive function (PLN, MOSES, ECAN, pattern matching, etc.).
 */
struct CogModule {
    char            id[32];              /* Module identifier */
    char            name[64];            /* Human-readable name */
    int             temporal_level;      /* Assigned TC level */
    int             active;              /* 1 if currently active */
    long            invocations;         /* Total invocation count */
    long            last_invoke_us;      /* Timestamp of last invocation */
    void            *state;              /* Module-specific state */
    int             (*tick)(CogModule *self, AtomSpace *as);
    int             (*query)(CogModule *self, GlyphResult *result);
};

/*
 * TopoComponent — A node in the Plan 9 cluster topology.
 * Represents a file server, CPU server, or auth server.
 */
struct TopoComponent {
    char    id[32];                      /* Component identifier */
    char    layer[32];                   /* "storage" or "compute" */
    char    subsystem[32];               /* "file-server", "cpu-server", etc. */
    int     num_ports;
    struct {
        char    name[32];
        char    kind[8];                 /* "BIDI", "SOURCE", "SINK" */
        char    dtype[16];               /* "9p", "9p_namespace" */
    } ports[8];
    int     state;                       /* 0=down, 1=up, 2=degraded */
};

/*
 * TopoConstraint — A topological invariant that must hold.
 */
struct TopoConstraint {
    char    name[64];
    int     dimension;                   /* Betti number dimension */
    char    op[4];                       /* "==", ">=", "<=" */
    int     value;                       /* Expected value */
    char    description[128];
    int     satisfied;                   /* Runtime: 1 if constraint holds */
};

/*
 * TopoAssembly — The complete topological model of the Plan 9 cluster.
 * Implements the RTSA (Runtime Topological Self-Assembly) framework.
 */
struct TopoAssembly {
    char            name[64];
    int             num_components;
    TopoComponent   components[16];
    int             num_constraints;
    TopoConstraint  constraints[8];
    
    /* Computed topological invariants */
    int             betti[4];            /* β₀, β₁, β₂, β₃ */
    int             euler_characteristic;
    int             all_constraints_ok;
    
    /* Simplicial complex representation */
    int             num_simplices[4];    /* Count by dimension */
    /* Adjacency matrix for Betti computation */
    int             adjacency[16][16];
};

/*
 * AtomSpace — The kernel-resident hypergraph knowledge store.
 * A simplified but functional AtomSpace for kernel-level operation.
 */
struct AtomSpace {
    int     num_atoms;
    int     num_links;
    int     capacity;
    Atom    *atoms;                      /* Dynamic array of atoms */
    long    version;                     /* Monotonic version counter */
};

/*
 * Atom — A single node or link in the AtomSpace hypergraph.
 */
struct Atom {
    long    id;                          /* Unique atom identifier */
    char    type[32];                    /* Atom type string */
    char    name[64];                    /* Atom name (for nodes) */
    double  tv_strength;                 /* Truth value: strength */
    double  tv_confidence;               /* Truth value: confidence */
    long    av_sti;                      /* Attention value: STI */
    long    av_lti;                      /* Attention value: LTI */
    int     num_outgoing;                /* Number of outgoing links */
    long    outgoing[16];                /* Outgoing atom IDs */
};

/*
 * GlyphEngine — The master cognitive engine structure.
 * This is the root object that owns all cognitive subsystems.
 * One instance exists per kernel, initialized at boot time.
 */
struct GlyphEngine {
    /* Identity */
    char            version[16];
    int             initialized;
    long            boot_time;
    
    /* Glyph dispatch table */
    int             num_glyphs;
    GlyphAction     glyph_map[GLYPH_MAP_SIZE];
    
    /* Temporal hierarchy (time-crystal scheduler) */
    TemporalLevel   temporal[TC_NUM_LEVELS];
    long            global_tick;         /* Master tick counter */
    
    /* Cognitive modules */
    int             num_modules;
    CogModule       *modules[32];
    
    /* Knowledge store */
    AtomSpace       atomspace;
    
    /* Topology */
    TopoAssembly    topology;
    
    /* Kernel promises */
    int             promises[NUM_KERNEL_PROMISES];
    
    /* Autognosis self-image */
    struct {
        double      awareness_score;
        double      convergence_factor;
        long        cycle_count;
        char        last_reflection[512];
    } autognosis;
    
    /* Statistics */
    long            total_sentences;
    long            total_errors;
};

/* ============================================================================
 * Function Prototypes: Core Engine
 * ============================================================================ */

/* Engine lifecycle */
GlyphEngine *glyph_engine_init(void);
void         glyph_engine_shutdown(GlyphEngine *engine);
GlyphEngine *glyph_engine_get(void);

/* Sentence parsing and dispatch */
int  glyph_parse_sentence(const char *raw, GlyphSentence *sentence);
int  glyph_dispatch(GlyphEngine *engine, GlyphSentence *sentence, 
                    GlyphResult *result);

/* Glyph map management */
int  glyph_register(GlyphEngine *engine, const GlyphAction *action);
GlyphAction *glyph_lookup(GlyphEngine *engine, const char *glyph_id);

/* Result management */
GlyphResult *glyph_result_new(void);
void         glyph_result_free(GlyphResult *result);
int          glyph_result_set_json(GlyphResult *result, const char *fmt, ...);
int          glyph_result_set_error(GlyphResult *result, int code, 
                                    const char *msg);

/* ============================================================================
 * Function Prototypes: Temporal Scheduler
 * ============================================================================ */

int  temporal_init(GlyphEngine *engine);
int  temporal_register_module(GlyphEngine *engine, CogModule *module, 
                              int level);
int  temporal_tick(GlyphEngine *engine);
int  temporal_get_level_status(GlyphEngine *engine, int level, 
                               GlyphResult *result);
int  temporal_get_hierarchy_status(GlyphEngine *engine, GlyphResult *result,
                                   int argc, char **argv);

/* ============================================================================
 * Function Prototypes: Topology Module (p9topo)
 * ============================================================================ */

int  topo_init(GlyphEngine *engine, const char *config_path);
int  topo_compute_betti(TopoAssembly *assembly);
int  topo_check_constraints(TopoAssembly *assembly);
int  topo_get_status(GlyphEngine *engine, GlyphResult *result,
                     int argc, char **argv);
int  topo_list_components(GlyphEngine *engine, GlyphResult *result,
                          int argc, char **argv);
int  topo_get_namespace_map(GlyphEngine *engine, GlyphResult *result,
                            int argc, char **argv);
int  topo_get_persistence(GlyphEngine *engine, GlyphResult *result,
                          int argc, char **argv);

/* ============================================================================
 * Function Prototypes: AtomSpace
 * ============================================================================ */

int   atomspace_init(AtomSpace *as, int capacity);
void  atomspace_destroy(AtomSpace *as);
long  atomspace_add_node(AtomSpace *as, const char *type, const char *name);
long  atomspace_add_link(AtomSpace *as, const char *type, 
                         long *outgoing, int num_outgoing);
Atom *atomspace_get(AtomSpace *as, long id);
int   atomspace_set_tv(AtomSpace *as, long id, double strength, 
                       double confidence);
int   atomspace_set_av(AtomSpace *as, long id, long sti, long lti);
int   atomspace_get_status(GlyphEngine *engine, GlyphResult *result,
                           int argc, char **argv);

/* ============================================================================
 * Function Prototypes: Cognitive Modules
 * ============================================================================ */

CogModule *cogmodule_pln_create(void);
CogModule *cogmodule_moses_create(void);
CogModule *cogmodule_pattern_create(void);
CogModule *cogmodule_attention_create(void);
CogModule *cogmodule_autognosis_create(void);

/* ============================================================================
 * Function Prototypes: /dev/glyph Device Driver
 * ============================================================================ */

void devglyph_init(void);
#ifdef GLYPH_KERNEL_SIMULATION
long devglyph_read(void *chanptr, void *buf, long n, long long offset);
long devglyph_write(void *chanptr, void *buf, long n, long long offset);
void devglyph_close(void *chanptr);
#else
long devglyph_read(Chan *c, void *buf, long n, vlong offset);
long devglyph_write(Chan *c, void *buf, long n, vlong offset);
void devglyph_close(Chan *c);
#endif

/* ============================================================================
 * Function Prototypes: Kernel Promises
 * ============================================================================ */

int  promises_validate_all(GlyphEngine *engine);
int  promises_get_status(GlyphEngine *engine, GlyphResult *result);

/* ============================================================================
 * Function Prototypes: Autognosis
 * ============================================================================ */

int  autognosis_observe(GlyphEngine *engine);
int  autognosis_build_self_image(GlyphEngine *engine);
int  autognosis_check_convergence(GlyphEngine *engine);
int  autognosis_get_status(GlyphEngine *engine, GlyphResult *result,
                           int argc, char **argv);

#endif /* _GLYPH_H_ */
