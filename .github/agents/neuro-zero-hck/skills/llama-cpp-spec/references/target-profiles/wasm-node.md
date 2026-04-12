# WASM Node.js Target Profile

Target: Server-side and CLI LLM inference using WASM for portability.

## Platform Characteristics

| Feature | Specification |
|---------|--------------|
| Runtime | Node.js 16+ / Deno / Bun |
| WASM version | MVP + SIMD + Threads |
| Memory model | SharedArrayBuffer (native) |
| Threading | Worker threads |
| Storage | Filesystem |
| Max memory | System RAM |

## Use Cases

1. **Portable CLI tools** - Single binary works on any OS
2. **Serverless functions** - Cold start optimization
3. **Edge computing** - Cloudflare Workers, Vercel Edge
4. **Electron apps** - Cross-platform desktop
5. **Development** - Same code as browser

## Build Configuration

### Emscripten for Node.js

```bash
# Node.js optimized build
emcc -O3 -s WASM=1 \
    -s ENVIRONMENT=node \
    -s NODERAWFS=1 \
    -s ALLOW_MEMORY_GROWTH=1 \
    -s MAXIMUM_MEMORY=4GB \
    -s EXPORTED_FUNCTIONS='["_malloc","_free","_init","_generate","_load_model"]' \
    -s EXPORTED_RUNTIME_METHODS='["ccall","cwrap","FS"]' \
    -s MODULARIZE=1 \
    -s EXPORT_ES6=1 \
    -msimd128 \
    -pthread -s PTHREAD_POOL_SIZE=4 \
    -o llama-node.mjs llama-tiny.c

# Without threads (simpler, Cloudflare compatible)
emcc -O3 -s WASM=1 \
    -s ENVIRONMENT=node \
    -s NODERAWFS=1 \
    -s ALLOW_MEMORY_GROWTH=1 \
    -s SINGLE_FILE=1 \
    -msimd128 \
    -o llama-node-single.mjs llama-tiny.c
```

## Node.js Bindings

### ES Module Wrapper

```javascript
// llama.mjs
import createModule from './llama-node.mjs';
import { readFile } from 'fs/promises';
import { createReadStream } from 'fs';

let Module = null;

export async function init() {
    Module = await createModule();
    return true;
}

export async function loadModel(path) {
    // Read model file
    const buffer = await readFile(path);
    
    // Allocate in WASM memory
    const ptr = Module._malloc(buffer.byteLength);
    Module.HEAPU8.set(buffer, ptr);
    
    // Initialize model
    const model = Module._init(ptr, buffer.byteLength);
    
    if (!model) {
        Module._free(ptr);
        throw new Error('Failed to load model');
    }
    
    return {
        ptr: model,
        size: buffer.byteLength,
        
        generate(prompt, params = {}) {
            return generate(model, prompt, params);
        },
        
        free() {
            Module._free_model(model);
        }
    };
}

export function generate(model, prompt, params = {}) {
    const {
        maxTokens = 256,
        temperature = 0.7,
        topP = 0.9,
        stream = false
    } = params;
    
    const promptPtr = Module.allocateUTF8(prompt);
    
    if (stream) {
        return generateStream(model, promptPtr, maxTokens, temperature, topP);
    }
    
    const resultPtr = Module._generate(model, promptPtr, maxTokens, temperature, topP);
    const result = Module.UTF8ToString(resultPtr);
    
    Module._free(promptPtr);
    Module._free(resultPtr);
    
    return result;
}

async function* generateStream(model, promptPtr, maxTokens, temperature, topP) {
    // Set up streaming callback
    const tokens = [];
    let done = false;
    
    Module._set_token_callback((ptr) => {
        tokens.push(Module.UTF8ToString(ptr));
    });
    
    Module._set_done_callback(() => {
        done = true;
    });
    
    // Start generation in background
    Module._generate_async(model, promptPtr, maxTokens, temperature, topP);
    
    // Yield tokens as they arrive
    while (!done) {
        while (tokens.length > 0) {
            yield tokens.shift();
        }
        await new Promise(r => setTimeout(r, 10));
    }
    
    // Yield remaining tokens
    while (tokens.length > 0) {
        yield tokens.shift();
    }
    
    Module._free(promptPtr);
}
```

### CLI Example

```javascript
#!/usr/bin/env node
// llama-cli.mjs
import { init, loadModel } from './llama.mjs';
import { createInterface } from 'readline';

async function main() {
    const modelPath = process.argv[2] || 'model.gguf';
    
    console.log('Loading model...');
    await init();
    const model = await loadModel(modelPath);
    console.log('Ready!\n');
    
    const rl = createInterface({
        input: process.stdin,
        output: process.stdout
    });
    
    const chat = async (prompt) => {
        process.stdout.write('Assistant: ');
        
        for await (const token of model.generate(prompt, { stream: true })) {
            process.stdout.write(token);
        }
        
        console.log('\n');
    };
    
    const ask = () => {
        rl.question('You: ', async (input) => {
            if (input.toLowerCase() === 'exit') {
                model.free();
                rl.close();
                return;
            }
            
            await chat(input);
            ask();
        });
    };
    
    ask();
}

main().catch(console.error);
```

## Edge Runtime Compatibility

### Cloudflare Workers

```javascript
// worker.js (Cloudflare)
import createModule from './llama-cf.mjs';

let llama = null;

export default {
    async fetch(request, env) {
        if (!llama) {
            llama = await createModule();
            // Load model from R2 or KV
            const model = await env.MODELS.get('tinyllama-q4_0', 'arrayBuffer');
            llama.loadModel(model);
        }
        
        const { prompt } = await request.json();
        const response = llama.generate(prompt, { maxTokens: 100 });
        
        return new Response(JSON.stringify({ response }), {
            headers: { 'Content-Type': 'application/json' }
        });
    }
};
```

### Vercel Edge Functions

```javascript
// api/chat.js
import { init, loadModel } from '@/lib/llama';

export const config = { runtime: 'edge' };

let model = null;

export default async function handler(req) {
    if (!model) {
        await init();
        model = await loadModel(process.env.MODEL_URL);
    }
    
    const { prompt } = await req.json();
    
    // Stream response
    const stream = new ReadableStream({
        async start(controller) {
            for await (const token of model.generate(prompt, { stream: true })) {
                controller.enqueue(new TextEncoder().encode(token));
            }
            controller.close();
        }
    });
    
    return new Response(stream, {
        headers: { 'Content-Type': 'text/plain; charset=utf-8' }
    });
}
```

## Performance Comparison

| Runtime | TinyLlama 1.1B Q4_0 | Notes |
|---------|---------------------|-------|
| Node.js WASM | 15-25 tok/s | With SIMD |
| Node.js WASM (threads) | 25-40 tok/s | 4 threads |
| Native (llama.cpp) | 40-60 tok/s | Reference |
| Cloudflare Workers | 5-10 tok/s | Cold start ~2s |
| Bun WASM | 20-30 tok/s | Faster startup |

## Package Structure

```
llama-tiny-node/
├── package.json
├── index.mjs           # Main entry
├── llama-node.mjs      # Emscripten glue
├── llama-node.wasm     # WASM binary
├── cli.mjs             # CLI tool
└── types.d.ts          # TypeScript definitions
```

### package.json

```json
{
    "name": "llama-tiny",
    "version": "1.0.0",
    "type": "module",
    "main": "index.mjs",
    "bin": {
        "llama": "cli.mjs"
    },
    "exports": {
        ".": "./index.mjs",
        "./wasm": "./llama-node.wasm"
    },
    "files": [
        "index.mjs",
        "llama-node.mjs",
        "llama-node.wasm",
        "cli.mjs",
        "types.d.ts"
    ]
}
```

### TypeScript Definitions

```typescript
// types.d.ts
export interface GenerateParams {
    maxTokens?: number;
    temperature?: number;
    topP?: number;
    topK?: number;
    stream?: boolean;
}

export interface Model {
    ptr: number;
    size: number;
    generate(prompt: string, params?: GenerateParams): string | AsyncGenerator<string>;
    free(): void;
}

export function init(): Promise<boolean>;
export function loadModel(path: string): Promise<Model>;
export function generate(model: Model, prompt: string, params?: GenerateParams): string;
```

## Memory Management

### Streaming Large Models

```javascript
// Stream model loading for large files
async function loadModelStreaming(path) {
    const stat = await fs.stat(path);
    const ptr = Module._malloc(stat.size);
    
    const stream = createReadStream(path);
    let offset = 0;
    
    for await (const chunk of stream) {
        Module.HEAPU8.set(chunk, ptr + offset);
        offset += chunk.length;
        
        // Report progress
        console.log(`Loading: ${Math.round(offset / stat.size * 100)}%`);
    }
    
    return Module._init(ptr, stat.size);
}
```

### Memory Limits

```javascript
// Check available memory before loading
import { freemem } from 'os';

function canLoadModel(modelSize) {
    const available = freemem();
    const required = modelSize * 1.5; // Model + KV cache + overhead
    return available > required;
}
```
