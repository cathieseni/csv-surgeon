"""Integration tests for the window command via CLI main."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def prices_csv(tmp_path) -> Path:
    p = tmp_path / "prices.csv"
    rows = [
        {"day": "1", "price": "10"},
        {"day": "2", "price": "20"},
        {"day": "3", "price": "30"},
        {"day": "4", "price": "40"},
        {"day": "5", "price": "50"},
    ]
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["day", "price"])
        w.writeheader()
        w.writerows(rows)
    return p


def _run_main(args: list[str], capsys):
    sys.argv = ["csv-surgeon"] + args
    main()
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


def test_cli_window_basic(prices_csv, capsys):
    rows = _run_main(["window", str(prices_csv), "--col", "price", "--size", "3"], capsys)
    assert len(rows) == 5
    assert "price_mean_3" in rows[0]


def test_cli_window_values_correct(prices_csv, capsys):
    rows = _run_main(["window", str(prices_csv), "--col", "price", "--size", "3", "--func", "sum"], capsys)
    # row index 2: window [10,20,30] -> sum 60
    assert float(rows[2]["price_sum_3"]) == pytest.approx(60.0)
    # row index 4: window [30,40,50] -> sum 120
    assert float(rows[4]["price_sum_3"]) == pytest.approx(120.0)


def test_cli_window_mean(prices_csv, capsys):
    rows = _run_main(["window", str(prices_csv), "--col", "price", "--size", "2", "--func", "mean"], capsys)
    assert float(rows[1]["price_mean_2"]) == pytest.approx(15.0)
    assert float(rows[3]["price_mean_2"]) == pytest.approx(35.0)


def test_cli_window_custom_out_col(prices_csv, capsys):
    rows = _run_main(
        ["window", str(prices_csv), "--col", "price", "--size", "2", "--out-col", "ma2"],
        capsys,
    )
    assert "ma2" in rows[0]
    assert "price_mean_2" not in rows[0]
