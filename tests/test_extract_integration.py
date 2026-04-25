"""Integration tests for the extract command via the CLI entry point."""
from __future__ import annotations

import csv
import io
from pathlib import Path

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def people_csv(tmp_path: Path) -> Path:
    p = tmp_path / "people.csv"
    p.write_text(
        "name,age,city,salary\n"
        "Alice,30,NYC,90000\n"
        "Bob,25,LA,75000\n"
        "Carol,35,Chicago,110000\n"
    )
    return p


def _run_main(args, capsys):
    main(args)
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


def test_cli_extract_basic(people_csv, capsys):
    rows = _run_main(["extract", str(people_csv), "-c", "name,age"], capsys)
    assert len(rows) == 3


def test_cli_extract_columns_correct(people_csv, capsys):
    rows = _run_main(["extract", str(people_csv), "-c", "name,city"], capsys)
    assert list(rows[0].keys()) == ["name", "city"]
    assert rows[0]["name"] == "Alice"
    assert rows[0]["city"] == "NYC"


def test_cli_extract_single_column(people_csv, capsys):
    rows = _run_main(["extract", str(people_csv), "-c", "salary"], capsys)
    assert all(list(r.keys()) == ["salary"] for r in rows)
    assert rows[1]["salary"] == "75000"


def test_cli_extract_output_file(people_csv, tmp_path, capsys):
    out = tmp_path / "result.csv"
    main(["extract", str(people_csv), "-c", "name,salary", "-o", str(out)])
    rows = list(csv.DictReader(out.open()))
    assert len(rows) == 3
    assert "age" not in rows[0]
    assert "city" not in rows[0]


def test_cli_extract_preserves_order(people_csv, capsys):
    rows = _run_main(["extract", str(people_csv), "-c", "salary,name"], capsys)
    assert list(rows[0].keys()) == ["salary", "name"]
