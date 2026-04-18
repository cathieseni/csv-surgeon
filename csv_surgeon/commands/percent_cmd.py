"""percent command – add a column with each row's percentage of a numeric column total."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Dict


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("percent", help="Add a percentage column for a numeric field")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--col", required=True, help="Numeric column to compute percentages for")
    p.add_argument("--out-col", default=None, help="Name of the new percentage column (default: <col>_pct)")
    p.add_argument("--decimals", type=int, default=2, help="Decimal places (default: 2)")
    p.add_argument("--output", "-o", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _compute_total(rows: List[Dict[str, str]], col: str) -> float:
    total = 0.0
    for row in rows:
        try:
            total += float(row[col])
        except (ValueError, KeyError):
            pass
    return total


def _add_percent(rows: List[Dict[str, str]], col: str, out_col: str, decimals: int, total: float) -> List[Dict[str, str]]:
    result = []
    for row in rows:
        new_row = dict(row)
        try:
            val = float(row[col])
            pct = round((val / total * 100) if total != 0 else 0.0, decimals)
        except (ValueError, KeyError):
            pct = ""
        new_row[out_col] = str(pct) if pct != "" else ""
        result.append(new_row)
    return result


def _write(fieldnames, rows, dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            sys.exit("error: empty CSV")
        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    col = args.col
    if col not in fieldnames:
        sys.exit(f"error: column '{col}' not found")

    out_col = args.out_col or f"{col}_pct"
    total = _compute_total(rows, col)
    new_rows = _add_percent(rows, col, out_col, args.decimals, total)
    new_fieldnames = fieldnames + [out_col]

    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(new_fieldnames, new_rows, fh)
    else:
        _write(new_fieldnames, new_rows, sys.stdout)
