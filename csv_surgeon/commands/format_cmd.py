"""format_cmd – pad/align column values to a fixed width."""
from __future__ import annotations

import csv
import io
import sys
from argparse import ArgumentParser, Namespace
from typing import Dict, List


def add_subparser(sub) -> None:
    p: ArgumentParser = sub.add_parser(
        "format",
        help="Pad/align column values to a fixed width.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "-s",
        "--spec",
        dest="specs",
        action="append",
        metavar="COL:WIDTH[:ALIGN]",
        required=True,
        help="Column format spec. ALIGN is l(eft), r(ight), or c(enter). Default: left.",
    )
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_specs(raw: List[str]) -> Dict[str, tuple]:
    specs: Dict[str, tuple] = {}
    for item in raw:
        parts = item.split(":")
        if len(parts) < 2:
            raise ValueError(f"Invalid format spec: {item!r}. Expected COL:WIDTH[:ALIGN]")
        col = parts[0]
        try:
            width = int(parts[1])
        except ValueError:
            raise ValueError(f"Width must be an integer in spec: {item!r}")
        align = parts[2].lower() if len(parts) >= 3 else "l"
        if align not in ("l", "r", "c"):
            raise ValueError(f"Align must be l, r, or c in spec: {item!r}")
        specs[col] = (width, align)
    return specs


def _format_value(value: str, width: int, align: str) -> str:
    if align == "r":
        return value.rjust(width)
    if align == "c":
        return value.center(width)
    return value.ljust(width)


def _write(rows, fieldnames, dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def run(args: Namespace) -> None:
    specs = _parse_specs(args.specs)

    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        rows = []
        for row in reader:
            new_row = dict(row)
            for col, (width, align) in specs.items():
                if col in new_row:
                    new_row[col] = _format_value(new_row[col], width, align)
            rows.append(new_row)

    if args.output:
        with open(args.output, "w", newline="") as out:
            _write(rows, fieldnames, out)
    else:
        _write(rows, fieldnames, sys.stdout)
