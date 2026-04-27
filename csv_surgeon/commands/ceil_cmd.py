"""ceil command – round numeric column values up to the nearest integer (or multiple)."""
from __future__ import annotations

import argparse
import csv
import math
import sys
from typing import IO, Iterator


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("ceil", help="Ceiling-round numeric columns.")
    p.add_argument("file", help="Input CSV file (use '-' for stdin).")
    p.add_argument(
        "-c",
        "--columns",
        required=True,
        help="Comma-separated column names to apply ceiling to.",
    )
    p.add_argument(
        "-m",
        "--multiple",
        type=float,
        default=1.0,
        help="Round up to the nearest multiple of this value (default: 1).",
    )
    p.add_argument("-o", "--output", help="Output file (default: stdout).")
    p.set_defaults(func=run)


def _parse_columns(columns_str: str) -> list[str]:
    cols = [c.strip() for c in columns_str.split(",") if c.strip()]
    if not cols:
        raise ValueError("--columns must specify at least one column name.")
    return cols


def _ceil_rows(
    rows: Iterator[dict],
    columns: list[str],
    multiple: float,
) -> Iterator[dict]:
    if multiple <= 0:
        raise ValueError("--multiple must be a positive number.")
    for row in rows:
        out = dict(row)
        for col in columns:
            raw = out.get(col, "")
            try:
                val = float(raw)
                ceiled = math.ceil(val / multiple) * multiple
                # Preserve int-like output when multiple is a whole number
                if multiple == int(multiple):
                    out[col] = str(int(ceiled))
                else:
                    out[col] = str(ceiled)
            except (ValueError, TypeError):
                pass  # leave non-numeric values unchanged
        yield out


def _write(rows: Iterator[dict], fieldnames: list[str], dest: IO[str]) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    src = sys.stdin if args.file == "-" else open(args.file, newline="")  # noqa: WPS515
    try:
        reader = csv.DictReader(src)
        fieldnames = list(reader.fieldnames or [])
        columns = _parse_columns(args.columns)
        ceiled = _ceil_rows(reader, columns, args.multiple)
        if args.output:
            with open(args.output, "w", newline="") as fout:
                _write(ceiled, fieldnames, fout)
        else:
            _write(ceiled, fieldnames, sys.stdout)
    finally:
        if src is not sys.stdin:
            src.close()
