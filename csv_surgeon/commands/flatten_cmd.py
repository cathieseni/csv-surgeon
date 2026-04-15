"""flatten command – split multi-value cells into separate rows."""
from __future__ import annotations

import csv
import io
import sys
from argparse import ArgumentParser, Namespace
from typing import Iterator


def add_subparser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "flatten",
        help="Split multi-value cells into separate rows.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument(
        "-c", "--column", required=True, dest="column",
        help="Column whose values should be split.",
    )
    p.add_argument(
        "-d", "--delimiter", default="|", dest="sep",
        help="Separator used inside the cell (default: '|').",
    )
    p.add_argument(
        "-o", "--output", default=None, dest="output",
        help="Output file (default: stdout).",
    )
    p.set_defaults(func=run)


def _flatten_rows(
    rows: list[dict],
    column: str,
    sep: str,
) -> Iterator[dict]:
    for row in rows:
        raw = row.get(column, "")
        parts = [v.strip() for v in raw.split(sep)] if raw else [""]
        for part in parts:
            yield {**row, column: part}


def run(args: Namespace) -> None:
    if args.input == "-":
        reader = csv.DictReader(sys.stdin)
    else:
        fh = open(args.input, newline="", encoding="utf-8")
        reader = csv.DictReader(fh)

    fieldnames = reader.fieldnames or []
    rows = list(reader)

    if args.column not in fieldnames:
        sys.exit(f"Error: column '{args.column}' not found in CSV.")

    flattened = list(_flatten_rows(rows, args.column, args.sep))
    _write(flattened, fieldnames, args.output)


def _write(
    rows: list[dict],
    fieldnames: list[str],
    output: str | None,
) -> None:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    text = buf.getvalue()

    if output:
        with open(output, "w", newline="", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
