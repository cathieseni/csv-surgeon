"""abs command – replace numeric column values with their absolute value."""
from __future__ import annotations

import csv
import io
import sys
from typing import List


def add_subparser(subparsers):
    p = subparsers.add_parser("abs", help="Replace numeric values with their absolute value.")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("-c", "--columns", required=True, help="Comma-separated column names")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_columns(spec: str) -> List[str]:
    cols = [c.strip() for c in spec.split(",")]
    if not cols or any(c == "" for c in cols):
        raise ValueError(f"Invalid columns spec: {spec!r}")
    return cols


def _abs_rows(rows, columns):
    for row in rows:
        new_row = dict(row)
        for col in columns:
            if col not in new_row:
                raise KeyError(f"Column not found: {col!r}")
            val = new_row[col]
            try:
                f = float(val)
                new_row[col] = str(abs(int(f)) if f == int(f) else abs(f))
            except (ValueError, TypeError):
                pass  # leave non-numeric values unchanged
        yield new_row


def _write(fieldnames, rows, dest):
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args):
    columns = _parse_columns(args.columns)
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = list(_abs_rows(reader, columns))

    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(fieldnames, rows, fh)
    else:
        _write(fieldnames, rows, sys.stdout)
