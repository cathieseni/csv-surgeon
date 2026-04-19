"""Integration tests for the corr subcommand via CLI."""
from __future__ import annotations
import csv
import io
import pytest
from unittest.mock import patch
from csv_surgeon.cli import main


@pytest.fixture()
def data_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("x,y,z\n1,2,10\n2,4,8\n3,6,6\n4,8,4\n")
    return str(p)


def _run_main(args: list[str]) -> str:
    import sys, io as _io
    buf = _io.StringIO()
    with patch("sys.stdout", buf):
        with patch("sys.argv", ["csv-surgeon"] + args):
            main()
    return buf.getvalue()


def _parse(output: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(output)))


def test_cli_corr_basic(data_csv):
    out = _run_main(["corr", data_csv])
    rows = _parse(out)
    assert len(rows) == 9


def test_cli_corr_self_is_one(data_csv):
    out = _run_main(["corr", data_csv])
    rows = _parse(out)
    for r in rows:
        if r["col_a"] == r["col_b"]:
            assert abs(float(r["correlation"]) - 1.0) < 1e-5


def test_cli_corr_subset_columns(data_csv):
    out = _run_main(["corr", data_csv, "-c", "x,y"])
    rows = _parse(out)
    assert len(rows) == 4
    cols = {r["col_a"] for r in rows} | {r["col_b"] for r in rows}
    assert cols == {"x", "y"}


def test_cli_corr_output_file(data_csv, tmp_path):
    out_file = str(tmp_path / "corr.csv")
    _run_main(["corr", data_csv, "-o", out_file])
    with open(out_file) as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 9
