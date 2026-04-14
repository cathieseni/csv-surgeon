"""Tests for csv_surgeon.parser module."""

import pytest
from csv_surgeon.parser import FilterExpression, parse_filter, parse_filters


# --- parse_filter ---

def test_parse_equality():
    f = parse_filter("col:name == 'Alice'")
    assert f.column == "name"
    assert f.op == "=="
    assert f.value == "Alice"


def test_parse_numeric_gt():
    f = parse_filter("col:age > 30")
    assert f.column == "age"
    assert f.op == ">"
    assert f.value == "30"


def test_parse_contains():
    f = parse_filter('col:email contains gmail')
    assert f.op == "contains"
    assert f.value == "gmail"


def test_parse_startswith():
    f = parse_filter("col:code startswith 'US'")
    assert f.op == "startswith"
    assert f.value == "US"


def test_parse_invalid_raises():
    with pytest.raises(ValueError, match="Invalid filter expression"):
        parse_filter("name = Alice")


def test_parse_unknown_op_raises():
    with pytest.raises(ValueError):
        parse_filter("col:name ~= 'Alice'")


# --- FilterExpression.matches ---

def test_matches_string_equality():
    f = FilterExpression(column="status", op="==", value="active")
    assert f.matches({"status": "active"}) is True
    assert f.matches({"status": "inactive"}) is False


def test_matches_numeric_comparison():
    f = FilterExpression(column="age", op=">", value="25")
    assert f.matches({"age": "30"}) is True
    assert f.matches({"age": "20"}) is False


def test_matches_contains():
    f = FilterExpression(column="email", op="contains", value="@example")
    assert f.matches({"email": "user@example.com"}) is True
    assert f.matches({"email": "user@other.com"}) is False


def test_matches_missing_column_raises():
    f = FilterExpression(column="missing", op="==", value="x")
    with pytest.raises(KeyError, match="missing"):
        f.matches({"name": "Alice"})


# --- parse_filters ---

def test_parse_filters_multiple():
    filters = parse_filters(["col:age >= 18", "col:status == 'active'"])
    assert len(filters) == 2
    assert filters[0].column == "age"
    assert filters[1].column == "status"


def test_parse_filters_empty():
    assert parse_filters([]) == []
