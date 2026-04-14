"""Subcommand: rename — rename one or more columns in a CSV file."""

from __future__ import annotations

import argparse
import csv
import sys
from typing import Dict, List, Optional


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "rename",
        help="Rename columns in a CSV file.",
    )
    p.add_argument("input", help="Input CSV file.")
    p.add_argument(
        "-r",
        "--rename",
        metavar="OLD:NEW",
        action="append",
        required=True,
        dest="specs",
        help="Column rename spec in OLD:NEW format. Repeatable.",
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
    """Parse a list of 'OLD:NEW' strings into a mapping."""
    mapping: Dict[str, str] = {}
    for spec in specs:
        if ":" not in spec:
            raise ValueError(
                f"Invalid rename spec {spec!r}: expected format OLD:NEW"
            )
        old, new = spec.split(":", 1)
        old, new = old.strip(), new.strip()
        if not old or not new:
            raise ValueError(
                f"Invalid rename spec {spec!r}: OLD and NEW must be non-empty"
            )
        mapping[old] = new
    return mapping


def run(args: argparse.Namespace) -> None:
    try:
        mapping = _parse_specs(args.specs)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            print("error: empty or missing header row", file=sys.stderr)
            sys.exit(1)

        unknown = set(mapping) - set(reader.fieldnames)
        if unknown:
            print(
                f"error: columns not found in header: {', '.join(sorted(unknown))}",
                file=sys.stderr,
            )
            sys.exit(1)

        new_fieldnames = [
            mapping.get(col, col) for col in reader.fieldnames
        ]
        rows = list(reader)

    _write(rows, reader.fieldnames, new_fieldnames, mapping, args.output)


def _write(
    rows: List[Dict],
    old_fieldnames: List[str],
    new_fieldnames: List[str],
    mapping: Dict[str, str],
    output: Optional[str],
) -> None:
    dest = open(output, "w", newline="", encoding="utf-8") if output else sys.stdout
    try:
        writer = csv.DictWriter(dest, fieldnames=new_fieldnames)
        writer.writeheader()
        for row in rows:
            new_row = {mapping.get(k, k): v for k, v in row.items()}
            writer.writerow(new_row)
    finally:
        if output:
            dest.close()
