"""Command-line interface for csv-surgeon."""

from __future__ import annotations

import argparse
import sys

from csv_surgeon.transformer import transform_file


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csv-surgeon",
        description="In-place CSV filtering with a chainable DSL.",
    )
    p.add_argument("input", help="Path to the input CSV file.")
    p.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output file path. Defaults to overwriting the input file.",
    )
    p.add_argument(
        "-f",
        "--filter",
        dest="filter_dsl",
        default="",
        metavar="EXPR",
        help=(
            "Semicolon-separated filter expressions, e.g. "
            "'age>30;name~Alice'. "
            "Operators: = != > >= < <= ~ (contains) ^ (startswith)."
        ),
    )
    p.add_argument(
        "-d",
        "--delimiter",
        default=",",
        help="Field delimiter (default: ',').",
    )
    p.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding (default: utf-8).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    output_path = args.output or args.input

    try:
        count = transform_file(
            args.input,
            output_path,
            args.filter_dsl,
            delimiter=args.delimiter,
            encoding=args.encoding,
        )
    except FileNotFoundError as exc:
        print(f"csv-surgeon: error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"csv-surgeon: filter error: {exc}", file=sys.stderr)
        return 2

    print(f"csv-surgeon: {count} row(s) written to '{output_path}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
