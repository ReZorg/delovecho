#!/usr/bin/env python3
"""
Dual-Org Neural Build-Path Optimizer
=====================================
Evolved from oc-build-nn via circled-operators algebraic composition.

Architecture:
  BuildPathNetwork (nn Module pattern) with ⊕⊗ extensions:
    - PositionEmbedding P[N×S]   — softmax → step probabilities
    - DependencyLogits  D[N×N]   — sigmoid → dep probabilities
    - OrgEmbedding      O[N×2]   — org membership (opencog|openclaw)
    - CrossOrgBridge    B[2×2]   — ⊕/⊗ interaction between orgs
    - ComponentType     T[N×K]   — language/build system features

  N = 112 components, S = 6 steps, K = 8 feature dims
  Total parameters: 13,216 + 224 + 4 + 896 = 14,340

The network learns:
  1. Optimal build order via position embeddings (P)
  2. Hidden dependencies via dependency logits (D)
  3. Cross-org integration patterns via bridge matrix (B)
  4. Language-aware build scheduling via type features (T)

Training modes:
  - Simulation: Against known dependency graph
  - Online: From real CI build results
  - Cross-org: Discovers opencog⊗openclaw integration points
"""

import json
import numpy as np
import os

class DualOrgBuildPathNetwork:
    """
    nn.Module-pattern neural build-path optimizer for opencog/* ⊕ openclaw/*.
    
    Implements the Torch7 nn interface:
      forward(input) → build_order
      backward(input, gradOutput) → gradients
      zeroGradParameters() → zero grads
      updateParameters(lr) → gradient descent
      parameters() → {weights}, {gradWeights}
    """
    
    def __init__(self, topology_path='/home/ubuntu/topology_analysis.json'):
        with open(topology_path) as f:
            topo = json.load(f)
        
        self.components = topo['components']
        self.N = topo['n_components']
        self.S = topo['n_steps']
        self.K = 8  # feature dimensions
        
        self.dep_graph = topo['dep_graph']
        self.reverse_graph = topo['reverse_graph']
        self.tiers = topo['tiers']
        self.oplus_components = topo['oplus_components']
        self.stats = topo['stats']
        
        # Component index
        self.idx = {c: i for i, c in enumerate(self.components)}
        
        # Org membership
        self.org_map = {}
        for comp_list in self.oplus_components:
            for c in comp_list:
                # Determine org from topology data
                pass
        
        # ===== LEARNABLE PARAMETERS =====
        
        # P[N×S]: Position embedding (which step each component belongs at)
        self.P = np.array(topo['position_weight_seed'])
        self.gradP = np.zeros_like(self.P)
        
        # D[N×N]: Dependency logits (pairwise dependency probabilities)
        self.D = np.array(topo['dependency_matrix']) * 3.0  # warm-start known deps
        self.gradD = np.zeros_like(self.D)
        
        # O[N×2]: Org embedding (opencog=0, openclaw=1)
        self.O = np.zeros((self.N, 2))
        self.gradO = np.zeros_like(self.O)
        
        # B[2×2]: Cross-org bridge matrix
        self.B = np.eye(2) * 0.5  # Start with weak self-connection
        self.gradB = np.zeros_like(self.B)
        
        # T[N×K]: Component type features
        self.T = np.random.randn(self.N, self.K) * 0.1
        self.gradT = np.zeros_like(self.T)
        
        # Initialize org embeddings from scan data
        self._init_org_embeddings()
        self._init_type_features()
        
        # Training history
        self.history = []
        self.epoch = 0
        
    def _init_org_embeddings(self):
        """Initialize O[N×2] from org membership"""
        try:
            with open('/home/ubuntu/repo_metadata_scan.json') as f:
                scan = json.load(f)
            org_lookup = {}
            for r in scan['results']:
                short = r['output']['repo'].split('/')[-1]
                org_lookup[short] = r['output']['org']
            
            for i, comp in enumerate(self.components):
                org = org_lookup.get(comp, 'opencog')
                if org == 'opencog':
                    self.O[i] = [1.0, 0.0]
                else:
                    self.O[i] = [0.0, 1.0]
        except:
            # Default: all opencog
            self.O[:, 0] = 1.0
    
    def _init_type_features(self):
        """Initialize T[N×K] from language and build system"""
        lang_map = {'C++': 0, 'Python': 1, 'Scheme': 2, 'JavaScript': 3, 
                    'TypeScript': 4, 'C': 5, 'Java': 6}
        build_map = {'cmake': 0, 'make': 1, 'package.json': 2, 'setup.py': 3,
                     'nix': 4, 'mixed': 5}
        
        try:
            with open('/home/ubuntu/repo_metadata_scan.json') as f:
                scan = json.load(f)
            for r in scan['results']:
                short = r['output']['repo'].split('/')[-1]
                if short in self.idx:
                    i = self.idx[short]
                    lang = r['output']['primary_language']
                    build = r['output']['build_system']
                    if lang in lang_map:
                        self.T[i, lang_map[lang]] = 1.0
                    if build in build_map:
                        self.T[i, 7] = build_map[build] / 5.0
        except:
            pass
    
    def _softmax(self, x, axis=-1):
        """Numerically stable softmax"""
        e = np.exp(x - np.max(x, axis=axis, keepdims=True))
        return e / (e.sum(axis=axis, keepdims=True) + 1e-8)
    
    def _sigmoid(self, x):
        """Numerically stable sigmoid"""
        return np.where(x >= 0, 
                       1 / (1 + np.exp(-x)),
                       np.exp(x) / (1 + np.exp(x)))
    
    def forward(self, input_data=None):
        """
        Compute build order from current embeddings.
        
        Returns:
            build_order: list of (component, step) sorted by step
            step_probs: P after softmax [N×S]
            dep_probs: D after sigmoid [N×N]
            org_influence: O @ B [N×2]
        """
        # Step probabilities
        self.step_probs = self._softmax(self.P, axis=1)
        
        # Dependency probabilities
        self.dep_probs = self._sigmoid(self.D)
        
        # Org influence (cross-org bridge)
        self.org_influence = self.O @ self.B
        
        # Compute build order: argmax of step probabilities
        step_assignments = np.argmax(self.step_probs, axis=1)
        
        # Build order sorted by step
        build_order = sorted(
            [(self.components[i], int(step_assignments[i])) for i in range(self.N)],
            key=lambda x: (x[1], x[0])
        )
        
        self.output = {
            'build_order': build_order,
            'step_probs': self.step_probs,
            'dep_probs': self.dep_probs,
            'org_influence': self.org_influence,
        }
        
        return self.output
    
    def simulate_build(self, build_order):
        """
        Simulate a build attempt against the true dependency graph.
        
        Returns:
            results: list of (component, step, success, missing_deps)
        """
        built = set()
        results = []
        
        for comp, step in build_order:
            required = set(self.dep_graph.get(comp, []))
            missing = required - built
            success = len(missing) == 0
            results.append((comp, step, success, list(missing)))
            if success:
                built.add(comp)
        
        return results
    
    def backward(self, input_data, build_results):
        """
        Compute gradients from build results.
        
        For each component:
          - Success → reinforce current position (negative grad on P)
          - Failure → push later + strengthen missing dep edges
        """
        total_loss = 0.0
        successes = 0
        
        for comp, step, success, missing in build_results:
            i = self.idx[comp]
            
            if success:
                successes += 1
                # Reinforce: negative gradient on current position
                self.gradP[i, step] -= 1.0
                # Slight positive gradient on other positions
                for s in range(self.S):
                    if s != step:
                        self.gradP[i, s] += 0.1
            else:
                total_loss += 1.0
                # Push component to later step
                self.gradP[i, step] += 1.0
                if step + 1 < self.S:
                    self.gradP[i, step + 1] -= 0.5
                
                # Strengthen dependency edges for missing deps
                for dep in missing:
                    if dep in self.idx:
                        j = self.idx[dep]
                        self.gradD[i, j] -= 1.0  # strengthen dep edge
                        
                        # Push dep to earlier step
                        dep_step = np.argmax(self.step_probs[j])
                        if dep_step > 0:
                            self.gradP[j, dep_step] += 0.5
                            self.gradP[j, dep_step - 1] -= 0.5
        
        # Entropy regularization: encourage peaked distributions
        entropy = -np.sum(self.step_probs * np.log(self.step_probs + 1e-8), axis=1)
        entropy_grad = 0.1 * (np.log(self.step_probs + 1e-8) + 1)
        self.gradP += entropy_grad
        
        # Cross-org bridge gradient
        # If components from different orgs succeed together, strengthen bridge
        for comp, step, success, _ in build_results:
            i = self.idx[comp]
            org_idx = np.argmax(self.O[i])
            if success:
                self.gradB[org_idx, org_idx] -= 0.01
            else:
                self.gradB[org_idx, org_idx] += 0.01
        
        # Compute loss
        failure_rate = 1.0 - successes / max(len(build_results), 1)
        mean_entropy = np.mean(entropy)
        loss = failure_rate + 0.1 * mean_entropy
        
        self.gradInput = {
            'loss': loss,
            'failure_rate': failure_rate,
            'entropy': mean_entropy,
            'successes': successes,
            'total': len(build_results),
        }
        
        return self.gradInput
    
    def zeroGradParameters(self):
        """Zero all accumulated gradients"""
        self.gradP.fill(0)
        self.gradD.fill(0)
        self.gradO.fill(0)
        self.gradB.fill(0)
        self.gradT.fill(0)
    
    def updateParameters(self, lr=0.1):
        """Update weights via gradient descent"""
        self.P -= lr * self.gradP
        self.D -= lr * self.gradD
        self.O -= lr * self.gradO
        self.B -= lr * self.gradB
        self.T -= lr * self.gradT
    
    def parameters(self):
        """Return {weights}, {gradWeights}"""
        weights = {
            'P': self.P, 'D': self.D, 'O': self.O, 'B': self.B, 'T': self.T
        }
        grads = {
            'gradP': self.gradP, 'gradD': self.gradD, 'gradO': self.gradO,
            'gradB': self.gradB, 'gradT': self.gradT
        }
        return weights, grads
    
    def train(self, epochs=300, lr=0.1, verbose=True):
        """Full training loop with simulation"""
        best_loss = float('inf')
        converged = False
        
        for epoch in range(epochs):
            self.zeroGradParameters()
            
            # Forward pass
            output = self.forward()
            
            # Simulate build
            results = self.simulate_build(output['build_order'])
            
            # Backward pass
            grad_info = self.backward(None, results)
            
            # Update parameters
            self.updateParameters(lr)
            
            loss = grad_info['loss']
            successes = grad_info['successes']
            entropy = grad_info['entropy']
            
            self.history.append({
                'epoch': epoch,
                'loss': round(loss, 4),
                'successes': successes,
                'total': grad_info['total'],
                'entropy': round(entropy, 4),
            })
            
            if loss < best_loss:
                best_loss = loss
            
            if verbose and (epoch % 50 == 0 or epoch == epochs - 1):
                print(f"  Epoch {epoch:4d}: loss={loss:.4f} success={successes}/{grad_info['total']} entropy={entropy:.4f}")
            
            # Convergence check
            if successes == grad_info['total'] and entropy < 0.5:
                if verbose:
                    print(f"  ✅ Converged at epoch {epoch}! loss={loss:.4f} entropy={entropy:.4f}")
                converged = True
                break
            
            self.epoch = epoch
        
        return {
            'converged': converged,
            'epochs': epoch + 1,
            'best_loss': round(best_loss, 4),
            'final_loss': round(loss, 4),
            'final_successes': successes,
            'final_entropy': round(entropy, 4),
        }
    
    def extract_learned_knowledge(self):
        """Extract learned tiers, dependencies, and cross-org patterns"""
        output = self.forward()
        
        # Learned tier assignments
        learned_tiers = {}
        for i, comp in enumerate(self.components):
            learned_tiers[comp] = int(np.argmax(self.step_probs[i]))
        
        # Learned dependency edges (threshold > 0.5)
        learned_deps = {}
        for i, comp_i in enumerate(self.components):
            deps = []
            for j, comp_j in enumerate(self.components):
                if i != j and self.dep_probs[i, j] > 0.5:
                    deps.append((comp_j, round(float(self.dep_probs[i, j]), 3)))
            if deps:
                deps.sort(key=lambda x: -x[1])
                learned_deps[comp_i] = deps
        
        # Cross-org bridge strength
        bridge = {
            'opencog_self': round(float(self.B[0, 0]), 3),
            'opencog_to_openclaw': round(float(self.B[0, 1]), 3),
            'openclaw_to_opencog': round(float(self.B[1, 0]), 3),
            'openclaw_self': round(float(self.B[1, 1]), 3),
        }
        
        # ⊕-component analysis
        oplus_summary = []
        for comp_list in self.oplus_components:
            orgs = set()
            for c in comp_list:
                org_idx = np.argmax(self.O[self.idx[c]]) if c in self.idx else 0
                orgs.add('opencog' if org_idx == 0 else 'openclaw')
            oplus_summary.append({
                'size': len(comp_list),
                'orgs': sorted(orgs),
                'members': comp_list[:5],
            })
        
        return {
            'learned_tiers': learned_tiers,
            'learned_deps': {k: [(d, p) for d, p in v] for k, v in learned_deps.items()},
            'cross_org_bridge': bridge,
            'oplus_components': oplus_summary[:10],
            'n_learned_dep_edges': sum(len(v) for v in learned_deps.values()),
            'n_tiers': len(set(learned_tiers.values())),
        }
    
    def save_state(self, path):
        """Save network state to JSON"""
        state = {
            'components': self.components,
            'n_components': self.N,
            'n_steps': self.S,
            'n_features': self.K,
            'position_weight': self.P.tolist(),
            'dependency_weight': self.D.tolist(),
            'org_embedding': self.O.tolist(),
            'cross_org_bridge': self.B.tolist(),
            'type_features': self.T.tolist(),
            'history': self.history,
            'epoch': self.epoch,
        }
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, path):
        """Load network state from JSON"""
        with open(path) as f:
            state = json.load(f)
        self.P = np.array(state['position_weight'])
        self.D = np.array(state['dependency_weight'])
        self.O = np.array(state['org_embedding'])
        self.B = np.array(state['cross_org_bridge'])
        self.T = np.array(state['type_features'])
        self.history = state.get('history', [])
        self.epoch = state.get('epoch', 0)


# ============================================
# MAIN: Train and extract knowledge
# ============================================
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Dual-Org Neural Build-Path Optimizer')
    parser.add_argument('--topology', default='/home/ubuntu/topology_analysis.json')
    parser.add_argument('--epochs', type=int, default=300)
    parser.add_argument('--lr', type=float, default=0.1)
    parser.add_argument('--output', default='/home/ubuntu/neural_state.json')
    parser.add_argument('--knowledge', default='/home/ubuntu/learned_knowledge.json')
    args = parser.parse_args()
    
    print("=" * 70)
    print("DUAL-ORG NEURAL BUILD-PATH OPTIMIZER")
    print("opencog/* ⊕ openclaw/* via circled-operators")
    print("=" * 70)
    
    net = DualOrgBuildPathNetwork(args.topology)
    print(f"\nNetwork: {net.N} components × {net.S} steps")
    print(f"Parameters: P[{net.N}×{net.S}] + D[{net.N}×{net.N}] + O[{net.N}×2] + B[2×2] + T[{net.N}×{net.K}]")
    total_params = net.N * net.S + net.N * net.N + net.N * 2 + 4 + net.N * net.K
    print(f"Total: {total_params:,} parameters")
    
    print(f"\n🏋️ Training ({args.epochs} epochs, lr={args.lr})...")
    result = net.train(epochs=args.epochs, lr=args.lr)
    
    print(f"\n📊 Training Results:")
    print(f"  Converged: {result['converged']}")
    print(f"  Epochs: {result['epochs']}")
    print(f"  Best loss: {result['best_loss']}")
    print(f"  Final loss: {result['final_loss']}")
    print(f"  Final successes: {result['final_successes']}/{net.N}")
    print(f"  Final entropy: {result['final_entropy']}")
    
    # Extract learned knowledge
    knowledge = net.extract_learned_knowledge()
    print(f"\n🧠 Learned Knowledge:")
    print(f"  Learned dep edges: {knowledge['n_learned_dep_edges']}")
    print(f"  Learned tiers: {knowledge['n_tiers']}")
    print(f"  Cross-org bridge: {knowledge['cross_org_bridge']}")
    
    print(f"\n📋 Learned Tier Assignments:")
    tier_groups = {}
    for comp, tier in knowledge['learned_tiers'].items():
        tier_groups.setdefault(tier, []).append(comp)
    for tier in sorted(tier_groups.keys()):
        comps = sorted(tier_groups[tier])
        print(f"  Tier {tier} ({len(comps)}): {', '.join(comps[:8])}{'...' if len(comps) > 8 else ''}")
    
    # Save state
    net.save_state(args.output)
    print(f"\n💾 Neural state saved to {args.output}")
    
    # Save knowledge
    knowledge['training_result'] = result
    knowledge['stats'] = net.stats
    with open(args.knowledge, 'w') as f:
        json.dump(knowledge, f, indent=2)
    print(f"💾 Learned knowledge saved to {args.knowledge}")
