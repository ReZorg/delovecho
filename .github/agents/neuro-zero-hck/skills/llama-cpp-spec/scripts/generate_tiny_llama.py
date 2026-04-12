#!/usr/bin/env python3
"""
generate_tiny_llama.py - Generate minimal LLM inference scaffolds

Usage:
    python generate_tiny_llama.py --target wasm-web --model qwen2-0.5b --output ./my-chatbot
    python generate_tiny_llama.py --target wasm-node --model tinyllama --output ./my-cli
    python generate_tiny_llama.py --list-models
    python generate_tiny_llama.py --list-targets
"""

import argparse
import json
import os
import shutil
from pathlib import Path

# Model configurations
MODELS = {
    "qwen2-0.5b": {
        "name": "Qwen2-0.5B",
        "arch": "qwen2",
        "template": "chatml",
        "n_vocab": 151936,
        "n_embd": 896,
        "n_layer": 24,
        "n_head": 14,
        "n_head_kv": 2,
        "n_ff": 4864,
        "n_ctx": 32768,
        "rope_freq_base": 1000000,
        "q4_0_size_mb": 350,
        "gguf_url": "https://huggingface.co/Qwen/Qwen2-0.5B-Instruct-GGUF/resolve/main/qwen2-0_5b-instruct-q4_0.gguf",
        "recommended": True
    },
    "smollm-360m": {
        "name": "SmolLM-360M",
        "arch": "llama",
        "template": "chatml",
        "n_vocab": 49152,
        "n_embd": 960,
        "n_layer": 32,
        "n_head": 15,
        "n_head_kv": 5,
        "n_ff": 2560,
        "n_ctx": 2048,
        "rope_freq_base": 10000,
        "q4_0_size_mb": 220,
        "gguf_url": "https://huggingface.co/HuggingFaceTB/SmolLM-360M-Instruct-GGUF/resolve/main/smollm-360m-instruct-q4_0.gguf",
        "recommended": True
    },
    "smollm-135m": {
        "name": "SmolLM-135M",
        "arch": "llama",
        "template": "chatml",
        "n_vocab": 49152,
        "n_embd": 576,
        "n_layer": 30,
        "n_head": 9,
        "n_head_kv": 3,
        "n_ff": 1536,
        "n_ctx": 2048,
        "rope_freq_base": 10000,
        "q4_0_size_mb": 85,
        "gguf_url": "https://huggingface.co/HuggingFaceTB/SmolLM-135M-Instruct-GGUF/resolve/main/smollm-135m-instruct-q4_0.gguf",
        "recommended": False
    },
    "tinyllama": {
        "name": "TinyLlama-1.1B",
        "arch": "llama",
        "template": "chatml",
        "n_vocab": 32000,
        "n_embd": 2048,
        "n_layer": 22,
        "n_head": 32,
        "n_head_kv": 4,
        "n_ff": 5632,
        "n_ctx": 2048,
        "rope_freq_base": 10000,
        "q4_0_size_mb": 670,
        "gguf_url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_0.gguf",
        "recommended": True
    },
    "phi-2": {
        "name": "Phi-2",
        "arch": "phi2",
        "template": "phi",
        "n_vocab": 51200,
        "n_embd": 2560,
        "n_layer": 32,
        "n_head": 32,
        "n_head_kv": 32,
        "n_ff": 10240,
        "n_ctx": 2048,
        "rope_freq_base": 10000,
        "partial_rotary_factor": 0.4,
        "q4_0_size_mb": 1600,
        "gguf_url": "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_0.gguf",
        "recommended": False
    },
    "gemma-2b": {
        "name": "Gemma-2B",
        "arch": "gemma",
        "template": "gemma",
        "n_vocab": 256000,
        "n_embd": 2048,
        "n_layer": 18,
        "n_head": 8,
        "n_head_kv": 1,
        "n_ff": 16384,
        "n_ctx": 8192,
        "rope_freq_base": 10000,
        "q4_0_size_mb": 1200,
        "gguf_url": "https://huggingface.co/google/gemma-2b-it-GGUF/resolve/main/gemma-2b-it.Q4_0.gguf",
        "recommended": False
    }
}

# Target configurations
TARGETS = {
    "wasm-web": {
        "name": "WASM Web Worker",
        "description": "Browser-based inference in Web Workers",
        "template_dir": "wasm-web-worker",
        "features": ["streaming", "indexeddb_cache", "service_worker"],
        "max_memory_mb": 2048,
        "simd": True
    },
    "wasm-node": {
        "name": "WASM Node.js",
        "description": "Server-side WASM for portability",
        "template_dir": "wasm-node",
        "features": ["streaming", "filesystem", "threads"],
        "max_memory_mb": 4096,
        "simd": True
    },
    "native-tiny": {
        "name": "Native Tiny",
        "description": "Minimal native C implementation",
        "template_dir": "native-tiny",
        "features": ["streaming", "mmap"],
        "max_memory_mb": None,
        "simd": False
    }
}

# Chat templates
TEMPLATES = {
    "chatml": {
        "system": "<|im_start|>system\n{content}<|im_end|>\n",
        "user": "<|im_start|>user\n{content}<|im_end|>\n",
        "assistant": "<|im_start|>assistant\n{content}<|im_end|>\n",
        "generation": "<|im_start|>assistant\n",
        "stop": ["<|im_end|>", "<|im_start|>"]
    },
    "llama2": {
        "system": "<<SYS>>\n{content}\n<</SYS>>\n\n",
        "user": "[INST] {content} [/INST]",
        "assistant": " {content} </s><s>",
        "generation": "",
        "stop": ["</s>"]
    },
    "phi": {
        "system": "",
        "user": "Instruct: {content}\n",
        "assistant": "Output: {content}\n",
        "generation": "Output:",
        "stop": ["Instruct:", "\n\n"]
    },
    "gemma": {
        "system": "",
        "user": "<start_of_turn>user\n{content}<end_of_turn>\n",
        "assistant": "<start_of_turn>model\n{content}<end_of_turn>\n",
        "generation": "<start_of_turn>model\n",
        "stop": ["<end_of_turn>"]
    }
}


def get_script_dir():
    """Get the directory containing this script."""
    return Path(__file__).parent.absolute()


def get_skill_dir():
    """Get the skill root directory."""
    return get_script_dir().parent


def list_models():
    """Print available models."""
    print("\nAvailable Models:\n")
    print(f"{'Model':<15} {'Size (Q4_0)':<12} {'Context':<10} {'Recommended':<12}")
    print("-" * 50)
    
    for key, model in MODELS.items():
        rec = "✓" if model.get("recommended") else ""
        print(f"{key:<15} {model['q4_0_size_mb']:<10} MB {model['n_ctx']:<10} {rec:<12}")
    
    print("\nUse --model <name> to select a model.")


def list_targets():
    """Print available targets."""
    print("\nAvailable Targets:\n")
    
    for key, target in TARGETS.items():
        print(f"  {key}")
        print(f"    {target['description']}")
        print(f"    Features: {', '.join(target['features'])}")
        if target['max_memory_mb']:
            print(f"    Max memory: {target['max_memory_mb']} MB")
        print()


def generate_config(model_key: str, target_key: str) -> dict:
    """Generate configuration for the scaffold."""
    model = MODELS[model_key]
    target = TARGETS[target_key]
    template = TEMPLATES[model["template"]]
    
    return {
        "model": {
            "key": model_key,
            **model
        },
        "target": {
            "key": target_key,
            **target
        },
        "template": {
            "name": model["template"],
            **template
        },
        "build": {
            "simd": target["simd"],
            "max_memory_mb": target["max_memory_mb"] or 4096
        }
    }


def copy_template(target_key: str, output_dir: Path):
    """Copy template files to output directory."""
    skill_dir = get_skill_dir()
    template_dir = skill_dir / "templates" / TARGETS[target_key]["template_dir"]
    
    if not template_dir.exists():
        print(f"Warning: Template directory not found: {template_dir}")
        print("Creating minimal scaffold...")
        output_dir.mkdir(parents=True, exist_ok=True)
        return False
    
    # Copy template files
    shutil.copytree(template_dir, output_dir, dirs_exist_ok=True)
    return True


def generate_manifest(config: dict, output_dir: Path):
    """Generate manifest.json with configuration."""
    manifest = {
        "name": f"tiny-llm-{config['model']['key']}",
        "version": "1.0.0",
        "model": config["model"]["key"],
        "model_name": config["model"]["name"],
        "architecture": config["model"]["arch"],
        "target": config["target"]["key"],
        "template": config["template"]["name"],
        "gguf_url": config["model"]["gguf_url"],
        "q4_0_size_mb": config["model"]["q4_0_size_mb"],
        "context_length": config["model"]["n_ctx"],
        "build": config["build"]
    }
    
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)


def generate_config_header(config: dict, output_dir: Path):
    """Generate C configuration header."""
    model = config["model"]
    
    header = f"""// Auto-generated configuration for {model['name']}
#ifndef LLAMA_CONFIG_H
#define LLAMA_CONFIG_H

// Model: {model['name']}
#define MODEL_NAME "{model['name']}"
#define MODEL_ARCH "{model['arch']}"

// Architecture parameters
#define N_VOCAB {model['n_vocab']}
#define N_EMBD {model['n_embd']}
#define N_LAYER {model['n_layer']}
#define N_HEAD {model['n_head']}
#define N_HEAD_KV {model['n_head_kv']}
#define N_FF {model['n_ff']}
#define N_CTX {model['n_ctx']}
#define ROPE_FREQ_BASE {model['rope_freq_base']}f

// GQA ratio
#define GQA_RATIO ({model['n_head']} / {model['n_head_kv']})

// Chat template
#define TEMPLATE_NAME "{config['template']['name']}"

// Build configuration
#define USE_SIMD {1 if config['build']['simd'] else 0}
#define MAX_MEMORY_MB {config['build']['max_memory_mb']}

#endif // LLAMA_CONFIG_H
"""
    
    config_path = output_dir / "llama-config.h"
    with open(config_path, "w") as f:
        f.write(header)


def generate_readme(config: dict, output_dir: Path):
    """Generate README with instructions."""
    model = config["model"]
    target = config["target"]
    
    readme = f"""# Tiny LLM: {model['name']}

Minimal LLM inference engine for {target['description'].lower()}.

## Model

- **Name**: {model['name']}
- **Architecture**: {model['arch']}
- **Size (Q4_0)**: {model['q4_0_size_mb']} MB
- **Context Length**: {model['n_ctx']}
- **Chat Template**: {config['template']['name']}

## Quick Start

### 1. Download Model

```bash
wget {model['gguf_url']}
```

### 2. Build

"""
    
    if target["key"] == "wasm-web":
        readme += """```bash
# Requires Emscripten SDK
source /path/to/emsdk/emsdk_env.sh
make
```

### 3. Run

```bash
make serve
# Open http://localhost:8080
```
"""
    elif target["key"] == "wasm-node":
        readme += """```bash
# Requires Emscripten SDK
source /path/to/emsdk/emsdk_env.sh
make
```

### 3. Run

```bash
node cli.mjs model.gguf
```
"""
    else:
        readme += """```bash
make
```

### 3. Run

```bash
./llama-tiny model.gguf "Hello!"
```
"""
    
    readme += f"""
## Configuration

See `llama-config.h` for model-specific parameters.
See `manifest.json` for build configuration.

## Memory Requirements

| Context | KV Cache | Total |
|---------|----------|-------|
| 512 | ~{model['n_layer'] * model['n_head_kv'] * 64 * 512 * 2 // (1024*1024)} MB | ~{model['q4_0_size_mb'] + model['n_layer'] * model['n_head_kv'] * 64 * 512 * 2 // (1024*1024)} MB |
| 2048 | ~{model['n_layer'] * model['n_head_kv'] * 64 * 2048 * 2 // (1024*1024)} MB | ~{model['q4_0_size_mb'] + model['n_layer'] * model['n_head_kv'] * 64 * 2048 * 2 // (1024*1024)} MB |

## Files

- `llama-config.h` - Model configuration
- `manifest.json` - Build manifest
- `Makefile` - Build script
"""
    
    readme_path = output_dir / "README.md"
    with open(readme_path, "w") as f:
        f.write(readme)


def main():
    parser = argparse.ArgumentParser(
        description="Generate minimal LLM inference scaffolds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --target wasm-web --model qwen2-0.5b --output ./my-chatbot
  %(prog)s --target wasm-node --model tinyllama --output ./my-cli
  %(prog)s --list-models
  %(prog)s --list-targets
"""
    )
    
    parser.add_argument("--target", choices=list(TARGETS.keys()),
                        help="Target platform")
    parser.add_argument("--model", choices=list(MODELS.keys()),
                        help="Model to configure for")
    parser.add_argument("--output", type=Path,
                        help="Output directory")
    parser.add_argument("--list-models", action="store_true",
                        help="List available models")
    parser.add_argument("--list-targets", action="store_true",
                        help="List available targets")
    
    args = parser.parse_args()
    
    if args.list_models:
        list_models()
        return
    
    if args.list_targets:
        list_targets()
        return
    
    if not args.target or not args.model or not args.output:
        parser.print_help()
        print("\nError: --target, --model, and --output are required")
        return 1
    
    # Validate model fits in target memory
    model = MODELS[args.model]
    target = TARGETS[args.target]
    
    if target["max_memory_mb"] and model["q4_0_size_mb"] > target["max_memory_mb"]:
        print(f"Warning: Model size ({model['q4_0_size_mb']} MB) exceeds target max memory ({target['max_memory_mb']} MB)")
        print("Consider using a smaller model or increasing context limits.")
    
    # Generate scaffold
    print(f"Generating scaffold for {model['name']} on {target['name']}...")
    
    config = generate_config(args.model, args.target)
    
    # Copy template
    output_dir = args.output.absolute()
    template_copied = copy_template(args.target, output_dir)
    
    # Generate config files
    generate_manifest(config, output_dir)
    generate_config_header(config, output_dir)
    generate_readme(config, output_dir)
    
    print(f"\nGenerated scaffold at: {output_dir}")
    print(f"  Model: {model['name']} ({model['arch']})")
    print(f"  Target: {target['name']}")
    print(f"  Size: {model['q4_0_size_mb']} MB (Q4_0)")
    print(f"  Template: {config['template']['name']}")
    
    if template_copied:
        print("\nNext steps:")
        print(f"  1. cd {output_dir}")
        print(f"  2. Download model: wget {model['gguf_url']}")
        print("  3. Build: make")
    else:
        print("\nNote: Template files not found. Only configuration generated.")
    
    return 0


if __name__ == "__main__":
    exit(main() or 0)
