"""Tests for csv_surgeon/commands/fill_cmd.py"""
from __future__ import annotations

import csv
import io
import textwrap
from pathlib import Path

import pytest

from csv_surgeon.commands.fill_cmd import _fill_row, _parse_specs, run


CSV_CONTENT = textwrap.dedent("""\
    id,name,score
    1,Alice,90
    2,,85
    3,Carol,
    4,,
""").strip()


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(CSV_CONTENT, encoding="utf-8")
    return p


class _Args:
    def __init__(self, file, spec, output=None):
        self.file = str(file)
        self.spec = spec
        self.output = output


# --- unit tests ---

def test_parse_specs_single():
    assert _parse_specs(["name=N/A"]) == {"name": "N/A"}


def test_parse_specs_multiple():
    result = _parse_specs(["name=N/A", "score=0"])
    assert result == {"name": "N/A", "score": "0"}


def test_parse_specs_value_with_equals():
    # value itself contains '='
    result = _parse_specs(["name=a=b"])
    assert result == {"name": "a=b"}


def test_parse_specs_invalid():
    with pytest.raises(ValueError):
        _parse_specs(["badspec"])


def test_fill_row_empty_cell():
    row = {"id": "1", "name": "", "score": "90"}
    result = _fill_row(row, {"name": "Unknown"})
    assert result["name"] == "Unknown"
    assert result["score"] == "90"


def test_fill_row_non_empty_untouched():
    row = {"id": "1", "name": "Alice", "score": ""}
    result = _fill_row(row, {"name": "Unknown", "score": "0"})
    assert result["name"] == "Alice"
    assert result["score"] == "0"


# --- integration tests ---

def test_run_stdout(csv_file, capsys):
    run(_Args(csv_file, spec=["name=Unknown", "score=0"]))
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert rows[1]["name"] == "Unknown"
    assert rows[2]["score"] == "0"
    assert rows[0]["name"] == "Alice"  # unchanged


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    run(_Args(csv_file, spec=["name=N/A"], output=str(out)))
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert rows[1]["name"] == "N/A"


def test_run_unknown_column_exits(csv_file):
    with pytest.raises(SystemExit):
        run(_Args(csv_file, spec=["ghost=x"]))
