export HUGGINGFACE_TOKEN='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'
export HF_TOKEN='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'
CUDA_VISIBLE_DEVICES=3 python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-30B-A3B-Instruct-2507 \
  --port 8005 \
  --tensor-parallel-size 1 \
  --max-model-len 8000