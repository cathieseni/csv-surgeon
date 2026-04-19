"""Tests for lag_cmd."""
from __future__ import annotations

import csv
import io
import sys
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.lag_cmd import _lag_rows, _parse_columns, run


def _make_rows(data):
    return [dict(zip(data[0], row)) for row in data[1:]]


def test_parse_columns_single():
    assert _parse_columns("price") == ["price"]


def test_parse_columns_multiple():
    assert _parse_columns("price,qty") == ["price", "qty"]


def test_parse_columns_empty_raises():
    with pytest.raises(ValueError):
        _parse_columns("  ")


def test_lag_rows_default_period():
    rows = _make_rows([["val"], ["10"], ["20"], ["30"]])
    result = _lag_rows(rows, ["val"], 1, "")
    assert result[0]["val_lag1"] == ""
    assert result[1]["val_lag1"] == "10"
    assert result[2]["val_lag1"] == "20"


def test_lag_rows_period_2():
    rows = _make_rows([["val"], ["1"], ["2"], ["3"], ["4"]])
    result = _lag_rows(rows, ["val"], 2, "NA")
    assert result[0]["val_lag2"] == "NA"
    assert result[1]["val_lag2"] == "NA"
    assert result[2]["val_lag2"] == "1"
    assert result[3]["val_lag2"] == "2"


def test_lag_rows_multiple_columns():
    rows = _make_rows([["a", "b"], ["1", "x"], ["2", "y"]])
    result = _lag_rows(rows, ["a", "b"], 1, "")
    assert result[1]["a_lag1"] == "1"
    assert result[1]["b_lag1"] == "x"


def test_lag_rows_preserves_original():
    rows = _make_rows([["val"], ["10"], ["20"]])
    result = _lag_rows(rows, ["val"], 1, "")
    assert result[0]["val"] == "10"
    assert result[1]["val"] == "20"


def test_run_stdout(tmp_path, capsys):
    f = tmp_path / "data.csv"
    f.write_text("price,qty\n100,5\n200,10\n300,15\n")
    args = SimpleNamespace(
        input=str(f), columns="price", periods=1, fill="", output=None
    )
    run(args)
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert "price_lag1" in rows[0]
    assert rows[0]["price_lag1"] == ""
    assert rows[1]["price_lag1"] == "100"


def test_run_output_file(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("val\n1\n2\n3\n")
    out = tmp_path / "out.csv"
    args = SimpleNamespace(
        input=str(f), columns="val", periods=1, fill="0", output=str(out)
    )
    run(args)
    rows = list(csv.DictReader(out.open()))
    assert rows[0]["val_lag1"] == "0"
    assert rows[2]["val_lag1"] == "2"
