"""Integration tests for the diff subcommand via CLI."""
from __future__ import annotations

import csv
import io
from pathlib import Path

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def base_csv(tmp_path: Path) -> Path:
    p = tmp_path / "base.csv"
    p.write_text("dept,employee\nEng,Alice\nEng,Bob\nHR,Carol\n")
    return p


@pytest.fixture()
def new_csv(tmp_path: Path) -> Path:
    p = tmp_path / "new.csv"
    p.write_text("dept,employee\nEng,Alice\nHR,Carol\nHR,Dave\n")
    return p


def _run_main(args: list[str], capsys) -> list[dict]:
    main(args)
    out = capsys.readouterr().out
    return list(csv.DictReader(io.StringIO(out)))


def test_cli_diff_basic(base_csv, new_csv, capsys):
    rows = _run_main(["diff", str(base_csv), str(new_csv)], capsys)
    assert len(rows) == 2


def test_cli_diff_removed_correct(base_csv, new_csv, capsys):
    rows = _run_main(["diff", str(base_csv), str(new_csv)], capsys)
    removed = [r for r in rows if r["_diff"] == "removed"]
    assert removed[0]["employee"] == "Bob"


def test_cli_diff_added_correct(base_csv, new_csv, capsys):
    rows = _run_main(["diff", str(base_csv), str(new_csv)], capsys)
    added = [r for r in rows if r["_diff"] == "added"]
    assert added[0]["employee"] == "Dave"


def test_cli_diff_with_key(base_csv, new_csv, capsys):
    rows = _run_main(
        ["diff", str(base_csv), str(new_csv), "--keys", "employee"], capsys
    )
    names = {r["employee"] for r in rows}
    assert "Bob" in names
    assert "Dave" in names
