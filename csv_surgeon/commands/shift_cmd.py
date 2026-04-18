"""shift_cmd: shift numeric column values by a constant offset or scale factor."""
import csv
import io
import sys
from typing import List, Tuple


def add_subparser(subparsers):
    p = subparsers.add_parser("shift", help="Shift or scale numeric column values")
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "--spec",
        dest="specs",
        metavar="COL:OP:VALUE",
        action="append",
        required=True,
        help="e.g. price:add:10  or  score:mul:1.5  (ops: add, sub, mul, div)",
    )
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=run)


def _parse_specs(raw: List[str]) -> List[Tuple[str, str, float]]:
    result = []
    valid_ops = {"add", "sub", "mul", "div"}
    for item in raw:
        parts = item.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid spec '{item}': expected COL:OP:VALUE")
        col, op, val_str = parts
        if op not in valid_ops:
            raise ValueError(f"Unknown op '{op}': choose from {sorted(valid_ops)}")
        try:
            val = float(val_str)
        except ValueError:
            raise ValueError(f"Non-numeric value '{val_str}' in spec '{item}'")
        result.append((col, op, val))
    return result


def _shift_row(row: dict, specs: List[Tuple[str, str, float]]) -> dict:
    row = dict(row)
    for col, op, val in specs:
        if col not in row:
            continue
        try:
            num = float(row[col])
        except (ValueError, TypeError):
            continue
        if op == "add":
            num += val
        elif op == "sub":
            num -= val
        elif op == "mul":
            num *= val
        elif op == "div":
            num /= val
        row[col] = str(num) if num != int(num) else str(int(num))
    return row


def _write(rows, fieldnames, dest):
    writer = csv.DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def run(args):
    specs = _parse_specs(args.specs)
    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = [_shift_row(r, specs) for r in reader]
    if args.output:
        with open(args.output, "w", newline="") as out:
            _write(rows, fieldnames, out)
    else:
        _write(rows, fieldnames, sys.stdout)
