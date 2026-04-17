"""Tests for split_cmd."""
from __future__ import annotations

import csv
import io
import os
import sys
from pathlib import Path

import pytest

from csv_surgeon.commands.split_cmd import _split_rows, _write, run


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text("name,dept\nAlice,Eng\nBob,HR\nCarol,Eng\nDave,HR\nEve,Finance\n")
    return p


class _Args:
    def __init__(self, input, by, outdir=".", prefix=""):
        self.input = input
        self.by = by
        self.outdir = outdir
        self.prefix = prefix


_ROWS = [
    {"name": "Alice", "dept": "Eng"},
    {"name": "Bob", "dept": "HR"},
    {"name": "Carol", "dept": "Eng"},
    {"name": "Dave", "dept": "HR"},
    {"name": "Eve", "dept": "Finance"},
]


def test_split_rows_groups_correctly():
    buckets = _split_rows(_ROWS, "dept")
    assert set(buckets.keys()) == {"Eng", "HR", "Finance"}
    assert len(buckets["Eng"]) == 2
    assert len(buckets["HR"]) == 2
    assert len(buckets["Finance"]) == 1


def test_split_rows_preserves_order():
    buckets = _split_rows(_ROWS, "dept")
    assert buckets["Eng"][0]["name"] == "Alice"
    assert buckets["Eng"][1]["name"] == "Carol"


def test_write_creates_files(tmp_path):
    buckets = {"Eng": [_ROWS[0]], "HR": [_ROWS[1]]}
    written = _write(buckets, ["name", "dept"], str(tmp_path), "")
    assert len(written) == 2
    for f in written:
        assert os.path.exists(f)


def test_write_file_contents(tmp_path):
    buckets = {"Eng": [_ROWS[0], _ROWS[2]]}
    _write(buckets, ["name", "dept"], str(tmp_path), "split_")
    out = tmp_path / "split_Eng.csv"
    rows = list(csv.DictReader(out.open()))
    assert [r["name"] for r in rows] == ["Alice", "Carol"]


def test_run_creates_output_files(csv_file, tmp_path):
    args = _Args(str(csv_file), "dept", str(tmp_path))
    run(args)
    files = list(tmp_path.iterdir())
    assert len(files) == 3


def test_run_missing_column_exits(csv_file, tmp_path, capsys):
    args = _Args(str(csv_file), "nonexistent", str(tmp_path))
    with pytest.raises(SystemExit):
        run(args)
    captured = capsys.readouterr()
    assert "nonexistent" in captured.err


def test_run_missing_file_exits(tmp_path, capsys):
    args = _Args(str(tmp_path / "missing.csv"), "dept", str(tmp_path))
    with pytest.raises(SystemExit):
        run(args)
