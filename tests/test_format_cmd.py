"""Tests for format_cmd."""
from __future__ import annotations

import csv
import io
import sys
from argparse import Namespace
from pathlib import Path

import pytest

from csv_surgeon.commands.format_cmd import _parse_specs, _format_value, run


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text("name,age,city\nAlice,30,NY\nBob,5,LA\n")
    return p


class _Args(Namespace):
    def __init__(self, **kw):
        defaults = {"output": None}
        defaults.update(kw)
        super().__init__(**defaults)


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


# --- _parse_specs ---

def test_parse_specs_single():
    specs = _parse_specs(["name:10"])
    assert specs == {"name": (10, "l")}


def test_parse_specs_align_right():
    specs = _parse_specs(["age:5:r"])
    assert specs == {"age": (5, "r")}


def test_parse_specs_align_center():
    specs = _parse_specs(["city:8:c"])
    assert specs == {"city": (8, "c")}


def test_parse_specs_invalid_no_width():
    with pytest.raises(ValueError, match="Invalid format spec"):
        _parse_specs(["name"])


def test_parse_specs_invalid_align():
    with pytest.raises(ValueError, match="Align must be"):
        _parse_specs(["name:10:x"])


# --- _format_value ---

def test_format_left():
    assert _format_value("hi", 6, "l") == "hi    "


def test_format_right():
    assert _format_value("hi", 6, "r") == "    hi"


def test_format_center():
    assert _format_value("hi", 6, "c") == "  hi  "


# --- run ---

def test_run_stdout(csv_file, capsys):
    args = _Args(input=str(csv_file), specs=["name:10"])
    run(args)
    rows = _read_stdout(capsys)
    assert rows[0]["name"] == "Alice     "
    assert rows[1]["name"] == "Bob       "


def test_run_right_align(csv_file, capsys):
    args = _Args(input=str(csv_file), specs=["age:5:r"])
    run(args)
    rows = _read_stdout(capsys)
    assert rows[0]["age"] == "   30"
    assert rows[1]["age"] == "    5"


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    args = _Args(input=str(csv_file), specs=["name:8"], output=str(out))
    run(args)
    rows = list(csv.DictReader(out.open()))
    assert rows[0]["name"] == "Alice   "


def test_run_unknown_column_ignored(csv_file, capsys):
    args = _Args(input=str(csv_file), specs=["nonexistent:10"])
    run(args)  # should not raise
    rows = _read_stdout(capsys)
    assert len(rows) == 2
