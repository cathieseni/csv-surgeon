"""Subcommand: dedupe — remove duplicate rows based on one or more key columns."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import IO, List, Optional


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "dedupe",
        help="Remove duplicate rows based on key column(s).",
    )
    p.add_argument("file", help="Input CSV file.")
    p.add_argument(
        "-k",
        "--keys",
        metavar="COL",
        nargs="+",
        required=True,
        help="Column name(s) that form the uniqueness key.",
    )
    p.add_argument(
        "--keep",
        choices=["first", "last"],
        default="first",
        help="Which duplicate to keep (default: first).",
    )
    p.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        default=None,
        help="Output file (default: stdout).",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    with open(args.file, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            print("error: empty or invalid CSV file", file=sys.stderr)
            sys.exit(1)
        fieldnames: List[str] = list(reader.fieldnames)
        missing = [k for k in args.keys if k not in fieldnames]
        if missing:
            print(f"error: unknown key column(s): {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
        rows = list(reader)

    deduped = _dedupe(rows, keys=args.keys, keep=args.keep)

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as out:
            _, fieldnames, deduped)
    else:
        _write(sys.stdout, fieldnames, deduped)


def _dedupe(
    rows: List[dict],
    keys: List[str],
    keep: str = "first",
) -> List[dict]:
    """Return rows with duplicates removed, preserving insertion order."""
    seen: set = set()
    result: List[dict] = []
    iterable = rows if keep == "first" else reversed(rows)
    for row in iterable:
        key = tuple(row.get(k, "") for k in keys)
        if key not in seen:
            seen.add(key)
            result.append(row)
    if keep == "last":
        result.reverse()
    return result


def _write(stream: IO[str], fieldnames: List[str], rows: List[dict]) -> None:
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
