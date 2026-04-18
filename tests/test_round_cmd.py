"""Tests for round_cmd."""
from __future__ import annotations

import csv
import io
import sys
import textwrap

import pytest

from csv_surgeon.commands.round_cmd import _parse_specs, _round_row, run


# --- _parse_specs ---

def test_parse_specs_single():
    assert _parse_specs(["price:2"]) == {"price": 2}


def test_parse_specs_multiple():
    assert _parse_specs(["price:2", "score:0"]) == {"price": 2, "score": 0}


def test_parse_specs_zero_places():
    assert _parse_specs(["val:0"]) == {"val": 0}


def test_parse_specs_no_colon_raises():
    with pytest.raises(ValueError, match="expected COL:N"):
        _parse_specs(["price2"])


def test_parse_specs_negative_raises():
    with pytest.raises(ValueError, match=">= 0"):
        _parse_specs(["price:-1"])


def test_parse_specs_bad_n_raises():
    with pytest.raises(ValueError, match="Invalid decimal places"):
        _parse_specs(["price:abc"])


# --- _round_row ---

def _row(**kw):
    return kw


def test_round_row_basic():
    row = _row(price="3.14159", name="alice")
    result = _round_row(row, {"price": 2})
    assert result["price"] == "3.14"
    assert result["name"] == "alice"


def test_round_row_zero_places():
    row = _row(score="4.7")
    result = _round_row(row, {"score": 0})
    assert result["score"] == "5"


def test_round_row_non_numeric_unchanged():
    row = _row(price="n/a")
    result = _round_row(row, {"price": 2})
    assert result["price"] == "n/a"


def test_round_row_empty_unchanged():
    row = _row(price="")
    result = _round_row(row, {"price": 2})
    assert result["price"] == ""


def test_round_row_missing_col_unchanged():
    row = _row(name="bob")
    result = _round_row(row, {"price": 2})
    assert "price" not in result


# --- run (integration) ---

class _Args:
    def __init__(self, input, specs, output=None):
        self.input = input
        self.specs = specs
        self.output = output


def test_run_stdout(tmp_path, capsys):
    f = tmp_path / "data.csv"
    f.write_text("name,price\nalice,1.23456\nbob,9.9")
    run(_Args(str(f), ["price:2"]))
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert rows[0]["price"] == "1.23"
    assert rows[1]["price"] == "9.9"


def test_run_output_file(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("val\n3.14159\n2.71828")
    out = tmp_path / "out.csv"
    run(_Args(str(f), ["val:3"], str(out)))
    rows = list(csv.DictReader(out.open()))
    assert rows[0]["val"] == "3.142"
    assert rows[1]["val"] == "2.718"
