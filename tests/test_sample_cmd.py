"""Tests for csv_surgeon/commands/sample_cmd.py"""
from __future__ import annotations

import csv
import io
import sys
import textwrap
import pytest

from csv_surgeon.commands.sample_cmd import _sample_rows, run, _write


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CSV_CONTENT = textwrap.dedent("""\
    name,score
    alice,10
    bob,20
    carol,30
    dave,40
    eve,50
""").strip()


@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text(CSV_CONTENT + "\n")
    return p


class _Args:
    def __init__(self, input, count=None, fraction=None, seed=None, output=None):
        self.input = str(input)
        self.count = count
        self.fraction = fraction
        self.seed = seed
        self.output = output


def _parse_stdout(capsys):
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    return list(reader)


# ---------------------------------------------------------------------------
# Unit tests for _sample_rows
# ---------------------------------------------------------------------------

def _make_rows(n=5):
    return [{"name": f"r{i}", "val": str(i)} for i in range(n)]


def test_sample_by_count():
    rows = _make_rows(10)
    result = _sample_rows(rows, count=3, fraction=None, seed=42)
    assert len(result) == 3


def test_sample_by_fraction():
    rows = _make_rows(10)
    result = _sample_rows(rows, count=None, fraction=0.5, seed=0)
    assert len(result) == 5


def test_sample_count_exceeds_rows():
    rows = _make_rows(3)
    result = _sample_rows(rows, count=100, fraction=None, seed=1)
    assert len(result) == 3


def test_sample_invalid_count():
    with pytest.raises(ValueError, match="--count"):
        _sample_rows(_make_rows(5), count=-1, fraction=None, seed=None)


def test_sample_invalid_fraction():
    with pytest.raises(ValueError, match="--fraction"):
        _sample_rows(_make_rows(5), count=None, fraction=1.5, seed=None)


def test_sample_reproducible():
    rows = _make_rows(20)
    a = _sample_rows(rows, count=5, fraction=None, seed=7)
    b = _sample_rows(rows, count=5, fraction=None, seed=7)
    assert a == b


# ---------------------------------------------------------------------------
# Integration tests via run()
# ---------------------------------------------------------------------------

def test_run_count(csv_file, capsys):
    run(_Args(csv_file, count=2, seed=0))
    rows = _parse_stdout(capsys)
    assert len(rows) == 2
    assert all("name" in r and "score" in r for r in rows)


def test_run_fraction(csv_file, capsys):
    run(_Args(csv_file, fraction=0.4, seed=1))
    rows = _parse_stdout(capsys)
    assert len(rows) >= 1


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    run(_Args(csv_file, count=3, seed=5, output=str(out)))
    assert out.exists()
    reader = csv.DictReader(out.open())
    assert len(list(reader)) == 3
