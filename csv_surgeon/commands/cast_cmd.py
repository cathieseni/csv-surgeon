"""cast_cmd – convert column values to a target type (int, float, str, bool)."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import Dict, List

CAST_FUNCS = {
    "int": int,
    "float": float,
    "str": str,
    "bool": lambda v: v.strip().lower() not in ("", "0", "false", "no"),
}


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("cast", help="Cast column values to a target type")
    p.add_argument("input", help="Input CSV file (use '-' for stdin)")
    p.add_argument(
        "-s",
        "--spec",
        dest="specs",
        metavar="COL:TYPE",
        action="append",
        required=True,
        help="Column and type, e.g. age:int (repeatable)",
    )
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.add_argument(
        "--errors",
        choices=("raise", "null", "keep"),
        default="raise",
        help="How to handle cast errors (default: raise)",
    )
    p.set_defaults(func=run)


def _parse_specs(raw: List[str]) -> Dict[str, str]:
    specs: Dict[str, str] = {}
    for item in raw:
        if ":" not in item:
            raise ValueError(f"Invalid cast spec {item!r}: expected COL:TYPE")
        col, _, typ = item.partition(":")
        col, typ = col.strip(), typ.strip().lower()
        if typ not in CAST_FUNCS:
            raise ValueError(f"Unknown type {typ!r}. Choose from: {', '.join(CAST_FUNCS)}")
        specs[col] = typ
    return specs


def _cast_row(
    row: Dict[str, str],
    specs: Dict[str, str],
    errors: str,
) -> Dict[str, str]:
    out = dict(row)
    for col, typ in specs.items():
        if col not in out:
            continue
        try:
            out[col] = str(CAST_FUNCS[typ](out[col]))
        except (ValueError, TypeError):
            if errors == "raise":
                raise
            if errors == "null":
                out[col] = ""
            # errors == "keep": leave original value
    return out


def run(args: argparse.Namespace) -> None:
    specs = _parse_specs(args.specs)
    src = sys.stdin if args.input == "-" else open(args.input, newline="", encoding="utf-8")
    try:
        reader = csv.DictReader(src)
        rows = [_cast_row(r, specs, args.errors) for r in reader]
        fieldnames = reader.fieldnames or []
    finally:
        if src is not sys.stdin:
            src.close()
    _write(rows, fieldnames, args.output)


def _write(rows: List[Dict[str, str]], fieldnames: List[str], output: str | None) -> None:
    dst = sys.stdout if output is None else open(output, "w", newline="", encoding="utf-8")
    try:
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if dst is not sys.stdout:
            dst.close()
