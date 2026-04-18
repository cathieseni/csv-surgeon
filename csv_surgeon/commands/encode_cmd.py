"""encode_cmd – base64 encode/decode columns."""
from __future__ import annotations

import argparse
import base64
import csv
import sys
from typing import List


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("encode", help="Base64 encode or decode columns")
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "--columns", "-c", required=True,
        help="Comma-separated column names to encode/decode"
    )
    p.add_argument(
        "--decode", "-d", action="store_true",
        help="Decode instead of encode"
    )
    p.add_argument("--output", "-o", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_columns(spec: str) -> List[str]:
    return [c.strip() for c in spec.split(",") if c.strip()]


def _encode_row(row: dict, columns: List[str], decode: bool) -> dict:
    result = dict(row)
    for col in columns:
        if col not in result:
            continue
        val = result[col]
        try:
            if decode:
                result[col] = base64.b64decode(val.encode()).decode()
            else:
                result[col] = base64.b64encode(val.encode()).decode()
        except Exception:
            result[col] = val  # leave unchanged on error
    return result


def _write(rows, fieldnames, output_path):
    if output_path:
        with open(output_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)
    else:
        w = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def run(args: argparse.Namespace) -> None:
    columns = _parse_columns(args.columns)
    with open(args.input, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = [_encode_row(row, columns, args.decode) for row in reader]
    _write(rows, fieldnames, args.output)
