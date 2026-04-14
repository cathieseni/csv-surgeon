"""Tests for csv_surgeon.cli."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from csv_surgeon.cli import main

SAMPLE_CSV = textwrap.dedent("""\
    name,age,city
    Alice,30,Berlin
    Bob,25,Paris
    Carol,35,Berlin
""").strip()


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(SAMPLE_CSV, encoding="utf-8")
    return p


def test_main_no_filter(csv_file: Path, capsys):
    rc = main([str(csv_file)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "3 row(s)" in out


def test_main_with_filter(csv_file: Path, tmp_path: Path, capsys):
    out_file = tmp_path / "out.csv"
    rc = main([
        str(csv_file),
        "--output", str(out_file),
        "--filter", "city=Berlin",
    ])
    assert rc == 0
    content = out_file.read_text(encoding="utf-8")
    lines = [ln for ln in content.splitlines() if ln]
    assert len(lines) == 3  # header + 2 rows


def test_main_inplace_filter(csv_file: Path):
    rc = main([str(csv_file), "--filter", "age>28"])
    assert rc == 0
    lines = [ln for ln in csv_file.read_text().splitlines() if ln]
    assert len(lines) == 3  # header + Alice + Carol


def test_main_missing_file(capsys):
    rc = main(["nonexistent.csv"])
    assert rc == 1
    assert "error" in capsys.readouterr().err


def test_main_bad_filter(csv_file: Path, capsys):
    rc = main([str(csv_file), "--filter", "???"])
    assert rc == 2
    assert "filter error" in capsys.readouterr().err
