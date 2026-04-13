/**
 * OpenCog-Inferno Kernel Implementation
 * Core kernel functions for cognitive operating system
 * 
 * Copyright (c) 2026 OpenCog Community
 * Licensed under AGPL-3.0
 */

#define _GNU_SOURCE

#include "cognitive_kernel.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <pthread.h>

/* ========================================================================
 * GLOBAL KERNEL STATE
 * ======================================================================== */

static AtomSpace* g_kernel_atomspace = NULL;
static pthread_rwlock_t g_atomspace_lock;
static bool g_kernel_initialized = false;

/* ========================================================================
 * ATOMSPACE IMPLEMENTATION
 * ======================================================================== */

/**
 * Create a new AtomSpace
 */
static AtomSpace* atomspace_create(void) {
    AtomSpace* as = (AtomSpace*)calloc(1, sizeof(AtomSpace));
    if (!as) return NULL;
    
    as->next_handle = 1;
    as->atom_capacity = 1024;
    as->atoms = (Atom**)calloc(as->atom_capacity, sizeof(Atom*));
    
    if (!as->atoms) {
        free(as);
        return NULL;
    }
    
    // Initialize indices (simplified - would use hash tables in production)
    as->name_index = NULL;  // TODO: Implement hash table
    as->type_index = NULL;  // TODO: Implement hash table
    as->incoming_index = NULL;  // TODO: Implement hash table
    
    as->version = 0;
    
    return as;
}

/**
 * Destroy an AtomSpace
 */
static void atomspace_destroy(AtomSpace* as) {
    if (!as) return;
    
    // Free all atoms
    for (size_t i = 0; i < as->atom_count; i++) {
        if (as->atoms[i]) {
            if (as->atoms[i]->name) free(as->atoms[i]->name);
            if (as->atoms[i]->outgoing) free(as->atoms[i]->outgoing);
            free(as->atoms[i]);
        }
    }
    
    free(as->atoms);
    free(as);
}

/**
 * Add an atom to the AtomSpace
 */
static AtomHandle atomspace_add_atom(AtomSpace* as, Atom* atom) {
    if (!as || !atom) return INVALID_ATOM_HANDLE;
    
    // Expand capacity if needed
    if (as->atom_count >= as->atom_capacity) {
        size_t new_capacity = as->atom_capacity * 2;
        Atom** new_atoms = (Atom**)realloc(as->atoms, new_capacity * sizeof(Atom*));
        if (!new_atoms) return INVALID_ATOM_HANDLE;
        
        as->atoms = new_atoms;
        as->atom_capacity = new_capacity;
    }
    
    // Assign handle and add to array
    atom->handle = as->next_handle++;
    as->atoms[as->atom_count++] = atom;
    as->version++;
    
    return atom->handle;
}

/**
 * Find an atom by handle
 */
static Atom* atomspace_get_atom(AtomSpace* as, AtomHandle handle) {
    if (!as || handle == INVALID_ATOM_HANDLE) return NULL;
    
    // Linear search (would use hash table in production)
    for (size_t i = 0; i < as->atom_count; i++) {
        if (as->atoms[i] && as->atoms[i]->handle == handle) {
            return as->atoms[i];
        }
    }
    
    return NULL;
}

/* ========================================================================
 * KERNEL INITIALIZATION
 * ======================================================================== */

int cognitive_kernel_init(void) {
    if (g_kernel_initialized) {
        fprintf(stderr, "Cognitive kernel already initialized\n");
        return -1;
    }
    
    // Initialize read-write lock
    if (pthread_rwlock_init(&g_atomspace_lock, NULL) != 0) {
        fprintf(stderr, "Failed to initialize atomspace lock\n");
        return -1;
    }
    
    // Create kernel AtomSpace
    g_kernel_atomspace = atomspace_create();
    if (!g_kernel_atomspace) {
        fprintf(stderr, "Failed to create kernel AtomSpace\n");
        pthread_rwlock_destroy(&g_atomspace_lock);
        return -1;
    }
    
    g_kernel_initialized = true;
    
    printf("OpenCog-Inferno Kernel initialized\n");
    printf("  AtomSpace capacity: %zu atoms\n", g_kernel_atomspace->atom_capacity);
    printf("  Cognitive system calls: enabled\n");
    
    return 0;
}

void cognitive_kernel_shutdown(void) {
    if (!g_kernel_initialized) return;
    
    printf("Shutting down OpenCog-Inferno Kernel...\n");
    
    // Destroy kernel AtomSpace
    if (g_kernel_atomspace) {
        printf("  Cleaning up %zu atoms\n", g_kernel_atomspace->atom_count);
        atomspace_destroy(g_kernel_atomspace);
        g_kernel_atomspace = NULL;
    }
    
    // Destroy lock
    pthread_rwlock_destroy(&g_atomspace_lock);
    
    g_kernel_initialized = false;
    printf("Kernel shutdown complete\n");
}

AtomSpace* cognitive_kernel_atomspace(void) {
    return g_kernel_atomspace;
}

/* ========================================================================
 * COGNITIVE SYSTEM CALLS
 * ======================================================================== */

AtomHandle sys_atom_create(AtomType type, const char* name, 
                           AtomHandle* outgoing, size_t outgoing_count,
                           TruthValue tv) {
    if (!g_kernel_initialized) {
        fprintf(stderr, "Kernel not initialized\n");
        return INVALID_ATOM_HANDLE;
    }
    
    // Allocate new atom
    Atom* atom = (Atom*)calloc(1, sizeof(Atom));
    if (!atom) return INVALID_ATOM_HANDLE;
    
    atom->type = type;
    atom->tv = tv;
    atom->av = av_default();
    
    // Copy name for nodes
    if (name) {
        atom->name = strdup(name);
        if (!atom->name) {
            free(atom);
            return INVALID_ATOM_HANDLE;
        }
    }
    
    // Copy outgoing set for links
    if (outgoing_count > 0 && outgoing) {
        atom->outgoing = (Atom**)malloc(outgoing_count * sizeof(Atom*));
        if (!atom->outgoing) {
            if (atom->name) free(atom->name);
            free(atom);
            return INVALID_ATOM_HANDLE;
        }
        
        // Resolve handles to atom pointers
        for (size_t i = 0; i < outgoing_count; i++) {
            atom->outgoing[i] = atomspace_get_atom(g_kernel_atomspace, outgoing[i]);
            if (!atom->outgoing[i]) {
                fprintf(stderr, "Invalid outgoing atom handle: %lu\n", outgoing[i]);
                free(atom->outgoing);
                if (atom->name) free(atom->name);
                free(atom);
                return INVALID_ATOM_HANDLE;
            }
        }
        
        atom->outgoing_count = outgoing_count;
    }
    
    // Add to kernel AtomSpace
    pthread_rwlock_wrlock(&g_atomspace_lock);
    AtomHandle handle = atomspace_add_atom(g_kernel_atomspace, atom);
    pthread_rwlock_unlock(&g_atomspace_lock);
    
    return handle;
}

Atom* sys_atom_get(AtomHandle handle) {
    if (!g_kernel_initialized) return NULL;
    
    pthread_rwlock_rdlock(&g_atomspace_lock);
    Atom* atom = atomspace_get_atom(g_kernel_atomspace, handle);
    pthread_rwlock_unlock(&g_atomspace_lock);
    
    return atom;
}

int sys_atom_delete(AtomHandle handle) {
    if (!g_kernel_initialized) return -1;
    
    pthread_rwlock_wrlock(&g_atomspace_lock);
    
    Atom* atom = atomspace_get_atom(g_kernel_atomspace, handle);
    if (!atom) {
        pthread_rwlock_unlock(&g_atomspace_lock);
        return -1;
    }
    
    // Free atom memory
    if (atom->name) free(atom->name);
    if (atom->outgoing) free(atom->outgoing);
    
    // Remove from array (simplified - would use better data structure)
    for (size_t i = 0; i < g_kernel_atomspace->atom_count; i++) {
        if (g_kernel_atomspace->atoms[i] == atom) {
            free(atom);
            g_kernel_atomspace->atoms[i] = NULL;
            g_kernel_atomspace->version++;
            break;
        }
    }
    
    pthread_rwlock_unlock(&g_atomspace_lock);
    return 0;
}

int sys_atom_set_tv(AtomHandle handle, TruthValue tv) {
    if (!g_kernel_initialized) return -1;
    
    pthread_rwlock_wrlock(&g_atomspace_lock);
    
    Atom* atom = atomspace_get_atom(g_kernel_atomspace, handle);
    if (!atom) {
        pthread_rwlock_unlock(&g_atomspace_lock);
        return -1;
    }
    
    atom->tv = tv;
    g_kernel_atomspace->version++;
    
    pthread_rwlock_unlock(&g_atomspace_lock);
    return 0;
}

int sys_atom_set_av(AtomHandle handle, AttentionValue av) {
    if (!g_kernel_initialized) return -1;
    
    pthread_rwlock_wrlock(&g_atomspace_lock);
    
    Atom* atom = atomspace_get_atom(g_kernel_atomspace, handle);
    if (!atom) {
        pthread_rwlock_unlock(&g_atomspace_lock);
        return -1;
    }
    
    atom->av = av;
    g_kernel_atomspace->version++;
    
    pthread_rwlock_unlock(&g_atomspace_lock);
    return 0;
}

int sys_pattern_match(AtomHandle pattern, PatternMatchCallback callback, void* user_data) {
    if (!g_kernel_initialized || !callback) return -1;
    
    // Simplified pattern matching - just find atoms of same type
    pthread_rwlock_rdlock(&g_atomspace_lock);
    
    Atom* pattern_atom = atomspace_get_atom(g_kernel_atomspace, pattern);
    if (!pattern_atom) {
        pthread_rwlock_unlock(&g_atomspace_lock);
        return -1;
    }
    
    int match_count = 0;
    
    // Find all atoms of the same type
    for (size_t i = 0; i < g_kernel_atomspace->atom_count; i++) {
        Atom* atom = g_kernel_atomspace->atoms[i];
        if (atom && atom->type == pattern_atom->type && atom->handle != pattern) {
            AtomHandle match = atom->handle;
            callback(&match, 1, user_data);
            match_count++;
        }
    }
    
    pthread_rwlock_unlock(&g_atomspace_lock);
    return match_count;
}

int sys_pln_infer(AtomHandle rule, AtomHandle* premises, 
                  size_t premise_count, AtomHandle* conclusion) {
    // Stub implementation - would integrate with PLN engine
    fprintf(stderr, "PLN inference not yet implemented\n");
    return -1;
}

int sys_moses_evolve(struct MOSESPopulation* population, 
                     FitnessFunction fitness_fn, void* user_data) {
    // Stub implementation - would integrate with MOSES
    fprintf(stderr, "MOSES evolution not yet implemented\n");
    return -1;
}

int sys_attention_allocate(AtomHandle handle, int16_t sti_delta) {
    if (!g_kernel_initialized) return -1;
    
    pthread_rwlock_wrlock(&g_atomspace_lock);
    
    Atom* atom = atomspace_get_atom(g_kernel_atomspace, handle);
    if (!atom) {
        pthread_rwlock_unlock(&g_atomspace_lock);
        return -1;
    }
    
    // Update short-term importance
    atom->av.sti += sti_delta;
    
    // Clamp to valid range
    if (atom->av.sti < -32768) atom->av.sti = -32768;
    if (atom->av.sti > 32767) atom->av.sti = 32767;
    
    pthread_rwlock_unlock(&g_atomspace_lock);
    return 0;
}

int sys_cognitive_channel_create(uint32_t target_pid, const char* channel_name) {
    // Stub implementation - would integrate with IPC system
    fprintf(stderr, "Cognitive channels not yet implemented\n");
    return -1;
}

int sys_cognitive_channel_send(int channel_id, AtomHandle* atoms, size_t atom_count) {
    // Stub implementation
    fprintf(stderr, "Cognitive channels not yet implemented\n");
    return -1;
}

int sys_cognitive_channel_recv(int channel_id, AtomHandle* atoms, size_t max_atoms) {
    // Stub implementation
    fprintf(stderr, "Cognitive channels not yet implemented\n");
    return -1;
}
