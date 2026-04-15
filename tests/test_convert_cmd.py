"""Tests for convert_cmd."""
from __future__ import annotations

import csv
import io
import sys
import textwrap
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.convert_cmd import _parse_specs, _convert_value, run


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()	mp_path):
    p = tmp_path / "data.csv"
    p.write_text(
        textwrap.dedent("""\
            name,city,created_at
            alice,new york,2024-03-15T08:00:00
            BOB,LONDON,2023-11-01T12:30:00
            Charlie,Paris,2022-07-04T00:00:00
        """)
    )
    return str(p)


class _Args(SimpleNamespace):
    def __init__(self, file, specs, output=None):
        super().__init__(file=file, specs=specs, output=output)


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


# ---------------------------------------------------------------------------
# _parse_specs
# ---------------------------------------------------------------------------

def test_parse_specs_single():
    specs = _parse_specs(["name:upper"])
    assert specs == [{"col": "name", "transform": "upper", "fmt": None}]


def test_parse_specs_multiple():
    specs = _parse_specs(["name:lower", "city:title"])
    assert len(specs) == 2
    assert specs[0]["transform"] == "lower"
    assert specs[1]["transform"] == "title"


def test_parse_specs_date_with_fmt():
    specs = _parse_specs(["created_at:date:%d/%m/%Y"])
    assert specs[0]["fmt"] == "%d/%m/%Y"


def test_parse_specs_invalid_transform():
    with pytest.raises(ValueError, match="Unknown transform"):
        _parse_specs(["name:explode"])


def test_parse_specs_missing_transform():
    with pytest.raises(ValueError, match="Invalid spec"):
        _parse_specs(["nameonly"])


# ---------------------------------------------------------------------------
# _convert_value
# ---------------------------------------------------------------------------

def test_convert_upper():
    assert _convert_value("hello", {"transform": "upper", "fmt": None}) == "HELLO"


def test_convert_lower():
    assert _convert_value("HELLO", {"transform": "lower", "fmt": None}) == "hello"


def test_convert_title():
    assert _convert_value("new york", {"transform": "title", "fmt": None}) == "New York"


def test_convert_strip():
    assert _convert_value("  hi  ", {"transform": "strip", "fmt": None}) == "hi"


def test_convert_date_default_fmt():
    result = _convert_value("2024-03-15T08:00:00", {"transform": "date", "fmt": None})
    assert result == "2024-03-15"


def test_convert_date_custom_fmt():
    result = _convert_value("2024-03-15T08:00:00", {"transform": "date", "fmt": "%d/%m/%Y"})
    assert result == "15/03/2024"


def test_convert_date_unparseable_passthrough():
    result = _convert_value("not-a-date", {"transform": "date", "fmt": None})
    assert result == "not-a-date"


# ---------------------------------------------------------------------------
# run()
# ---------------------------------------------------------------------------

def test_run_upper(csv_file, capsys):
    run(_Args(csv_file, ["name:upper"]))
    rows = _read_stdout(capsys)
    assert rows[0]["name"] == "ALICE"
    assert rows[1]["name"] == "BOB"


def test_run_lower(csv_file, capsys):
    run(_Args(csv_file, ["city:lower"]))
    rows = _read_stdout(capsys)
    assert rows[1]["city"] == "london"


def test_run_date(csv_file, capsys):
    run(_Args(csv_file, ["created_at:date:%d/%m/%Y"]))
    rows = _read_stdout(capsys)
    assert rows[0]["created_at"] == "15/03/2024"


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    run(_Args(csv_file, ["name:title"], output=out))
    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["name"] == "Alice"


def test_run_unknown_column_ignored(csv_file, capsys):
    """Specs for missing columns should not raise."""
    run(_Args(csv_file, ["nonexistent:upper"]))
    rows = _read_stdout(capsys)
    assert len(rows) == 3
