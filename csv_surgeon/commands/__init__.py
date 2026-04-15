"""Register all subcommands with the top-level argument parser."""
from __future__ import annotations

import argparse

from csv_surgeon.commands import (
    aggregate_cmd,
    cast_cmd,
    dedupe_cmd,
    drop_cmd,
    fill_cmd,
    head_cmd,
    join_cmd,
    pivot_cmd,
    rename_cmd,
    sample_cmd,
    slice_cmd,
    sort_cmd,
    stats_cmd,
)


def register_all(subparsers: argparse._SubParsersAction) -> None:
    """Attach every subcommand to *subparsers*."""
    aggregate_cmd.add_subparser(subparsers)
    cast_cmd.add_subparser(subparsers)
    dedupe_cmd.add_subparser(subparsers)
    drop_cmd.add_subparser(subparsers)
    fill_cmd.add_subparser(subparsers)
    head_cmd.add_subparser(subparsers)
    join_cmd.add_subparser(subparsers)
    pivot_cmd.add_subparser(subparsers)
    rename_cmd.add_subparser(subparsers)
    sample_cmd.add_subparser(subparsers)
    slice_cmd.add_subparser(subparsers)
    sort_cmd.add_subparser(subparsers)
    stats_cmd.add_subparser(subparsers)
