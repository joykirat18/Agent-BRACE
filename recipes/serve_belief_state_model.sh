#!/usr/bin/env bash
# Serve the finetuned belief-state model via vLLM's OpenAI-compatible API.
#
# The served model is used by TextWorldAgent (decouple_trajectory=True +
# belief_state_model_url) to generate per-step belief states independently
# of the main policy.
#
# Usage:
#   ./recipes/serve_belief_state_model.sh
#
# Override defaults with env vars, e.g.:
#   MODEL_PATH=local/checkpoints/belief-sft-qwen25-3b/merged_model \
#   PORT=8001 \
#   GPUS=0,1 \
#   ./recipes/serve_belief_state_model.sh
#
# NOTE: vLLM cannot serve raw LoRA adapters directly.
# First merge the adapter into a full HF model:
#   ./recipes/merge_belief_state_lora.sh
#
# After the server is ready (prints "Application startup complete"), set in
# the training recipe:
#   belief_state_model_url="http://localhost:${PORT}"
#   belief_state_model_name="${SERVED_MODEL_NAME}"

set -euo pipefail
cd "$(dirname "$0")/.."

# ---------------------------------------------------------------------------
# Config (all overridable via env vars)
# ---------------------------------------------------------------------------

# Path to the merged full-weight model produced by merge_belief_state_lora.sh.
# This must be a complete HF model directory (not a raw LoRA adapter).
# Run ./recipes/merge_belief_state_lora.sh first if you only have the adapter.
MODEL_PATH="${MODEL_PATH:-/home/user/textworld-RL/local/checkpoints/alfworld-belief-sft-qwen3b/merged_model}"

# Name exposed via the /v1/models endpoint (must match belief_state_model_name
# in the training recipe).
SERVED_MODEL_NAME="${SERVED_MODEL_NAME:-belief-state}"

# Port for the OpenAI-compatible HTTP server.
PORT="${PORT:-8001}"

# GPU(s) to use.  Comma-separated device indices, e.g. "2,3".
GPUS="${GPUS:-0,1}"

# Tensor-parallel size: set to the number of GPUs in GPUS.
TP_SIZE="${TP_SIZE:-2}"

# GPU memory fraction (leave headroom for other processes).
GPU_MEM_UTIL="${GPU_MEM_UTIL:-0.90}"

# Maximum model context length.
MAX_MODEL_LEN="${MAX_MODEL_LEN:-4096}"

# Maximum number of sequences batched together.
MAX_NUM_SEQS="${MAX_NUM_SEQS:-64}"

# dtype: auto | float16 | bfloat16
DTYPE="${DTYPE:-bfloat16}"

# ---------------------------------------------------------------------------
# Validate model path
# ---------------------------------------------------------------------------
if [[ "$MODEL_PATH" != */* ]]; then
    # Looks like a plain HF repo id — vLLM will download it.
    echo "Model path looks like an HF repo id: ${MODEL_PATH}"
elif [ ! -e "$MODEL_PATH" ]; then
    echo "ERROR: MODEL_PATH does not exist: ${MODEL_PATH}" >&2
    echo "Train then merge first:" >&2
    echo "  TRAIN_JSONL=<path> OUTPUT_DIR=<dir> ./recipes/finetune_belief_qwen25_3b.sh" >&2
    echo "  ./recipes/merge_belief_state_lora.sh" >&2
    exit 1
elif [ -f "${MODEL_PATH}/adapter_config.json" ] && [ ! -f "${MODEL_PATH}/config.json" ]; then
    # Directory contains a LoRA adapter but no base-model config — not yet merged.
    echo "ERROR: ${MODEL_PATH} looks like a raw LoRA adapter, not a merged HF model." >&2
    echo "Run the merge step first:" >&2
    echo "  ADAPTER_PATH=${MODEL_PATH} ./recipes/merge_belief_state_lora.sh" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Launch vLLM server
# ---------------------------------------------------------------------------
echo "========================================================"
echo "  Belief-state vLLM server"
echo "  model       : ${MODEL_PATH}"
echo "  served name : ${SERVED_MODEL_NAME}"
echo "  url         : http://localhost:${PORT}"
echo "  GPUs        : ${GPUS}  (TP=${TP_SIZE})"
echo "  dtype       : ${DTYPE}"
echo "  max_len     : ${MAX_MODEL_LEN}"
echo "========================================================"

CUDA_VISIBLE_DEVICES="$GPUS" python3 -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_PATH" \
    --served-model-name "$SERVED_MODEL_NAME" \
    --port "$PORT" \
    --tensor-parallel-size "$TP_SIZE" \
    --gpu-memory-utilization "$GPU_MEM_UTIL" \
    --max-num-seqs "$MAX_NUM_SEQS" \
    --dtype "$DTYPE" \
    --trust-remote-code \
    --disable-log-requests \
    "$@"
