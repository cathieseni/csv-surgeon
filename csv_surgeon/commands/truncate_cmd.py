"""truncate command – truncate string columns to a maximum length."""
from __future__ import annotations

import csv
import sys
from typing import IO


def add_subparser(subparsers):
    p = subparsers.add_parser("truncate", help="Truncate string columns to a max length")
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "--spec",
        metavar="COL:N",
        action="append",
        required=True,
        dest="specs",
        help="Column and max length, e.g. name:10",
    )
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.add_argument("--suffix", default="", help="Suffix appended when truncated, e.g. '...'")
    p.set_defaults(func=run)


def _parse_specs(raw: list[str]) -> dict[str, int]:
    specs: dict[str, int] = {}
    for item in raw:
        if ":" not in item:
            raise ValueError(f"Invalid truncate spec (expected COL:N): {item!r}")
        col, _, n_str = item.rpartition(":")
        if not n_str.isdigit() or int(n_str) < 0:
            raise ValueError(f"Length must be a non-negative integer, got: {n_str!r}")
        specs[col] = int(n_str)
    return specs


def _truncate_rows(rows, specs: dict[str, int], suffix: str):
    for row in rows:
        new_row = dict(row)
        for col, max_len in specs.items():
            if col in new_row and len(new_row[col]) > max_len:
                new_row[col] = new_row[col][:max_len] + suffix
        yield new_row


def _write(rows, fieldnames: list[str], dest: IO[str]) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args) -> None:
    specs = _parse_specs(args.specs)
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    result = list(_truncate_rows(rows, specs, args.suffix))

    if args.output:
        with open(args.output, "w", newline="") as out:
            _write(result, fieldnames, out)
    else:
        _write(result, fieldnames, sys.stdout)
