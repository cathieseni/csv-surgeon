"""CLI sub-command: aggregate — compute column statistics from a CSV file."""
from __future__ import annotations

import csv
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List

from csv_surgeon.aggregator import AGGREGATORS, aggregate_summary


def add_subparser(subparsers) -> None:  # type: ignore[type-arg]
    p: ArgumentParser = subparsers.add_parser(
        "aggregate",
        help="Compute aggregations over CSV columns.",
    )
    p.add_argument("file", type=Path, help="Input CSV file.")
    p.add_argument(
        "-a",
        "--agg",
        metavar="COLUMN:AGG",
        action="append",
        dest="aggs",
        required=True,
        help=(
            "Column and aggregation, e.g. price:sum. "
            f"Available aggregations: {sorted(AGGREGATORS)}. "
            "Can be repeated."
        ),
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write results to this CSV file instead of stdout.",
    )
    p.set_defaults(func=run)


def _parse_specs(raw: List[str]) -> List[tuple[str, str]]:
    specs = []
    for item in raw:
        if ":" not in item:
            raise ValueError(f"Invalid aggregation spec '{item}'. Expected COLUMN:AGG.")
        col, agg = item.split(":", 1)
        specs.append((col.strip(), agg.strip()))
    return specs


def run(args: Namespace) -> int:
    if not args.file.exists():
        print(f"Error: file '{args.file}' not found.", file=sys.stderr)
        return 1

    try:
        specs = _parse_specs(args.aggs)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    with args.file.open(newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    try:
        summary = aggregate_summary(rows, specs)
    except (ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    def _write(out) -> None:  # type: ignore[type-arg]
        writer = csv.writer(out)
        writer.writerow(["metric", "value"])
        for key, val in summary.items():
            writer.writerow([key, val])

    if args.output:
        with args.output.open("w", newline="") as fh:
            _write(fh)
    else:
        _write(sys.stdout)

    return 0
