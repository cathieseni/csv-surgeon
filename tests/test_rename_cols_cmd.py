"""Tests for rename-cols command."""
from __future__ import annotations

import csv
import io
import sys
from types import SimpleNamespace

import pytest

from csv_surgeon.commands.rename_cols_cmd import (
    _parse_specs,
    _rename_header,
    run,
)


class _Args(SimpleNamespace):
    def __init__(self, input, specs, output=None):
        super().__init__(input=input, specs=specs, output=output)


def _read_stdout(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


@pytest.fixture
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("id,name,score\n1,Alice,90\n2,Bob,80\n")
    return str(p)


def test_parse_specs_index_single():
    specs = _parse_specs(["0:identifier"])
    assert specs == [("index", 0, "identifier")]


def test_parse_specs_index_multiple():
    specs = _parse_specs(["0:id", "2:points"])
    assert specs == [("index", 0, "id"), ("index", 2, "points")]


def test_parse_specs_regex():
    specs = _parse_specs(["s/score/points/"])
    assert specs == [("regex", "score", "points")]


def test_parse_specs_invalid_raises():
    with pytest.raises(ValueError):
        _parse_specs(["badspec"])


def test_parse_specs_invalid_regex_raises():
    with pytest.raises(ValueError):
        _parse_specs(["s/only_two_parts"])


def test_rename_header_by_index():
    header = ["id", "name", "score"]
    specs = _parse_specs(["1:full_name"])
    result = _rename_header(header, specs)
    assert result == ["id", "full_name", "score"]


def test_rename_header_negative_index():
    header = ["id", "name", "score"]
    specs = _parse_specs(["-1:points"])
    result = _rename_header(header, specs)
    assert result == ["id", "name", "points"]


def test_rename_header_by_regex():
    header = ["user_id", "user_name", "score"]
    specs = _parse_specs(["s/user_//"])
    result = _rename_header(header, specs)
    assert result == ["id", "name", "score"]


def test_rename_header_out_of_range_raises():
    header = ["a", "b"]
    specs = _parse_specs(["5:x"])
    with pytest.raises(IndexError):
        _rename_header(header, specs)


def test_run_stdout_index(csv_file, capsys):
    run(_Args(input=csv_file, specs=["2:points"]))
    rows = _read_stdout(capsys)
    assert rows[0]["points"] == "90"
    assert "score" not in rows[0]


def test_run_stdout_regex(csv_file, capsys):
    run(_Args(input=csv_file, specs=["s/name/full_name/"]))
    rows = _read_stdout(capsys)
    assert "full_name" in rows[0]
    assert "name" not in rows[0]


def test_run_output_file(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    run(_Args(input=csv_file, specs=["0:identifier"], output=out))
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["identifier"] == "1"
    assert "id" not in rows[0]
