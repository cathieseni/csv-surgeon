"""Tests for csv_surgeon/commands/clamp_cmd.py."""
from __future__ import annotations

import csv
import io
import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.clamp_cmd import (
    _clamp_row,
    _parse_specs,
    run,
)


# ---------------------------------------------------------------------------
# _parse_specs
# ---------------------------------------------------------------------------

def test_parse_specs_single():
    specs = _parse_specs(["price:0:100"])
    assert specs == {"price": (0.0, 100.0)}


def test_parse_specs_no_lower():
    specs = _parse_specs(["score::50"])
    assert specs["score"] == (None, 50.0)


def test_parse_specs_no_upper():
    specs = _parse_specs(["age:18:"])
    assert specs["age"] == (18.0, None)


def test_parse_specs_multiple():
    specs = _parse_specs(["a:1:9", "b:0:1"])
    assert specs["a"] == (1.0, 9.0)
    assert specs["b"] == (0.0, 1.0)


def test_parse_specs_invalid_no_colon_raises():
    with pytest.raises(ValueError, match="expected COL:MIN:MAX"):
        _parse_specs(["price"])


def test_parse_specs_min_gt_max_raises():
    with pytest.raises(ValueError, match="min"):
        _parse_specs(["x:10:5"])


def test_parse_specs_empty_col_raises():
    with pytest.raises(ValueError, match="column name"):
        _parse_specs([":0:10"])


# ---------------------------------------------------------------------------
# _clamp_row
# ---------------------------------------------------------------------------

def _row(**kw):
    return {k: str(v) for k, v in kw.items()}


def test_clamp_row_within_bounds():
    specs = {"x": (0.0, 10.0)}
    assert _clamp_row(_row(x=5), specs)["x"] == "5"


def test_clamp_row_below_lower():
    specs = {"x": (0.0, 10.0)}
    assert _clamp_row(_row(x=-3), specs)["x"] == "0"


def test_clamp_row_above_upper():
    specs = {"x": (0.0, 10.0)}
    assert _clamp_row(_row(x=99), specs)["x"] == "10"


def test_clamp_row_no_lower():
    specs = {"x": (None, 5.0)}
    assert _clamp_row(_row(x=-100), specs)["x"] == "-100"


def test_clamp_row_no_upper():
    specs = {"x": (5.0, None)}
    assert _clamp_row(_row(x=999), specs)["x"] == "999"


def test_clamp_row_non_numeric_unchanged():
    specs = {"x": (0.0, 10.0)}
    assert _clamp_row({"x": "N/A"}, specs)["x"] == "N/A"


def test_clamp_row_missing_column_ignored():
    specs = {"z": (0.0, 1.0)}
    row = {"x": "5"}
    assert _clamp_row(row, specs) == {"x": "5"}


# ---------------------------------------------------------------------------
# run (integration via temp file)
# ---------------------------------------------------------------------------

@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(
        textwrap.dedent("""\
        name,score
        Alice,120
        Bob,-5
        Carol,75
        """)
    )
    return p


class _Args(SimpleNamespace):
    def __init__(self, **kw):
        super().__init__(**kw)


def _read_stdout(capsys) -> list[dict]:
    captured = capsys.readouterr().out
    return list(csv.DictReader(io.StringIO(captured)))


def test_run_stdout(csv_file, capsys):
    args = _Args(specs=["score:0:100"], input=str(csv_file), output=None)
    run(args)
    rows = _read_stdout(capsys)
    assert rows[0]["score"] == "100"   # 120 clamped to 100
    assert rows[1]["score"] == "0"     # -5 clamped to 0
    assert rows[2]["score"] == "75"    # unchanged


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    args = _Args(specs=["score:0:100"], input=str(csv_file), output=str(out))
    run(args)
    rows = list(csv.DictReader(out.open()))
    assert rows[0]["score"] == "100"
    assert rows[1]["score"] == "0"


def test_run_preserves_other_columns(csv_file, capsys):
    args = _Args(specs=["score:0:100"], input=str(csv_file), output=None)
    run(args)
    rows = _read_stdout(capsys)
    assert all(r["name"] in {"Alice", "Bob", "Carol"} for r in rows)
