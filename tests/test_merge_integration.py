"""Integration tests for the merge subcommand via cli.main."""
from __future__ import annotations

import csv
import io
import sys
import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def left_csv(tmp_path):
    p = tmp_path / "left.csv"
    p.write_text("id,city\n1,London\n2,Paris\n")
    return str(p)


@pytest.fixture()
def right_csv(tmp_path):
    p = tmp_path / "right.csv"
    p.write_text("id,city\n3,Berlin\n")
    return str(p)


def _run_main(args, capsys):
    sys.argv = ["csv-surgeon"] + args
    main()
    return capsys.readouterr().out


def _parse(text):
    return list(csv.DictReader(io.StringIO(text)))


def test_cli_merge_basic(left_csv, right_csv, capsys):
    out = _run_main(["merge", left_csv, right_csv], capsys)
    rows = _parse(out)
    assert len(rows) == 3


def test_cli_merge_values(left_csv, right_csv, capsys):
    out = _run_main(["merge", left_csv, right_csv], capsys)
    rows = _parse(out)
    cities = [r["city"] for r in rows]
    assert cities == ["London", "Paris", "Berlin"]


def test_cli_merge_schema_mismatch_raises(left_csv, tmp_path, capsys):
    other = tmp_path / "other.csv"
    other.write_text("id,city,pop\n3,Berlin,3500000\n")
    with pytest.raises(SystemExit):
        sys.argv = ["csv-surgeon", "merge", left_csv, str(other)]
        try:
            main()
        except ValueError:
            raise SystemExit(1)


def test_cli_merge_fill(left_csv, tmp_path, capsys):
    other = tmp_path / "other.csv"
    other.write_text("id,city,pop\n3,Berlin,3500000\n")
    out = _run_main(["merge", left_csv, str(other), "--fill"], capsys)
    rows = _parse(out)
    assert len(rows) == 3
    assert rows[0]["pop"] == ""
    assert rows[2]["pop"] == "3500000"
