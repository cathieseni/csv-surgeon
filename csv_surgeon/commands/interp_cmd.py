"""interp: fill missing (empty) numeric values by linear interpolation."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Optional


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("interp", help="Linearly interpolate missing numeric values")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("-c", "--columns", required=True, help="Comma-separated column names to interpolate")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_columns(columns_str: str) -> List[str]:
    cols = [c.strip() for c in columns_str.split(",")]
    if not cols or any(c == "" for c in cols):
        raise ValueError("columns must be a non-empty comma-separated list")
    return cols


def _interp_column(values: List[str]) -> List[str]:
    """Return list with empty strings filled via linear interpolation."""
    # Convert to float or None
    nums: List[Optional[float]] = []
    for v in values:
        stripped = v.strip()
        try:
            nums.append(float(stripped) if stripped != "" else None)
        except ValueError:
            nums.append(None)

    result = list(nums)
    n = len(nums)
    i = 0
    while i < n:
        if result[i] is None:
            # find previous known
            left_i = i - 1
            left_v = result[left_i] if left_i >= 0 else None
            # find next known
            right_i = i
            while right_i < n and result[right_i] is None:
                right_i += 1
            right_v = result[right_i] if right_i < n else None

            for j in range(i, right_i):
                if left_v is None and right_v is None:
                    result[j] = 0.0
                elif left_v is None:
                    result[j] = right_v
                elif right_v is None:
                    result[j] = left_v
                else:
                    span = right_i - left_i
                    result[j] = left_v + (right_v - left_v) * (j - left_i) / span
            i = right_i
        else:
            i += 1

    return [
        (str(int(v)) if v == int(v) else str(v)) if orig.strip() == "" else orig
        for v, orig in zip(result, values)
    ]


def _interp_rows(rows: List[dict], columns: List[str]) -> List[dict]:
    if not rows:
        return rows
    col_values = {col: [r.get(col, "") for r in rows] for col in columns}
    filled = {col: _interp_column(vals) for col, vals in col_values.items()}
    result = []
    for i, row in enumerate(rows):
        new_row = dict(row)
        for col in columns:
            new_row[col] = filled[col][i]
        result.append(new_row)
    return result


def _write(rows: List[dict], fieldnames: List[str], dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    columns = _parse_columns(args.columns)
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    rows = _interp_rows(rows, columns)

    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(rows, fieldnames, fh)
    else:
        _write(rows, fieldnames, sys.stdout)
