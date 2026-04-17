"""split command – split a CSV into multiple files by unique values in a column."""
from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def add_subparser(subparsers: Any) -> None:
    p = subparsers.add_parser("split", help="Split CSV by column values")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--by", required=True, metavar="COLUMN", help="Column to split on")
    p.add_argument(
        "--outdir",
        default=".",
        metavar="DIR",
        help="Output directory (default: current dir)",
    )
    p.add_argument(
        "--prefix",
        default="",
        metavar="PREFIX",
        help="Filename prefix for output files",
    )
    p.set_defaults(func=run)


def _split_rows(
    rows: list[dict], column: str
) -> dict[str, list[dict]]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        key = row[column]
        buckets[key].append(row)
    return dict(buckets)


def _write(
    buckets: dict[str, list[dict]],
    fieldnames: list[str],
    outdir: str,
    prefix: str,
) -> list[str]:
    os.makedirs(outdir, exist_ok=True)
    written: list[str] = []
    for key, rows in buckets.items():
        safe_key = str(key).replace(os.sep, "_").replace(" ", "_")
        filename = os.path.join(outdir, f"{prefix}{safe_key}.csv")
        with open(filename, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        written.append(filename)
    return written


def run(args: Any) -> None:
    path = Path(args.input)
    if not path.exists():
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if args.by not in fieldnames:
        print(f"Error: column '{args.by}' not found", file=sys.stderr)
        sys.exit(1)

    buckets = _split_rows(rows, args.by)
    written = _write(buckets, fieldnames, args.outdir, args.prefix)
    for f in sorted(written):
        print(f)
