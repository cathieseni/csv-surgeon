"""Tests for window_cmd."""
from __future__ import annotations

import csv
import io
import sys
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.window_cmd import _window_rows, run


def _make_rows(values: list[float]) -> list[dict]:
    return [{"id": str(i), "val": str(v)} for i, v in enumerate(values)]


def _read_stdout(capsys) -> list[dict]:
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


class _Args(SimpleNamespace):
    def __init__(self, tmp_path, col="val", size=3, func="mean", out_col=None, output=None):
        import csv as _csv
        rows = _make_rows([10, 20, 30, 40, 50])
        p = tmp_path / "data.csv"
        with open(p, "w", newline="") as fh:
            w = _csv.DictWriter(fh, fieldnames=["id", "val"])
            w.writeheader()
            w.writerows(rows)
        super().__init__(input=str(p), col=col, size=size, func=func, out_col=out_col, output=output)


def test_window_rows_mean():
    rows = _make_rows([10, 20, 30])
    result = list(_window_rows(rows, "val", 2, "mean", "val_mean_2"))
    assert result[0]["val_mean_2"] == "10.0"
    assert result[1]["val_mean_2"] == "15.0"
    assert result[2]["val_mean_2"] == "25.0"


def test_window_rows_sum():
    rows = _make_rows([1, 2, 3, 4])
    result = list(_window_rows(rows, "val", 3, "sum", "out"))
    assert result[2]["out"] == "6.0"
    assert result[3]["out"] == "9.0"


def test_window_rows_min():
    rows = _make_rows([5, 3, 8, 1])
    result = list(_window_rows(rows, "val", 2, "min", "out"))
    assert result[1]["out"] == "3.0"
    assert result[3]["out"] == "1.0"


def test_window_rows_max():
    rows = _make_rows([5, 3, 8, 1])
    result = list(_window_rows(rows, "val", 2, "max", "out"))
    assert result[1]["out"] == "5.0"
    assert result[2]["out"] == "8.0"


def test_window_rows_default_out_col_present():
    rows = _make_rows([1, 2, 3])
    result = list(_window_rows(rows, "val", 2, "mean", "val_mean_2"))
    assert "val_mean_2" in result[0]


def test_run_stdout(tmp_path, capsys):
    args = _Args(tmp_path, size=2, func="mean")
    run(args)
    rows = _read_stdout(capsys)
    assert len(rows) == 5
    assert "val_mean_2" in rows[0]


def test_run_output_file(tmp_path):
    out = tmp_path / "out.csv"
    args = _Args(tmp_path, size=2, func="sum", output=str(out))
    run(args)
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 5
    assert rows[1]["val_sum_2"] == "30.0"


def test_run_custom_out_col(tmp_path, capsys):
    args = _Args(tmp_path, size=3, func="mean", out_col="rolling_avg")
    run(args)
    rows = _read_stdout(capsys)
    assert "rolling_avg" in rows[0]
