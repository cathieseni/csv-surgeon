"""Tests for movavg_cmd."""
from __future__ import annotations

import csv
import io
import types

import pytest

from csv_surgeon.commands.movavg_cmd import _movavg_rows, run


def _make_rows(values):
    return [{"id": str(i + 1), "val": str(v)} for i, v in enumerate(values)]


def test_movavg_single_element():
    rows = _make_rows([10])
    result = list(_movavg_rows(rows, "val", 3, "val_mavg"))
    assert float(result[0]["val_mavg"]) == pytest.approx(10.0)


def test_movavg_window_3():
    rows = _make_rows([1, 2, 3, 4, 5])
    result = list(_movavg_rows(rows, "val", 3, "val_mavg"))
    assert float(result[0]["val_mavg"]) == pytest.approx(1.0)
    assert float(result[1]["val_mavg"]) == pytest.approx(1.5)
    assert float(result[2]["val_mavg"]) == pytest.approx(2.0)
    assert float(result[3]["val_mavg"]) == pytest.approx(3.0)
    assert float(result[4]["val_mavg"]) == pytest.approx(4.0)


def test_movavg_window_1():
    rows = _make_rows([7, 8, 9])
    result = list(_movavg_rows(rows, "val", 1, "val_mavg"))
    assert [float(r["val_mavg"]) for r in result] == pytest.approx([7.0, 8.0, 9.0])


def test_movavg_skips_non_numeric():
    rows = [{"val": "abc"}, {"val": "2"}, {"val": "4"}]
    result = list(_movavg_rows(rows, "val", 2, "out"))
    # first value is NaN – average of only non-nan values in window
    assert float(result[1]["out"]) == pytest.approx(2.0)
    assert float(result[2]["out"]) == pytest.approx(3.0)


def test_movavg_preserves_other_columns():
    rows = [{"id": "1", "val": "5", "name": "alice"}]
    result = list(_movavg_rows(rows, "val", 3, "val_mavg"))
    assert result[0]["name"] == "alice"
    assert result[0]["id"] == "1"


def test_run_stdout(tmp_path, capsys):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("id,price\n1,10\n2,20\n3,30\n")
    args = types.SimpleNamespace(
        input=str(csv_path),
        col="price",
        window=2,
        out_col=None,
        output=None,
    )
    run(args)
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert "price_mavg" in rows[0]
    assert float(rows[2]["price_mavg"]) == pytest.approx(25.0)


def test_run_output_file(tmp_path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("x,y\n1,100\n2,200\n3,300\n")
    out_path = tmp_path / "out.csv"
    args = types.SimpleNamespace(
        input=str(csv_path),
        col="y",
        window=3,
        out_col="y_ma",
        output=str(out_path),
    )
    run(args)
    rows = list(csv.DictReader(out_path.open()))
    assert "y_ma" in rows[0]
    assert float(rows[2]["y_ma"]) == pytest.approx(200.0)
