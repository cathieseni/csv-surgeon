"""shuffle command – randomly shuffle rows in a CSV."""
from __future__ import annotations

import csv
import io
import random
import sys
from argparse import ArgumentParser, Namespace
from typing import List, Dict


def add_subparser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "shuffle",
        help="Randomly shuffle rows (header preserved).",
    )
    p.add_argument("input", help="Input CSV file.")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout).")
    p.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility.",
    )
    p.set_defaults(func=run)


def _shuffle_rows(
    rows: List[Dict[str, str]], seed: int | None
) -> List[Dict[str, str]]:
    rng = random.Random(seed)
    result = list(rows)
    rng.shuffle(result)
    return result


def _write(
    fieldnames: List[str],
    rows: List[Dict[str, str]],
    dest: io.TextIOBase,
) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def run(args: Namespace) -> None:
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    shuffled = _shuffle_rows(rows, args.seed)

    if args.output:
        with open(args.output, "w", newline="") as out:
            _write(fieldnames, shuffled, out)
    else:
        _write(fieldnames, shuffled, sys.stdout)
