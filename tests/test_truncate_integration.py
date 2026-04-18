"""Integration tests for the truncate CLI subcommand."""
from __future__ import annotations

import csv
import io
import sys
from unittest.mock import patch

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def people_csv(tmp_path):
    p = tmp_path / "people.csv"
    p.write_text("name,role\nAlexander Hamilton,Founding Father\nJo,Dev\n")
    return str(p)


def _run_main(args: list[str]) -> str:
    with patch("sys.argv", ["csv-surgeon"] + args):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            main()
            return mock_out.getvalue()


def _parse(output: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(output)))


def test_cli_truncate_basic(people_csv):
    out = _run_main(["truncate", people_csv, "--spec", "name:5"])
    rows = _parse(out)
    assert rows[0]["name"] == "Alexa"
    assert rows[1]["name"] == "Jo"


def test_cli_truncate_with_suffix(people_csv):
    out = _run_main(["truncate", people_csv, "--spec", "name:4", "--suffix", "..."])
    rows = _parse(out)
    assert rows[0]["name"] == "Alex..."


def test_cli_truncate_multiple_specs(people_csv):
    out = _run_main(["truncate", people_csv, "--spec", "name:3", "--spec", "role:7"])
    rows = _parse(out)
    assert rows[0]["name"] == "Ale"
    assert rows[0]["role"] == "Foundin"


def test_cli_truncate_output_file(people_csv, tmp_path):
    out_path = str(tmp_path / "out.csv")
    with patch("sys.argv", ["csv-surgeon", "truncate", people_csv, "--spec", "name:6", "-o", out_path]):
        main()
    with open(out_path) as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["name"] == "Alexan"
