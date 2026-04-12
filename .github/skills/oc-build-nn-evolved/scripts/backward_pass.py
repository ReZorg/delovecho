#!/usr/bin/env python3
"""
Backward Pass: Self-Improvement Engine for oc-build-nn-evolved

This script implements the skill's backward pass — the self-improvement logic
that updates the skill's knowledge state based on feedback signals.

Feedback types:
  1. Build failure: A CI build failed → update dependency logits
  2. New repo: A new repository was added → expand network dimensions
  3. Repo archived: A repository was archived → prune from network
  4. Cross-org integration: A new cross-org dependency detected → update bridge
  5. User feedback: Explicit correction → direct parameter update

Usage:
  python3 backward_pass.py --feedback build_failure --component atomspace --missing cogutil
  python3 backward_pass.py --feedback new_repo --repo opencog/new-component --deps cogutil,atomspace
  python3 backward_pass.py --feedback rescan  # Full rescan of both orgs
"""

import json
import argparse
import subprocess
import os
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(SKILL_DIR, 'model')
SCRIPTS_DIR = os.path.join(SKILL_DIR, 'scripts')


def load_model():
    """Load the current neural state"""
    model_path = os.path.join(MODEL_DIR, 'build_model.json')
    if os.path.exists(model_path):
        with open(model_path) as f:
            return json.load(f)
    return None


def save_model(model):
    """Save updated neural state"""
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, 'build_model.json')
    with open(model_path, 'w') as f:
        json.dump(model, f, indent=2)
    print(f"  Model saved to {model_path}")


def handle_build_failure(args):
    """Update network from a build failure signal"""
    print(f"  Build failure: {args.component} missing deps: {args.missing}")
    
    # Import and update the network
    sys.path.insert(0, SCRIPTS_DIR)
    from neural_build_path import DualOrgBuildPathNetwork
    
    topo_path = os.path.join(MODEL_DIR, 'topology.json')
    if not os.path.exists(topo_path):
        topo_path = '/home/ubuntu/topology_analysis.json'
    
    net = DualOrgBuildPathNetwork(topo_path)
    
    # Load saved state if exists
    state_path = os.path.join(MODEL_DIR, 'neural_state.json')
    if os.path.exists(state_path):
        net.load_state(state_path)
    
    # Single online learning step
    output = net.forward()
    
    # Create synthetic build result with the failure
    build_results = []
    for comp, step in output['build_order']:
        if comp == args.component:
            build_results.append((comp, step, False, args.missing.split(',')))
        else:
            build_results.append((comp, step, True, []))
    
    net.zeroGradParameters()
    grad = net.backward(None, build_results)
    net.updateParameters(0.05)  # Conservative lr for online learning
    
    net.save_state(state_path)
    print(f"  Updated: loss={grad['loss']:.4f}")


def handle_new_repo(args):
    """Expand network for a new repository"""
    print(f"  New repo: {args.repo}")
    print(f"  Dependencies: {args.deps}")
    print("  → Triggering full rescan and retrain")
    handle_rescan(args)


def handle_rescan(args):
    """Full rescan of both orgs and retrain"""
    print("  Rescanning opencog/* and openclaw/*...")
    
    # Run topology analysis
    topo_script = os.path.join(SCRIPTS_DIR, 'analyze_topology.py')
    subprocess.run([sys.executable, topo_script], check=True)
    
    # Retrain
    nn_script = os.path.join(SCRIPTS_DIR, 'neural_build_path.py')
    subprocess.run([
        sys.executable, nn_script,
        '--epochs', '300',
        '--lr', '0.1',
        '--output', os.path.join(MODEL_DIR, 'neural_state.json'),
        '--knowledge', os.path.join(MODEL_DIR, 'learned_knowledge.json'),
    ], check=True)
    
    print("  Rescan and retrain complete")


def main():
    parser = argparse.ArgumentParser(description='Backward Pass: Self-Improvement Engine')
    parser.add_argument('--feedback', required=True,
                       choices=['build_failure', 'new_repo', 'repo_archived', 'rescan'],
                       help='Type of feedback signal')
    parser.add_argument('--component', help='Component name (for build_failure)')
    parser.add_argument('--missing', help='Missing dependencies (for build_failure)')
    parser.add_argument('--repo', help='Repository name (for new_repo)')
    parser.add_argument('--deps', help='Dependencies (for new_repo)')
    
    args = parser.parse_args()
    
    print(f"Backward Pass: processing {args.feedback} signal")
    
    if args.feedback == 'build_failure':
        handle_build_failure(args)
    elif args.feedback == 'new_repo':
        handle_new_repo(args)
    elif args.feedback == 'rescan':
        handle_rescan(args)
    else:
        print(f"  Unknown feedback type: {args.feedback}")


if __name__ == '__main__':
    main()
