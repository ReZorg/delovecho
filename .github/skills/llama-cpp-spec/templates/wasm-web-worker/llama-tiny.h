/**
 * llama-tiny.h - Minimal LLM inference for WASM
 * 
 * Single-header API for tiny LLM inference engines.
 * Designed for browser web workers and edge computing.
 */

#ifndef LLAMA_TINY_H
#define LLAMA_TINY_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// Types
// ============================================================================

typedef int32_t llama_token;

typedef struct llama_model llama_model;
typedef struct llama_context llama_context;

// Token callback for streaming
typedef void (*llama_token_callback)(const char* text, void* user_data);

// Generation parameters
typedef struct {
    int32_t  max_tokens;      // Maximum tokens to generate (default: 256)
    float    temperature;     // Sampling temperature (default: 0.7)
    float    top_p;           // Nucleus sampling threshold (default: 0.9)
    int32_t  top_k;           // Top-K sampling (default: 40)
    float    repeat_penalty;  // Repetition penalty (default: 1.1)
    uint64_t seed;            // RNG seed (0 = random)
} llama_params;

// Model info
typedef struct {
    const char* name;         // Model name from GGUF
    const char* arch;         // Architecture (llama, phi, qwen2, etc.)
    int32_t n_vocab;          // Vocabulary size
    int32_t n_ctx;            // Context length
    int32_t n_embd;           // Embedding dimension
    int32_t n_layer;          // Number of layers
    int32_t n_head;           // Number of attention heads
    int32_t n_head_kv;        // Number of KV heads (for GQA)
    size_t  model_size;       // Model size in bytes
} llama_model_info;

// ============================================================================
// Initialization
// ============================================================================

/**
 * Initialize the library.
 * Must be called before any other function.
 * Returns 0 on success, -1 on error.
 */
int llama_init(void);

/**
 * Cleanup and free all resources.
 */
void llama_cleanup(void);

// ============================================================================
// Model Loading
// ============================================================================

/**
 * Load model from memory buffer (GGUF format).
 * 
 * @param data    Pointer to GGUF data
 * @param size    Size of data in bytes
 * @param n_ctx   Context size (0 = use model default)
 * @return        Model handle, or NULL on error
 */
llama_model* llama_load_model(const void* data, size_t size, int32_t n_ctx);

/**
 * Free model and associated resources.
 */
void llama_free_model(llama_model* model);

/**
 * Get model information.
 */
llama_model_info llama_get_model_info(const llama_model* model);

// ============================================================================
// Context Management
// ============================================================================

/**
 * Create inference context for a model.
 * Multiple contexts can share the same model.
 */
llama_context* llama_create_context(llama_model* model);

/**
 * Free context.
 */
void llama_free_context(llama_context* ctx);

/**
 * Clear KV cache (start new conversation).
 */
void llama_clear_context(llama_context* ctx);

// ============================================================================
// Generation
// ============================================================================

/**
 * Get default generation parameters.
 */
llama_params llama_default_params(void);

/**
 * Generate text from prompt (blocking).
 * 
 * @param ctx     Inference context
 * @param prompt  Input prompt (UTF-8)
 * @param params  Generation parameters
 * @return        Generated text (caller must free with llama_free_string)
 */
char* llama_generate(
    llama_context* ctx,
    const char* prompt,
    llama_params params
);

/**
 * Generate text with streaming callback.
 * 
 * @param ctx       Inference context
 * @param prompt    Input prompt (UTF-8)
 * @param params    Generation parameters
 * @param callback  Called for each generated token
 * @param user_data Passed to callback
 * @return          Total tokens generated
 */
int32_t llama_generate_stream(
    llama_context* ctx,
    const char* prompt,
    llama_params params,
    llama_token_callback callback,
    void* user_data
);

/**
 * Abort ongoing generation.
 */
void llama_abort(llama_context* ctx);

/**
 * Free string returned by llama_generate.
 */
void llama_free_string(char* str);

// ============================================================================
// Tokenization
// ============================================================================

/**
 * Tokenize text.
 * 
 * @param model   Model (for vocabulary)
 * @param text    Input text (UTF-8)
 * @param tokens  Output token buffer
 * @param max_tokens  Buffer size
 * @param add_bos Add beginning-of-sequence token
 * @return        Number of tokens, or negative on error
 */
int32_t llama_tokenize(
    const llama_model* model,
    const char* text,
    llama_token* tokens,
    int32_t max_tokens,
    bool add_bos
);

/**
 * Detokenize tokens to text.
 * 
 * @param model   Model (for vocabulary)
 * @param tokens  Input tokens
 * @param n_tokens Number of tokens
 * @return        Text (caller must free with llama_free_string)
 */
char* llama_detokenize(
    const llama_model* model,
    const llama_token* tokens,
    int32_t n_tokens
);

// ============================================================================
// Chat Templates
// ============================================================================

typedef enum {
    LLAMA_TEMPLATE_AUTO,      // Auto-detect from model
    LLAMA_TEMPLATE_CHATML,    // <|im_start|>...<|im_end|>
    LLAMA_TEMPLATE_LLAMA2,    // [INST]...[/INST]
    LLAMA_TEMPLATE_LLAMA3,    // <|start_header_id|>...
    LLAMA_TEMPLATE_PHI,       // Instruct:...Output:
    LLAMA_TEMPLATE_ALPACA,    // ### Instruction:...
} llama_template;

typedef struct {
    const char* role;     // "system", "user", "assistant"
    const char* content;  // Message content
} llama_message;

/**
 * Apply chat template to messages.
 * 
 * @param model     Model (for template detection)
 * @param messages  Array of messages
 * @param n_messages Number of messages
 * @param template  Template to use (AUTO = detect from model)
 * @param add_generation_prompt  Add assistant prefix for generation
 * @return          Formatted prompt (caller must free)
 */
char* llama_apply_template(
    const llama_model* model,
    const llama_message* messages,
    int32_t n_messages,
    llama_template template,
    bool add_generation_prompt
);

// ============================================================================
// Utilities
// ============================================================================

/**
 * Get library version string.
 */
const char* llama_version(void);

/**
 * Get last error message.
 */
const char* llama_get_error(void);

/**
 * Set log callback (default: stderr).
 */
typedef void (*llama_log_callback)(const char* msg, void* user_data);
void llama_set_log_callback(llama_log_callback callback, void* user_data);

#ifdef __cplusplus
}
#endif

#endif // LLAMA_TINY_H
