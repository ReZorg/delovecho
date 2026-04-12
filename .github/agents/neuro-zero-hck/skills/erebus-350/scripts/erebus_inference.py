#!/usr/bin/env python3
"""
erebus_inference.py — Load and run KoboldAI/OPT-350M-Erebus for text generation.

Usage:
    python erebus_inference.py --prompt "Your story prompt here"
    python erebus_inference.py --prompt "Your prompt" --max-tokens 200 --temperature 0.9
    python erebus_inference.py --prompt "[Genre: fantasy, romance]\nThe knight entered the chamber"
    python erebus_inference.py --interactive

Requirements:
    pip install transformers torch accelerate
"""

import argparse
import sys

MODEL_ID = "KoboldAI/OPT-350M-Erebus"


def load_model(device="auto", dtype="float16"):
    """Load the Erebus 350M model and tokenizer."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    dtype_map = {
        "float16": torch.float16,
        "float32": torch.float32,
        "bfloat16": torch.bfloat16,
    }
    torch_dtype = dtype_map.get(dtype, torch.float16)

    print(f"Loading {MODEL_ID} on {device} with {dtype}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch_dtype,
        device_map=device,
    )
    print(f"Model loaded. Parameters: {sum(p.numel() for p in model.parameters()):,}")
    return model, tokenizer


def generate(model, tokenizer, prompt, max_new_tokens=150, temperature=0.9,
             top_p=0.95, top_k=50, repetition_penalty=1.1, do_sample=True):
    """Generate text from a prompt."""
    import torch

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            do_sample=do_sample,
            pad_token_id=tokenizer.eos_token_id,
        )
    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated


def interactive_mode(model, tokenizer, **gen_kwargs):
    """Run an interactive text generation loop."""
    print("\n=== Erebus 350M Interactive Mode ===")
    print("Type your prompt and press Enter. Type 'quit' to exit.")
    print("Prefix with [Genre: ...] for genre-guided generation.\n")

    while True:
        try:
            prompt = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not prompt or prompt.lower() in ("quit", "exit", "q"):
            break
        result = generate(model, tokenizer, prompt, **gen_kwargs)
        # Print only the newly generated portion
        new_text = result[len(prompt):]
        print(new_text)
        print()


def main():
    parser = argparse.ArgumentParser(description="KoboldAI/OPT-350M-Erebus inference")
    parser.add_argument("--prompt", type=str, default=None, help="Text prompt for generation")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--max-tokens", type=int, default=150, help="Max new tokens (default: 150)")
    parser.add_argument("--temperature", type=float, default=0.9, help="Sampling temperature (default: 0.9)")
    parser.add_argument("--top-p", type=float, default=0.95, help="Top-p nucleus sampling (default: 0.95)")
    parser.add_argument("--top-k", type=int, default=50, help="Top-k sampling (default: 50)")
    parser.add_argument("--repetition-penalty", type=float, default=1.1, help="Repetition penalty (default: 1.1)")
    parser.add_argument("--device", type=str, default="auto", help="Device: auto, cpu, cuda (default: auto)")
    parser.add_argument("--dtype", type=str, default="float16", choices=["float16", "float32", "bfloat16"])

    args = parser.parse_args()

    if not args.prompt and not args.interactive:
        parser.print_help()
        sys.exit(1)

    model, tokenizer = load_model(device=args.device, dtype=args.dtype)

    gen_kwargs = dict(
        max_new_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        top_k=args.top_k,
        repetition_penalty=args.repetition_penalty,
    )

    if args.interactive:
        interactive_mode(model, tokenizer, **gen_kwargs)
    else:
        result = generate(model, tokenizer, args.prompt, **gen_kwargs)
        print(result)


if __name__ == "__main__":
    main()
