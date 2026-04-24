"""Integration tests for the 'outlier' CLI sub-command."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def scores_csv(tmp_path) -> str:
    p = tmp_path / "scores.csv"
    p.write_text(
        "player,score\n"
        "alice,50\n"
        "bob,55\n"
        "carol,52\n"
        "dave,53\n"
        "eve,300\n"
    )
    return str(p)


def _run_main(argv: list[str], capsys) -> list[dict]:
    sys.argv = ["csv-surgeon"] + argv
    main()
    captured = capsys.readouterr().out
    return list(csv.DictReader(io.StringIO(captured)))


def test_cli_outlier_flag_basic(scores_csv, capsys):
    rows = _run_main(["outlier", scores_csv, "--column", "score"], capsys)
    assert len(rows) == 5
    assert "outlier" in rows[0]


def test_cli_outlier_flag_correct_row(scores_csv, capsys):
    rows = _run_main(["outlier", scores_csv, "--column", "score"], capsys)
    by_player = {r["player"]: r["outlier"] for r in rows}
    assert by_player["eve"] == "1"
    for p in ("alice", "bob", "carol", "dave"):
        assert by_player[p] == "0"


def test_cli_outlier_remove(scores_csv, capsys):
    rows = _run_main(
        ["outlier", scores_csv, "--column", "score", "--action", "remove"],
        capsys,
    )
    players = [r["player"] for r in rows]
    assert "eve" not in players
    assert len(players) == 4


def test_cli_outlier_zscore_method(scores_csv, capsys):
    rows = _run_main(
        ["outlier", scores_csv, "--column", "score", "--method", "zscore", "--threshold", "1.5"],
        capsys,
    )
    by_player = {r["player"]: r["outlier"] for r in rows}
    assert by_player["eve"] == "1"


def test_cli_outlier_output_file(scores_csv, tmp_path, capsys):
    out = str(tmp_path / "result.csv")
    sys.argv = ["csv-surgeon", "outlier", scores_csv, "--column", "score", "--output", out]
    main()
    rows = list(csv.DictReader(open(out)))
    assert len(rows) == 5
    assert "outlier" in rows[0]
