"""Integration tests for the 'join' CLI subcommand."""
from __future__ import annotations

import csv
import io
import sys
import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def employees_csv(tmp_path):
    p = tmp_path / "employees.csv"
    p.write_text("id,name,age\n10,Diana,31\n20,Evan,25\n30,Faye,40\n")
    return str(p)


@pytest.fixture()
def departments_csv(tmp_path):
    p = tmp_path / "departments.csv"
    p.write_text("id,department\n10,HR\n20,Engineering\n")
    return str(p)


def _run_main(args, capsys):
    sys.argv = ["csv-surgeon"] + args
    try:
        main()
    except SystemExit:
        pass
    return capsys.readouterr().out


def _parse(output: str):
    return list(csv.DictReader(io.StringIO(output)))


def test_cli_join_left_default(employees_csv, departments_csv, capsys):
    out = _run_main(["join", employees_csv, departments_csv, "--key", "id"], capsys)
    rows = _parse(out)
    assert len(rows) == 3
    faye = next(r for r in rows if r["name"] == "Faye")
    assert faye["department"] == ""


def test_cli_join_inner(employees_csv, departments_csv, capsys):
    out = _run_main(
        ["join", employees_csv, departments_csv, "--key", "id", "--how", "inner"],
        capsys,
    )
    rows = _parse(out)
    assert len(rows) == 2
    names = {r["name"] for r in rows}
    assert names == {"Diana", "Evan"}


def test_cli_join_values_correct(employees_csv, departments_csv, capsys):
    out = _run_main(["join", employees_csv, departments_csv, "--key", "id"], capsys)
    rows = _parse(out)
    diana = next(r for r in rows if r["name"] == "Diana")
    assert diana["department"] == "HR"
    assert diana["age"] == "31"


def test_cli_join_output_file(employees_csv, departments_csv, tmp_path, capsys):
    out_path = str(tmp_path / "result.csv")
    _run_main(
        ["join", employees_csv, departments_csv, "--key", "id", "-o", out_path],
        capsys,
    )
    with open(out_path) as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 3
