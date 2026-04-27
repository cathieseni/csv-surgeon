"""bin_cmd – assign rows to equal-width bins for a numeric column."""
from __future__ import annotations

import csv
import sys
from typing import List


def add_subparser(subparsers):
    p = subparsers.add_parser("bin", help="Assign rows to equal-width numeric bins")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--column", required=True, help="Numeric column to bin")
    p.add_argument("--bins", type=int, default=5, help="Number of equal-width bins (default: 5)")
    p.add_argument("--label", default="bin", help="Output column name (default: bin)")
    p.add_argument("--output", "-o", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _compute_edges(values: List[float], n_bins: int) -> List[float]:
    """Return n_bins+1 equally-spaced edges covering [min, max]."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    if lo == hi:
        return [lo - 0.5 + i for i in range(n_bins + 1)]
    step = (hi - lo) / n_bins
    return [lo + i * step for i in range(n_bins + 1)]


def _assign_bin(value: float, edges: List[float]) -> str:
    """Return a label like '[0.0, 2.5)' for the bin the value falls into."""
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        # Last bin is inclusive on the right
        if i == len(edges) - 2:
            if lo <= value <= hi:
                return f"[{lo:.4g}, {hi:.4g}]"
        else:
            if lo <= value < hi:
                return f"[{lo:.4g}, {hi:.4g})"
    return ""


def _bin_rows(rows, column: str, n_bins: int, label: str):
    rows = list(rows)
    values = []
    for row in rows:
        try:
            values.append(float(row[column]))
        except (ValueError, KeyError):
            pass

    edges = _compute_edges(values, n_bins)

    for row in rows:
        new_row = dict(row)
        try:
            v = float(row[column])
            new_row[label] = _assign_bin(v, edges) if edges else ""
        except (ValueError, KeyError):
            new_row[label] = ""
        yield new_row


def _write(rows, fieldnames, dest):
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


def run(args):
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        rows = list(_bin_rows(reader, args.column, args.bins, args.label))

    out_fields = fieldnames + ([args.label] if args.label not in fieldnames else [])

    if args.output:
        with open(args.output, "w", newline="") as fh:
            _write(rows, out_fields, fh)
    else:
        _write(rows, out_fields, sys.stdout)
