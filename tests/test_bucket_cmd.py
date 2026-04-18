"""Tests for bucket_cmd."""
from __future__ import annotations

import csv
import io
import sys
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.bucket_cmd import (
    _assign_bucket,
    _bucket_rows,
    _parse_bins,
    run,
)


def _make_rows(data):
    return [dict(zip(["name", "score"], row)) for row in data]


# --- unit: _parse_bins ---

def test_parse_bins_valid():
    assert _parse_bins(["0", "50", "100"]) == [0.0, 50.0, 100.0]


def test_parse_bins_invalid_raises():
    with pytest.raises(ValueError):
        _parse_bins(["0", "abc", "100"])


# --- unit: _assign_bucket ---

def test_assign_bucket_first():
    assert _assign_bucket(5, [0, 10, 20], ["low", "high"]) == "low"


def test_assign_bucket_second():
    assert _assign_bucket(15, [0, 10, 20], ["low", "high"]) == "high"


def test_assign_bucket_last_edge_inclusive():
    assert _assign_bucket(20, [0, 10, 20], ["low", "high"]) == "high"


def test_assign_bucket_out_of_range():
    assert _assign_bucket(99, [0, 10, 20], ["low", "high"]) == ""


# --- unit: _bucket_rows ---

def test_bucket_rows_assigns_correctly():
    rows = _make_rows([("alice", "5"), ("bob", "15"), ("carol", "25")])
    result = list(
        _bucket_rows(rows, "score", [0.0, 10.0, 20.0, 30.0], ["low", "mid", "high"], "bucket")
    )
    assert result[0]["bucket"] == "low"
    assert result[1]["bucket"] == "mid"
    assert result[2]["bucket"] == "high"


def test_bucket_rows_non_numeric_gives_empty():
    rows = [{"name": "x", "score": "n/a"}]
    result = list(_bucket_rows(rows, "score", [0.0, 10.0], ["low"], "bucket"))
    assert result[0]["bucket"] == ""


# --- integration: run ---

class _Args(SimpleNamespace):
    def __init__(self, **kw):
        defaults = dict(col="score", bins=["0", "50", "100"], labels=None, out_col="bucket", output=None)
        defaults.update(kw)
        super().__init__(**defaults)


@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,score\nalice,20\nbob,75\ncarol,50\n")
    return str(p)


def test_run_stdout(csv_file, capsys):
    run(_Args(input=csv_file))
    out = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert rows[0]["bucket"] == "[0.0,50.0)"
    assert rows[1]["bucket"] == "[50.0,100.0)"
    assert rows[2]["bucket"] == "[50.0,100.0)"


def test_run_custom_labels(csv_file, capsys):
    run(_Args(input=csv_file, labels=["low", "high"]))
    out = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert rows[0]["bucket"] == "low"
    assert rows[1]["bucket"] == "high"


def test_run_output_file(csv_file, tmp_path):
    out_path = str(tmp_path / "out.csv")
    run(_Args(input=csv_file, output=out_path))
    with open(out_path) as fh:
        rows = list(csv.DictReader(fh))
    assert "bucket" in rows[0]


def test_run_wrong_label_count_exits(csv_file):
    with pytest.raises(SystemExit):
        run(_Args(input=csv_file, labels=["only_one"]))
