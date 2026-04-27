"""Tests for hash_cmd."""
from __future__ import annotations

import csv
import hashlib
import io
import textwrap
import types

import pytest

from csv_surgeon.commands.hash_cmd import (
    _hash_rows,
    _parse_columns,
    _write,
    run,
)


class _Args:
    def __init__(self, input, columns, algo="sha256", output=None):
        self.input = input
        self.columns = columns
        self.algo = algo
        self.output = output


def _make_rows():
    return [
        {"name": "Alice", "email": "alice@example.com", "score": "10"},
        {"name": "Bob", "email": "bob@example.com", "score": "20"},
    ]


def _read_stdout(capsys):
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    return list(reader)


# --- _parse_columns ---

def test_parse_columns_single():
    assert _parse_columns("email") == ["email"]


def test_parse_columns_multiple():
    assert _parse_columns("email,name") == ["email", "name"]


def test_parse_columns_strips_spaces():
    assert _parse_columns(" email , name ") == ["email", "name"]


def test_parse_columns_empty_raises():
    with pytest.raises(ValueError):
        _parse_columns("")


# --- _hash_rows ---

def test_hash_rows_sha256():
    rows = _make_rows()
    result = list(_hash_rows(rows, ["email"], "sha256"))
    expected = hashlib.sha256(b"alice@example.com").hexdigest()
    assert result[0]["email"] == expected


def test_hash_rows_md5():
    rows = _make_rows()
    result = list(_hash_rows(rows, ["email"], "md5"))
    expected = hashlib.md5(b"alice@example.com").hexdigest()
    assert result[0]["email"] == expected


def test_hash_rows_preserves_other_columns():
    rows = _make_rows()
    result = list(_hash_rows(rows, ["email"], "sha256"))
    assert result[0]["name"] == "Alice"
    assert result[0]["score"] == "10"


def test_hash_rows_multiple_columns():
    rows = _make_rows()
    result = list(_hash_rows(rows, ["email", "name"], "sha1"))
    assert result[0]["email"] == hashlib.sha1(b"alice@example.com").hexdigest()
    assert result[0]["name"] == hashlib.sha1(b"Alice").hexdigest()


# --- _write ---

def test_write_produces_header_and_rows():
    rows = [{"a": "1", "b": "2"}]
    buf = io.StringIO()
    _write(rows, ["a", "b"], buf)
    buf.seek(0)
    lines = buf.read().splitlines()
    assert lines[0] == "a,b"
    assert lines[1] == "1,2"


# --- run ---

def test_run_stdout(tmp_path, capsys):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("name,email\nAlice,alice@example.com\n")
    run(_Args(str(csv_path), "email"))
    rows = _read_stdout(capsys)
    expected = hashlib.sha256(b"alice@example.com").hexdigest()
    assert rows[0]["email"] == expected
    assert rows[0]["name"] == "Alice"


def test_run_output_file(tmp_path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("name,email\nBob,bob@example.com\n")
    out_path = tmp_path / "out.csv"
    run(_Args(str(csv_path), "email", output=str(out_path)))
    reader = csv.DictReader(out_path.open())
    rows = list(reader)
    expected = hashlib.sha256(b"bob@example.com").hexdigest()
    assert rows[0]["email"] == expected
