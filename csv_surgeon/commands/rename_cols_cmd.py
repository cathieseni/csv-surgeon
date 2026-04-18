"""rename-cols command: rename columns by position (e.g. 0=id, 1=name)."""
from __future__ import annotations

import csv
import sys
from argparse import ArgumentParser, Namespace
from typing import Dict, List


def add_subparser(subparsers) -> None:
    """Register the rename-cols subcommand."""
    p: ArgumentParser = subparsers.add_parser(
        "rename-cols",
        help="Rename columns by position index.",
        description=(
            "Rename one or more columns identified by zero-based position. "
            "Specs are given as INDEX=NEW_NAME pairs."
        ),
    )
    p.add_argument(
        "file",
        help="Input CSV file (use '-' for stdin).",
    )
    p.add_argument(
        "specs",
        nargs="+",
        metavar="INDEX=NAME",
        help="Column rename specs, e.g. 0=id 2=score.",
    )
    p.add_argument(
        "-o", "--output",
        default=None,
        metavar="FILE",
        help="Output file (default: stdout).",
    )
    p.set_defaults(func=run)


def _parse_specs(specs: List[str]) -> Dict[int, str]:
    """Parse INDEX=NAME strings into a mapping of column index -> new name.

    Raises ValueError for malformed specs.
    """
    result: Dict[int, str] = {}
    for spec in specs:
        if "=" not in spec:
            raise ValueError(f"Invalid spec {spec!r}: expected INDEX=NAME format.")
        idx_str, _, name = spec.partition("=")
        if not idx_str.lstrip("-").isdigit():
            raise ValueError(f"Invalid index {idx_str!r}: must be an integer.")
        if not name:
            raise ValueError(f"Empty name in spec {spec!r}.")
        result[int(idx_str)] = name
    return result


def _rename_header(fieldnames: List[str], mapping: Dict[int, str]) -> List[str]:
    """Return a new header list with positions renamed according to *mapping*."""
    header = list(fieldnames)
    for idx, new_name in mapping.items():
        if idx < 0:
            idx = len(header) + idx
        if idx < 0 or idx >= len(header):
            raise IndexError(
                f"Column index {idx} is out of range for a CSV with "
                f"{len(header)} columns."
            )
        header[idx] = new_name
    return header


def _write(rows, fieldnames: List[str], dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: Namespace) -> None:
    """Execute the rename-cols command."""
    try:
        mapping = _parse_specs(args.specs)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    src = sys.stdin if args.file == "-" else open(args.file, newline="")
    try:
        reader = csv.DictReader(src)
        if reader.fieldnames is None:
            # Consume first row to populate fieldnames
            next(reader, None)
        original_fields: List[str] = list(reader.fieldnames or [])

        try:
            new_fields = _rename_header(original_fields, mapping)
        except IndexError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)

        # Build renamed rows lazily
        rename_map = dict(zip(original_fields, new_fields))
        renamed_rows = (
            {rename_map[k]: v for k, v in row.items()} for row in reader
        )

        if args.output:
            with open(args.output, "w", newline="") as out:
                _write(renamed_rows, new_fields, out)
        else:
            _write(renamed_rows, new_fields, sys.stdout)
    finally:
        if src is not sys.stdin:
            src.close()
