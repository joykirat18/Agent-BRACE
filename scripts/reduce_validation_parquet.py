#!/usr/bin/env python3
"""Keep only the first N rows of a parquet file and write to a new path."""
from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

import pandas as pd


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    default_input = repo_root / "data-basic-parquet-MEM1" / "test.parquet"

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--path",
        type=Path,
        default=default_input,
        help=f"Input parquet (default: {default_input})",
    )
    p.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output parquet (default: <input_stem>_head<N>.parquet beside input)",
    )
    p.add_argument(
        "--n",
        type=int,
        default=50,
        help="Number of rows to keep from the start of the file",
    )
    args = p.parse_args()
    inp = args.path.resolve()
    if not inp.is_file():
        raise SystemExit(f"File not found: {inp}")

    if args.output is None:
        out_path = inp.with_name(f"{inp.stem}_head{args.n}{inp.suffix}")
    else:
        out_path = args.output.resolve()

    if out_path == inp:
        raise SystemExit("Refusing to write: --output is the same as --path")

    df = pd.read_parquet(inp)
    n = min(args.n, len(df))
    out = df.iloc[:n].copy()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(suffix=".parquet", dir=out_path.parent)
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        out.to_parquet(tmp_path, index=False)
        os.replace(tmp_path, out_path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise

    print(f"Wrote {len(out)} rows to {out_path} (read {len(df)} rows from {inp})")


if __name__ == "__main__":
    main()
