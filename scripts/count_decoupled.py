#!/usr/bin/env python3
"""Mean prompts (rows) per validation example in decoupled JSONL.

Each line is one model call. Examples are identified by ``gts`` (ground-truth /
game id); multiple lines share the same ``gts`` for one episode. This script
counts rows per ``gts`` and reports the mean and other stats across examples.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl_path", type=Path, help="Path to decoupled JSONL")
    parser.add_argument(
        "--gts-key",
        default="gts",
        help="JSON key for example id (default: gts)",
    )
    parser.add_argument(
        "--per-example",
        action="store_true",
        help="Print one JSON object per line: gts, n_prompts",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.jsonl_path.exists():
        raise FileNotFoundError(f"File not found: {args.jsonl_path}")

    counts: Counter[str] = Counter()
    missing_gts_lines: list[int] = []
    n_rows = 0

    with args.jsonl_path.open("r", encoding="utf-8") as f:
        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue
            n_rows += 1
            obj = json.loads(line)
            gts = obj.get(args.gts_key)
            if gts is None or gts == "":
                missing_gts_lines.append(line_no)
                continue
            key = str(gts)
            counts[key] += 1

    if args.per_example:
        for gts in sorted(counts.keys()):
            rec = {"gts": gts, "n_prompts": counts[gts]}
            print(json.dumps(rec, ensure_ascii=False))
        return 0

    per_example = list(counts.values())
    n_examples = len(per_example)

    def stat_line(name: str, xs: list[int]) -> str:
        if not xs:
            return f"{name}: (none)"
        return (
            f"{name}: n={len(xs)}  min={min(xs)}  max={max(xs)}  "
            f"mean={statistics.mean(xs):.4g}  median={statistics.median(xs):.4g}"
        )

    print(f"File: {args.jsonl_path}")
    print(f"Total rows (prompts): {n_rows}")
    print(f"Unique {args.gts_key!r} (examples): {n_examples}")
    if missing_gts_lines:
        print(
            f"Rows missing {args.gts_key!r}: {len(missing_gts_lines)} "
            f"(first line nos: {missing_gts_lines[:10]})"
        )
    print()
    if n_examples and n_rows == sum(per_example):
        print(f"Sanity: sum of per-example counts == total rows ({n_rows})")
    print(stat_line("Prompts per example", per_example))
    if len(per_example) >= 2:
        print(
            f"stdev={statistics.stdev(per_example):.4g}  "
            f"pstdev={statistics.pstdev(per_example):.4g}"
        )
    if per_example:
        dist = Counter(per_example)
        print()
        print("Distribution (n_prompts -> how many examples):")
        for k in sorted(dist.keys()):
            print(f"  {k} prompts: {dist[k]} examples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
