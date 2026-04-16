"""Integration tests for the reorder subcommand via CLI entry point."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def people_csv(tmp_path: Path) -> Path:
    p = tmp_path / "people.csv"
    p.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\n")
    return p


def _run_main(argv: list[str], capsys) -> list[dict]:
    sys.argv = ["csv-surgeon"] + argv
    main()
    captured = capsys.readouterr().out
    return list(csv.DictReader(io.StringIO(captured)))


def test_cli_reorder_basic(people_csv, capsys):
    rows = _run_main(["reorder", str(people_csv), "--columns", "city,name,age"], capsys)
    assert list(rows[0].keys()) == ["city", "name", "age"]


def test_cli_reorder_values_correct(people_csv, capsys):
    rows = _run_main(["reorder", str(people_csv), "--columns", "age,name"], capsys)
    assert rows[0]["age"] == "30"
    assert rows[0]["name"] == "Alice"
    # 'city' appended at end
    assert rows[0]["city"] == "NYC"


def test_cli_reorder_partial_columns(people_csv, capsys):
    rows = _run_main(["reorder", str(people_csv), "--columns", "city"], capsys)
    keys = list(rows[0].keys())
    assert keys[0] == "city"
    assert set(keys) == {"name", "age", "city"}


def test_cli_reorder_missing_column_exits(people_csv, capsys):
    sys.argv = ["csv-surgeon", "reorder", str(people_csv), "--columns", "ghost"]
    with pytest.raises((SystemExit, ValueError)):
        main()
