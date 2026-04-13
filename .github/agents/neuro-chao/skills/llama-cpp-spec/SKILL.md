---
name: llama-cpp-spec
description: Generate minimal/tiny LLM inference engines for WASM web workers, edge devices, and embedded chatbots. Use when building offline-capable browser chatbots, serverless LLM functions, or ultra-lightweight inference engines from llama.cpp patterns.
---

# Tiny LLM Inference Skill

Generate minimal LLM inference engines targeting WASM web workers, Node.js, and native platforms. Build offline-capable chatbots in under 100KB of runtime code.

## Quick Start

### 1. Generate Scaffold

```bash
python scripts/generate_tiny_llama.py \
    --target wasm-web \
    --model qwen2-0.5b \
    --output ./my-chatbot
```

### 2. Download Model

```bash
cd my-chatbot
wget https://huggingface.co/Qwen/Qwen2-0.5B-Instruct-GGUF/resolve/main/qwen2-0_5b-instruct-q4_0.gguf
```

### 3. Build and Run

```bash
source /path/to/emsdk/emsdk_env.sh
make
make serve  # Opens http://localhost:8080
```

## Parameter Space

| Dimension | Options |
|-----------|---------|
| **Target** | `wasm-web`, `wasm-node`, `native-tiny` |
| **Model** | `qwen2-0.5b`, `smollm-360m`, `smollm-135m`, `tinyllama`, `phi-2`, `gemma-2b` |

## Model Selection

| Model | Size (Q4_0) | WASM tok/s | Quality | Best For |
|-------|-------------|------------|---------|----------|
| SmolLM-135M | 85MB | 45 | Basic | Ultra-tiny, IoT |
| SmolLM-360M | 220MB | 25 | Good | Tiny, fast |
| **Qwen2-0.5B** | 350MB | 18 | Good | **Recommended** |
| TinyLlama-1.1B | 670MB | 10 | Good | Balanced |
| Phi-2 | 1.6GB | 4 | Excellent | Quality-critical |

## Target Profiles

### WASM Web Worker (`wasm-web`)

Browser-based inference for offline-capable PWAs.

```javascript
import { LlamaChat } from './llama-client.js';

const chat = new LlamaChat();
await chat.init();
await chat.loadModel('models/qwen2-0.5b-q4_0.gguf');

// Streaming response
for await (const token of chat.stream('Hello!')) {
    process.stdout.write(token);
}
```

**Features:**
- Web Worker isolation (non-blocking UI)
- IndexedDB model caching
- Service Worker for offline
- ~80KB runtime (gzipped)

### WASM Node.js (`wasm-node`)

Portable server-side inference.

```javascript
import { init, loadModel } from './llama.mjs';

await init();
const model = await loadModel('model.gguf');
const response = await model.generate('Hello!');
```

**Features:**
- Edge runtime compatible (Cloudflare, Vercel)
- Filesystem access
- Optional threading
- CLI tool included

### Native Tiny (`native-tiny`)

Minimal C implementation for embedded systems.

```c
llama_model* model = llama_load_model(data, size, 0);
llama_context* ctx = llama_create_context(model);
char* response = llama_generate(ctx, "Hello!", params);
```

**Features:**
- Single-file implementation
- No dependencies
- Memory-mapped models
- ARM/x86 optimized

## Reference Files

| Task | Reference |
|------|-----------|
| Understanding inference protocol | `references/formal-spec.md` |
| WASM web deployment | `references/target-profiles/wasm-web.md` |
| Node.js/Edge deployment | `references/target-profiles/wasm-node.md` |
| Model selection | `references/model-patterns/tiny-llms.md` |

## Common Workflows

### Offline Browser Chatbot

```bash
# Generate scaffold
python scripts/generate_tiny_llama.py \
    --target wasm-web \
    --model qwen2-0.5b \
    --output ./offline-chat

# Build
cd offline-chat
make

# Test locally
make serve
```

Deploy `index.html`, `llama-tiny.js`, `llama-tiny.wasm`, `worker.js`, `llama-client.js`, and model file.

### Cloudflare Worker LLM

```bash
python scripts/generate_tiny_llama.py \
    --target wasm-node \
    --model smollm-360m \
    --output ./cf-llm
```

Upload model to R2, deploy worker with WASM.

### CLI Chat Tool

```bash
python scripts/generate_tiny_llama.py \
    --target wasm-node \
    --model tinyllama \
    --output ./llama-cli

cd llama-cli
make
./cli.mjs model.gguf
```

## Size Budget

| Component | Tiny | Standard |
|-----------|------|----------|
| WASM binary | 50KB | 150KB |
| JS wrapper | 5KB | 15KB |
| **Total runtime** | **55KB** | **165KB** |
| Model (Q4_0) | 85-350MB | 670MB+ |

## Memory Requirements

```
Total = Model weights + KV cache + Overhead

KV cache ≈ 2 × n_layer × n_head_kv × head_dim × context × 2 bytes

Example (Qwen2-0.5B, 2K context):
  Weights: 350 MB
  KV cache: 2 × 24 × 2 × 64 × 2048 × 2 ≈ 25 MB
  Total: ~375 MB
```

## Chat Templates

Templates are auto-detected from model architecture:

| Model Family | Template | Format |
|--------------|----------|--------|
| Qwen, SmolLM | ChatML | `<\|im_start\|>user...` |
| LLaMA 2 | Llama2 | `[INST]...[/INST]` |
| LLaMA 3 | Llama3 | `<\|start_header_id\|>...` |
| Phi | Phi | `Instruct:...Output:` |

## Performance Tips

1. **Use smallest viable model** - Qwen2-0.5B is often sufficient
2. **Enable SIMD** - 2-3x faster, +50KB size
3. **Prefetch model** - Start download before user interaction
4. **Stream tokens** - Don't wait for full response
5. **Cache in IndexedDB** - Avoid re-downloading
6. **Limit context** - Shorter context = faster + less memory

## Templates

Pre-built templates in `templates/`:

- `wasm-web-worker/` - Browser chatbot with Web Worker
- `wasm-node/` - Node.js/Edge runtime
- `native-tiny/` - Minimal C implementation

## Integration with ggml-spec

This skill builds on `ggml-spec` for low-level tensor operations. Use together:

1. `ggml-spec` - Custom tensor operations, quantization
2. `llama-cpp-spec` - Complete inference engine, chat interface

```bash
# Custom GGML ops for specific hardware
python /home/ubuntu/skills/ggml-spec/scripts/generate_minimal.py \
    --arch arm64 --model llama --quants q4_k --output ./ggml-custom

# Tiny LLM using custom GGML
python scripts/generate_tiny_llama.py \
    --target native-tiny --model tinyllama --output ./llama-custom
```
