"""Tests for shift_cmd."""
import csv
import io
import sys
import pytest
from csv_surgeon.commands.shift_cmd import _parse_specs, _shift_row, run, _write


class _Args:
    def __init__(self, input, specs, output=None):
        self.input = input
        self.specs = specs
        self.output = output


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


@pytest.fixture
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,price,qty\nApple,10,3\nBanana,5,7\n")
    return str(p)


def test_parse_specs_single():
    specs = _parse_specs(["price:add:5"])
    assert specs == [("price", "add", 5.0)]


def test_parse_specs_multiple():
    specs = _parse_specs(["price:mul:2", "qty:sub:1"])
    assert specs == [("price", "mul", 2.0), ("qty", "sub", 1.0)]


def test_parse_specs_invalid_no_colon():
    with pytest.raises(ValueError, match="Invalid spec"):
        _parse_specs(["priceadd5"])


def test_parse_specs_bad_op():
    with pytest.raises(ValueError, match="Unknown op"):
        _parse_specs(["price:mod:3"])


def test_parse_specs_non_numeric_value():
    with pytest.raises(ValueError, match="Non-numeric"):
        _parse_specs(["price:add:abc"])


def test_shift_row_add():
    row = {"name": "Apple", "price": "10"}
    result = _shift_row(row, [("price", "add", 5.0)])
    assert result["price"] == "15"


def test_shift_row_mul():
    row = {"name": "Apple", "price": "10"}
    result = _shift_row(row, [("price", "mul", 1.5)])
    assert result["price"] == "15.0"


def test_shift_row_missing_col():
    row = {"name": "Apple"}
    result = _shift_row(row, [("price", "add", 5.0)])
    assert result == {"name": "Apple"}


def test_shift_row_non_numeric_cell():
    row = {"price": "N/A"}
    result = _shift_row(row, [("price", "add", 5.0)])
    assert result["price"] == "N/A"


def test_run_stdout(csv_file, capsys):
    run(_Args(csv_file, ["price:add:10"]))
    rows = _read_stdout(capsys)
    assert rows[0]["price"] == "20"
    assert rows[1]["price"] == "15"


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    run(_Args(csv_file, ["qty:mul:2"], output=out))
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["qty"] == "6"
    assert rows[1]["qty"] == "14"


def test_run_div(csv_file, capsys):
    run(_Args(csv_file, ["price:div:2"]))
    rows = _read_stdout(capsys)
    assert rows[0]["price"] == "5"
