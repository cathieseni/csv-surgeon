"""impute command – fill missing values using mean, median, mode, or a constant."""
from __future__ import annotations

import csv
import statistics
import sys
from collections import Counter
from typing import IO


def add_subparser(subparsers):
    p = subparsers.add_parser("impute", help="Impute missing values in numeric columns")
    p.add_argument("file", help="Input CSV file")
    p.add_argument(
        "--columns",
        required=True,
        help="Comma-separated column names to impute",
    )
    p.add_argument(
        "--strategy",
        choices=["mean", "median", "mode", "constant"],
        default="mean",
        help="Imputation strategy (default: mean)",
    )
    p.add_argument(
        "--fill-value",
        default="0",
        help="Constant value used when --strategy=constant (default: 0)",
    )
    p.add_argument("-o", "--output", help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_columns(raw: str) -> list[str]:
    cols = [c.strip() for c in raw.split(",") if c.strip()]
    if not cols:
        raise ValueError("--columns must not be empty")
    return cols


def _compute_fill(rows: list[dict], col: str, strategy: str, fill_value: str) -> str:
    if strategy == "constant":
        return fill_value
    values = []
    for row in rows:
        v = row.get(col, "").strip()
        if v:
            try:
                values.append(float(v))
            except ValueError:
                pass
    if not values:
        return fill_value
    if strategy == "mean":
        result = statistics.mean(values)
    elif strategy == "median":
        result = statistics.median(values)
    else:  # mode
        result = statistics.mode(values)
    # Preserve int-like appearance when possible
    return str(int(result)) if result == int(result) else str(result)


def _impute_rows(
    rows: list[dict], columns: list[str], strategy: str, fill_value: str
) -> list[dict]:
    fills = {col: _compute_fill(rows, col, strategy, fill_value) for col in columns}
    out = []
    for row in rows:
        new_row = dict(row)
        for col in columns:
            if col in new_row and new_row[col].strip() == "":
                new_row[col] = fills[col]
        out.append(new_row)
    return out


def _write(rows: list[dict], fieldnames: list[str], dest: IO) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args) -> None:
    columns = _parse_columns(args.columns)
    with open(args.file, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    missing = [c for c in columns if c not in fieldnames]
    if missing:
        print(f"impute: unknown columns: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)
    result = _impute_rows(rows, columns, args.strategy, args.fill_value)
    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(result, fieldnames, fh)
    else:
        _write(result, fieldnames, sys.stdout)
