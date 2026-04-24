"""copy_cmd – duplicate a column under a new name."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Tuple


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "copy",
        help="Duplicate one or more columns under new names.",
    )
    p.add_argument(
        "specs",
        nargs="+",
        metavar="SRC:DST",
        help="Column copy spec, e.g. 'price:price_backup'.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout).")
    p.set_defaults(func=run)


def _parse_specs(raw: List[str]) -> List[Tuple[str, str]]:
    """Parse 'SRC:DST' strings into (src, dst) pairs."""
    result = []
    for spec in raw:
        if ":" not in spec:
            raise argparse.ArgumentTypeError(
                f"Invalid copy spec {spec!r}: expected 'SRC:DST'."
            )
        src, dst = spec.split(":", 1)
        if not src or not dst:
            raise argparse.ArgumentTypeError(
                f"Invalid copy spec {spec!r}: SRC and DST must be non-empty."
            )
        result.append((src, dst))
    return result


def _copy_rows(rows, fieldnames: List[str], specs: List[Tuple[str, str]]):
    """Yield rows with extra copied columns appended."""
    for row in rows:
        new_row = dict(row)
        for src, dst in specs:
            new_row[dst] = row.get(src, "")
        yield new_row


def _write(fieldnames: List[str], rows, dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


def run(args) -> None:
    specs = _parse_specs(args.specs)

    src_file = sys.stdin if args.input == "-" else open(args.input, newline="")
    try:
        reader = csv.DictReader(src_file)
        original_fields = list(reader.fieldnames or [])
        # Validate source columns exist
        for src, _ in specs:
            if src not in original_fields:
                raise SystemExit(f"error: column {src!r} not found in input.")
        # Build output fieldnames: original + new destination columns (in order)
        extra = [dst for _, dst in specs]
        out_fields = original_fields + extra
        copied = _copy_rows(reader, original_fields, specs)
        if args.output:
            with open(args.output, "w", newline="") as fout:
                _write(out_fields, copied, fout)
        else:
            _write(out_fields, copied, sys.stdout)
    finally:
        if src_file is not sys.stdin:
            src_file.close()
