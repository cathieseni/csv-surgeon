"""pivot_cmd: pivot a CSV by grouping rows and spreading a column's values."""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from typing import Any


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("pivot", help="Pivot CSV: group rows and spread column values")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--index", required=True, help="Column(s) to use as row index (comma-separated)")
    p.add_argument("--columns", required=True, help="Column whose unique values become new columns")
    p.add_argument("--values", required=True, help="Column whose values populate the pivot cells")
    p.add_argument("--aggfunc", default="first", choices=["first", "sum", "count", "mean"],
                   help="Aggregation function when multiple values map to a cell (default: first)")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _aggregate(values: list[str], aggfunc: str) -> str:
    if not values:
        return ""
    if aggfunc == "first":
        return values[0]
    if aggfunc == "count":
        return str(len(values))
    nums = [float(v) for v in values if v != ""]
    if not nums:
        return ""
    if aggfunc == "sum":
        return str(sum(nums))
    if aggfunc == "mean":
        return str(sum(nums) / len(nums))
    return values[0]


def run(args: Any) -> None:
    index_cols = [c.strip() for c in args.index.split(",")]
    col_col = args.columns
    val_col = args.values
    aggfunc = args.aggfunc

    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row")
        raw_rows = list(reader)

    # Collect unique pivot column values (preserving order)
    pivot_vals: list[str] = []
    seen: set[str] = set()
    for row in raw_rows:
        v = row[col_col]
        if v not in seen:
            pivot_vals.append(v)
            seen.add(v)

    # Accumulate cell values
    cell_data: dict[tuple[str, ...], dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for row in raw_rows:
        key = tuple(row[c] for c in index_cols)
        cell_data[key][row[col_col]].append(row[val_col])

    out_fieldnames = index_cols + pivot_vals
    out_rows = []
    for key, cells in cell_data.items():
        out_row = dict(zip(index_cols, key))
        for pv in pivot_vals:
            out_row[pv] = _aggregate(cells.get(pv, []), aggfunc)
        out_rows.append(out_row)

    _write(out_rows, out_fieldnames, args.output)


def _write(rows: list[dict], fieldnames: list[str], output: str | None) -> None:
    dest = open(output, "w", newline="") if output else sys.stdout
    try:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if output:
            dest.close()
