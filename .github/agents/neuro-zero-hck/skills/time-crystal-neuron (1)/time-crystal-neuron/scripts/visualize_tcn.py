#!/usr/bin/env python3
"""
Time Crystal Neuron Visualization

Generates visual representations of time crystal neuron models,
including temporal hierarchy diagrams and state transition timelines.

Usage:
    python visualize_tcn.py model.json --output diagram.png
    python visualize_tcn.py model.json --timeline --steps 24
"""

import argparse
import json
import math
import os

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import Circle, FancyBboxPatch
    import numpy as np
except ImportError:
    print("Error: matplotlib and numpy required. Run: pip install matplotlib numpy")
    exit(1)


# Color scheme matching the original diagram
COLORS = {
    "feedback": "#6B9BD1",      # Blue
    "rhythm": "#6B9BD1",        # Blue
    "morphological": "#6B9BD1", # Blue
    "mechanical": "#F4C542",    # Yellow
    "anatomic": "#7BC47F",      # Green
    "junction": "#A0A0A0",      # Gray
    "other": "#4DB8B8",         # Teal
    "universal": "#F4C542",     # Yellow (slow)
    "particular": "#6B9BD1"     # Blue (fast)
}

TEMPORAL_SCALES = {
    "ultra_fast": 0.008,
    "fast": 0.026,
    "medium_fast": 0.052,
    "medium": 0.11,
    "medium_slow": 0.16,
    "slow": 0.25,
    "very_slow": 0.33,
    "ultra_slow": 0.5,
    "slowest": 1.0
}


def load_model(filepath: str) -> dict:
    """Load a TCN model from JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)


def draw_hierarchy_diagram(model: dict, output_path: str):
    """Draw a hierarchical diagram of the model structure."""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title
    structure = model.get('structure', [3, 4, 3, 3])
    ax.text(50, 97, f"Time Crystal Neuron [{','.join(map(str, structure))}]",
            ha='center', va='top', fontsize=16, fontweight='bold')
    ax.text(50, 93, f"Context: {model.get('context', 'Unknown')}",
            ha='center', va='top', fontsize=12, style='italic')
    
    # Draw domains
    domains = model.get('domains', [])
    n_domains = len(domains)
    
    if n_domains == 0:
        ax.text(50, 50, "No domains in model", ha='center', va='center', fontsize=14)
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return
    
    domain_width = 80 / n_domains
    domain_start_x = 10
    
    for d_idx, domain in enumerate(domains):
        domain_x = domain_start_x + d_idx * domain_width + domain_width / 2
        
        # Domain label
        ax.text(domain_x, 88, domain.get('name', f'Domain {d_idx+1}').upper(),
                ha='center', va='center', fontsize=11, fontweight='bold')
        
        # Draw layers
        layers = domain.get('layers', [])
        n_layers = len(layers)
        layer_height = 70 / max(n_layers, 1)
        
        for l_idx, layer in enumerate(layers):
            layer_y = 80 - (l_idx + 0.5) * layer_height
            
            # Draw components as circles
            components = layer.get('components', [])
            n_comps = len(components)
            
            if n_comps == 0:
                continue
            
            # Arrange components in a cluster
            comp_radius = min(3, domain_width / (n_comps + 2))
            
            for c_idx, comp in enumerate(components):
                # Position in a grid-like pattern
                row = c_idx // 4
                col = c_idx % 4
                
                cx = domain_x - 1.5 * comp_radius + col * comp_radius * 1.2
                cy = layer_y - row * comp_radius * 1.2
                
                # Color based on category
                category = comp.get('category', 'other')
                color = COLORS.get(category, COLORS['other'])
                
                # Draw circle
                circle = Circle((cx, cy), comp_radius * 0.8, 
                               facecolor=color, edgecolor='#333333', 
                               linewidth=0.5, alpha=0.8)
                ax.add_patch(circle)
                
                # Label (abbreviation)
                abbrev = comp.get('abbreviation', '?')
                if len(abbrev) <= 4:
                    ax.text(cx, cy, abbrev, ha='center', va='center',
                           fontsize=6, fontweight='bold')
    
    # Legend
    legend_y = 10
    legend_x = 75
    ax.text(legend_x, legend_y + 8, "Categories:", fontsize=10, fontweight='bold')
    
    for i, (cat, color) in enumerate(list(COLORS.items())[:6]):
        circle = Circle((legend_x + 2, legend_y + 5 - i * 2), 1,
                        facecolor=color, edgecolor='#333333', linewidth=0.5)
        ax.add_patch(circle)
        ax.text(legend_x + 5, legend_y + 5 - i * 2, cat.replace('_', ' ').title(),
               fontsize=8, va='center')
    
    # Cycle info
    ax.text(10, 5, f"Cycle Length: {model.get('cycle_length', 0):.3f}s",
           fontsize=10)
    ax.text(10, 2, f"Universal Sets: {len(model.get('universal_sets', []))} | "
                   f"Particular Sets: {len(model.get('particular_sets', []))}",
           fontsize=9)
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Hierarchy diagram saved to: {output_path}")


def draw_timeline(model: dict, output_path: str, n_steps: int = 24):
    """Draw a timeline showing state transitions."""
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    
    # Collect all unique components with their periods
    components = []
    seen = set()
    
    for domain in model.get('domains', []):
        for layer in domain.get('layers', []):
            for comp in layer.get('components', []):
                abbrev = comp.get('abbreviation', '')
                if abbrev not in seen:
                    seen.add(abbrev)
                    components.append({
                        'name': abbrev,
                        'period': comp.get('period', 1.0),
                        'category': comp.get('category', 'other'),
                        'scale': comp.get('temporal_scale', 'medium')
                    })
    
    # Sort by period (fastest first)
    components.sort(key=lambda x: x['period'])
    components = components[:15]  # Limit for readability
    
    n_components = len(components)
    if n_components == 0:
        ax.text(0.5, 0.5, "No components to visualize", 
               transform=ax.transAxes, ha='center', va='center')
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return
    
    # Time axis
    base_period = components[0]['period']
    total_time = base_period * n_steps
    time_points = np.linspace(0, total_time, n_steps + 1)
    
    # Draw timeline for each component
    for i, comp in enumerate(components):
        y = n_components - i
        period = comp['period']
        color = COLORS.get(comp['category'], COLORS['other'])
        
        # Component label
        ax.text(-0.02 * total_time, y, comp['name'], 
               ha='right', va='center', fontsize=9, fontweight='bold')
        ax.text(-0.15 * total_time, y, f"{period*1000:.0f}ms" if period < 1 else f"{period:.2f}s",
               ha='right', va='center', fontsize=8, color='gray')
        
        # Draw oscillation
        for t in time_points[:-1]:
            # Phase within period
            phase = (t % period) / period
            
            # Draw circle at active phases
            if phase < 0.5:
                alpha = 1.0 - phase * 2
            else:
                alpha = (phase - 0.5) * 2
            
            circle = Circle((t, y), 0.3, facecolor=color, 
                           edgecolor='none', alpha=0.3 + 0.7 * alpha)
            ax.add_patch(circle)
        
        # Draw baseline
        ax.plot([0, total_time], [y, y], 'k-', linewidth=0.5, alpha=0.3)
    
    # Formatting
    ax.set_xlim(-0.2 * total_time, total_time * 1.05)
    ax.set_ylim(0, n_components + 1)
    ax.set_xlabel('Time (seconds)', fontsize=11)
    ax.set_ylabel('Components', fontsize=11)
    ax.set_title(f"Time Crystal Neuron Timeline - {model.get('context', 'Unknown')}", 
                fontsize=14, fontweight='bold')
    
    # Grid
    ax.set_yticks([])
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Timeline saved to: {output_path}")


def draw_temporal_scales(output_path: str):
    """Draw a reference diagram of temporal scales."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    scales = list(TEMPORAL_SCALES.items())
    n_scales = len(scales)
    
    # Draw scale bars
    max_period = max(TEMPORAL_SCALES.values())
    
    for i, (scale_name, period) in enumerate(scales):
        y = n_scales - i
        width = (period / max_period) * 80
        
        # Color gradient from fast (blue) to slow (yellow)
        t = i / (n_scales - 1)
        color = plt.cm.coolwarm(t)
        
        # Draw bar
        bar = FancyBboxPatch((10, y - 0.3), width, 0.6,
                            boxstyle="round,pad=0.02",
                            facecolor=color, edgecolor='#333333',
                            linewidth=1)
        ax.add_patch(bar)
        
        # Labels
        ax.text(5, y, scale_name.replace('_', ' ').title(),
               ha='right', va='center', fontsize=10, fontweight='bold')
        
        period_str = f"{period*1000:.0f}ms" if period < 1 else f"{period:.2f}s"
        ax.text(12 + width, y, period_str,
               ha='left', va='center', fontsize=9)
    
    ax.set_xlim(0, 100)
    ax.set_ylim(0, n_scales + 1)
    ax.axis('off')
    ax.set_title("Time Crystal Neuron - Temporal Scales", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Temporal scales diagram saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Visualize Time Crystal Neuron Model"
    )
    parser.add_argument('model', nargs='?', default=None,
                        help='Path to model JSON file')
    parser.add_argument('--output', '-o', type=str, default='tcn_diagram.png',
                        help='Output image path')
    parser.add_argument('--timeline', action='store_true',
                        help='Generate timeline visualization')
    parser.add_argument('--steps', type=int, default=24,
                        help='Number of time steps for timeline')
    parser.add_argument('--scales', action='store_true',
                        help='Generate temporal scales reference diagram')
    
    args = parser.parse_args()
    
    if args.scales:
        draw_temporal_scales(args.output)
        return
    
    if args.model is None:
        print("Error: Model file required (unless using --scales)")
        return
    
    if not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        return
    
    model = load_model(args.model)
    
    if args.timeline:
        draw_timeline(model, args.output, args.steps)
    else:
        draw_hierarchy_diagram(model, args.output)


if __name__ == '__main__':
    main()
