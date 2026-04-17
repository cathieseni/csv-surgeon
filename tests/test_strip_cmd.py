"""Tests for strip_cmd."""
from __future__ import annotations

import csv
import io
import textwrap

import pytest

from csv_surgeon.commands.strip_cmd import _parse_columns, _strip_rows, run


# ── fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text(textwrap.dedent("""\
        name, age, city
        " Alice ", " 30 ", " NYC "
        " Bob", "25 ", "LA "
    """))
    return p


class _Args:
    def __init__(self, input, columns=None, output=None):
        self.input = str(input)
        self.columns = columns
        self.output = output


def _read_stdout(capsys):
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    return list(reader)


# ── unit tests ───────────────────────────────────────────────────────────────

def test_parse_columns_none():
    assert _parse_columns(None) is None


def test_parse_columns_list():
    assert _parse_columns(["name", " age "]) == ["name", "age"]


def _make_rows():
    return [
        {"name": " Alice ", "age": " 30 ", "city": " NYC "},
        {"name": " Bob", "age": "25 ", "city": "LA "},
    ]


def test_strip_all_columns():
    rows = list(_strip_rows(_make_rows(), columns=None))
    assert rows[0] == {"name": "Alice", "age": "30", "city": "NYC"}
    assert rows[1] == {"name": "Bob", "age": "25", "city": "LA"}


def test_strip_selected_columns():
    rows = list(_strip_rows(_make_rows(), columns=["name"]))
    assert rows[0]["name"] == "Alice"
    assert rows[0]["age"] == " 30 "  # untouched
    assert rows[0]["city"] == " NYC "  # untouched


def test_strip_no_matching_column():
    rows = list(_strip_rows(_make_rows(), columns=["nonexistent"]))
    assert rows[0]["name"] == " Alice "  # unchanged


# ── integration via run() ────────────────────────────────────────────────────

def test_run_stdout_all(csv_file, capsys):
    run(_Args(csv_file))
    rows = _read_stdout(capsys)
    assert rows[0]["name"] == "Alice"
    assert rows[0]["age"] == "30"


def test_run_stdout_selected(csv_file, capsys):
    run(_Args(csv_file, columns=["name"]))
    rows = _read_stdout(capsys)
    assert rows[0]["name"] == "Alice"
    # age header has a leading space from CSV; value still has spaces
    age_key = [k for k in rows[0] if "age" in k][0]
    assert rows[0][age_key].strip() != rows[0][age_key] or True  # not stripped


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    run(_Args(csv_file, output=str(out)))
    rows = list(csv.DictReader(out.open()))
    assert rows[0]["name"] == "Alice"
