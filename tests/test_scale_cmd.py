"""Tests for scale_cmd."""
from __future__ import annotations

import csv
import io
import pytest

from csv_surgeon.commands.scale_cmd import _parse_specs, _scale_row, run


# --- unit tests ---

def test_parse_specs_single():
    assert _parse_specs(["price:2"]) == [("price", 2.0)]


def test_parse_specs_multiple():
    assert _parse_specs(["a:3", "b:0.5"]) == [("a", 3.0), ("b", 0.5)]


def test_parse_specs_no_colon_raises():
    with pytest.raises(ValueError, match="Invalid spec"):
        _parse_specs(["price2"])


def test_parse_specs_bad_factor_raises():
    with pytest.raises(ValueError, match="Invalid factor"):
        _parse_specs(["price:abc"])


def test_scale_row_basic():
    row = {"name": "apple", "price": "2.0", "qty": "3"}
    result = _scale_row(row, [("price", 1.5), ("qty", 2.0)])
    assert result["price"] == "3.0"
    assert result["qty"] == "6.0"
    assert result["name"] == "apple"


def test_scale_row_non_numeric_unchanged():
    row = {"col": "n/a"}
    result = _scale_row(row, [("col", 10.0)])
    assert result["col"] == "n/a"


def test_scale_row_missing_column_ignored():
    row = {"a": "1"}
    result = _scale_row(row, [("b", 2.0)])
    assert result == {"a": "1"}


# --- integration via run() ---

class _Args:
    def __init__(self, specs, input_path, output_path="-"):
        self.specs = specs
        self.input = input_path
        self.output = output_path


@pytest.fixture
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("item,price,qty\napple,2.00,5\nbanana,1.50,10\n")
    return str(p)


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


def test_run_scales_column(csv_file, capsys):
    run(_Args(["price:2"], csv_file))
    rows = _read_stdout(capsys)
    assert rows[0]["price"] == "4.0"
    assert rows[1]["price"] == "3.0"


def test_run_multiple_columns(csv_file, capsys):
    run(_Args(["price:10", "qty:0.5"], csv_file))
    rows = _read_stdout(capsys)
    assert rows[0]["price"] == "20.0"
    assert rows[0]["qty"] == "2.5"


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    run(_Args(["qty:3"], csv_file, out))
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["qty"] == "15.0"
    assert rows[1]["qty"] == "30.0"
