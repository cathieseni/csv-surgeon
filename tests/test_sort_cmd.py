"""Tests for the sort subcommand."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.sort_cmd import run


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(
        "name,age,score\n"
        "Alice,30,88.5\n"
        "Bob,25,92.0\n"
        "Carol,35,75.0\n"
        "Dave,25,80.0\n"
    )
    return p


class _Args(SimpleNamespace):
    numeric: bool = False
    output: str | None = None
    inplace: bool = False


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


def test_sort_single_key_asc(csv_file, capsys):
    run(_Args(file=str(csv_file), keys=["name"]))
    rows = _read_stdout(capsys)
    assert [r["name"] for r in rows] == ["Alice", "Bob", "Carol", "Dave"]


def test_sort_single_key_desc(csv_file, capsys):
    run(_Args(file=str(csv_file), keys=["name:desc"]))
    rows = _read_stdout(capsys)
    assert [r["name"] for r in rows] == ["Dave", "Carol", "Bob", "Alice"]


def test_sort_numeric(csv_file, capsys):
    run(_Args(file=str(csv_file), keys=["score"], numeric=True))
    rows = _read_stdout(capsys)
    assert [r["score"] for r in rows] == ["75.0", "80.0", "88.5", "92.0"]


def test_sort_numeric_desc(csv_file, capsys):
    run(_Args(file=str(csv_file), keys=["age:desc"], numeric=True))
    rows = _read_stdout(capsys)
    assert rows[0]["name"] == "Carol"


def test_sort_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    run(_Args(file=str(csv_file), keys=["name"], output=str(out)))
    rows = list(csv.DictReader(out.open()))
    assert [r["name"] for r in rows] == ["Alice", "Bob", "Carol", "Dave"]


def test_sort_inplace(csv_file):
    run(_Args(file=str(csv_file), keys=["age"], numeric=True, inplace=True))
    rows = list(csv.DictReader(csv_file.open()))
    ages = [int(r["age"]) for r in rows]
    assert ages == sorted(ages)


def test_sort_unknown_column_exits(csv_file):
    with pytest.raises(SystemExit):
        run(_Args(file=str(csv_file), keys=["nonexistent"]))


def test_sort_missing_file_exits(tmp_path):
    with pytest.raises(SystemExit):
        run(_Args(file=str(tmp_path / "missing.csv"), keys=["name"]))
