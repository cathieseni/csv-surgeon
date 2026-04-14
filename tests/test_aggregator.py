"""Tests for csv_surgeon.aggregator."""
import pytest

from csv_surgeon.aggregator import (
    AGGREGATORS,
    agg_count,
    agg_max,
    agg_mean,
    agg_min,
    agg_sum,
    agg_unique,
    aggregate_column,
    aggregate_summary,
)

ROWS = [
    {"name": "Alice", "score": "90", "dept": "eng"},
    {"name": "Bob",   "score": "70", "dept": "eng"},
    {"name": "Carol", "score": "80", "dept": "hr"},
    {"name": "Dave",  "score": "70", "dept": "hr"},
]


def test_count():
    assert agg_count(["a", "b", "c"]) == "3"


def test_sum():
    assert agg_sum(["1", "2", "3"]) == "6.0"


def test_min():
    assert agg_min(["5", "3", "8"]) == "3.0"


def test_max():
    assert agg_max(["5", "3", "8"]) == "8.0"


def test_mean():
    assert agg_mean(["10", "20", "30"]) == "20.0"


def test_unique():
    assert agg_unique(["a", "b", "a"]) == "2"


def test_empty_values_min():
    assert agg_min([]) == ""


def test_empty_values_max():
    assert agg_max([]) == ""


def test_empty_values_mean():
    assert agg_mean([]) == ""


def test_aggregate_column_sum():
    result = aggregate_column(ROWS, "score", "sum")
    assert result == "310.0"


def test_aggregate_column_count():
    result = aggregate_column(ROWS, "name", "count")
    assert result == "4"


def test_aggregate_column_unique_dept():
    result = aggregate_column(ROWS, "dept", "unique")
    assert result == "2"


def test_aggregate_column_unknown_raises():
    with pytest.raises(ValueError, match="Unknown aggregator"):
        aggregate_column(ROWS, "score", "median")


def test_aggregate_summary():
    specs = [("score", "sum"), ("name", "count")]
    summary = aggregate_summary(ROWS, specs)
    assert summary == {"score__sum": "310.0", "name__count": "4"}


def test_all_aggregators_registered():
    for name in ("count", "sum", "min", "max", "mean", "unique"):
        assert name in AGGREGATORS
