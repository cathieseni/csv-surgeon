"""join command – join two CSV files on a common key column."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import Dict, List


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "join",
        help="Join two CSV files on a common key column (left join by default).",
    )
    p.add_argument("left", help="Primary CSV file (or '-' for stdin).")
    p.add_argument("right", help="Secondary CSV file to join against.")
    p.add_argument("-k", "--key", required=True, help="Column name to join on.")
    p.add_argument(
        "--how",
        choices=["left", "inner"],
        default="left",
        help="Join strategy: 'left' (default) keeps all left rows; 'inner' keeps only matches.",
    )
    p.add_argument("-o", "--output", default="-", help="Output file (default: stdout).")
    p.set_defaults(func=run)


def _load_right(path: str, key: str) -> Dict[str, List[Dict[str, str]]]:
    """Load the right-hand CSV into a dict keyed by the join column."""
    lookup: Dict[str, List[Dict[str, str]]] = {}
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            k = row.get(key, "")
            lookup.setdefault(k, []).append(dict(row))
    return lookup


def run(args: argparse.Namespace) -> None:
    right_lookup = _load_right(args.right, args.key)

    left_fh = sys.stdin if args.left == "-" else open(args.left, newline="")
    try:
        reader = csv.DictReader(left_fh)
        left_fieldnames = list(reader.fieldnames or [])

        # Determine extra columns from the right file (excluding the key).
        right_extra: List[str] = []
        if right_lookup:
            sample = next(iter(right_lookup.values()))[0]
            right_extra = [c for c in sample if c != args.key and c not in left_fieldnames]

        out_fieldnames = left_fieldnames + right_extra
        joined_rows = []

        for left_row in reader:
            k = left_row.get(args.key, "")
            matches = right_lookup.get(k)
            if matches:
                for right_row in matches:
                    merged = dict(left_row)
                    for col in right_extra:
                        merged[col] = right_row.get(col, "")
                    joined_rows.append(merged)
            elif args.how == "left":
                merged = dict(left_row)
                for col in right_extra:
                    merged[col] = ""
                joined_rows.append(merged)
    finally:
        if left_fh is not sys.stdin:
            left_fh.close()

    _write(joined_rows, out_fieldnames, args.output)


def _write(rows: List[Dict[str, str]], fieldnames: List[str], dest: str) -> None:
    out_fh = sys.stdout if dest == "-" else open(dest, "w", newline="")
    try:
        writer = csv.DictWriter(out_fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if out_fh is not sys.stdout:
            out_fh.close()
