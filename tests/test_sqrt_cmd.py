"""Tests for sqrt_cmd."""
from __future__ import annotations

import csv
import io
import math
import pytest

from csv_surgeon.commands.sqrt_cmd import (
    _parse_columns,
    _sqrt_rows,
    _write,
    run,
)


# ---------------------------------------------------------------------------
# _parse_columns
# ---------------------------------------------------------------------------

def test_parse_columns_single():
    assert _parse_columns("value") == ["value"]


def test_parse_columns_multiple():
    assert _parse_columns("a,b,c") == ["a", "b", "c"]


def test_parse_columns_strips_spaces():
    assert _parse_columns(" x , y ") == ["x", "y"]


def test_parse_columns_empty_raises():
    with pytest.raises(ValueError):
        _parse_columns("")


# ---------------------------------------------------------------------------
# _sqrt_rows
# ---------------------------------------------------------------------------

def _make_rows():
    return [
        {"name": "a", "val": "9"},
        {"name": "b", "val": "4"},
        {"name": "c", "val": "0"},
    ]


def test_sqrt_rows_basic():
    rows = _sqrt_rows(_make_rows(), ["val"], "_sqrt")
    assert rows[0]["val_sqrt"] == str(math.sqrt(9))
    assert rows[1]["val_sqrt"] == str(math.sqrt(4))
    assert rows[2]["val_sqrt"] == str(math.sqrt(0))


def test_sqrt_rows_negative_gives_empty():
    rows = _sqrt_rows([{"v": "-1"}], ["v"], "_sqrt")
    assert rows[0]["v_sqrt"] == ""


def test_sqrt_rows_non_numeric_gives_empty():
    rows = _sqrt_rows([{"v": "abc"}], ["v"], "_sqrt")
    assert rows[0]["v_sqrt"] == ""


def test_sqrt_rows_custom_suffix():
    rows = _sqrt_rows([{"x": "16"}], ["x"], "_root")
    assert "x_root" in rows[0]
    assert rows[0]["x_root"] == str(4.0)


def test_sqrt_rows_preserves_original_column():
    rows = _sqrt_rows([{"x": "25"}], ["x"], "_sqrt")
    assert rows[0]["x"] == "25"


def test_sqrt_rows_multiple_columns():
    rows = _sqrt_rows([{"a": "9", "b": "16"}], ["a", "b"], "_sqrt")
    assert rows[0]["a_sqrt"] == str(3.0)
    assert rows[0]["b_sqrt"] == str(4.0)


# ---------------------------------------------------------------------------
# _write
# ---------------------------------------------------------------------------

def test_write_produces_valid_csv():
    rows = [{"x": "4", "x_sqrt": "2.0"}]
    buf = io.StringIO()
    _write(rows, ["x", "x_sqrt"], buf)
    buf.seek(0)
    reader = csv.DictReader(buf)
    result = list(reader)
    assert result[0]["x_sqrt"] == "2.0"


# ---------------------------------------------------------------------------
# run (integration via _Args)
# ---------------------------------------------------------------------------

class _Args:
    def __init__(self, file, columns, suffix="_sqrt", output=None):
        self.file = file
        self.columns = columns
        self.suffix = suffix
        self.output = output


def test_run_stdout(tmp_path, capsys):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,score\nalice,9\nbob,16\n")
    run(_Args(str(csv_file), "score"))
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert rows[0]["score_sqrt"] == str(math.sqrt(9))
    assert rows[1]["score_sqrt"] == str(math.sqrt(16))


def test_run_output_file(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("v\n4\n25\n")
    out_file = tmp_path / "out.csv"
    run(_Args(str(csv_file), "v", output=str(out_file)))
    reader = csv.DictReader(out_file.open())
    rows = list(reader)
    assert rows[0]["v_sqrt"] == str(2.0)
    assert rows[1]["v_sqrt"] == str(5.0)


def test_run_missing_column_raises(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("a\n1\n")
    with pytest.raises(SystemExit):
        run(_Args(str(csv_file), "nonexistent"))
