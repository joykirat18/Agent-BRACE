#!/usr/bin/env python3
"""Count min/max occurrences of <|im_end|> per JSONL response."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path


TOKEN = "<|im_end|>"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count min/max number of '<|im_end|>' tokens per response in a JSONL file."
    )
    parser.add_argument("jsonl_path", type=Path, help="Path to JSONL file")
    parser.add_argument(
        "--response-key",
        default="response",
        help="JSON key that contains the response text (default: response)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.jsonl_path.exists():
        raise FileNotFoundError(f"File not found: {args.jsonl_path}")

    n_rows = 0
    min_count = None
    max_count = None
    min_rows = []
    max_rows = []
    missing_key_rows = []
    count_freq: Counter[int] = Counter()

    with args.jsonl_path.open("r", encoding="utf-8") as f:
        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue
            n_rows += 1
            obj = json.loads(line)
            response = obj.get(args.response_key)
            if not isinstance(response, str):
                missing_key_rows.append(line_no)
                continue

            count = response.count(TOKEN)
            count_freq[count] += 1
            instance_id = obj.get("instance_id")
            row_meta = (line_no, instance_id, count)

            if min_count is None or count < min_count:
                min_count = count
                min_rows = [row_meta]
            elif count == min_count:
                min_rows.append(row_meta)

            if max_count is None or count > max_count:
                max_count = count
                max_rows = [row_meta]
            elif count == max_count:
                max_rows.append(row_meta)

    print(f"File: {args.jsonl_path}")
    print(f"Token: {TOKEN}")
    print(f"Rows processed: {n_rows}")
    print()

    if min_count is None:
        print("No valid rows found with a string response.")
    else:
        print(f"Min per response: {min_count}")
        print("Rows with min (line_no, instance_id, count):")
        for row in min_rows:
            print(f"  {row}")
        print()
        print(f"Max per response: {max_count}")
        print("Rows with max (line_no, instance_id, count):")
        for row in max_rows:
            print(f"  {row}")
        print()
        print("Full distribution (count -> frequency):")
        for c in sorted(count_freq):
            print(f"  {c} -> {count_freq[c]}")

    if missing_key_rows:
        print()
        print(
            f"Warning: {len(missing_key_rows)} rows missing string key "
            f"'{args.response_key}': {missing_key_rows}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
