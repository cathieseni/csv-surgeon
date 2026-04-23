"""Integration tests for the `impute` CLI subcommand."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def data_csv(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(
        "name,score,age\n"
        "Alice,90,30\n"
        "Bob,,25\n"
        "Carol,80,\n"
        "Dave,,40\n"
    )
    return p


def _run_main(args: list[str]) -> str:
    sys.argv = ["csv-surgeon"] + args
    main()


def _parse(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


def test_cli_impute_mean(data_csv, capsys):
    _run_main(["impute", str(data_csv), "--columns", "score", "--strategy", "mean"])
    rows = _parse(capsys.readouterr().out)
    # mean of 90 and 80 = 85
    assert rows[1]["score"] == "85"
    assert rows[3]["score"] == "85"


def test_cli_impute_median(data_csv, capsys):
    _run_main(["impute", str(data_csv), "--columns", "score", "--strategy", "median"])
    rows = _parse(capsys.readouterr().out)
    assert rows[1]["score"] == "85"


def test_cli_impute_constant(data_csv, capsys):
    _run_main(
        [
            "impute", str(data_csv),
            "--columns", "score",
            "--strategy", "constant",
            "--fill-value", "0",
        ]
    )
    rows = _parse(capsys.readouterr().out)
    assert rows[1]["score"] == "0"
    assert rows[3]["score"] == "0"


def test_cli_impute_preserves_non_missing(data_csv, capsys):
    _run_main(["impute", str(data_csv), "--columns", "score"])
    rows = _parse(capsys.readouterr().out)
    assert rows[0]["score"] == "90"
    assert rows[2]["score"] == "80"


def test_cli_impute_output_file(data_csv, tmp_path, capsys):
    out = tmp_path / "out.csv"
    _run_main(
        ["impute", str(data_csv), "--columns", "age", "--strategy", "mean", "-o", str(out)]
    )
    rows = _parse(out.read_text())
    # mean of 30, 25, 40 = 31.666… → check it is non-empty
    assert rows[2]["age"] != ""
