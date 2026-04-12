/**
 * OpenCog-Inferno Kernel
 * Cognitive Operating System Kernel Header
 * 
 * This header defines the core kernel structures and interfaces for
 * the OpenCog-Inferno cognitive operating system.
 * 
 * Copyright (c) 2026 OpenCog Community
 * Licensed under AGPL-3.0
 */

#ifndef _COGNITIVE_KERNEL_H_
#define _COGNITIVE_KERNEL_H_

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* ========================================================================
 * CORE COGNITIVE TYPES
 * ======================================================================== */

/**
 * Atom Handle - Unique identifier for atoms in the AtomSpace
 */
typedef uint64_t AtomHandle;

#define INVALID_ATOM_HANDLE 0

/**
 * Atom Type - Defines the type of an atom
 */
typedef enum {
    // Basic node types
    ATOM_TYPE_NODE = 1,
    ATOM_TYPE_CONCEPT_NODE,
    ATOM_TYPE_PREDICATE_NODE,
    ATOM_TYPE_SCHEMA_NODE,
    ATOM_TYPE_VARIABLE_NODE,
    
    // Link types
    ATOM_TYPE_LINK = 100,
    ATOM_TYPE_INHERITANCE_LINK,
    ATOM_TYPE_SIMILARITY_LINK,
    ATOM_TYPE_EVALUATION_LINK,
    ATOM_TYPE_EXECUTION_LINK,
    ATOM_TYPE_LIST_LINK,
    ATOM_TYPE_AND_LINK,
    ATOM_TYPE_OR_LINK,
    ATOM_TYPE_NOT_LINK,
    ATOM_TYPE_IMPLICATION_LINK,
    
    // Truth value types
    ATOM_TYPE_SIMPLE_TRUTH_VALUE = 200,
    ATOM_TYPE_FUZZY_TRUTH_VALUE,
    ATOM_TYPE_PROBABILISTIC_TRUTH_VALUE,
    
    ATOM_TYPE_MAX = 1000
} AtomType;

/**
 * Truth Value - Represents uncertainty and confidence
 */
typedef struct {
    float strength;     // [0.0, 1.0] - degree of truth
    float confidence;   // [0.0, 1.0] - confidence in the strength
} TruthValue;

/**
 * Attention Value - Represents importance and focus
 */
typedef struct {
    int16_t sti;        // Short-term importance
    int16_t lti;        // Long-term importance
    int16_t vlti;       // Very long-term importance
} AttentionValue;

/**
 * Atom - Core cognitive primitive
 */
typedef struct Atom {
    AtomHandle handle;
    AtomType type;
    char* name;             // For nodes
    struct Atom** outgoing; // For links
    size_t outgoing_count;
    TruthValue tv;
    AttentionValue av;
    uint64_t flags;
    void* metadata;
} Atom;

/* ========================================================================
 * COGNITIVE PROCESS STRUCTURES
 * ======================================================================== */

/**
 * Cognitive Process - Extended process with cognitive capabilities
 */
typedef struct CognitiveProcess {
    // Traditional process fields
    uint32_t pid;
    uint32_t parent_pid;
    void* memory_space;
    uint64_t cpu_time;
    
    // Cognitive extensions
    struct AtomSpace* local_atomspace;
    struct PLNContext* reasoning_context;
    struct AttentionBank* attention_bank;
    struct MOSESPopulation* learning_state;
    
    // Distributed cognition
    struct DistributedAtomSpace* shared_knowledge;
    struct CognitiveChannel** cognitive_channels;
    size_t channel_count;
    
    // Resource limits
    size_t max_atoms;
    size_t max_attention;
    uint64_t max_inference_steps;
    
    // Statistics
    uint64_t atoms_created;
    uint64_t inferences_performed;
    uint64_t patterns_matched;
} CognitiveProcess;

/**
 * AtomSpace - Kernel-level hypergraph knowledge base
 */
typedef struct AtomSpace {
    AtomHandle next_handle;
    Atom** atoms;
    size_t atom_count;
    size_t atom_capacity;
    
    // Type hierarchy
    AtomType* type_hierarchy;
    size_t type_count;
    
    // Indices for fast lookup
    void* name_index;       // Hash table: name -> atom
    void* type_index;       // Hash table: type -> atoms
    void* incoming_index;   // Hash table: atom -> incoming links
    
    // Distributed sync
    uint64_t version;
    struct DistributedAtomSpace* distributed;
    
    // Lock-free access
    void* lock_free_queue;
} AtomSpace;

/* ========================================================================
 * COGNITIVE SYSTEM CALLS
 * ======================================================================== */

/**
 * Create a new atom in the kernel AtomSpace
 * 
 * @param type The type of atom to create
 * @param name The name of the atom (for nodes)
 * @param outgoing Array of outgoing atoms (for links)
 * @param outgoing_count Number of outgoing atoms
 * @param tv Truth value
 * @return Handle to the created atom, or INVALID_ATOM_HANDLE on error
 */
AtomHandle sys_atom_create(AtomType type, const char* name, 
                           AtomHandle* outgoing, size_t outgoing_count,
                           TruthValue tv);

/**
 * Get an atom by its handle
 * 
 * @param handle The atom handle
 * @return Pointer to the atom, or NULL if not found
 */
Atom* sys_atom_get(AtomHandle handle);

/**
 * Delete an atom from the AtomSpace
 * 
 * @param handle The atom handle to delete
 * @return 0 on success, -1 on error
 */
int sys_atom_delete(AtomHandle handle);

/**
 * Update an atom's truth value
 * 
 * @param handle The atom handle
 * @param tv The new truth value
 * @return 0 on success, -1 on error
 */
int sys_atom_set_tv(AtomHandle handle, TruthValue tv);

/**
 * Update an atom's attention value
 * 
 * @param handle The atom handle
 * @param av The new attention value
 * @return 0 on success, -1 on error
 */
int sys_atom_set_av(AtomHandle handle, AttentionValue av);

/**
 * Pattern Matching - Execute a pattern query
 * 
 * @param pattern The pattern to match
 * @param callback Callback function for each match
 * @param user_data User data passed to callback
 * @return Number of matches found, or -1 on error
 */
typedef void (*PatternMatchCallback)(AtomHandle* match, size_t match_size, void* user_data);

int sys_pattern_match(AtomHandle pattern, PatternMatchCallback callback, void* user_data);

/**
 * PLN Inference - Perform a single inference step
 * 
 * @param rule The inference rule to apply
 * @param premises Array of premise atoms
 * @param premise_count Number of premises
 * @param conclusion Output: the inferred conclusion
 * @return 0 on success, -1 on error
 */
int sys_pln_infer(AtomHandle rule, AtomHandle* premises, 
                  size_t premise_count, AtomHandle* conclusion);

/**
 * MOSES Evolution - Run one generation of evolutionary learning
 * 
 * @param population The current population
 * @param fitness_fn Fitness evaluation function
 * @param user_data User data for fitness function
 * @return 0 on success, -1 on error
 */
typedef float (*FitnessFunction)(AtomHandle program, void* user_data);

int sys_moses_evolve(struct MOSESPopulation* population, 
                     FitnessFunction fitness_fn, void* user_data);

/**
 * Attention Allocation - Allocate attention to an atom
 * 
 * @param handle The atom to allocate attention to
 * @param sti_delta Change in short-term importance
 * @return 0 on success, -1 on error
 */
int sys_attention_allocate(AtomHandle handle, int16_t sti_delta);

/**
 * Create a cognitive IPC channel
 * 
 * @param target_pid The process to communicate with
 * @param channel_name Name of the channel
 * @return Channel ID on success, -1 on error
 */
int sys_cognitive_channel_create(uint32_t target_pid, const char* channel_name);

/**
 * Send atoms through a cognitive channel
 * 
 * @param channel_id The channel ID
 * @param atoms Array of atoms to send
 * @param atom_count Number of atoms
 * @return Number of atoms sent, or -1 on error
 */
int sys_cognitive_channel_send(int channel_id, AtomHandle* atoms, size_t atom_count);

/**
 * Receive atoms from a cognitive channel
 * 
 * @param channel_id The channel ID
 * @param atoms Output buffer for atoms
 * @param max_atoms Maximum number of atoms to receive
 * @return Number of atoms received, or -1 on error
 */
int sys_cognitive_channel_recv(int channel_id, AtomHandle* atoms, size_t max_atoms);

/* ========================================================================
 * KERNEL INITIALIZATION
 * ======================================================================== */

/**
 * Initialize the cognitive kernel
 * 
 * @return 0 on success, -1 on error
 */
int cognitive_kernel_init(void);

/**
 * Shutdown the cognitive kernel
 */
void cognitive_kernel_shutdown(void);

/**
 * Get the kernel AtomSpace
 * 
 * @return Pointer to the kernel AtomSpace
 */
AtomSpace* cognitive_kernel_atomspace(void);

/* ========================================================================
 * UTILITY FUNCTIONS
 * ======================================================================== */

/**
 * Create a simple truth value
 */
static inline TruthValue tv_create(float strength, float confidence) {
    TruthValue tv = { strength, confidence };
    return tv;
}

/**
 * Create a default truth value (strength=1.0, confidence=1.0)
 */
static inline TruthValue tv_default(void) {
    return tv_create(1.0f, 1.0f);
}

/**
 * Create an attention value
 */
static inline AttentionValue av_create(int16_t sti, int16_t lti, int16_t vlti) {
    AttentionValue av = { sti, lti, vlti };
    return av;
}

/**
 * Create a default attention value (all zeros)
 */
static inline AttentionValue av_default(void) {
    return av_create(0, 0, 0);
}

#endif /* _COGNITIVE_KERNEL_H_ */
