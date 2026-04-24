"""Unit tests for csv_surgeon/commands/mask_cmd.py."""
from __future__ import annotations

import csv
import io
from typing import Dict, List

import pytest

from csv_surgeon.commands.mask_cmd import _mask_rows, _parse_specs


# ---------------------------------------------------------------------------
# _parse_specs
# ---------------------------------------------------------------------------

def test_parse_specs_single():
    specs = _parse_specs(["email:.+@.+:***"])
    assert specs == [{"col": "email", "pattern": ".+@.+", "replacement": "***"}]


def test_parse_specs_multiple():
    specs = _parse_specs(["email:.+@.+:REDACTED", "phone:\\d{10}:HIDDEN"])
    assert len(specs) == 2
    assert specs[1]["col"] == "phone"


def test_parse_specs_invalid_no_colon_raises():
    with pytest.raises(ValueError, match="Invalid mask spec"):
        _parse_specs(["nodivider"])


def test_parse_specs_only_two_parts_raises():
    with pytest.raises(ValueError, match="Invalid mask spec"):
        _parse_specs(["col:pattern"])


# ---------------------------------------------------------------------------
# _mask_rows
# ---------------------------------------------------------------------------

def _rows() -> List[Dict[str, str]]:
    return [
        {"name": "Alice", "email": "alice@example.com", "phone": "5551234567"},
        {"name": "Bob",   "email": "bob@work.org",      "phone": "5559876543"},
    ]


def test_mask_rows_email():
    specs = _parse_specs(["email:.+:REDACTED"])
    result = list(_mask_rows(_rows(), specs))
    assert result[0]["email"] == "REDACTED"
    assert result[1]["email"] == "REDACTED"


def test_mask_rows_partial_regex():
    specs = _parse_specs(["email:@.+:@***"])
    result = list(_mask_rows(_rows(), specs))
    assert result[0]["email"] == "alice@***"
    assert result[1]["email"] == "bob@***"


def test_mask_rows_preserves_other_columns():
    specs = _parse_specs(["email:.+:X"])
    result = list(_mask_rows(_rows(), specs))
    assert result[0]["name"] == "Alice"
    assert result[0]["phone"] == "5551234567"


def test_mask_rows_unknown_column_is_noop():
    specs = _parse_specs(["nonexistent:.+:X"])
    original = _rows()
    result = list(_mask_rows(original, specs))
    assert result[0]["email"] == original[0]["email"]


def test_mask_rows_multiple_specs():
    specs = _parse_specs(["email:.+:E", "phone:.+:P"])
    result = list(_mask_rows(_rows(), specs))
    assert result[0]["email"] == "E"
    assert result[0]["phone"] == "P"


def test_mask_rows_empty_input():
    specs = _parse_specs(["email:.+:X"])
    result = list(_mask_rows([], specs))
    assert result == []


def test_mask_rows_no_match_unchanged():
    specs = _parse_specs(["name:^\\d+$:NUM"])
    result = list(_mask_rows(_rows(), specs))
    assert result[0]["name"] == "Alice"
