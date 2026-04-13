# Whisper Model Pattern

OpenAI Whisper: Encoder-decoder transformer for speech recognition.

## Architecture Overview

```
Audio → Mel Spectrogram → Encoder → Cross-Attention → Decoder → Text Tokens

Encoder (Audio):
    Conv1D → Conv1D → Positional Emb → N × Encoder Block → Encoder Output

Decoder (Text):
    Token Emb + Pos Emb → N × Decoder Block → Output Projection → Logits

Encoder Block:
    x → LayerNorm → Self-Attention → + → LayerNorm → FFN → +

Decoder Block:
    x → LayerNorm → Causal Self-Attention → +
      → LayerNorm → Cross-Attention (to encoder) → +
      → LayerNorm → FFN → +
```

## Required Operations

### Minimal Op Set (15 operations)

| Operation | Usage | Priority |
|-----------|-------|----------|
| CONV_1D | Audio feature extraction | Critical |
| GET_ROWS | Token embedding | Critical |
| MUL_MAT | All projections | Critical |
| NORM | Layer normalization | Critical |
| SOFT_MAX | Attention scores | Critical |
| GELU | FFN activation | Critical |
| ADD | Residual, positional emb | Critical |
| MUL | Attention scaling | Critical |
| RESHAPE | Head splitting | Required |
| PERMUTE | Dimension reorder | Required |
| TRANSPOSE | Attention transpose | Required |
| CONT | Contiguous for matmul | Required |
| DIAG_MASK_INF | Causal mask (decoder) | Required |
| PAD | Audio padding | Required |
| SCALE | Attention scaling | Required |

### Key Differences from LLaMA

| Aspect | LLaMA | Whisper |
|--------|-------|---------|
| Normalization | RMS Norm | Layer Norm |
| Activation | SiLU | GELU |
| Position | RoPE | Sinusoidal + Learned |
| Architecture | Decoder-only | Encoder-Decoder |
| Attention | Causal | Encoder: bidirectional, Decoder: causal + cross |

## Tensor Shapes

For Whisper with:
- `n_mels`: Mel spectrogram bins (80)
- `n_audio_ctx`: Audio context length (1500)
- `n_text_ctx`: Text context length (448)
- `n_audio_state`: Encoder hidden size
- `n_text_state`: Decoder hidden size
- `n_audio_head`: Encoder attention heads
- `n_text_head`: Decoder attention heads
- `n_audio_layer`: Encoder layers
- `n_text_layer`: Decoder layers

### Weight Tensors

```
# Encoder
encoder.conv1.weight : [n_audio_state, n_mels, 3]
encoder.conv1.bias   : [n_audio_state]
encoder.conv2.weight : [n_audio_state, n_audio_state, 3]
encoder.conv2.bias   : [n_audio_state]
encoder.positional_embedding : [n_audio_ctx, n_audio_state]

encoder.blocks.{i}.attn_ln.weight : [n_audio_state]
encoder.blocks.{i}.attn_ln.bias   : [n_audio_state]
encoder.blocks.{i}.attn.query.weight : [n_audio_state, n_audio_state]
encoder.blocks.{i}.attn.query.bias   : [n_audio_state]
encoder.blocks.{i}.attn.key.weight   : [n_audio_state, n_audio_state]
encoder.blocks.{i}.attn.value.weight : [n_audio_state, n_audio_state]
encoder.blocks.{i}.attn.value.bias   : [n_audio_state]
encoder.blocks.{i}.attn.out.weight   : [n_audio_state, n_audio_state]
encoder.blocks.{i}.attn.out.bias     : [n_audio_state]
encoder.blocks.{i}.mlp_ln.weight : [n_audio_state]
encoder.blocks.{i}.mlp_ln.bias   : [n_audio_state]
encoder.blocks.{i}.mlp.0.weight  : [n_audio_state * 4, n_audio_state]
encoder.blocks.{i}.mlp.0.bias    : [n_audio_state * 4]
encoder.blocks.{i}.mlp.2.weight  : [n_audio_state, n_audio_state * 4]
encoder.blocks.{i}.mlp.2.bias    : [n_audio_state]

encoder.ln_post.weight : [n_audio_state]
encoder.ln_post.bias   : [n_audio_state]

# Decoder
decoder.token_embedding.weight    : [n_vocab, n_text_state]
decoder.positional_embedding      : [n_text_ctx, n_text_state]

decoder.blocks.{i}.attn_ln.weight : [n_text_state]
decoder.blocks.{i}.attn.query/key/value/out : ...
decoder.blocks.{i}.cross_attn_ln.weight : [n_text_state]
decoder.blocks.{i}.cross_attn.query/key/value/out : ...
decoder.blocks.{i}.mlp_ln/mlp : ...

decoder.ln.weight : [n_text_state]
decoder.ln.bias   : [n_text_state]
```

## Forward Pass Pseudocode

### Encoder

```python
def whisper_encode(mel, weights):
    # mel: [n_mels, n_frames]
    
    # Convolutional feature extraction
    x = CONV_1D(mel, weights.conv1, stride=1, padding=1)
    x = GELU(x)
    x = CONV_1D(x, weights.conv2, stride=2, padding=1)
    x = GELU(x)
    
    # x: [n_audio_state, n_audio_ctx]
    x = TRANSPOSE(x)  # [n_audio_ctx, n_audio_state]
    x = ADD(x, weights.positional_embedding)
    
    for layer in range(n_audio_layer):
        w = weights.encoder.blocks[layer]
        
        # Self-attention (bidirectional, no causal mask)
        x_norm = NORM(x, w.attn_ln)
        Q = MUL_MAT(x_norm, w.attn.query) + w.attn.query.bias
        K = MUL_MAT(x_norm, w.attn.key)  # No bias for K
        V = MUL_MAT(x_norm, w.attn.value) + w.attn.value.bias
        
        attn = attention(Q, K, V, mask=None)  # No causal mask
        attn = MUL_MAT(attn, w.attn.out) + w.attn.out.bias
        x = ADD(x, attn)
        
        # FFN
        x_norm = NORM(x, w.mlp_ln)
        ffn = MUL_MAT(x_norm, w.mlp.0) + w.mlp.0.bias
        ffn = GELU(ffn)
        ffn = MUL_MAT(ffn, w.mlp.2) + w.mlp.2.bias
        x = ADD(x, ffn)
    
    x = NORM(x, weights.encoder.ln_post)
    return x  # Encoder output for cross-attention
```

### Decoder

```python
def whisper_decode(tokens, encoder_output, weights, kv_cache, pos):
    # Token + positional embedding
    x = GET_ROWS(weights.decoder.token_embedding, tokens)
    x = ADD(x, weights.decoder.positional_embedding[pos:pos+len(tokens)])
    
    for layer in range(n_text_layer):
        w = weights.decoder.blocks[layer]
        
        # Causal self-attention
        x_norm = NORM(x, w.attn_ln)
        Q = MUL_MAT(x_norm, w.attn.query) + w.attn.query.bias
        K = MUL_MAT(x_norm, w.attn.key)
        V = MUL_MAT(x_norm, w.attn.value) + w.attn.value.bias
        
        # Update KV cache
        kv_cache.self_k[layer] = CONCAT(kv_cache.self_k[layer], K)
        kv_cache.self_v[layer] = CONCAT(kv_cache.self_v[layer], V)
        
        attn = attention(Q, kv_cache.self_k[layer], kv_cache.self_v[layer], 
                        mask=causal_mask)
        attn = MUL_MAT(attn, w.attn.out) + w.attn.out.bias
        x = ADD(x, attn)
        
        # Cross-attention to encoder
        x_norm = NORM(x, w.cross_attn_ln)
        Q = MUL_MAT(x_norm, w.cross_attn.query) + w.cross_attn.query.bias
        
        # K, V from encoder (cached after first token)
        if kv_cache.cross_k[layer] is None:
            K = MUL_MAT(encoder_output, w.cross_attn.key)
            V = MUL_MAT(encoder_output, w.cross_attn.value) + w.cross_attn.value.bias
            kv_cache.cross_k[layer] = K
            kv_cache.cross_v[layer] = V
        
        attn = attention(Q, kv_cache.cross_k[layer], kv_cache.cross_v[layer],
                        mask=None)  # No mask for cross-attention
        attn = MUL_MAT(attn, w.cross_attn.out) + w.cross_attn.out.bias
        x = ADD(x, attn)
        
        # FFN
        x_norm = NORM(x, w.mlp_ln)
        ffn = MUL_MAT(x_norm, w.mlp.0) + w.mlp.0.bias
        ffn = GELU(ffn)
        ffn = MUL_MAT(ffn, w.mlp.2) + w.mlp.2.bias
        x = ADD(x, ffn)
    
    x = NORM(x, weights.decoder.ln)
    logits = MUL_MAT(x, TRANSPOSE(weights.decoder.token_embedding))
    return logits
```

## Model Sizes

| Model | Params | Encoder | Decoder | n_mels | n_audio_ctx |
|-------|--------|---------|---------|--------|-------------|
| tiny | 39M | 4 layers | 4 layers | 80 | 1500 |
| base | 74M | 6 layers | 6 layers | 80 | 1500 |
| small | 244M | 12 layers | 12 layers | 80 | 1500 |
| medium | 769M | 24 layers | 24 layers | 80 | 1500 |
| large | 1.5B | 32 layers | 32 layers | 80 | 1500 |

## GGUF Metadata Keys

```
general.architecture = "whisper"
general.name = "Whisper Large v3"

whisper.encoder.n_layer = 32
whisper.encoder.n_state = 1280
whisper.encoder.n_head = 20
whisper.decoder.n_layer = 32
whisper.decoder.n_state = 1280
whisper.decoder.n_head = 20
whisper.n_mels = 80
whisper.n_audio_ctx = 1500
whisper.n_text_ctx = 448
whisper.n_vocab = 51865
```

## Audio Preprocessing

```python
def audio_to_mel(audio, n_mels=80, n_fft=400, hop_length=160, sample_rate=16000):
    # 1. Resample to 16kHz if needed
    # 2. Pad/trim to 30 seconds (480000 samples)
    # 3. STFT with n_fft=400, hop_length=160
    # 4. Mel filterbank (80 bins)
    # 5. Log mel spectrogram
    # 6. Normalize
    
    # Output: [80, 3000] for 30s audio
    return mel_spectrogram
```

## Minimal Implementation Checklist

```
[ ] Mel spectrogram preprocessing (can be external)
[ ] Conv1D layers (2 layers)
[ ] Layer normalization (with bias)
[ ] GELU activation
[ ] Encoder self-attention (bidirectional)
[ ] Decoder causal self-attention
[ ] Decoder cross-attention
[ ] Positional embeddings (sinusoidal + learned)
[ ] Token embedding lookup
[ ] KV cache (self + cross attention)
[ ] Output projection
```

## Performance Notes

| Component | % Time | Notes |
|-----------|--------|-------|
| Encoder | 20-30% | Run once per audio |
| Decoder self-attn | 30-40% | Per token |
| Decoder cross-attn | 20-30% | Per token |
| FFN | 10-20% | Per token |

**Optimization opportunities:**
- Cache encoder output and cross-attention KV
- Batch decode multiple beams
- Fuse attention operations
