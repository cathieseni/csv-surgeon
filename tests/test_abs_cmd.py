"""Tests for the abs command."""
from __future__ import annotations

import csv
import io
import sys
import pytest

from csv_surgeon.commands.abs_cmd import _parse_columns, _abs_rows, run


def _make_rows(data):
    """Create list of dicts from list-of-lists (first row = headers)."""
    headers = data[0]
    return [dict(zip(headers, row)) for row in data[1:]]


# --- _parse_columns ---

def test_parse_columns_single():
    assert _parse_columns("score") == ["score"]


def test_parse_columns_multiple():
    assert _parse_columns("a, b, c") == ["a", "b", "c"]


def test_parse_columns_empty_raises():
    with pytest.raises(ValueError):
        _parse_columns("")


# --- _abs_rows ---

def test_abs_rows_positive_unchanged():
    rows = _make_rows([["x"], ["3"], ["7"]])
    result = list(_abs_rows(rows, ["x"]))
    assert [r["x"] for r in result] == ["3", "7"]


def test_abs_rows_negative_made_positive():
    rows = _make_rows([["x"], ["-5"], ["-2"]])
    result = list(_abs_rows(rows, ["x"]))
    assert [r["x"] for r in result] == ["5", "2"]


def test_abs_rows_float_values():
    rows = _make_rows([["x"], ["-3.14"], ["2.71"]])
    result = list(_abs_rows(rows, ["x"]))
    assert float(result[0]["x"]) == pytest.approx(3.14)
    assert float(result[1]["x"]) == pytest.approx(2.71)


def test_abs_rows_non_numeric_unchanged():
    rows = _make_rows([["name", "val"], ["alice", "-10"], ["bob", "n/a"]])
    result = list(_abs_rows(rows, ["val"]))
    assert result[0]["val"] == "10"
    assert result[1]["val"] == "n/a"


def test_abs_rows_missing_column_raises():
    rows = _make_rows([["x"], ["1"]])
    with pytest.raises(KeyError):
        list(_abs_rows(rows, ["missing"]))


def test_abs_rows_multiple_columns():
    rows = _make_rows([["a", "b"], ["-1", "-2"], ["3", "-4"]])
    result = list(_abs_rows(rows, ["a", "b"]))
    assert result[0] == {"a": "1", "b": "2"}
    assert result[1] == {"a": "3", "b": "4"}


# --- run (integration via tmp file) ---

class _Args:
    def __init__(self, input, columns, output=None):
        self.input = input
        self.columns = columns
        self.output = output


def test_run_stdout(tmp_path, capsys):
    f = tmp_path / "data.csv"
    f.write_text("score,name\n-10,alice\n5,bob\n-3,carol\n")
    run(_Args(str(f), "score"))
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert [r["score"] for r in rows] == ["10", "5", "3"]


def test_run_output_file(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("val\n-7\n0\n4\n")
    out = tmp_path / "out.csv"
    run(_Args(str(f), "val", str(out)))
    reader = csv.DictReader(out.open())
    vals = [r["val"] for r in reader]
    assert vals == ["7", "0", "4"]
