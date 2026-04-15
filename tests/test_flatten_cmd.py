"""Unit tests for flatten_cmd."""
from __future__ import annotations

import csv
import io
import sys
import textwrap
from argparse import Namespace
from pathlib import Path

import pytest

from csv_surgeon.commands.flatten_cmd import _flatten_rows, run


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(
        textwrap.dedent("""\
        id,name,tags
        1,Alice,python|data
        2,Bob,devops
        3,Carol,python|ml|data
        """),
        encoding="utf-8",
    )
    return p


class _Args(Namespace):
    def __init__(self, **kw):
        defaults = dict(input="", column="tags", sep="|", output=None)
        defaults.update(kw)
        super().__init__(**defaults)


def _read_stdout(capsys) -> list[dict]:
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


def test_flatten_rows_single_value():
    rows = [{"id": "1", "tags": "python"}]
    result = list(_flatten_rows(rows, "tags", "|"))
    assert result == [{"id": "1", "tags": "python"}]


def test_flatten_rows_multiple_values():
    rows = [{"id": "1", "tags": "python|data|ml"}]
    result = list(_flatten_rows(rows, "tags", "|"))
    assert len(result) == 3
    assert [r["tags"] for r in result] == ["python", "data", "ml"]
    assert all(r["id"] == "1" for r in result)


def test_flatten_rows_empty_cell():
    rows = [{"id": "2", "tags": ""}]
    result = list(_flatten_rows(rows, "tags", "|"))
    assert result == [{"id": "2", "tags": ""}]


def test_flatten_rows_custom_sep():
    rows = [{"id": "1", "tags": "a,b,c"}]
    result = list(_flatten_rows(rows, "tags", ","))
    assert [r["tags"] for r in result] == ["a", "b", "c"]


def test_run_stdout(csv_file, capsys):
    args = _Args(input=str(csv_file))
    run(args)
    rows = _read_stdout(capsys)
    tags = [r["tags"] for r in rows]
    assert tags.count("python") == 2
    assert "ml" in tags
    assert len(rows) == 5  # 2+1+3 = 6 parts but Bob has 1 → 2+1+3=6 total


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    args = _Args(input=str(csv_file), output=str(out))
    run(args)
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert len(rows) == 6


def test_run_missing_column_exits(csv_file):
    args = _Args(input=str(csv_file), column="nonexistent")
    with pytest.raises(SystemExit):
        run(args)
