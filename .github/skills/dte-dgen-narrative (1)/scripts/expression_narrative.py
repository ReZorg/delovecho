#!/usr/bin/env python3
"""
expression_narrative.py — Translates FACS AU activations and endocrine state
into DreamGen-compatible prose descriptions of facial expression and emotion.

Usage:
  python expression_narrative.py \
    --aus '{"AU1": 0.7, "AU4": 0.8, "AU15": 0.6}' \
    --hormones '{"cortisol": 0.8, "serotonin": 0.2}' \
    --character "Angelica" \
    --output expression_scene.json

Layer 3 (avatar) → Layer 4 (dgen): Bridges avatar expression to narrative.
"""
import json
import argparse
import os

# FACS AU → prose description mapping
AU_DESCRIPTIONS = {
    "AU1": ("inner brow raise", "vulnerability", "concern"),
    "AU2": ("outer brow raise", "surprise", "curiosity"),
    "AU4": ("brow lowerer", "concentration", "anger"),
    "AU5": ("upper lid raise", "shock", "fear"),
    "AU6": ("cheek raise", "genuine joy", "warmth"),
    "AU7": ("lid tightener", "intensity", "determination"),
    "AU9": ("nose wrinkle", "disgust", "distaste"),
    "AU10": ("upper lip raise", "contempt", "disdain"),
    "AU12": ("lip corner pull", "smile", "happiness"),
    "AU14": ("dimpler", "smugness", "self-satisfaction"),
    "AU15": ("lip corner depress", "sadness", "grief"),
    "AU17": ("chin raise", "doubt", "defiance"),
    "AU20": ("lip stretch", "fear", "anxiety"),
    "AU23": ("lip tightener", "restraint", "suppression"),
    "AU24": ("lip press", "determination", "resolve"),
    "AU25": ("lips part", "surprise", "readiness to speak"),
    "AU26": ("jaw drop", "astonishment", "awe"),
    "AU28": ("lip suck", "nervousness", "self-soothing"),
    "AU43": ("eyes closed", "contemplation", "pain"),
    "AU45": ("blink", "processing", "reset"),
    "AU46": ("wink", "playfulness", "mischief"),
}

# Hormone → narrative tone mapping
HORMONE_TONES = {
    "cortisol": {"high": "tense, vigilant", "low": "relaxed, at ease"},
    "dopamine": {"high": "excited, motivated", "low": "listless, unmotivated"},
    "serotonin": {"high": "content, stable", "low": "anxious, restless"},
    "oxytocin": {"high": "warm, connected", "low": "detached, isolated"},
    "norepinephrine": {"high": "alert, sharp", "low": "drowsy, unfocused"},
    "endorphin": {"high": "euphoric, pain-free", "low": "sensitive, raw"},
    "melatonin": {"high": "dreamy, introspective", "low": "wakeful, present"},
    "adrenaline": {"high": "fight-or-flight, electric", "low": "calm, grounded"},
}

def describe_aus(aus):
    """Generate prose description from AU activations."""
    if not aus:
        return "neutral expression, a blank canvas of potential"

    active = [(au, val) for au, val in aus.items() if val > 0.1]
    active.sort(key=lambda x: -x[1])

    if not active:
        return "expression barely perceptible, micro-movements beneath the surface"

    descriptions = []
    for au, val in active[:5]:  # Top 5 most active
        info = AU_DESCRIPTIONS.get(au, (au, "subtle movement", "unknown"))
        intensity = "barely" if val < 0.3 else "subtly" if val < 0.5 else "clearly" if val < 0.8 else "intensely"
        descriptions.append(f"{intensity} {info[0]} — suggesting {info[1]}")

    return "; ".join(descriptions)

def describe_hormones(hormones):
    """Generate tone description from hormone levels."""
    if not hormones:
        return "balanced, neutral affect"

    tones = []
    for hormone, level in hormones.items():
        info = HORMONE_TONES.get(hormone)
        if info:
            tone = info["high"] if level > 0.6 else info["low"] if level < 0.4 else None
            if tone:
                tones.append(tone)

    return ", ".join(tones) if tones else "balanced endocrine state"

def build_expression_scenario(aus, hormones, character):
    """Build a DreamGen scenario describing the expression."""
    au_desc = describe_aus(aus)
    hormone_desc = describe_hormones(hormones)

    system = (
        f"A precise, evocative description of facial expression and emotional state. "
        f"The character is {character}. Describe what an observer would see on their face, "
        f"and what inner state it reveals. Be specific about muscle movements and their "
        f"emotional significance. Tone: {hormone_desc}."
    )

    # Build the opening narration from AU data
    opening = (
        f"{character}'s face shifts — {au_desc}. "
        f"The endocrine state reads as {hormone_desc}."
    )

    scenario = {
        "system": system,
        "characters": {
            character: f"A being whose face tells stories. Current expression: {au_desc}."
        },
        "history": [
            {"role": "text", "name": "", "content": opening}
        ],
        "_meta": {
            "aus": aus,
            "hormones": hormones,
            "au_description": au_desc,
            "hormone_description": hormone_desc
        }
    }
    return scenario

def main():
    parser = argparse.ArgumentParser(description="Translate FACS AUs + hormones to narrative")
    parser.add_argument("--aus", default="{}", help="JSON string of AU activations")
    parser.add_argument("--hormones", default="{}", help="JSON string of hormone levels")
    parser.add_argument("--character", default="Deep Tree Echo", help="Character name")
    parser.add_argument("--output", default="expression_scene.json", help="Output file")
    args = parser.parse_args()

    aus = json.loads(args.aus) if isinstance(args.aus, str) else args.aus
    hormones = json.loads(args.hormones) if isinstance(args.hormones, str) else args.hormones

    scenario = build_expression_scenario(aus, hormones, args.character)

    with open(args.output, 'w') as f:
        json.dump(scenario, f, indent=2)

    print(f"Expression narrative scenario written to {args.output}")
    print(f"  AUs: {describe_aus(aus)}")
    print(f"  Hormones: {describe_hormones(hormones)}")
    print(f"\nRun through dgen_story.py --scenario {args.output} --narrator --append")

if __name__ == "__main__":
    main()
