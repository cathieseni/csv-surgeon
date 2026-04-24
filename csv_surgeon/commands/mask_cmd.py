"""mask command – redact or replace values in specified columns."""
from __future__ import annotations

import csv
import re
import sys
from argparse import ArgumentParser, Namespace
from typing import Dict, Iterable, Iterator, List


def add_subparser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "mask",
        help="Redact or replace values in columns (e.g. mask email addresses).",
    )
    p.add_argument(
        "specs",
        nargs="+",
        metavar="COL:PATTERN:REPLACEMENT",
        help=(
            "Masking spec: column name, regex pattern, and replacement string "
            "separated by colons. Use \\: to escape a literal colon. "
            "Example: email:.+@.+:***REDACTED***"
        ),
    )
    p.add_argument("-i", "--input", default="-", help="Input CSV file (default: stdin).")
    p.add_argument("-o", "--output", default="-", help="Output CSV file (default: stdout).")
    p.set_defaults(func=run)


def _parse_specs(raw: List[str]) -> List[Dict[str, str]]:
    """Parse 'COL:PATTERN:REPLACEMENT' specs into dicts."""
    specs = []
    for item in raw:
        parts = re.split(r"(?<!\\):", item, maxsplit=2)
        if len(parts) != 3:
            raise ValueError(
                f"Invalid mask spec {item!r}: expected COL:PATTERN:REPLACEMENT"
            )
        col, pattern, replacement = parts
        col = col.replace("\\:", ":")
        pattern = pattern.replace("\\:", ":")
        replacement = replacement.replace("\\:", ":")
        specs.append({"col": col, "pattern": pattern, "replacement": replacement})
    return specs


def _mask_rows(
    rows: Iterable[Dict[str, str]],
    specs: List[Dict[str, str]],
) -> Iterator[Dict[str, str]]:
    compiled = [
        {"col": s["col"], "rx": re.compile(s["pattern"]), "repl": s["replacement"]}
        for s in specs
    ]
    for row in rows:
        new_row = dict(row)
        for spec in compiled:
            col = spec["col"]
            if col in new_row:
                new_row[col] = spec["rx"].sub(spec["repl"], new_row[col])
        yield new_row


def _write(
    fieldnames: List[str],
    rows: Iterator[Dict[str, str]],
    dest,
) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: Namespace) -> None:
    specs = _parse_specs(args.specs)

    in_fh = open(args.input, newline="") if args.input != "-" else sys.stdin
    out_fh = open(args.output, "w", newline="") if args.output != "-" else sys.stdout

    try:
        reader = csv.DictReader(in_fh)
        fieldnames = list(reader.fieldnames or [])
        masked = _mask_rows(reader, specs)
        _write(fieldnames, masked, out_fh)
    finally:
        if args.input != "-":
            in_fh.close()
        if args.output != "-":
            out_fh.close()
