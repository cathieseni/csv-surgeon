"""Tests for corr_cmd."""
from __future__ import annotations
import csv
import io
import math
import pytest
from csv_surgeon.commands.corr_cmd import _parse_columns, _pearson, _compute_corr, _write


def _make_rows():
    return [
        {"x": "1", "y": "2", "z": "10"},
        {"x": "2", "y": "4", "z": "8"},
        {"x": "3", "y": "6", "z": "6"},
        {"x": "4", "y": "8", "z": "4"},
    ]


def test_parse_columns_single():
    assert _parse_columns("x") == ["x"]


def test_parse_columns_multiple():
    assert _parse_columns("x,y,z") == ["x", "y", "z"]


def test_parse_columns_strips_spaces():
    assert _parse_columns(" x , y ") == ["x", "y"]


def test_pearson_perfect_positive():
    xs = [1.0, 2.0, 3.0, 4.0]
    ys = [2.0, 4.0, 6.0, 8.0]
    assert abs(_pearson(xs, ys) - 1.0) < 1e-9


def test_pearson_perfect_negative():
    xs = [1.0, 2.0, 3.0, 4.0]
    ys = [8.0, 6.0, 4.0, 2.0]
    assert abs(_pearson(xs, ys) - (-1.0)) < 1e-9


def test_pearson_constant_returns_nan():
    xs = [1.0, 1.0, 1.0]
    ys = [2.0, 3.0, 4.0]
    assert math.isnan(_pearson(xs, ys))


def test_pearson_too_few_points():
    assert math.isnan(_pearson([1.0], [2.0]))


def test_compute_corr_shape():
    rows = _make_rows()
    results = _compute_corr(rows, ["x", "y", "z"])
    assert len(results) == 9  # 3x3


def test_compute_corr_self_correlation():
    rows = _make_rows()
    results = _compute_corr(rows, ["x", "y"])
    self_corr = [r for r in results if r["col_a"] == r["col_b"]]
    for r in self_corr:
        assert abs(float(r["correlation"]) - 1.0) < 1e-6


def test_compute_corr_x_z_negative():
    rows = _make_rows()
    results = _compute_corr(rows, ["x", "z"])
    xz = next(r for r in results if r["col_a"] == "x" and r["col_b"] == "z")
    assert float(xz["correlation"]) < -0.99


def test_write_output():
    results = [{"col_a": "x", "col_b": "y", "correlation": "1.000000"}]
    buf = io.StringIO()
    _write(results, buf)
    buf.seek(0)
    reader = csv.DictReader(buf)
    rows = list(reader)
    assert rows[0]["col_a"] == "x"
    assert rows[0]["correlation"] == "1.000000 test_write_empty_no_error():
    buf = io.StringIO()
    _write([], buf)
    assert buf.getvalue() == ""
