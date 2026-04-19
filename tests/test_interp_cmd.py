"""Tests for interp_cmd."""
from __future__ import annotations

import csv
import io
import pytest

from csv_surgeon.commands.interp_cmd import (
    _parse_columns,
    _interp_column,
    _interp_rows,
    run,
    _write,
)


def _make_rows(data):
    keys = list(data[0].keys())
    return [{k: str(v) for k, v in r.items()} for r in data], keys


# --- _parse_columns ---

def test_parse_columns_single():
    assert _parse_columns("price") == ["price"]


def test_parse_columns_multiple():
    assert _parse_columns("a, b, c") == ["a", "b", "c"]


def test_parse_columns_empty_raises():
    with pytest.raises(ValueError):
        _parse_columns("")


# --- _interp_column ---

def test_interp_column_no_missing():
    assert _interp_column(["1", "2", "3"]) == ["1", "2", "3"]


def test_interp_column_middle_missing():
    result = _interp_column(["0", "", "4"])
    assert result[1] != ""
    assert float(result[1]) == pytest.approx(2.0)


def test_interp_column_leading_missing():
    result = _interp_column(["", "", "3"])
    assert float(result[0]) == pytest.approx(3.0)
    assert float(result[1]) == pytest.approx(3.0)


def test_interp_column_trailing_missing():
    result = _interp_column(["5", "", ""])
    assert float(result[1]) == pytest.approx(5.0)
    assert float(result[2]) == pytest.approx(5.0)


def test_interp_column_all_missing():
    result = _interp_column(["", ""])
    assert float(result[0]) == pytest.approx(0.0)
    assert float(result[1]) == pytest.approx(0.0)


def test_interp_column_preserves_non_empty():
    original = ["1", "3", "5"]
    result = _interp_column(original)
    assert result == original


# --- _interp_rows ---

def test_interp_rows_fills_column():
    rows = [
        {"x": "1", "y": "10"},
        {"x": "", "y": "20"},
        {"x": "3", "y": "30"},
    ]
    result = _interp_rows(rows, ["x"])
    assert float(result[1]["x"]) == pytest.approx(2.0)
    assert result[1]["y"] == "20"  # untouched


def test_interp_rows_multiple_columns():
    rows = [
        {"a": "0", "b": "100"},
        {"a": "", "b": ""},
        {"a": "2", "b": "200"},
    ]
    result = _interp_rows(rows, ["a", "b"])
    assert float(result[1]["a"]) == pytest.approx(1.0)
    assert float(result[1]["b"]) == pytest.approx(150.0)


def test_interp_rows_empty_input():
    assert _interp_rows([], ["x"]) == []


# --- run via _write ---

def test_write_output():
    rows = [{"col": "1"}, {"col": "2"}]
    out = io.StringIO()
    _write(rows, ["col"], out)
    out.seek(0)
    reader = csv.DictReader(out)
    data = list(reader)
    assert [r["col"] for r in data] == ["1", "2"]
