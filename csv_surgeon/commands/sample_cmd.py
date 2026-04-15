"""sample_cmd – randomly sample N rows (or a fraction) from a CSV."""
from __future__ import annotations

import argparse
import csv
import io
import random
import sys
from typing import List, Dict


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "sample",
        help="Randomly sample rows from a CSV.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("-n", "--count", type=int, metavar="N",
                       help="Number of rows to sample.")
    group.add_argument("-f", "--fraction", type=float, metavar="F",
                       help="Fraction of rows to sample (0 < F <= 1).")
    p.add_argument("-s", "--seed", type=int, default=None,
                   help="Random seed for reproducibility.")
    p.add_argument("-o", "--output", default=None,
                   help="Output file (default: stdout).")
    p.set_defaults(func=run)


def _sample_rows(
    rows: List[Dict[str, str]],
    count: int | None,
    fraction: float | None,
    seed: int | None,
) -> List[Dict[str, str]]:
    rng = random.Random(seed)
    if count is not None:
        if count < 0:
            raise ValueError(f"--count must be >= 0, got {count}")
        return rng.sample(rows, min(count, len(rows)))
    # fraction path
    if not (0 < fraction <= 1):
        raise ValueError(f"--fraction must be in (0, 1], got {fraction}")
    k = max(1, round(len(rows) * fraction))
    return rng.sample(rows, min(k, len(rows)))


def run(args: argparse.Namespace) -> None:
    src = sys.stdin if args.input == "-" else open(args.input, newline="")
    try:
        reader = csv.DictReader(src)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    finally:
        if args.input != "-":
            src.close()

    sampled = _sample_rows(rows, args.count, args.fraction, args.seed)
    _write(sampled, fieldnames, args.output)


def _write(
    rows: List[Dict[str, str]],
    fieldnames: List[str],
    output: str | None,
) -> None:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    text = buf.getvalue()
    if output:
        with open(output, "w", newline="") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
