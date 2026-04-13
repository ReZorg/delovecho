#!/usr/bin/env bash
# convert_to_gguf.sh — Convert KoboldAI/OPT-350M-Erebus to GGUF for KoboldCpp.
#
# Usage:
#   bash convert_to_gguf.sh [output_dir]
#
# Prerequisites:
#   pip install transformers torch
#   git clone https://github.com/ggerganov/llama.cpp
#   cd llama.cpp && make
#
# The script downloads the model, converts to GGUF, and optionally quantizes.

set -euo pipefail

MODEL_ID="KoboldAI/OPT-350M-Erebus"
OUTPUT_DIR="${1:-./erebus-350-gguf}"
LLAMA_CPP_DIR="${LLAMA_CPP_DIR:-./llama.cpp}"

echo "=== Erebus 350M GGUF Conversion ==="

# Step 1: Download model
echo "[1/3] Downloading model from HuggingFace..."
if command -v huggingface-cli &>/dev/null; then
    huggingface-cli download "$MODEL_ID" --local-dir "${OUTPUT_DIR}/hf-model"
else
    pip install huggingface_hub
    python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('${MODEL_ID}', local_dir='${OUTPUT_DIR}/hf-model')
"
fi

# Step 2: Convert to GGUF
echo "[2/3] Converting to GGUF format..."
if [ ! -f "${LLAMA_CPP_DIR}/convert_hf_to_gguf.py" ]; then
    echo "ERROR: llama.cpp not found at ${LLAMA_CPP_DIR}"
    echo "Clone it: git clone https://github.com/ggerganov/llama.cpp"
    exit 1
fi

python3 "${LLAMA_CPP_DIR}/convert_hf_to_gguf.py" \
    "${OUTPUT_DIR}/hf-model" \
    --outfile "${OUTPUT_DIR}/erebus-350m-f16.gguf" \
    --outtype f16

# Step 3: Quantize (optional but recommended for CPU)
echo "[3/3] Quantizing to Q4_K_M (recommended for CPU)..."
if [ -f "${LLAMA_CPP_DIR}/llama-quantize" ]; then
    "${LLAMA_CPP_DIR}/llama-quantize" \
        "${OUTPUT_DIR}/erebus-350m-f16.gguf" \
        "${OUTPUT_DIR}/erebus-350m-q4_k_m.gguf" \
        Q4_K_M
    echo "Quantized model: ${OUTPUT_DIR}/erebus-350m-q4_k_m.gguf"
elif [ -f "${LLAMA_CPP_DIR}/quantize" ]; then
    "${LLAMA_CPP_DIR}/quantize" \
        "${OUTPUT_DIR}/erebus-350m-f16.gguf" \
        "${OUTPUT_DIR}/erebus-350m-q4_k_m.gguf" \
        Q4_K_M
    echo "Quantized model: ${OUTPUT_DIR}/erebus-350m-q4_k_m.gguf"
else
    echo "WARNING: llama-quantize not found. Skipping quantization."
    echo "Full-precision model: ${OUTPUT_DIR}/erebus-350m-f16.gguf"
fi

echo ""
echo "=== Done ==="
echo "F16 model:  ${OUTPUT_DIR}/erebus-350m-f16.gguf"
echo ""
echo "To run with KoboldCpp:"
echo "  koboldcpp ${OUTPUT_DIR}/erebus-350m-q4_k_m.gguf --contextsize 2048"
