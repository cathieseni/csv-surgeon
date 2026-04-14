"""Command registry for csv-surgeon subcommands."""
from __future__ import annotations

from csv_surgeon.commands import (
    aggregate_cmd,
    cast_cmd,
    dedupe_cmd,
    drop_cmd,
    fill_cmd,
    rename_cmd,
    slice_cmd,
    sort_cmd,
)

#: Ordered list of command modules that expose ``add_subparser``.
COMMANDS = [
    aggregate_cmd,
    cast_cmd,
    dedupe_cmd,
    drop_cmd,
    fill_cmd,
    rename_cmd,
    slice_cmd,
    sort_cmd,
]


def register_all(subparsers) -> None:
    """Register every command module with *subparsers*."""
    for cmd in COMMANDS:
        cmd.add_subparser(subparsers)
