"""Tests for the shuffle command."""
from __future__ import annotations

import csv
import io
import sys
from types import SimpleNamespace
from typing import List, Dict

import pytest

from csv_surgeon.commands.shuffle_cmd import _shuffle_rows, _write, run


def _make_rows(n: int = 5) -> List[Dict[str, str]]:
    return [{"id": str(i), "val": str(i * 10)} for i in range(1, n + 1)]


# ---------------------------------------------------------------------------
# _shuffle_rows
# ---------------------------------------------------------------------------

def test_shuffle_rows_same_elements():
    rows = _make_rows(10)
    result = _shuffle_rows(rows, seed=42)
    assert sorted(r["id"] for r in result) == sorted(r["id"] for r in rows)


def test_shuffle_rows_reproducible_with_seed():
    rows = _make_rows(10)
    r1 = _shuffle_rows(rows, seed=7)
    r2 = _shuffle_rows(rows, seed=7)
    assert [r["id"] for r in r1] == [r["id"] for r in r2]


def test_shuffle_rows_different_seeds_differ():
    rows = _make_rows(20)
    r1 = _shuffle_rows(rows, seed=1)
    r2 = _shuffle_rows(rows, seed=2)
    # With 20 rows it is astronomically unlikely they match
    assert [r["id"] for r in r1] != [r["id"] for r in r2]


def test_shuffle_rows_no_seed_returns_all():
    rows = _make_rows(8)
    result = _shuffle_rows(rows, seed=None)
    assert len(result) == len(rows)


def test_shuffle_rows_does_not_mutate_original():
    rows = _make_rows(5)
    original_order = [r["id"] for r in rows]
    _shuffle_rows(rows, seed=99)
    assert [r["id"] for r in rows] == original_order


# ---------------------------------------------------------------------------
# _write
# ---------------------------------------------------------------------------

def test_write_produces_valid_csv():
    rows = _make_rows(3)
    buf = io.StringIO()
    _write(["id", "val"], rows, buf)
    buf.seek(0)
    reader = csv.DictReader(buf)
    out = list(reader)
    assert len(out) == 3
    assert out[0]["id"] == "1"


# ---------------------------------------------------------------------------
# run (integration)
# ---------------------------------------------------------------------------

@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("id,val\n1,10\n2,20\n3,30\n4,40\n5,50\n")
    return str(p)


class _Args(SimpleNamespace):
    def __init__(self, **kw):
        super().__init__(**kw)


def _read_stdout(capsys) -> List[Dict[str, str]]:
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    return list(reader)


def test_run_stdout_contains_all_rows(csv_file, capsys):
    args = _Args(input=csv_file, output=None, seed=42)
    run(args)
    rows = _read_stdout(capsys)
    assert sorted(r["id"] for r in rows) == ["1", "2", "3", "4", "5"]


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _Args(input=csv_file, output=out, seed=0)
    run(args)
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 5


def test_run_seed_reproducible(csv_file, capsys):
    args1 = _Args(input=csv_file, output=None, seed=123)
    run(args1)
    out1 = capsys.readouterr().out

    args2 = _Args(input=csv_file, output=None, seed=123)
    run(args2)
    out2 = capsys.readouterr().out

    assert out1 == out2
