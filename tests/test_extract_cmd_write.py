"""Additional unit tests for extract_cmd._write helper."""
from __future__ import annotations

import csv
import io

from csv_surgeon.commands.extract_cmd import _write


def _collect(rows, fieldnames):
    buf = io.StringIO()
    _write(rows, fieldnames, buf)
    buf.seek(0)
    return list(csv.DictReader(buf))


def test_write_empty_rows():
    result = _collect([], ["name", "age"])
    assert result == []


def test_write_single_row():
    rows = [{"name": "Alice", "age": "30"}]
    result = _collect(rows, ["name", "age"])
    assert result == [{"name": "Alice", "age": "30"}]


def test_write_multiple_rows():
    rows = [
        {"x": "1", "y": "2"},
        {"x": "3", "y": "4"},
    ]
    result = _collect(rows, ["x", "y"])
    assert len(result) == 2
    assert result[1]["x"] == "3"


def test_write_respects_fieldnames_order():
    rows = [{"b": "2", "a": "1"}]
    buf = io.StringIO()
    _write(rows, ["a", "b"], buf)
    buf.seek(0)
    header = buf.readline().strip()
    assert header == "a,b"


def test_write_omits_extra_keys():
    """Keys in row dict beyond fieldnames should be silently ignored by DictWriter."""
    rows = [{"name": "Alice", "age": "30", "extra": "ignored"}]
    result = _collect(rows, ["name", "age"])
    assert "extra" not in result[0]
