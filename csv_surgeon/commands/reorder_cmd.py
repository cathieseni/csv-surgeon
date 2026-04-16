"""reorder command – reorder CSV columns."""
from __future__ import annotations

import csv
import sys
from argparse import ArgumentParser, Namespace
from typing import IO


def add_subparser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "reorder",
        help="Reorder columns in a CSV file.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument(
        "--columns",
        required=True,
        help="Comma-separated list of column names in desired order.",
    )
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout).")
    p.set_defaults(func=run)


def _parse_columns(spec: str) -> list[str]:
    return [c.strip() for c in spec.split(",") if c.strip()]


def _reorder_rows(
    reader: csv.DictReader,
    columns: list[str],
) -> tuple[list[str], list[dict]]:
    fieldnames = reader.fieldnames or []
    missing = [c for c in columns if c not in fieldnames]
    if missing:
        raise ValueError(f"Columns not found in CSV: {missing}")
    # Append any columns not explicitly listed at the end
    extra = [f for f in fieldnames if f not in columns]
    ordered = columns + extra
    rows = [{col: row.get(col, "") for col in ordered} for row in reader]
    return ordered, rows


def _write(fieldnames: list[str], rows: list[dict], dest: IO[str]) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def run(args: Namespace) -> None:
    columns = _parse_columns(args.columns)
    src = sys.stdin if args.input == "-" else open(args.input, newline="")
    try:
        reader = csv.DictReader(src)
        ordered, rows = _reorder_rows(reader, columns)
    finally:
        if src is not sys.stdin:
            src.close()

    if args.output:
        with open(args.output, "w", newline="") as fout:
            _write(ordered, rows, fout)
    else:
        _write(ordered, rows, sys.stdout)
