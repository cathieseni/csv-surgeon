"""Tests for csv_surgeon/commands/slice_cmd.py."""
from __future__ import annotations

import csv
import io
from typing import List, Dict, Optional

import pytest

from csv_surgeon.commands.slice_cmd import _slice_rows, run


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ROWS: List[Dict[str, str]] = [
    {"id": str(i), "val": str(i * 10)} for i in range(10)
]


@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "val"])
        writer.writeheader()
        writer.writerows(ROWS)
    return str(p)


class _Args:
    def __init__(
        self,
        input: str,
        start: int = 0,
        end: Optional[int] = None,
        step: int = 1,
        output: Optional[str] = None,
    ):
        self.input = input
        self.start = start
        self.end = end
        self.step = step
        self.output = output
        self.func = run


# ---------------------------------------------------------------------------
# Unit: _slice_rows
# ---------------------------------------------------------------------------

def test_slice_default():
    result = _slice_rows(ROWS, 0, None, 1)
    assert result == ROWS


def test_slice_start():
    result = _slice_rows(ROWS, 3, None, 1)
    assert result[0]["id"] == "3"
    assert len(result) == 7


def test_slice_end():
    result = _slice_rows(ROWS, 0, 5, 1)
    assert len(result) == 5
    assert result[-1]["id"] == "4"


def test_slice_start_end():
    result = _slice_rows(ROWS, 2, 6, 1)
    assert [r["id"] for r in result] == ["2", "3", "4", "5"]


def test_slice_step():
    result = _slice_rows(ROWS, 0, None, 2)
    assert [r["id"] for r in result] == ["0", "2", "4", "6", "8"]


def test_slice_step_invalid():
    with pytest.raises(ValueError, match="--step"):
        _slice_rows(ROWS, 0, None, 0)


def test_slice_out_of_range():
    result = _slice_rows(ROWS, 8, 20, 1)
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Integration: run()
# ---------------------------------------------------------------------------

def test_run_stdout_default(csv_file, capsys):
    run(_Args(input=csv_file))
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert len(rows) == 10


def test_run_stdout_slice(csv_file, capsys):
    run(_Args(input=csv_file, start=2, end=5))
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert len(rows) == 3
    assert rows[0]["id"] == "2"


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    run(_Args(input=csv_file, start=0, end=3, output=out))
    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3


def test_run_step(csv_file, capsys):
    run(_Args(input=csv_file, step=3))
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert [r["id"] for r in rows] == ["0", "3", "6", "9"]
