"""window command – add a rolling aggregate column."""
from __future__ import annotations

import argparse
import csv
import sys
from collections import deque
from typing import Iterable, Iterator


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("window", help="Add rolling window aggregate column")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--col", required=True, help="Column to aggregate")
    p.add_argument("--size", type=int, required=True, help="Window size")
    p.add_argument(
        "--func",
        choices=["sum", "mean", "min", "max"],
        default="mean",
        help="Aggregation function (default: mean)",
    )
    p.add_argument("--out-col", default=None, help="Output column name (default: <col>_<func>_<size>)")
    p.add_argument("--output", "-o", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _window_rows(
    rows: Iterable[dict],
    col: str,
    size: int,
    func: str,
    out_col: str,
) -> Iterator[dict]:
    buf: deque[float] = deque(maxlen=size)
    for row in rows:
        try:
            buf.append(float(row[col]))
        except (ValueError, KeyError):
            buf.append(float("nan"))
        valid = [v for v in buf if v == v]  # exclude nan
        if not valid:
            result = ""
        elif func == "sum":
            result = str(sum(valid))
        elif func == "mean":
            result = str(sum(valid) / len(valid))
        elif func == "min":
            result = str(min(valid))
        else:
            result = str(max(valid))
        yield {**row, out_col: result}


def _write(rows: Iterable[dict], fieldnames: list[str], dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    func_name = args.func if isinstance(args.func, str) else "mean"
    out_col = args.out_col or f"{args.col}_{func_name}_{args.size}"
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or []) + [out_col]
        rows = list(_window_rows(reader, args.col, args.size, func_name, out_col))
    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(rows, fieldnames, fh)
    else:
        _write(rows, fieldnames, sys.stdout)
