"""Command sub-modules for csv-surgeon."""
from csv_surgeon.commands import (
    aggregate_cmd,
    sort_cmd,
    rename_cmd,
    dedupe_cmd,
    fill_cmd,
    cast_cmd,
    slice_cmd,
)

ALL_COMMANDS = [
    aggregate_cmd,
    sort_cmd,
    rename_cmd,
    dedupe_cmd,
    fill_cmd,
    cast_cmd,
    slice_cmd,
]
