"""round command – round numeric columns to N decimal places."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import Dict


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("round", help="Round numeric columns to N decimal places")
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "specs",
        nargs="+",
        metavar="COL:N",
        help="Column name and decimal places, e.g. price:2",
    )
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_specs(specs: list[str]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for spec in specs:
        if ":" not in spec:
            raise ValueError(f"Invalid spec {spec!r}: expected COL:N")
        col, _, n_str = spec.partition(":")
        if not col:
            raise ValueError(f"Empty column name in spec {spec!r}")
        try:
            n = int(n_str)
        except ValueError:
            raise ValueError(f"Invalid decimal places {n_str!r} in spec {spec!r}")
        if n < 0:
            raise ValueError(f"Decimal places must be >= 0, got {n}")
        result[col] = n
    return result


def _round_row(row: dict, specs: Dict[str, int]) -> dict:
    out = dict(row)
    for col, places in specs.items():
        if col in out and out[col].strip() != "":
            try:
                out[col] = str(round(float(out[col]), places))
            except ValueError:
                pass  # leave non-numeric values unchanged
    return out


def _write(rows: list[dict], fieldnames: list[str], output: str | None) -> None:
    dest = open(output, "w", newline="") if output else sys.stdout
    try:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if output:
            dest.close()


def run(args: argparse.Namespace) -> None:
    specs = _parse_specs(args.specs)
    with open(args.input, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = [_round_row(row, specs) for row in reader]
    _write(rows, fieldnames, args.output)
