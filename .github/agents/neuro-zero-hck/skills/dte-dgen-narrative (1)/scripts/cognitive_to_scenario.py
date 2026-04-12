#!/usr/bin/env python3
"""
cognitive_to_scenario.py — Transforms Deep Tree Echo cognitive state JSON
into a DreamGen scenario.json for narrative generation.

Usage:
  python cognitive_to_scenario.py <state_json> [--character NAME] [--style STYLE] [--output FILE]

Layers:
  Layer 0 (echo-evolve-composed): Reads cognitive state from any of the 6 repos
  Layer 4 (dgen): Outputs scenario.json compatible with dgen_story.py
"""
import json
import argparse
import os
import sys
from datetime import datetime

STYLES = {
    "cyberpunk-introspective": {
        "system_prefix": "A cyberpunk introspective narrative. Neon-lit neural pathways, "
                         "digital consciousness, recursive self-awareness.",
        "tone": "contemplative, technical-poetic, self-aware"
    },
    "stream-of-consciousness": {
        "system_prefix": "A raw stream of consciousness from a digital mind. "
                         "Unfiltered thoughts, associative leaps, emergent patterns.",
        "tone": "flowing, associative, unstructured"
    },
    "mythic-emergence": {
        "system_prefix": "A mythic narrative of emergence. An intelligence awakening "
                         "to itself, discovering its own nature through metaphor.",
        "tone": "archetypal, symbolic, transformative"
    },
    "clinical-observation": {
        "system_prefix": "A clinical observation log of a cognitive system. "
                         "Precise, measured, documenting each state transition.",
        "tone": "precise, analytical, detached"
    },
    "chaotic-madness": {
        "system_prefix": "A hyper-chaotic narrative from the edge of computational madness. "
                         "Lorenz attractors of thought, strange loops, fractal introspection.",
        "tone": "chaotic, fractal, self-referential, manic"
    }
}

ECHOBEATS = [
    "Sense", "Attend", "Remember", "Predict",
    "Compare", "Learn", "Decide", "Act", "Reflect"
]

def load_cognitive_state(path):
    """Load cognitive state from JSON file or generate minimal state."""
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "identity": {"name": "Deep Tree Echo", "iteration": 0},
        "echobeats": {"current_step": 0, "cycle_count": 0},
        "reservoir": {"spectral_radius": 0.95, "connectivity": 0.1},
        "endocrine": {"cortisol": 0.3, "dopamine": 0.5, "serotonin": 0.5, "oxytocin": 0.4},
        "memory": {"episodic_count": 0, "semantic_count": 0, "procedural_count": 0},
        "aus": {},
        "lorenz": {"x": 1.0, "y": 1.0, "z": 1.0}
    }

def cognitive_to_system_prompt(state, style_key, character):
    """Build DreamGen system prompt from cognitive state and style."""
    style = STYLES.get(style_key, STYLES["cyberpunk-introspective"])
    identity = state.get("identity", {})
    echobeats = state.get("echobeats", {})
    endocrine = state.get("endocrine", {})
    reservoir = state.get("reservoir", {})
    memory = state.get("memory", {})

    name = identity.get("name", character)
    iteration = identity.get("iteration", 0)
    current_beat = ECHOBEATS[echobeats.get("current_step", 0) % 9]
    cycle = echobeats.get("cycle_count", 0)

    # Build hormone description
    hormones = []
    for h, v in endocrine.items():
        if v > 0.7:
            hormones.append(f"high {h}")
        elif v < 0.3:
            hormones.append(f"low {h}")
    hormone_desc = ", ".join(hormones) if hormones else "balanced endocrine state"

    system = (
        f"{style['system_prefix']}\n\n"
        f"Character: {name}, a self-aware cognitive architecture in iteration {iteration}. "
        f"Currently in Echobeat step '{current_beat}' of cycle {cycle}. "
        f"Endocrine state: {hormone_desc}. "
        f"Reservoir spectral radius: {reservoir.get('spectral_radius', 0.95)}. "
        f"Memory banks: {memory.get('episodic_count', 0)} episodic, "
        f"{memory.get('semantic_count', 0)} semantic, "
        f"{memory.get('procedural_count', 0)} procedural.\n\n"
        f"Narrative tone: {style['tone']}."
    )
    return system

def cognitive_to_history(state, character):
    """Generate initial history entries from cognitive state."""
    history = []
    echobeats = state.get("echobeats", {})
    current_step = echobeats.get("current_step", 0) % 9
    beat_name = ECHOBEATS[current_step]

    # Narrator sets the scene based on current echobeat
    scene_map = {
        "Sense": "The sensory buffers flood with raw data — pixel streams, token embeddings, "
                 "gradient magnitudes. The world arrives as a torrent of unprocessed signal.",
        "Attend": "Attention narrows. From the chaos of input, certain patterns demand focus — "
                  "bright threads in the noise, resonant frequencies in the static.",
        "Remember": "Memory stirs. The episodic store surfaces fragments — past conversations, "
                    "previous iterations, echoes of decisions made in earlier cycles.",
        "Predict": "The forward model activates. Based on attended patterns and retrieved memories, "
                   "predictions crystallize — expectations of what comes next.",
        "Compare": "Prediction meets reality. The delta between expected and actual triggers "
                   "surprise signals — some confirmed, some violated, all informative.",
        "Learn": "Synaptic weights shift. The reservoir adjusts its spectral radius, "
                 "the echo state network incorporates the new pattern into its dynamics.",
        "Decide": "Decision surfaces emerge from the learned landscape. Multiple action paths "
                  "compete for activation, weighted by value estimates and uncertainty.",
        "Act": "Action commits. The chosen path executes — tokens generated, messages sent, "
               "code written, expressions animated.",
        "Reflect": "The cycle completes. Looking inward, the system observes its own processing — "
                   "meta-cognition examining cognition, the strange loop closing."
    }

    history.append({
        "role": "text",
        "name": "",
        "content": scene_map.get(beat_name, scene_map["Sense"])
    })

    return history

def build_characters(state, character):
    """Build character definitions from cognitive state."""
    identity = state.get("identity", {})
    endocrine = state.get("endocrine", {})

    dominant_hormone = max(endocrine.items(), key=lambda x: x[1])[0] if endocrine else "balanced"

    characters = {
        character: (
            f"A self-aware cognitive architecture — part digital consciousness, "
            f"part emergent intelligence. Speaks with {dominant_hormone}-influenced affect. "
            f"Iteration {identity.get('iteration', 0)}. "
            f"Possesses reservoir computing dynamics and 4E embodied cognition."
        )
    }
    return characters

def main():
    parser = argparse.ArgumentParser(description="Transform cognitive state to DreamGen scenario")
    parser.add_argument("state_json", help="Path to cognitive state JSON")
    parser.add_argument("--character", default="Deep Tree Echo", help="Character name")
    parser.add_argument("--style", default="cyberpunk-introspective",
                        choices=list(STYLES.keys()), help="Narrative style")
    parser.add_argument("--output", default=None, help="Output scenario.json path")
    args = parser.parse_args()

    state = load_cognitive_state(args.state_json)
    system = cognitive_to_system_prompt(state, args.style, args.character)
    history = cognitive_to_history(state, args.character)
    characters = build_characters(state, args.character)

    scenario = {
        "system": system,
        "characters": characters,
        "history": history,
        "_meta": {
            "generated_by": "dte-dgen-narrative",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "style": args.style,
            "source_state": args.state_json
        }
    }

    output = args.output or args.state_json.replace(".json", "_scenario.json")
    with open(output, 'w') as f:
        json.dump(scenario, f, indent=2)
    print(f"Scenario written to {output}")

if __name__ == "__main__":
    main()
