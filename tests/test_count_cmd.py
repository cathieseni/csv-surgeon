"""Tests for csv_surgeon/commands/count_cmd.py"""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path
from argparse import Namespace

import pytest

from csv_surgeon.commands.count_cmd import _count_rows, _write, run


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    with p.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "age"])
        writer.writeheader()
        writer.writerows([
            {"name": "Alice", "age": "30"},
            {"name": "Bob", "age": "25"},
            {"name": "Carol", "age": "40"},
        ])
    return p


class _Args(Namespace):
    def __init__(self, file, no_header=False, output=None):
        super().__init__(file=str(file), no_header=no_header, output=output)


def _read_stdout(capsys) -> str:
    return capsys.readouterr().out.strip()


def test_count_rows_basic():
    rows = [{"name": "Alice"}, {"name": "Bob"}, {"name": "Carol"}]
    buf = io.StringIO()
    buf.write("name\n" + "\n".join(r["name"] for r in rows))
    buf.seek(0)
    reader = csv.DictReader(buf)
    assert _count_rows(reader) == 3


def test_write_output():
    buf = io.StringIO()
    _write(42, buf)
    assert buf.getvalue() == "42\n"


def test_run_stdout(csv_file, capsys):
    run(_Args(csv_file))
    assert _read_stdout(capsys) == "3"


def test_run_no_header(tmp_path, capsys):
    p = tmp_path / "noheader.csv"
    p.write_text("Alice,30\nBob,25\n", encoding="utf-8")
    run(_Args(p, no_header=True))
    assert _read_stdout(capsys) == "2"


def test_run_empty_csv(tmp_path, capsys):
    p = tmp_path / "empty.csv"
    with p.open("w", newline="") as fh:
        csv.DictWriter(fh, fieldnames=["col"]).writeheader()
    run(_Args(p))
    assert _read_stdout(capsys) == "0"


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "count.txt"
    run(_Args(csv_file, output=str(out)))
    assert out.read_text(encoding="utf-8").strip() == "3"
