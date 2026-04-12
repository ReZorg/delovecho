# WASM Web Worker Template

Minimal LLM inference engine for browser web workers.

## Files

```
wasm-web-worker/
├── README.md           # This file
├── llama-tiny.c        # Minimal inference engine
├── llama-tiny.h        # Public API
├── Makefile            # Emscripten build
├── worker.js           # Web Worker wrapper
├── llama-client.js     # Main thread API
├── index.html          # Demo page
└── chat.css            # Minimal styling
```

## Build

```bash
# Requires Emscripten SDK
source /path/to/emsdk/emsdk_env.sh

# Build WASM
make

# Output: llama-tiny.js, llama-tiny.wasm
```

## Usage

```html
<script type="module">
import { LlamaChat } from './llama-client.js';

const chat = new LlamaChat();
await chat.init();
await chat.loadModel('models/qwen2-0.5b-q4_0.gguf');

const response = await chat.send('Hello!');
console.log(response);
</script>
```

## API

```javascript
// Initialize
const chat = new LlamaChat();
await chat.init();

// Load model (URL or ArrayBuffer)
await chat.loadModel(urlOrBuffer);

// Generate (blocking)
const response = await chat.send(prompt, { maxTokens: 256 });

// Generate (streaming)
for await (const token of chat.stream(prompt)) {
    process.stdout.write(token);
}

// Clear conversation
chat.clear();

// Abort generation
chat.abort();
```

## Configuration

```javascript
const chat = new LlamaChat({
    // Default generation parameters
    temperature: 0.7,
    topP: 0.9,
    topK: 40,
    maxTokens: 256,
    
    // System prompt
    systemPrompt: 'You are a helpful assistant.',
    
    // Chat template (auto-detected from model)
    template: 'chatml'  // or 'llama2', 'phi', 'alpaca'
});
```

## Supported Models

| Model | Size | Recommended |
|-------|------|-------------|
| Qwen2-0.5B-Q4_0 | 350MB | ✓ Fastest |
| SmolLM-360M-Q4_0 | 220MB | ✓ Tiny |
| TinyLlama-1.1B-Q4_0 | 670MB | ✓ Balanced |
| Phi-2-Q4_0 | 1.6GB | Best quality |

## Browser Support

- Chrome 90+
- Firefox 89+
- Safari 15+
- Edge 90+

## Size

- WASM binary: ~80KB (gzipped)
- JS wrapper: ~5KB
- Total runtime: ~85KB
