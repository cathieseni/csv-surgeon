"""Tests for truncate_cmd."""
from __future__ import annotations

import csv
import io
import sys
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.truncate_cmd import _parse_specs, _truncate_rows, run


def _make_rows(data):
    return [dict(zip(data[0], row)) for row in data[1:]]


# --- _parse_specs ---

def test_parse_specs_single():
    assert _parse_specs(["name:5"]) == {"name": 5}


def test_parse_specs_multiple():
    assert _parse_specs(["name:5", "city:3"]) == {"name": 5, "city": 3}


def test_parse_specs_zero():
    assert _parse_specs(["name:0"]) == {"name": 0}


def test_parse_specs_invalid_no_colon():
    with pytest.raises(ValueError, match="Invalid truncate spec"):
        _parse_specs(["name5"])


def test_parse_specs_invalid_non_int():
    with pytest.raises(ValueError, match="non-negative integer"):
        _parse_specs(["name:abc"])


# --- _truncate_rows ---

def test_truncate_rows_basic():
    rows = _make_rows([["name"], ["Alexander"], ["Jo"]])
    result = list(_truncate_rows(rows, {"name": 4}, ""))
    assert result[0]["name"] == "Alex"
    assert result[1]["name"] == "Jo"


def test_truncate_rows_with_suffix():
    rows = _make_rows([["name"], ["Alexander"]])
    result = list(_truncate_rows(rows, {"name": 4}, "..."))
    assert result[0]["name"] == "Alex..."


def test_truncate_rows_unknown_column_ignored():
    rows = _make_rows([["name"], ["Alice"]])
    result = list(_truncate_rows(rows, {"missing": 2}, ""))
    assert result[0]["name"] == "Alice"


def test_truncate_rows_zero_length():
    rows = _make_rows([["tag"], ["hello"]])
    result = list(_truncate_rows(rows, {"tag": 0}, ""))
    assert result[0]["tag"] == ""


# --- run (integration) ---

@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,city\nAlexander,Springfield\nJo,NY\n")
    return str(p)


class _Args(SimpleNamespace):
    def __init__(self, **kw):
        super().__init__(output=None, suffix="", **kw)


def test_run_stdout(csv_file, capsys):
    run(_Args(input=csv_file, specs=["name:4"]))
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert rows[0]["name"] == "Alex"
    assert rows[1]["name"] == "Jo"


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    run(_Args(input=csv_file, specs=["city:5"], output=out))
    with open(out) as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["city"] == "Sprin"


def test_run_with_suffix(csv_file, capsys):
    run(_Args(input=csv_file, specs=["name:3"], suffix="."))
    captured = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(captured)))
    assert rows[0]["name"] == "Ale."
