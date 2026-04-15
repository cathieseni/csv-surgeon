"""Tests for csv_surgeon/commands/freq_cmd.py."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import List, Dict

import pytest

from csv_surgeon.commands.freq_cmd import _compute_freq, run


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(
        "name,dept,score\n"
        "Alice,eng,90\n"
        "Bob,eng,85\n"
        "Carol,hr,92\n"
        "Dave,eng,88\n"
        "Eve,hr,75\n"
    )
    return p


class _Args(SimpleNamespace):
    def __init__(self, **kw):
        super().__init__(
            input="",
            columns=[],
            output=None,
            limit=None,
            asc=False,
            **kw,
        )


def _make_rows(text: str) -> List[Dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text)))


def _read_stdout(capsys) -> List[Dict[str, str]]:
    captured = capsys.readouterr().out
    return list(csv.DictReader(io.StringIO(captured)))


# ---------------------------------------------------------------------------
# Unit tests for _compute_freq
# ---------------------------------------------------------------------------

def test_compute_freq_basic():
    rows = _make_rows("dept\neng\neng\nhr\neng\nhr\n")
    result = _compute_freq(rows, ["dept"], limit=None, ascending=False)
    assert result[0] == {"column": "dept", "value": "eng", "count": "3"}
    assert result[1] == {"column": "dept", "value": "hr", "count": "2"}


def test_compute_freq_ascending():
    rows = _make_rows("dept\neng\neng\nhr\n")
    result = _compute_freq(rows, ["dept"], limit=None, ascending=True)
    assert result[0]["value"] == "hr"  # least common first


def test_compute_freq_limit():
    rows = _make_rows("dept\neng\neng\nhr\nfin\n")
    result = _compute_freq(rows, ["dept"], limit=1, ascending=False)
    assert len(result) == 1
    assert result[0]["value"] == "eng"


def test_compute_freq_multiple_columns():
    rows = _make_rows("dept,role\neng,dev\neng,qa\nhr,mgr\n")
    result = _compute_freq(rows, ["dept", "role"], limit=None, ascending=False)
    columns = [r["column"] for r in result]
    assert "dept" in columns and "role" in columns


# ---------------------------------------------------------------------------
# Integration tests via run()
# ---------------------------------------------------------------------------

def test_run_stdout(csv_file, capsys):
    args = _Args(input=str(csv_file), columns=["dept"])
    run(args)
    rows = _read_stdout(capsys)
    assert rows[0]["column"] == "dept"
    assert rows[0]["value"] == "eng"
    assert rows[0]["count"] == "3"


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    args = _Args(input=str(csv_file), columns=["dept"], output=str(out))
    run(args)
    rows = list(csv.DictReader(out.open()))
    assert len(rows) == 2  # eng + hr


def test_run_unknown_column_exits(csv_file):
    args = _Args(input=str(csv_file), columns=["nonexistent"])
    with pytest.raises(SystemExit):
        run(args)


def test_run_limit(csv_file, capsys):
    args = _Args(input=str(csv_file), columns=["dept"], limit=1)
    run(args)
    rows = _read_stdout(capsys)
    assert len(rows) == 1
