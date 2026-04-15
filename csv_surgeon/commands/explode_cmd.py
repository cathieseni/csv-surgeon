"""explode_cmd – split multi-value cells into separate rows."""
from __future__ import annotations

import argparse
import csv
import io
import sys
from typing import Iterator


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "explode",
        help="Split a multi-value column into one row per value.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument("-c", "--column", required=True, help="Column to explode.")
    p.add_argument(
        "-s",
        "--sep",
        default="|",
        help="Separator used inside the cell (default: '|').",
    )
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout).")
    p.set_defaults(func=run)


def _explode_rows(
    rows: list[dict],
    column: str,
    sep: str,
) -> Iterator[dict]:
    for row in rows:
        raw = row.get(column, "")
        values = [v.strip() for v in raw.split(sep)] if raw else [""]
        for val in values:
            new_row = dict(row)
            new_row[column] = val
            yield new_row


def run(args: argparse.Namespace) -> None:
    src = sys.stdin if args.input == "-" else open(args.input, newline="", encoding="utf-8")
    try:
        reader = csv.DictReader(src)
        if reader.fieldnames is None:
            sys.exit("explode: input CSV has no header row.")
        fieldnames = list(reader.fieldnames)
        if args.column not in fieldnames:
            sys.exit(f"explode: column '{args.column}' not found in CSV.")
        rows = list(reader)
    finally:
        if src is not sys.stdin:
            src.close()

    exploded = list(_explode_rows(rows, args.column, args.sep))
    _write(exploded, fieldnames, args.output)


def _write(
    rows: list[dict],
    fieldnames: list[str],
    output: str | None,
) -> None:
    dest = open(output, "w", newline="", encoding="utf-8") if output else sys.stdout
    try:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if output:
            dest.close()
