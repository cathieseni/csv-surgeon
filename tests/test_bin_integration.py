"""Integration tests for the 'bin' subcommand via main()."""
from __future__ import annotations

import csv
import io
import sys

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def scores_csv(tmp_path):
    p = tmp_path / "scores.csv"
    p.write_text(
        "name,score\nAlice,10\nBob,30\nCarol,50\nDave,70\nEve,90\n"
    )
    return str(p)


def _run_main(args, capsys):
    sys.argv = ["csv-surgeon"] + args
    main()
    return capsys.readouterr().out


def _parse(output):
    return list(csv.DictReader(io.StringIO(output)))


def test_cli_bin_basic(scores_csv, capsys):
    out = _run_main(["bin", scores_csv, "--column", "score", "--bins", "5"], capsys)
    rows = _parse(out)
    assert len(rows) == 5
    assert "bin" in rows[0]


def test_cli_bin_values_correct(scores_csv, capsys):
    out = _run_main(["bin", scores_csv, "--column", "score", "--bins", "2"], capsys)
    rows = _parse(out)
    bins = [r["bin"] for r in rows]
    # Alice (10) and Bob (30) in first half; Carol (50), Dave (70), Eve (90) in second
    assert bins[0] == bins[1]
    assert bins[2] == bins[3] == bins[4]
    assert bins[0] != bins[2]


def test_cli_bin_custom_label(scores_csv, capsys):
    out = _run_main(
        ["bin", scores_csv, "--column", "score", "--bins", "3", "--label", "bucket"],
        capsys,
    )
    rows = _parse(out)
    assert "bucket" in rows[0]
    assert "bin" not in rows[0]


def test_cli_bin_output_file(scores_csv, tmp_path, capsys):
    out_path = str(tmp_path / "binned.csv")
    _run_main(
        ["bin", scores_csv, "--column", "score", "--output", out_path],
        capsys,
    )
    with open(out_path) as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 5
    assert "bin" in rows[0]
