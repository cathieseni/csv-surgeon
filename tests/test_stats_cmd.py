"""Tests for csv_surgeon/commands/stats_cmd.py"""
from __future__ import annotations

import csv
import io
import sys
from argparse import Namespace
from pathlib import Path

import pytest

from csv_surgeon.commands.stats_cmd import _compute_stats, _write, run


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(
        "name,age,score\n"
        "Alice,30,88.5\n"
        "Bob,25,92.0\n"
        "Carol,35,76.0\n"
        "Dave,,bad\n",  # missing age, non-numeric score
    )
    return p


class _Args(Namespace):
    def __init__(self, file, columns=None, output=None):
        super().__init__()
        self.file = str(file)
        self.columns = columns
        self.output = output


def _read_stdout(capsys) -> list[dict]:
    captured = capsys.readouterr().out
    return list(csv.DictReader(io.StringIO(captured)))


def test_compute_stats_basic():
    rows = [
        {"age": "30", "score": "88.5"},
        {"age": "25", "score": "92.0"},
        {"age": "35", "score": "76.0"},
    ]
    stats = _compute_stats(rows, ["age", "score"])
    assert stats["age"]["count"] == 3
    assert stats["age"]["min"] == 25.0
    assert stats["age"]["max"] == 35.0
    assert stats["age"]["sum"] == 90.0
    assert stats["age"]["mean"] == 30.0
    assert stats["score"]["count"] == 3


def test_compute_stats_skips_non_numeric():
    rows = [{"x": "1"}, {"x": "abc"}, {"x": "3"}]
    stats = _compute_stats(rows, ["x"])
    assert stats["x"]["count"] == 2
    assert stats["x"]["sum"] == 4.0


def test_compute_stats_all_non_numeric():
    rows = [{"x": "a"}, {"x": "b"}]
    stats = _compute_stats(rows, ["x"])
    assert stats["x"]["count"] == 0
    assert stats["x"]["mean"] == ""


def test_write_output():
    stats = {"age": {"count": 2, "min": 20.0, "max": 30.0, "sum": 50.0, "mean": 25.0}}
    buf = io.StringIO()
    _write(stats, buf)
    buf.seek(0)
    rows = list(csv.DictReader(buf))
    assert len(rows) == 1
    assert rows[0]["column"] == "age"
    assert rows[0]["mean"] == "25.0"


def test_run_stdout_all_columns(csv_file, capsys):
    run(_Args(csv_file))
    rows = _read_stdout(capsys)
    cols = {r["column"] for r in rows}
    assert "age" in cols
    assert "score" in cols


def test_run_stdout_selected_columns(csv_file, capsys):
    run(_Args(csv_file, columns=["age"]))
    rows = _read_stdout(capsys)
    assert len(rows) == 1
    assert rows[0]["column"] == "age"
    assert rows[0]["count"] == "3"


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "stats.csv"
    run(_Args(csv_file, output=str(out)))
    rows = list(csv.DictReader(out.open()))
    assert any(r["column"] == "score" for r in rows)


def test_run_unknown_column_exits(csv_file):
    with pytest.raises(SystemExit):
        run(_Args(csv_file, columns=["nonexistent"]))
