"""Integration tests for the bucket command via CLI main."""
from __future__ import annotations

import csv
import io
import sys

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def scores_csv(tmp_path):
    p = tmp_path / "scores.csv"
    p.write_text("name,score\nalice,10\nbob,55\ncarol,90\ndave,50\n")
    return str(p)


def _run_main(args, capsys):
    sys.argv = ["csv-surgeon"] + args
    try:
        main()
    except SystemExit:
        pass
    return capsys.readouterr().out


def _parse(out):
    return list(csv.DictReader(io.StringIO(out)))


def test_cli_bucket_basic(scores_csv, capsys):
    out = _run_main(["bucket", scores_csv, "--col", "score", "--bins", "0", "50", "100"], capsys)
    rows = _parse(out)
    assert len(rows) == 4
    assert "bucket" in rows[0]


def test_cli_bucket_values_correct(scores_csv, capsys):
    out = _run_main(
        ["bucket", scores_csv, "--col", "score", "--bins", "0", "50", "100", "--labels", "low", "high"],
        capsys,
    )
    rows = _parse(out)
    by_name = {r["name"]: r["bucket"] for r in rows}
    assert by_name["alice"] == "low"
    assert by_name["bob"] == "high"
    assert by_name["carol"] == "high"
    assert by_name["dave"] == "high"  # 50 == last edge of first bin → falls to high


def test_cli_bucket_custom_out_col(scores_csv, capsys):
    out = _run_main(
        ["bucket", scores_csv, "--col", "score", "--bins", "0", "100", "--out-col", "grade"],
        capsys,
    )
    rows = _parse(out)
    assert "grade" in rows[0]
    assert "bucket" not in rows[0]


def test_cli_bucket_three_bins(scores_csv, capsys):
    out = _run_main(
        [
            "bucket", scores_csv,
            "--col", "score",
            "--bins", "0", "40", "70", "100",
            "--labels", "low", "mid", "high",
        ],
        capsys,
    )
    rows = _parse(out)
    by_name = {r["name"]: r["bucket"] for r in rows}
    assert by_name["alice"] == "low"
    assert by_name["bob"] == "mid"
    assert by_name["carol"] == "high"
