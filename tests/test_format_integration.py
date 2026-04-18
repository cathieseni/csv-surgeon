"""Integration tests for the format command via cli.main."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def people_csv(tmp_path: Path) -> Path:
    p = tmp_path / "people.csv"
    p.write_text("name,score,city\nAlice,9,New York\nBob,100,LA\nCarol,42,Chicago\n")
    return p


def _run_main(args):
    with patch("sys.argv", ["csv-surgeon"] + args):
        main()


def _parse(capsys):
    out = capsys.readouterr().out
    return list(csv.DictReader(io.StringIO(out)))


def test_cli_format_left(people_csv, capsys):
    _run_main(["format", str(people_csv), "-s", "name:8"])
    rows = _parse(capsys)
    assert rows[0]["name"] == "Alice   "
    assert rows[1]["name"] == "Bob     "


def test_cli_format_right(people_csv, capsys):
    _run_main(["format", str(people_csv), "-s", "score:5:r"])
    rows = _parse(capsys)
    assert rows[0]["score"] == "    9"
    assert rows[1]["score"] == "  100"


def test_cli_format_center(people_csv, capsys):
    _run_main(["format", str(people_csv), "-s", "city:10:c"])
    rows = _parse(capsys)
    assert rows[0]["city"] == " New York "


def test_cli_format_multiple_specs(people_csv, capsys):
    _run_main(["format", str(people_csv), "-s", "name:8", "-s", "score:5:r"])
    rows = _parse(capsys)
    assert rows[2]["name"] == "Carol   "
    assert rows[2]["score"] == "   42"


def test_cli_format_output_file(people_csv, tmp_path):
    out = tmp_path / "out.csv"
    _run_main(["format", str(people_csv), "-s", "name:10", "-o", str(out)])
    rows = list(csv.DictReader(out.open()))
    assert rows[0]["name"] == "Alice     "
