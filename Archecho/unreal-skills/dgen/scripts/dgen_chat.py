#!/usr/bin/env python3
"""DreamGen Chat Completion - OpenAI-compatible API wrapper.

Usage:
    python dgen_chat.py --system "System prompt" --messages messages.json [options]
    python dgen_chat.py --system "You are a writer" --user "Write a scene" [options]

Options:
    --model         Model ID: lucid-v1-medium or lucid-v1-extra-large (default: lucid-v1-extra-large)
    --system        System prompt text
    --user          Single user message (alternative to --messages)
    --messages      Path to JSON file with messages array
    --role-mode     Response role: 'assistant' or 'text' (default: text)
    --char-name     Character name for text role responses
    --max-tokens    Maximum tokens to generate (default: 500)
    --temperature   Sampling temperature (default: 0.8)
    --min-p         Min-p sampling (default: 0.05)
    --top-p         Top-p sampling (default: 0.95)
    --rep-penalty   Repetition penalty (default: 1.02)
    --freq-penalty  Frequency penalty (default: 0.1)
    --pres-penalty  Presence penalty (default: 0.1)
    --dry           Enable DRY sampler with defaults
    --output        Output file path (default: stdout)
    --no-stream     Disable streaming output
"""

import argparse
import json
import os
import sys
from openai import OpenAI

def main():
    parser = argparse.ArgumentParser(description="DreamGen Chat Completion")
    parser.add_argument("--model", default="lucid-v1-extra-large", 
                        choices=["lucid-v1-medium", "lucid-v1-extra-large"])
    parser.add_argument("--system", help="System prompt")
    parser.add_argument("--user", help="Single user message")
    parser.add_argument("--messages", help="Path to messages JSON file")
    parser.add_argument("--role-mode", default="text", choices=["assistant", "text"])
    parser.add_argument("--char-name", help="Character name for text role")
    parser.add_argument("--max-tokens", type=int, default=500)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--min-p", type=float, default=0.05)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--rep-penalty", type=float, default=1.02)
    parser.add_argument("--freq-penalty", type=float, default=0.1)
    parser.add_argument("--pres-penalty", type=float, default=0.1)
    parser.add_argument("--dry", action="store_true", help="Enable DRY sampler")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--no-stream", action="store_true")
    args = parser.parse_args()

    # Build messages
    messages = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    
    if args.messages:
        with open(args.messages) as f:
            messages.extend(json.load(f))
    elif args.user:
        messages.append({"role": "user", "content": args.user})
    else:
        print("Error: Provide --user or --messages", file=sys.stderr)
        sys.exit(1)

    # Build role_config
    role_config = {
        "assistant": {
            "role": args.role_mode,
            "open": args.role_mode == "text"
        }
    }
    if args.char_name and args.role_mode == "text":
        role_config["assistant"]["name"] = args.char_name

    # Build extra_body
    extra_body = {
        "min_p": args.min_p,
        "repetition_penalty": args.rep_penalty,
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
        top_p=args.top_p,
        frequency_penalty=args.freq_penalty,
        presence_penalty=args.pres_penalty,
        stream=not args.no_stream,
        extra_body=extra_body
    )

    # Handle output
    output_file = open(args.output, "w") if args.output else sys.stdout
    
    if args.no_stream:
        content = response.choices[0].message.content
        output_file.write(content)
    else:
        for chunk in response:
            if chunk.choices[0].delta.content:
                output_file.write(chunk.choices[0].delta.content)
                if output_file == sys.stdout:
                    output_file.flush()
    
    if args.output:
        output_file.close()
        print(f"\nOutput saved to: {args.output}", file=sys.stderr)

if __name__ == "__main__":
    main()
