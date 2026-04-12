#!/usr/bin/env python3
"""
Generate GitHub Actions workflow from learned build order.

Reads the neural network's learned tier assignments and dependency graph
to produce an optimal-build.yml with maximized concurrency per tier.

Usage:
  python3 generate_gha.py --knowledge learned_knowledge.json --output optimal-build.yml
"""

import json
import argparse
import yaml
from collections import defaultdict


def generate_workflow(knowledge_path, output_path):
    with open(knowledge_path) as f:
        knowledge = json.load(f)
    
    tiers = knowledge['learned_tiers']
    deps = knowledge.get('learned_deps', {})
    
    # Group by tier
    tier_groups = defaultdict(list)
    for comp, tier in tiers.items():
        tier_groups[tier].append(comp)
    
    # Build workflow
    workflow = {
        'name': 'Optimal Build (Neural)',
        'on': {
            'push': {'branches': ['main']},
            'workflow_dispatch': {},
        },
        'jobs': {},
    }
    
    for tier in sorted(tier_groups.keys()):
        comps = sorted(tier_groups[tier])
        
        # Filter to buildable components (cmake or make)
        job_id = f'tier-{tier}'
        needs = [f'tier-{t}' for t in range(tier) if t in tier_groups]
        
        job = {
            'name': f'Tier {tier} ({len(comps)} components)',
            'runs-on': 'ubuntu-latest',
            'strategy': {
                'matrix': {
                    'component': comps,
                },
                'fail-fast': False,
            },
            'steps': [
                {'uses': 'actions/checkout@v4'},
                {
                    'name': 'Build ${{ matrix.component }}',
                    'run': f'echo "Building ${{{{ matrix.component }}}}" # Tier {tier}',
                },
            ],
        }
        
        if needs:
            job['needs'] = needs
        
        workflow['jobs'][job_id] = job
    
    # Write YAML
    with open(output_path, 'w') as f:
        yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)
    
    print(f"Generated {output_path}")
    print(f"  Tiers: {len(tier_groups)}")
    print(f"  Jobs: {len(workflow['jobs'])}")
    total = sum(len(v) for v in tier_groups.values())
    print(f"  Components: {total}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--knowledge', default='/home/ubuntu/learned_knowledge.json')
    parser.add_argument('--output', default='/home/ubuntu/optimal-build.yml')
    args = parser.parse_args()
    generate_workflow(args.knowledge, args.output)
