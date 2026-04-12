#!/usr/bin/env python3
"""Initialize a new Live2D character from the {{char}}-model template.

Usage:
    python init_character.py <char_id> [--display-name "Name"] [--archetype explorer]

Creates:
    characters/<char_id>/manifest.yaml  (from template, with id filled in)
    models/<char_id>/                   (empty directory for model assets)
"""

import argparse
import os
import shutil
import sys

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'templates', 'manifest.yaml')

def init_character(char_id: str, display_name: str = None, archetype: str = 'explorer',
                   output_dir: str = None):
    if output_dir is None:
        output_dir = os.getcwd()

    char_dir = os.path.join(output_dir, 'characters', char_id)
    model_dir = os.path.join(output_dir, 'models', char_id)

    # Create directories
    os.makedirs(char_dir, exist_ok=True)
    os.makedirs(os.path.join(model_dir, 'textures'), exist_ok=True)
    os.makedirs(os.path.join(model_dir, 'motions'), exist_ok=True)

    # Read and customize template
    with open(TEMPLATE_PATH, 'r') as f:
        content = f.read()

    content = content.replace('{{char}}', char_id)
    if display_name:
        content = content.replace('display_name: "Character Name"',
                                  f'display_name: "{display_name}"')
    content = content.replace('archetype: "explorer"', f'archetype: "{archetype}"')

    manifest_path = os.path.join(char_dir, 'manifest.yaml')
    with open(manifest_path, 'w') as f:
        f.write(content)

    print(f"✅ Character '{char_id}' initialized:")
    print(f"   Manifest: {manifest_path}")
    print(f"   Model dir: {model_dir}/")
    print(f"\nNext steps:")
    print(f"  1. Place Live2D model files in {model_dir}/")
    print(f"  2. Edit {manifest_path} to customize personality and expressions")
    print(f"  3. Register in CharacterRegistry (see SKILL.md Step 3)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Initialize a new Live2D character')
    parser.add_argument('char_id', help='Character identifier (lowercase, no spaces)')
    parser.add_argument('--display-name', help='Human-readable display name')
    parser.add_argument('--archetype', default='explorer',
                        choices=['explorer', 'guardian', 'creator', 'sage', 'rebel'],
                        help='Character archetype (default: explorer)')
    parser.add_argument('--output-dir', help='Output directory (default: cwd)')
    args = parser.parse_args()

    init_character(args.char_id, args.display_name, args.archetype, args.output_dir)
