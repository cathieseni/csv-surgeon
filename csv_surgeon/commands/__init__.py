"""Register all sub-commands with the top-level argument parser."""
from __future__ import annotations

import argparse

from csv_surgeon.commands import (
    aggregate_cmd,
    sort_cmd,
    rename_cmd,
    dedupe_cmd,
    fill_cmd,
    cast_cmd,
    slice_cmd,
    drop_cmd,
    stats_cmd,
    pivot_cmd,
    sample_cmd,
)

_COMMANDS = [
    aggregate_cmd,
    sort_cmd,
    rename_cmd,
    dedupe_cmd,
    fill_cmd,
    cast_cmd,
    slice_cmd,
    drop_cmd,
    stats_cmd,
    pivot_cmd,
    sample_cmd,
]


def register_all(subparsers: argparse._SubParsersAction) -> None:
    """Call ``add_subparser`` on every registered command module."""
    for cmd in _COMMANDS:
        cmd.add_subparser(subparsers)
