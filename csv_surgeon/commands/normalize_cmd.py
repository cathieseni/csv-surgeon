"""normalize command – normalize numeric columns to [0,1] or z-score."""
from __future__ import annotations

import argparse
import csv
import math
import sys
from typing import IO


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("normalize", help="Normalize numeric columns")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("-c", "--columns", required=True, help="Comma-separated columns to normalize")
    p.add_argument(
        "--method",
        choices=["minmax", "zscore"],
        default="minmax",
        help="Normalization method (default: minmax)",
    )
    p.add_argument("-o", "--output", help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_columns(spec: str) -> list[str]:
    return [c.strip() for c in spec.split(",") if c.strip()]


def _compute_stats(rows: list[dict], columns: list[str]) -> dict[str, dict]:
    stats: dict[str, dict] = {}
    for col in columns:
        vals = []
        for row in rows:
            try:
                vals.append(float(row[col]))
            except (ValueError, KeyError):
                pass
        if not vals:
            stats[col] = {"min": 0.0, "max": 0.0, "mean": 0.0, "std": 1.0}
            continue
        mean = sum(vals) / len(vals)
        variance = sum((v - mean) ** 2 for v in vals) / len(vals)
        stats[col] = {
            "min": min(vals),
            "max": max(vals),
            "mean": mean,
            "std": math.sqrt(variance) or 1.0,
        }
    return stats


def _normalize_rows(
    rows: list[dict],
    columns: list[str],
    stats: dict[str, dict],
    method: str,
) -> list[dict]:
    result = []
    for row in rows:
        new_row = dict(row)
        for col in columns:
            try:
                v = float(row[col])
            except (ValueError, KeyError):
                continue
            s = stats[col]
            if method == "minmax":
                denom = s["max"] - s["min"] or 1.0
                new_row[col] = str(round((v - s["min"]) / denom, 6))
            else:
                new_row[col] = str(round((v - s["mean"]) / s["std"], 6))
        result.append(new_row)
    return result


def _write(fieldnames: list[str], rows: list[dict], dest: IO[str]) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    with open(args.file, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    columns = _parse_columns(args.columns)
    stats = _compute_stats(rows, columns)
    normalized = _normalize_rows(rows, columns, stats, args.method)

    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(fieldnames, normalized, fh)
    else:
        _write(fieldnames, normalized, sys.stdout)
