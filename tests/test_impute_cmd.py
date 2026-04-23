"""Unit tests for impute_cmd."""
from __future__ import annotations

import csv
import io
import sys

import pytest

from csv_surgeon.commands.impute_cmd import (
    _compute_fill,
    _impute_rows,
    _parse_columns,
    run,
)


def _make_rows(data: list[dict]) -> list[dict]:
    return data


# ---------------------------------------------------------------------------
# _parse_columns
# ---------------------------------------------------------------------------

def test_parse_columns_single():
    assert _parse_columns("score") == ["score"]


def test_parse_columns_multiple():
    assert _parse_columns("a, b, c") == ["a", "b", "c"]


def test_parse_columns_empty_raises():
    with pytest.raises(ValueError):
        _parse_columns("   ")


# ---------------------------------------------------------------------------
# _compute_fill
# ---------------------------------------------------------------------------

ROWS = [
    {"score": "10", "grade": "A"},
    {"score": "",   "grade": "B"},
    {"score": "20", "grade": "C"},
    {"score": "30", "grade": ""},
]


def test_compute_fill_mean():
    assert _compute_fill(ROWS, "score", "mean", "0") == "20"


def test_compute_fill_median():
    assert _compute_fill(ROWS, "score", "median", "0") == "20"


def test_compute_fill_mode():
    rows = [{"v": "1"}, {"v": "2"}, {"v": "2"}, {"v": ""}]
    assert _compute_fill(rows, "v", "mode", "0") == "2"


def test_compute_fill_constant():
    assert _compute_fill(ROWS, "score", "constant", "99") == "99"


def test_compute_fill_all_missing_returns_fill_value():
    rows = [{"x": ""}, {"x": ""}]
    assert _compute_fill(rows, "x", "mean", "0") == "0"


# ---------------------------------------------------------------------------
# _impute_rows
# ---------------------------------------------------------------------------

def test_impute_rows_fills_blanks():
    rows = [{"a": "10"}, {"a": ""}, {"a": "20"}]
    result = _impute_rows(rows, ["a"], "mean", "0")
    assert result[1]["a"] == "15"


def test_impute_rows_leaves_non_blank_unchanged():
    rows = [{"a": "10"}, {"a": ""}, {"a": "20"}]
    result = _impute_rows(rows, ["a"], "mean", "0")
    assert result[0]["a"] == "10"
    assert result[2]["a"] == "20"


def test_impute_rows_multiple_columns():
    rows = [
        {"a": "1", "b": ""},
        {"a": "",  "b": "4"},
        {"a": "3", "b": "6"},
    ]
    result = _impute_rows(rows, ["a", "b"], "mean", "0")
    assert result[1]["a"] == "2"
    assert result[0]["b"] == "5"


# ---------------------------------------------------------------------------
# run (integration via _Args stub)
# ---------------------------------------------------------------------------

class _Args:
    def __init__(self, file, columns, strategy="mean", fill_value="0", output=None):
        self.file = file
        self.columns = columns
        self.strategy = strategy
        self.fill_value = fill_value
        self.output = output


def test_run_stdout(tmp_path, capsys):
    src = tmp_path / "data.csv"
    src.write_text("x,y\n1,\n,4\n3,6\n")
    run(_Args(str(src), "x,y"))
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert rows[0]["y"] == "5"
    assert rows[1]["x"] == "2"


def test_run_unknown_column_exits(tmp_path):
    src = tmp_path / "data.csv"
    src.write_text("a,b\n1,2\n")
    with pytest.raises(SystemExit):
        run(_Args(str(src), "z"))
