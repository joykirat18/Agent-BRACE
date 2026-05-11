#!/usr/bin/env python3
"""Merge a LoRA adapter checkpoint into its base model and save as a full HuggingFace model.

Usage:
    python3 meow_tea_experiments/scripts/merge_lora_to_hf.py \
        --adapter_path local/checkpoints/belief-sft-qwen25-3b/final_model \
        --output_path  local/checkpoints/belief-sft-qwen25-3b/merged_model \
        [--base_model  Qwen/Qwen2.5-3B-Instruct]  # inferred from adapter config if omitted
        [--dtype       bfloat16]
        [--device      cpu]                        # use "cuda" to merge on GPU (faster)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def infer_base_model(adapter_path: Path) -> str | None:
    """Try to read base_model_name_or_path from adapter_config.json."""
    cfg_file = adapter_path / "adapter_config.json"
    if not cfg_file.is_file():
        return None
    try:
        cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
        return cfg.get("base_model_name_or_path")
    except Exception:
        return None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Merge LoRA adapter into base model → HF format")
    p.add_argument(
        "--adapter_path",
        type=Path,
        required=True,
        help="Directory containing the LoRA adapter (adapter_config.json + adapter_model.* files). "
             "Typically OUTPUT_DIR/final_model from finetune_belief_state_sft.py.",
    )
    p.add_argument(
        "--output_path",
        type=Path,
        required=True,
        help="Where to write the merged full-weight model (HF format, ready for vLLM).",
    )
    p.add_argument(
        "--base_model",
        type=str,
        default=None,
        help="Base model name or local path. Inferred from adapter_config.json if omitted.",
    )
    p.add_argument(
        "--dtype",
        type=str,
        default="bfloat16",
        choices=["float32", "float16", "bfloat16"],
        help="dtype to use when loading the base model (default: bfloat16).",
    )
    p.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="Device for merging: 'cpu' (safe, lower VRAM) or 'cuda' (faster). Default: cpu.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
    except ImportError as e:
        raise SystemExit(
            "Missing dependency. Install: pip install transformers peft torch\n"
            f"Import error: {e}"
        ) from e

    adapter_path = args.adapter_path.expanduser().resolve()
    output_path = args.output_path.expanduser().resolve()

    if not adapter_path.is_dir():
        raise SystemExit(f"adapter_path does not exist or is not a directory: {adapter_path}")

    adapter_cfg = adapter_path / "adapter_config.json"
    if not adapter_cfg.is_file():
        raise SystemExit(
            f"No adapter_config.json found in {adapter_path}. "
            "Make sure this is a LoRA adapter directory produced by SFTTrainer."
        )

    # Resolve base model
    base_model = args.base_model or infer_base_model(adapter_path)
    if not base_model:
        raise SystemExit(
            "Could not infer base model from adapter_config.json. "
            "Pass --base_model explicitly."
        )
    logger.info("Base model : %s", base_model)
    logger.info("Adapter    : %s", adapter_path)
    logger.info("Output     : %s", output_path)
    logger.info("dtype      : %s  |  device: %s", args.dtype, args.device)

    dtype_map = {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }
    torch_dtype = dtype_map[args.dtype]

    # Load base model
    logger.info("Loading base model...")
    base = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch_dtype,
        device_map=args.device,
        trust_remote_code=True,
    )

    # Load tokenizer (from adapter dir first, fall back to base model)
    tokenizer_source = str(adapter_path) if (adapter_path / "tokenizer_config.json").is_file() else base_model
    logger.info("Loading tokenizer from %s ...", tokenizer_source)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_source, trust_remote_code=True)

    # Attach LoRA adapter
    logger.info("Attaching LoRA adapter...")
    model = PeftModel.from_pretrained(base, str(adapter_path), torch_dtype=torch_dtype)

    # Merge adapter weights into the base model
    logger.info("Merging LoRA weights (this may take a minute on CPU)...")
    model = model.merge_and_unload()

    # Save merged model
    output_path.mkdir(parents=True, exist_ok=True)
    logger.info("Saving merged model to %s ...", output_path)
    model.save_pretrained(str(output_path), safe_serialization=True)
    tokenizer.save_pretrained(str(output_path))

    # Quick sanity check
    n_params = sum(p.numel() for p in model.parameters()) / 1e9
    logger.info("Done. Merged model saved (%.2f B parameters).", n_params)
    logger.info(
        "Serve with vLLM:\n"
        "  python3 -m vllm.entrypoints.openai.api_server \\\n"
        "    --model %s \\\n"
        "    --served-model-name belief-state \\\n"
        "    --port 8001",
        output_path,
    )


if __name__ == "__main__":
    main()
