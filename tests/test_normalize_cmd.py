"""Tests for normalize_cmd."""
from __future__ import annotations

import csv
import io
import math
import types

import pytest

from csv_surgeon.commands.normalize_cmd import (
    _compute_stats,
    _normalize_rows,
    _parse_columns,
    run,
)


def _make_rows(data: list[dict]) -> list[dict]:
    return [dict(r) for r in data]


RAW = [
    {"name": "a", "score": "10", "val": "100"},
    {"name": "b", "score": "20", "val": "200"},
    {"name": "c", "score": "30", "val": "300"},
]


def test_parse_columns_single():
    assert _parse_columns("score") == ["score"]


def test_parse_columns_multiple():
    assert _parse_columns("score, val") == ["score", "val"]


def test_compute_stats_minmax():
    stats = _compute_stats(RAW, ["score"])
    assert stats["score"]["min"] == 10.0
    assert stats["score"]["max"] == 30.0


def test_compute_stats_zscore_mean():
    stats = _compute_stats(RAW, ["score"])
    assert stats["score"]["mean"] == pytest.approx(20.0)


def test_normalize_minmax_range():
    stats = _compute_stats(RAW, ["score"])
    rows = _normalize_rows(RAW, ["score"], stats, "minmax")
    values = [float(r["score"]) for r in rows]
    assert min(values) == pytest.approx(0.0)
    assert max(values) == pytest.approx(1.0)


def test_normalize_zscore_mean_zero():
    stats = _compute_stats(RAW, ["score"])
    rows = _normalize_rows(RAW, ["score"], stats, "zscore")
    values = [float(r["score"]) for r in rows]
    assert sum(values) == pytest.approx(0.0, abs=1e-5)


def test_normalize_preserves_non_numeric_columns():
    stats = _compute_stats(RAW, ["score"])
    rows = _normalize_rows(RAW, ["score"], stats, "minmax")
    assert rows[0]["name"] == "a"


def test_normalize_skips_non_numeric_values():
    data = [{"x": "bad"}, {"x": "2"}]
    stats = _compute_stats(data, ["x"])
    rows = _normalize_rows(data, ["x"], stats, "minmax")
    assert rows[0]["x"] == "bad"


class _Args:
    def __init__(self, file, columns, method="minmax", output=None):
        self.file = file
        self.columns = columns
        self.method = method
        self.output = output


def test_run_stdout(tmp_path, capsys):
    f = tmp_path / "data.csv"
    f.write_text("name,score\na,10\nb,20\nc,30\n")
    run(_Args(str(f), "score"))
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert float(rows[0]["score"]) == pytest.approx(0.0)
    assert float(rows[2]["score"]) == pytest.approx(1.0)


def test_run_output_file(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("name,score\na,5\nb,15\n")
    out = tmp_path / "out.csv"
    run(_Args(str(f), "score", output=str(out)))
    rows = list(csv.DictReader(out.open()))
    assert float(rows[0]["score"]) == pytest.approx(0.0)
    assert float(rows[1]["score"]) == pytest.approx(1.0)
