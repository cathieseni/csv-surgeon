"""corr: compute pairwise Pearson correlation between numeric columns."""
from __future__ import annotations
import argparse
import csv
import math
import sys
from typing import IO


def add_subparser(subparsers):
    p = subparsers.add_parser("corr", help="Compute pairwise Pearson correlation")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("-c", "--columns", help="Comma-separated columns (default: all numeric)")
    p.add_argument("-o", "--output", help="Output CSV file (default: stdout)")
    p.set_defaults(func=run)


def _parse_columns(spec: str) -> list[str]:
    return [c.strip() for c in spec.split(",") if c.strip()]


def _pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


def _compute_corr(rows: list[dict], columns: list[str]) -> list[dict]:
    data: dict[str, list[float]] = {c: [] for c in columns}
    for row in rows:
        try:
            vals = {c: float(row[c]) for c in columns}
        except (ValueError, KeyError):
            continue
        for c, v in vals.items():
            data[c].append(v)
    results = []
    for c1 in columns:
        for c2 in columns:
            r = _pearson(data[c1], data[c2])
            results.append({"col_a": c1, "col_b": c2, "correlation": f"{r:.6f}"})
    return results


def _write(results: list[dict], dest: IO[str]) -> None:
    if not results:
        return
    writer = csv.DictWriter(dest, fieldnames=["col_a", "col_b", "correlation"])
    writer.writeheader()
    writer.writerows(results)


def run(args) -> None:
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if args.columns:
        columns = _parse_columns(args.columns)
    else:
        columns = []
        for col in fieldnames:
            try:
                float(rows[0][col])
                columns.append(col)
            except (ValueError, KeyError, IndexError):
                pass

    results = _compute_corr(rows, columns)

    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(results, fh)
    else:
        _write(results, sys.stdout)
