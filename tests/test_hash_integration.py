"""Integration tests for the hash command via CLI main."""
from __future__ import annotations

import csv
import hashlib
import io
import sys

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def people_csv(tmp_path):
    p = tmp_path / "people.csv"
    p.write_text(
        "name,email,age\n"
        "Alice,alice@example.com,30\n"
        "Bob,bob@example.com,25\n"
        "Carol,carol@example.com,35\n"
    )
    return str(p)


def _run_main(argv: list[str], capsys):
    sys.argv = ["csv-surgeon"] + argv
    main()
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    return list(reader)


def test_cli_hash_basic(people_csv, capsys):
    rows = _run_main(["hash", people_csv, "--columns", "email"], capsys)
    assert len(rows) == 3


def test_cli_hash_values_correct(people_csv, capsys):
    rows = _run_main(["hash", people_csv, "--columns", "email"], capsys)
    expected = hashlib.sha256(b"alice@example.com").hexdigest()
    assert rows[0]["email"] == expected


def test_cli_hash_preserves_other_columns(people_csv, capsys):
    rows = _run_main(["hash", people_csv, "--columns", "email"], capsys)
    assert rows[0]["name"] == "Alice"
    assert rows[0]["age"] == "30"


def test_cli_hash_algo_md5(people_csv, capsys):
    rows = _run_main(
        ["hash", people_csv, "--columns", "email", "--algo", "md5"], capsys
    )
    expected = hashlib.md5(b"alice@example.com").hexdigest()
    assert rows[0]["email"] == expected


def test_cli_hash_multiple_columns(people_csv, capsys):
    rows = _run_main(
        ["hash", people_csv, "--columns", "email,name"], capsys
    )
    assert rows[0]["name"] == hashlib.sha256(b"Alice").hexdigest()
    assert rows[0]["email"] == hashlib.sha256(b"alice@example.com").hexdigest()


def test_cli_hash_output_file(people_csv, tmp_path, capsys):
    out = str(tmp_path / "out.csv")
    _run_main(["hash", people_csv, "--columns", "email", "--output", out], capsys)
    with open(out) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3
    assert rows[1]["email"] == hashlib.sha256(b"bob@example.com").hexdigest()
