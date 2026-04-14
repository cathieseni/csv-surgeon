"""slice_cmd – extract a row range from a CSV file."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import Dict, List, Optional


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("slice", help="Extract a row range from a CSV")
    p.add_argument("input", help="Input CSV file (use '-' for stdin)")
    p.add_argument("--start", type=int, default=0, help="First row index (0-based, default 0)")
    p.add_argument("--end", type=int, default=None, help="Last row index exclusive (default: EOF)")
    p.add_argument("--step", type=int, default=1, help="Step between rows (default 1)")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _slice_rows(
    rows: List[Dict[str, str]],
    start: int,
    end: Optional[int],
    step: int,
) -> List[Dict[str, str]]:
    if step < 1:
        raise ValueError("--step must be >= 1")
    return rows[start:end:step]


def run(args: argparse.Namespace) -> None:
    src = sys.stdin if args.input == "-" else open(args.input, newline="", encoding="utf-8")
    try:
        reader = csv.DictReader(src)
        rows = list(reader)
        fieldnames: List[str] = list(reader.fieldnames or [])
    finally:
        if src is not sys.stdin:
            src.close()

    sliced = _slice_rows(rows, args.start, args.end, args.step)
    _write(sliced, fieldnames, args.output)


def _write(
    rows: List[Dict[str, str]],
    fieldnames: List[str],
    output: Optional[str],
) -> None:
    dst = sys.stdout if output is None else open(output, "w", newline="", encoding="utf-8")
    try:
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if dst is not sys.stdout:
            dst.close()
