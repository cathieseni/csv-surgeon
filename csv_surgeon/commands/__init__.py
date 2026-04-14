"""Register all sub-commands with the top-level argument parser."""
from __future__ import annotations

import argparse

from csv_surgeon.commands import (
    aggregate_cmd,
    cast_cmd,
    dedupe_cmd,
    drop_cmd,
    fill_cmd,
    pivot_cmd,
    rename_cmd,
    slice_cmd,
    sort_cmd,
    stats_cmd,
)

_COMMANDS = [
    aggregate_cmd,
    cast_cmd,
    dedupe_cmd,
    drop_cmd,
    fill_cmd,
    pivot_cmd,
    rename_cmd,
    slice_cmd,
    sort_cmd,
    stats_cmd,
]


def register_all(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Call add_subparser for every registered command module."""
    for cmd in _COMMANDS:
        cmd.add_subparser(subparsers)
