"""scale command – multiply numeric columns by a factor."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Tuple


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("scale", help="Multiply numeric columns by a factor")
    p.add_argument("specs", nargs="+", metavar="COL:FACTOR",
                   help="Column name and numeric factor, e.g. price:2.5")
    p.add_argument("-i", "--input", default="-", help="Input CSV (default stdin)")
    p.add_argument("-o", "--output", default="-", help="Output CSV (default stdout)")
    p.set_defaults(func=run)


def _parse_specs(specs: List[str]) -> List[Tuple[str, float]]:
    result = []
    for spec in specs:
        if ":" not in spec:
            raise ValueError(f"Invalid spec {spec!r}: expected COL:FACTOR")
        col, factor_str = spec.split(":", 1)
        try:
            factor = float(factor_str)
        except ValueError:
            raise ValueError(f"Invalid factor {factor_str!r} in spec {spec!r}")
        result.append((col, factor))
    return result


def _scale_row(row: dict, specs: List[Tuple[str, float]]) -> dict:
    out = dict(row)
    for col, factor in specs:
        if col in out:
            try:
                out[col] = str(float(out[col]) * factor)
            except ValueError:
                pass  # leave non-numeric values unchanged
    return out


def _write(rows, fieldnames, dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    specs = _parse_specs(args.specs)

    in_fh = open(args.input, newline="") if args.input != "-" else sys.stdin
    try:
        reader = csv.DictReader(in_fh)
        rows = [_scale_row(r, specs) for r in reader]
        fieldnames = reader.fieldnames or []
    finally:
        if args.input != "-":
            in_fh.close()

    if args.output == "-":
        _write(rows, fieldnames, sys.stdout)
    else:
        with open(args.output, "w", newline="") as fh:
            _write(rows, fieldnames, fh)
