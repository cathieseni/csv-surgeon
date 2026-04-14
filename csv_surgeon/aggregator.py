"""Aggregation functions for CSV columns."""
from __future__ import annotations

from typing import Callable, Dict, List


AGGREGATORS: Dict[str, Callable[[List[str]], str]] = {}


def register(name: str) -> Callable:
    """Decorator to register an aggregator function."""
    def decorator(fn: Callable[[List[str]], str]) -> Callable:
        AGGREGATORS[name] = fn
        return fn
    return decorator


@register("count")
def agg_count(values: List[str]) -> str:
    return str(len(values))


@register("sum")
def agg_sum(values: List[str]) -> str:
    return str(sum(float(v) for v in values if v.strip() != ""))


@register("min")
def agg_min(values: List[str]) -> str:
    nums = [float(v) for v in values if v.strip() != ""]
    return str(min(nums)) if nums else ""


@register("max")
def agg_max(values: List[str]) -> str:
    nums = [float(v) for v in values if v.strip() != ""]
    return str(max(nums)) if nums else ""


@register("mean")
def agg_mean(values: List[str]) -> str:
    nums = [float(v) for v in values if v.strip() != ""]
    return str(sum(nums) / len(nums)) if nums else ""


@register("unique")
def agg_unique(values: List[str]) -> str:
    return str(len(set(values)))


def aggregate_column(
    rows: List[Dict[str, str]],
    column: str,
    agg_name: str,
) -> str:
    """Apply a named aggregation to a column across all rows."""
    if agg_name not in AGGREGATORS:
        raise ValueError(
            f"Unknown aggregator '{agg_name}'. "
            f"Available: {sorted(AGGREGATORS)}"
        )
    values = [row[column] for row in rows if column in row]
    return AGGREGATORS[agg_name](values)


def aggregate_summary(
    rows: List[Dict[str, str]],
    specs: List[tuple[str, str]],
) -> Dict[str, str]:
    """Return a dict of {label: result} for multiple (column, agg) specs."""
    return {
        f"{col}__{agg}": aggregate_column(rows, col, agg)
        for col, agg in specs
    }
