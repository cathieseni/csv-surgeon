"""Tests for log_cmd."""
from __future__ import annotations

import csv
import io
import math
import textwrap

import pytest

from csv_surgeon.commands.log_cmd import _log_rows, _parse_columns, run


def _make_rows(data: list[dict]) -> list[dict]:
    return data


class _Args:
    def __init__(self, input, columns, base="e", output="-"):
        self.input = input
        self.columns = columns
        self.base = base
        self.output = output


def test_parse_columns_single():
    assert _parse_columns("price") == ["price"]


def test_parse_columns_multiple():
    assert _parse_columns("a,b,c") == ["a", "b", "c"]


def test_parse_columns_strips_spaces():
    assert _parse_columns(" x , y ") == ["x", "y"]


def test_parse_columns_empty_raises():
    with pytest.raises(ValueError):
        _parse_columns("")


def test_log_rows_natural(tmp_path):
    rows = [{"val": "1.0"}, {"val": str(math.e)}]
    result = _log_rows(rows, ["val"], "e")
    assert float(result[0]["val"]) == pytest.approx(0.0)
    assert float(result[1]["val"]) == pytest.approx(1.0)


def test_log_rows_base2():
    rows = [{"val": "8"}]
    result = _log_rows(rows, ["val"], "2")
    assert float(result[0]["val"]) == pytest.approx(3.0)


def test_log_rows_base10():
    rows = [{"val": "1000"}]
    result = _log_rows(rows, ["val"], "10")
    assert float(result[0]["val"]) == pytest.approx(3.0)


def test_log_rows_non_positive_raises():
    rows = [{"val": "0"}]
    with pytest.raises(ValueError, match="non-positive"):
        _log_rows(rows, ["val"], "e")


def test_log_rows_negative_raises():
    rows = [{"val": "-5"}]
    with pytest.raises(ValueError):
        _log_rows(rows, ["val"], "e")


def test_log_rows_preserves_other_columns():
    rows = [{"name": "alice", "score": "100"}]
    result = _log_rows(rows, ["score"], "10")
    assert result[0]["name"] == "alice"


def test_run_stdout(tmp_path, capsys):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("x,y\n10,100\n1,10\n")
    run(_Args(str(csv_path), "x,y", base="10"))
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert float(rows[0]["x"]) == pytest.approx(1.0)
    assert float(rows[1]["y"]) == pytest.approx(1.0)


def test_run_output_file(tmp_path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("v\n2\n4\n8\n")
    out_path = tmp_path / "out.csv"
    run(_Args(str(csv_path), "v", base="2", output=str(out_path)))
    rows = list(csv.DictReader(out_path.open()))
    assert float(rows[0]["v"]) == pytest.approx(1.0)
    assert float(rows[1]["v"]) == pytest.approx(2.0)
    assert float(rows[2]["v"]) == pytest.approx(3.0)
