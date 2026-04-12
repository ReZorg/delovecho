#!/usr/bin/env python3
"""
Time Crystal Neuron Model Generator

Generates a time crystal neuron model specification for a given context,
mapping domain concepts to the hierarchical temporal structure from
Nanobrain Figure 6.14.

Usage:
    python generate_tcn_model.py --context "language processing" --output model.json
    python generate_tcn_model.py --context "financial markets" --structure 3,4,3,3
"""

import argparse
import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from math import gcd
from functools import reduce

# Temporal scales from the generalized neuron model (in seconds)
TEMPORAL_SCALES = {
    "ultra_fast": 0.008,      # 8ms
    "fast": 0.026,            # 26ms
    "medium_fast": 0.052,     # 52ms
    "medium": 0.11,           # 0.11s
    "medium_slow": 0.16,      # 0.16s
    "slow": 0.25,             # 0.25s
    "very_slow": 0.33,        # 0.33s
    "ultra_slow": 0.5,        # 0.5s
    "slowest": 1.0            # 1s
}

# Component categories
COMPONENT_CATEGORIES = {
    "feedback": ["Fi-lo", "Fi-fe", "Mi-fm", "β-sp-A", "A"],
    "rhythm": ["Rh", "Io", "Ep", "Me-Rh"],
    "morphological": ["Ca", "Bi", "Py", "Ui-p", "Mu-p"],
    "mechanical": ["Au", "Bu", "Ch-Co"],
    "anatomic": ["AIS[3]", "Mu-in", "Mo-n", "Se-n", "An-n", "En-re-Mi", 
                 "P-As", "PNN", "G", "Br", "Li", "Ax", "Ac", "Me", "Io-Ch", "Pr-Ch(3)"],
    "junction": ["Ax-d", "Ax-s", "Ax-Ax-d", "Ax-x", "El", "GlS", "Gl", "Sy-c", "Sn-cl-co", "Nt"]
}

# Default components at each temporal scale
SCALE_COMPONENTS = {
    "ultra_fast": ["Ax", "Pr-Ch(3)"],
    "fast": ["Io-Ch", "Li", "Ax"],
    "medium_fast": ["Me", "Ac", "Li"],
    "medium": ["AIS[3]", "An-n", "En-re-Mi", "P-As", "An"],
    "medium_slow": ["Ch-Co", "Ac", "Se-n", "Br", "PNN"],
    "slow": ["Ca", "Mu-p", "Fi-lo", "Ax-d", "Ax-s", "Ax-s-d", "Sn-cl-co"],
    "very_slow": ["Rh", "Ep", "Io", "Mi-fm", "A", "Jn", "Soma", "β-sp-A", "Fi-fe", "Mo-n", "Mu-in", "Br", "Li"],
    "ultra_slow": ["Bu", "Au", "Gl-S", "Nt", "El", "Ax-s-d", "Jn", "Gl"],
    "slowest": ["Me-Rh", "Fi-lo", "Ui-p", "Bi", "Bu", "Gl-S", "Ax-Ax-d", "Io", "Mo-n", "G", "P-As", "El", "Nt", "Ax-d", "Ac", "Sy-c"]
}


@dataclass
class Component:
    """A component in the time crystal neuron model."""
    name: str
    abbreviation: str
    temporal_scale: str
    period: float
    category: str
    context_mapping: Optional[str] = None


@dataclass
class Layer:
    """A functional layer containing components at multiple scales."""
    name: str
    components: List[Component] = field(default_factory=list)
    

@dataclass
class Domain:
    """A spatial domain containing multiple layers."""
    name: str
    layers: List[Layer] = field(default_factory=list)


@dataclass
class TimeCrystalNeuron:
    """Complete time crystal neuron model."""
    context: str
    structure: List[int]  # [a, b, c, d]
    domains: List[Domain] = field(default_factory=list)
    cycle_length: float = 0.0
    universal_sets: List[str] = field(default_factory=list)
    particular_sets: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)


def lcm(a: int, b: int) -> int:
    """Compute least common multiple."""
    return abs(a * b) // gcd(a, b)


def compute_cycle_length(periods: List[float]) -> float:
    """Compute the cycle length as LCM of periods (in ms for precision)."""
    periods_ms = [int(p * 1000) for p in periods]
    return reduce(lcm, periods_ms) / 1000


def categorize_component(abbrev: str) -> str:
    """Determine the category of a component."""
    for category, components in COMPONENT_CATEGORIES.items():
        if abbrev in components:
            return category
    return "other"


def generate_context_mapping(context: str, scale: str, abbrev: str) -> str:
    """Generate a context-specific mapping for a component."""
    # Default mappings for common contexts
    mappings = {
        "language": {
            "ultra_fast": {"Ax": "character_encoding", "Pr-Ch(3)": "byte_stream"},
            "fast": {"Io-Ch": "token_boundary", "Li": "embedding_layer"},
            "medium_fast": {"Me": "token_embedding", "Ac": "positional_encoding"},
            "medium": {"AIS[3]": "attention_head", "An-n": "local_context"},
            "medium_slow": {"PNN": "phrase_structure", "Br": "syntax_tree"},
            "slow": {"Fi-lo": "semantic_feedback", "Ax-d": "cross_attention"},
            "very_slow": {"Soma": "sentence_repr", "Rh": "discourse_rhythm"},
            "ultra_slow": {"Nt": "context_signal", "El": "skip_connection"},
            "slowest": {"Me-Rh": "document_context", "Bi": "bidirectional"}
        },
        "financial": {
            "ultra_fast": {"Ax": "tick_data", "Pr-Ch(3)": "order_flow"},
            "fast": {"Io-Ch": "bid_ask_spread", "Li": "price_level"},
            "medium_fast": {"Me": "candle_data", "Ac": "volume_profile"},
            "medium": {"AIS[3]": "signal_generation", "An-n": "local_trend"},
            "medium_slow": {"PNN": "support_resistance", "Br": "pattern_branch"},
            "slow": {"Fi-lo": "risk_feedback", "Ax-d": "correlation"},
            "very_slow": {"Soma": "position_state", "Rh": "volatility_cycle"},
            "ultra_slow": {"Nt": "market_signal", "El": "arbitrage_link"},
            "slowest": {"Me-Rh": "trend_cycle", "Bi": "long_short"}
        },
        "audio": {
            "ultra_fast": {"Ax": "sample_data", "Pr-Ch(3)": "waveform"},
            "fast": {"Io-Ch": "frequency_bin", "Li": "spectral_layer"},
            "medium_fast": {"Me": "frame_data", "Ac": "mel_feature"},
            "medium": {"AIS[3]": "onset_detection", "An-n": "local_pitch"},
            "medium_slow": {"PNN": "note_structure", "Br": "harmonic_branch"},
            "slow": {"Fi-lo": "tempo_feedback", "Ax-d": "chord_progression"},
            "very_slow": {"Soma": "phrase_repr", "Rh": "beat_rhythm"},
            "ultra_slow": {"Nt": "section_signal", "El": "transition"},
            "slowest": {"Me-Rh": "song_structure", "Bi": "verse_chorus"}
        }
    }
    
    # Find matching context
    context_lower = context.lower()
    for key in mappings:
        if key in context_lower:
            scale_map = mappings[key].get(scale, {})
            return scale_map.get(abbrev, f"{context}_{abbrev}")
    
    return f"{context}_{abbrev}"


def build_model(context: str, structure: List[int]) -> TimeCrystalNeuron:
    """Build a time crystal neuron model for the given context."""
    a, b, c, d = structure  # domains, layers, scales, components
    
    model = TimeCrystalNeuron(
        context=context,
        structure=structure
    )
    
    # Get scale names based on c (number of scales per layer)
    scale_names = list(TEMPORAL_SCALES.keys())
    
    # Create domains
    domain_names = ["dendrite", "soma", "axon"][:a] if a <= 3 else [f"domain_{i+1}" for i in range(a)]
    
    all_periods = []
    
    for domain_idx, domain_name in enumerate(domain_names):
        domain = Domain(name=domain_name)
        
        # Create layers for this domain
        for layer_idx in range(b):
            layer = Layer(name=f"layer_{layer_idx+1}")
            
            # Determine which scales this layer uses
            scale_offset = (domain_idx * b + layer_idx) % len(scale_names)
            layer_scales = [scale_names[(scale_offset + i) % len(scale_names)] for i in range(c)]
            
            # Add components for each scale
            for scale_idx, scale in enumerate(layer_scales):
                period = TEMPORAL_SCALES[scale]
                all_periods.append(period)
                
                # Get components for this scale
                available = SCALE_COMPONENTS.get(scale, [])
                selected = available[:d] if len(available) >= d else available
                
                for abbrev in selected:
                    component = Component(
                        name=abbrev,
                        abbreviation=abbrev,
                        temporal_scale=scale,
                        period=period,
                        category=categorize_component(abbrev),
                        context_mapping=generate_context_mapping(context, scale, abbrev)
                    )
                    layer.components.append(component)
            
            domain.layers.append(layer)
        
        model.domains.append(domain)
    
    # Compute cycle length
    if all_periods:
        model.cycle_length = compute_cycle_length(all_periods)
    
    # Classify into Universal and Particular sets (sys-n style)
    # Slow oscillators (>= 0.5s) are Universal, faster are Particular
    for domain in model.domains:
        for layer in domain.layers:
            for comp in layer.components:
                if comp.period >= 0.5:
                    if comp.abbreviation not in model.universal_sets:
                        model.universal_sets.append(comp.abbreviation)
                else:
                    if comp.abbreviation not in model.particular_sets:
                        model.particular_sets.append(comp.abbreviation)
    
    return model


def generate_nn_architecture(model: TimeCrystalNeuron) -> str:
    """Generate a Lua/Torch nn architecture from the model."""
    lines = [
        "-- Time Crystal Neuron Architecture",
        f"-- Context: {model.context}",
        f"-- Structure: [{','.join(map(str, model.structure))}]",
        f"-- Cycle Length: {model.cycle_length:.3f}s",
        "",
        "require 'nn'",
        "",
        "-- Build hierarchical model",
        "tcn = nn.Sequential()",
        ""
    ]
    
    for domain in model.domains:
        lines.append(f"-- Domain: {domain.name}")
        lines.append(f"{domain.name} = nn.Sequential()")
        
        for layer in domain.layers:
            lines.append(f"  -- {layer.name}")
            lines.append(f"  {layer.name} = nn.Concat(1)")
            
            for comp in layer.components:
                lines.append(f"    -- {comp.abbreviation} ({comp.temporal_scale}, {comp.period}s)")
                lines.append(f"    -- Context: {comp.context_mapping}")
            
            lines.append(f"  {domain.name}:add({layer.name})")
        
        lines.append(f"tcn:add({domain.name})")
        lines.append("")
    
    return "\n".join(lines)


def generate_sys_n_spec(model: TimeCrystalNeuron) -> str:
    """Generate a sys-n style state transition specification."""
    lines = [
        f"# Time Crystal Neuron State Specification",
        f"## Context: {model.context}",
        f"## Structure: Neuron [{','.join(map(str, model.structure))}]",
        "",
        "## Universal Sets (Slow Oscillators >= 0.5s)",
        ""
    ]
    
    for u in model.universal_sets[:5]:  # Limit to 5 for readability
        lines.append(f"- **{u}**")
    
    lines.extend([
        "",
        "## Particular Sets (Fast Oscillators < 0.5s)",
        ""
    ])
    
    for p in model.particular_sets[:10]:  # Limit to 10
        lines.append(f"- **{p}**")
    
    lines.extend([
        "",
        f"## Cycle Length: {model.cycle_length:.3f}s",
        "",
        "## Temporal Hierarchy",
        ""
    ])
    
    # Group by scale
    scale_groups = {}
    for domain in model.domains:
        for layer in domain.layers:
            for comp in layer.components:
                if comp.temporal_scale not in scale_groups:
                    scale_groups[comp.temporal_scale] = []
                if comp.abbreviation not in scale_groups[comp.temporal_scale]:
                    scale_groups[comp.temporal_scale].append(comp.abbreviation)
    
    for scale in TEMPORAL_SCALES:
        if scale in scale_groups:
            period = TEMPORAL_SCALES[scale]
            comps = ", ".join(scale_groups[scale][:5])
            lines.append(f"| {scale} | {period}s | {comps} |")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Time Crystal Neuron Model",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--context', type=str, required=True,
                        help='Domain context (e.g., "language processing")')
    parser.add_argument('--structure', type=str, default="3,4,3,3",
                        help='Structure as a,b,c,d (default: 3,4,3,3)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output JSON file path')
    parser.add_argument('--nn', action='store_true',
                        help='Generate nn architecture code')
    parser.add_argument('--sysn', action='store_true',
                        help='Generate sys-n specification')
    
    args = parser.parse_args()
    
    # Parse structure
    structure = [int(x) for x in args.structure.split(',')]
    if len(structure) != 4:
        print("Error: Structure must be 4 integers (a,b,c,d)")
        return
    
    print(f"Generating Time Crystal Neuron Model")
    print(f"  Context: {args.context}")
    print(f"  Structure: Neuron [{','.join(map(str, structure))}]")
    print()
    
    # Build model
    model = build_model(args.context, structure)
    
    print(f"Model Statistics:")
    print(f"  Domains: {len(model.domains)}")
    print(f"  Cycle Length: {model.cycle_length:.3f}s")
    print(f"  Universal Sets: {len(model.universal_sets)}")
    print(f"  Particular Sets: {len(model.particular_sets)}")
    print()
    
    # Output JSON
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(model.to_dict(), f, indent=2)
        print(f"Model saved to: {args.output}")
    
    # Generate nn architecture
    if args.nn:
        nn_code = generate_nn_architecture(model)
        nn_file = args.output.replace('.json', '.lua') if args.output else 'tcn_model.lua'
        with open(nn_file, 'w') as f:
            f.write(nn_code)
        print(f"nn architecture saved to: {nn_file}")
    
    # Generate sys-n spec
    if args.sysn:
        sysn_spec = generate_sys_n_spec(model)
        sysn_file = args.output.replace('.json', '_sysn.md') if args.output else 'tcn_sysn.md'
        with open(sysn_file, 'w') as f:
            f.write(sysn_spec)
        print(f"sys-n specification saved to: {sysn_file}")
    
    # Print summary if no file output
    if not args.output:
        print("Sample Context Mappings:")
        for domain in model.domains[:1]:
            for layer in domain.layers[:1]:
                for comp in layer.components[:5]:
                    print(f"  {comp.abbreviation} -> {comp.context_mapping}")


if __name__ == '__main__':
    main()
