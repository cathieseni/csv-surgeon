"""movavg command – add a moving average column for a numeric field."""
from __future__ import annotations

import argparse
import csv
import sys
from collections import deque
from typing import Iterator


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("movavg", help="Add a moving-average column")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--col", required=True, help="Source numeric column")
    p.add_argument("--window", type=int, default=3, help="Window size (default 3)")
    p.add_argument("--out-col", default=None, help="Output column name (default: <col>_mavg)")
    p.add_argument("--output", "-o", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _movavg_rows(
    rows: list[dict],
    col: str,
    window: int,
    out_col: str,
) -> Iterator[dict]:
    buf: deque[float] = deque(maxlen=window)
    for row in rows:
        try:
            buf.append(float(row[col]))
        except (ValueError, KeyError):
            buf.append(float("nan"))
        avg = sum(v for v in buf if v == v) / max(len([v for v in buf if v == v]), 1)
        yield {**row, out_col: f"{avg:.6g}"}


def _write(fieldnames: list[str], rows: Iterator[dict], dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


def run(args: argparse.Namespace) -> None:
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            sys.exit("error: empty CSV")
        all_rows = list(reader)
        fieldnames = list(reader.fieldnames)

    out_col = args.out_col or f"{args.col}_mavg"
    if out_col not in fieldnames:
        fieldnames.append(out_col)

    result = _movavg_rows(all_rows, args.col, args.window, out_col)

    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(fieldnames, result, fh)
    else:
        _write(fieldnames, result, sys.stdout)
