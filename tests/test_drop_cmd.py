"""Tests for csv_surgeon.commands.drop_cmd."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

import pytest

from csv_surgeon.commands.drop_cmd import _parse_columns, run


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\nCarol,35,Chicago\n", encoding="utf-8")
    return p


class _Args:
    def __init__(self, input, columns, output=None, inplace=False):
        self.input = input
        self.columns = columns
        self.output = output
        self.inplace = inplace


def _read_stdout(capsys) -> list[dict]:
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


# ---------------------------------------------------------------------------
# Unit tests for _parse_columns
# ---------------------------------------------------------------------------

def test_parse_columns_single():
    assert _parse_columns("age") == ["age"]


def test_parse_columns_multiple():
    assert _parse_columns("age, city") == ["age", "city"]


def test_parse_columns_strips_whitespace():
    assert _parse_columns(" name , city ") == ["name", "city"]


# ---------------------------------------------------------------------------
# Integration tests for run()
# ---------------------------------------------------------------------------

def test_drop_single_column(csv_file, capsys):
    run(_Args(str(csv_file), "age"))
    rows = _read_stdout(capsys)
    assert all("age" not in r for r in rows)
    assert rows[0] == {"name": "Alice", "city": "NYC"}


def test_drop_multiple_columns(csv_file, capsys):
    run(_Args(str(csv_file), "age,city"))
    rows = _read_stdout(capsys)
    assert rows == [{"name": "Alice"}, {"name": "Bob"}, {"name": "Carol"}]


def test_drop_to_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    run(_Args(str(csv_file), "city", output=str(out)))
    rows = list(csv.DictReader(out.open(newline="", encoding="utf-8")))
    assert "city" not in rows[0]
    assert rows[0]["name"] == "Alice"


def test_drop_inplace(csv_file):
    run(_Args(str(csv_file), "age", inplace=True))
    rows = list(csv.DictReader(csv_file.open(newline="", encoding="utf-8")))
    assert "age" not in rows[0]
    assert len(rows) == 3


def test_drop_unknown_column_raises(csv_file):
    with pytest.raises(ValueError, match="not found"):
        run(_Args(str(csv_file), "nonexistent"))


def test_drop_preserves_row_count(csv_file, capsys):
    run(_Args(str(csv_file), "city"))
    rows = _read_stdout(capsys)
    assert len(rows) == 3
