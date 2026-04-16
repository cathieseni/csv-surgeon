"""merge command – vertically stack two CSV files (union)."""
from __future__ import annotations

import csv
import sys
from typing import IO


def add_subparser(subparsers):
    p = subparsers.add_parser("merge", help="Vertically merge two CSV files")
    p.add_argument("file", help="Primary CSV file")
    p.add_argument("other", help="CSV file to append")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.add_argument(
        "--fill",
        action="store_true",
        help="Fill missing columns with empty string instead of raising",
    )
    p.set_defaults(func=run)


def _load(path: str):
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return fieldnames, rows


def _merge_rows(fields_a, rows_a, fields_b, rows_b, fill: bool):
    all_fields = list(fields_a)
    for f in fields_b:
        if f not in all_fields:
            all_fields.append(f)

    extra_a = [f for f in all_fields if f not in fields_a]
    extra_b = [f for f in all_fields if f not in fields_b]

    if not fill:
        if extra_a:
            raise ValueError(f"Columns in 'other' not in primary: {extra_a}. Use --fill to allow.")
        if extra_b:
            raise ValueError(f"Columns in primary not in 'other': {extra_b}. Use --fill to allow.")

    merged = []
    for row in rows_a:
        merged.append({f: row.get(f, "") for f in all_fields})
    for row in rows_b:
        merged.append({f: row.get(f, "") for f in all_fields})
    return all_fields, merged


def _write(fieldnames, rows, dest: IO):
    writer = csv.DictWriter(dest, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def run(args):
    fields_a, rows_a = _load(args.file)
    fields_b, rows_b = _load(args.other)
    fieldnames, rows = _merge_rows(fields_a, rows_a, fields_b, rows_b, fill=args.fill)
    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(fieldnames, rows, fh)
    else:
        _write(fieldnames, rows, sys.stdout)
