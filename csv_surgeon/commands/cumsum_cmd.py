"""cumsum command – add cumulative sum columns for numeric fields."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("cumsum", help="Add cumulative-sum columns")
    p.add_argument(
        "columns",
        metavar="COL",
        nargs="+",
        help="Column names to accumulate (output column: <col>_cumsum)",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("-o", "--output", default="-", help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _cumsum_rows(rows: List[dict], columns: List[str]) -> List[dict]:
    accumulators = {col: 0.0 for col in columns}
    out = []
    for row in rows:
        new_row = dict(row)
        for col in columns:
            try:
                accumulators[col] += float(row[col])
            except (ValueError, KeyError):
                pass
            new_row[f"{col}_cumsum"] = accumulators[col]
        out.append(new_row)
    return out


def _write(rows: List[dict], dest) -> None:
    if not rows:
        return
    writer = csv.DictWriter(dest, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    result = _cumsum_rows(rows, args.columns)

    if args.output == "-":
        _write(result, sys.stdout)
    else:
        with open(args.output, "w", newline="") as fh:
            _write(result, fh)
