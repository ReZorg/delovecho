# Tiny LLM Model Patterns

Models suitable for browser/edge inference with WASM.

## Model Selection Guide

| Model | Params | Q4_0 Size | WASM tok/s | Quality | Best For |
|-------|--------|-----------|------------|---------|----------|
| Qwen2-0.5B | 0.5B | 350MB | 15-25 | Good | Fastest, simple tasks |
| TinyLlama-1.1B | 1.1B | 670MB | 8-15 | Good | Balanced |
| Phi-2 | 2.7B | 1.6GB | 3-6 | Excellent | Quality-critical |
| Gemma-2B | 2B | 1.2GB | 4-8 | Very Good | Instruction following |
| StableLM-2-1.6B | 1.6B | 1GB | 5-10 | Good | Chat |

## Qwen2-0.5B

**Recommended for:** Fastest inference, simple Q&A, classification

### Architecture

```yaml
architecture: qwen2
n_vocab: 151936
n_embd: 896
n_layer: 24
n_head: 14
n_head_kv: 2  # GQA
n_ff: 4864
n_ctx: 32768
rope_freq_base: 1000000
```

### Chat Template

```
<|im_start|>system
{system}<|im_end|>
<|im_start|>user
{user}<|im_end|>
<|im_start|>assistant
```

### Special Tokens

```
BOS: 151643 (<|endoftext|>)
EOS: 151645 (<|im_end|>)
PAD: 151643
```

### Memory Requirements

| Context | KV Cache | Total (Q4_0) |
|---------|----------|--------------|
| 512 | 5MB | 355MB |
| 2048 | 20MB | 370MB |
| 8192 | 80MB | 430MB |

### GGUF Download

```bash
# Hugging Face
wget https://huggingface.co/Qwen/Qwen2-0.5B-Instruct-GGUF/resolve/main/qwen2-0_5b-instruct-q4_0.gguf
```

---

## TinyLlama-1.1B

**Recommended for:** Balanced speed/quality, general chat

### Architecture

```yaml
architecture: llama
n_vocab: 32000
n_embd: 2048
n_layer: 22
n_head: 32
n_head_kv: 4  # GQA
n_ff: 5632
n_ctx: 2048
rope_freq_base: 10000
```

### Chat Template (ChatML)

```
<|system|>
{system}</s>
<|user|>
{user}</s>
<|assistant|>
```

### Special Tokens

```
BOS: 1 (<s>)
EOS: 2 (</s>)
```

### Memory Requirements

| Context | KV Cache | Total (Q4_0) |
|---------|----------|--------------|
| 512 | 11MB | 681MB |
| 2048 | 46MB | 716MB |

### GGUF Download

```bash
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_0.gguf
```

---

## Phi-2

**Recommended for:** Best quality, complex reasoning

### Architecture

```yaml
architecture: phi2
n_vocab: 51200
n_embd: 2560
n_layer: 32
n_head: 32
n_head_kv: 32  # Full attention
n_ff: 10240
n_ctx: 2048
rope_freq_base: 10000
partial_rotary_factor: 0.4  # Only 40% of dims rotated
```

### Differences from LLaMA

- Uses **partial rotary embeddings** (40% of head_dim)
- Uses **LayerNorm** instead of RMSNorm
- Uses **GELU** activation instead of SiLU
- **No** GQA (full KV heads)

### Chat Template

```
Instruct: {user}
Output: {assistant}
```

### Memory Requirements

| Context | KV Cache | Total (Q4_0) |
|---------|----------|--------------|
| 512 | 40MB | 1.64GB |
| 2048 | 160MB | 1.76GB |

### GGUF Download

```bash
wget https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_0.gguf
```

---

## SmolLM-135M / 360M

**Recommended for:** Ultra-tiny, IoT, extreme constraints

### Architecture (360M)

```yaml
architecture: llama
n_vocab: 49152
n_embd: 960
n_layer: 32
n_head: 15
n_head_kv: 5  # GQA
n_ff: 2560
n_ctx: 2048
```

### Memory Requirements

| Model | Q4_0 Size | KV Cache (2K) | Total |
|-------|-----------|---------------|-------|
| 135M | 85MB | 15MB | 100MB |
| 360M | 220MB | 30MB | 250MB |

### GGUF Download

```bash
wget https://huggingface.co/HuggingFaceTB/SmolLM-360M-Instruct-GGUF/resolve/main/smollm-360m-instruct-q4_0.gguf
```

---

## Implementation Differences

### Operations by Architecture

| Operation | LLaMA/Qwen | Phi-2 | Notes |
|-----------|------------|-------|-------|
| RMS_NORM | ✓ | ✗ | Phi uses LayerNorm |
| NORM | ✗ | ✓ | With bias |
| SILU | ✓ | ✗ | |
| GELU | ✗ | ✓ | |
| ROPE (full) | ✓ | ✗ | |
| ROPE (partial) | ✗ | ✓ | 40% of dims |
| GQA | ✓ | ✗ | Phi has full KV |

### Minimal Op Sets

**LLaMA-family (Qwen, TinyLlama, SmolLM):**
```
GET_ROWS, MUL_MAT, RMS_NORM, ROPE, SOFT_MAX, SILU, ADD, MUL
```

**Phi-family:**
```
GET_ROWS, MUL_MAT, NORM, ROPE_PARTIAL, SOFT_MAX, GELU, ADD, MUL
```

---

## Quantization Recommendations

### By Use Case

| Use Case | Quantization | Notes |
|----------|--------------|-------|
| Fastest inference | Q4_0 | Simplest dequant |
| Best quality | Q5_K_M | Good balance |
| Minimum size | Q2_K | Quality loss |
| Development | Q8_0 | Near-F16 quality |

### Size Comparison (TinyLlama 1.1B)

| Quant | Size | Relative |
|-------|------|----------|
| F16 | 2.2GB | 100% |
| Q8_0 | 1.2GB | 55% |
| Q5_K_M | 800MB | 36% |
| Q4_K_M | 670MB | 30% |
| Q4_0 | 630MB | 29% |
| Q2_K | 450MB | 20% |

---

## Chat Template Implementations

### JavaScript Template Engine

```javascript
const TEMPLATES = {
    chatml: {
        system: '<|im_start|>system\n{content}<|im_end|>\n',
        user: '<|im_start|>user\n{content}<|im_end|>\n',
        assistant: '<|im_start|>assistant\n{content}<|im_end|>\n',
        generation: '<|im_start|>assistant\n'
    },
    llama2: {
        system: '<<SYS>>\n{content}\n<</SYS>>\n\n',
        user: '[INST] {content} [/INST]',
        assistant: ' {content} </s><s>',
        generation: ''
    },
    phi: {
        system: '',
        user: 'Instruct: {content}\n',
        assistant: 'Output: {content}\n',
        generation: 'Output:'
    },
    alpaca: {
        system: '{content}\n\n',
        user: '### Instruction:\n{content}\n\n',
        assistant: '### Response:\n{content}\n\n',
        generation: '### Response:\n'
    }
};

function applyTemplate(messages, templateName) {
    const tmpl = TEMPLATES[templateName];
    let result = '';
    
    for (const msg of messages) {
        const format = tmpl[msg.role];
        result += format.replace('{content}', msg.content);
    }
    
    result += tmpl.generation;
    return result;
}
```

---

## Model Selection Flowchart

```
Start
  │
  ├─ Memory < 400MB? ──────────────────► Qwen2-0.5B or SmolLM-360M
  │
  ├─ Need best quality? ───────────────► Phi-2 (if memory allows)
  │
  ├─ Need long context (>4K)? ─────────► Qwen2-0.5B (32K native)
  │
  ├─ General chat, balanced? ──────────► TinyLlama-1.1B
  │
  └─ Extreme constraints (<100MB)? ────► SmolLM-135M
```

---

## Benchmark Results (WASM Chrome)

| Model | Q4_0 | Prompt tok/s | Gen tok/s | First token |
|-------|------|--------------|-----------|-------------|
| SmolLM-135M | 85MB | 150 | 45 | 200ms |
| SmolLM-360M | 220MB | 80 | 25 | 400ms |
| Qwen2-0.5B | 350MB | 50 | 18 | 600ms |
| TinyLlama-1.1B | 670MB | 25 | 10 | 1.2s |
| Phi-2 | 1.6GB | 10 | 4 | 3s |

*Tested on M1 MacBook Air, Chrome 120*
