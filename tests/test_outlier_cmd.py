"""Unit tests for outlier_cmd."""
from __future__ import annotations

import csv
import io
import sys
from types import SimpleNamespace
from typing import List, Dict

import pytest

from csv_surgeon.commands.outlier_cmd import (
    _detect_outliers,
    _is_outlier_iqr,
    _is_outlier_zscore,
    _percentile,
    run,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_rows(values: List[float], col: str = "v") -> List[Dict[str, str]]:
    return [{col: str(v)} for v in values]


def _read_stdout(capsys) -> List[Dict[str, str]]:
    captured = capsys.readouterr().out
    return list(csv.DictReader(io.StringIO(captured)))


# ---------------------------------------------------------------------------
# _percentile
# ---------------------------------------------------------------------------

def test_percentile_median():
    assert _percentile([1.0, 2.0, 3.0, 4.0, 5.0], 50) == 3.0


def test_percentile_q1():
    vals = sorted([1.0, 2.0, 3.0, 4.0])
    result = _percentile(vals, 25)
    assert result == pytest.approx(1.75)


def test_percentile_empty():
    assert _percentile([], 50) == 0.0


# ---------------------------------------------------------------------------
# _is_outlier_iqr
# ---------------------------------------------------------------------------

def test_iqr_not_outlier():
    vals = sorted([1.0, 2.0, 3.0, 4.0, 5.0])
    assert not _is_outlier_iqr(3.0, vals, 1.5)


def test_iqr_is_outlier_high():
    vals = sorted([1.0, 2.0, 3.0, 4.0, 100.0])
    assert _is_outlier_iqr(100.0, vals, 1.5)


def test_iqr_is_outlier_low():
    vals = sorted([-100.0, 1.0, 2.0, 3.0, 4.0])
    assert _is_outlier_iqr(-100.0, vals, 1.5)


# ---------------------------------------------------------------------------
# _is_outlier_zscore
# ---------------------------------------------------------------------------

def test_zscore_not_outlier():
    assert not _is_outlier_zscore(0.0, 0.0, 1.0, 3.0)


def test_zscore_is_outlier():
    assert _is_outlier_zscore(10.0, 0.0, 1.0, 3.0)


def test_zscore_zero_sigma_never_outlier():
    assert not _is_outlier_zscore(999.0, 5.0, 0.0, 3.0)


# ---------------------------------------------------------------------------
# _detect_outliers
# ---------------------------------------------------------------------------

def test_detect_outliers_iqr_flags_correctly():
    rows = _make_rows([1, 2, 3, 4, 100])
    flags = _detect_outliers(rows, "v", "iqr", 1.5, 3.0)
    assert flags == [False, False, False, False, True]


def test_detect_outliers_zscore_flags_correctly():
    rows = _make_rows([1, 2, 3, 4, 100])
    flags = _detect_outliers(rows, "v", "zscore", 1.5, 2.0)
    assert flags[-1] is True
    assert all(not f for f in flags[:-1])


def test_detect_outliers_non_numeric_not_flagged():
    rows = [{"v": "abc"}, {"v": "1"}, {"v": "2"}]
    flags = _detect_outliers(rows, "v", "iqr", 1.5, 3.0)
    assert flags[0] is False


# ---------------------------------------------------------------------------
# run – flag action
# ---------------------------------------------------------------------------

class _Args(SimpleNamespace):
    def __init__(self, input, column, method="iqr", k=1.5, threshold=3.0,
                 action="flag", output=None):
        super().__init__(
            input=input, column=column, method=method, k=k,
            threshold=threshold, action=action, output=output,
        )


@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,score\nalice,10\nbob,12\ncharlie,200\n")
    return str(p)


def test_run_flag_adds_column(csv_file, capsys):
    run(_Args(csv_file, column="score"))
    rows = _read_stdout(capsys)
    assert "outlier" in rows[0]


def test_run_flag_marks_outlier(csv_file, capsys):
    run(_Args(csv_file, column="score"))
    rows = _read_stdout(capsys)
    outlier_flags = {r["name"]: r["outlier"] for r in rows}
    assert outlier_flags["charlie"] == "1"
    assert outlier_flags["alice"] == "0"
    assert outlier_flags["bob"] == "0"


def test_run_remove_drops_outlier(csv_file, capsys):
    run(_Args(csv_file, column="score", action="remove"))
    rows = _read_stdout(capsys)
    names = [r["name"] for r in rows]
    assert "charlie" not in names
    assert len(names) == 2


def test_run_remove_no_outlier_column(csv_file, capsys):
    run(_Args(csv_file, column="score", action="remove"))
    rows = _read_stdout(capsys)
    assert "outlier" not in rows[0]


def test_run_missing_column_exits(csv_file):
    with pytest.raises(SystemExit):
        run(_Args(csv_file, column="nonexistent"))


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    run(_Args(csv_file, column="score", output=out))
    rows = list(csv.DictReader(open(out)))
    assert len(rows) == 3
    assert "outlier" in rows[0]
