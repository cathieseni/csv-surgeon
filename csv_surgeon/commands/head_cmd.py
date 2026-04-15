"""head command – output the first N rows of a CSV file."""
from __future__ import annotations

import csv
import io
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Dict


def add_subparser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "head",
        help="Print the first N rows of a CSV (default 10).",
    )
    p.add_argument("file", help="Input CSV file.")
    p.add_argument(
        "-n",
        "--rows",
        type=int,
        default=10,
        metavar="N",
        help="Number of rows to output (default: 10).",
    )
    p.add_argument(
        "-o",
        "--output",
        default=None,
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )
    p.set_defaults(func=run)


def _head_rows(rows: List[Dict[str, str]], n: int) -> List[Dict[str, str]]:
    """Return up to *n* rows from *rows*."""
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    return rows[:n]


def run(args: Namespace) -> None:
    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    selected = _head_rows(rows, args.rows)
    _write(fieldnames, selected, args.output)


def _write(
    fieldnames: List[str],
    rows: List[Dict[str, str]],
    output: str | None,
) -> None:
    if output:
        dest = open(output, "w", newline="")
    else:
        dest = io.TextIOWrapper(sys.stdout.buffer, newline="")

    try:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if output:
            dest.close()
