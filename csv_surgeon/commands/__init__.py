"""Register all subcommands."""
from __future__ import annotations

from argparse import _SubParsersAction

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
    head_cmd,
    join_cmd,
    uniq_cmd,
    freq_cmd,
    flatten_cmd,
    explode_cmd,
    transpose_cmd,
    convert_cmd,
    reorder_cmd,
    add_col_cmd,
    merge_cmd,
    split_cmd,
    replace_cmd,
    strip_cmd,
    validate_cmd,
    format_cmd,
    diff_cmd,
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
    head_cmd,
    join_cmd,
    uniq_cmd,
    freq_cmd,
    flatten_cmd,
    explode_cmd,
    transpose_cmd,
    convert_cmd,
    reorder_cmd,
    add_col_cmd,
    merge_cmd,
    split_cmd,
    replace_cmd,
    strip_cmd,
    validate_cmd,
    format_cmd,
    diff_cmd,
]


def register_all(subparsers: _SubParsersAction) -> None:
    for cmd in _COMMANDS:
        cmd.add_subparser(subparsers)
