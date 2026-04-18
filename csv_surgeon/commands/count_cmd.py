"""count command – print the number of data rows in a CSV."""
from __future__ import annotations

import csv
import sys
from argparse import ArgumentParser, Namespace
from typing import IO


def add_subparser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "count",
        help="Print the number of data rows (excluding header) in a CSV file.",
    )
    p.add_argument("file", help="Input CSV file")
    p.add_argument(
        "--no-header",
        action="store_true",
        default=False,
        help="Treat the first row as data, not a header",
    )
    p.add_argument(
        "-o", "--output",
        default=None,
        help="Write result to this file instead of stdout",
    )
    p.set_defaults(func=run)


def _count_rows(reader: csv.DictReader) -> int:
    return sum(1 for _ in reader)


def _write(count: int, dest: IO[str]) -> None:
    dest.write(f"{count}\n")


def run(args: Namespace) -> None:
    with open(args.file, newline="", encoding="utf-8") as fh:
        if args.no_header:
            reader = csv.reader(fh)
            count = sum(1 for _ in reader)
        else:
            reader = csv.DictReader(fh)
            count = _count_rows(reader)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as out:
            _write(count, out)
    else:
        _write(count, sys.stdout)
