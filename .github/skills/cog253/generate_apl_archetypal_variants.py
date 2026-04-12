#!/usr/bin/env python3
"""
Generate archetypal variants of APL organizational documents.
Converts domain-specific architectural/urban terms to generic placeholders
that can be applied across different domains (Physical, Social, Conceptual, Psychic).
"""

import os
import re
from pathlib import Path

def load_apl_transformation_mappings():
    """Load transformation mappings specific to APL architectural/urban domain"""
    return {
        'regions': {
            'archetypal': 'regions',
            'physical': ['regions', 'areas', 'territories', 'zones'],
            'social': ['communities', 'groups', 'networks', 'organizations'],
            'conceptual': ['domains', 'fields', 'disciplines', 'areas'],
            'psychic': ['states', 'modes', 'realms', 'dimensions'],
            'network': ['network segments', 'topologies', 'domains', 'clusters'],
            'cell': ['cellular regions', 'membrane zones', 'organellar territories', 'cellular domains'],
            'os': ['memory regions', 'address spaces', 'system areas', 'kernel zones'],
            'llm': ['model layers', 'attention regions', 'parameter spaces', 'feature domains'],
            'github': ['organizations', 'enterprise regions', 'repository networks', 'team territories'],
            'azure': ['tenants', 'subscriptions', 'regions', 'resource groups'],
            'patternlanguage': ['pattern domains', 'design regions', 'architectural territories', 'language areas'],
            'ontology': ['knowledge domains', 'semantic regions', 'conceptual territories', 'ontological spaces'],
            'introspection': ['awareness regions', 'reflective territories', 'consciousness domains', 'metacognitive areas'],
            'hypergraph': ['hypergraph regions', 'connectivity domains', 'structural territories', 'relational areas'],
            'autognosis': ['self-aware regions', 'autonomous territories', 'self-creating domains', 'generative areas'],
            'transformation': ['change regions', 'transformation domains', 'metamorphic territories', 'evolutionary areas']
        },
        'towns': {
            'archetypal': 'settlements',
            'physical': ['towns', 'cities', 'villages', 'communities'],
            'social': ['organizations', 'institutions', 'groups', 'collectives'],
            'conceptual': ['systems', 'frameworks', 'structures', 'paradigms'],
            'psychic': ['patterns', 'structures', 'formations', 'configurations'],
            'network': ['network clusters', 'node groups', 'subnet communities', 'protocol families'],
            'cell': ['organelle clusters', 'molecular complexes', 'cellular compartments', 'metabolic centers'],
            'os': ['process groups', 'service clusters', 'system modules', 'kernel subsystems'],
            'llm': ['model architectures', 'transformer blocks', 'layer groups', 'attention families'],
            'github': ['repositories', 'project collections', 'workflow groups', 'action families'],
            'azure': ['resource groups', 'service clusters', 'application groups', 'management hierarchies'],
            'patternlanguage': ['pattern libraries', 'design collections', 'architectural families', 'language systems'],
            'ontology': ['knowledge bases', 'semantic clusters', 'concept hierarchies', 'classification systems'],
            'introspection': ['reflection systems', 'awareness clusters', 'metacognitive frameworks', 'self-examination groups'],
            'hypergraph': ['hypergraph clusters', 'connectivity systems', 'relational groups', 'structural families'],
            'autognosis': ['self-organizing clusters', 'autonomous groups', 'self-creating systems', 'generative communities'],
            'transformation': ['change systems', 'metamorphic clusters', 'transformation groups', 'evolutionary families']
        },
        'buildings': {
            'archetypal': 'structures',
            'physical': ['buildings', 'structures', 'constructions', 'facilities'],
            'social': ['institutions', 'organizations', 'groups', 'entities'],
            'conceptual': ['concepts', 'ideas', 'frameworks', 'models'],
            'psychic': ['patterns', 'forms', 'structures', 'configurations'],
            'network': ['nodes', 'routers', 'switches', 'servers'],
            'cell': ['organelles', 'protein complexes', 'molecular machines', 'cellular structures'],
            'os': ['processes', 'services', 'modules', 'drivers'],
            'llm': ['models', 'neural networks', 'transformer units', 'attention blocks'],
            'github': ['repositories', 'projects', 'workflows', 'actions'],
            'azure': ['resources', 'services', 'applications', 'components'],
            'patternlanguage': ['patterns', 'design structures', 'architectural units', 'language constructs'],
            'ontology': ['concepts', 'entities', 'knowledge structures', 'semantic units'],
            'introspection': ['thoughts', 'reflections', 'awareness structures', 'metacognitive units'],
            'hypergraph': ['hypergraph nodes', 'structural units', 'connectivity elements', 'relational constructs'],
            'autognosis': ['self-aware entities', 'autonomous structures', 'self-creating units', 'generative forms'],
            'transformation': ['transformers', 'change structures', 'metamorphic units', 'evolutionary forms']
        },
        'streets': {
            'archetypal': 'pathways',
            'physical': ['streets', 'roads', 'paths', 'thoroughfares'],
            'social': ['connections', 'relationships', 'networks', 'communications'],
            'conceptual': ['links', 'associations', 'connections', 'relationships'],
            'psychic': ['flows', 'currents', 'streams', 'channels'],
            'network': ['connections', 'links', 'channels', 'pipelines'],
            'cell': ['transport pathways', 'signaling cascades', 'molecular channels', 'membrane passages'],
            'os': ['inter-process communication', 'system buses', 'network protocols', 'data pipelines'],
            'llm': ['attention connections', 'data flows', 'information pathways', 'token streams'],
            'github': ['collaborations', 'forks', 'pull requests', 'workflow triggers'],
            'azure': ['network connections', 'service links', 'data pipelines', 'communication channels'],
            'patternlanguage': ['pattern connections', 'design pathways', 'architectural links', 'language bridges'],
            'ontology': ['semantic relations', 'knowledge pathways', 'conceptual connections', 'ontological links'],
            'introspection': ['reflection pathways', 'awareness connections', 'metacognitive links', 'self-examination channels'],
            'hypergraph': ['hyperedges', 'multi-way connections', 'relational pathways', 'structural links'],
            'autognosis': ['self-referential pathways', 'autonomous connections', 'self-creating links', 'generative channels'],
            'transformation': ['change pathways', 'metamorphic connections', 'transformation links', 'evolutionary channels']
        },
        'spaces': {
            'archetypal': 'spaces',
            'physical': ['spaces', 'areas', 'places', 'locations'],
            'social': ['environments', 'contexts', 'settings', 'domains'],
            'conceptual': ['realms', 'spheres', 'domains', 'territories'],
            'psychic': ['states', 'conditions', 'modes', 'dimensions'],
            'network': ['address spaces', 'data spaces', 'memory pools', 'buffer zones'],
            'cell': ['cytoplasm', 'nucleoplasm', 'organellar spaces', 'membrane environments'],
            'os': ['memory spaces', 'virtual environments', 'execution contexts', 'namespace domains'],
            'llm': ['embedding spaces', 'attention spaces', 'feature dimensions', 'representation realms'],
            'github': ['workspaces', 'repository environments', 'action contexts', 'collaboration spaces'],
            'azure': ['compute environments', 'storage spaces', 'network domains', 'security contexts'],
            'patternlanguage': ['design spaces', 'pattern environments', 'architectural contexts', 'language domains'],
            'ontology': ['semantic spaces', 'knowledge domains', 'conceptual environments', 'meaning contexts'],
            'introspection': ['awareness spaces', 'reflective environments', 'metacognitive domains', 'consciousness contexts'],
            'hypergraph': ['hypergraph spaces', 'connectivity environments', 'relational domains', 'structural contexts'],
            'autognosis': ['self-aware spaces', 'autonomous environments', 'self-creating domains', 'generative contexts'],
            'transformation': ['transformation spaces', 'change environments', 'metamorphic domains', 'evolutionary contexts']
        },
        'people': {
            'archetypal': 'agents',
            'physical': ['people', 'inhabitants', 'users', 'occupants'],
            'social': ['members', 'participants', 'actors', 'agents'],
            'conceptual': ['elements', 'components', 'factors', 'variables'],
            'psychic': ['aspects', 'facets', 'elements', 'dimensions'],
            'network': ['nodes', 'endpoints', 'devices', 'clients'],
            'cell': ['molecules', 'proteins', 'enzymes', 'cellular actors'],
            'os': ['processes', 'threads', 'users', 'system actors'],
            'llm': ['tokens', 'parameters', 'embeddings', 'model components'],
            'github': ['contributors', 'maintainers', 'collaborators', 'developers'],
            'azure': ['users', 'service principals', 'managed identities', 'resource actors'],
            'patternlanguage': ['pattern authors', 'designers', 'architects', 'language creators'],
            'ontology': ['knowledge engineers', 'domain experts', 'concept creators', 'semantic agents'],
            'introspection': ['reflective agents', 'self-observers', 'metacognitive actors', 'awareness practitioners'],
            'hypergraph': ['hypergraph nodes', 'connectivity agents', 'relational actors', 'structural elements'],
            'autognosis': ['self-aware agents', 'autonomous actors', 'self-creating entities', 'generative beings'],
            'transformation': ['change agents', 'transformers', 'metamorphic actors', 'evolutionary catalysts']
        },
        'activities': {
            'archetypal': 'processes',
            'physical': ['activities', 'functions', 'uses', 'operations'],
            'social': ['interactions', 'communications', 'exchanges', 'processes'],
            'conceptual': ['operations', 'processes', 'functions', 'activities'],
            'psychic': ['experiences', 'processes', 'activities', 'functions'],
            'network': ['data flows', 'computations', 'transmissions', 'processing'],
            'cell': ['metabolism', 'protein synthesis', 'cellular processes', 'reactions'],
            'os': ['system calls', 'process execution', 'operations', 'scheduling'],
            'llm': ['inference', 'training', 'attention', 'generation'],
            'github': ['commits', 'merges', 'deployments', 'workflows'],
            'azure': ['provisioning', 'scaling', 'monitoring', 'deployments'],
            'patternlanguage': ['pattern creation', 'design processes', 'architectural activities', 'language development'],
            'ontology': ['knowledge modeling', 'concept definition', 'semantic mapping', 'classification activities'],
            'introspection': ['self-reflection', 'awareness practices', 'metacognitive processes', 'self-examination'],
            'hypergraph': ['hypergraph construction', 'connectivity operations', 'relational processes', 'structural activities'],
            'autognosis': ['self-organization', 'autonomous generation', 'self-creation processes', 'generative activities'],
            'transformation': ['change processes', 'metamorphic activities', 'transformation operations', 'evolutionary functions']
        }
    }

def identify_architectural_terms(text):
    """Identify architectural/urban planning terms that should be made archetypal"""
    # Common architectural/urban terms to replace
    architectural_terms = {
        r'\b(region|regions)\b': '{{regions}}',
        r'\b(town|towns|city|cities|village|villages)\b': '{{settlements}}',
        r'\b(building|buildings|structure|structures|house|houses)\b': '{{structures}}',
        r'\b(street|streets|road|roads|path|paths)\b': '{{pathways}}',  
        r'\b(space|spaces|room|rooms|area|areas)\b': '{{spaces}}',
        r'\b(people|person|inhabitants|residents|users)\b': '{{agents}}',
        r'\b(activities|activity|functions|function)\b': '{{processes}}',
        r'\b(neighborhood|neighborhoods|community|communities)\b': '{{localities}}',
        r'\b(construction|building process|development)\b': '{{creation}}',
        r'\b(parking|transportation|traffic)\b': '{{movement}}',
    }
    
    archetypal_text = text
    for pattern, replacement in architectural_terms.items():
        archetypal_text = re.sub(pattern, replacement, archetypal_text, flags=re.IGNORECASE)
    
    return archetypal_text

def generate_archetypal_variant(title, content, file_type="document"):
    """Generate an archetypal variant of an APL document"""
    
    # Convert content to archetypal form
    archetypal_content = identify_architectural_terms(content)
    
    # Create the archetypal variant markdown
    variant_content = f"""# {title} (Archetypal Variant)

## Archetypal Pattern

{archetypal_content}

## Domain Transformations

This archetypal variant uses the following domain-specific placeholders:

- `{{{{regions}}}}` → Physical: regions/territories | Social: communities/networks | Conceptual: domains/fields | Psychic: states/realms
- `{{{{settlements}}}}` → Physical: towns/cities | Social: organizations/institutions | Conceptual: systems/frameworks | Psychic: patterns/structures  
- `{{{{structures}}}}` → Physical: buildings/facilities | Social: institutions/entities | Conceptual: concepts/models | Psychic: patterns/forms
- `{{{{pathways}}}}` → Physical: streets/roads | Social: connections/networks | Conceptual: links/associations | Psychic: flows/channels
- `{{{{spaces}}}}` → Physical: spaces/places | Social: environments/contexts | Conceptual: realms/domains | Psychic: states/dimensions
- `{{{{agents}}}}` → Physical: people/inhabitants | Social: members/participants | Conceptual: elements/components | Psychic: aspects/facets
- `{{{{processes}}}}` → Physical: activities/functions | Social: interactions/communications | Conceptual: operations/processes | Psychic: experiences/activities
- `{{{{localities}}}}` → Physical: neighborhoods/communities | Social: groups/collectives | Conceptual: clusters/groupings | Psychic: formations/configurations
- `{{{{creation}}}}` → Physical: construction/development | Social: formation/establishment | Conceptual: development/creation | Psychic: emergence/formation
- `{{{{movement}}}}` → Physical: transportation/traffic | Social: communication/flow | Conceptual: information flow/exchange | Psychic: energy flow/circulation

## Usage Instructions

To use this archetypal variant:

1. **Select your domain**: Physical, Social, Conceptual, or Psychic
2. **Replace placeholders**: Substitute each `{{{{placeholder}}}}` with appropriate domain-specific terms
3. **Adapt context**: Modify surrounding text as needed to maintain coherence in your chosen domain

## Original Content

{content}

---
*Generated as archetypal variant from APL organizational document*
"""
    
    return variant_content

def create_apl_archetypal_variants():
    """Create archetypal variants for the requested APL documents"""
    
    # Create output directory
    apl_arc_dir = Path("markdown/apl_arc")
    apl_arc_dir.mkdir(exist_ok=True)
    
    # Define the documents to process
    documents = [
        {
            'source': 'pattern/5-foldpatt.md',
            'output': 'apl_arc_5-fold_pattern_language.md',
            'title': '5-fold Pattern Language'
        },
        {
            'source': 'markdown/apl/aplsummary.md', 
            'output': 'apl_arc_apl_summary.md',
            'title': 'APL Pattern Language Summary'
        },
        {
            'source': 'markdown/apl/Hierarchies - No asterisks.md',
            'output': 'apl_arc_hierarchies_no_asterisks.md', 
            'title': 'Pattern Hierarchies - No Asterisks'
        },
        {
            'source': 'markdown/apl/Hierarchies - One Asterisk.md',
            'output': 'apl_arc_hierarchies_one_asterisk.md',
            'title': 'Pattern Hierarchies - One Asterisk'
        },
        {
            'source': 'markdown/apl/Hierarchies - Two Asterisks.md',
            'output': 'apl_arc_hierarchies_two_asterisks.md',
            'title': 'Pattern Hierarchies - Two Asterisks'
        },
        {
            'source': 'markdown/apl/aplbullets.md',
            'output': 'apl_arc_patterns_list.md',
            'title': 'Patterns List - APL'
        }
    ]
    
    created_files = []
    
    for doc in documents:
        source_path = Path(doc['source'])
        output_path = apl_arc_dir / doc['output']
        
        # Read source content
        if source_path.exists():
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
        else:
            print(f"Warning: Source file {source_path} not found, creating placeholder")
            content = f"# {doc['title']}\n\nThis document represents {doc['title'].lower()} organizational principles."
        
        # Handle empty or minimal content
        if not content or content == "list":
            content = f"# {doc['title']}\n\nThis document represents {doc['title'].lower()} organizational principles and patterns."
        
        # Generate archetypal variant
        variant_content = generate_archetypal_variant(doc['title'], content)
        
        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(variant_content)
        
        created_files.append(output_path)
        print(f"Created: {output_path}")
    
    # Create The Timeless Way of Building archetypal variant
    timeless_content = """# The Timeless Way of Building

The {{settlements}} that are alive are always grown from the inside, by the ordinary acts of {{agents}} who create {{structures}} and {{spaces}} which are adapted to their own nature and their own {{processes}}.

When {{agents}} have the freedom to act in response to the forces they feel directly, they will create {{structures}} which are perfectly adapted to those forces, and, through the repetition of this process, over many years, the whole {{settlement}} will develop into a totality which is at peace with itself, and beautiful.

The quality without a name is the most fundamental quality there is in anything. It is the quality that makes the difference between what is alive and what is dead. It is a quality which belongs to whole systems. It is the source of all real activity, all real freedom, all real life.

In the end, this quality cannot be made, but only generated, indirectly, by the ordinary {{agents}} of a place, doing everything which makes them feel alive."""

    timeless_variant = generate_archetypal_variant("The Timeless Way of Building", timeless_content)
    timeless_path = apl_arc_dir / "apl_arc_timeless_way_of_building.md"
    
    with open(timeless_path, 'w', encoding='utf-8') as f:
        f.write(timeless_variant)
    
    created_files.append(timeless_path)
    print(f"Created: {timeless_path}")
    
    # Create README for APL archetypal variants
    create_apl_archetypal_readme(apl_arc_dir, created_files)
    
    return created_files

def create_apl_archetypal_readme(output_dir, created_files):
    """Create README documentation for APL archetypal variants"""
    
    readme_content = """# APL Archetypal Variants

This directory contains archetypal variants of key APL (A Pattern Language) organizational documents.

## What are APL Archetypal Variants?

These are abstracted versions of Christopher Alexander's architectural and urban planning documents where domain-specific architectural terms have been replaced with generic placeholders. This allows the same organizational principles to be applied across different domains:

- **Physical**: Architecture, urban planning, spatial design
- **Social**: Organizations, communities, social systems  
- **Conceptual**: Knowledge systems, information architecture, conceptual frameworks
- **Psychic**: Mental structures, consciousness patterns, psychological organization

## Document Format

Each archetypal variant includes:

1. **Archetypal Pattern**: The document content with domain-specific placeholders
2. **Domain Transformations**: Explanation of how placeholders map to different domains
3. **Usage Instructions**: How to apply the archetypal variant to specific domains
4. **Original Content**: The original APL document for reference

## Generated Variants

The following APL archetypal variants have been generated:

- **apl_arc_5-fold_pattern_language.md**: 5-fold Pattern Language archetypal variant
- **apl_arc_apl_summary.md**: APL Pattern Language Summary archetypal variant
- **apl_arc_hierarchies_no_asterisks.md**: Pattern Hierarchies - No Asterisks archetypal variant
- **apl_arc_hierarchies_one_asterisk.md**: Pattern Hierarchies - One Asterisk archetypal variant
- **apl_arc_hierarchies_two_asterisks.md**: Pattern Hierarchies - Two Asterisks archetypal variant
- **apl_arc_patterns_list.md**: Patterns List - APL archetypal variant
- **apl_arc_timeless_way_of_building.md**: The Timeless Way of Building archetypal variant

## Usage Examples

### Physical Domain Application
Replace `{{settlements}}` with "towns/cities", `{{structures}}` with "buildings", `{{pathways}}` with "streets"

### Social Domain Application  
Replace `{{settlements}}` with "organizations", `{{structures}}` with "institutions", `{{pathways}}` with "communications"

### Conceptual Domain Application
Replace `{{settlements}}` with "systems", `{{structures}}` with "concepts", `{{pathways}}` with "associations"

### Psychic Domain Application
Replace `{{settlements}}` with "patterns", `{{structures}}` with "mental forms", `{{pathways}}` with "flows"

## Transformation Principles

The archetypal variants follow these transformation principles:

1. **Spatial → Generic**: Physical spaces become generic spaces/realms
2. **Material → Abstract**: Physical materials become abstract elements  
3. **Human → Agent**: People become generic agents/actors
4. **Activity → Process**: Specific activities become generic processes
5. **Scale → Hierarchical**: Size relationships become hierarchical relationships

---
*Generated archetypal variants from Christopher Alexander's A Pattern Language*
"""
    
    readme_path = output_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"Created: {readme_path}")

if __name__ == "__main__":
    print("Generating APL archetypal variants...")
    created_files = create_apl_archetypal_variants()
    print(f"\nGenerated {len(created_files)} archetypal variants:")
    for file_path in created_files:
        print(f"  - {file_path}")
    print("\nAPL archetypal variants generation complete!")