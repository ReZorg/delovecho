#
# cogkernel_glyph.b — Limbo Module: Glyph-Noetic Kernel Interface
#
# This Limbo module provides the user-space interface to the
# kernel-resident Glyph-Noetic Engine via /dev/glyph.
#
# It demonstrates:
#   - Writing noetic sentences to /dev/glyph
#   - Reading JSON results
#   - Temporal level constants from time-crystal-nn
#   - Autognosis self-image access
#   - Topology health monitoring
#
# Compile: limbo cogkernel_glyph.b
# Run:     cogkernel_glyph [glyph-sentence]
#
# Copyright (c) 2026 ManusCog Project
# License: AGPL-3.0
#

implement CogKernelGlyph;

include "sys.m";
    sys: Sys;
include "draw.m";
include "bufio.m";
    bufio: Bufio;
    Iobuf: import bufio;

CogKernelGlyph: module {
    init: fn(nil: ref Draw->Context, argv: list of string);
};

# ============================================================================
# Constants: Temporal Hierarchy (from /time-crystal-neuron)
# ============================================================================

TC_LEVEL_QUANTUM:       con 0;    # 1μs  — Quantum resonance
TC_LEVEL_PROTEIN:       con 1;    # 8ms  — Protein dynamics
TC_LEVEL_ION_CHANNEL:   con 2;    # 26ms — Ion channel gating
TC_LEVEL_MEMBRANE:      con 3;    # 52ms — Membrane dynamics
TC_LEVEL_AIS:           con 4;    # 110ms — Axon initial segment
TC_LEVEL_DENDRITIC:     con 5;    # 160ms — Dendritic integration
TC_LEVEL_SYNAPTIC:      con 6;    # 250ms — Synaptic plasticity
TC_LEVEL_SOMA:          con 7;    # 330ms — Soma processing
TC_LEVEL_NETWORK:       con 8;    # 500ms — Network synchronization
TC_LEVEL_GLOBAL:        con 9;    # 1000ms — Global rhythm
TC_LEVEL_CIRCADIAN:     con 10;   # 60s — Circadian modulation
TC_LEVEL_HOMEOSTATIC:   con 11;   # 3600s — Homeostatic regulation

# Glyph device path
GLYPH_DEV: con "/dev/glyph";

# ============================================================================
# Core Functions
# ============================================================================

# Send a noetic sentence to the kernel and return the result
glyph_query(sentence: string): string
{
    # Open /dev/glyph for writing
    fd := sys->open(GLYPH_DEV, Sys->ORDWR);
    if (fd == nil) {
        sys->fprint(sys->fildes(2), "Error: cannot open %s: %r\n", GLYPH_DEV);
        return "ERROR: /dev/glyph not available";
    }

    # Write the noetic sentence
    data := array of byte sentence;
    n := sys->write(fd, data, len data);
    if (n < 0) {
        sys->fprint(sys->fildes(2), "Error: write to %s failed: %r\n", GLYPH_DEV);
        return "ERROR: write failed";
    }

    # Read the result
    buf := array[65536] of byte;
    n = sys->read(fd, buf, len buf);
    if (n < 0) {
        sys->fprint(sys->fildes(2), "Error: read from %s failed: %r\n", GLYPH_DEV);
        return "ERROR: read failed";
    }

    return string buf[0:n];
}

# Query a specific temporal level
query_temporal_level(level: int): string
{
    glyphs := array[] of {
        "[T~q]?",   # L0: Quantum
        "[T~p]?",   # L1: Protein
        "[T~i]?",   # L2: Ion channel
        "[T~m]?",   # L3: Membrane
        "[T~a]?",   # L4: AIS
        "[T~d]?",   # L5: Dendritic
        "[T~s]?",   # L6: Synaptic
        "[T~o]?",   # L7: Soma
        "[T~n]?",   # L8: Network
        "[T~g]?",   # L9: Global
        "[T~c]?",   # L10: Circadian
        "[T~h]?",   # L11: Homeostatic
    };

    if (level < 0 || level >= len glyphs)
        return "ERROR: invalid temporal level";

    return glyph_query(glyphs[level]);
}

# Run a complete cognitive health check
cognitive_health_check(): string
{
    result := "";

    # 1. Engine status
    result += "=== Engine Status ===\n";
    result += glyph_query("[K:STATUS]?") + "\n\n";

    # 2. Temporal hierarchy
    result += "=== Temporal Hierarchy ===\n";
    result += glyph_query("[T-HIERARCHY]?") + "\n\n";

    # 3. Topology health
    result += "=== Topology Health ===\n";
    result += glyph_query("[T:ASSEMBLY]?") + "\n\n";

    # 4. AtomSpace status
    result += "=== AtomSpace ===\n";
    result += glyph_query("[S:ATOMSPACE]?") + "\n\n";

    # 5. Kernel promises
    result += "=== Kernel Promises ===\n";
    result += glyph_query("[K:PROMISES]?") + "\n\n";

    # 6. Autognosis self-image
    result += "=== Autognosis ===\n";
    result += glyph_query("[N:DECISION]?") + "\n\n";

    # 7. Namespace map
    result += "=== Cognitive Namespace ===\n";
    result += glyph_query("[P:NS]?") + "\n\n";

    # 8. Persistence diagram
    result += "=== Persistence Diagram ===\n";
    result += glyph_query("[T:PERSIST]?") + "\n";

    return result;
}

# ============================================================================
# Main Entry Point
# ============================================================================

init(nil: ref Draw->Context, argv: list of string)
{
    sys = load Sys Sys->PATH;
    bufio = load Bufio Bufio->PATH;

    argv = tl argv;  # Skip program name

    if (argv == nil) {
        # No arguments: run interactive mode
        sys->print("Glyph-Noetic Kernel Interface (Limbo)\n");
        sys->print("Usage: cogkernel_glyph [sentence | --health | --glyphs]\n\n");

        # Default: show engine status
        result := glyph_query("[K:STATUS]?");
        sys->print("%s\n", result);
        return;
    }

    cmd := hd argv;

    case cmd {
    "--health" =>
        # Full cognitive health check
        sys->print("%s", cognitive_health_check());

    "--glyphs" =>
        # List all registered glyphs
        result := glyph_query("[K:GLYPHS]?");
        sys->print("%s\n", result);

    "--temporal" =>
        # Show temporal hierarchy
        result := glyph_query("[T-HIERARCHY]?");
        sys->print("%s\n", result);

    "--topology" =>
        # Show topology status
        result := glyph_query("[T:ASSEMBLY]?");
        sys->print("%s\n", result);

    "--autognosis" =>
        # Show autognosis self-image
        result := glyph_query("[N:DECISION]?");
        sys->print("%s\n", result);

    "--promises" =>
        # Show kernel promises
        result := glyph_query("[K:PROMISES]?");
        sys->print("%s\n", result);

    "--namespace" =>
        # Show cognitive namespace
        result := glyph_query("[P:NS]?");
        sys->print("%s\n", result);

    * =>
        # Treat the argument as a noetic sentence
        sentence := "";
        for (a := argv; a != nil; a = tl a) {
            if (sentence != "")
                sentence += " ";
            sentence += hd a;
        }
        result := glyph_query(sentence);
        sys->print("%s\n", result);
    }
}
