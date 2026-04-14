"""Tests for csv_surgeon/commands/rename_cmd.py."""

from __future__ import annotations

import csv
import io
import sys
import types
from pathlib import Path

import pytest

from csv_surgeon.commands.rename_cmd import _parse_specs, run


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text("name,age,city\nAlice,30,NY\nBob,25,LA\n", encoding="utf-8")
    return p


class _Args:
    def __init__(self, input, specs, output=None):
        self.input = str(input)
        self.specs = specs
        self.output = output


# --- _parse_specs unit tests ---

def test_parse_specs_single():
    assert _parse_specs(["name:full_name"]) == {"name": "full_name"}


def test_parse_specs_multiple():
    result = _parse_specs(["name:full_name", "age:years"])
    assert result == {"name": "full_name", "age": "years"}


def test_parse_specs_invalid_no_colon():
    with pytest.raises(ValueError, match="OLD:NEW"):
        _parse_specs(["badspec"])


def test_parse_specs_empty_old():
    with pytest.raises(ValueError, match="non-empty"):
        _parse_specs([":new"])


def test_parse_specs_empty_new():
    with pytest.raises(ValueError, match="non-empty"):
        _parse_specs(["old:"])


# --- run() integration tests ---

def test_run_stdout(csv_file, capsys):
    args = _Args(csv_file, ["name:full_name"])
    run(args)
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert reader.fieldnames == ["full_name", "age", "city"]
    assert rows[0]["full_name"] == "Alice"
    assert rows[1]["full_name"] == "Bob"


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    args = _Args(csv_file, ["age:years", "city:location"], output=str(out))
    run(args)
    reader = csv.DictReader(out.open(newline="", encoding="utf-8"))
    rows = list(reader)
    assert reader.fieldnames == ["name", "years", "location"]
    assert rows[0]["years"] == "30"
    assert rows[1]["location"] == "LA"


def test_run_unknown_column_exits(csv_file, capsys):
    args = _Args(csv_file, ["nonexistent:foo"])
    with pytest.raises(SystemExit) as exc_info:
        run(args)
    assert exc_info.value.code == 1
    assert "nonexistent" in capsys.readouterr().err


def test_run_invalid_spec_exits(csv_file, capsys):
    args = _Args(csv_file, ["badspec"])
    with pytest.raises(SystemExit) as exc_info:
        run(args)
    assert exc_info.value.code == 1
