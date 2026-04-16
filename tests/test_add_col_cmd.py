"""Tests for add-col command."""
from __future__ import annotations

import csv
import io
import sys
import textwrap
from pathlib import Path

import pytest

from csv_surgeon.commands.add_col_cmd import _parse_specs, _add_columns, run


@pytest.fixture
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text(textwrap.dedent("""\
        name,age
        Alice,30
        Bob,25
    """))
    return p


class _Args:
    def __init__(self, input, specs, output=None):
        self.input = str(input)
        self.specs = specs
        self.output = output


def _read_stdout(capsys):
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    return list(reader)


def test_parse_specs_single():
    assert _parse_specs(["status=active"]) == [("status", "active")]


def test_parse_specs_multiple():
    result = _parse_specs(["status=active", "label=user"])
    assert result == [("status", "active"), ("label", "user")]


def test_parse_specs_invalid():
    with pytest.raises(ValueError, match="Invalid spec"):
        _parse_specs(["badspec"])


def test_add_columns_constant():
    rows = [{"name": "Alice", "age": "30"}]
    result = _add_columns(rows, [("status", "active")])
    assert result[0]["status"] == "active"


def test_add_columns_template():
    rows = [{"name": "Alice", "age": "30"}]
    result = _add_columns(rows, [("label", "{name}-{age}")])
    assert result[0]["label"] == "Alice-30"


def test_add_columns_missing_placeholder():
    rows = [{"name": "Alice"}]
    result = _add_columns(rows, [("label", "{missing}")])
    assert result[0]["label"] == "{missing}"


def test_run_stdout(csv_file, capsys):
    run(_Args(csv_file, ["status=active"]))
    rows = _read_stdout(capsys)
    assert all(r["status"] == "active" for r in rows)
    assert rows[0]["name"] == "Alice"


def test_run_template(csv_file, capsys):
    run(_Args(csv_file, ["label={name}({age})"]))
    rows = _read_stdout(capsys)
    assert rows[0]["label"] == "Alice(30)"
    assert rows[1]["label"] == "Bob(25)"


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    run(_Args(csv_file, ["status=new"], output=str(out)))
    rows = list(csv.DictReader(out.open()))
    assert rows[0]["status"] == "new"


def test_run_preserves_existing_columns(csv_file, capsys):
    run(_Args(csv_file, ["x=1"]))
    rows = _read_stdout(capsys)
    assert "name" in rows[0] and "age" in rows[0]
