"""freq command – compute value frequency counts for one or more columns."""
from __future__ import annotations

import csv
import sys
from argparse import ArgumentParser, Namespace
from collections import Counter
from typing import Dict, List


def add_subparser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "freq",
        help="Count value frequencies for specified columns.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument(
        "columns",
        nargs="+",
        metavar="COLUMN",
        help="One or more column names to compute frequencies for.",
    )
    p.add_argument(
        "-o", "--output",
        default=None,
        metavar="FILE",
        help="Output CSV file (default: stdout).",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Only emit the top-N most common values per column.",
    )
    p.add_argument(
        "--desc",
        action="store_true",
        default=True,
        help="Sort by count descending (default: True).",
    )
    p.add_argument(
        "--asc",
        action="store_true",
        default=False,
        help="Sort by count ascending instead.",
    )
    p.set_defaults(func=run)


def _compute_freq(
    rows: List[Dict[str, str]],
    columns: List[str],
    limit: int | None,
    ascending: bool,
) -> List[Dict[str, str]]:
    result: List[Dict[str, str]] = []
    for col in columns:
        counter: Counter = Counter(row[col] for row in rows if col in row)
        ordered = counter.most_common()  # highest first
        if ascending:
            ordered = list(reversed(ordered))
        if limit is not None:
            ordered = ordered[:limit]
        for value, count in ordered:
            result.append({"column": col, "value": value, "count": str(count)})
    return result


def _write(out_rows: List[Dict[str, str]], dest: str | None) -> None:
    fieldnames = ["column", "value", "count"]
    fh = open(dest, "w", newline="") if dest else sys.stdout
    try:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)
    finally:
        if dest:
            fh.close()


def run(args: Namespace) -> None:
    fh = open(args.input, newline="") if args.input != "-" else sys.stdin
    try:
        reader = csv.DictReader(fh)
        rows = list(reader)
        headers = reader.fieldnames or []
    finally:
        if args.input != "-":
            fh.close()

    missing = [c for c in args.columns if c not in headers]
    if missing:
        print(f"freq: unknown columns: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    ascending = args.asc  # --asc overrides default desc
    out_rows = _compute_freq(rows, args.columns, args.limit, ascending)
    _write(out_rows, args.output)
