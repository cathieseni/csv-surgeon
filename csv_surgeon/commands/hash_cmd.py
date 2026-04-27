"""hash_cmd – hash column values using md5, sha1, or sha256."""
from __future__ import annotations

import csv
import hashlib
import io
import sys
from typing import Iterable

_ALGOS = {"md5", "sha1", "sha256"}


def add_subparser(subparsers):
    p = subparsers.add_parser("hash", help="Hash column values")
    p.add_argument("input", help="Input CSV file (use '-' for stdin)")
    p.add_argument(
        "--columns",
        required=True,
        help="Comma-separated column names to hash",
    )
    p.add_argument(
        "--algo",
        default="sha256",
        choices=sorted(_ALGOS),
        help="Hash algorithm (default: sha256)",
    )
    p.add_argument(
        "--output", "-o",
        default=None,
        help="Output file (default: stdout)",
    )
    p.set_defaults(func=run)


def _parse_columns(raw: str) -> list[str]:
    cols = [c.strip() for c in raw.split(",")]
    if not cols or any(c == "" for c in cols):
        raise ValueError(f"Invalid --columns spec: {raw!r}")
    return cols


def _hash_rows(
    rows: Iterable[dict],
    columns: list[str],
    algo: str,
) -> Iterable[dict]:
    for row in rows:
        out = dict(row)
        for col in columns:
            raw = row.get(col, "")
            digest = hashlib.new(algo, raw.encode()).hexdigest()
            out[col] = digest
        yield out


def _write(rows: Iterable[dict], fieldnames: list[str], dest: io.TextIOBase):
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args):
    columns = _parse_columns(args.columns)

    src = sys.stdin if args.input == "-" else open(args.input, newline="")
    try:
        reader = csv.DictReader(src)
        fieldnames = list(reader.fieldnames or [])
        hashed = list(_hash_rows(reader, columns, args.algo))
    finally:
        if src is not sys.stdin:
            src.close()

    if args.output:
        with open(args.output, "w", newline="") as fout:
            _write(hashed, fieldnames, fout)
    else:
        _write(hashed, fieldnames, sys.stdout)
