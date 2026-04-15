"""Tests for csv_surgeon/commands/head_cmd.py."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.head_cmd import _head_rows, run


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    with p.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "name", "score"])
        for i in range(1, 21):          # 20 data rows
            writer.writerow([str(i), f"user{i}", str(i * 10)])
    return p


class _Args(SimpleNamespace):
    def __init__(self, file: str, rows: int = 10, output: str | None = None):
        super().__init__(file=file, rows=rows, output=output)


def _read_stdout(capsys) -> list[dict]:
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    return list(reader)


# ---------------------------------------------------------------------------
# Unit tests for _head_rows
# ---------------------------------------------------------------------------

def test_head_rows_default():
    rows = [{"a": str(i)} for i in range(20)]
    result = _head_rows(rows, 10)
    assert len(result) == 10
    assert result[0] == {"a": "0"}
    assert result[-1] == {"a": "9"}


def test_head_rows_fewer_than_n():
    rows = [{"a": str(i)} for i in range(3)]
    result = _head_rows(rows, 10)
    assert result == rows


def test_head_rows_zero():
    rows = [{"a": "1"}, {"a": "2"}]
    assert _head_rows(rows, 0) == []


def test_head_rows_negative_raises():
    with pytest.raises(ValueError, match="n must be >= 0"):
        _head_rows([], -1)


# ---------------------------------------------------------------------------
# Integration tests via run()
# ---------------------------------------------------------------------------

def test_run_default_ten(csv_file, capsys):
    run(_Args(str(csv_file)))
    rows = _read_stdout(capsys)
    assert len(rows) == 10
    assert rows[0]["id"] == "1"
    assert rows[-1]["id"] == "10"


def test_run_custom_n(csv_file, capsys):
    run(_Args(str(csv_file), rows=5))
    rows = _read_stdout(capsys)
    assert len(rows) == 5


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    run(_Args(str(csv_file), rows=3, output=str(out)))
    with out.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 3


def test_run_missing_file(tmp_path):
    with pytest.raises(SystemExit):
        run(_Args(str(tmp_path / "nope.csv")))
