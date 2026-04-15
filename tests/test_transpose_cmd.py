"""Unit tests for csv_surgeon/commands/transpose_cmd.py."""
from __future__ import annotations

import csv
import io
import sys
import textwrap
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.transpose_cmd import _transpose_rows, _write, run


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_rows():
    return [
        {"name": "Alice", "age": "30", "city": "NY"},
        {"name": "Bob",   "age": "25", "city": "LA"},
    ]


def _fieldnames():
    return ["name", "age", "city"]


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(textwrap.dedent("""\
        name,age,city
        Alice,30,NY
        Bob,25,LA
    """), encoding="utf-8")
    return p


class _Args(Namespace):
    def __init__(self, file, output=None):
        super().__init__()
        self.file = file
        self.output = output


# ---------------------------------------------------------------------------
# _transpose_rows
# ---------------------------------------------------------------------------

def test_transpose_shape():
    transposed = _transpose_rows(_make_rows(), _fieldnames())
    # 3 fields → 3 rows in transposed output
    assert len(transposed) == 3
    # each row: field name + 2 values
    assert all(len(r) == 3 for r in transposed)


def test_transpose_first_column_is_header():
    transposed = _transpose_rows(_make_rows(), _fieldnames())
    assert [r[0] for r in transposed] == ["name", "age", "city"]


def test_transpose_values():
    transposed = _transpose_rows(_make_rows(), _fieldnames())
    assert transposed[0] == ["name", "Alice", "Bob"]
    assert transposed[1] == ["age", "30", "25"]
    assert transposed[2] == ["city", "NY", "LA"]


def test_transpose_single_row():
    rows = [{"x": "1", "y": "2"}]
    transposed = _transpose_rows(rows, ["x", "y"])
    assert transposed == [["x", "1"], ["y", "2"]]


def test_transpose_empty_rows():
    transposed = _transpose_rows([], ["a", "b"])
    assert transposed == [["a"], ["b"]]


# ---------------------------------------------------------------------------
# run – stdout
# ---------------------------------------------------------------------------

def test_run_stdout(csv_file, capsys):
    run(_Args(file=str(csv_file)))
    captured = capsys.readouterr().out
    reader = csv.reader(io.StringIO(captured))
    rows = list(reader)
    assert rows[0] == ["name", "Alice", "Bob"]
    assert rows[1] == ["age", "30", "25"]
    assert rows[2] == ["city", "NY", "LA"]


# ---------------------------------------------------------------------------
# run – output file
# ---------------------------------------------------------------------------

def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    run(_Args(file=str(csv_file), output=str(out)))
    rows = list(csv.reader(out.open(encoding="utf-8")))
    assert rows[0] == ["name", "Alice", "Bob"]
    assert len(rows) == 3
