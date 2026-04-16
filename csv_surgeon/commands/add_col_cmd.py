"""add-col command: add a new column with a constant or template value."""
from __future__ import annotations

import csv
import io
import sys
from argparse import ArgumentParser, Namespace
from typing import List, Dict


def add_subparser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "add-col",
        help="Add one or more new columns to the CSV.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "-s",
        "--spec",
        dest="specs",
        action="append",
        required=True,
        metavar="NAME=VALUE",
        help="Column spec: NAME=VALUE (VALUE may reference {col} placeholders)",
    )
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_specs(raw: List[str]) -> List[tuple]:
    """Return list of (name, template) pairs."""
    result = []
    for item in raw:
        if "=" not in item:
            raise ValueError(f"Invalid spec {item!r}: expected NAME=VALUE")
        name, _, template = item.partition("=")
        result.append((name.strip(), template))
    return result


def _add_columns(rows: List[Dict], specs: List[tuple]) -> List[Dict]:
    out = []
    for row in rows:
        new_row = dict(row)
        for name, template in specs:
            try:
                new_row[name] = template.format(**row)
            except KeyError:
                new_row[name] = template
        out.append(new_row)
    return out


def _write(fieldnames, rows, dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: Namespace) -> None:
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        original_fields = list(reader.fieldnames or [])
        rows = list(reader)

    specs = _parse_specs(args.specs)
    new_fields = [name for name, _ in specs if name not in original_fields]
    fieldnames = original_fields + new_fields
    rows = _add_columns(rows, specs)

    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(fieldnames, rows, fh)
    else:
        _write(fieldnames, rows, sys.stdout)
