"""Sort command: sort CSV rows by one or more columns."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Optional


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("sort", help="Sort CSV rows by column(s)")
    p.add_argument("file", help="Input CSV file")
    p.add_argument(
        "-k", "--key",
        dest="keys",
        action="append",
        metavar="COLUMN[:asc|desc]",
        required=True,
        help="Column to sort by; append :desc for descending (repeatable)",
    )
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.add_argument("--inplace", action="store_true", help="Edit file in place")
    p.add_argument(
        "--numeric",
        action="store_true",
        help="Treat sort keys as numeric values",
    )
    p.set_defaults(func=run)


def _parse_key(spec: str):
    """Return (column_name, reverse) from 'col' or 'col:desc'."""
    if ":" in spec:
        col, direction = spec.rsplit(":", 1)
        reverse = direction.lower() == "desc"
    else:
        col, reverse = spec, False
    return col, reverse


def run(args: argparse.Namespace) -> None:
    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    keys = [_parse_key(k) for k in args.keys]

    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            print("error: empty CSV file", file=sys.stderr)
            sys.exit(1)
        fieldnames: List[str] = list(reader.fieldnames)
        rows = list(reader)

    for col, _ in reversed(keys):
        if col not in fieldnames:
            print(f"error: unknown column '{col}'", file=sys.stderr)
            sys.exit(1)

    def sort_key(row):
        vals = []
        for col, _ in keys:
            val = row[col]
            if args.numeric:
                try:
                    val = float(val)
                except ValueError:
                    pass
            vals.append(val)
        return vals

    # Apply per-key reversal via a stable multi-pass sort
    for col, reverse in reversed(keys):
        rows.sort(
            key=lambda r, c=col: (float(r[c]) if args.numeric else r[c]),
            reverse=reverse,
        )

    _write(rows, fieldnames, args)


def _write(rows, fieldnames, args) -> None:
    if args.inplace:
        dest = args.file
    elif args.output:
        dest = args.output
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        return

    with open(dest, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
