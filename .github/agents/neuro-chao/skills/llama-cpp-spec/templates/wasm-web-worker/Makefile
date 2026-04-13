# Makefile for Tiny LLM WASM build
# Requires Emscripten SDK

CC = emcc
CFLAGS = -O3 -DNDEBUG

# WASM settings
WASM_FLAGS = -s WASM=1 \
             -s ALLOW_MEMORY_GROWTH=1 \
             -s MAXIMUM_MEMORY=4GB \
             -s STACK_SIZE=1MB \
             -s INITIAL_MEMORY=64MB \
             -s MODULARIZE=1 \
             -s EXPORT_NAME='createLlamaTinyModule' \
             -s EXPORTED_FUNCTIONS='["_malloc","_free","_llama_init","_llama_load_model","_llama_free_model","_llama_create_context","_llama_free_context","_llama_clear_context","_llama_generate","_llama_generate_stream","_llama_abort","_llama_get_error","_llama_get_model_info_ptr","_set_token_callback"]' \
             -s EXPORTED_RUNTIME_METHODS='["ccall","cwrap","UTF8ToString","allocateUTF8","setValue","getValue","addFunction"]' \
             -s ALLOW_TABLE_GROWTH=1 \
             --no-entry

# Optional: SIMD support (faster, larger binary)
# SIMD_FLAGS = -msimd128

# Source files
SRCS = llama-tiny.c
OBJS = $(SRCS:.c=.o)

# Output
OUT = llama-tiny.js

.PHONY: all clean simd

all: $(OUT)

# Standard build (smaller, compatible)
$(OUT): $(SRCS)
	$(CC) $(CFLAGS) $(WASM_FLAGS) -o $@ $^
	@echo "Built: $(OUT) and llama-tiny.wasm"
	@ls -lh $(OUT) llama-tiny.wasm

# SIMD build (faster, requires browser support)
simd: WASM_FLAGS += -msimd128
simd: $(OUT)
	@echo "Built with SIMD support"

# Debug build
debug: CFLAGS = -O0 -g -DDEBUG
debug: WASM_FLAGS += -s ASSERTIONS=2
debug: $(OUT)
	@echo "Built debug version"

# Single file build (WASM embedded in JS)
single: WASM_FLAGS += -s SINGLE_FILE=1
single: $(OUT)
	@echo "Built single-file version"

# Size report
size: $(OUT)
	@echo "=== Size Report ==="
	@ls -lh $(OUT) llama-tiny.wasm
	@echo ""
	@echo "Gzipped sizes:"
	@gzip -c $(OUT) | wc -c | awk '{printf "  llama-tiny.js: %.1f KB\n", $$1/1024}'
	@gzip -c llama-tiny.wasm | wc -c | awk '{printf "  llama-tiny.wasm: %.1f KB\n", $$1/1024}'

clean:
	rm -f $(OUT) llama-tiny.wasm *.o

# Development server
serve:
	python3 -m http.server 8080

# Help
help:
	@echo "Tiny LLM WASM Build"
	@echo ""
	@echo "Targets:"
	@echo "  all     - Build standard WASM (default)"
	@echo "  simd    - Build with SIMD support (faster)"
	@echo "  debug   - Build debug version"
	@echo "  single  - Build single-file (WASM embedded)"
	@echo "  size    - Show size report"
	@echo "  serve   - Start development server"
	@echo "  clean   - Remove build artifacts"
	@echo ""
	@echo "Requirements:"
	@echo "  - Emscripten SDK (source emsdk_env.sh)"
