"""Tests for csv_surgeon/commands/explode_cmd.py."""
from __future__ import annotations

import csv
import io
import textwrap
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from csv_surgeon.commands.explode_cmd import _explode_rows, run


def _make_rows(data: list[dict]) -> list[dict]:
    return data


@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text(
        textwrap.dedent(
            """\
            name,skills
            Alice,python|sql
            Bob,java
            Carol,
            """
        ),
        encoding="utf-8",
    )
    return str(p)


class _Args(SimpleNamespace):
    def __init__(self, input, column, sep="|", output=None):
        super().__init__(input=input, column=column, sep=sep, output=output)


def _read_stdout(capsys):
    out = capsys.readouterr().out
    return list(csv.DictReader(io.StringIO(out)))


# --- unit tests for _explode_rows ---

def test_explode_rows_multiple_values():
    rows = [{"name": "Alice", "skills": "python|sql"}]
    result = list(_explode_rows(rows, "skills", "|"))
    assert len(result) == 2
    assert result[0] == {"name": "Alice", "skills": "python"}
    assert result[1] == {"name": "Alice", "skills": "sql"}


def test_explode_rows_single_value():
    rows = [{"name": "Bob", "skills": "java"}]
    result = list(_explode_rows(rows, "skills", "|"))
    assert result == [{"name": "Bob", "skills": "java"}]


def test_explode_rows_empty_cell():
    rows = [{"name": "Carol", "skills": ""}]
    result = list(_explode_rows(rows, "skills", "|"))
    assert result == [{"name": "Carol", "skills": ""}]


def test_explode_rows_custom_sep():
    rows = [{"name": "Dave", "tags": "a,b,c"}]
    result = list(_explode_rows(rows, "tags", ","))
    assert [r["tags"] for r in result] == ["a", "b", "c"]


def test_explode_rows_preserves_other_columns():
    rows = [{"name": "Eve", "skills": "x|y", "age": "30"}]
    result = list(_explode_rows(rows, "skills", "|"))
    assert all(r["age"] == "30" and r["name"] == "Eve" for r in result)


# --- integration via run() ---

def test_run_stdout(csv_file, capsys):
    run(_Args(input=csv_file, column="skills"))
    rows = _read_stdout(capsys)
    names = [r["name"] for r in rows]
    assert names.count("Alice") == 2
    assert names.count("Bob") == 1


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    run(_Args(input=csv_file, column="skills", output=out))
    with open(out, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert any(r["skills"] == "python" for r in rows)
    assert any(r["skills"] == "sql" for r in rows)


def test_run_missing_column_exits(csv_file):
    with pytest.raises(SystemExit):
        run(_Args(input=csv_file, column="nonexistent"))
