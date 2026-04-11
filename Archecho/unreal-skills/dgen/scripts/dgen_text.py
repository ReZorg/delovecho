#!/usr/bin/env python3
"""DreamGen Native Text Completion API.

For raw prompt control using ChatML+Text format.

Usage:
    python dgen_text.py --prompt prompt.txt [options]
    python dgen_text.py --prompt-str "<|im_start|>system\n..." [options]

Options:
    --model         Model ID: lucid-v1-medium or lucid-v1-extra-large (default: lucid-v1-extra-large)
    --prompt        Path to prompt file (ChatML format)
    --prompt-str    Raw prompt string
    --max-tokens    Maximum tokens to generate (default: 500)
    --temperature   Sampling temperature (default: 0.8)
    --min-p         Min-p sampling (default: 0.05)
    --top-p         Top-p sampling (default: 0.95)
    --top-k         Top-k sampling (default: 0, disabled)
    --rep-penalty   Repetition penalty (default: 1.02)
    --freq-penalty  Frequency penalty (default: 0.1)
    --pres-penalty  Presence penalty (default: 0.1)
    --stop          Stop sequences (comma-separated)
    --allowed-roles Allowed roles for generation (comma-separated, e.g., "text,user")
    --no-eos        Ignore EOS token
    --no-eom        Disallow message end token
    --output        Output file path (default: stdout)
"""

import argparse
import json
import os
import sys
import requests

def main():
    parser = argparse.ArgumentParser(description="DreamGen Native Text Completion")
    parser.add_argument("--model", default="lucid-v1-extra-large",
                        choices=["lucid-v1-medium", "lucid-v1-extra-large"])
    parser.add_argument("--prompt", help="Path to prompt file")
    parser.add_argument("--prompt-str", help="Raw prompt string")
    parser.add_argument("--max-tokens", type=int, default=500)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--min-p", type=float, default=0.05)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--top-k", type=int, default=0)
    parser.add_argument("--rep-penalty", type=float, default=1.02)
    parser.add_argument("--freq-penalty", type=float, default=0.1)
    parser.add_argument("--pres-penalty", type=float, default=0.1)
    parser.add_argument("--stop", help="Stop sequences (comma-separated)")
    parser.add_argument("--allowed-roles", help="Allowed roles (comma-separated)")
    parser.add_argument("--no-eos", action="store_true")
    parser.add_argument("--no-eom", action="store_true")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()

    # Get prompt
    if args.prompt:
        with open(args.prompt) as f:
            prompt = f.read()
    elif args.prompt_str:
        prompt = args.prompt_str
    else:
        print("Error: Provide --prompt or --prompt-str", file=sys.stderr)
        sys.exit(1)

    # Build sampling params
    sampling_params = {
        "kind": "basic",
        "maxTokens": args.max_tokens,
        "temperature": args.temperature,
        "minP": args.min_p,
        "topP": args.top_p,
        "repetitionPenalty": args.rep_penalty,
        "frequencyPenalty": args.freq_penalty,
        "presencePenalty": args.pres_penalty,
    }
    
    if args.top_k > 0:
        sampling_params["topK"] = args.top_k
    if args.stop:
        sampling_params["stopSequences"] = args.stop.split(",")
    if args.allowed_roles:
        sampling_params["allowedRoles"] = args.allowed_roles.split(",")
    if args.no_eos:
        sampling_params["ignoreEos"] = True
    if args.no_eom:
        sampling_params["disallowMessageEnd"] = True

    # Build request
    request_body = {
        "modelId": args.model,
        "input": prompt,
        "samplingParams": sampling_params
    }

    # Make request
    api_key = os.environ.get("DGEN_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://dreamgen.com/api/v1/model/completion",
        headers=headers,
        json=request_body,
        stream=True
    )

    # Handle streaming response
    output_file = open(args.output, "w") if args.output else sys.stdout
    full_output = ""
    
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if data.get("success"):
                output = data.get("output", "")
                output_file.write(output)
                full_output += output
                if output_file == sys.stdout:
                    output_file.flush()
            else:
                print(f"\nError: {data.get('message')}", file=sys.stderr)
                sys.exit(1)

    if args.output:
        output_file.close()
        print(f"\nOutput saved to: {args.output}", file=sys.stderr)

if __name__ == "__main__":
    main()
