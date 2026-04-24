"""clamp command – clamp numeric column values to [min, max] bounds."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import Dict, List, Optional, Tuple


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "clamp",
        help="Clamp numeric column values to specified [min, max] bounds.",
    )
    p.add_argument(
        "specs",
        nargs="+",
        metavar="COL:MIN:MAX",
        help="Column and bounds, e.g. price:0:100. Use '' to omit a bound.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout).")
    p.set_defaults(func=run)


def _parse_specs(raw: List[str]) -> Dict[str, Tuple[Optional[float], Optional[float]]]:
    specs: Dict[str, Tuple[Optional[float], Optional[float]]] = {}
    for item in raw:
        parts = item.split(":")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid spec {item!r}: expected COL:MIN:MAX (use empty string to omit a bound)."
            )
        col, lo_s, hi_s = parts
        if not col:
            raise ValueError(f"Invalid spec {item!r}: column name must not be empty.")
        lo = float(lo_s) if lo_s.strip() != "" else None
        hi = float(hi_s) if hi_s.strip() != "" else None
        if lo is not None and hi is not None and lo > hi:
            raise ValueError(
                f"Invalid spec {item!r}: min ({lo}) must be <= max ({hi})."
            )
        specs[col] = (lo, hi)
    return specs


def _clamp_row(
    row: Dict[str, str],
    specs: Dict[str, Tuple[Optional[float], Optional[float]]],
) -> Dict[str, str]:
    out = dict(row)
    for col, (lo, hi) in specs.items():
        if col not in out:
            continue
        try:
            val = float(out[col])
        except (ValueError, TypeError):
            continue
        if lo is not None:
            val = max(lo, val)
        if hi is not None:
            val = min(hi, val)
        # Preserve int-like appearance when possible
        out[col] = str(int(val)) if val == int(val) else str(val)
    return out


def _write(rows: List[Dict[str, str]], fieldnames: List[str], dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    specs = _parse_specs(args.specs)
    src = sys.stdin if args.input == "-" else open(args.input, newline="")
    try:
        reader = csv.DictReader(src)
        rows = [_clamp_row(r, specs) for r in reader]
        fieldnames = list(reader.fieldnames or [])
    finally:
        if src is not sys.stdin:
            src.close()

    if args.output:
        with open(args.output, "w", newline="") as f:
            _write(rows, fieldnames, f)
    else:
        _write(rows, fieldnames, sys.stdout)
