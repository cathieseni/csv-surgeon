"""Tests for encode_cmd."""
from __future__ import annotations

import base64
import csv
import io
import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.encode_cmd import _parse_columns, _encode_row, run


# ── helpers ──────────────────────────────────────────────────────────────────

class _Args(SimpleNamespace):
    def __init__(self, **kw):
        kw.setdefault("decode", False)
        kw.setdefault("output", None)
        super().__init__(**kw)


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(textwrap.dedent("""\
        name,secret,score
        Alice,hello,10
        Bob,world,20
    """))
    return p


def _read_stdout(capsys) -> list[dict]:
    captured = capsys.readouterr().out
    return list(csv.DictReader(io.StringIO(captured)))


# ── unit tests ────────────────────────────────────────────────────────────────

def test_parse_columns_single():
    assert _parse_columns("name") == ["name"]


def test_parse_columns_multiple():
    assert _parse_columns("a, b, c") == ["a", "b", "c"]


def test_encode_row_encodes():
    row = {"name": "Alice", "secret": "hello"}
    result = _encode_row(row, ["secret"], decode=False)
    assert result["secret"] == base64.b64encode(b"hello").decode()
    assert result["name"] == "Alice"


def test_encode_row_decodes():
    encoded = base64.b64encode(b"hello").decode()
    row = {"secret": encoded}
    result = _encode_row(row, ["secret"], decode=True)
    assert result["secret"] == "hello"


def test_encode_row_missing_column_ignored():
    row = {"name": "Alice"}
    result = _encode_row(row, ["nonexistent"], decode=False)
    assert result == {"name": "Alice"}


def test_run_encode_stdout(csv_file, capsys):
    args = _Args(input=str(csv_file), columns="secret")
    run(args)
    rows = _read_stdout(capsys)
    assert rows[0]["secret"] == base64.b64encode(b"hello").decode()
    assert rows[0]["name"] == "Alice"
    assert rows[0]["score"] == "10"


def test_run_decode_roundtrip(csv_file, tmp_path, capsys):
    encoded_file = tmp_path / "encoded.csv"
    args_enc = _Args(input=str(csv_file), columns="secret", output=str(encoded_file))
    run(args_enc)

    args_dec = _Args(input=str(encoded_file), columns="secret", decode=True)
    run(args_dec)
    rows = _read_stdout(capsys)
    assert rows[0]["secret"] == "hello"
    assert rows[1]["secret"] == "world"


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    args = _Args(input=str(csv_file), columns="secret", output=str(out))
    run(args)
    rows = list(csv.DictReader(out.open()))
    assert rows[1]["secret"] == base64.b64encode(b"world").decode()
