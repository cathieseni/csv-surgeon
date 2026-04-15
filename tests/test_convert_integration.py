"""Integration tests for the convert subcommand via cli.main."""
from __future__ import annotations

import csv
import io
import sys
import textwrap

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def people_csv(tmp_path):
    p = tmp_path / "people.csv"
    p.write_text(
        textwrap.dedent("""\
            name,city,joined
            alice,new york,2023-06-01T00:00:00
            BOB,LONDON,2022-01-15T00:00:00
            Charlie,paris,2021-09-30T00:00:00
        """)
    )
    return str(p)


def _run_main(argv, capsys):
    sys.argv = ["csv-surgeon"] + argv
    main()
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


def test_cli_convert_upper(people_csv, capsys):
    rows = _run_main(["convert", people_csv, "name:upper"], capsys)
    assert rows[0]["name"] == "ALICE"
    assert rows[1]["name"] == "BOB"
    assert rows[2]["name"] == "CHARLIE"


def test_cli_convert_lower(people_csv, capsys):
    rows = _run_main(["convert", people_csv, "city:lower"], capsys)
    assert rows[1]["city"] == "london"


def test_cli_convert_title(people_csv, capsys):
    rows = _run_main(["convert", people_csv, "city:title"], capsys)
    assert rows[0]["city"] == "New York"
    assert rows[2]["city"] == "Paris"


def test_cli_convert_date_default(people_csv, capsys):
    rows = _run_main(["convert", people_csv, "joined:date"], capsys)
    assert rows[0]["joined"] == "2023-06-01"


def test_cli_convert_date_custom_fmt(people_csv, capsys):
    rows = _run_main(["convert", people_csv, "joined:date:%d/%m/%Y"], capsys)
    assert rows[0]["joined"] == "01/06/2023"
    assert rows[1]["joined"] == "15/01/2022"


def test_cli_convert_multiple_specs(people_csv, capsys):
    rows = _run_main(["convert", people_csv, "name:upper", "city:title"], capsys)
    assert rows[0]["name"] == "ALICE"
    assert rows[0]["city"] == "New York"


def test_cli_convert_output_file(people_csv, tmp_path, capsys):
    out = str(tmp_path / "result.csv")
    sys.argv = ["csv-surgeon", "convert", people_csv, "name:lower", "-o", out]
    main()
    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["name"] == "alice"
    assert rows[1]["name"] == "bob"
