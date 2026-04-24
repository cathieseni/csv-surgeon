"""Integration tests for the `mask` CLI subcommand."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path
from typing import List, Dict

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def people_csv(tmp_path: Path) -> Path:
    p = tmp_path / "people.csv"
    p.write_text(
        "name,email,ssn\n"
        "Alice,alice@example.com,123-45-6789\n"
        "Bob,bob@work.org,987-65-4321\n"
    )
    return p


def _run_main(argv: List[str], capsys) -> str:
    sys.argv = ["csv-surgeon"] + argv
    main()
    return capsys.readouterr().out


def _parse(output: str) -> List[Dict[str, str]]:
    return list(csv.DictReader(io.StringIO(output)))


def test_cli_mask_email(people_csv, capsys):
    out = _run_main(["mask", "-i", str(people_csv), "email:.+:REDACTED"], capsys)
    rows = _parse(out)
    assert all(r["email"] == "REDACTED" for r in rows)


def test_cli_mask_preserves_other_columns(people_csv, capsys):
    out = _run_main(["mask", "-i", str(people_csv), "email:.+:X"], capsys)
    rows = _parse(out)
    assert rows[0]["name"] == "Alice"
    assert rows[1]["name"] == "Bob"


def test_cli_mask_ssn_partial(people_csv, capsys):
    # Replace digits with * keeping dashes
    out = _run_main(["mask", "-i", str(people_csv), "ssn:\\d:*"], capsys)
    rows = _parse(out)
    assert rows[0]["ssn"] == "***-**-****"
    assert rows[1]["ssn"] == "***-**-****"


def test_cli_mask_multiple_columns(people_csv, capsys):
    out = _run_main(
        ["mask", "-i", str(people_csv), "email:.+:E", "ssn:.+:S"],
        capsys,
    )
    rows = _parse(out)
    assert rows[0]["email"] == "E"
    assert rows[0]["ssn"] == "S"


def test_cli_mask_output_file(people_csv, tmp_path, capsys):
    out_file = tmp_path / "out.csv"
    _run_main(
        ["mask", "-i", str(people_csv), "-o", str(out_file), "email:.+:HIDDEN"],
        capsys,
    )
    rows = _parse(out_file.read_text())
    assert rows[0]["email"] == "HIDDEN"
