"""Tests for diff_cmd."""
from __future__ import annotations

import csv
import io
import sys
from argparse import Namespace
from pathlib import Path

import pytest

from csv_surgeon.commands.diff_cmd import _diff_rows, _load, run


@pytest.fixture()
def csv_a(tmp_path: Path) -> Path:
    p = tmp_path / "a.csv"
    p.write_text("id,name\n1,Alice\n2,Bob\n")
    return p


@pytest.fixture()
def csv_b(tmp_path: Path) -> Path:
    p = tmp_path / "b.csv"
    p.write_text("id,name\n1,Alice\n3,Carol\n")
    return p


class _Args(Namespace):
    def __init__(self, **kw):
        defaults = dict(keys="", output="-")
        defaults.update(kw)
        super().__init__(**defaults)


def _read_stdout(capsys) -> list[dict]:
    out = capsys.readouterr().out
    return list(csv.DictReader(io.StringIO(out)))


def test_diff_rows_removed():
    a = [{"id": "1"}, {"id": "2"}]
    b = [{"id": "1"}]
    result = list(_diff_rows(a, b, ["id"]))
    removed = [r for r in result if r["_diff"] == "removed"]
    assert len(removed) == 1
    assert removed[0]["id"] == "2"


def test_diff_rows_added():
    a = [{"id": "1"}]
    b = [{"id": "1"}, {"id": "3"}]
    result = list(_diff_rows(a, b, ["id"]))
    added = [r for r in result if r["_diff"] == "added"]
    assert len(added) == 1
    assert added[0]["id"] == "3"


def test_diff_rows_no_diff():
    rows = [{"id": "1"}, {"id": "2"}]
    assert list(_diff_rows(rows, rows, ["id"])) == []


def test_run_stdout(csv_a, csv_b, capsys):
    run(_Args(file_a=str(csv_a), file_b=str(csv_b)))
    rows = _read_stdout(capsys)
    diffs = {r["_diff"] for r in rows}
    assert "removed" in diffs
    assert "added" in diffs


def test_run_output_file(csv_a, csv_b, tmp_path):
    out = tmp_path / "out.csv"
    run(_Args(file_a=str(csv_a), file_b=str(csv_b), output=str(out)))
    rows = list(csv.DictReader(out.open()))
    assert any(r["_diff"] == "removed" for r in rows)
    assert any(r["_diff"] == "added" for r in rows)


def test_run_mismatched_schema_raises(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,name\n1,Alice\n")
    b.write_text("id,email\n1,a@b.com\n")
    with pytest.raises(ValueError, match="schemas"):
        run(_Args(file_a=str(a), file_b=str(b)))


def test_run_invalid_key_raises(csv_a, csv_b):
    with pytest.raises(ValueError, match="Key column"):
        run(_Args(file_a=str(csv_a), file_b=str(csv_b), keys="nonexistent"))
