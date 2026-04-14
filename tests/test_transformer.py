"""Tests for csv_surgeon.transformer."""

from __future__ import annotations

import textwrap

import pytest

from csv_surgeon.transformer import filter_rows, transform_csv

SAMPLE_CSV = textwrap.dedent("""\
    name,age,city
    Alice,30,Berlin
    Bob,25,Paris
    Carol,35,Berlin
    Dave,28,Rome
""").strip()


def _rows():
    return [
        {"name": "Alice", "age": "30", "city": "Berlin"},
        {"name": "Bob", "age": "25", "city": "Paris"},
        {"name": "Carol", "age": "35", "city": "Berlin"},
        {"name": "Dave", "age": "28", "city": "Rome"},
    ]


def test_filter_rows_no_filters():
    from csv_surgeon.parser import parse_filters
    result = list(filter_rows(_rows(), parse_filters("") if False else []))
    assert len(result) == 4


def test_filter_rows_equality():
    from csv_surgeon.parser import parse_filters
    exprs = parse_filters("city=Berlin")
    result = list(filter_rows(_rows(), exprs))
    assert len(result) == 2
    assert all(r["city"] == "Berlin" for r in result)


def test_filter_rows_numeric_gt():
    from csv_surgeon.parser import parse_filters
    exprs = parse_filters("age>28")
    result = list(filter_rows(_rows(), exprs))
    assert {r["name"] for r in result} == {"Alice", "Carol"}


def test_filter_rows_chained():
    from csv_surgeon.parser import parse_filters
    exprs = parse_filters("city=Berlin;age>30")
    result = list(filter_rows(_rows(), exprs))
    assert len(result) == 1
    assert result[0]["name"] == "Carol"


def test_transform_csv_empty_filter():
    result = transform_csv(SAMPLE_CSV, "")
    lines = [ln for ln in result.splitlines() if ln]
    assert lines[0] == "name,age,city"
    assert len(lines) == 5  # header + 4 data rows


def test_transform_csv_with_filter():
    result = transform_csv(SAMPLE_CSV, "city=Berlin")
    lines = [ln for ln in result.splitlines() if ln]
    assert len(lines) == 3  # header + 2 matches


def test_transform_csv_no_match():
    result = transform_csv(SAMPLE_CSV, "city=Tokyo")
    lines = [ln for ln in result.splitlines() if ln]
    assert len(lines) == 1  # header only


def test_transform_csv_contains():
    result = transform_csv(SAMPLE_CSV, "name~li")
    lines = [ln for ln in result.splitlines() if ln]
    # Alice contains 'li'
    assert len(lines) == 2


def test_transform_csv_startswith():
    result = transform_csv(SAMPLE_CSV, "name^C")
    lines = [ln for ln in result.splitlines() if ln]
    assert len(lines) == 2  # Carol
