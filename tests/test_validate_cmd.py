"""Tests for validate_cmd."""
from __future__ import annotations

import csv
import io
import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.validate_cmd import _parse_rules, _validate, run


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(textwrap.dedent("""\
        id,email,age
        1,alice@example.com,30
        2,bad-email,25
        3,bob@example.com,abc
        4,carol@example.com,22
    """))
    return p


class _Args(SimpleNamespace):
    def __init__(self, file, rules=None, drop_invalid=False, output="-"):
        super().__init__(file=str(file), rules=rules or [], drop_invalid=drop_invalid, output=output)


def _make_rows(data: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(data)))


def test_parse_rules_single():
    rules = _parse_rules(["age:\\d+"])
    assert len(rules) == 1
    col, pat = rules[0]
    assert col == "age"
    assert pat.fullmatch("42")
    assert not pat.fullmatch("abc")


def test_parse_rules_multiple():
    rules = _parse_rules(["age:\\d+", "id:\\d+"])
    assert [c for c, _ in rules] == ["age", "id"]


def test_parse_rules_invalid_raises():
    with pytest.raises(ValueError, match="Invalid rule spec"):
        _parse_rules(["nodcolon"])


def test_validate_all_valid():
    rows = _make_rows("id,age\n1,30\n2,25\n")
    rules = _parse_rules(["age:\\d+"])
    valid, errors = _validate(iter(rows), rules, drop_invalid=False)
    assert errors == []


def test_validate_reports_errors():
    rows = _make_rows("id,age\n1,30\n2,abc\n")
    rules = _parse_rules(["age:\\d+"])
    valid, errors = _validate(iter(rows), rules, drop_invalid=False)
    assert len(errors) == 1
    assert "age" in errors[0]
    assert "abc" in errors[0]


def test_validate_drop_invalid():
    rows = _make_rows("id,age\n1,30\n2,abc\n3,99\n")
    rules = _parse_rules(["age:\\d+"])
    valid, errors = _validate(iter(rows), rules, drop_invalid=True)
    assert len(valid) == 2
    assert all(r["age"].isdigit() for r in valid)


def test_run_drop_invalid_stdout(csv_file, capsys):
    args = _Args(csv_file, rules=["age:\\d+", r"email:.+@.+\..+"], drop_invalid=True)
    run(args)
    out = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert all(r["age"].isdigit() for r in rows)


def test_run_invalid_exits(csv_file, capsys):
    args = _Args(csv_file, rules=["age:\\d+"], drop_invalid=False)
    with pytest.raises(SystemExit) as exc:
        run(args)
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "age" in err


def test_run_all_valid_no_exit(tmp_path, capsys):
    p = tmp_path / "ok.csv"
    p.write_text("id,age\n1,10\n2,20\n")
    args = _Args(p, rules=["age:\\d+"], drop_invalid=False)
    run(args)  # should not raise
