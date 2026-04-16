"""Tests for merge_cmd."""
from __future__ import annotations

import csv
import io
import pytest

from csv_surgeon.commands.merge_cmd import _merge_rows, run


FIELDS_A = ["id", "name"]
ROWS_A = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]

FIELDS_B = ["id", "name"]
ROWS_B = [{"id": "3", "name": "Carol"}]


def test_merge_same_schema():
    fields, rows = _merge_rows(FIELDS_A, ROWS_A, FIELDS_B, ROWS_B, fill=False)
    assert fields == ["id", "name"]
    assert len(rows) == 3
    assert rows[2]["name"] == "Carol"


def test_merge_extra_column_raises_without_fill():
    fields_b = ["id", "name", "dept"]
    rows_b = [{"id": "3", "name": "Carol", "dept": "Eng"}]
    with pytest.raises(ValueError, match="--fill"):
        _merge_rows(FIELDS_A, ROWS_A, fields_b, rows_b, fill=False)


def test_merge_extra_column_fill():
    fields_b = ["id", "name", "dept"]
    rows_b = [{"id": "3", "name": "Carol", "dept": "Eng"}]
    fields, rows = _merge_rows(FIELDS_A, ROWS_A, fields_b, rows_b, fill=True)
    assert "dept" in fields
    assert rows[0]["dept"] == ""
    assert rows[2]["dept"] == "Eng"


def test_merge_missing_column_fill():
    fields_b = ["id"]
    rows_b = [{"id": "3"}]
    fields, rows = _merge_rows(FIELDS_A, ROWS_A, fields_b, rows_b, fill=True)
    assert rows[2]["name"] == ""


@pytest.fixture()
def csv_files(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,name\n1,Alice\n2,Bob\n")
    b.write_text("id,name\n3,Carol\n")
    return str(a), str(b)


class _Args:
    def __init__(self, file, other, output=None, fill=False):
        self.file = file
        self.other = other
        self.output = output
        self.fill = fill


def test_run_stdout(csv_files, capsys):
    a, b = csv_files
    run(_Args(a, b))
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert len(rows) == 3
    assert rows[2]["name"] == "Carol"


def test_run_output_file(csv_files, tmp_path):
    a, b = csv_files
    out_path = str(tmp_path / "out.csv")
    run(_Args(a, b, output=out_path))
    with open(out_path) as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 3


def test_run_fill_flag(tmp_path, capsys):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,name\n1,Alice\n")
    b.write_text("id,name,dept\n2,Bob,Eng\n")
    run(_Args(str(a), str(b), fill=True))
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert rows[0]["dept"] == ""
    assert rows[1]["dept"] == "Eng"
