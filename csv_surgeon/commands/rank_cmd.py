"""rank command – add a rank column based on a numeric field."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Dict


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("rank", help="Add a rank column based on a numeric field")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--col", required=True, help="Column to rank by")
    p.add_argument("--output", "-o", default=None, help="Output file (default: stdout)")
    p.add_argument("--rank-col", default="rank", help="Name of new rank column (default: rank)")
    p.add_argument("--desc", action="store_true", help="Rank in descending order")
    p.add_argument("--method", choices=["ordinal", "dense"], default="ordinal",
                   help="Ranking method: ordinal (1,2,3,...) or dense (ties share rank)")
    p.set_defaults(func=run)


def _rank_rows(rows: List[Dict], col: str, rank_col: str, desc: bool, method: str) -> List[Dict]:
    def _val(r):
        try:
            return float(r[col])
        except (ValueError, KeyError):
            return float("-inf") if desc else float("inf")

    sorted_rows = sorted(rows, key=_val, reverse=desc)

    if method == "dense":
        current_rank = 1
        prev_val = None
        for row in sorted_rows:
            v = _val(row)
            if prev_val is not None and v != prev_val:
                current_rank += 1
            row[rank_col] = current_rank
            prev_val = v
    else:  # ordinal
        for i, row in enumerate(sorted_rows, start=1):
            row[rank_col] = i

    return rows


def _write(fieldnames, rows, dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no headers")
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    rank_col = args.rank_col
    if rank_col in fieldnames:
        raise ValueError(f"Column '{rank_col}' already exists; use --rank-col to choose another name")
    if args.col not in fieldnames:
        raise ValueError(f"Column '{args.col}' not found in CSV")

    fieldnames.append(rank_col)
    rows = _rank_rows(rows, args.col, rank_col, args.desc, args.method)

    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(fieldnames, rows, fh)
    else:
        _write(fieldnames, rows, sys.stdout)
