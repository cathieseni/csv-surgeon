"""replace_cmd – find-and-replace values in CSV columns."""
from __future__ import annotations

import csv
import re
import sys
from argparse import ArgumentParser, Namespace
from typing import IO


def add_subparser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "replace",
        help="Find and replace text in one or more columns.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "-s",
        "--spec",
        dest="specs",
        metavar="COL:FIND:REPLACE",
        action="append",
        required=True,
        help="Replacement spec (repeatable). Use --regex to treat FIND as a pattern.",
    )
    p.add_argument("--regex", action="store_true", help="Treat FIND as a regular expression")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_specs(raw: list[str]) -> list[tuple[str, str, str]]:
    result = []
    for item in raw:
        parts = item.split(":", 2)
        if len(parts) != 3:
            raise ValueError(f"Invalid spec {item!r}: expected COL:FIND:REPLACE")
        result.append((parts[0], parts[1], parts[2]))
    return result


def _replace_row(
    row: dict,
    specs: list[tuple[str, str, str]],
    use_regex: bool,
) -> dict:
    row = dict(row)
    for col, find, replace in specs:
        if col not in row:
            continue
        if use_regex:
            row[col] = re.sub(find, replace, row[col])
        else:
            row[col] = row[col].replace(find, replace)
    return row


def run(args: Namespace) -> None:
    specs = _parse_specs(args.specs)
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = [_replace_row(r, specs, args.regex) for r in reader]
    _write(fieldnames, rows, args.output)


def _write(fieldnames: list[str], rows: list[dict], output: str | None) -> None:
    def _dump(fh: IO[str]) -> None:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    if output:
        with open(output, "w", newline="") as fh:
            _dump(fh)
    else:
        _dump(sys.stdout)
