"""Tests for rank_cmd."""
from __future__ import annotations

import csv
import io
import sys
import types
from unittest.mock import patch

import pytest

from csv_surgeon.commands.rank_cmd import _rank_rows, run


def _make_rows(data):
    return [dict(zip(["name", "score"], row)) for row in data]


def _read_stdout(capsys):
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    return list(reader)


class _Args:
    def __init__(self, input, col="score", output=None, rank_col="rank", desc=False, method="ordinal"):
        self.input = input
        self.col = col
        self.output = output
        self.rank_col = rank_col
        self.desc = desc
        self.method = method


@pytest.fixture
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,score\nAlice,30\nBob,10\nCarol,20\n")
    return str(p)


def test_rank_rows_ordinal_asc():
    rows = _make_rows([("Alice", "30"), ("Bob", "10"), ("Carol", "20")])
    result = _rank_rows(rows, "score", "rank", desc=False, method="ordinal")
    by_name = {r["name"]: int(r["rank"]) for r in result}
    assert by_name["Bob"] == 1
    assert by_name["Carol"] == 2
    assert by_name["Alice"] == 3


def test_rank_rows_ordinal_desc():
    rows = _make_rows([("Alice", "30"), ("Bob", "10"), ("Carol", "20")])
    result = _rank_rows(rows, "score", "rank", desc=True, method="ordinal")
    by_name = {r["name"]: int(r["rank"]) for r in result}
    assert by_name["Alice"] == 1
    assert by_name["Carol"] == 2
    assert by_name["Bob"] == 3


def test_rank_rows_dense_ties():
    rows = _make_rows([("Alice", "20"), ("Bob", "10"), ("Carol", "20")])
    result = _rank_rows(rows, "score", "rank", desc=False, method="dense")
    by_name = {r["name"]: int(r["rank"]) for r in result}
    assert by_name["Bob"] == 1
    assert by_name["Alice"] == by_name["Carol"] == 2


def test_run_stdout(csv_file, capsys):
    run(_Args(input=csv_file))
    rows = _read_stdout(capsys)
    assert "rank" in rows[0]
    assert len(rows) == 3


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    run(_Args(input=csv_file, output=out))
    with open(out) as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 3
    assert "rank" in rows[0]


def test_run_duplicate_rank_col_raises(csv_file):
    with pytest.raises(ValueError, match="already exists"):
        run(_Args(input=csv_file, rank_col="score"))


def test_run_missing_col_raises(csv_file):
    with pytest.raises(ValueError, match="not found"):
        run(_Args(input=csv_file, col="nonexistent"))
