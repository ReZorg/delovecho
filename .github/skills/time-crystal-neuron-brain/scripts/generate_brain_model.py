#!/usr/bin/env python3
"""
Time Crystal Brain Model Generator

Generates a complete time crystal brain model specification,
extending the single neuron model to the whole brain architecture
from Nanobrain Figure 7.15.

Usage:
    python generate_brain_model.py --output brain_model.json
    python generate_brain_model.py --region cerebellum --output cerebellum.json
    python generate_brain_model.py --subsystem proprioception --output proprio.json
"""

import argparse
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from math import gcd
from functools import reduce


# Hierarchical levels of the brain model
HIERARCHY_LEVELS = {
    1: {"name": "microtubule", "scale": "molecular", "period_base": 0.001},
    2: {"name": "neuron", "scale": "cellular", "period_base": 0.008},
    3: {"name": "cortical_branches", "scale": "columnar", "period_base": 0.05},
    4: {"name": "cortex_domain", "scale": "regional", "period_base": 0.1},
    5: {"name": "cerebellum", "scale": "organ", "period_base": 0.2},
    6: {"name": "hypothalamus", "scale": "nuclear", "period_base": 0.3},
    7: {"name": "hippocampus", "scale": "nuclear", "period_base": 0.4},
    8: {"name": "thalamic_body", "scale": "relay", "period_base": 0.5},
    9: {"name": "skin_nerve_net", "scale": "peripheral", "period_base": 0.7},
    10: {"name": "cranial_nerve", "scale": "peripheral", "period_base": 0.8},
    11: {"name": "thoracic_nerve", "scale": "spinal", "period_base": 0.9},
    12: {"name": "blood_vessel", "scale": "vascular", "period_base": 1.0}
}

# Brain regions with their components
BRAIN_REGIONS = {
    "microtubule": {
        "level": 1,
        "components": [
            {"abbrev": "Dub-bell", "name": "Dumbbell shape", "period": 0.001},
            {"abbrev": "Spiral", "name": "Spiral structure", "period": 0.001},
            {"abbrev": "Helix", "name": "Alpha helix", "period": 0.002},
            {"abbrev": "Pitch", "name": "Helix pitch", "period": 0.002},
            {"abbrev": "H2O-ext", "name": "External water", "period": 0.003},
            {"abbrev": "H2O-int", "name": "Internal water", "period": 0.003},
            {"abbrev": "Topo", "name": "Topology", "period": 0.004},
            {"abbrev": "Lattice", "name": "Surface lattice", "period": 0.005}
        ]
    },
    "cortex_domain": {
        "level": 4,
        "components": [
            {"abbrev": "A", "name": "Occipital lobe", "period": 0.1},
            {"abbrev": "B", "name": "Frontal lobe", "period": 0.1},
            {"abbrev": "C", "name": "Temporal lobe", "period": 0.1},
            {"abbrev": "D", "name": "Parietal lobe", "period": 0.1},
            {"abbrev": "E(6)", "name": "Neurological function", "period": 0.12},
            {"abbrev": "F(6)", "name": "Lateral Brodmann", "period": 0.12},
            {"abbrev": "G(6)", "name": "Medial Brodmann", "period": 0.12},
            {"abbrev": "H(6)", "name": "Gyrus nuclei", "period": 0.12},
            {"abbrev": "Vc", "name": "Visual cortex", "period": 0.08},
            {"abbrev": "Mc", "name": "Motor cortex", "period": 0.08},
            {"abbrev": "Sc", "name": "Somatosensory cortex", "period": 0.08},
            {"abbrev": "Hp(6)", "name": "Hippocampus", "period": 0.15},
            {"abbrev": "Ic", "name": "Insula cortex", "period": 0.1}
        ]
    },
    "cerebellum": {
        "level": 5,
        "components": [
            {"abbrev": "M", "name": "Mid lobe", "period": 0.2},
            {"abbrev": "L", "name": "Left lobe", "period": 0.2},
            {"abbrev": "R", "name": "Right lobe", "period": 0.2},
            {"abbrev": "A", "name": "Posterior quadrate lobule", "period": 0.22},
            {"abbrev": "B", "name": "Anterior lobule", "period": 0.22},
            {"abbrev": "C", "name": "Folia", "period": 0.18},
            {"abbrev": "D", "name": "Horizontal fissure", "period": 0.25},
            {"abbrev": "E", "name": "Middle lobule", "period": 0.22},
            {"abbrev": "F", "name": "Dorsolateral fissure", "period": 0.25},
            {"abbrev": "G", "name": "Postlunate fissure", "period": 0.25},
            {"abbrev": "H", "name": "Inferior semilunar lobule", "period": 0.22},
            {"abbrev": "I", "name": "Tonsil", "period": 0.2}
        ]
    },
    "hypothalamus": {
        "level": 6,
        "components": [
            {"abbrev": "Lim", "name": "Limbic system", "period": 0.3},
            {"abbrev": "Mam", "name": "Mammillothalamic tract", "period": 0.35},
            {"abbrev": "HR", "name": "Heart rate", "period": 0.8},
            {"abbrev": "BP", "name": "Blood pressure", "period": 1.0},
            {"abbrev": "Oxy", "name": "Oxytocin", "period": 0.5},
            {"abbrev": "Ant-pr", "name": "Anterior preoptic", "period": 0.3},
            {"abbrev": "Post-pr", "name": "Posterior preoptic", "period": 0.3},
            {"abbrev": "Arc", "name": "Arcuate nucleus", "period": 0.4},
            {"abbrev": "Sup", "name": "Supraoptic", "period": 0.35},
            {"abbrev": "Para", "name": "Paraventricular", "period": 0.35}
        ]
    },
    "hippocampus": {
        "level": 7,
        "components": [
            {"abbrev": "CAIV", "name": "CA4 region", "period": 0.4},
            {"abbrev": "CAII", "name": "CA2 region", "period": 0.4},
            {"abbrev": "CAI", "name": "CA1 region", "period": 0.4},
            {"abbrev": "U-trap", "name": "U-shaped trap", "period": 0.45},
            {"abbrev": "V-trap", "name": "V-shaped trap", "period": 0.45},
            {"abbrev": "Lat-ant", "name": "Lateral anterior nucleus", "period": 0.42},
            {"abbrev": "Lat-post", "name": "Lateral posterior nucleus", "period": 0.42},
            {"abbrev": "Intra", "name": "Intralaminar nucleus", "period": 0.38},
            {"abbrev": "Ret", "name": "Reticular nucleus", "period": 0.38}
        ]
    },
    "thalamic_body": {
        "level": 8,
        "components": [
            {"abbrev": "VM", "name": "Ventromedial nucleus", "period": 0.5},
            {"abbrev": "SC", "name": "Supra chiasmatic", "period": 24.0},
            {"abbrev": "Ant", "name": "Anterior nucleus", "period": 0.5},
            {"abbrev": "Post", "name": "Posterior nucleus", "period": 0.5},
            {"abbrev": "Med", "name": "Medial nuclei", "period": 0.55},
            {"abbrev": "Lat", "name": "Lateral nuclei", "period": 0.55},
            {"abbrev": "Med-dor", "name": "Medial dorsal", "period": 0.52},
            {"abbrev": "Lat-post", "name": "Lateral posterior", "period": 0.52}
        ]
    },
    "cranial_nerve": {
        "level": 10,
        "components": [
            {"abbrev": "Olf", "name": "Olfactory", "period": 0.8},
            {"abbrev": "Opt", "name": "Optic", "period": 0.016},
            {"abbrev": "Ocm", "name": "Oculomotor", "period": 0.1},
            {"abbrev": "Tro", "name": "Trochlear", "period": 0.1},
            {"abbrev": "Tri", "name": "Trigeminal", "period": 0.05},
            {"abbrev": "Abd", "name": "Abducens", "period": 0.1},
            {"abbrev": "Fac", "name": "Facial", "period": 0.2},
            {"abbrev": "Ves", "name": "Vestibulocochlear", "period": 0.001},
            {"abbrev": "Glo", "name": "Glossopharyngeal", "period": 0.3},
            {"abbrev": "Vag", "name": "Vagus", "period": 0.8},
            {"abbrev": "Acc", "name": "Accessory", "period": 0.5},
            {"abbrev": "Hyp", "name": "Hypoglossal", "period": 0.2}
        ]
    },
    "blood_vessel": {
        "level": 12,
        "components": [
            {"abbrev": "Sup-cer", "name": "Superior cerebral artery", "period": 1.0},
            {"abbrev": "Mid-cer", "name": "Middle cerebral artery", "period": 1.0},
            {"abbrev": "Ant-spi", "name": "Anterior spinal artery", "period": 1.0},
            {"abbrev": "Post-cer", "name": "Posterior cerebral artery", "period": 1.0},
            {"abbrev": "Bas", "name": "Basilar artery", "period": 1.0},
            {"abbrev": "Pon", "name": "Pontine arteries", "period": 1.0}
        ]
    }
}

# Functional subsystems
SUBSYSTEMS = {
    "proprioception": {
        "name": "Proprioception System",
        "abbrev": "Pr",
        "components": [
            {"abbrev": "Sc", "name": "Spinal cord", "period": 0.05, "role": "pathway"},
            {"abbrev": "Th", "name": "Thalamus", "period": 0.5, "role": "relay"},
            {"abbrev": "Cb", "name": "Cerebellum", "period": 0.2, "role": "coordination"},
            {"abbrev": "Pc", "name": "Proprioception cell", "period": 0.02, "role": "sensor"},
            {"abbrev": "Se(4)", "name": "Sensor quartet", "period": 0.01, "role": "input"},
            {"abbrev": "Vpn", "name": "Ventral posterior nuclei", "period": 0.5, "role": "relay"},
            {"abbrev": "D[3]", "name": "Dorsal triad", "period": 0.3, "role": "pathway"},
            {"abbrev": "K[3]", "name": "Kinesthesia triad", "period": 0.1, "role": "sense"},
            {"abbrev": "Ex[4]", "name": "External haptic", "period": 0.05, "role": "input"}
        ]
    },
    "homeostatic": {
        "name": "Homeostatic System",
        "abbrev": "HoS",
        "components": [
            {"abbrev": "HoS", "name": "Homeostatic", "period": 1.0, "role": "system"},
            {"abbrev": "Fb", "name": "Feedback", "period": 0.5, "role": "control"},
            {"abbrev": "C*[4]", "name": "Brain stem quartet", "period": 0.3, "role": "integration"},
            {"abbrev": "Fls[4]", "name": "Feedback local TC", "period": 0.8, "role": "regulation"},
            {"abbrev": "B*[3]", "name": "Motor triad", "period": 0.2, "role": "output"},
            {"abbrev": "Ac[5]", "name": "Activated quintet", "period": 0.05, "role": "input"},
            {"abbrev": "V[3]", "name": "Voluntary triad", "period": 0.15, "role": "control"}
        ]
    },
    "emotion": {
        "name": "Emotion/Personality System",
        "abbrev": "Em/Pe",
        "components": [
            {"abbrev": "Em", "name": "Emotion", "period": 0.5, "role": "state"},
            {"abbrev": "Tc", "name": "Time crystal", "period": 0.33, "role": "pattern"},
            {"abbrev": "Thy", "name": "Thyroid", "period": 3600, "role": "metabolic"},
            {"abbrev": "Pe", "name": "Personality", "period": 86400, "role": "trait"},
            {"abbrev": "Tha", "name": "Thalamus", "period": 0.5, "role": "integration"},
            {"abbrev": "In", "name": "Insula", "period": 0.3, "role": "interoception"},
            {"abbrev": "Ci", "name": "Cingulate", "period": 0.4, "role": "monitoring"},
            {"abbrev": "St", "name": "Striatum", "period": 0.2, "role": "reward"},
            {"abbrev": "ACC", "name": "Anterior cingulate", "period": 0.35, "role": "executive"},
            {"abbrev": "PTC", "name": "Personality time crystal", "period": 86400, "role": "dynamics"}
        ]
    },
    "olfactory": {
        "name": "Olfactory System",
        "abbrev": "Ols",
        "components": [
            {"abbrev": "Ols(2)", "name": "Olfactory system", "period": 0.5, "role": "system"},
            {"abbrev": "N1(6)", "name": "Nose1 sensors", "period": 0.1, "role": "input"},
            {"abbrev": "N2(6)", "name": "Nose2 sensors", "period": 0.1, "role": "input"},
            {"abbrev": "Olc(2)", "name": "Olfactory cortex", "period": 0.3, "role": "processing"}
        ]
    },
    "entorhinal": {
        "name": "Entorhinal System",
        "abbrev": "EC",
        "components": [
            {"abbrev": "MEC(6)", "name": "Medial entorhinal", "period": 0.4, "role": "spatial"},
            {"abbrev": "LEC(5)", "name": "Lateral entorhinal", "period": 0.4, "role": "object"}
        ]
    },
    "spinal": {
        "name": "Spinal System",
        "abbrev": "Sp",
        "components": [
            {"abbrev": "Sc[3]", "name": "Spinal cord", "period": 0.05, "role": "pathway"},
            {"abbrev": "Mc", "name": "Meissner's corpuscle", "period": 0.01, "role": "sensor"},
            {"abbrev": "Ep", "name": "Epidermis layer", "period": 0.02, "role": "surface"},
            {"abbrev": "De", "name": "Dermis layer", "period": 0.03, "role": "deep"},
            {"abbrev": "Hy", "name": "Hypodermis layer", "period": 0.05, "role": "subcutaneous"},
            {"abbrev": "Nb", "name": "Nerve bundle", "period": 0.01, "role": "transmission"},
            {"abbrev": "Sa", "name": "Sacral", "period": 0.1, "role": "segment"},
            {"abbrev": "Lu", "name": "Lumbar", "period": 0.1, "role": "segment"},
            {"abbrev": "Ca", "name": "Cervical", "period": 0.1, "role": "segment"}
        ]
    }
}


@dataclass
class BrainComponent:
    """A component in the brain model."""
    abbrev: str
    name: str
    period: float
    level: int = 0
    region: str = ""
    role: str = ""


@dataclass
class BrainRegion:
    """A region of the brain."""
    name: str
    level: int
    scale: str
    components: List[BrainComponent] = field(default_factory=list)


@dataclass
class BrainSubsystem:
    """A functional subsystem of the brain."""
    name: str
    abbrev: str
    components: List[BrainComponent] = field(default_factory=list)


@dataclass
class TimeCrystalBrain:
    """Complete time crystal brain model."""
    name: str = "Time Crystal Brain"
    regions: List[BrainRegion] = field(default_factory=list)
    subsystems: List[BrainSubsystem] = field(default_factory=list)
    hierarchy_levels: int = 12
    total_components: int = 0
    
    def to_dict(self):
        return asdict(self)


def lcm(a: int, b: int) -> int:
    """Compute least common multiple."""
    return abs(a * b) // gcd(a, b)


def build_full_brain_model() -> TimeCrystalBrain:
    """Build a complete brain model with all regions and subsystems."""
    model = TimeCrystalBrain()
    
    # Add all regions
    for region_name, region_data in BRAIN_REGIONS.items():
        level_info = HIERARCHY_LEVELS[region_data["level"]]
        region = BrainRegion(
            name=region_name,
            level=region_data["level"],
            scale=level_info["scale"]
        )
        
        for comp_data in region_data["components"]:
            comp = BrainComponent(
                abbrev=comp_data["abbrev"],
                name=comp_data["name"],
                period=comp_data["period"],
                level=region_data["level"],
                region=region_name
            )
            region.components.append(comp)
            model.total_components += 1
        
        model.regions.append(region)
    
    # Add all subsystems
    for subsys_name, subsys_data in SUBSYSTEMS.items():
        subsystem = BrainSubsystem(
            name=subsys_data["name"],
            abbrev=subsys_data["abbrev"]
        )
        
        for comp_data in subsys_data["components"]:
            comp = BrainComponent(
                abbrev=comp_data["abbrev"],
                name=comp_data["name"],
                period=comp_data["period"],
                role=comp_data.get("role", "")
            )
            subsystem.components.append(comp)
        
        model.subsystems.append(subsystem)
    
    return model


def build_region_model(region_name: str) -> Optional[BrainRegion]:
    """Build a model for a specific brain region."""
    if region_name not in BRAIN_REGIONS:
        return None
    
    region_data = BRAIN_REGIONS[region_name]
    level_info = HIERARCHY_LEVELS[region_data["level"]]
    
    region = BrainRegion(
        name=region_name,
        level=region_data["level"],
        scale=level_info["scale"]
    )
    
    for comp_data in region_data["components"]:
        comp = BrainComponent(
            abbrev=comp_data["abbrev"],
            name=comp_data["name"],
            period=comp_data["period"],
            level=region_data["level"],
            region=region_name
        )
        region.components.append(comp)
    
    return region


def build_subsystem_model(subsys_name: str) -> Optional[BrainSubsystem]:
    """Build a model for a specific functional subsystem."""
    if subsys_name not in SUBSYSTEMS:
        return None
    
    subsys_data = SUBSYSTEMS[subsys_name]
    
    subsystem = BrainSubsystem(
        name=subsys_data["name"],
        abbrev=subsys_data["abbrev"]
    )
    
    for comp_data in subsys_data["components"]:
        comp = BrainComponent(
            abbrev=comp_data["abbrev"],
            name=comp_data["name"],
            period=comp_data["period"],
            role=comp_data.get("role", "")
        )
        subsystem.components.append(comp)
    
    return subsystem


def generate_hierarchy_summary(model: TimeCrystalBrain) -> str:
    """Generate a markdown summary of the brain hierarchy."""
    lines = [
        "# Time Crystal Brain Model Summary",
        "",
        f"**Total Hierarchy Levels**: {model.hierarchy_levels}",
        f"**Total Components**: {model.total_components}",
        f"**Regions**: {len(model.regions)}",
        f"**Subsystems**: {len(model.subsystems)}",
        "",
        "## Regions by Level",
        "",
        "| Level | Region | Scale | Components |",
        "|-------|--------|-------|------------|"
    ]
    
    for region in sorted(model.regions, key=lambda r: r.level):
        lines.append(f"| {region.level} | {region.name} | {region.scale} | {len(region.components)} |")
    
    lines.extend([
        "",
        "## Functional Subsystems",
        "",
        "| Subsystem | Abbrev | Components |",
        "|-----------|--------|------------|"
    ])
    
    for subsys in model.subsystems:
        lines.append(f"| {subsys.name} | {subsys.abbrev} | {len(subsys.components)} |")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Time Crystal Brain Model",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output JSON file path')
    parser.add_argument('--region', type=str, default=None,
                        help='Generate model for specific region')
    parser.add_argument('--subsystem', type=str, default=None,
                        help='Generate model for specific subsystem')
    parser.add_argument('--list-regions', action='store_true',
                        help='List available regions')
    parser.add_argument('--list-subsystems', action='store_true',
                        help='List available subsystems')
    parser.add_argument('--summary', action='store_true',
                        help='Generate markdown summary')
    
    args = parser.parse_args()
    
    if args.list_regions:
        print("Available brain regions:")
        for name, data in BRAIN_REGIONS.items():
            level = data["level"]
            scale = HIERARCHY_LEVELS[level]["scale"]
            print(f"  {name} (Level {level}, {scale})")
        return
    
    if args.list_subsystems:
        print("Available functional subsystems:")
        for name, data in SUBSYSTEMS.items():
            print(f"  {name}: {data['name']} ({data['abbrev']})")
        return
    
    # Build appropriate model
    if args.region:
        model = build_region_model(args.region)
        if model is None:
            print(f"Error: Unknown region '{args.region}'")
            print("Use --list-regions to see available regions")
            return
        output_data = asdict(model)
        print(f"Generated model for region: {args.region}")
        print(f"  Level: {model.level}")
        print(f"  Scale: {model.scale}")
        print(f"  Components: {len(model.components)}")
    
    elif args.subsystem:
        model = build_subsystem_model(args.subsystem)
        if model is None:
            print(f"Error: Unknown subsystem '{args.subsystem}'")
            print("Use --list-subsystems to see available subsystems")
            return
        output_data = asdict(model)
        print(f"Generated model for subsystem: {model.name}")
        print(f"  Abbreviation: {model.abbrev}")
        print(f"  Components: {len(model.components)}")
    
    else:
        model = build_full_brain_model()
        output_data = model.to_dict()
        print("Generated complete Time Crystal Brain Model")
        print(f"  Hierarchy Levels: {model.hierarchy_levels}")
        print(f"  Total Components: {model.total_components}")
        print(f"  Regions: {len(model.regions)}")
        print(f"  Subsystems: {len(model.subsystems)}")
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nModel saved to: {args.output}")
    
    if args.summary:
        if isinstance(model, TimeCrystalBrain):
            summary = generate_hierarchy_summary(model)
            summary_file = args.output.replace('.json', '_summary.md') if args.output else 'brain_summary.md'
            with open(summary_file, 'w') as f:
                f.write(summary)
            print(f"Summary saved to: {summary_file}")


if __name__ == '__main__':
    main()
