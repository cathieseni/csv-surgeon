"""End-to-end integration tests for the pivot sub-command via the CLI."""
from __future__ import annotations

import csv
import io
import sys
from unittest.mock import patch

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def sales_csv(tmp_path):
    p = tmp_path / "sales.csv"
    p.write_text(
        "region,product,revenue\n"
        "East,A,100\n"
        "East,B,200\n"
        "West,A,300\n"
        "West,B,400\n"
    )
    return str(p)


def _run_main(args: list[str], capsys) -> list[dict]:
    with patch("sys.argv", ["csv-surgeon"] + args):
        main()
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


def test_cli_pivot_basic(sales_csv, capsys):
    rows = _run_main(
        ["pivot", sales_csv, "--index", "region", "--columns", "product", "--values", "revenue"],
        capsys,
    )
    assert len(rows) == 2
    headers = list(rows[0].keys())
    assert "region" in headers
    assert "A" in headers
    assert "B" in headers


def test_cli_pivot_values_correct(sales_csv, capsys):
    rows = _run_main(
        ["pivot", sales_csv, "--index", "region", "--columns", "product", "--values", "revenue"],
        capsys,
    )
    east = next(r for r in rows if r["region"] == "East")
    assert east["A"] == "100"
    assert east["B"] == "200"


def test_cli_pivot_aggfunc_sum(tmp_path, capsys):
    p = tmp_path / "dup.csv"
    p.write_text("region,product,revenue\nEast,A,100\nEast,A,50\n")
    rows = _run_main(
        ["pivot", str(p), "--index", "region", "--columns", "product",
         "--values", "revenue", "--aggfunc", "sum"],
        capsys,
    )
    assert rows[0]["A"] == "150.0"


def test_cli_pivot_output_file(sales_csv, tmp_path):
    out = str(tmp_path / "pivot_out.csv")
    with patch("sys.argv", [
        "csv-surgeon", "pivot", sales_csv,
        "--index", "region", "--columns", "product", "--values", "revenue",
        "-o", out,
    ]):
        main()
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2
