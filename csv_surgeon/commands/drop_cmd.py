"""drop_cmd – remove columns from a CSV."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Sequence


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("drop", help="Drop one or more columns from a CSV.")
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument(
        "-c",
        "--columns",
        required=True,
        help="Comma-separated list of column names to drop.",
    )
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout).")
    p.add_argument(
        "--inplace",
        action="store_true",
        help="Edit the input file in place (ignored when input is stdin).",
    )
    p.set_defaults(func=run)


def _parse_columns(spec: str) -> List[str]:
    """Split a comma-separated column spec into a list of names."""
    return [c.strip() for c in spec.split(",") if c.strip()]


def run(args) -> None:
    columns_to_drop = _parse_columns(args.columns)

    if args.input == "-":
        source = sys.stdin
    else:
        source = open(args.input, newline="", encoding="utf-8")

    try:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row.")

        unknown = set(columns_to_drop) - set(reader.fieldnames)
        if unknown:
            raise ValueError(f"Column(s) not found in CSV: {', '.join(sorted(unknown))}")

        kept_fields = [f for f in reader.fieldnames if f not in columns_to_drop]
        rows = [{k: row[k] for k in kept_fields} for row in reader]
    finally:
        if args.input != "-":
            source.close()

    inplace = getattr(args, "inplace", False) and args.input != "-"
    output_path = args.input if inplace else getattr(args, "output", None)

    _write(kept_fields, rows, output_path)


def _write(fieldnames: Sequence[str], rows: list, output_path) -> None:
    if output_path is None:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    else:
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
