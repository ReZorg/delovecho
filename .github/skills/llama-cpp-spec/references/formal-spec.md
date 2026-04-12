# Tiny LLM Inference Formal Specification

This document defines the minimal protocol for LLM text generation, enabling implementations as small as 50-100KB for web workers and embedded systems.

## 1. Inference Protocol

### 1.1 Core Loop

```
Initialize:
    model ← load_gguf(path)
    kv_cache ← allocate(model.n_layer, model.n_ctx)
    pos ← 0

Generate(prompt, max_tokens):
    tokens ← tokenize(prompt)
    
    // Prefill phase: process all prompt tokens
    for token in tokens:
        logits ← forward(model, token, kv_cache, pos)
        pos += 1
    
    // Decode phase: generate new tokens
    output ← []
    for i in 0..max_tokens:
        next_token ← sample(logits, params)
        if next_token == EOS: break
        
        output.append(next_token)
        logits ← forward(model, next_token, kv_cache, pos)
        pos += 1
    
    return detokenize(output)
```

### 1.2 Forward Pass Contract

```c
// Minimal forward pass signature
float* forward(
    model_t* model,      // Model weights
    int32_t token,       // Single input token
    kv_cache_t* kv,      // Key-value cache
    int32_t pos          // Current position
);
// Returns: logits array of size n_vocab
```

### 1.3 Batch Processing (Optional)

For efficiency, process multiple tokens:

```c
float* forward_batch(
    model_t* model,
    int32_t* tokens,     // Array of tokens
    int32_t n_tokens,    // Number of tokens
    kv_cache_t* kv,
    int32_t pos_start
);
```

## 2. Tokenization Protocol

### 2.1 BPE Tokenizer Contract

```c
typedef struct {
    char** vocab;           // Token strings
    int32_t n_vocab;        // Vocabulary size
    float* scores;          // Token scores (for BPE merge priority)
    int32_t bos_token;      // Beginning of sequence
    int32_t eos_token;      // End of sequence
    int32_t pad_token;      // Padding token
} tokenizer_t;

// Encode text to tokens
int32_t tokenize(
    tokenizer_t* tok,
    const char* text,
    int32_t* tokens,        // Output buffer
    int32_t max_tokens,
    bool add_bos            // Add BOS token?
);

// Decode tokens to text
char* detokenize(
    tokenizer_t* tok,
    int32_t* tokens,
    int32_t n_tokens
);
```

### 2.2 Minimal BPE Algorithm

```python
def tokenize_bpe(text, vocab, merges):
    # 1. Convert to bytes/characters
    tokens = list(text.encode('utf-8'))
    
    # 2. Apply BPE merges greedily
    while True:
        # Find highest-priority merge
        best_pair = None
        best_score = -inf
        
        for i in range(len(tokens) - 1):
            pair = (tokens[i], tokens[i+1])
            if pair in merges and merges[pair] > best_score:
                best_pair = (i, pair)
                best_score = merges[pair]
        
        if best_pair is None:
            break
        
        # Apply merge
        i, (a, b) = best_pair
        tokens = tokens[:i] + [vocab[a + b]] + tokens[i+2:]
    
    return tokens
```

### 2.3 Special Tokens

| Token | Purpose | Typical ID |
|-------|---------|------------|
| BOS | Start of generation | 1 |
| EOS | End of generation | 2 |
| PAD | Padding for batching | 0 |
| UNK | Unknown token | 0 |

## 3. Sampling Protocol

### 3.1 Sampler Contract

```c
typedef struct {
    float temperature;      // 0.0 = greedy, 1.0 = neutral
    float top_p;           // Nucleus sampling threshold
    int32_t top_k;         // Top-K sampling
    float repeat_penalty;  // Repetition penalty
    uint64_t seed;         // RNG seed
} sampler_params_t;

int32_t sample(
    float* logits,
    int32_t n_vocab,
    sampler_params_t* params,
    int32_t* recent_tokens,  // For repetition penalty
    int32_t n_recent
);
```

### 3.2 Sampling Algorithms

**Greedy (temperature = 0):**
```c
int32_t sample_greedy(float* logits, int32_t n_vocab) {
    int32_t max_idx = 0;
    for (int i = 1; i < n_vocab; i++) {
        if (logits[i] > logits[max_idx]) max_idx = i;
    }
    return max_idx;
}
```

**Temperature Scaling:**
```c
void apply_temperature(float* logits, int32_t n_vocab, float temp) {
    if (temp == 0.0f) return;  // Greedy
    for (int i = 0; i < n_vocab; i++) {
        logits[i] /= temp;
    }
}
```

**Softmax:**
```c
void softmax(float* logits, int32_t n_vocab) {
    float max_val = logits[0];
    for (int i = 1; i < n_vocab; i++) {
        if (logits[i] > max_val) max_val = logits[i];
    }
    
    float sum = 0.0f;
    for (int i = 0; i < n_vocab; i++) {
        logits[i] = expf(logits[i] - max_val);
        sum += logits[i];
    }
    
    for (int i = 0; i < n_vocab; i++) {
        logits[i] /= sum;
    }
}
```

**Top-K Sampling:**
```c
int32_t sample_top_k(float* probs, int32_t n_vocab, int32_t k, rng_t* rng) {
    // 1. Find top-k indices
    // 2. Renormalize probabilities
    // 3. Sample from top-k
}
```

**Top-P (Nucleus) Sampling:**
```c
int32_t sample_top_p(float* probs, int32_t n_vocab, float p, rng_t* rng) {
    // 1. Sort by probability (descending)
    // 2. Find smallest set with cumsum >= p
    // 3. Renormalize and sample
}
```

**Repetition Penalty:**
```c
void apply_repetition_penalty(float* logits, int32_t* recent, int32_t n_recent, float penalty) {
    for (int i = 0; i < n_recent; i++) {
        int32_t token = recent[i];
        if (logits[token] > 0) {
            logits[token] /= penalty;
        } else {
            logits[token] *= penalty;
        }
    }
}
```

## 4. KV Cache Protocol

### 4.1 Cache Structure

```c
typedef struct {
    float* k;              // Key cache: [n_layer, n_head_kv, max_seq, head_dim]
    float* v;              // Value cache: [n_layer, n_head_kv, max_seq, head_dim]
    int32_t n_layer;
    int32_t n_head_kv;
    int32_t head_dim;
    int32_t max_seq;
    int32_t cur_seq;       // Current sequence length
} kv_cache_t;
```

### 4.2 Cache Operations

```c
// Allocate cache
kv_cache_t* kv_cache_alloc(int32_t n_layer, int32_t n_head_kv, 
                           int32_t head_dim, int32_t max_seq);

// Update cache with new K, V
void kv_cache_update(kv_cache_t* cache, int32_t layer,
                     float* k, float* v, int32_t pos);

// Get K, V for attention
void kv_cache_get(kv_cache_t* cache, int32_t layer,
                  float** k_out, float** v_out, int32_t* seq_len);

// Clear cache (new conversation)
void kv_cache_clear(kv_cache_t* cache);

// Shift cache (sliding window)
void kv_cache_shift(kv_cache_t* cache, int32_t shift);
```

### 4.3 Memory Layout

```
KV Cache Memory:
┌─────────────────────────────────────────────────────┐
│ Layer 0 K: [head_0][head_1]...[head_kv]             │
│ Layer 0 V: [head_0][head_1]...[head_kv]             │
├─────────────────────────────────────────────────────┤
│ Layer 1 K: ...                                      │
│ Layer 1 V: ...                                      │
├─────────────────────────────────────────────────────┤
│ ...                                                 │
└─────────────────────────────────────────────────────┘

Per head: [pos_0][pos_1]...[pos_max_seq]
Per position: [dim_0][dim_1]...[dim_head]
```

### 4.4 Memory Estimation

```
KV cache size = 2 × n_layer × n_head_kv × head_dim × max_seq × sizeof(float16)

Example (TinyLlama 1.1B, 2K context):
  = 2 × 22 × 4 × 64 × 2048 × 2
  = 46 MB
```

## 5. Chat Template Protocol

### 5.1 Template Format

```c
typedef struct {
    const char* system_prefix;    // Before system message
    const char* system_suffix;    // After system message
    const char* user_prefix;      // Before user message
    const char* user_suffix;      // After user message
    const char* assistant_prefix; // Before assistant response
    const char* assistant_suffix; // After assistant response
    bool add_generation_prompt;   // Add assistant_prefix for generation
} chat_template_t;
```

### 5.2 Common Templates

**ChatML (Qwen, many models):**
```
<|im_start|>system
{system}<|im_end|>
<|im_start|>user
{user}<|im_end|>
<|im_start|>assistant
{assistant}<|im_end|>
```

**Llama 2 Chat:**
```
[INST] <<SYS>>
{system}
<</SYS>>

{user} [/INST] {assistant} </s><s>[INST] {user} [/INST]
```

**Llama 3 / Llama 3.1:**
```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{assistant}<|eot_id|>
```

**Phi-3:**
```
<|system|>
{system}<|end|>
<|user|>
{user}<|end|>
<|assistant|>
{assistant}<|end|>
```

### 5.3 Apply Template

```c
char* apply_chat_template(
    chat_template_t* tmpl,
    message_t* messages,
    int32_t n_messages,
    bool add_generation_prompt
);
```

## 6. Model Loading Protocol

### 6.1 GGUF Minimal Reader

```c
typedef struct {
    char magic[4];         // "GGUF"
    uint32_t version;      // 3
    uint64_t n_tensors;
    uint64_t n_kv;
} gguf_header_t;

typedef struct {
    // Hyperparameters (from GGUF metadata)
    int32_t n_vocab;
    int32_t n_embd;
    int32_t n_layer;
    int32_t n_head;
    int32_t n_head_kv;
    int32_t n_ff;
    int32_t n_ctx;
    float rope_freq_base;
    float rope_freq_scale;
    
    // Weights (mmap'd or loaded)
    void* weights_data;
    size_t weights_size;
    
    // Tensor offsets
    tensor_info_t* tensors;
    int32_t n_tensors;
} model_t;
```

### 6.2 Required Metadata Keys

```
general.architecture     → "llama", "phi", "qwen2", etc.
general.name            → Model name
{arch}.context_length   → n_ctx
{arch}.embedding_length → n_embd
{arch}.block_count      → n_layer
{arch}.attention.head_count     → n_head
{arch}.attention.head_count_kv  → n_head_kv
{arch}.feed_forward_length      → n_ff
{arch}.rope.freq_base   → rope_freq_base
tokenizer.ggml.model    → "llama", "gpt2", etc.
tokenizer.ggml.tokens   → vocabulary
tokenizer.ggml.bos_token_id → BOS token
tokenizer.ggml.eos_token_id → EOS token
```

## 7. Streaming Protocol

### 7.1 Callback Interface

```c
typedef void (*token_callback_t)(
    int32_t token,
    const char* text,
    void* user_data
);

void generate_streaming(
    model_t* model,
    const char* prompt,
    sampler_params_t* params,
    token_callback_t callback,
    void* user_data
);
```

### 7.2 Web Worker Message Protocol

```typescript
// Worker → Main thread
interface TokenMessage {
    type: 'token';
    token: number;
    text: string;
}

interface DoneMessage {
    type: 'done';
    total_tokens: number;
    tokens_per_second: number;
}

interface ErrorMessage {
    type: 'error';
    message: string;
}

// Main thread → Worker
interface GenerateMessage {
    type: 'generate';
    prompt: string;
    max_tokens: number;
    temperature: number;
    top_p: number;
}

interface LoadMessage {
    type: 'load';
    model_url: string;
}
```

## 8. Size Budget

### 8.1 Target Sizes

| Component | Tiny | Small | Full |
|-----------|------|-------|------|
| WASM binary | 50KB | 150KB | 500KB |
| JS wrapper | 5KB | 10KB | 30KB |
| Total runtime | 55KB | 160KB | 530KB |

### 8.2 Size Reduction Strategies

1. **Single quantization type** - Only Q4_0 or Q8_0
2. **No SIMD** - Scalar fallback only (or WASM SIMD only)
3. **Fixed architecture** - LLaMA-only, no architecture switching
4. **Minimal sampling** - Greedy + temperature only
5. **No grammar** - Remove grammar-constrained generation
6. **Static allocation** - No dynamic memory after init

## 9. Performance Targets

### 9.1 Benchmarks

| Model | Platform | Target tok/s |
|-------|----------|--------------|
| TinyLlama 1.1B Q4_0 | WASM (Chrome) | 5-10 |
| Phi-2 2.7B Q4_0 | WASM (Chrome) | 2-5 |
| Qwen2-0.5B Q4_0 | WASM (Chrome) | 15-25 |
| TinyLlama 1.1B Q4_0 | Node.js WASM | 10-20 |
| TinyLlama 1.1B Q4_0 | Native ARM64 | 30-50 |

### 9.2 Memory Targets

| Model | Weights | KV Cache (2K) | Total |
|-------|---------|---------------|-------|
| Qwen2-0.5B Q4_0 | 350MB | 20MB | 370MB |
| TinyLlama 1.1B Q4_0 | 670MB | 46MB | 716MB |
| Phi-2 2.7B Q4_0 | 1.6GB | 100MB | 1.7GB |
