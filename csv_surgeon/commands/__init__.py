"""Register all subcommands with the top-level argument parser."""
from __future__ import annotations

import argparse

from csv_surgeon.commands import (
    aggregate_cmd,
    cast_cmd,
    dedupe_cmd,
    drop_cmd,
    explode_cmd,
    fill_cmd,
    flatten_cmd,
    freq_cmd,
    head_cmd,
    join_cmd,
    pivot_cmd,
    rename_cmd,
    sample_cmd,
    slice_cmd,
    sort_cmd,
    stats_cmd,
    uniq_cmd,
)

_COMMANDS = [
    aggregate_cmd,
    cast_cmd,
    dedupe_cmd,
    drop_cmd,
    explode_cmd,
    fill_cmd,
    flatten_cmd,
    freq_cmd,
    head_cmd,
    join_cmd,
    pivot_cmd,
    rename_cmd,
    sample_cmd,
    slice_cmd,
    sort_cmd,
    stats_cmd,
    uniq_cmd,
]


def register_all(subparsers: argparse._SubParsersAction) -> None:
    """Call add_subparser() for every known command module."""
    for mod in _COMMANDS:
        mod.add_subparser(subparsers)
