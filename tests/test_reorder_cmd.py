"""Tests for reorder_cmd."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.reorder_cmd import _parse_columns, _reorder_rows, run


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text("a,b,c\n1,2,3\n4,5,6\n")
    return p


class _Args(SimpleNamespace):
    def __init__(self, **kw):
        super().__init__(input=None, columns="", output=None, **kw)


def _read_stdout(capsys) -> list[dict]:
    captured = capsys.readouterr().out
    return list(csv.DictReader(io.StringIO(captured)))


def test_parse_columns_single():
    assert _parse_columns("a") == ["a"]


def test_parse_columns_multiple():
    assert _parse_columns("c,a,b") == ["c", "a", "b"]


def test_parse_columns_strips_spaces():
    assert _parse_columns(" c , a ") == ["c", "a"]


def test_reorder_rows_basic():
    src = io.StringIO("a,b,c\n1,2,3\n")
    reader = csv.DictReader(src)
    ordered, rows = _reorder_rows(reader, ["c", "b", "a"])
    assert ordered == ["c", "b", "a"]
    assert rows[0] == {"c": "3", "b": "2", "a": "1"}


def test_reorder_rows_extra_columns_appended():
    src = io.StringIO("a,b,c\n1,2,3\n")
    reader = csv.DictReader(src)
    ordered, rows = _reorder_rows(reader, ["c", "a"])
    assert ordered == ["c", "a", "b"]


def test_reorder_rows_missing_column_raises():
    src = io.StringIO("a,b\n1,2\n")
    reader = csv.DictReader(src)
    with pytest.raises(ValueError, match="not found"):
        _reorder_rows(reader, ["a", "z"])


def test_run_stdout(csv_file, capsys):
    args = _Args(input=str(csv_file), columns="c,b,a")
    run(args)
    rows = _read_stdout(capsys)
    assert list(rows[0].keys()) == ["c", "b", "a"]
    assert rows[0] == {"c": "3", "b": "2", "a": "1"}


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    args = _Args(input=str(csv_file), columns="b,a,c", output=str(out))
    run(args)
    rows = list(csv.DictReader(out.open())0].keys()) == ["b", "a", "c"]


def test_run_stdin(csv_file, capsys, monkeypatch):
    monkeypatch.setattr(sys, "stdin", csv_file.open(newline=""))
    args = _Args(input="-", columns="c,a,b")
    run(args)
    rows = _read_stdout(capsys)
    assert rows[0]["c"] == "3"
