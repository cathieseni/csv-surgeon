"""uniq command – emit only rows where a column's value changes (like Unix uniq)."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import IO, Iterator, List, Optional


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "uniq",
        help="Filter consecutive duplicate values in a column (like Unix uniq).",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument("-c", "--column", required=True, help="Column to watch for changes.")
    p.add_argument(
        "-o", "--output", default=None, help="Output file (default: stdout)."
    )
    p.add_argument(
        "--count",
        action="store_true",
        help="Prepend a '__count__' column with the run length.",
    )
    p.set_defaults(func=run)


def _uniq_rows(
    rows: List[dict],
    column: str,
    include_count: bool,
) -> Iterator[dict]:
    """Yield one row per consecutive run; optionally include run length."""
    if not rows:
        return

    sentinel = object()
    current_val = sentinel
    run: List[dict] = []

    def _emit(run_rows: List[dict]) -> dict:
        row = dict(run_rows[0])
        if include_count:
            row = {"__count__": len(run_rows), **row}
        return row

    for row in rows:
        val = row.get(column)
        if val != current_val:
            if run:
                yield _emit(run)
            current_val = val
            run = [row]
        else:
            run.append(row)

    if run:
        yield _emit(run)


def _write(fieldnames: List[str], result_rows: List[dict], dest: IO[str]) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(result_rows)


def run(args: argparse.Namespace) -> None:
    src = sys.stdin if args.input == "-" else open(args.input, newline="")
    try:
        reader = csv.DictReader(src)
        rows = list(reader)
        fieldnames: List[str] = list(reader.fieldnames or [])
    finally:
        if src is not sys.stdin:
            src.close()

    if args.column not in fieldnames:
        raise ValueError(f"Column '{args.column}' not found in CSV.")

    result = list(_uniq_rows(rows, args.column, args.count))
    out_fields = (["__count__"] + fieldnames) if args.count else fieldnames

    if args.output:
        with open(args.output, "w", newline="") as f:
            _write(out_fields, result, f)
    else:
        _write(out_fields, result, sys.stdout)
