"""Integration tests for the flatten sub-command via CLI entry point."""
from __future__ import annotations

import csv
import io
import textwrap
from pathlib import Path

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def skills_csv(tmp_path: Path) -> Path:
    p = tmp_path / "skills.csv"
    p.write_text(
        textwrap.dedent("""\
        employee,skills
        Alice,python|sql|excel
        Bob,java
        Carol,python|rust
        """),
        encoding="utf-8",
    )
    return p


def _run_main(args: list[str], capsys) -> list[dict]:
    main(args)
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


def test_cli_flatten_basic(skills_csv, capsys):
    rows = _run_main(["flatten", str(skills_csv), "-c", "skills"], capsys)
    assert len(rows) == 6  # 3+1+2


def test_cli_flatten_values_correct(skills_csv, capsys):
    rows = _run_main(["flatten", str(skills_csv), "-c", "skills"], capsys)
    skill_values = [r["skills"] for r in rows]
    assert "python" in skill_values
    assert "rust" in skill_values
    assert skill_values.count("python") == 2


def test_cli_flatten_custom_sep(tmp_path, capsys):
    p = tmp_path / "data.csv"
    p.write_text("id,vals\n1,a;b;c\n2,x\n", encoding="utf-8")
    rows = _run_main(["flatten", str(p), "-c", "vals", "-d", ";"], capsys)
    assert len(rows) == 4
    assert [r["vals"] for r in rows[:3]] == ["a", "b", "c"]


def test_cli_flatten_output_file(skills_csv, tmp_path, capsys):
    out = tmp_path / "result.csv"
    main(["flatten", str(skills_csv), "-c", "skills", "-o", str(out)])
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert len(rows) == 6
