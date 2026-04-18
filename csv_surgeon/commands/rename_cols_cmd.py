"""rename-cols command: rename header columns by position or pattern."""
from __future__ import annotations

import csv
import io
import re
import sys
from argparse import ArgumentParser, Namespace
from typing import List, Tuple


def add_subparser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "rename-cols",
        help="Rename CSV columns by index (0:new) or regex (s/old/new/)",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.add_argument(
        "specs",
        nargs="+",
        help="Rename specs: index:new_name  OR  s/pattern/replacement/",
    )
    p.set_defaults(func=run)


def _parse_specs(specs: List[str]) -> List[Tuple[str, str | int]]:
    """Return list of (kind, value) where kind is 'index' or 'regex'."""
    parsed = []
    for spec in specs:
        if spec.startswith("s/"):
            parts = spec.split("/")
            if len(parts) != 4 or parts[0] != "s":
                raise ValueError(f"Invalid regex spec: {spec!r}")
            parsed.append(("regex", parts[1], parts[2]))
        elif ":" in spec:
            idx_str, new_name = spec.split(":", 1)
            if not idx_str.lstrip("-").isdigit():
                raise ValueError(f"Invalid index spec: {spec!r}")
            parsed.append(("index", int(idx_str), new_name))
        else:
            raise ValueError(f"Unrecognised spec: {spec!r}")
    return parsed


def _rename_header(fieldnames: List[str], parsed_specs) -> List[str]:
    header = list(fieldnames)
    for spec in parsed_specs:
        if spec[0] == "index":
            _, idx, new_name = spec
            if idx < 0:
                idx = len(header) + idx
            if 0 <= idx < len(header):
                header[idx] = new_name
            else:
                raise IndexError(f"Column index {idx} out of range")
        else:  # regex
            _, pattern, replacement = spec
            header = [re.sub(pattern, replacement, col) for col in header]
    return header


def _write(rows, fieldnames, output) -> None:
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args: Namespace) -> None:
    parsed_specs = _parse_specs(args.specs)

    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return
        old_names = list(reader.fieldnames)
        new_names = _rename_header(old_names, parsed_specs)
        mapping = dict(zip(old_names, new_names))

        rows = []
        for row in reader:
            rows.append({mapping.get(k, k): v for k, v in row.items()})

    if args.output:
        with open(args.output, "w", newline="") as out:
            _write(rows, new_names, out)
    else:
        _write(rows, new_names, sys.stdout)
