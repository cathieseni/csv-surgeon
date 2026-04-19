"""pow command – raise numeric column values to a power."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import IO


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("pow", help="Raise column values to a power")
    p.add_argument(
        "specs",
        nargs="+",
        metavar="COL:EXPONENT",
        help="Column name and exponent, e.g. score:2",
    )
    p.add_argument("-i", "--input", default="-", help="Input CSV (default: stdin)")
    p.add_argument("-o", "--output", default="-", help="Output CSV (default: stdout)")
    p.set_defaults(func=run)


def _parse_specs(specs: list[str]) -> dict[str, float]:
    result: dict[str, float] = {}
    for spec in specs:
        if ":" not in spec:
            raise ValueError(f"Invalid spec '{spec}': expected COL:EXPONENT")
        col, exp_str = spec.split(":", 1)
        try:
            result[col] = float(exp_str)
        except ValueError:
            raise ValueError(f"Invalid exponent '{exp_str}' for column '{col}'")
    return result


def _pow_row(row: dict, specs: dict[str, float]) -> dict:
    out = dict(row)
    for col, exp in specs.items():
        if col not in out:
            continue
        try:
            out[col] = str(float(out[col]) ** exp)
        except (ValueError, TypeError):
            pass
    return out


def _write(rows, fieldnames, dest: IO) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    specs = _parse_specs(args.specs)

    in_fh = open(args.input, newline="") if args.input != "-" else sys.stdin
    try:
        reader = csv.DictReader(in_fh)
        rows = [_pow_row(r, specs) for r in reader]
        fieldnames = reader.fieldnames or []
    finally:
        if args.input != "-":
            in_fh.close()

    if args.output == "-":
        _write(rows, fieldnames, sys.stdout)
    else:
        with open(args.output, "w", newline="") as fh:
            _write(rows, fieldnames, fh)
