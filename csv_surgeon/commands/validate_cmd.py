"""validate command – check rows against column rules."""
from __future__ import annotations

import csv
import re
import sys
from argparse import _SubParsersAction, ArgumentParser, Namespace
from typing import Iterator


def add_subparser(sub: _SubParsersAction) -> None:
    p: ArgumentParser = sub.add_parser(
        "validate",
        help="Validate CSV rows against column rules; report or drop invalid rows.",
    )
    p.add_argument("file", help="Input CSV file")
    p.add_argument(
        "-r",
        "--rule",
        dest="rules",
        metavar="COL:PATTERN",
        action="append",
        default=[],
        help="Regex rule applied to column (repeatable)",
    )
    p.add_argument(
        "--drop-invalid",
        action="store_true",
        help="Output only valid rows instead of reporting errors",
    )
    p.add_argument("-o", "--output", default="-", help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_rules(raw: list[str]) -> list[tuple[str, re.Pattern]]:
    rules: list[tuple[str, re.Pattern]] = []
    for spec in raw:
        if ":" not in spec:
            raise ValueError(f"Invalid rule spec (expected COL:PATTERN): {spec!r}")
        col, pattern = spec.split(":", 1)
        rules.append((col.strip(), re.compile(pattern)))
    return rules


def _validate(rows: Iterator[dict], rules: list[tuple[str, re.Pattern]], drop: bool):
    errors: list[str] = []
    valid: list[dict] = []
    for i, row in enumerate(rows, start=2):  # row 1 = header
        ok = True
        for col, pattern in rules:
            val = row.get(col, "")
            if not pattern.fullmatch(val):
                errors.append(f"Row {i}: column {col!r} value {val!r} does not match /{pattern.pattern}/")
                ok = False
        if ok or drop:
            if ok:
                valid.append(row)
    return valid, errors


def _write(rows: list[dict], fieldnames: list[str], dest: str) -> None:
    fh = open(dest, "w", newline="") if dest != "-" else sys.stdout
    try:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    finally:
        if dest != "-":
            fh.close()


def run(args: Namespace) -> None:
    rules = _parse_rules(args.rules)
    with open(args.file, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        valid, errors = _validate(iter(reader), rules, args.drop_invalid)

    if args.drop_invalid:
        _write(valid, list(fieldnames), args.output)
    else:
        for msg in errors:
            print(msg, file=sys.stderr)
        if errors:
            sys.exit(1)
