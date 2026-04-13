/**
 * OpenCog-Inferno Kernel Test Program
 * Demonstrates basic cognitive kernel functionality
 * 
 * Copyright (c) 2026 OpenCog Community
 */

#include "../kernel/cognitive_kernel.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void print_separator(void) {
    printf("\n");
    printf("========================================\n");
}

void print_atom(Atom* atom) {
    if (!atom) {
        printf("  NULL atom\n");
        return;
    }
    
    printf("  Atom[%lu]:\n", atom->handle);
    printf("    Type: %d\n", atom->type);
    if (atom->name) {
        printf("    Name: %s\n", atom->name);
    }
    printf("    TV: strength=%.2f, confidence=%.2f\n", 
           atom->tv.strength, atom->tv.confidence);
    printf("    AV: sti=%d, lti=%d, vlti=%d\n",
           atom->av.sti, atom->av.lti, atom->av.vlti);
    if (atom->outgoing_count > 0) {
        printf("    Outgoing: [");
        for (size_t i = 0; i < atom->outgoing_count; i++) {
            printf("%lu", atom->outgoing[i]->handle);
            if (i < atom->outgoing_count - 1) printf(", ");
        }
        printf("]\n");
    }
}

void pattern_match_callback(AtomHandle* match, size_t match_size, void* user_data) {
    int* count = (int*)user_data;
    (*count)++;
    
    printf("  Match %d: [", *count);
    for (size_t i = 0; i < match_size; i++) {
        printf("%lu", match[i]);
        if (i < match_size - 1) printf(", ");
    }
    printf("]\n");
}

int main(void) {
    printf("OpenCog-Inferno Kernel Test Program\n");
    printf("===================================\n\n");
    
    // Test 1: Kernel Initialization
    print_separator();
    printf("Test 1: Kernel Initialization\n");
    print_separator();
    
    if (cognitive_kernel_init() != 0) {
        fprintf(stderr, "Failed to initialize kernel\n");
        return 1;
    }
    
    AtomSpace* as = cognitive_kernel_atomspace();
    printf("Kernel initialized successfully\n");
    printf("AtomSpace capacity: %zu\n", as->atom_capacity);
    
    // Test 2: Create Concept Nodes
    print_separator();
    printf("Test 2: Create Concept Nodes\n");
    print_separator();
    
    AtomHandle cat = sys_atom_create(
        ATOM_TYPE_CONCEPT_NODE,
        "Cat",
        NULL, 0,
        tv_create(1.0f, 0.9f)
    );
    
    AtomHandle animal = sys_atom_create(
        ATOM_TYPE_CONCEPT_NODE,
        "Animal",
        NULL, 0,
        tv_create(1.0f, 1.0f)
    );
    
    AtomHandle mammal = sys_atom_create(
        ATOM_TYPE_CONCEPT_NODE,
        "Mammal",
        NULL, 0,
        tv_create(1.0f, 0.95f)
    );
    
    printf("Created 3 concept nodes:\n");
    printf("  Cat: %lu\n", cat);
    printf("  Animal: %lu\n", animal);
    printf("  Mammal: %lu\n", mammal);
    
    // Test 3: Create Inheritance Links
    print_separator();
    printf("Test 3: Create Inheritance Links\n");
    print_separator();
    
    AtomHandle outgoing1[] = { cat, mammal };
    AtomHandle link1 = sys_atom_create(
        ATOM_TYPE_INHERITANCE_LINK,
        NULL,
        outgoing1, 2,
        tv_create(0.95f, 0.9f)
    );
    
    AtomHandle outgoing2[] = { mammal, animal };
    AtomHandle link2 = sys_atom_create(
        ATOM_TYPE_INHERITANCE_LINK,
        NULL,
        outgoing2, 2,
        tv_create(1.0f, 1.0f)
    );
    
    printf("Created 2 inheritance links:\n");
    printf("  Cat -> Mammal: %lu\n", link1);
    printf("  Mammal -> Animal: %lu\n", link2);
    
    // Test 4: Retrieve and Display Atoms
    print_separator();
    printf("Test 4: Retrieve and Display Atoms\n");
    print_separator();
    
    Atom* cat_atom = sys_atom_get(cat);
    Atom* link1_atom = sys_atom_get(link1);
    
    printf("Retrieved atoms:\n");
    print_atom(cat_atom);
    print_atom(link1_atom);
    
    // Test 5: Update Truth Values
    print_separator();
    printf("Test 5: Update Truth Values\n");
    print_separator();
    
    printf("Original Cat truth value: strength=%.2f, confidence=%.2f\n",
           cat_atom->tv.strength, cat_atom->tv.confidence);
    
    sys_atom_set_tv(cat, tv_create(0.8f, 0.95f));
    cat_atom = sys_atom_get(cat);
    
    printf("Updated Cat truth value: strength=%.2f, confidence=%.2f\n",
           cat_atom->tv.strength, cat_atom->tv.confidence);
    
    // Test 6: Attention Allocation
    print_separator();
    printf("Test 6: Attention Allocation\n");
    print_separator();
    
    printf("Original Cat attention: sti=%d\n", cat_atom->av.sti);
    
    sys_attention_allocate(cat, 100);
    cat_atom = sys_atom_get(cat);
    
    printf("After allocation (+100): sti=%d\n", cat_atom->av.sti);
    
    sys_attention_allocate(cat, -50);
    cat_atom = sys_atom_get(cat);
    
    printf("After allocation (-50): sti=%d\n", cat_atom->av.sti);
    
    // Test 7: Pattern Matching
    print_separator();
    printf("Test 7: Pattern Matching\n");
    print_separator();
    
    printf("Finding all concept nodes:\n");
    int match_count = 0;
    sys_pattern_match(cat, pattern_match_callback, &match_count);
    printf("Total matches: %d\n", match_count);
    
    // Test 8: AtomSpace Statistics
    print_separator();
    printf("Test 8: AtomSpace Statistics\n");
    print_separator();
    
    printf("AtomSpace statistics:\n");
    printf("  Total atoms: %zu\n", as->atom_count);
    printf("  Version: %lu\n", as->version);
    printf("  Capacity: %zu\n", as->atom_capacity);
    
    // Test 9: Knowledge Graph Traversal
    print_separator();
    printf("Test 9: Knowledge Graph Traversal\n");
    print_separator();
    
    printf("Traversing: Cat -> Mammal -> Animal\n");
    
    Atom* current = cat_atom;
    printf("Start: %s (handle=%lu)\n", current->name, current->handle);
    
    // Find inheritance link from Cat
    for (size_t i = 0; i < as->atom_count; i++) {
        Atom* a = as->atoms[i];
        if (a && a->type == ATOM_TYPE_INHERITANCE_LINK && 
            a->outgoing_count > 0 && a->outgoing[0]->handle == current->handle) {
            current = a->outgoing[1];
            printf("  -> %s (handle=%lu, tv=%.2f)\n", 
                   current->name, current->handle, a->tv.strength);
            break;
        }
    }
    
    // Find inheritance link from Mammal
    for (size_t i = 0; i < as->atom_count; i++) {
        Atom* a = as->atoms[i];
        if (a && a->type == ATOM_TYPE_INHERITANCE_LINK && 
            a->outgoing_count > 0 && a->outgoing[0]->handle == current->handle) {
            current = a->outgoing[1];
            printf("  -> %s (handle=%lu, tv=%.2f)\n", 
                   current->name, current->handle, a->tv.strength);
            break;
        }
    }
    
    // Test 10: Cleanup
    print_separator();
    printf("Test 10: Cleanup\n");
    print_separator();
    
    cognitive_kernel_shutdown();
    printf("Kernel shutdown complete\n");
    
    print_separator();
    printf("\nAll tests completed successfully!\n");
    
    return 0;
}
