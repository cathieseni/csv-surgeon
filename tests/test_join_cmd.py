"""Tests for csv_surgeon/commands/join_cmd.py."""
from __future__ import annotations

import csv
import io
import os
import sys
import pytest

from csv_surgeon.commands.join_cmd import _load_right, run


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def left_csv(tmp_path):
    p = tmp_path / "left.csv"
    p.write_text("id,name\n1,Alice\n2,Bob\n3,Carol\n")
    return str(p)


@pytest.fixture()
def right_csv(tmp_path):
    p = tmp_path / "right.csv"
    p.write_text("id,dept\n1,Engineering\n2,Marketing\n")
    return str(p)


class _Args:
    def __init__(self, left, right, key, how="left", output="-"):
        self.left = left
        self.right = right
        self.key = key
        self.how = how
        self.output = output


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_load_right(right_csv):
    lookup = _load_right(right_csv, "id")
    assert "1" in lookup
    assert lookup["1"][0]["dept"] == "Engineering"
    assert "2" in lookup


def test_join_left_keeps_unmatched(left_csv, right_csv, capsys):
    run(_Args(left_csv, right_csv, key="id", how="left"))
    rows = _read_stdout(capsys)
    assert len(rows) == 3
    carol = next(r for r in rows if r["name"] == "Carol")
    assert carol["dept"] == ""


def test_join_left_matched_rows(left_csv, right_csv, capsys):
    run(_Args(left_csv, right_csv, key="id", how="left"))
    rows = _read_stdout(capsys)
    alice = next(r for r in rows if r["name"] == "Alice")
    assert alice["dept"] == "Engineering"


def test_join_inner_excludes_unmatched(left_csv, right_csv, capsys):
    run(_Args(left_csv, right_csv, key="id", how="inner"))
    rows = _read_stdout(capsys)
    assert len(rows) == 2
    names = {r["name"] for r in rows}
    assert "Carol" not in names


def test_join_output_columns(left_csv, right_csv, capsys):
    run(_Args(left_csv, right_csv, key="id"))
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    assert set(reader.fieldnames or []) == {"id", "name", "dept"}


def test_join_to_file(left_csv, right_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    run(_Args(left_csv, right_csv, key="id", output=out))
    with open(out) as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 3
