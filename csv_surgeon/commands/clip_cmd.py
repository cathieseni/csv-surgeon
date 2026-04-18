"""clip command – clamp numeric column values to [min, max] bounds."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import Dict, List, Optional, Tuple


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("clip", help="Clamp numeric column values to [min, max]")
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "--spec",
        dest="specs",
        action="append",
        required=True,
        metavar="COL:MIN:MAX",
        help="Column and bounds, e.g. score:0:100 (use '' to omit a bound)",
    )
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_specs(raw: List[str]) -> List[Tuple[str, Optional[float], Optional[float]]]:
    result = []
    for item in raw:
        parts = item.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid spec '{item}': expected COL:MIN:MAX")
        col, lo, hi = parts
        lo_val = float(lo) if lo.strip() != "" else None
        hi_val = float(hi) if hi.strip() != "" else None
        result.append((col, lo_val, hi_val))
    return result


def _clip_row(
    row: Dict[str, str],
    specs: List[Tuple[str, Optional[float], Optional[float]]],
) -> Dict[str, str]:
    out = dict(row)
    for col, lo, hi in specs:
        if col not in out:
            continue
        try:
            val = float(out[col])
        except ValueError:
            continue
        if lo is not None:
            val = max(lo, val)
        if hi is not None:
            val = min(hi, val)
        # Preserve int-like representation
        out[col] = str(int(val)) if val == int(val) else str(val)
    return out


def _write(rows, fieldnames, dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args) -> None:
    specs = _parse_specs(args.specs)
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = [_clip_row(r, specs) for r in reader]

    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(rows, fieldnames, fh)
    else:
        _write(rows, fieldnames, sys.stdout)
