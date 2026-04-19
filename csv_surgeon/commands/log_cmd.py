"""log command – apply log transformation to numeric columns."""
from __future__ import annotations

import argparse
import csv
import math
import sys
from typing import IO


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("log", help="Apply log transformation to numeric columns")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--columns", required=True, help="Comma-separated column names")
    p.add_argument(
        "--base",
        choices=["e", "2", "10"],
        default="e",
        help="Logarithm base (default: e)",
    )
    p.add_argument("--output", "-o", default="-", help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_columns(raw: str) -> list[str]:
    cols = [c.strip() for c in raw.split(",")]
    if not cols or any(c == "" for c in cols):
        raise ValueError(f"Invalid columns spec: {raw!r}")
    return cols


def _log_fn(base: str):
    if base == "2":
        return math.log2
    if base == "10":
        return math.log10
    return math.log


def _log_rows(rows: list[dict], columns: list[str], base: str) -> list[dict]:
    fn = _log_fn(base)
    out = []
    for row in rows:
        new = dict(row)
        for col in columns:
            try:
                val = float(row[col])
                if val <= 0:
                    raise ValueError(f"log undefined for non-positive value {val} in column {col!r}")
                new[col] = str(fn(val))
            except (KeyError, ValueError) as exc:
                raise ValueError(str(exc)) from exc
        out.append(new)
    return out


def _write(fieldnames: list[str], rows: list[dict], dest: IO[str]) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    columns = _parse_columns(args.columns)
    result = _log_rows(rows, columns, args.base)

    if args.output == "-":
        _write(fieldnames, result, sys.stdout)
    else:
        with open(args.output, "w", newline="") as fh:
            _write(fieldnames, result, fh)
