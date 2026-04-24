"""outlier_cmd – flag or remove rows where a column value is an outlier.

Detection methods:
  iqr   : outside [Q1 - k*IQR, Q3 + k*IQR]  (default k=1.5)
  zscore: |z| > threshold                    (default threshold=3.0)
"""
from __future__ import annotations

import csv
import sys
from argparse import ArgumentParser, Namespace
from statistics import mean, stdev
from typing import List, Dict


def add_subparser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "outlier",
        help="flag or remove rows whose column value is an outlier",
    )
    p.add_argument("input", help="input CSV file")
    p.add_argument("--column", required=True, help="numeric column to inspect")
    p.add_argument(
        "--method",
        choices=["iqr", "zscore"],
        default="iqr",
        help="detection method (default: iqr)",
    )
    p.add_argument(
        "--k",
        type=float,
        default=1.5,
        help="IQR multiplier (default: 1.5)",
    )
    p.add_argument(
        "--threshold",
        type=float,
        default=3.0,
        help="z-score threshold (default: 3.0)",
    )
    p.add_argument(
        "--action",
        choices=["flag", "remove"],
        default="flag",
        help="flag adds an 'outlier' column; remove drops the row (default: flag)",
    )
    p.add_argument("--output", "-o", default=None, help="output file (default: stdout)")
    p.set_defaults(func=run)


def _percentile(sorted_vals: List[float], pct: float) -> float:
    """Linear-interpolation percentile on a *sorted* list."""
    n = len(sorted_vals)
    if n == 0:
        return 0.0
    idx = pct / 100.0 * (n - 1)
    lo, hi = int(idx), min(int(idx) + 1, n - 1)
    return sorted_vals[lo] + (idx - lo) * (sorted_vals[hi] - sorted_vals[lo])


def _is_outlier_iqr(value: float, sorted_vals: List[float], k: float) -> bool:
    q1 = _percentile(sorted_vals, 25)
    q3 = _percentile(sorted_vals, 75)
    iqr = q3 - q1
    return value < q1 - k * iqr or value > q3 + k * iqr


def _is_outlier_zscore(value: float, mu: float, sigma: float, threshold: float) -> bool:
    if sigma == 0:
        return False
    return abs((value - mu) / sigma) > threshold


def _detect_outliers(
    rows: List[Dict[str, str]],
    column: str,
    method: str,
    k: float,
    threshold: float,
) -> List[bool]:
    numeric: List[float] = []
    for row in rows:
        try:
            numeric.append(float(row[column]))
        except (ValueError, KeyError):
            numeric.append(float("nan"))

    valid = sorted(v for v in numeric if v == v)  # exclude NaN
    mu = mean(valid) if valid else 0.0
    sigma = stdev(valid) if len(valid) > 1 else 1.0

    flags: List[bool] = []
    for v in numeric:
        if v != v:  # NaN -> not an outlier
            flags.append(False)
        elif method == "iqr":
            flags.append(_is_outlier_iqr(v, valid, k))
        else:
            flags.append(_is_outlier_zscore(v, mu, sigma, threshold))
    return flags


def run(args: Namespace) -> None:
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    if args.column not in fieldnames:
        print(f"error: column '{args.column}' not found", file=sys.stderr)
        sys.exit(1)

    flags = _detect_outliers(rows, args.column, args.method, args.k, args.threshold)

    if args.action == "flag":
        out_fieldnames = fieldnames + ["outlier"]
        out_rows = [
            {**row, "outlier": "1" if flag else "0"}
            for row, flag in zip(rows, flags)
        ]
    else:
        out_fieldnames = fieldnames
        out_rows = [row for row, flag in zip(rows, flags) if not flag]

    _write(out_rows, out_fieldnames, args.output)


def _write(rows: List[Dict[str, str]], fieldnames: List[str], path) -> None:
    dest = open(path, "w", newline="") if path else sys.stdout
    try:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if path:
            dest.close()
