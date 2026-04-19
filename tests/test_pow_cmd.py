"""Tests for pow_cmd."""
from __future__ import annotations

import csv
import io
import pytest

from csv_surgeon.commands.pow_cmd import _parse_specs, _pow_row, run


# --- _parse_specs ---

def test_parse_specs_single():
    assert _parse_specs(["score:2"]) == {"score": 2.0}


def test_parse_specs_multiple():
    assert _parse_specs(["a:3", "b:0.5"]) == {"a": 3.0, "b": 0.5}


def test_parse_specs_no_colon_raises():
    with pytest.raises(ValueError, match="Invalid spec"):
        _parse_specs(["score2"])


def test_parse_specs_bad_exponent_raises():
    with pytest.raises(ValueError, match="Invalid exponent"):
        _parse_specs(["score:abc"])


# --- _pow_row ---

def _row(**kw):
    return {k: str(v) for k, v in kw.items()}


def test_pow_row_square():
    row = _row(score="4", name="alice")
    result = _pow_row(row, {"score": 2.0})
    assert float(result["score"]) == pytest.approx(16.0)
    assert result["name"] == "alice"


def test_pow_row_sqrt():
    row = _row(val="9")
    result = _pow_row(row, {"val": 0.5})
    assert float(result["val"]) == pytest.approx(3.0)


def test_pow_row_missing_column_skipped():
    row = _row(a="2")
    result = _pow_row(row, {"b": 2.0})
    assert result == row


def test_pow_row_non_numeric_skipped():
    row = _row(score="hello")
    result = _pow_row(row, {"score": 2.0})
    assert result["score"] == "hello"


# --- run (integration via args) ---

class _Args:
    def __init__(self, specs, input_path, output_path):
        self.specs = specs
        self.input = input_path
        self.output = output_path


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


def test_run_stdout(tmp_path, capsys):
    f = tmp_path / "data.csv"
    f.write_text("name,score\nalice,3\nbob,4\n")
    run(_Args(["score:2"], str(f), "-"))
    rows = _read_stdout(capsys)
    assert float(rows[0]["score"]) == pytest.approx(9.0)
    assert float(rows[1]["score"]) == pytest.approx(16.0)


def test_run_output_file(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("x,y\n2,3\n4,5\n")
    out = tmp_path / "out.csv"
    run(_Args(["x:3", "y:2"], str(f), str(out)))
    rows = list(csv.DictReader(out.open()))
    assert float(rows[0]["x"]) == pytest.approx(8.0)
    assert float(rows[0]["y"]) == pytest.approx(9.0)
    assert float(rows[1]["x"]) == pytest.approx(64.0)
    assert float(rows[1]["y"]) == pytest.approx(25.0)
