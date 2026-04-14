"""Tests for csv_surgeon/commands/cast_cmd.py."""
from __future__ import annotations

import csv
import io
import os
import tempfile
from typing import List, Dict, Optional

import pytest

from csv_surgeon.commands.cast_cmd import _parse_specs, _cast_row, run


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,age,score\nAlice,30,9.5\nBob,25,8.0\nCarol,40,7.75\n", encoding="utf-8")
    return str(p)


class _Args:
    def __init__(
        self,
        input: str,
        specs: List[str],
        output: Optional[str] = None,
        errors: str = "raise",
    ):
        self.input = input
        self.specs = specs
        self.output = output
        self.errors = errors
        self.func = run


def _read_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Unit: _parse_specs
# ---------------------------------------------------------------------------

def test_parse_specs_single():
    assert _parse_specs(["age:int"]) == {"age": "int"}


def test_parse_specs_multiple():
    result = _parse_specs(["age:int", "score:float"])
    assert result == {"age": "int", "score": "float"}


def test_parse_specs_invalid_no_colon():
    with pytest.raises(ValueError, match="Invalid cast spec"):
        _parse_specs(["ageint"])


def test_parse_specs_unknown_type():
    with pytest.raises(ValueError, match="Unknown type"):
        _parse_specs(["age:integer"])


# ---------------------------------------------------------------------------
# Unit: _cast_row
# ---------------------------------------------------------------------------

def test_cast_row_int():
    row = {"name": "Alice", "age": "30"}
    result = _cast_row(row, {"age": "int"}, "raise")
    assert result["age"] == "30"  # stored as str representation


def test_cast_row_bool_true():
    row = {"flag": "true"}
    result = _cast_row(row, {"flag": "bool"}, "raise")
    assert result["flag"] == "True"


def test_cast_row_bool_false():
    row = {"flag": "0"}
    result = _cast_row(row, {"flag": "bool"}, "raise")
    assert result["flag"] == "False"


def test_cast_row_error_null():
    row = {"age": "notanumber"}
    result = _cast_row(row, {"age": "int"}, "null")
    assert result["age"] == ""


def test_cast_row_error_keep():
    row = {"age": "notanumber"}
    result = _cast_row(row, {"age": "int"}, "keep")
    assert result["age"] == "notanumber"


def test_cast_row_error_raise():
    row = {"age": "notanumber"}
    with pytest.raises((ValueError, TypeError)):
        _cast_row(row, {"age": "int"}, "raise")


# ---------------------------------------------------------------------------
# Integration: run()
# ---------------------------------------------------------------------------

def test_run_stdout(csv_file, capsys):
    args = _Args(input=csv_file, specs=["age:int", "score:float"])
    run(args)
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert rows[0]["age"] == "30"
    assert rows[0]["score"] == "9.5"


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _Args(input=csv_file, specs=["age:int"], output=out)
    run(args)
    rows = _read_csv(out)
    assert len(rows) == 3
    assert rows[1]["age"] == "25"


def test_run_errors_null(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("name,age\nAlice,30\nBob,N/A\n", encoding="utf-8")
    out = str(tmp_path / "out.csv")
    args = _Args(input=str(p), specs=["age:int"], output=out, errors="null")
    run(args)
    rows = _read_csv(out)
    assert rows[1]["age"] == ""
