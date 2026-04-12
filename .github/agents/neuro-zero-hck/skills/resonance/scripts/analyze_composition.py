#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
from collections import defaultdict

def find_php_files(path):
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".php"):
                yield os.path.join(root, file)

def analyze_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    class_name_match = re.search(r"class\s+([\w\\]+)", content)
    if not class_name_match:
        return None

    class_name = class_name_match.group(1)

    attributes = re.findall(r"#\[([\w\\]+)", content)
    constructor_deps = []
    constructor_match = re.search(r"__construct\((.*?)\)", content, re.DOTALL)
    if constructor_match:
        params = constructor_match.group(1)
        constructor_deps = re.findall(r"private\s+readonly\s+([\w\\]+)\s+\$?(\w+)", params)
        constructor_deps = [dep[0] for dep in constructor_deps]

    return {
        "class_name": class_name,
        "attributes": attributes,
        "dependencies": constructor_deps,
    }

def main():
    parser = argparse.ArgumentParser(description="Analyze Resonance project composition.")
    parser.add_argument("path", help="Path to the Resonance project directory.")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: Path not found: {args.path}")
        return

    print(f"Analyzing project at: {args.path}\n")

    additive_compositions = defaultdict(list)
    multiplicative_compositions = defaultdict(list)

    for file_path in find_php_files(args.path):
        analysis = analyze_file(file_path)
        if not analysis:
            continue

        # Additive (Collections)
        for attr in analysis["attributes"]:
            if "Singleton" in attr:
                match = re.search(r"collection:\s*SingletonCollection::(\w+)", open(file_path).read())
                if match:
                    collection_name = match.group(1)
                    additive_compositions[collection_name].append(analysis["class_name"])

        # Multiplicative (Dependencies)
        if analysis["dependencies"]:
            multiplicative_compositions[analysis["class_name"]] = analysis["dependencies"]

    print("=== Additive Compositions (⊕) ===")
    print("--- SingletonCollections ---")
    for collection, items in sorted(additive_compositions.items()):
        if len(items) > 1:
            print(f"\nCollection: {collection}")
            for item in items:
                print(f"  - {item}")

    print("\n\n=== Multiplicative Compositions (⊗) ===")
    print("--- Constructor Injection ---")
    for class_name, deps in sorted(multiplicative_compositions.items()):
        if deps:
            print(f"\nClass: {class_name}")
            for dep in deps:
                print(f"  - depends on {dep}")

if __name__ == "__main__":
    main()
