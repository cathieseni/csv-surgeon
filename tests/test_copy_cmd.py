"""Tests for copy_cmd."""
from __future__ import annotations

import argparse
import csv
import io
import sys
import textwrap
from pathlib import Path

import pytest

from csv_surgeon.commands.copy_cmd import _copy_rows, _parse_specs, run


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _Args:
    def __init__(self, specs, input, output=None):
        self.specs = specs
        self.input = input
        self.output = output


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(textwrap.dedent("""\
        name,score,grade
        Alice,90,A
        Bob,75,B
        Carol,88,A
    """))
    return p


# ---------------------------------------------------------------------------
# _parse_specs
# ---------------------------------------------------------------------------

def test_parse_specs_single():
    assert _parse_specs(["score:score_bak"]) == [("score", "score_bak")]


def test_parse_specs_multiple():
    result = _parse_specs(["score:score_bak", "grade:grade_copy"])
    assert result == [("score", "score_bak"), ("grade", "grade_copy")]


def test_parse_specs_no_colon_raises():
    with pytest.raises(argparse.ArgumentTypeError, match="expected 'SRC:DST'"):
        _parse_specs(["nodash"])


def test_parse_specs_empty_src_raises():
    with pytest.raises(argparse.ArgumentTypeError, match="non-empty"):
        _parse_specs([":dst"])


def test_parse_specs_empty_dst_raises():
    with pytest.raises(argparse.ArgumentTypeError, match="non-empty"):
        _parse_specs(["src:"])


# ---------------------------------------------------------------------------
# _copy_rows
# ---------------------------------------------------------------------------

def _make_rows():
    return [
        {"name": "Alice", "score": "90"},
        {"name": "Bob", "score": "75"},
    ]


def test_copy_rows_adds_column():
    rows = list(_copy_rows(_make_rows(), ["name", "score"], [("score", "score_bak")]))
    assert all("score_bak" in r for r in rows)
    assert rows[0]["score_bak"] == "90"
    assert rows[1]["score_bak"] == "75"


def test_copy_rows_preserves_original():
    rows = list(_copy_rows(_make_rows(), ["name", "score"], [("score", "score_bak")]))
    assert rows[0]["score"] == "90"


def test_copy_rows_missing_src_yields_empty():
    rows = list(_copy_rows(_make_rows(), ["name", "score"], [("missing", "dst")]))
    assert rows[0]["dst"] == ""


# ---------------------------------------------------------------------------
# run (integration)
# ---------------------------------------------------------------------------

def test_run_stdout(csv_file, capsys):
    args = _Args(specs=["score:score_bak"], input=str(csv_file))
    run(args)
    rows = _read_stdout(capsys)
    assert "score_bak" in rows[0]
    assert rows[0]["score_bak"] == rows[0]["score"]


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    args = _Args(specs=["score:score_bak"], input=str(csv_file), output=str(out))
    run(args)
    rows = list(csv.DictReader(out.open()))
    assert rows[0]["score_bak"] == "90"


def test_run_multiple_specs(csv_file, capsys):
    args = _Args(specs=["score:s2", "grade:g2"], input=str(csv_file))
    run(args)
    rows = _read_stdout(capsys)
    assert rows[0]["s2"] == "90"
    assert rows[0]["g2"] == "A"


def test_run_missing_column_exits(csv_file):
    args = _Args(specs=["nonexistent:copy"], input=str(csv_file))
    with pytest.raises(SystemExit):
        run(args)
