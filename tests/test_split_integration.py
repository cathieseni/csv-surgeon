"""Integration tests for the split command via CLI main()."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def dept_csv(tmp_path: Path) -> Path:
    p = tmp_path / "employees.csv"
    p.write_text(
        "name,dept,salary\n"
        "Alice,Eng,90000\n"
        "Bob,HR,70000\n"
        "Carol,Eng,95000\n"
        "Dave,HR,72000\n"
        "Eve,Finance,80000\n"
    )
    return p


def _run_main(args: list[str]) -> None:
    main(args)


def test_cli_split_creates_files(dept_csv, tmp_path):
    outdir = tmp_path / "out"
    _run_main(["split", str(dept_csv), "--by", "dept", "--outdir", str(outdir)])
    assert (outdir / "Eng.csv").exists()
    assert (outdir / "HR.csv").exists()
    assert (outdir / "Finance.csv").exists()


def test_cli_split_correct_rows(dept_csv, tmp_path):
    outdir = tmp_path / "out"
    _run_main(["split", str(dept_csv), "--by", "dept", "--outdir", str(outdir)])
    eng_rows = list(csv.DictReader((outdir / "Eng.csv").open()))
    assert [r["name"] for r in eng_rows] == ["Alice", "Carol"]


def test_cli_split_prefix(dept_csv, tmp_path):
    outdir = tmp_path / "out"
    _run_main(
        ["split", str(dept_csv), "--by", "dept", "--outdir", str(outdir), "--prefix", "emp_"]
    )
    assert (outdir / "emp_Eng.csv").exists()
    assert (outdir / "emp_HR.csv").exists()


def test_cli_split_preserves_all_columns(dept_csv, tmp_path):
    outdir = tmp_path / "out"
    _run_main(["split", str(dept_csv), "--by", "dept", "--outdir", str(outdir)])
    rows = list(csv.DictReader((outdir / "Finance.csv").open()))
    assert rows[0] == {"name": "Eve", "dept": "Finance", "salary": "80000"}
