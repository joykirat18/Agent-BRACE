#!/usr/bin/env python3
# Copyright 2025 Anonymous Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Supervised fine-tuning for belief-state prediction from JSONL produced by
``generate_belief_state_dataset.py``.

Expected JSONL fields (one object per line):
  goal, previous_belief_state (str; empty at step 0),
  observations (list; last element is current obs),
  actions (list; stored for reference, not used in the prompt),
  gpt_belief_state or belief_state (target text),
  optional: action_leaked (skipped if --skip_leaked and True).

Uses Hugging Face ``transformers`` + ``trl.SFTTrainer`` only (no verl).

Multi-GPU: launch with ``accelerate`` (see ``recipes/finetune_belief_qwen25_3b.sh`` and
``NUM_GPUS``). Example:

  NUM_GPUS=4 accelerate launch --num_processes=4 --multi_gpu \\
    meow_tea_experiments/scripts/finetune_belief_state_sft.py ...args...

Rows are pre-tokenized with ``input_ids`` + ``completion_mask`` so training only
uses loss on the assistant span. This avoids TRL's ``assistant_only_loss`` path,
which requires chat templates with ``{% generation %}`` (not provided by all
tokenizers, e.g. some Qwen2.5 builds).

Example:
  python3 meow_tea_experiments/scripts/finetune_belief_state_sft.py \\
    --train_jsonl local/belief_dataset/train_belief.jsonl \\
    --output_dir local/checkpoints/belief-sft-qwen3b \\
    --model_name_or_path Qwen/Qwen2.5-3B-Instruct \\
    --max_length 4096 \\
  --adaptive_max_length \\
    --num_train_epochs 3

Resume from the latest checkpoint in ``output_dir``:

  ... --resume

Or from a specific step folder:

  ... --resume_from_checkpoint local/checkpoints/belief-sft-qwen3b/checkpoint-500

Optional LoRA (lower VRAM):
  ... --lora_r 64 --lora_alpha 128
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from datasets import Dataset
from transformers import PreTrainedTokenizerBase

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# User prompt must match the distribution used during teacher labeling (see
# ``generate_belief_state_dataset._BELIEF_PROMPT_TEMPLATE``).
_USER_PROMPT_TEMPLATE = """\
You are playing a text-based game. Given the goal description, your previous belief \
state (if available), and the current observation, produce an updated belief state \
that captures what you know — and what you don't know — about the current world state.

Goal:
{goal}

Previous belief state:
{previous_belief_state}

Current observation:
{current_obs}

Output ONLY a belief state within <belief_state> </belief_state> tags.

STRICT RULES — your belief state MUST NOT contain:
- Any next action, plan, intention, or statement of what you will do next.
- Any forward-looking phrases such as "I will", "I should", "my next step is",
  "I plan to", "I intend to", "I need to go", "I should try", "next I will", etc.
- Any recommendation or suggestion about which command to execute.

ONLY record what you have ALREADY observed or inferred from past observations. \
The belief state is a retrospective summary of world knowledge, NOT a plan.

CERTAINTY SCALE — when describing any fact about location, object, connection, \
inventory, or goal progress, you MUST attach exactly one level from this Likert-style \
scale (use the word or phrase naturally in the same sentence as the fact):

  - "certain" or "confirmed": you have directly observed this to be true.
  - "almost certain": very strong evidence, would be very surprised if wrong.
  - "probable": more likely true than not, based on what you have seen.
  - "possible": could go either way; some evidence for it, some against.
  - "unlikely": more evidence against it than for it, but cannot rule it out.
  - "doubtful": little reason to believe it; would be surprised if true.
  - "unknown": no evidence either way; you have not explored or observed enough to say.

FORMATTING REQUIREMENTS:
- Write one short bullet per distinct fact (use "- " at the start of each line).
- EVERY bullet MUST contain exactly one certainty marker from the scale above \
  (e.g. "certain", "confirmed", "almost certain", "probable", "possible", \
  "unlikely", "doubtful", or "unknown") applied to that bullet's claim.
- Cover: current location, known room connections, objects and their states, inventory, \
  and which parts of the goal are complete or not — each as its own labeled bullet \
  with an appropriate certainty level.
- Do not use JSON, numeric probabilities, or percentages. Use only the natural-language \
  scale defined above.

Examples of valid bullets:
- It is confirmed that I am in the kitchen.
- The east exit almost certainly leads to the hallway.
- The key is probably still in the living room.
- It is possible the chest is already open.
- It is unlikely the lamp is in the basement.
- It is doubtful the door to the garden is unlocked.
- It is unknown whether the drawer contains the note.\
"""


def build_user_prompt(goal: str, previous_belief_state: str, current_obs: str) -> str:
    """Align with generator: goal + previous belief state (empty at step 0) + current obs."""
    prev_belief_str = (
        previous_belief_state.strip()
        if previous_belief_state.strip()
        else "(none — this is the first observation)"
    )
    return _USER_PROMPT_TEMPLATE.format(
        goal=goal.strip(),
        previous_belief_state=prev_belief_str,
        current_obs=current_obs.strip(),
    )


def load_valid_jsonl_rows(
    path: Path,
    skip_leaked: bool,
    prefer_gpt_belief: bool,
) -> List[Dict[str, Any]]:
    """Return raw JSON objects from JSONL that pass the same filters as training."""
    rows: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                logger.warning("Skip line %d: JSON error %s", line_no, e)
                continue

            if skip_leaked and row.get("action_leaked"):
                continue

            if prefer_gpt_belief:
                inner = (row.get("gpt_belief_state") or row.get("belief_state") or "").strip()
            else:
                inner = (row.get("belief_state") or row.get("gpt_belief_state") or "").strip()

            if not inner:
                continue

            try:
                if not row.get("goal") or not row.get("observations"):
                    raise ValueError("missing goal or observations")
                build_user_prompt(
                    row["goal"],
                    row.get("previous_belief_state", ""),
                    row["observations"][-1],
                )
            except (KeyError, ValueError) as e:
                logger.warning("Skip line %d: %s", line_no, e)
                continue

            rows.append(row)
    return rows


def row_to_message_record(row: Dict[str, Any], prefer_gpt_belief: bool) -> Dict[str, Any]:
    if prefer_gpt_belief:
        inner = (row.get("gpt_belief_state") or row.get("belief_state") or "").strip()
    else:
        inner = (row.get("belief_state") or row.get("gpt_belief_state") or "").strip()
    user_content = build_user_prompt(
        row["goal"],
        row.get("previous_belief_state", ""),
        row["observations"][-1],
    )
    assistant_content = f"<belief_state>\n{inner}\n</belief_state>"
    return {
        "messages": [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content},
        ],
    }


def split_train_eval_rows(
    rows: List[Dict[str, Any]],
    val_ratio: float,
    seed: int,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Random shuffle then hold out ``val_ratio`` of rows for evaluation (default 20%).
    If ``val_ratio <= 0`` or fewer than 2 rows, returns (rows, []).
    """
    if val_ratio <= 0 or len(rows) < 2:
        return rows, []
    rng = random.Random(seed)
    shuffled = list(rows)
    rng.shuffle(shuffled)
    n_val = max(1, round(len(shuffled) * val_ratio))
    if n_val >= len(shuffled):
        n_val = max(1, len(shuffled) // 5)
    eval_rows = shuffled[:n_val]
    train_rows = shuffled[n_val:]
    return train_rows, eval_rows


def load_jsonl_messages(
    path: Path,
    skip_leaked: bool,
    prefer_gpt_belief: bool,
) -> List[Dict[str, Any]]:
    raw = load_valid_jsonl_rows(path, skip_leaked, prefer_gpt_belief)
    return [row_to_message_record(r, prefer_gpt_belief) for r in raw]


def _normalize_token_ids(
    ids: Union[Sequence[int], Sequence[Sequence[int]], List[int]],
) -> List[int]:
    """Handle tokenizers that return ``list[int]`` or ``list[list[int]]`` for one example."""
    if not ids:
        return []
    if isinstance(ids[0], list):
        return [int(x) for x in ids[0]]  # type: ignore[arg-type]
    return [int(x) for x in ids]


def _full_chat_input_ids(
    messages: List[Dict[str, str]],
    tokenizer: PreTrainedTokenizerBase,
) -> List[int]:
    """Tokenize the full user+assistant chat (same entrypoint as training)."""
    raw = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=False,
        tokenize=True,
    )
    return _normalize_token_ids(raw)


def _length_percentile_nearest_rank(sorted_lengths: List[int], q: float) -> int:
    """Smallest value such that at least fraction ``q`` of samples are <= that value (q in (0, 1])."""
    n = len(sorted_lengths)
    if n == 0:
        raise ValueError("sorted_lengths must be non-empty")
    q = min(1.0, max(1e-9, q))
    k = min(n - 1, max(0, math.ceil(q * n) - 1))
    return sorted_lengths[k]


def resolve_effective_max_length(
    lengths: List[int],
    cap: int,
    coverage: float,
    adaptive: bool,
) -> Tuple[int, Dict[str, Any]]:
    """
    Return ``max_length`` for SFT and a small stats dict for logging.

    When ``adaptive`` is True, use the nearest-rank ``coverage`` percentile of
    observed full-sequence lengths, then clamp to ``cap`` (VRAM / model limit).
    """
    coverage = min(1.0, max(1e-9, float(coverage)))
    stats: Dict[str, Any] = {"adaptive": adaptive, "cap": cap, "coverage": coverage}
    if not adaptive:
        stats.update({"reason": "fixed", "effective": cap})
        return cap, stats
    if not lengths:
        stats.update({"reason": "no_lengths", "effective": cap})
        return cap, stats
    stats["n"] = len(lengths)
    stats["min_len"] = min(lengths)
    stats["max_len"] = max(lengths)
    s = sorted(lengths)
    data_pct = _length_percentile_nearest_rank(s, coverage)
    stats["percentile_length"] = data_pct
    effective = min(cap, data_pct)
    stats["effective"] = effective
    if effective < data_pct:
        stats["capped_below_percentile"] = True
    return effective, stats


def tokenize_messages_with_completion_mask(
    messages: List[Dict[str, str]],
    tokenizer: PreTrainedTokenizerBase,
    max_length: int,
) -> Dict[str, List[int]]:
    """
    Build ``input_ids`` and ``completion_mask`` (1 = train on this token).

    Uses user-only template + full chat so we never depend on
    ``return_assistant_tokens_mask`` / ``{% generation %}``.
    """
    if len(messages) != 2 or messages[0]["role"] != "user" or messages[1]["role"] != "assistant":
        raise ValueError("Expected exactly one user and one assistant message")

    prompt_ids = tokenizer.apply_chat_template(
        messages[:1],
        add_generation_prompt=True,
        tokenize=True,
    )
    full_ids = _full_chat_input_ids(messages, tokenizer)
    prompt_ids = _normalize_token_ids(prompt_ids)

    plen: int
    if len(full_ids) >= len(prompt_ids) and full_ids[: len(prompt_ids)] == prompt_ids:
        plen = len(prompt_ids)
    else:
        # String boundary fallback (some template/tokenize pairs disagree slightly)
        prompt_text = tokenizer.apply_chat_template(
            messages[:1], add_generation_prompt=True, tokenize=False
        )
        full_text = tokenizer.apply_chat_template(
            messages, add_generation_prompt=False, tokenize=False
        )
        if not full_text.startswith(prompt_text):
            raise ValueError("Full chat string does not start with prompt string; cannot align spans")
        prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
        full_ids = tokenizer(full_text, add_special_tokens=False)["input_ids"]
        plen = len(prompt_ids)

    completion_mask = [0] * plen + [1] * (len(full_ids) - plen)

    if len(full_ids) > max_length:
        drop = len(full_ids) - max_length
        full_ids = full_ids[drop:]
        completion_mask = completion_mask[drop:]

    if 1 not in completion_mask:
        raise ValueError("Truncation removed all completion tokens; increase --max_length")

    return {"input_ids": full_ids, "completion_mask": completion_mask}


def build_processed_dataset(
    message_rows: List[Dict[str, Any]],
    tokenizer: PreTrainedTokenizerBase,
    max_length: int,
    split_name: str,
) -> Dataset:
    processed: List[Dict[str, List[int]]] = []
    skipped = 0
    for i, row in enumerate(message_rows):
        try:
            processed.append(
                tokenize_messages_with_completion_mask(
                    row["messages"], tokenizer, max_length
                )
            )
        except Exception as e:  # noqa: BLE001
            skipped += 1
            logger.warning("%s row %d skipped: %s", split_name, i, e)
    if not processed:
        raise ValueError(f"No examples left after tokenization ({split_name}, skipped={skipped})")
    if skipped:
        logger.info("%s: kept %d examples, skipped %d", split_name, len(processed), skipped)
    return Dataset.from_list(processed)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="SFT belief state model (JSONL → Qwen Instruct)")
    p.add_argument(
        "--train_jsonl",
        type=Path,
        required=True,
        help="Training JSONL (e.g. local/belief_dataset/train_belief.jsonl)",
    )
    p.add_argument(
        "--eval_jsonl",
        type=Path,
        default=None,
        help="Optional eval JSONL (same schema). If omitted, a random hold-out split "
        "from --train_jsonl is used (see --val_ratio); eval rows are written to "
        "--split_eval_jsonl_out (default: OUTPUT_DIR/eval_split.jsonl).",
    )
    p.add_argument(
        "--val_ratio",
        type=float,
        default=0.1,
        help="When --eval_jsonl is not set, fraction of train JSONL rows for eval "
        "(shuffle + split). Set to 0 to disable eval.",
    )
    p.add_argument(
        "--split_eval_jsonl_out",
        type=Path,
        default=None,
        help="Where to write the hold-out eval JSONL when splitting from train "
        "(default: OUTPUT_DIR/eval_split.jsonl).",
    )
    p.add_argument(
        "--output_dir",
        type=Path,
        default=Path("local/checkpoints/belief-sft-qwen"),
        help="Where to save checkpoints and final adapter/model",
    )
    p.add_argument(
        "--model_name_or_path",
        type=str,
        default="Qwen/Qwen2.5-3B-Instruct",
        help="Base instruct model (default: Qwen2.5-3B-Instruct)",
    )
    p.add_argument(
        "--max_length",
        type=int,
        default=4096,
        help="Upper bound on sequence length (padding / truncation). With --adaptive_max_length, "
        "this is the hard cap; the run may use a smaller value from the data.",
    )
    p.add_argument(
        "--adaptive_max_length",
        action="store_true",
        help="Pick max_length as min(--max_length, nearest-rank percentile of full chat lengths) "
        "so roughly --adaptive_coverage of examples fit without needing a longer window.",
    )
    p.add_argument(
        "--adaptive_coverage",
        type=float,
        default=0.99,
        help="With --adaptive_max_length, target fraction of examples with full length <= chosen "
        "max_length before applying --max_length cap (default: 0.99). Values > 1 are treated as 1.",
    )
    p.add_argument("--num_train_epochs", type=float, default=3.0)
    p.add_argument("--per_device_train_batch_size", type=int, default=1)
    p.add_argument("--per_device_eval_batch_size", type=int, default=1)
    p.add_argument("--gradient_accumulation_steps", type=int, default=8)
    p.add_argument("--learning_rate", type=float, default=2e-5)
    p.add_argument("--warmup_ratio", type=float, default=0.03)
    p.add_argument("--logging_steps", type=int, default=10)
    p.add_argument("--save_steps", type=int, default=100)
    p.add_argument("--eval_steps", type=int, default=100)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--skip_leaked",
        action="store_true",
        help="Drop rows with action_leaked == true",
    )
    p.add_argument(
        "--prefer_sanitized_belief",
        action="store_true",
        help="Use belief_state over gpt_belief_state when both exist (default: prefer gpt_belief_state)",
    )
    p.add_argument("--bf16", action="store_true", help="Use bfloat16 (recommended on Ampere+)")
    p.add_argument("--fp16", action="store_true", help="Use float16 (if bf16 unavailable)")
    p.add_argument("--gradient_checkpointing", action="store_true", default=True)
    p.add_argument("--no_gradient_checkpointing", action="store_false", dest="gradient_checkpointing")
    # LoRA
    p.add_argument("--lora_r", type=int, default=0, help="LoRA rank; 0 = full fine-tune")
    p.add_argument("--lora_alpha", type=int, default=64)
    p.add_argument("--lora_dropout", type=float, default=0.05)
    p.add_argument(
        "--resume",
        action="store_true",
        help="Resume from the latest checkpoint under --output_dir (see get_last_checkpoint). "
        "Ignored if there is no checkpoint; use --resume_from_checkpoint for an explicit path.",
    )
    p.add_argument(
        "--resume_from_checkpoint",
        type=Path,
        default=None,
        help="Explicit checkpoint directory to resume from (e.g. OUTPUT_DIR/checkpoint-500). "
        "Overrides --resume.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)

    try:
        import torch
        from accelerate import PartialState
        from trl import SFTConfig, SFTTrainer
        from transformers import AutoTokenizer
        from transformers.trainer_utils import get_last_checkpoint
    except ImportError as e:
        raise SystemExit(
            "Missing dependency. Install: pip install transformers trl datasets accelerate torch\n"
            f"Import error: {e}"
        ) from e

    state = PartialState()
    prefer_gpt = not args.prefer_sanitized_belief
    all_rows = load_valid_jsonl_rows(
        args.train_jsonl,
        skip_leaked=args.skip_leaked,
        prefer_gpt_belief=prefer_gpt,
    )
    if not all_rows:
        raise SystemExit(f"No training examples loaded from {args.train_jsonl}")

    eval_rows: List[Dict[str, Any]] = []
    if args.eval_jsonl is not None and args.eval_jsonl.is_file():
        train_rows = all_rows
        eval_rows = load_valid_jsonl_rows(
            args.eval_jsonl,
            skip_leaked=args.skip_leaked,
            prefer_gpt_belief=prefer_gpt,
        )
        if not eval_rows and state.is_main_process:
            logger.warning("Eval JSONL %s produced no examples after filtering", args.eval_jsonl)
    else:
        if args.eval_jsonl is not None and state.is_main_process:
            logger.warning(
                "Eval path %s is not a file; splitting train with val_ratio=%s",
                args.eval_jsonl,
                args.val_ratio,
            )
        train_rows, eval_rows = split_train_eval_rows(
            all_rows, val_ratio=args.val_ratio, seed=args.seed
        )
        if eval_rows:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            eval_out = args.split_eval_jsonl_out or (args.output_dir / "eval_split.jsonl")
            eval_out.parent.mkdir(parents=True, exist_ok=True)
            if state.is_main_process:
                with eval_out.open("w", encoding="utf-8") as ef:
                    for r in eval_rows:
                        ef.write(json.dumps(r, ensure_ascii=False) + "\n")
                logger.info(
                    "No --eval_jsonl: split train into %d train / %d eval (val_ratio=%.2f); wrote eval to %s",
                    len(train_rows),
                    len(eval_rows),
                    args.val_ratio,
                    eval_out,
                )
        elif args.val_ratio > 0 and state.is_main_process:
            logger.info(
                "val_ratio=%s but dataset too small for a hold-out; training on all %d rows",
                args.val_ratio,
                len(train_rows),
            )

    train_records = [row_to_message_record(r, prefer_gpt) for r in train_rows]
    eval_records = [row_to_message_record(r, prefer_gpt) for r in eval_rows]

    with state.main_process_first():
        tokenizer = AutoTokenizer.from_pretrained(
            args.model_name_or_path, trust_remote_code=True
        )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if args.adaptive_max_length:
        profile_records = list(train_records)
        if eval_records:
            profile_records.extend(eval_records)
        lengths = [
            len(_full_chat_input_ids(r["messages"], tokenizer)) for r in profile_records
        ]
        max_length, ml_stats = resolve_effective_max_length(
            lengths,
            cap=args.max_length,
            coverage=args.adaptive_coverage,
            adaptive=True,
        )
    else:
        max_length, ml_stats = resolve_effective_max_length(
            [],
            cap=args.max_length,
            coverage=args.adaptive_coverage,
            adaptive=False,
        )
    if state.is_main_process:
        if ml_stats.get("adaptive"):
            logger.info(
                "Adaptive max_length: coverage=%.4f n=%d min_len=%s max_len=%s percentile_len=%s cap=%s -> %s",
                ml_stats.get("coverage", args.adaptive_coverage),
                ml_stats.get("n", 0),
                ml_stats.get("min_len"),
                ml_stats.get("max_len"),
                ml_stats.get("percentile_length"),
                ml_stats.get("cap"),
                max_length,
            )
            if ml_stats.get("capped_below_percentile"):
                logger.warning(
                    "--max_length cap %s is below the target percentile length %s; long examples will be truncated more.",
                    args.max_length,
                    ml_stats.get("percentile_length"),
                )
        else:
            logger.info("Using fixed max_length=%d", max_length)

    train_ds = build_processed_dataset(
        train_records, tokenizer, max_length, "train"
    )
    if state.is_main_process:
        logger.info("Train tokenized examples: %d", len(train_ds))

    eval_ds = None
    if eval_records:
        eval_ds = build_processed_dataset(
            eval_records, tokenizer, max_length, "eval"
        )
        if state.is_main_process:
            logger.info("Eval tokenized examples: %d", len(eval_ds))

    peft_config = None
    if args.lora_r > 0:
        try:
            from peft import LoraConfig, TaskType
        except ImportError as e:
            raise SystemExit("LoRA requires: pip install peft\n" f"{e}") from e

        peft_config = LoraConfig(
            r=args.lora_r,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
            target_modules=[
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
            ],
        )
        if state.is_main_process:
            logger.info("LoRA enabled: r=%d alpha=%d", args.lora_r, args.lora_alpha)

    torch_dtype = (
        torch.bfloat16 if args.bf16 else (torch.float16 if args.fp16 else torch.float32)
    )

    sft_kwargs: Dict[str, Any] = dict(
        output_dir=str(args.output_dir),
        num_train_epochs=args.num_train_epochs,
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=args.per_device_eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        warmup_ratio=args.warmup_ratio,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        save_total_limit=3,
        bf16=args.bf16,
        fp16=args.fp16 and not args.bf16,
        gradient_checkpointing=args.gradient_checkpointing,
        max_length=max_length,
        # Pre-tokenized rows use completion_mask; do not use assistant_only_loss (needs template {% generation %}).
        assistant_only_loss=False,
        completion_only_loss=True,
        dataset_kwargs={"skip_prepare_dataset": True},
        report_to="none",
        ddp_find_unused_parameters=False,
        seed=args.seed,
        model_init_kwargs={
            "torch_dtype": torch_dtype,
            "trust_remote_code": True,
        },
    )
    if eval_ds is not None:
        sft_kwargs["eval_strategy"] = "steps"
        sft_kwargs["eval_steps"] = args.eval_steps
        sft_kwargs["load_best_model_at_end"] = True
        sft_kwargs["metric_for_best_model"] = "eval_loss"
    else:
        sft_kwargs["eval_strategy"] = "no"

    sft_args = SFTConfig(**sft_kwargs)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    trainer = SFTTrainer(
        model=args.model_name_or_path,
        args=sft_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        processing_class=tokenizer,
        peft_config=peft_config,
    )

    resume_path: Optional[str] = None
    if args.resume_from_checkpoint is not None:
        rp = args.resume_from_checkpoint.expanduser().resolve()
        if not rp.is_dir():
            raise SystemExit(f"--resume_from_checkpoint is not a directory: {rp}")
        resume_path = str(rp)
        if state.is_main_process:
            logger.info("Resuming from explicit checkpoint: %s", resume_path)
    elif args.resume:
        resume_path = get_last_checkpoint(str(args.output_dir))
        if resume_path is None:
            if state.is_main_process:
                logger.warning(
                    "No checkpoint found under %s; starting training from scratch",
                    args.output_dir,
                )
        elif state.is_main_process:
            logger.info("Resuming from latest checkpoint: %s", resume_path)

    trainer.train(resume_from_checkpoint=resume_path)
    state.wait_for_everyone()
    if state.is_main_process:
        trainer.save_model(str(args.output_dir / "final_model"))
        tokenizer.save_pretrained(str(args.output_dir / "final_model"))
        logger.info("Saved to %s", args.output_dir / "final_model")


if __name__ == "__main__":
    main()
