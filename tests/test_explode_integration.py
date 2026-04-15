"""End-to-end CLI integration tests for the 'explode' subcommand."""
from __future__ import annotations

import csv
import io
import textwrap
from unittest.mock import patch

import pytest

from csv_surgeon.cli import main


@pytest.fixture()
def skills_csv(tmp_path):
    p = tmp_path / "skills.csv"
    p.write_text(
        textwrap.dedent(
            """\
            employee,skills,dept
            Alice,python|sql|pandas,eng
            Bob,java,eng
            Carol,excel|powerpoint,sales
            """
        ),
        encoding="utf-8",
    )
    return str(p)


def _run_main(args: list[str], capsys) -> list[dict]:
    with patch("sys.argv", ["csv-surgeon"] + args):
        main()
    out = capsys.readouterr().out
    return list(csv.DictReader(io.StringIO(out)))


def test_cli_explode_basic(skills_csv, capsys):
    rows = _run_main(["explode", skills_csv, "-c", "skills"], capsys)
    assert len(rows) == 6  # Alice×3 + Bob×1 + Carol×2


def test_cli_explode_values_correct(skills_csv, capsys):
    rows = _run_main(["explode", skills_csv, "-c", "skills"], capsys)
    skills = {r["skills"] for r in rows}
    assert "python" in skills
    assert "pandas" in skills
    assert "powerpoint" in skills


def test_cli_explode_preserves_other_columns(skills_csv, capsys):
    rows = _run_main(["explode", skills_csv, "-c", "skills"], capsys)
    alice_rows = [r for r in rows if r["employee"] == "Alice"]
    assert all(r["dept"] == "eng" for r in alice_rows)


def test_cli_explode_custom_sep(tmp_path, capsys):
    p = tmp_path / "data.csv"
    p.write_text("name,tags\nX,a;b;c\nY,d\n", encoding="utf-8")
    rows = _run_main(["explode", str(p), "-c", "tags", "-s", ";"], capsys)
    assert len(rows) == 4
    assert {r["tags"] for r in rows} == {"a", "b", "c", "d"}
