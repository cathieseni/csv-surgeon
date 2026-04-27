"""Unit tests for bin_cmd."""
from __future__ import annotations

import csv
import io
import pytest

from csv_surgeon.commands.bin_cmd import (
    _compute_edges,
    _assign_bin,
    _bin_rows,
    run,
)


def _make_rows(data):
    return [dict(zip(["id", "score"], row)) for row in data]


# ── _compute_edges ────────────────────────────────────────────────────────────

def test_compute_edges_basic():
    edges = _compute_edges([0.0, 10.0], 5)
    assert len(edges) == 6
    assert edges[0] == pytest.approx(0.0)
    assert edges[-1] == pytest.approx(10.0)


def test_compute_edges_equal_values():
    edges = _compute_edges([5.0, 5.0], 4)
    assert len(edges) == 5


def test_compute_edges_empty():
    assert _compute_edges([], 3) == []


# ── _assign_bin ───────────────────────────────────────────────────────────────

def test_assign_bin_first():
    edges = [0.0, 2.0, 4.0, 6.0]
    assert _assign_bin(0.5, edges) == "[0, 2)"


def test_assign_bin_last_inclusive():
    edges = [0.0, 2.0, 4.0, 6.0]
    assert _assign_bin(6.0, edges) == "[4, 6]"


def test_assign_bin_boundary():
    edges = [0.0, 2.0, 4.0]
    assert _assign_bin(2.0, edges) == "[2, 4]"


def test_assign_bin_no_match():
    edges = [0.0, 2.0]
    assert _assign_bin(99.0, edges) == ""


# ── _bin_rows ─────────────────────────────────────────────────────────────────

def test_bin_rows_basic():
    rows = _make_rows([("a", "0"), ("b", "5"), ("c", "10")])
    result = list(_bin_rows(rows, "score", 2, "bin"))
    assert all("bin" in r for r in result)
    bins = [r["bin"] for r in result]
    assert bins[0] != bins[-1]  # first and last in different bins


def test_bin_rows_non_numeric_gets_empty():
    rows = [{"id": "a", "score": "N/A"}, {"id": "b", "score": "3"}]
    result = list(_bin_rows(rows, "score", 2, "bin"))
    assert result[0]["bin"] == ""
    assert result[1]["bin"] != ""


def test_bin_rows_custom_label():
    rows = _make_rows([("a", "1"), ("b", "2")])
    result = list(_bin_rows(rows, "score", 2, "group"))
    assert "group" in result[0]
    assert "bin" not in result[0]


# ── run (integration via tmp file) ───────────────────────────────────────────

class _Args:
    def __init__(self, path, column="score", bins=3, label="bin", output=None):
        self.input = path
        self.column = column
        self.bins = bins
        self.label = label
        self.output = output


@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("id,score\n1,10\n2,20\n3,30\n4,40\n4,50\n")
    return str(p)


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


def test_run_adds_bin_column(csv_file, capsys):
    run(_Args(csv_file))
    rows = _read_stdout(capsys)
    assert all("bin" in r for r in rows)
    assert len(rows) == 5


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    run(_Args(csv_file, output=out))
    with open(out) as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 5
    assert "bin" in rows[0]
