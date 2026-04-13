#!/usr/bin/env python3
"""
Generate UE5 Blueprint JSON for DTE MetaHuman components.

Generates importable Blueprint component definitions that can be
pasted into UE5's Blueprint editor or used with the Blueprint Utilities plugin.

Usage:
    python generate_bp_json.py <component_type> [--output <file>]

Component types:
    expression_bridge   BP_ExpressionBridge component variables and defaults
    cognitive_cycle     BP_CognitiveComponent with ESN parameters
    full_character      Complete BP_DTECharacter with all components
    au_map              Action Unit variable map with default values

Examples:
    python generate_bp_json.py expression_bridge --output bp_expression.json
    python generate_bp_json.py au_map
"""

import json
import sys
import argparse


# FACS AU definitions used by the DTE expression system
AU_DEFINITIONS = {
    "AU1":  {"name": "Inner Brow Raise",     "default": 0.0, "ctrl": ["CTRL_expressions_browRaiseInnerL", "CTRL_expressions_browRaiseInnerR"]},
    "AU2":  {"name": "Outer Brow Raise",     "default": 0.0, "ctrl": ["CTRL_expressions_browRaiseOuterL", "CTRL_expressions_browRaiseOuterR"]},
    "AU4":  {"name": "Brow Lowerer",         "default": 0.0, "ctrl": ["CTRL_expressions_browDownL", "CTRL_expressions_browDownR", "CTRL_expressions_browLateralL", "CTRL_expressions_browLateralR"]},
    "AU5":  {"name": "Upper Lid Raiser",     "default": 0.0, "ctrl": ["CTRL_expressions_eyeUpperLidUpL", "CTRL_expressions_eyeUpperLidUpR", "CTRL_expressions_eyeWidenL", "CTRL_expressions_eyeWidenR"]},
    "AU6":  {"name": "Cheek Raiser",         "default": 0.0, "ctrl": ["CTRL_expressions_eyeCheekRaiseL", "CTRL_expressions_eyeCheekRaiseR"]},
    "AU7":  {"name": "Lid Tightener",        "default": 0.0, "ctrl": ["CTRL_expressions_eyeSquintInnerL", "CTRL_expressions_eyeSquintInnerR"]},
    "AU9":  {"name": "Nose Wrinkler",        "default": 0.0, "ctrl": ["CTRL_expressions_noseWrinkleL", "CTRL_expressions_noseWrinkleR"]},
    "AU10": {"name": "Upper Lip Raiser",     "default": 0.0, "ctrl": ["CTRL_expressions_mouthUpperLipRaiseL", "CTRL_expressions_mouthUpperLipRaiseR"]},
    "AU12": {"name": "Lip Corner Puller",    "default": 0.0, "ctrl": ["CTRL_expressions_mouthCornerPullL", "CTRL_expressions_mouthCornerPullR"]},
    "AU14": {"name": "Dimpler",              "default": 0.0, "ctrl": ["CTRL_expressions_mouthDimpleL", "CTRL_expressions_mouthDimpleR"]},
    "AU15": {"name": "Lip Corner Depressor", "default": 0.0, "ctrl": ["CTRL_expressions_mouthCornerDepressL", "CTRL_expressions_mouthCornerDepressR"]},
    "AU17": {"name": "Chin Raiser",          "default": 0.0, "ctrl": ["CTRL_expressions_jawChinRaiseDL", "CTRL_expressions_jawChinRaiseDR"]},
    "AU18": {"name": "Lip Pucker",           "default": 0.0, "ctrl": ["CTRL_expressions_mouthLipsPurseUL", "CTRL_expressions_mouthLipsPurseDL"]},
    "AU20": {"name": "Lip Stretcher",        "default": 0.0, "ctrl": ["CTRL_expressions_mouthStretchL", "CTRL_expressions_mouthStretchR"]},
    "AU22": {"name": "Lip Funneler",         "default": 0.0, "ctrl": ["CTRL_expressions_mouthFunnelDL", "CTRL_expressions_mouthFunnelUL"]},
    "AU23": {"name": "Lip Tightener",        "default": 0.0, "ctrl": ["CTRL_expressions_mouthLipsTightenUL", "CTRL_expressions_mouthLipsTightenUR"]},
    "AU24": {"name": "Lip Pressor",          "default": 0.0, "ctrl": ["CTRL_expressions_mouthPressDL", "CTRL_expressions_mouthPressDR"]},
    "AU25": {"name": "Lips Part",            "default": 0.0, "ctrl": ["CTRL_expressions_mouthLipsPartL", "CTRL_expressions_mouthLipsPartR"]},
    "AU26": {"name": "Jaw Drop",             "default": 0.0, "ctrl": ["CTRL_expressions_jawOpen"]},
    "AU43": {"name": "Eyes Closed",          "default": 0.0, "ctrl": ["CTRL_expressions_eyeBlinkL", "CTRL_expressions_eyeBlinkR"]},
}

# Emotion presets (FACS AU combinations)
EMOTION_PRESETS = {
    "happiness_duchenne": {"AU6": 0.6, "AU7": 0.4, "AU12": 0.8, "AU25": 0.3},
    "happiness_gentle":   {"AU6": 0.3, "AU12": 0.5, "AU25": 0.1},
    "surprise":           {"AU1": 0.6, "AU2": 0.6, "AU5": 0.7, "AU25": 0.4, "AU26": 0.5},
    "fear":               {"AU1": 0.7, "AU2": 0.7, "AU4": 0.4, "AU5": 0.8, "AU7": 0.5, "AU20": 0.4, "AU26": 0.6},
    "anger":              {"AU4": 0.7, "AU5": 0.4, "AU7": 0.6, "AU23": 0.5, "AU24": 0.4},
    "sadness":            {"AU1": 0.5, "AU4": 0.3, "AU15": 0.5, "AU17": 0.3},
    "disgust":            {"AU9": 0.6, "AU10": 0.5, "AU15": 0.3, "AU17": 0.3},
    "contempt":           {"AU12": 0.3, "AU14": 0.4},  # Asymmetric (right side only)
}


def generate_expression_bridge():
    return {
        "component_name": "BP_ExpressionBridge",
        "component_class": "ActorComponent",
        "category": "DTE|Expression",
        "variables": {
            "ActionUnitValues": {au: info["default"] for au, info in AU_DEFINITIONS.items()},
            "LorenzState": {"X": 1.0, "Y": 1.0, "Z": 1.0},
            "ChaosIntensity": 0.15,
            "ChaosTimeStep": 0.01,
            "ConfidencePosture": 0.5,
            "Charisma": 0.5,
            "EyeSparkle": 0.5,
        },
        "au_to_ctrl_mapping": {au: info["ctrl"] for au, info in AU_DEFINITIONS.items()},
        "emotion_presets": EMOTION_PRESETS,
    }


def generate_cognitive_cycle():
    return {
        "component_name": "BP_CognitiveComponent",
        "component_class": "ActorComponent",
        "category": "DTE|Cognition",
        "variables": {
            "ReservoirSize": 512,
            "SpectralRadius": 0.9,
            "LeakRate": 0.3,
            "Sparsity": 0.1,
            "InputScaling": 0.5,
            "CognitiveTickRate": 0.033,
            "EmotionalValence": 0.0,
            "Arousal": 0.0,
            "CognitiveLoad": 0.0,
            "OntogeneticStage": "Juvenile",
            "4E_Embodied": 0.0,
            "4E_Embedded": 0.0,
            "4E_Enacted": 0.0,
            "4E_Extended": 0.0,
        },
        "echobeats_steps": [
            "Sense", "Attend", "Remember", "Predict",
            "Compare", "Learn", "Decide", "Act", "Reflect"
        ],
        "cognitive_modes": [
            "Focus", "Explore", "Social", "Rest", "Flow", "Alarm"
        ],
    }


def generate_full_character():
    return {
        "actor_name": "BP_DTECharacter",
        "actor_class": "Character",
        "components": [
            generate_expression_bridge(),
            generate_cognitive_cycle(),
            {
                "component_name": "EndocrineSystem",
                "component_class": "ActorComponent",
                "category": "DTE|Endocrine",
                "glands": 10,
                "hormone_channels": 16,
            },
            {
                "component_name": "MetaHumanFace",
                "component_class": "SkeletalMeshComponent",
                "category": "DTE|Mesh",
                "dna_asset": "MetaHuman_DNA_Asset",
            },
        ],
    }


def generate_au_map():
    return AU_DEFINITIONS


def main():
    parser = argparse.ArgumentParser(description="Generate UE5 Blueprint JSON for DTE MetaHuman")
    parser.add_argument("component_type", choices=["expression_bridge", "cognitive_cycle", "full_character", "au_map"])
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    args = parser.parse_args()

    generators = {
        "expression_bridge": generate_expression_bridge,
        "cognitive_cycle": generate_cognitive_cycle,
        "full_character": generate_full_character,
        "au_map": generate_au_map,
    }

    result = generators[args.component_type]()
    output = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Written to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
