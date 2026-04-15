"""End-to-end CLI integration tests for the `head` command."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def sales_csv(tmp_path: Path) -> Path:
    p = tmp_path / "sales.csv"
    with p.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["region", "product", "amount"])
        products = ["widget", "gadget", "doohickey"]
        for i in range(1, 31):          # 30 rows
            writer.writerow(
                [f"region{(i % 3) + 1}", products[i % 3], str(i * 5)]
            )
    return p


def _run_main(args: list[str], capsys) -> list[dict]:
    sys.argv = ["csv-surgeon"] + args
    main()
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    return list(reader)


def test_cli_head_default(sales_csv, capsys):
    rows = _run_main(["head", str(sales_csv)], capsys)
    assert len(rows) == 10
    assert "region" in rows[0]
    assert "product" in rows[0]
    assert "amount" in rows[0]


def test_cli_head_custom_n(sales_csv, capsys):
    rows = _run_main(["head", "-n", "7", str(sales_csv)], capsys)
    assert len(rows) == 7


def test_cli_head_more_than_available(sales_csv, capsys):
    rows = _run_main(["head", "-n", "100", str(sales_csv)], capsys)
    assert len(rows) == 30   # only 30 rows in fixture


def test_cli_head_zero_rows(sales_csv, capsys):
    rows = _run_main(["head", "-n", "0", str(sales_csv)], capsys)
    assert rows == []


def test_cli_head_output_file(sales_csv, tmp_path, capsys):
    out = tmp_path / "result.csv"
    _run_main(["head", "-n", "5", str(sales_csv), "-o", str(out)], capsys)
    with out.open(newline="") as fh:
        saved = list(csv.DictReader(fh))
    assert len(saved) == 5
    assert saved[0]["region"] == "region2"
