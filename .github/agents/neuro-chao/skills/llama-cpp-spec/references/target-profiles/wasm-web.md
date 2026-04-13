# WASM Web Worker Target Profile

Target: Browser-based LLM inference in Web Workers for offline-capable chatbots.

## Platform Characteristics

| Feature | Specification |
|---------|--------------|
| Runtime | Browser (Chrome, Firefox, Safari, Edge) |
| WASM version | MVP + SIMD (optional) |
| Memory model | SharedArrayBuffer (if available) |
| Threading | Web Workers (single-threaded WASM) |
| Storage | IndexedDB, Cache API |
| Max memory | ~2-4GB (browser dependent) |

## Build Configuration

### Emscripten Flags

```bash
# Minimal build (50KB target)
emcc -O3 -s WASM=1 \
    -s EXPORTED_FUNCTIONS='["_malloc","_free","_init","_generate"]' \
    -s EXPORTED_RUNTIME_METHODS='["ccall","cwrap","UTF8ToString"]' \
    -s ALLOW_MEMORY_GROWTH=1 \
    -s MAXIMUM_MEMORY=2GB \
    -s STACK_SIZE=1MB \
    -s TOTAL_MEMORY=64MB \
    -s MODULARIZE=1 \
    -s EXPORT_ES6=1 \
    -s SINGLE_FILE=0 \
    --no-entry \
    -o llama-tiny.js llama-tiny.c

# With SIMD (150KB target, faster)
emcc -O3 -s WASM=1 -msimd128 \
    -s EXPORTED_FUNCTIONS='["_malloc","_free","_init","_generate"]' \
    ...
```

### CMake Configuration

```cmake
set(CMAKE_TOOLCHAIN_FILE $ENV{EMSDK}/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")

# Disable features for size
set(LLAMA_NATIVE OFF)
set(LLAMA_AVX OFF)
set(LLAMA_AVX2 OFF)
set(LLAMA_F16C OFF)
set(LLAMA_FMA OFF)
```

## JavaScript Bindings

### Module Wrapper

```javascript
// llama-worker.js
let Module = null;
let model = null;

// Initialize WASM module
async function initModule() {
    Module = await createLlamaModule();
    return true;
}

// Load model from URL or ArrayBuffer
async function loadModel(source) {
    let buffer;
    if (typeof source === 'string') {
        const response = await fetch(source);
        buffer = await response.arrayBuffer();
    } else {
        buffer = source;
    }
    
    // Allocate WASM memory and copy model
    const ptr = Module._malloc(buffer.byteLength);
    Module.HEAPU8.set(new Uint8Array(buffer), ptr);
    
    // Initialize model
    model = Module._init(ptr, buffer.byteLength);
    
    if (!model) {
        Module._free(ptr);
        throw new Error('Failed to load model');
    }
    
    return { success: true, size: buffer.byteLength };
}

// Generate text
function* generate(prompt, params = {}) {
    const {
        maxTokens = 256,
        temperature = 0.7,
        topP = 0.9,
        topK = 40
    } = params;
    
    // Encode prompt
    const promptPtr = Module.allocateUTF8(prompt);
    
    // Set up callback for streaming
    const tokens = [];
    Module._set_callback((tokenPtr) => {
        const text = Module.UTF8ToString(tokenPtr);
        tokens.push(text);
    });
    
    // Generate
    Module._generate(model, promptPtr, maxTokens, temperature, topP, topK);
    
    Module._free(promptPtr);
    
    return tokens.join('');
}
```

### Web Worker Interface

```javascript
// worker.js
importScripts('llama-tiny.js');

let llama = null;

self.onmessage = async (e) => {
    const { type, data, id } = e.data;
    
    try {
        switch (type) {
            case 'init':
                await initModule();
                self.postMessage({ type: 'ready', id });
                break;
                
            case 'load':
                const result = await loadModel(data.url);
                self.postMessage({ type: 'loaded', id, data: result });
                break;
                
            case 'generate':
                // Stream tokens back to main thread
                for await (const token of generate(data.prompt, data.params)) {
                    self.postMessage({ type: 'token', id, data: token });
                }
                self.postMessage({ type: 'done', id });
                break;
                
            case 'abort':
                Module._abort_generation();
                break;
        }
    } catch (error) {
        self.postMessage({ type: 'error', id, data: error.message });
    }
};
```

### Main Thread API

```javascript
// llama-client.js
export class LlamaClient {
    constructor() {
        this.worker = new Worker('worker.js');
        this.callbacks = new Map();
        this.nextId = 0;
        
        this.worker.onmessage = (e) => {
            const { type, id, data } = e.data;
            const callback = this.callbacks.get(id);
            if (callback) callback(type, data);
        };
    }
    
    async init() {
        return this._call('init');
    }
    
    async loadModel(url) {
        return this._call('load', { url });
    }
    
    async *generate(prompt, params = {}) {
        const id = this.nextId++;
        
        return new Promise((resolve, reject) => {
            const tokens = [];
            
            this.callbacks.set(id, (type, data) => {
                if (type === 'token') {
                    tokens.push(data);
                    // Optionally yield for streaming
                } else if (type === 'done') {
                    this.callbacks.delete(id);
                    resolve(tokens.join(''));
                } else if (type === 'error') {
                    this.callbacks.delete(id);
                    reject(new Error(data));
                }
            });
            
            this.worker.postMessage({ type: 'generate', id, data: { prompt, params } });
        });
    }
    
    abort() {
        this.worker.postMessage({ type: 'abort' });
    }
    
    _call(type, data = {}) {
        const id = this.nextId++;
        return new Promise((resolve, reject) => {
            this.callbacks.set(id, (respType, respData) => {
                this.callbacks.delete(id);
                if (respType === 'error') reject(new Error(respData));
                else resolve(respData);
            });
            this.worker.postMessage({ type, id, data });
        });
    }
}
```

## Model Storage

### IndexedDB Caching

```javascript
const DB_NAME = 'llama-models';
const STORE_NAME = 'models';

async function cacheModel(name, buffer) {
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    await tx.store.put(buffer, name);
}

async function getCachedModel(name) {
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, 'readonly');
    return tx.store.get(name);
}

async function loadModelWithCache(url, name) {
    // Try cache first
    let buffer = await getCachedModel(name);
    
    if (!buffer) {
        // Download and cache
        const response = await fetch(url);
        buffer = await response.arrayBuffer();
        await cacheModel(name, buffer);
    }
    
    return buffer;
}
```

### Service Worker for Offline

```javascript
// sw.js
const CACHE_NAME = 'llama-v1';
const MODEL_CACHE = 'llama-models-v1';

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // Cache model files separately
    if (url.pathname.endsWith('.gguf')) {
        event.respondWith(
            caches.open(MODEL_CACHE).then(cache =>
                cache.match(event.request).then(response =>
                    response || fetch(event.request).then(networkResponse => {
                        cache.put(event.request, networkResponse.clone());
                        return networkResponse;
                    })
                )
            )
        );
    }
});
```

## Size Optimization

### Dead Code Elimination

```c
// Only include needed operations
#define GGML_OP_MUL_MAT 1
#define GGML_OP_RMS_NORM 1
#define GGML_OP_ROPE 1
#define GGML_OP_SOFT_MAX 1
#define GGML_OP_SILU 1
// ... minimal set

// Exclude unused
#define GGML_NO_METAL 1
#define GGML_NO_CUDA 1
#define GGML_NO_VULKAN 1
#define GGML_NO_BLAS 1
```

### Quantization-Only Build

```c
// Only Q4_0 support
#define GGML_TYPE_Q4_0 1
// Disable all others
#define GGML_NO_Q4_1 1
#define GGML_NO_Q5_0 1
// ...
```

## Browser Compatibility

| Browser | WASM | SIMD | SharedArrayBuffer | Max Memory |
|---------|------|------|-------------------|------------|
| Chrome 90+ | ✓ | ✓ | ✓ | 4GB |
| Firefox 89+ | ✓ | ✓ | ✓ | 4GB |
| Safari 15+ | ✓ | ✓ | ✓* | 2GB |
| Edge 90+ | ✓ | ✓ | ✓ | 4GB |

*Safari requires specific headers for SharedArrayBuffer

### Required Headers (for SharedArrayBuffer)

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

## Performance Tips

1. **Use SIMD** - 2-3x faster, +100KB size
2. **Prefetch model** - Start download before user interaction
3. **Stream tokens** - Don't wait for full response
4. **Reuse context** - Keep KV cache between messages
5. **Quantize aggressively** - Q4_0 is fastest in WASM

## Example HTML

```html
<!DOCTYPE html>
<html>
<head>
    <title>Tiny LLM Chat</title>
    <script type="module">
        import { LlamaClient } from './llama-client.js';
        
        const llama = new LlamaClient();
        
        async function init() {
            await llama.init();
            await llama.loadModel('models/tinyllama-1.1b-q4_0.gguf');
            document.getElementById('status').textContent = 'Ready!';
        }
        
        async function chat() {
            const input = document.getElementById('input').value;
            const output = document.getElementById('output');
            
            output.textContent = 'Thinking...';
            const response = await llama.generate(input, { maxTokens: 256 });
            output.textContent = response;
        }
        
        init();
    </script>
</head>
<body>
    <div id="status">Loading...</div>
    <input id="input" type="text" placeholder="Ask something...">
    <button onclick="chat()">Send</button>
    <div id="output"></div>
</body>
</html>
```
