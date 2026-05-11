#!/usr/bin/env bash
# Merge the LoRA adapter from finetune_belief_state_sft.py into a full HF model
# so it can be served directly by vLLM.
#
# Usage:
#   ./recipes/merge_belief_state_lora.sh
#
# Override defaults via env vars:
#   ADAPTER_PATH=local/checkpoints/belief-sft-qwen25-3b/final_model \
#   OUTPUT_PATH=local/checkpoints/belief-sft-qwen25-3b/merged_model \
#   BASE_MODEL=Qwen/Qwen2.5-3B-Instruct \
#   DEVICE=cuda \
#   ./recipes/merge_belief_state_lora.sh
#
# After merging, serve with:
#   MODEL_PATH=<OUTPUT_PATH> ./recipes/serve_belief_state_model.sh

set -euo pipefail
cd "$(dirname "$0")/.."

ADAPTER_PATH="${ADAPTER_PATH:-/home/user/textworld-RL/local/checkpoints/2_wep-sft-qwen3b/final_model}"
OUTPUT_PATH="${OUTPUT_PATH:-/home/user/textworld-RL/local/checkpoints/2_wep-sft-qwen3b/merged_model}"
# BASE_MODEL is optional: inferred from adapter_config.json when left empty.
BASE_MODEL="${BASE_MODEL:-}"
# cpu is safe on any machine; set DEVICE=cuda if you want to merge on GPU.
DEVICE="${DEVICE:-cpu}"
DTYPE="${DTYPE:-bfloat16}"

echo "========================================================"
echo "  LoRA → HF merge"
echo "  adapter : ${ADAPTER_PATH}"
echo "  output  : ${OUTPUT_PATH}"
echo "  device  : ${DEVICE}  dtype: ${DTYPE}"
echo "========================================================"

EXTRA_ARGS=()
if [ -n "$BASE_MODEL" ]; then
    EXTRA_ARGS+=(--base_model "$BASE_MODEL")
fi

python3 meow_tea_experiments/scripts/merge_lora_to_hf.py \
    --adapter_path "$ADAPTER_PATH" \
    --output_path  "$OUTPUT_PATH" \
    --dtype        "$DTYPE" \
    --device       "$DEVICE" \
    "${EXTRA_ARGS[@]}" \
    "$@"

echo ""
echo "Merged model saved to: ${OUTPUT_PATH}"
echo "Now serve with:"
echo "  MODEL_PATH=${OUTPUT_PATH} ./recipes/serve_belief_state_model.sh"
