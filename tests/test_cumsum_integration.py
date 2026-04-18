"""Integration tests for the cumsum CLI subcommand."""
from __future__ import annotations

import csv
import io
import sys

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def sales_csv(tmp_path):
    p = tmp_path / "sales.csv"
    p.write_text("month,revenue,units\nJan,1000,5\nFeb,2000,8\nMar,500,2\n")
    return str(p)


def _run_main(args, capsys):
    sys.argv = ["csv-surgeon"] + args
    try:
        main()
    except SystemExit:
        pass
    return capsys.readouterr().out


def _parse(text):
    return list(csv.DictReader(io.StringIO(text)))


def test_cli_cumsum_basic(sales_csv, capsys):
    out = _run_main(["cumsum", sales_csv, "revenue"], capsys)
    rows = _parse(out)
    assert "revenue_cumsum" in rows[0]


def test_cli_cumsum_values_correct(sales_csv, capsys):
    out = _run_main(["cumsum", sales_csv, "revenue"], capsys)
    rows = _parse(out)
    assert float(rows[0]["revenue_cumsum"]) == pytest.approx(1000.0)
    assert float(rows[1]["revenue_cumsum"]) == pytest.approx(3000.0)
    assert float(rows[2]["revenue_cumsum"]) == pytest.approx(3500.0)


def test_cli_cumsum_multiple_columns(sales_csv, capsys):
    out = _run_main(["cumsum", sales_csv, "revenue", "units"], capsys)
    rows = _parse(out)
    assert "revenue_cumsum" in rows[0]
    assert "units_cumsum" in rows[0]
    assert float(rows[2]["units_cumsum"]) == pytest.approx(15.0)


def test_cli_cumsum_preserves_original(sales_csv, capsys):
    out = _run_main(["cumsum", sales_csv, "revenue"], capsys)
    rows = _parse(out)
    assert rows[0]["revenue"] == "1000"
    assert rows[0]["month"] == "Jan"
