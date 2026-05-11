#!/usr/bin/env python3
"""Count environment steps per row in validation JSONL via ``user\\n`` markers.

After each model action, the environment appends a ``user\\n`` block with the new
observation. Counting ``user\\n`` in ``output`` is one step per environment round
(same as counting real actions in this chat template, and robust to prompt text
like ``<action> </action>`` in instructions).
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

USER_TURN = "user\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl_path", type=Path, help="Path to JSONL file")
    parser.add_argument(
        "--output-key",
        default="output",
        help="JSON key holding the trajectory text (default: output)",
    )
    parser.add_argument(
        "--per-row",
        action="store_true",
        help="Print one JSON object per line: gts, score, reward, n_steps, success",
    )
    return parser.parse_args()


def count_steps(text: str) -> int:
    return text.count(USER_TURN)


def is_success(obj: dict) -> bool:
    r = obj.get("reward")
    if r is not None and float(r) >= 1.0:
        return True
    s = obj.get("score")
    if s is not None and float(s) >= 1.0:
        return True
    return False


def main() -> int:
    args = parse_args()
    if not args.jsonl_path.exists():
        raise FileNotFoundError(f"File not found: {args.jsonl_path}")

    n_rows = 0
    missing_key_rows: list[int] = []
    success_steps: list[int] = []
    fail_steps: list[int] = []
    all_steps: list[int] = []

    with args.jsonl_path.open("r", encoding="utf-8") as f:
        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue
            n_rows += 1
            obj = json.loads(line)
            out = obj.get(args.output_key)
            if not isinstance(out, str):
                missing_key_rows.append(line_no)
                n = 0
            else:
                n = count_steps(out)

            all_steps.append(n)
            ok = is_success(obj)
            if ok:
                success_steps.append(n)
            else:
                fail_steps.append(n)

            if args.per_row:
                rec = {
                    "line": line_no,
                    "gts": obj.get("gts"),
                    "score": obj.get("score"),
                    "reward": obj.get("reward"),
                    "n_steps": n,
                    "success": ok,
                }
                print(json.dumps(rec, ensure_ascii=False))

    if args.per_row:
        return 0

    def stat_line(name: str, xs: list[int]) -> str:
        if not xs:
            return f"{name}: (none)"
        return (
            f"{name}: n={len(xs)}  min={min(xs)}  max={max(xs)}  "
            f"mean={statistics.mean(xs):.4g}  median={statistics.median(xs):.4g}"
        )

    print(f"File: {args.jsonl_path}")
    print(f"Rows processed: {n_rows}")
    if missing_key_rows:
        print(f"Rows missing string {args.output_key!r}: {len(missing_key_rows)} (first lines: {missing_key_rows[:10]})")
    print()
    print(stat_line("Steps (user\\n count) — all rows", all_steps))
    print(stat_line("Steps (user\\n count) — successful", success_steps))
    print(stat_line("Steps (user\\n count) — unsuccessful", fail_steps))
    print()
    print(
        "Each step is counted as one `user\\n` substring in `output` (one per env "
        "observation after an action). The JSON field `step` is usually the rollout "
        "horizon cap, not this count."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
