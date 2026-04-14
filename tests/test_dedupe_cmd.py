"""Tests for csv_surgeon/commands/dedupe_cmd.py"""
from __future__ import annotations

import csv
import io
import textwrap
from pathlib import Path
from typing import List

import pytest

from csv_surgeon.commands.dedupe_cmd import _dedupe, run


CSV_CONTENT = textwrap.dedent("""\
    id,name,dept
    1,Alice,Eng
    2,Bob,HR
    3,Alice,Eng
    4,Carol,HR
    5,Bob,Sales
""").strip()


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(CSV_CONTENT, encoding="utf-8")
    return p


class _Args:
    def __init__(self, file, keys, keep="first", output=None):
        self.file = str(file)
        self.keys = keys
        self.keep = keep
        self.output = output


# --- unit tests for _dedupe ---

def _make_rows() -> List[dict]:
    return [
        {"id": "1", "name": "Alice", "dept": "Eng"},
        {"id": "2", "name": "Bob",   "dept": "HR"},
        {"id": "3", "name": "Alice", "dept": "Eng"},
        {"id": "4", "name": "Carol", "dept": "HR"},
        {"id": "5", "name": "Bob",   "dept": "Sales"},
    ]


def test_dedupe_keep_first_single_key():
    rows = _make_rows()
    result = _dedupe(rows, keys=["name"], keep="first")
    assert [r["id"] for r in result] == ["1", "2", "4"]


def test_dedupe_keep_last_single_key():
    rows = _make_rows()
    result = _dedupe(rows, keys=["name"], keep="last")
    assert [r["id"] for r in result] == ["3", "4", "5"]


def test_dedupe_multi_key():
    rows = _make_rows()
    result = _dedupe(rows, keys=["name", "dept"], keep="first")
    # Bob,HR and Bob,Sales are distinct
    assert [r["id"] for r in result] == ["1", "2", "4", "5"]


def test_dedupe_no_duplicates():
    rows = _make_rows()
    result = _dedupe(rows, keys=["id"], keep="first")
    assert len(result) == len(rows)


# --- integration tests via run() ---

def test_run_stdout(csv_file, capsys):
    run(_Args(csv_file, keys=["name"], keep="first"))
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    ids = [r["id"] for r in reader]
    assert ids == ["1", "2", "4"]


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    run(_Args(csv_file, keys=["name"], keep="last", output=str(out)))
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert [r["id"] for r in rows] == ["3", "4", "5"]


def test_run_unknown_key_exits(csv_file):
    with pytest.raises(SystemExit):
        run(_Args(csv_file, keys=["nonexistent"]))
