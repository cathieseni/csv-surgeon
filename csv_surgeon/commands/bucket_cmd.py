"""bucket_cmd: bin numeric column values into labeled buckets."""
from __future__ import annotations

import csv
import sys
from typing import List, Tuple


def add_subparser(subparsers):
    p = subparsers.add_parser("bucket", help="Bin a numeric column into labeled buckets")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--col", required=True, help="Column to bucket")
    p.add_argument(
        "--bins",
        required=True,
        nargs="+",
        metavar="EDGE",
        help="Bin edges (e.g. 0 10 20 100)",
    )
    p.add_argument(
        "--labels",
        nargs="+",
        metavar="LABEL",
        help="Labels for each bin (count = len(bins)-1)",
    )
    p.add_argument("--out-col", default="bucket", help="Name of new column (default: bucket)")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_bins(bin_strs: List[str]) -> List[float]:
    try:
        return [float(b) for b in bin_strs]
    except ValueError as exc:
        raise ValueError(f"Invalid bin edge: {exc}") from exc


def _assign_bucket(
    value: float, edges: List[float], labels: List[str]
) -> str:
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        if lo <= value < hi:
            return labels[i]
    # last edge inclusive
    if value == edges[-1]:
        return labels[-1]
    return ""


def _bucket_rows(rows, col: str, edges: List[float], labels: List[str], out_col: str):
    for row in rows:
        try:
            val = float(row[col])
        except (ValueError, KeyError):
            val = None
        row[out_col] = _assign_bucket(val, edges, labels) if val is not None else ""
        yield row


def _write(fieldnames, rows, dest):
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args):
    edges = _parse_bins(args.bins)
    if len(edges) < 2:
        print("bucket: need at least 2 bin edges", file=sys.stderr)
        sys.exit(1)
    n_bins = len(edges) - 1
    if args.labels:
        if len(args.labels) != n_bins:
            print(
                f"bucket: expected {n_bins} labels, got {len(args.labels)}",
                file=sys.stderr,
            )
            sys.exit(1)
        labels = args.labels
    else:
        labels = [f"[{edges[i]},{edges[i+1]})" for i in range(n_bins)]

    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or []) + [args.out_col]
        rows = list(_bucket_rows(reader, args.col, edges, labels, args.out_col))

    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(fieldnames, rows, fh)
    else:
        _write(fieldnames, rows, sys.stdout)
