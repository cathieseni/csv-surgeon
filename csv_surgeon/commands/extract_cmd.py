"""extract_cmd – extract a subset of columns into a new CSV."""
from __future__ import annotations

import csv
import sys
from argparse import ArgumentParser, Namespace
from typing import List


def add_subparser(sub) -> None:
    p: ArgumentParser = sub.add_parser(
        "extract",
        help="Extract specific columns from a CSV",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "-c",
        "--columns",
        required=True,
        help="Comma-separated list of column names to extract",
    )
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_columns(columns_str: str) -> List[str]:
    cols = [c.strip() for c in columns_str.split(",")]
    if not cols or any(c == "" for c in cols):
        raise ValueError(f"Invalid column specification: {columns_str!r}")
    return cols


def _extract_rows(rows, columns: List[str]):
    """Yield dicts containing only the requested columns."""
    for row in rows:
        missing = [c for c in columns if c not in row]
        if missing:
            raise KeyError(f"Column(s) not found in CSV: {missing}")
        yield {c: row[c] for c in columns}


def _write(rows, fieldnames: List[str], dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


def run(args: Namespace) -> None:
    columns = _parse_columns(args.columns)
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        extracted = list(_extract_rows(reader, columns))

    if args.output:
        with open(args.output, "w", newline="") as out:
            _write(extracted, columns, out)
    else:
        _write(extracted, columns, sys.stdout)
