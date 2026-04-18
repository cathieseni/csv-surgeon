"""Tests for percent_cmd."""
from __future__ import annotations

import csv
import io
import sys
import pytest

from csv_surgeon.commands.percent_cmd import _compute_total, _add_percent, run


_ROWS = [
    {"name": "alice", "sales": "200"},
    {"name": "bob", "sales": "300"},
    {"name": "carol", "sales": "500"},
]


def test_compute_total_basic():
    assert _compute_total(_ROWS, "sales") == 1000.0


def test_compute_total_skips_non_numeric():
    rows = [{"v": "10"}, {"v": "bad"}, {"v": "40"}]
    assert _compute_total(rows, "v") == 50.0


def test_add_percent_values():
    result = _add_percent(_ROWS, "sales", "sales_pct", 2, 1000.0)
    assert result[0]["sales_pct"] == "20.0"
    assert result[1]["sales_pct"] == "30.0"
    assert result[2]["sales_pct"] == "50.0"


def test_add_percent_zero_total():
    rows = [{"v": "0"}, {"v": "0"}]
    result = _add_percent(rows, "v", "v_pct", 2, 0.0)
    assert result[0]["v_pct"] == "0.0"


def test_add_percent_decimals():
    rows = [{"v": "1"}, {"v": "2"}]
    result = _add_percent(rows, "v", "v_pct", 4, 3.0)
    assert result[0]["v_pct"] == "33.3333"


class _Args:
    def __init__(self, input, col, out_col=None, decimals=2, output=None):
        self.input = input
        self.col = col
        self.out_col = out_col
        self.decimals = decimals
        self.output = output


@pytest.fixture()
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,sales\nalice,200\nbob,300\ncarol,500\n")
    return str(p)


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


def test_run_stdout(csv_file, capsys):
    run(_Args(csv_file, "sales"))
    rows = _read_stdout(capsys)
    assert rows[0]["sales_pct"] == "20.0"
    assert rows[2]["sales_pct"] == "50.0"


def test_run_custom_out_col(csv_file, capsys):
    run(_Args(csv_file, "sales", out_col="pct"))
    rows = _read_stdout(capsys)
    assert "pct" in rows[0]


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    run(_Args(csv_file, "sales", output=out))
    with open(out) as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 3
    assert rows[1]["sales_pct"] == "30.0"


def test_run_missing_col_exits(csv_file):
    with pytest.raises(SystemExit):
        run(_Args(csv_file, "revenue"))
