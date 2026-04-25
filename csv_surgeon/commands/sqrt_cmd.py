"""sqrt command – add square-root columns for numeric fields."""
from __future__ import annotations

import csv
import math
import sys
from typing import Iterable


def add_subparser(subparsers):
    p = subparsers.add_parser(
        "sqrt",
        help="Add square-root of numeric columns as new columns.",
    )
    p.add_argument(
        "columns",
        help="Comma-separated column names to take the square root of.",
    )
    p.add_argument(
        "--suffix",
        default="_sqrt",
        help="Suffix appended to source column name for the new column (default: _sqrt).",
    )
    p.add_argument(
        "--output", "-o",
        default=None,
        help="Output file (default: stdout).",
    )
    p.set_defaults(func=run)


def _parse_columns(columns_str: str) -> list[str]:
    cols = [c.strip() for c in columns_str.split(",")]
    if not cols or any(c == "" for c in cols):
        raise ValueError(f"Invalid columns specification: {columns_str!r}")
    return cols


def _sqrt_rows(
    rows: Iterable[dict],
    columns: list[str],
    suffix: str,
) -> list[dict]:
    out = []
    for row in rows:
        new_row = dict(row)
        for col in columns:
            try:
                val = float(row[col])
                if val < 0:
                    new_row[col + suffix] = ""
                else:
                    new_row[col + suffix] = str(math.sqrt(val))
            except (ValueError, KeyError):
                new_row[col + suffix] = ""
        out.append(new_row)
    return out


def _write(rows: list[dict], fieldnames: list[str], dest):
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args):
    columns = _parse_columns(args.columns)
    suffix = args.suffix

    with open(args.file, newline="") as fh:
        reader = csv.DictReader(fh)
        original_fields = reader.fieldnames or []
        rows = list(reader)

    new_fields = list(original_fields)
    for col in columns:
        if col not in new_fields:
            raise SystemExit(f"Column not found: {col!r}")
        new_fields.append(col + suffix)

    result = _sqrt_rows(rows, columns, suffix)

    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(result, new_fields, fh)
    else:
        _write(result, new_fields, sys.stdout)
