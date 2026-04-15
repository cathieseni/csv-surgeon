"""transpose command – pivot rows into columns and vice-versa."""
from __future__ import annotations

import csv
import io
import sys
from argparse import ArgumentParser, Namespace
from typing import List


def add_subparser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "transpose",
        help="Transpose CSV rows into columns.",
    )
    p.add_argument("file", help="Input CSV file (use '-' for stdin).")
    p.add_argument(
        "-o", "--output",
        default=None,
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )
    p.set_defaults(func=run)


def _transpose_rows(rows: List[dict], fieldnames: List[str]) -> List[List[str]]:
    """Return a list-of-lists representing the transposed table.

    The first column of the output contains the original header names;
    each subsequent column corresponds to one input row.
    """
    result: List[List[str]] = []
    for field in fieldnames:
        result.append([field] + [row.get(field, "") for row in rows])
    return result


def _write(transposed: List[List[str]], dest: io.TextIOBase) -> None:
    writer = csv.writer(dest)
    for row in transposed:
        writer.writerow(row)


def run(args: Namespace) -> None:
    if args.file == "-":
        reader = csv.DictReader(sys.stdin)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    else:
        with open(args.file, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
            fieldnames = list(reader.fieldnames or [])

    if not fieldnames:
        return

    transposed = _transpose_rows(rows, fieldnames)

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            _write(transposed, fh)
    else:
        _write(transposed, sys.stdout)
