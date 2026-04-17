"""Tests for replace_cmd."""
from __future__ import annotations

import csv
import io
import textwrap
from argparse import Namespace
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.replace_cmd import _parse_specs, _replace_row, run


# ---------------------------------------------------------------------------
# _parse_specs
# ---------------------------------------------------------------------------

def test_parse_specs_single():
    assert _parse_specs(["name:Alice:Bob"]) == [("name", "Alice", "Bob")]


def test_parse_specs_multiple():
    specs = _parse_specs(["city:NY:New York", "code:001:1"])
    assert specs == [("city", "NY", "New York"), ("code", "001", "1")]


def test_parse_specs_invalid_raises():
    with pytest.raises(ValueError, match="Invalid spec"):
        _parse_specs(["badspec"])


# ---------------------------------------------------------------------------
# _replace_row
# ---------------------------------------------------------------------------

def test_replace_row_literal():
    row = {"name": "Alice", "city": "NY"}
    result = _replace_row(row, [("city", "NY", "New York")], use_regex=False)
    assert result["city"] == "New York"
    assert result["name"] == "Alice"


def test_replace_row_regex():
    row = {"val": "foo123bar"}
    result = _replace_row(row, [("val", r"\d+", "NUM")], use_regex=True)
    assert result["val"] == "fooNUMbar"


def test_replace_row_missing_column_ignored():
    row = {"a": "hello"}
    result = _replace_row(row, [("b", "x", "y")], use_regex=False)
    assert result == {"a": "hello"}


# ---------------------------------------------------------------------------
# run (integration via tmp file)
# ---------------------------------------------------------------------------

@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text(textwrap.dedent("""\
        name,city
        Alice,NY
        Bob,LA
        Carol,NY
    """))
    return p


class _Args(Namespace):
    def __init__(self, **kw):
        defaults = dict(specs=["city:NY:New York"], regex=False, output=None)
        defaults.update(kw)
        super().__init__(**defaults)


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


def test_run_literal_replace(csv_file, capsys):
    run(_Args(input=str(csv_file)))
    rows = _read_stdout(capsys)
    cities = [r["city"] for r in rows]
    assert cities == ["New York", "LA", "New York"]


def test_run_regex_replace(csv_file, capsys):
    run(_Args(input=str(csv_file), specs=["name:[aeiou]:*"], regex=True))
    rows = _read_stdout(capsys)
    assert rows[0]["name"] == "*l*c*"


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    run(_Args(input=str(csv_file), output=str(out)))
    rows = list(csv.DictReader(out.open()))
    assert rows[0]["city"] == "New York"
