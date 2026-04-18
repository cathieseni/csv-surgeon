"""Tests for cumsum_cmd."""
from __future__ import annotations

import csv
import io
import textwrap

import pytest

from csv_surgeon.commands.cumsum_cmd import _cumsum_rows, run


def _make_rows():
    return [
        {"name": "a", "val": "10", "qty": "2"},
        {"name": "b", "val": "5",  "qty": "3"},
        {"name": "c", "val": "20", "qty": "1"},
    ]


def test_cumsum_single_column():
    rows = _make_rows()
    result = _cumsum_rows(rows, ["val"])
    assert [r["val_cumsum"] for r in result] == [10.0, 15.0, 35.0]


def test_cumsum_multiple_columns():
    rows = _make_rows()
    result = _cumsum_rows(rows, ["val", "qty"])
    assert [r["qty_cumsum"] for r in result] == [2.0, 5.0, 6.0]
    assert [r["val_cumsum"] for r in result] == [10.0, 15.0, 35.0]


def test_cumsum_skips_non_numeric():
    rows = [
        {"x": "1"},
        {"x": "n/a"},
        {"x": "3"},
    ]
    result = _cumsum_rows(rows, ["x"])
    assert result[0]["x_cumsum"] == 1.0
    assert result[1]["x_cumsum"] == 1.0   # unchanged on bad value
    assert result[2]["x_cumsum"] == 4.0


def test_cumsum_preserves_original_columns():
    rows = _make_rows()
    result = _cumsum_rows(rows, ["val"])
    assert result[0]["name"] == "a"
    assert result[0]["val"] == "10"


def test_cumsum_empty_rows():
    assert _cumsum_rows([], ["val"]) == []


class _Args:
    def __init__(self, input, columns, output="-"):
        self.input = input
        self.columns = columns
        self.output = output


def test_run_stdout(tmp_path, capsys):
    f = tmp_path / "data.csv"
    f.write_text("item,amount\nA,100\nB,50\nC,200\n")
    run(_Args(str(f), ["amount"]))
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert rows[0]["amount_cumsum"] == "100.0"
    assert rows[2]["amount_cumsum"] == "350.0"


def test_run_output_file(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("item,amount\nA,100\nB,50\n")
    out = tmp_path / "out.csv"
    run(_Args(str(f), ["amount"], str(out)))
    reader = csv.DictReader(out.open())
    rows = list(reader)
    assert rows[1]["amount_cumsum"] == "150.0"
