"""strip command – trim whitespace from column values."""
from __future__ import annotations

import csv
import sys
from typing import List


def add_subparser(subparsers):
    p = subparsers.add_parser("strip", help="Trim whitespace from column values")
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "-c", "--columns", metavar="COL", nargs="+",
        help="Columns to strip (default: all)"
    )
    p.add_argument("-o", "--output", metavar="FILE", help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_columns(columns_arg) -> List[str] | None:
    if not columns_arg:
        return None
    return [c.strip() for c in columns_arg]


def _strip_rows(rows, columns):
    for row in rows:
        if columns is None:
            yield {k: v.strip() for k, v in row.items()}
        else:
            yield {k: (v.strip() if k in columns else v) for k, v in row.items()}


def _write(fieldnames, rows, dest):
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


def run(args):
    columns = _parse_columns(getattr(args, "columns", None))
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = list(_strip_rows(reader, columns))

    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(fieldnames, rows, fh)
    else:
        _write(fieldnames, rows, sys.stdout)
