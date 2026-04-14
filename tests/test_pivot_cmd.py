"""Tests for pivot_cmd."""
from __future__ import annotations

import csv
import io
import os
import tempfile

import pytest

from csv_surgeon.commands.pivot_cmd import _aggregate, run


@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text(
        "region,product,sales\n"
        "East,A,10\n"
        "East,B,20\n"
        "West,A,30\n"
        "West,B,40\n"
        "East,A,5\n"
    )
    return str(p)


class _Args:
    def __init__(self, input, index, columns, values, aggfunc="first", output=None):
        self.input = input
        self.index = index
        self.columns = columns
        self.values = values
        self.aggfunc = aggfunc
        self.output = output


def _read_stdout(capsys):
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    return list(reader)


def test_aggregate_first():
    assert _aggregate(["10", "5"], "first") == "10"


def test_aggregate_count():
    assert _aggregate(["10", "5"], "count") == "2"


def test_aggregate_sum():
    assert _aggregate(["10", "5"], "sum") == "15.0"


def test_aggregate_mean():
    assert _aggregate(["10", "20"], "mean") == "15.0"


def test_aggregate_empty():
    assert _aggregate([], "first") == ""


def test_pivot_first(csv_file, capsys):
    args = _Args(csv_file, index="region", columns="product", values="sales", aggfunc="first")
    run(args)
    rows = _read_stdout(capsys)
    east = next(r for r in rows if r["region"] == "East")
    assert east["A"] == "10"
    assert east["B"] == "20"
    west = next(r for r in rows if r["region"] == "West")
    assert west["A"] == "30"


def test_pivot_sum(csv_file, capsys):
    args = _Args(csv_file, index="region", columns="product", values="sales", aggfunc="sum")
    run(args)
    rows = _read_stdout(capsys)
    east = next(r for r in rows if r["region"] == "East")
    assert east["A"] == "15.0"  # 10 + 5


def test_pivot_count(csv_file, capsys):
    args = _Args(csv_file, index="region", columns="product", values="sales", aggfunc="count")
    run(args)
    rows = _read_stdout(capsys)
    east = next(r for r in rows if r["region"] == "East")
    assert east["A"] == "2"
    assert east["B"] == "1"


def test_pivot_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _Args(csv_file, index="region", columns="product", values="sales", output=out)
    run(args)
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2
    assert "A" in rows[0]
    assert "B" in rows[0]


def test_pivot_multi_index(tmp_path, capsys):
    p = tmp_path / "multi.csv"
    p.write_text("region,year,product,sales\nEast,2023,A,1\nEast,2023,B,2\nEast,2024,A,3\n")
    args = _Args(str(p), index="region,year", columns="product", values="sales")
    run(args)
    rows = _read_stdout(capsys)
    assert any(r["region"] == "East" and r["year"] == "2024" for r in rows)
