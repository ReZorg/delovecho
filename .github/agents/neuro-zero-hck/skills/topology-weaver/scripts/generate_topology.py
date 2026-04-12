#!/usr/bin/env python3
"""
Topology Generator for Topology Weaver
Generates MLP topology specifications with contextual tags from terminology.
"""

import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional
import yaml


@dataclass
class ContextualTag:
    """A contextual tag derived from terminology."""
    name: str
    source_term: str
    category: str
    description: str


@dataclass
class IntegrationPoint:
    """An integration point for attention meshworks."""
    name: str
    point_type: str  # wave_input, superposition_state, wave_output
    connects_to: List[str]
    tag: Optional[ContextualTag] = None


@dataclass
class MLPComponent:
    """A component of the MLP block."""
    name: str
    component_type: str  # linear, activation
    input_dim: Optional[int] = None
    output_dim: Optional[int] = None
    tag: Optional[ContextualTag] = None
    parameters: Dict = field(default_factory=dict)


@dataclass
class MLPBlock:
    """An MLP block with contextual tags."""
    name: str
    components: List[MLPComponent]
    integration_points: List[IntegrationPoint]
    tags: List[ContextualTag]


@dataclass
class Topology:
    """Complete topology specification."""
    name: str
    architecture: str
    d_model: int
    n_layers: int
    mlp_blocks: List[MLPBlock]
    global_tags: List[ContextualTag]
    meshwork_anchors: List[IntegrationPoint]


# GPT-2 architecture configurations
GPT2_CONFIGS = {
    'gpt2': {'d_model': 768, 'n_layers': 12, 'n_heads': 12},
    'gpt2-medium': {'d_model': 1024, 'n_layers': 24, 'n_heads': 16},
    'gpt2-large': {'d_model': 1280, 'n_layers': 36, 'n_heads': 20},
    'gpt2-xl': {'d_model': 1600, 'n_layers': 48, 'n_heads': 25},
}

# Default tag mappings
DEFAULT_TAG_MAPPINGS = {
    'particle': ('discrete_feature', 'Discrete, position-local feature detector'),
    'wave': ('distributed_field', 'Distributed activation pattern'),
    'transformation': ('field_evolution', 'Forward propagation transformation'),
    'interaction': ('coupling_point', 'Weight interaction / coupling'),
    'measurement': ('measurement_gate', 'Nonlinearity / collapse point'),
    'state': ('superposed_state', 'Hidden state superposition'),
    'flow': ('residual_flow', 'Residual stream flow'),
    'composition': ('hierarchical_nest', 'Nested compositional structure'),
}


class TopologyGenerator:
    """Generate MLP topology from terminology."""
    
    def __init__(self, architecture: str = 'gpt2'):
        if architecture not in GPT2_CONFIGS:
            raise ValueError(f"Unknown architecture: {architecture}")
        
        self.architecture = architecture
        self.config = GPT2_CONFIGS[architecture]
        self.terminology = {}
        self.tag_mappings = dict(DEFAULT_TAG_MAPPINGS)
    
    def load_terminology(self, filepath: str):
        """Load terminology from JSON file."""
        with open(filepath) as f:
            self.terminology = json.load(f)
        
        # Update tag mappings from terminology clusters
        for cluster in self.terminology.get('clusters', []):
            category = cluster['name'].replace('_cluster', '')
            if cluster.get('architectural_mapping'):
                central = cluster['central_concept']
                self.tag_mappings[category] = (
                    cluster['architectural_mapping'],
                    f"Derived from '{central}' in source context"
                )
    
    def generate(self, name: str = 'topology') -> Topology:
        """Generate the topology specification."""
        d_model = self.config['d_model']
        n_layers = self.config['n_layers']
        
        # Generate global tags from terminology
        global_tags = self._generate_global_tags()
        
        # Generate MLP blocks for each layer
        mlp_blocks = []
        for layer_idx in range(n_layers):
            block = self._generate_mlp_block(layer_idx, d_model)
            mlp_blocks.append(block)
        
        # Generate meshwork anchors
        meshwork_anchors = self._generate_meshwork_anchors()
        
        return Topology(
            name=name,
            architecture=self.architecture,
            d_model=d_model,
            n_layers=n_layers,
            mlp_blocks=mlp_blocks,
            global_tags=global_tags,
            meshwork_anchors=meshwork_anchors
        )
    
    def _generate_global_tags(self) -> List[ContextualTag]:
        """Generate global contextual tags."""
        tags = []
        for category, (tag_name, description) in self.tag_mappings.items():
            # Find source term from terminology
            source_term = category
            if self.terminology:
                for cluster in self.terminology.get('clusters', []):
                    if cluster['name'].replace('_cluster', '') == category:
                        source_term = cluster['central_concept']
                        break
            
            tags.append(ContextualTag(
                name=tag_name,
                source_term=source_term,
                category=category,
                description=description
            ))
        return tags
    
    def _generate_mlp_block(self, layer_idx: int, d_model: int) -> MLPBlock:
        """Generate an MLP block for a layer."""
        hidden_dim = 4 * d_model  # GPT-2 uses 4x expansion
        
        # Create components with contextual tags
        components = [
            MLPComponent(
                name=f'c_fc_{layer_idx}',
                component_type='linear',
                input_dim=d_model,
                output_dim=hidden_dim,
                tag=ContextualTag(
                    name='particle_creation',
                    source_term=self._find_term('particle', 'transformation'),
                    category='projection',
                    description='Projects to higher-dimensional particle space'
                ),
                parameters={'bias': True}
            ),
            MLPComponent(
                name=f'gelu_{layer_idx}',
                component_type='activation',
                tag=ContextualTag(
                    name='measurement_gate',
                    source_term=self._find_term('measurement', 'collapse'),
                    category='nonlinearity',
                    description='GELU activation as measurement/collapse operation'
                ),
                parameters={'approximate': 'tanh'}
            ),
            MLPComponent(
                name=f'c_proj_{layer_idx}',
                component_type='linear',
                input_dim=hidden_dim,
                output_dim=d_model,
                tag=ContextualTag(
                    name='particle_annihilation',
                    source_term=self._find_term('particle', 'transformation'),
                    category='projection',
                    description='Projects back to model dimension (particle annihilation)'
                ),
                parameters={'bias': True}
            ),
        ]
        
        # Create integration points
        integration_points = [
            IntegrationPoint(
                name=f'pre_mlp_{layer_idx}',
                point_type='wave_input',
                connects_to=['attention_output', 'residual_stream'],
                tag=ContextualTag(
                    name='wave_entry',
                    source_term=self._find_term('wave', 'flow'),
                    category='integration',
                    description='Wave function enters MLP block'
                )
            ),
            IntegrationPoint(
                name=f'post_fc_{layer_idx}',
                point_type='superposition_state',
                connects_to=['gating_mechanism', 'skip_connection'],
                tag=ContextualTag(
                    name='superposition_peak',
                    source_term=self._find_term('state', 'superposition'),
                    category='integration',
                    description='Maximum superposition at hidden layer'
                )
            ),
            IntegrationPoint(
                name=f'post_mlp_{layer_idx}',
                point_type='wave_output',
                connects_to=['next_layer_input', 'residual_stream'],
                tag=ContextualTag(
                    name='wave_exit',
                    source_term=self._find_term('wave', 'flow'),
                    category='integration',
                    description='Wave function exits MLP block'
                )
            ),
        ]
        
        # Collect all tags
        tags = [c.tag for c in components if c.tag] + \
               [ip.tag for ip in integration_points if ip.tag]
        
        return MLPBlock(
            name=f'mlp_block_{layer_idx}',
            components=components,
            integration_points=integration_points,
            tags=tags
        )
    
    def _generate_meshwork_anchors(self) -> List[IntegrationPoint]:
        """Generate global meshwork anchor points."""
        return [
            IntegrationPoint(
                name='attention_query_anchor',
                point_type='query_field',
                connects_to=['mlp_output', 'position_encoding'],
                tag=ContextualTag(
                    name='query_wave',
                    source_term=self._find_term('wave', 'field'),
                    category='attention',
                    description='Query wave for attention computation'
                )
            ),
            IntegrationPoint(
                name='attention_key_anchor',
                point_type='key_field',
                connects_to=['mlp_output', 'position_encoding'],
                tag=ContextualTag(
                    name='key_wave',
                    source_term=self._find_term('wave', 'field'),
                    category='attention',
                    description='Key wave for attention computation'
                )
            ),
            IntegrationPoint(
                name='attention_value_anchor',
                point_type='value_field',
                connects_to=['mlp_output', 'content_stream'],
                tag=ContextualTag(
                    name='value_particle',
                    source_term=self._find_term('particle', 'state'),
                    category='attention',
                    description='Value particles carrying content'
                )
            ),
        ]
    
    def _find_term(self, *categories: str) -> str:
        """Find a term from terminology matching categories."""
        if not self.terminology:
            return categories[0]
        
        for category in categories:
            for cluster in self.terminology.get('clusters', []):
                if cluster['name'].replace('_cluster', '') == category:
                    return cluster['central_concept']
        
        # Fallback to first category
        return categories[0]


def topology_to_dict(topology: Topology) -> dict:
    """Convert topology to dictionary, handling nested dataclasses."""
    def convert(obj):
        if hasattr(obj, '__dataclass_fields__'):
            return {k: convert(v) for k, v in asdict(obj).items()}
        elif isinstance(obj, list):
            return [convert(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        return obj
    
    return convert(topology)


def main():
    parser = argparse.ArgumentParser(
        description='Generate MLP topology with contextual tags'
    )
    parser.add_argument(
        '--terminology', '-t',
        help='Path to terminology.json file'
    )
    parser.add_argument(
        '--architecture', '-a',
        default='gpt2',
        choices=list(GPT2_CONFIGS.keys()),
        help='Architecture to generate (default: gpt2)'
    )
    parser.add_argument(
        '--output', '-o',
        default='topology.yaml',
        help='Output file path (default: topology.yaml)'
    )
    parser.add_argument(
        '--name', '-n',
        default='generated_topology',
        help='Name for the topology'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['yaml', 'json'],
        default='yaml',
        help='Output format (default: yaml)'
    )
    
    args = parser.parse_args()
    
    # Generate topology
    generator = TopologyGenerator(args.architecture)
    
    if args.terminology:
        print(f"Loading terminology from: {args.terminology}")
        generator.load_terminology(args.terminology)
    
    print(f"Generating {args.architecture} topology...")
    topology = generator.generate(args.name)
    
    # Convert to dict
    topology_dict = topology_to_dict(topology)
    
    # Write output
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
        if args.format == 'yaml' or output_path.suffix in ['.yaml', '.yml']:
            yaml.dump(topology_dict, f, default_flow_style=False, sort_keys=False)
        else:
            json.dump(topology_dict, f, indent=2)
    
    print(f"✓ Generated topology: {args.name}")
    print(f"✓ Architecture: {args.architecture}")
    print(f"✓ Dimensions: d_model={topology.d_model}, n_layers={topology.n_layers}")
    print(f"✓ Global tags: {len(topology.global_tags)}")
    print(f"✓ Meshwork anchors: {len(topology.meshwork_anchors)}")
    print(f"✓ Output written to: {args.output}")


if __name__ == "__main__":
    main()
