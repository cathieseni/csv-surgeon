"""zscore command – add a z-score column for a numeric field."""
from __future__ import annotations

import csv
import math
import sys
from typing import List, Dict


def add_subparser(subparsers):
    p = subparsers.add_parser("zscore", help="Append z-score column(s) for numeric field(s)")
    p.add_argument("columns", nargs="+", help="Column name(s) to compute z-score for")
    p.add_argument("--suffix", default="_zscore", help="Suffix appended to new column name (default: _zscore)")
    p.add_argument("--places", type=int, default=4, help="Decimal places to round result (default: 4)")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _compute_stats(rows: List[Dict], col: str):
    values = []
    for row in rows:
        try:
            values.append(float(row[col]))
        except (ValueError, KeyError):
            pass
    n = len(values)
    if n == 0:
        return 0.0, 1.0
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    std = math.sqrt(variance) if variance > 0 else 1.0
    return mean, std


def _add_zscores(rows: List[Dict], columns: List[str], suffix: str, places: int) -> List[Dict]:
    stats = {col: _compute_stats(rows, col) for col in columns}
    result = []
    for row in rows:
        new_row = dict(row)
        for col in columns:
            mean, std = stats[col]
            try:
                z = (float(row[col]) - mean) / std
                new_row[col + suffix] = str(round(z, places))
            except (ValueError, KeyError):
                new_row[col + suffix] = ""
        result.append(new_row)
    return result


def _write(rows: List[Dict], fieldnames: List[str], dest):
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args):
    with open(args.input, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        original_fields = list(reader.fieldnames or [])

    new_fields = original_fields + [col + args.suffix for col in args.columns]
    result = _add_zscores(rows, args.columns, args.suffix, args.places)

    if args.output:
        with open(args.output, "w", newline="") as f:
            _write(result, new_fields, f)
    else:
        _write(result, new_fields, sys.stdout)
