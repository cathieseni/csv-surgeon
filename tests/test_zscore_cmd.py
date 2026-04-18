"""Tests for zscore_cmd."""
from __future__ import annotations

import csv
import io
import math
import sys
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.zscore_cmd import _compute_stats, _add_zscores, run


def _make_rows():
    return [
        {"name": "a", "score": "10"},
        {"name": "b", "score": "20"},
        {"name": "c", "score": "30"},
    ]


def test_compute_stats_basic():
    rows = _make_rows()
    mean, std = _compute_stats(rows, "score")
    assert mean == 20.0
    assert abs(std - math.sqrt(200 / 3)) < 1e-9


def test_compute_stats_constant_returns_std_one():
    rows = [{"v": "5"}, {"v": "5"}, {"v": "5"}]
    mean, std = _compute_stats(rows, "v")
    assert mean == 5.0
    assert std == 1.0


def test_compute_stats_empty_column():
    rows = [{"v": "x"}, {"v": "y"}]
    mean, std = _compute_stats(rows, "v")
    assert mean == 0.0
    assert std == 1.0


def test_add_zscores_keys_added():
    rows = _make_rows()
    result = _add_zscores(rows, ["score"], "_z", 4)
    assert all("score_z" in r for r in result)


def test_add_zscores_middle_is_zero():
    rows = _make_rows()
    result = _add_zscores(rows, ["score"], "_zscore", 6)
    assert float(result[1]["score_zscore"]) == pytest.approx(0.0, abs=1e-5)


def test_add_zscores_non_numeric_blank():
    rows = [{"v": "a"}, {"v": "b"}]
    result = _add_zscores(rows, ["v"], "_z", 4)
    assert result[0]["v_z"] == ""


def test_run_stdout(tmp_path, capsys):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,score\na,10\nb,20\nc,30\n")

    args = SimpleNamespace(
        input=str(csv_file),
        output=None,
        columns=["score"],
        suffix="_zscore",
        places=4,
    )
    run(args)
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert "score_zscore" in rows[0]
    assert float(rows[1]["score_zscore"]) == pytest.approx(0.0, abs=1e-4)


def test_run_output_file(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("x,y\n1,100\n2,200\n3,300\n")
    out_file = tmp_path / "out.csv"

    args = SimpleNamespace(
        input=str(csv_file),
        output=str(out_file),
        columns=["x", "y"],
        suffix="_z",
        places=3,
    )
    run(args)
    reader = csv.DictReader(out_file.open())
    rows = list(reader)
    assert "x_z" in rows[0]
    assert "y_z" in rows[0]
