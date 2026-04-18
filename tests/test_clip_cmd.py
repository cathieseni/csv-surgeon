"""Tests for clip_cmd."""
from __future__ import annotations

import csv
import io
import sys
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.clip_cmd import _clip_row, _parse_specs, run


# ---------------------------------------------------------------------------
# _parse_specs
# ---------------------------------------------------------------------------

def test_parse_specs_single():
    specs = _parse_specs(["score:0:100"])
    assert specs == [("score", 0.0, 100.0)]


def test_parse_specs_no_lower():
    specs = _parse_specs(["price::500"])
    assert specs == [("price", None, 500.0)]


def test_parse_specs_no_upper():
    specs = _parse_specs(["age:18:"])
    assert specs == [("age", 18.0, None)]


def test_parse_specs_invalid_raises():
    with pytest.raises(ValueError, match="Invalid spec"):
        _parse_specs(["badspec"])


# ---------------------------------------------------------------------------
# _clip_row
# ---------------------------------------------------------------------------

def _row(**kw):
    return {k: str(v) for k, v in kw.items()}


def test_clip_row_clamps_above():
    specs = [("score", 0.0, 100.0)]
    result = _clip_row(_row(score=150), specs)
    assert result["score"] == "100"


def test_clip_row_clamps_below():
    specs = [("score", 0.0, 100.0)]
    result = _clip_row(_row(score=-5), specs)
    assert result["score"] == "0"


def test_clip_row_within_bounds():
    specs = [("score", 0.0, 100.0)]
    result = _clip_row(_row(score=75), specs)
    assert result["score"] == "75"


def test_clip_row_non_numeric_unchanged():
    specs = [("score", 0.0, 100.0)]
    result = _clip_row({"score": "n/a"}, specs)
    assert result["score"] == "n/a"


def test_clip_row_missing_column_ignored():
    specs = [("missing", 0.0, 10.0)]
    row = {"other": "5"}
    result = _clip_row(row, specs)
    assert result == {"other": "5"}


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------

@pytest.fixture
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,score\nAlice,120\nBob,45\nCarol,-10\n")
    return str(p)


class _Args(SimpleNamespace):
    def __init__(self, **kw):
        super().__init__(input=None, specs=None, output=None, **kw)


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


def test_run_stdout(csv_file, capsys):
    args = _Args(input=csv_file, specs=["score:0:100"])
    run(args)
    rows = _read_stdout(capsys)
    assert rows[0]["score"] == "100"
    assert rows[1]["score"] == "45"
    assert rows[2]["score"] == "0"


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _Args(input=csv_file, specs=["score:0:100"], output=out)
    run(args)
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["score"] == "100"
    assert rows[2]["score"] == "0"
