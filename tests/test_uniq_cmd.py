"""Tests for the uniq command."""
from __future__ import annotations

import csv
import io
import sys
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.uniq_cmd import _uniq_rows, run


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _make_rows(data):
    """Convert list-of-tuples [(col, val), ...] rows into list of dicts."""
    return [dict(row) for row in data]


ROWS = [
    {"city": "NYC", "val": "1"},
    {"city": "NYC", "val": "2"},
    {"city": "LA", "val": "3"},
    {"city": "LA", "val": "4"},
    {"city": "NYC", "val": "5"},
]


@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("city,val\nNYC,1\nNYC,2\nLA,3\nLA,4\nNYC,5\n")
    return str(p)


class _Args(SimpleNamespace):
    def __init__(self, **kw):
        defaults = {"input": "-", "column": "city", "output": None, "count": False}
        defaults.update(kw)
        super().__init__(**defaults)


def _read_stdout(capsys):
    out = capsys.readouterr().out
    return list(csv.DictReader(io.StringIO(out)))


# ---------------------------------------------------------------------------
# Unit tests for _uniq_rows
# ---------------------------------------------------------------------------


def test_uniq_basic():
    result = list(_uniq_rows(ROWS, "city", include_count=False))
    assert [r["city"] for r in result] == ["NYC", "LA", "NYC"]


def test_uniq_with_count():
    result = list(_uniq_rows(ROWS, "city", include_count=True))
    assert result[0]["__count__"] == 2
    assert result[1]["__count__"] == 2
    assert result[2]["__count__"] == 1


def test_uniq_empty():
    assert list(_uniq_rows([], "city", include_count=False)) == []


def test_uniq_all_same():
    rows = [{"x": "a"}, {"x": "a"}, {"x": "a"}]
    result = list(_uniq_rows(rows, "x", include_count=True))
    assert len(result) == 1
    assert result[0]["__count__"] == 3


def test_uniq_all_different():
    rows = [{"x": str(i)} for i in range(4)]
    result = list(_uniq_rows(rows, "x", include_count=False))
    assert len(result) == 4


# ---------------------------------------------------------------------------
# Integration tests via run()
# ---------------------------------------------------------------------------


def test_run_stdout(csv_file, capsys):
    run(_Args(input=csv_file))
    rows = _read_stdout(capsys)
    assert [r["city"] for r in rows] == ["NYC", "LA", "NYC"]


def test_run_with_count(csv_file, capsys):
    run(_Args(input=csv_file, count=True))
    rows = _read_stdout(capsys)
    assert "__count__" in rows[0]
    assert rows[0]["__count__"] == "2"


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    run(_Args(input=csv_file, output=out))
    with open(out) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3


def test_run_invalid_column(csv_file):
    with pytest.raises(ValueError, match="not found"):
        run(_Args(input=csv_file, column="nonexistent"))
