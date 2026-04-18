"""diff command – show rows added/removed between two CSV files."""
from __future__ import annotations

import csv
import sys
from argparse import _SubParsersAction, ArgumentParser, Namespace
from typing import Iterator


def add_subparser(subparsers: _SubParsersAction) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "diff",
        help="Show rows present in one CSV but not the other.",
    )
    p.add_argument("file_a", help="Base CSV file.")
    p.add_argument("file_b", help="Comparison CSV file.")
    p.add_argument(
        "--keys",
        default="",
        help="Comma-separated key columns for identity (default: all columns).",
    )
    p.add_argument(
        "--output", "-o", default="-", help="Output file (default: stdout)."
    )
    p.set_defaults(func=run)


def _load(path: str) -> tuple[list[str], list[dict]]:
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return fieldnames, rows


def _key_fn(row: dict, keys: list[str]):
    return tuple(row[k] for k in keys)


def _diff_rows(
    rows_a: list[dict], rows_b: list[dict], keys: list[str]
) -> Iterator[dict]:
    set_b = {_key_fn(r, keys) for r in rows_b}
    set_a = {_key_fn(r, keys) for r in rows_a}
    for row in rows_a:
        if _key_fn(row, keys) not in set_b:
            yield {"_diff": "removed", **row}
    for row in rows_b:
        if _key_fn(row, keys) not in set_a:
            yield {"_diff": "added", **row}


def _write(fieldnames: list[str], rows, dest: str) -> None:
    out_fields = ["_diff"] + fieldnames
    fh = open(dest, "w", newline="") if dest != "-" else sys.stdout
    try:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if dest != "-":
            fh.close()


def run(args: Namespace) -> None:
    fields_a, rows_a = _load(args.file_a)
    fields_b, rows_b = _load(args.file_b)
    if fields_a != fields_b:
        raise ValueError("CSV files have different schemas.")
    keys = [k.strip() for k in args.keys.split(",") if k.strip()] or fields_a
    for k in keys:
        if k not in fields_a:
            raise ValueError(f"Key column '{k}' not found in CSV.")
    result = list(_diff_rows(rows_a, rows_b, keys))
    _write(fields_a, result, args.output)
