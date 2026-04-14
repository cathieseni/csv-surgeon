"""stats_cmd – compute per-column descriptive statistics."""
from __future__ import annotations

import csv
import sys
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from typing import IO


def add_subparser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "stats",
        help="Print descriptive statistics for numeric columns.",
    )
    p.add_argument("file", help="Input CSV file.")
    p.add_argument(
        "-c",
        "--columns",
        metavar="COL",
        nargs="+",
        help="Columns to analyse (default: all numeric columns).",
    )
    p.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        default=None,
        help="Write results to FILE instead of stdout.",
    )
    p.set_defaults(func=run)


def _compute_stats(rows: list[dict], columns: list[str]) -> dict[str, dict]:
    """Return {col: {count, min, max, sum, mean}} for each column."""
    buckets: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        for col in columns:
            raw = row.get(col, "").strip()
            try:
                buckets[col].append(float(raw))
            except ValueError:
                pass  # skip non-numeric cells

    stats: dict[str, dict] = {}
    for col, values in buckets.items():
        if not values:
            stats[col] = {"count": 0, "min": "", "max": "", "sum": "", "mean": ""}
        else:
            total = sum(values)
            stats[col] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "sum": total,
                "mean": round(total / len(values), 6),
            }
    return stats


def _write(stats: dict[str, dict], dest: IO[str]) -> None:
    fieldnames = ["column", "count", "min", "max", "sum", "mean"]
    writer = csv.DictWriter(dest, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for col, s in stats.items():
        writer.writerow({"column": col, **s})


def run(args: Namespace) -> None:
    with open(args.file, newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            print("error: empty or invalid CSV", file=sys.stderr)
            sys.exit(1)
        all_columns: list[str] = list(reader.fieldnames)
        rows = list(reader)

    columns = args.columns if args.columns else all_columns
    missing = [c for c in columns if c not in all_columns]
    if missing:
        print(f"error: unknown columns: {missing}", file=sys.stderr)
        sys.exit(1)

    stats = _compute_stats(rows, columns)

    if args.output:
        with open(args.output, "w", newline="") as out:
            _write(stats, out)
    else:
        _write(stats, sys.stdout)
