#!/usr/bin/env python3
"""DreamGen Story Generation Helper.

High-level interface for creative writing with character management.

Usage:
    python dgen_story.py --scenario scenario.json --continue-as "Character" [options]
    python dgen_story.py --scenario scenario.json --narrator [options]

Scenario JSON format:
{
    "system": "Setting and context description",
    "characters": {
        "Alice": "Character description for Alice",
        "Bob": "Character description for Bob"
    },
    "history": [
        {"role": "text", "name": "Alice", "content": "Hello there!"},
        {"role": "text", "name": "Bob", "content": "Hi Alice!"},
        {"role": "text", "name": "", "content": "The sun set behind the mountains."}
    ]
}

Options:
    --model         Model ID (default: lucid-v1-extra-large)
    --scenario      Path to scenario JSON file
    --continue-as   Character name to generate as
    --narrator      Generate as narrator (no character name)
    --max-tokens    Maximum tokens (default: 500)
    --temperature   Temperature (default: 0.8)
    --min-p         Min-p (default: 0.05)
    --dry           Enable DRY sampler
    --output        Output file path
    --append        Append to scenario file with new content
"""

import argparse
import json
import os
import sys
from openai import OpenAI

def build_messages(scenario):
    """Convert scenario to OpenAI messages format."""
    messages = []
    
    # Build system prompt with character descriptions
    system_parts = [scenario.get("system", "")]
    if scenario.get("characters"):
        system_parts.append("\n\nCharacters:")
        for name, desc in scenario["characters"].items():
            system_parts.append(f"- {name}: {desc}")
    
    messages.append({
        "role": "system",
        "content": "\n".join(system_parts)
    })
    
    # Convert history to messages with names
    for entry in scenario.get("history", []):
        role = entry.get("role", "text")
        name = entry.get("name", "")
        content = entry.get("content", "")
        
        if role == "text":
            # Use user/assistant alternation with names for text role
            # DreamGen interprets named messages as text role
            msg = {"role": "user", "content": content}
            if name:
                msg["name"] = name
            else:
                msg["name"] = ""  # Empty name = narrator
            messages.append(msg)
        else:
            messages.append({"role": role, "content": content})
    
    return messages

def main():
    parser = argparse.ArgumentParser(description="DreamGen Story Generation")
    parser.add_argument("--model", default="lucid-v1-extra-large")
    parser.add_argument("--scenario", required=True, help="Path to scenario JSON")
    parser.add_argument("--continue-as", help="Character name to generate as")
    parser.add_argument("--narrator", action="store_true", help="Generate as narrator")
    parser.add_argument("--max-tokens", type=int, default=500)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--min-p", type=float, default=0.05)
    parser.add_argument("--dry", action="store_true")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--append", action="store_true", help="Append to scenario")
    args = parser.parse_args()

    if not args.continue_as and not args.narrator:
        print("Error: Specify --continue-as CHARACTER or --narrator", file=sys.stderr)
        sys.exit(1)

    # Load scenario
    with open(args.scenario) as f:
        scenario = json.load(f)

    messages = build_messages(scenario)

    # Build role_config for response
    role_config = {
        "assistant": {
            "role": "text",
            "open": True
        }
    }
    if args.continue_as:
        role_config["assistant"]["name"] = args.continue_as
    # For narrator, name is omitted (empty string handled by API)

    # Build extra_body
    extra_body = {
        "min_p": args.min_p,
        "repetition_penalty": 1.02,
        "role_config": role_config
    }
    if args.dry:
        extra_body["dry"] = {
            "multiplier": 0.8,
            "base": 1.75,
            "allowed_length": 2
        }

    # Initialize client
    client = OpenAI(
        api_key=os.environ.get("DGEN_API_KEY"),
        base_url="https://dreamgen.com/api/openai/v1"
    )

    # Make request
    response = client.chat.completions.create(
        model=args.model,
        messages=messages,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        stream=True,
        extra_body=extra_body
    )

    # Collect output
    output_file = open(args.output, "w") if args.output else sys.stdout
    full_content = ""
    
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_content += content
            output_file.write(content)
            if output_file == sys.stdout:
                output_file.flush()

    if args.output:
        output_file.close()
        print(f"\nOutput saved to: {args.output}", file=sys.stderr)

    # Optionally append to scenario
    if args.append:
        new_entry = {
            "role": "text",
            "name": args.continue_as if args.continue_as else "",
            "content": full_content
        }
        scenario["history"].append(new_entry)
        with open(args.scenario, "w") as f:
            json.dump(scenario, f, indent=2)
        print(f"\nAppended to scenario: {args.scenario}", file=sys.stderr)

if __name__ == "__main__":
    main()
