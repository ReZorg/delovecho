#!/usr/bin/env python3
"""
GGML Minimal Implementation Generator

Generates a minimal GGML implementation scaffold based on:
- Target architecture (arm64, x86-64, wasm)
- Model family (llama, whisper, bert)
- Quantization types (f32, f16, q4_0, q4_k, etc.)

Usage:
    python generate_minimal.py --arch arm64 --model llama --quants q4_k,f16 --output ./my-impl
"""

import argparse
import os
import json
from pathlib import Path
from typing import List, Set

# =============================================================================
# Operation Requirements by Model
# =============================================================================

MODEL_OPS = {
    "llama": {
        "required": [
            "GET_ROWS", "MUL_MAT", "RMS_NORM", "ROPE", "SOFT_MAX",
            "SILU", "ADD", "MUL", "RESHAPE", "PERMUTE", "CONT"
        ],
        "optional": ["MUL_MAT_ID", "FLASH_ATTN_EXT", "DIAG_MASK_INF"]
    },
    "whisper": {
        "required": [
            "CONV_1D", "GET_ROWS", "MUL_MAT", "NORM", "SOFT_MAX",
            "GELU", "ADD", "MUL", "RESHAPE", "PERMUTE", "TRANSPOSE",
            "CONT", "DIAG_MASK_INF", "PAD", "SCALE"
        ],
        "optional": ["FLASH_ATTN_EXT"]
    },
    "bert": {
        "required": [
            "GET_ROWS", "MUL_MAT", "NORM", "SOFT_MAX", "GELU",
            "ADD", "MUL", "RESHAPE", "PERMUTE", "CONT"
        ],
        "optional": []
    },
    "custom": {
        "required": [],
        "optional": []
    }
}

# =============================================================================
# Architecture-Specific Settings
# =============================================================================

ARCH_SETTINGS = {
    "arm64": {
        "simd": "NEON",
        "compiler_flags": "-march=armv8-a",
        "defines": ["__ARM_NEON", "__aarch64__"],
        "file_suffix": "neon"
    },
    "x86-64": {
        "simd": "AVX2",
        "compiler_flags": "-mavx2 -mfma",
        "defines": ["__AVX2__", "__FMA__"],
        "file_suffix": "avx2"
    },
    "x86-64-avx512": {
        "simd": "AVX-512",
        "compiler_flags": "-mavx512f -mavx512bw -mavx512dq -mavx512vl",
        "defines": ["__AVX512F__"],
        "file_suffix": "avx512"
    },
    "wasm": {
        "simd": "WASM SIMD",
        "compiler_flags": "-msimd128",
        "defines": ["__wasm_simd128__"],
        "file_suffix": "wasm"
    },
    "scalar": {
        "simd": "None",
        "compiler_flags": "",
        "defines": [],
        "file_suffix": "scalar"
    }
}

# =============================================================================
# Quantization Type Definitions
# =============================================================================

QUANT_TYPES = {
    "f32": {"block_size": 1, "bytes_per_block": 4, "header": False},
    "f16": {"block_size": 1, "bytes_per_block": 2, "header": False},
    "q4_0": {"block_size": 32, "bytes_per_block": 18, "header": True},
    "q4_1": {"block_size": 32, "bytes_per_block": 20, "header": True},
    "q5_0": {"block_size": 32, "bytes_per_block": 22, "header": True},
    "q5_1": {"block_size": 32, "bytes_per_block": 24, "header": True},
    "q8_0": {"block_size": 32, "bytes_per_block": 34, "header": True},
    "q4_k": {"block_size": 256, "bytes_per_block": 144, "header": True},
    "q5_k": {"block_size": 256, "bytes_per_block": 176, "header": True},
    "q6_k": {"block_size": 256, "bytes_per_block": 210, "header": True},
}

# =============================================================================
# File Templates
# =============================================================================

def generate_config_h(model: str, arch: str, quants: List[str]) -> str:
    """Generate configuration header."""
    arch_info = ARCH_SETTINGS[arch]
    ops = MODEL_OPS[model]
    
    defines = "\n".join(f"#define {d}" for d in arch_info["defines"])
    op_defines = "\n".join(f"#define GGML_OP_{op} 1" for op in ops["required"])
    type_defines = "\n".join(f"#define GGML_TYPE_{t.upper()} 1" for t in quants)
    
    return f'''#ifndef GGML_CONFIG_H
#define GGML_CONFIG_H

// Generated configuration for {model} on {arch}

// Architecture
#define GGML_ARCH "{arch}"
#define GGML_SIMD "{arch_info["simd"]}"
{defines}

// Model: {model}
#define GGML_MODEL "{model}"

// Enabled operations
{op_defines}

// Enabled types
{type_defines}

// Compiler flags: {arch_info["compiler_flags"]}

#endif // GGML_CONFIG_H
'''

def generate_makefile(model: str, arch: str, quants: List[str]) -> str:
    """Generate Makefile."""
    arch_info = ARCH_SETTINGS[arch]
    suffix = arch_info["file_suffix"]
    
    return f'''# Generated Makefile for {model} on {arch}

CC = cc
CFLAGS = -O3 {arch_info["compiler_flags"]} -Wall -Wextra
LDFLAGS = -lm

# Source files
SRCS = main.c \\
       ggml-ops-{suffix}.c \\
       ggml-quants-{suffix}.c \\
       gguf-minimal.c \\
       {model}-minimal.c

OBJS = $(SRCS:.c=.o)
TARGET = {model}-minimal

all: $(TARGET)

$(TARGET): $(OBJS)
\t$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
\t$(CC) $(CFLAGS) -c -o $@ $<

clean:
\trm -f $(OBJS) $(TARGET)

.PHONY: all clean
'''

def generate_readme(model: str, arch: str, quants: List[str]) -> str:
    """Generate README."""
    arch_info = ARCH_SETTINGS[arch]
    ops = MODEL_OPS[model]
    
    return f'''# {model.title()} Minimal Implementation ({arch})

Generated minimal GGML implementation for {model} models on {arch} architecture.

## Configuration

- **Architecture**: {arch} ({arch_info["simd"]})
- **Model**: {model}
- **Quantization types**: {", ".join(quants)}
- **Required operations**: {len(ops["required"])}

## Build

```bash
make
```

Or manually:

```bash
{arch_info["compiler_flags"] and f'cc -O3 {arch_info["compiler_flags"]} -o {model}-minimal *.c -lm' or f'cc -O3 -o {model}-minimal *.c -lm'}
```

## Operations Implemented

| Operation | Status |
|-----------|--------|
{chr(10).join(f"| {op} | ✓ Required |" for op in ops["required"])}
{chr(10).join(f"| {op} | ○ Optional |" for op in ops["optional"])}

## Quantization Types

| Type | Block Size | Bytes/Block |
|------|------------|-------------|
{chr(10).join(f"| {t} | {QUANT_TYPES[t]['block_size']} | {QUANT_TYPES[t]['bytes_per_block']} |" for t in quants)}

## Files

```
{model}-{arch}-minimal/
├── ggml-config.h       # Generated configuration
├── ggml-minimal.h      # Core types and macros
├── ggml-quants.h       # Quantization structures
├── ggml-quants-{arch_info["file_suffix"]}.c  # SIMD-optimized quantization
├── ggml-ops.h          # Operation declarations
├── ggml-ops-{arch_info["file_suffix"]}.c     # SIMD-optimized operations
├── gguf-minimal.h      # GGUF file format
├── gguf-minimal.c      # GGUF implementation
├── {model}-minimal.h   # Model structure
├── {model}-minimal.c   # Model forward pass
├── main.c              # Example usage
├── Makefile            # Build script
└── README.md           # This file
```

## Extending

To add more operations, edit `ggml-ops-{arch_info["file_suffix"]}.c`.

To add more quantization types, edit `ggml-quants-{arch_info["file_suffix"]}.c`.

## License

MIT
'''

def generate_stub_files(output_dir: Path, model: str, arch: str, quants: List[str]):
    """Generate stub implementation files."""
    arch_info = ARCH_SETTINGS[arch]
    suffix = arch_info["file_suffix"]
    ops = MODEL_OPS[model]
    
    # ggml-ops.h
    op_decls = "\n".join(f"void ggml_compute_{op.lower()}(struct ggml_tensor* dst);" 
                         for op in ops["required"])
    
    ops_h = f'''#ifndef GGML_OPS_H
#define GGML_OPS_H

#include "ggml-minimal.h"

#ifdef __cplusplus
extern "C" {{
#endif

// Operation declarations for {model}
{op_decls}

#ifdef __cplusplus
}}
#endif

#endif // GGML_OPS_H
'''
    
    # ggml-ops-{suffix}.c
    op_impls = "\n\n".join(f'''void ggml_compute_{op.lower()}(struct ggml_tensor* dst) {{
    // TODO: Implement {op} for {arch}
    (void)dst;
}}''' for op in ops["required"])
    
    ops_c = f'''#include "ggml-ops.h"
#include "ggml-quants.h"
{"#include <arm_neon.h>" if arch == "arm64" else ""}
{"#include <immintrin.h>" if "x86" in arch else ""}

// {arch_info["simd"]}-optimized operations for {model}

{op_impls}
'''
    
    # Write files
    (output_dir / "ggml-ops.h").write_text(ops_h)
    (output_dir / f"ggml-ops-{suffix}.c").write_text(ops_c)

# =============================================================================
# Main Generator
# =============================================================================

def generate_scaffold(model: str, arch: str, quants: List[str], output_dir: str):
    """Generate complete scaffold."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate configuration files
    (output_path / "ggml-config.h").write_text(generate_config_h(model, arch, quants))
    (output_path / "Makefile").write_text(generate_makefile(model, arch, quants))
    (output_path / "README.md").write_text(generate_readme(model, arch, quants))
    
    # Generate stub implementation files
    generate_stub_files(output_path, model, arch, quants)
    
    # Copy template files from skill directory if available
    skill_dir = Path(__file__).parent.parent
    template_dir = skill_dir / "templates" / f"{model}-{arch}-minimal"
    
    if template_dir.exists():
        print(f"Copying template files from {template_dir}")
        for f in template_dir.glob("*"):
            if f.is_file() and f.name not in ["README.md", "Makefile", "ggml-config.h"]:
                (output_path / f.name).write_text(f.read_text())
    
    # Generate manifest
    manifest = {
        "model": model,
        "arch": arch,
        "quants": quants,
        "ops_required": MODEL_OPS[model]["required"],
        "ops_optional": MODEL_OPS[model]["optional"],
        "simd": ARCH_SETTINGS[arch]["simd"],
    }
    (output_path / "manifest.json").write_text(json.dumps(manifest, indent=2))
    
    print(f"\nGenerated scaffold at: {output_path}")
    print(f"  Model: {model}")
    print(f"  Architecture: {arch} ({ARCH_SETTINGS[arch]['simd']})")
    print(f"  Quantization: {', '.join(quants)}")
    print(f"  Operations: {len(MODEL_OPS[model]['required'])} required")
    print(f"\nNext steps:")
    print(f"  1. Implement operations in ggml-ops-{ARCH_SETTINGS[arch]['file_suffix']}.c")
    print(f"  2. Implement quantization in ggml-quants-{ARCH_SETTINGS[arch]['file_suffix']}.c")
    print(f"  3. Run 'make' to build")

def main():
    parser = argparse.ArgumentParser(
        description="Generate minimal GGML implementation scaffold",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --arch arm64 --model llama --quants q4_k,f16 --output ./llama-arm64
  %(prog)s --arch x86-64 --model whisper --quants q5_k --output ./whisper-x64
  %(prog)s --arch wasm --model bert --quants f32 --output ./bert-wasm
        """
    )
    
    parser.add_argument("--arch", required=True, 
                        choices=list(ARCH_SETTINGS.keys()),
                        help="Target architecture")
    parser.add_argument("--model", required=True,
                        choices=list(MODEL_OPS.keys()),
                        help="Model family")
    parser.add_argument("--quants", required=True,
                        help="Comma-separated quantization types (e.g., q4_k,f16)")
    parser.add_argument("--output", required=True,
                        help="Output directory")
    parser.add_argument("--list-ops", action="store_true",
                        help="List operations for model and exit")
    parser.add_argument("--list-types", action="store_true",
                        help="List quantization types and exit")
    
    args = parser.parse_args()
    
    if args.list_ops:
        ops = MODEL_OPS[args.model]
        print(f"Operations for {args.model}:")
        print(f"  Required: {', '.join(ops['required'])}")
        print(f"  Optional: {', '.join(ops['optional'])}")
        return
    
    if args.list_types:
        print("Quantization types:")
        for t, info in QUANT_TYPES.items():
            print(f"  {t}: block_size={info['block_size']}, bytes={info['bytes_per_block']}")
        return
    
    # Parse quantization types
    quants = [q.strip().lower() for q in args.quants.split(",")]
    for q in quants:
        if q not in QUANT_TYPES:
            print(f"Error: Unknown quantization type '{q}'")
            print(f"Available: {', '.join(QUANT_TYPES.keys())}")
            return
    
    generate_scaffold(args.model, args.arch, quants, args.output)

if __name__ == "__main__":
    main()
