"""Subcommand: fill — fill empty cells in specified columns with a default value."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import Dict, IO, List


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "fill",
        help="Fill empty cells with a default value.",
    )
    p.add_argument("file", help="Input CSV file.")
    p.add_argument(
        "-s",
        "--spec",
        metavar="COL=VALUE",
        nargs="+",
        required=True,
        help="One or more COL=VALUE pairs specifying fill values per column.",
    )
    p.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        default=None,
        help="Output file (default: stdout).",
    )
    p.set_defaults(func=run)


def _parse_specs(specs: List[str]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for spec in specs:
        if "=" not in spec:
            raise ValueError(f"Invalid fill spec (expected COL=VALUE): {spec!r}")
        col, _, value = spec.partition("=")
        result[col.strip()] = value
    return result


def run(args: argparse.Namespace) -> None:
    try:
        fill_map = _parse_specs(args.spec)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    with open(args.file, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            print("error: empty or invalid CSV file", file=sys.stderr)
            sys.exit(1)
        fieldnames: List[str] = list(reader.fieldnames)
        missing = [c for c in fill_map if c not in fieldnames]
        if missing:
            print(f"error: unknown column(s): {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
        rows = [_fill_row(row, fill_map) for row in reader]

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as out:
            _write(out, fieldnames, rows)
    else:
        _write(sys.stdout, fieldnames, rows)


def _fill_row(row: dict, fill_map: Dict[str, str]) -> dict:
    return {
        col: (fill_map[col] if (not val and col in fill_map) else val)
        for col, val in row.items()
    }


def _write(stream: IO[str], fieldnames: List[str], rows: List[dict]) -> None:
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
