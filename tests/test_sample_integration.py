"""End-to-end integration tests for the `sample` sub-command via cli.main."""
from __future__ import annotations

import csv
import io
import sys
import textwrap
import pytest

from csv_surgeon.cli import main


CSV_CONTENT = textwrap.dedent("""\
    id,city,value
    1,London,100
    2,Paris,200
    3,Berlin,300
    4,Rome,400
    5,Madrid,500
    6,Lisbon,600
    7,Vienna,700
    8,Warsaw,800
""").strip()


@pytest.fixture()
def sales_csv(tmp_path):
    p = tmp_path / "cities.csv"
    p.write_text(CSV_CONTENT + "\n")
    return p


def _run_main(args, capsys):
    sys.argv = ["csv-surgeon"] + args
    try:
        main()
    except SystemExit:
        pass
    return capsys.readouterr().out


def _parse(text):
    return list(csv.DictReader(io.StringIO(text)))


def test_cli_sample_count(sales_csv, capsys):
    out = _run_main(["sample", str(sales_csv), "-n", "3", "--seed", "0"], capsys)
    rows = _parse(out)
    assert len(rows) == 3
    assert "id" in rows[0]


def test_cli_sample_fraction(sales_csv, capsys):
    out = _run_main(["sample", str(sales_csv), "-f", "0.5", "--seed", "1"], capsys)
    rows = _parse(out)
    assert 1 <= len(rows) <= 8


def test_cli_sample_reproducible(sales_csv, capsys):
    out1 = _run_main(["sample", str(sales_csv), "-n", "4", "--seed", "99"], capsys)
    out2 = _run_main(["sample", str(sales_csv), "-n", "4", "--seed", "99"], capsys)
    assert out1 == out2


def test_cli_sample_output_file(sales_csv, tmp_path, capsys):
    out_file = tmp_path / "result.csv"
    _run_main(
        ["sample", str(sales_csv), "-n", "5", "--seed", "7", "-o", str(out_file)],
        capsys,
    )
    assert out_file.exists()
    rows = _parse(out_file.read_text())
    assert len(rows) == 5


def test_cli_sample_header_preserved(sales_csv, capsys):
    out = _run_main(["sample", str(sales_csv), "-n", "2", "--seed", "3"], capsys)
    rows = _parse(out)
    for row in rows:
        assert set(row.keys()) == {"id", "city", "value"}
