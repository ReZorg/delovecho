#!/usr/bin/env python3
"""
Time Crystal Brain Model Visualization

Generates visual representations of the time crystal brain model,
including hierarchy diagrams, region maps, and subsystem networks.

Usage:
    python visualize_brain.py brain_model.json --output brain_diagram.png
    python visualize_brain.py brain_model.json --hierarchy --output hierarchy.png
    python visualize_brain.py --levels --output levels.png
"""

import argparse
import json
import math
import os

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Wedge
    import numpy as np
except ImportError:
    print("Error: matplotlib and numpy required. Run: pip install matplotlib numpy")
    exit(1)


# Color scheme for brain regions by level
LEVEL_COLORS = {
    1: "#E8D5E8",   # Microtubule - light purple
    2: "#6B9BD1",   # Neuron - blue
    3: "#7BC47F",   # Cortical branches - green
    4: "#F4C542",   # Cortex domain - yellow
    5: "#E8A5A5",   # Cerebellum - pink
    6: "#A5C8E8",   # Hypothalamus - light blue
    7: "#C8E8A5",   # Hippocampus - light green
    8: "#E8C8A5",   # Thalamic body - tan
    9: "#C8A5E8",   # Skin nerve net - lavender
    10: "#A5E8C8",  # Cranial nerve - mint
    11: "#E8E8A5",  # Thoracic nerve - light yellow
    12: "#FF9999"   # Blood vessel - coral
}

SUBSYSTEM_COLORS = {
    "proprioception": "#6B9BD1",
    "homeostatic": "#F4C542",
    "emotion": "#E8A5A5",
    "olfactory": "#7BC47F",
    "entorhinal": "#C8A5E8",
    "spinal": "#A5E8C8"
}


def load_model(filepath: str) -> dict:
    """Load a brain model from JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)


def draw_hierarchy_levels(output_path: str):
    """Draw a reference diagram of the 12 hierarchy levels."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    levels = [
        (1, "Microtubule", "Molecular", "0.001s"),
        (2, "Neuron", "Cellular", "0.008s"),
        (3, "Cortical Branches", "Columnar", "0.05s"),
        (4, "Cortex Domain", "Regional", "0.1s"),
        (5, "Cerebellum", "Organ", "0.2s"),
        (6, "Hypothalamus", "Nuclear", "0.3s"),
        (7, "Hippocampus", "Nuclear", "0.4s"),
        (8, "Thalamic Body", "Relay", "0.5s"),
        (9, "Skin Nerve Net", "Peripheral", "0.7s"),
        (10, "Cranial Nerve", "Peripheral", "0.8s"),
        (11, "Thoracic Nerve", "Spinal", "0.9s"),
        (12, "Blood Vessel", "Vascular", "1.0s")
    ]
    
    n_levels = len(levels)
    bar_height = 0.6
    
    for i, (level, name, scale, period) in enumerate(levels):
        y = n_levels - i
        color = LEVEL_COLORS.get(level, "#CCCCCC")
        
        # Draw bar with width proportional to scale
        width = 50 + (level * 3)
        bar = FancyBboxPatch((10, y - bar_height/2), width, bar_height,
                            boxstyle="round,pad=0.02",
                            facecolor=color, edgecolor='#333333',
                            linewidth=1)
        ax.add_patch(bar)
        
        # Level number
        ax.text(5, y, str(level), ha='center', va='center',
               fontsize=12, fontweight='bold')
        
        # Name
        ax.text(15, y, name, ha='left', va='center',
               fontsize=10, fontweight='bold')
        
        # Scale
        ax.text(45, y, scale, ha='left', va='center',
               fontsize=9, style='italic', color='#666666')
        
        # Period
        ax.text(65, y, period, ha='left', va='center',
               fontsize=9, color='#888888')
    
    ax.set_xlim(0, 80)
    ax.set_ylim(0, n_levels + 1)
    ax.axis('off')
    ax.set_title("Time Crystal Brain Model - Hierarchy Levels", 
                fontsize=14, fontweight='bold', pad=20)
    
    # Column headers
    ax.text(5, n_levels + 0.5, "Level", ha='center', fontsize=10, fontweight='bold')
    ax.text(25, n_levels + 0.5, "Region", ha='center', fontsize=10, fontweight='bold')
    ax.text(45, n_levels + 0.5, "Scale", ha='left', fontsize=10, fontweight='bold')
    ax.text(65, n_levels + 0.5, "Period", ha='left', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Hierarchy levels diagram saved to: {output_path}")


def draw_brain_regions(model: dict, output_path: str):
    """Draw a diagram showing all brain regions."""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    regions = model.get('regions', [])
    if not regions:
        ax.text(0.5, 0.5, "No regions in model", 
               transform=ax.transAxes, ha='center', va='center')
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return
    
    # Arrange regions in a circular layout
    n_regions = len(regions)
    center_x, center_y = 50, 50
    radius = 35
    
    for i, region in enumerate(regions):
        angle = 2 * math.pi * i / n_regions - math.pi / 2
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        
        level = region.get('level', 1)
        color = LEVEL_COLORS.get(level, "#CCCCCC")
        n_components = len(region.get('components', []))
        
        # Size based on number of components
        size = 3 + n_components * 0.3
        
        circle = Circle((x, y), size, facecolor=color, 
                        edgecolor='#333333', linewidth=1.5, alpha=0.8)
        ax.add_patch(circle)
        
        # Region name
        name = region.get('name', 'Unknown').replace('_', '\n')
        ax.text(x, y, name, ha='center', va='center',
               fontsize=8, fontweight='bold')
        
        # Component count
        ax.text(x, y - size - 1, f"({n_components})", ha='center', va='top',
               fontsize=7, color='#666666')
    
    # Center label
    ax.text(center_x, center_y, "Time Crystal\nBrain Model",
           ha='center', va='center', fontsize=12, fontweight='bold')
    
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Brain Regions Overview", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Brain regions diagram saved to: {output_path}")


def draw_subsystems(model: dict, output_path: str):
    """Draw a diagram showing functional subsystems."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    subsystems = model.get('subsystems', [])
    if not subsystems:
        ax.text(0.5, 0.5, "No subsystems in model", 
               transform=ax.transAxes, ha='center', va='center')
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return
    
    n_subsystems = len(subsystems)
    cols = 3
    rows = math.ceil(n_subsystems / cols)
    
    cell_width = 30
    cell_height = 20
    
    for i, subsys in enumerate(subsystems):
        row = i // cols
        col = i % cols
        
        x = 5 + col * cell_width
        y = 95 - (row + 1) * cell_height
        
        name = subsys.get('name', 'Unknown')
        abbrev = subsys.get('abbrev', '?')
        components = subsys.get('components', [])
        
        # Get color
        subsys_key = name.lower().split()[0]
        color = SUBSYSTEM_COLORS.get(subsys_key, "#CCCCCC")
        
        # Draw box
        box = FancyBboxPatch((x, y), cell_width - 2, cell_height - 2,
                            boxstyle="round,pad=0.3",
                            facecolor=color, edgecolor='#333333',
                            linewidth=1.5, alpha=0.7)
        ax.add_patch(box)
        
        # Subsystem name
        ax.text(x + (cell_width - 2) / 2, y + cell_height - 5,
               f"{name}\n({abbrev})", ha='center', va='top',
               fontsize=9, fontweight='bold')
        
        # Component list (abbreviated)
        comp_abbrevs = [c.get('abbrev', '?') for c in components[:4]]
        if len(components) > 4:
            comp_abbrevs.append(f"+{len(components) - 4}")
        comp_text = ", ".join(comp_abbrevs)
        ax.text(x + (cell_width - 2) / 2, y + 3,
               comp_text, ha='center', va='bottom',
               fontsize=7, color='#444444', wrap=True)
    
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    ax.set_title("Functional Subsystems", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Subsystems diagram saved to: {output_path}")


def draw_region_detail(region: dict, output_path: str):
    """Draw a detailed diagram of a single region."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    name = region.get('name', 'Unknown')
    level = region.get('level', 1)
    scale = region.get('scale', 'unknown')
    components = region.get('components', [])
    
    color = LEVEL_COLORS.get(level, "#CCCCCC")
    
    # Title
    ax.text(50, 95, f"{name.replace('_', ' ').title()}", 
           ha='center', va='top', fontsize=16, fontweight='bold')
    ax.text(50, 90, f"Level {level} | {scale.title()} Scale",
           ha='center', va='top', fontsize=11, color='#666666')
    
    # Draw components
    n_components = len(components)
    if n_components == 0:
        ax.text(50, 50, "No components", ha='center', va='center')
    else:
        cols = min(4, n_components)
        rows = math.ceil(n_components / cols)
        
        cell_width = 80 / cols
        cell_height = 60 / rows
        
        for i, comp in enumerate(components):
            row = i // cols
            col = i % cols
            
            x = 10 + col * cell_width + cell_width / 2
            y = 80 - row * cell_height - cell_height / 2
            
            # Circle for component
            radius = min(cell_width, cell_height) * 0.35
            circle = Circle((x, y), radius, facecolor=color,
                           edgecolor='#333333', linewidth=1, alpha=0.8)
            ax.add_patch(circle)
            
            # Component abbreviation
            abbrev = comp.get('abbrev', '?')
            ax.text(x, y, abbrev, ha='center', va='center',
                   fontsize=8 if len(abbrev) <= 4 else 6, fontweight='bold')
            
            # Component name below
            comp_name = comp.get('name', '')
            ax.text(x, y - radius - 2, comp_name, ha='center', va='top',
                   fontsize=6, color='#666666')
            
            # Period
            period = comp.get('period', 0)
            period_str = f"{period*1000:.0f}ms" if period < 1 else f"{period:.2f}s"
            ax.text(x, y - radius - 6, period_str, ha='center', va='top',
                   fontsize=5, color='#888888')
    
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Region detail diagram saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Visualize Time Crystal Brain Model"
    )
    parser.add_argument('model', nargs='?', default=None,
                        help='Path to brain model JSON file')
    parser.add_argument('--output', '-o', type=str, default='brain_diagram.png',
                        help='Output image path')
    parser.add_argument('--levels', action='store_true',
                        help='Generate hierarchy levels reference diagram')
    parser.add_argument('--regions', action='store_true',
                        help='Generate regions overview diagram')
    parser.add_argument('--subsystems', action='store_true',
                        help='Generate subsystems diagram')
    parser.add_argument('--region-detail', type=str, default=None,
                        help='Generate detail diagram for specific region')
    
    args = parser.parse_args()
    
    if args.levels:
        draw_hierarchy_levels(args.output)
        return
    
    if args.model is None:
        print("Error: Model file required (unless using --levels)")
        return
    
    if not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        return
    
    model = load_model(args.model)
    
    if args.subsystems:
        draw_subsystems(model, args.output)
    elif args.region_detail:
        # Find the specific region
        regions = model.get('regions', [])
        target_region = None
        for region in regions:
            if region.get('name', '').lower() == args.region_detail.lower():
                target_region = region
                break
        
        if target_region:
            draw_region_detail(target_region, args.output)
        else:
            print(f"Error: Region '{args.region_detail}' not found")
    else:
        draw_brain_regions(model, args.output)


if __name__ == '__main__':
    main()
