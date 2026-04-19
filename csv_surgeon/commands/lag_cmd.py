"""lag_cmd – add lag (previous-row) columns for numeric fields."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Optional


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("lag", help="Add lag columns for numeric fields")
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "--columns", "-c", required=True,
        help="Comma-separated column names to lag"
    )
    p.add_argument(
        "--periods", "-n", type=int, default=1,
        help="Number of periods to lag (default: 1)"
    )
    p.add_argument(
        "--fill", default="",
        help="Fill value for missing lag rows (default: empty string)"
    )
    p.add_argument("--output", "-o", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_columns(raw: str) -> List[str]:
    cols = [c.strip() for c in raw.split(",") if c.strip()]
    if not cols:
        raise ValueError("--columns must specify at least one column")
    return cols


def _lag_rows(rows: List[dict], columns: List[str], periods: int, fill: str) -> List[dict]:
    out = []
    for i, row in enumerate(rows):
        new_row = dict(row)
        for col in columns:
            lag_key = f"{col}_lag{periods}"
            if i < periods:
                new_row[lag_key] = fill
            else:
                new_row[lag_key] = rows[i - periods].get(col, fill)
        out.append(new_row)
    return out


def _write(rows: List[dict], fieldnames: List[str], dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            print("Empty CSV", file=sys.stderr)
            sys.exit(1)
        columns = _parse_columns(args.columns)
        for col in columns:
            if col not in reader.fieldnames:
                print(f"Column not found: {col}", file=sys.stderr)
                sys.exit(1)
        rows = list(reader)
        orig_fields = list(reader.fieldnames)

    lag_fields = [f"{c}_lag{args.periods}" for c in columns]
    fieldnames = orig_fields + lag_fields
    result = _lag_rows(rows, columns, args.periods, args.fill)

    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(result, fieldnames, fh)
    else:
        _write(result, fieldnames, sys.stdout)
