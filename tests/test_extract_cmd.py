"""Tests for extract_cmd."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.extract_cmd import (
    _extract_rows,
    _parse_columns,
    _write,
    run,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\nCarol,35,Chicago\n")
    return p


class _Args(SimpleNamespace):
    def __init__(self, input, columns, output=None):
        super().__init__(input=str(input), columns=columns, output=output)


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_parse_columns_single():
    assert _parse_columns("name") == ["name"]


def test_parse_columns_multiple():
    assert _parse_columns("name,age") == ["name", "age"]


def test_parse_columns_strips_spaces():
    assert _parse_columns(" name , age ") == ["name", "age"]


def test_parse_columns_empty_raises():
    with pytest.raises(ValueError):
        _parse_columns("")


def _make_rows():
    return [
        {"name": "Alice", "age": "30", "city": "NYC"},
        {"name": "Bob", "age": "25", "city": "LA"},
    ]


def test_extract_rows_single_column():
    result = list(_extract_rows(_make_rows(), ["name"]))
    assert result == [{"name": "Alice"}, {"name": "Bob"}]


def test_extract_rows_multiple_columns():
    result = list(_extract_rows(_make_rows(), ["name", "city"]))
    assert result == [
        {"name": "Alice", "city": "NYC"},
        {"name": "Bob", "city": "LA"},
    ]


def test_extract_rows_missing_column_raises():
    with pytest.raises(KeyError):
        list(_extract_rows(_make_rows(), ["nonexistent"]))


def test_extract_rows_preserves_order():
    result = list(_extract_rows(_make_rows(), ["city", "name"]))
    assert list(result[0].keys()) == ["city", "name"]


# ---------------------------------------------------------------------------
# Integration via run()
# ---------------------------------------------------------------------------

def test_run_stdout(csv_file, capsys):
    run(_Args(csv_file, "name,age"))
    rows = _read_stdout(capsys)
    assert len(rows) == 3
    assert list(rows[0].keys()) == ["name", "age"]


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    run(_Args(csv_file, "name,city", output=str(out)))
    rows = list(csv.DictReader(out.open()))
    assert len(rows) == 3
    assert all("age" not in r for r in rows)


def test_run_missing_column_raises(csv_file):
    with pytest.raises(KeyError):
        run(_Args(csv_file, "name,salary"))
