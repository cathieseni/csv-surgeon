"""Tests for csv_surgeon/commands/ceil_cmd.py."""
from __future__ import annotations

import csv
import io
import math
import sys
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.ceil_cmd import (
    _ceil_rows,
    _parse_columns,
    _write,
    run,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_rows(*dicts):
    return iter(list(dicts))


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


# ---------------------------------------------------------------------------
# _parse_columns
# ---------------------------------------------------------------------------

def test_parse_columns_single():
    assert _parse_columns("price") == ["price"]


def test_parse_columns_multiple():
    assert _parse_columns("price, tax, total") == ["price", "tax", "total"]


def test_parse_columns_strips_spaces():
    assert _parse_columns(" a , b ") == ["a", "b"]


def test_parse_columns_empty_raises():
    with pytest.raises(ValueError, match="at least one"):
        _parse_columns("")


# ---------------------------------------------------------------------------
# _ceil_rows
# ---------------------------------------------------------------------------

def test_ceil_rows_integer_values():
    rows = _make_rows({"x": "2.1"}, {"x": "3.0"}, {"x": "4.9"})
    result = list(_ceil_rows(rows, ["x"], 1.0))
    assert [r["x"] for r in result] == ["3", "3", "5"]


def test_ceil_rows_already_integer():
    rows = _make_rows({"x": "5.0"})
    result = list(_ceil_rows(rows, ["x"], 1.0))
    assert result[0]["x"] == "5"


def test_ceil_rows_multiple():
    rows = _make_rows({"x": "11"}, {"x": "15"}, {"x": "21"})
    result = list(_ceil_rows(rows, ["x"], 10.0))
    assert [r["x"] for r in result] == ["20", "20", "30"]


def test_ceil_rows_non_numeric_unchanged():
    rows = _make_rows({"x": "n/a"}, {"x": ""})
    result = list(_ceil_rows(rows, ["x"], 1.0))
    assert result[0]["x"] == "n/a"
    assert result[1]["x"] == ""


def test_ceil_rows_preserves_other_columns():
    rows = _make_rows({"name": "Alice", "score": "7.2"})
    result = list(_ceil_rows(rows, ["score"], 1.0))
    assert result[0]["name"] == "Alice"
    assert result[0]["score"] == "8"


def test_ceil_rows_invalid_multiple_raises():
    rows = _make_rows({"x": "1"})
    with pytest.raises(ValueError, match="positive"):
        list(_ceil_rows(rows, ["x"], 0.0))


# ---------------------------------------------------------------------------
# run (integration via capsys)
# ---------------------------------------------------------------------------

@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("item,price\nA,1.1\nB,2.9\nC,3.0\n")
    return str(p)


class _Args(SimpleNamespace):
    def __init__(self, **kwargs):
        defaults = {"output": None, "multiple": 1.0}
        defaults.update(kwargs)
        super().__init__(**defaults)


def test_run_stdout(csv_file, capsys):
    run(_Args(file=csv_file, columns="price"))
    rows = _read_stdout(capsys)
    assert [r["price"] for r in rows] == ["2", "3", "3"]


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    run(_Args(file=csv_file, columns="price", output=out))
    with open(out) as f:
        rows = list(csv.DictReader(f))
    assert [r["price"] for r in rows] == ["2", "3", "3"]


def test_run_multiple_10(csv_file, capsys):
    run(_Args(file=csv_file, columns="price", multiple=10.0))
    rows = _read_stdout(capsys)
    assert all(r["price"] == "10" for r in rows)
