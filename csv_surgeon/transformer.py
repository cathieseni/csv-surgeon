"""CSV transformation engine: applies filter chains to CSV data."""

from __future__ import annotations

import csv
import io
from typing import Iterable, Iterator, List

from csv_surgeon.parser import FilterExpression, matches, parse_filters


def filter_rows(
    rows: Iterable[dict],
    filter_expressions: List[FilterExpression],
) -> Iterator[dict]:
    """Yield rows that satisfy ALL filter expressions (AND semantics)."""
    for row in rows:
        if all(matches(row, expr) for expr in filter_expressions):
            yield row


def transform_csv(
    source: str,
    filter_dsl: str,
    *,
    delimiter: str = ",",
) -> str:
    """Apply a DSL filter string to CSV source text and return filtered CSV.

    Args:
        source: Raw CSV text.
        filter_dsl: Semicolon-separated filter expressions, e.g.
                    ``"age>30;name~Alice"``.
        delimiter: Field delimiter (default ``','``).

    Returns:
        Filtered CSV text preserving the original header.
    """
    expressions = parse_filters(filter_dsl) if filter_dsl.strip() else []

    reader = csv.DictReader(io.StringIO(source), delimiter=delimiter)
    fieldnames = reader.fieldnames or []

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        delimiter=delimiter,
        lineterminator="\n",
    )
    writer.writeheader()

    for row in filter_rows(reader, expressions):
        writer.writerow(row)

    return output.getvalue()


def transform_file(
    input_path: str,
    output_path: str,
    filter_dsl: str,
    *,
    delimiter: str = ",",
    encoding: str = "utf-8",
) -> int:
    """Read *input_path*, apply filters, write result to *output_path*.

    Returns:
        Number of rows written (excluding header).
    """
    with open(input_path, newline="", encoding=encoding) as fh:
        source = fh.read()

    result = transform_csv(source, filter_dsl, delimiter=delimiter)

    with open(output_path, "w", newline="", encoding=encoding) as fh:
        fh.write(result)

    # Count data rows (lines minus header)
    lines = [ln for ln in result.splitlines() if ln]
    return max(0, len(lines) - 1)
