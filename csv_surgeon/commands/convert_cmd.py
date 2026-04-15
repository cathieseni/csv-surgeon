"""convert_cmd – convert column values between formats (date, upper, lower, title, strip)."""
from __future__ import annotations

import argparse
import csv
import io
import sys
from datetime import datetime
from typing import Dict, List


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "convert",
        help="Convert column values using a named transformation.",
    )
    p.add_argument("file", help="Input file (use '-' for stdin).")
    p.add_argument(
        "specs",
        nargs="+",
        metavar="COL:TRANSFORM",
        help="Column and transform name, e.g. name:upper or created_at:date:%Y-%m-%d.",
    )
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout).")
    p.set_defaults(func=run)


_SIMPLE_TRANSFORMS = {
    "upper": str.upper,
    "lower": str.lower,
    "title": str.title,
    "strip": str.strip,
}


def _parse_specs(raw: List[str]) -> List[Dict]:
    """Return list of {col, transform, fmt} dicts."""
    specs = []
    for token in raw:
        parts = token.split(":")
        if len(parts) < 2:
            raise ValueError(f"Invalid spec '{token}': expected COL:TRANSFORM.")
        col = parts[0]
        transform = parts[1]
        fmt = parts[2] if len(parts) >= 3 else None
        if transform not in _SIMPLE_TRANSFORMS and transform != "date":
            raise ValueError(
                f"Unknown transform '{transform}'. "
                f"Choose from: {', '.join(list(_SIMPLE_TRANSFORMS) + ['date'])}."
            )
        specs.append({"col": col, "transform": transform, "fmt": fmt})
    return specs


def _convert_value(value: str, spec: Dict) -> str:
    transform = spec["transform"]
    if transform in _SIMPLE_TRANSFORMS:
        return _SIMPLE_TRANSFORMS[transform](value)
    if transform == "date":
        fmt = spec["fmt"] or "%Y-%m-%d"
        try:
            dt = datetime.fromisoformat(value)
        except ValueError:
            return value  # leave unchanged if unparseable
        return dt.strftime(fmt)
    return value


def run(args: argparse.Namespace) -> None:
    specs = _parse_specs(args.specs)
    src = sys.stdin if args.file == "-" else open(args.file, newline="", encoding="utf-8")
    try:
        reader = csv.DictReader(src)
        fieldnames = reader.fieldnames or []
        rows = []
        for row in reader:
            for spec in specs:
                col = spec["col"]
                if col in row:
                    row[col] = _convert_value(row[col], spec)
            rows.append(row)
    finally:
        if src is not sys.stdin:
            src.close()
    _write(fieldnames, rows, args.output)


def _write(fieldnames: List[str], rows: List[Dict], output: str | None) -> None:
    dest = open(output, "w", newline="", encoding="utf-8") if output else sys.stdout
    try:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if output:
            dest.close()
