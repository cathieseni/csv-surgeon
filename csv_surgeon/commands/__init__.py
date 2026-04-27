"""Register all subcommands with the top-level argument parser."""
from __future__ import annotations


def register_all(subparsers) -> None:  # noqa: PLR0912
    from csv_surgeon.commands import aggregate_cmd
    from csv_surgeon.commands import sort_cmd
    from csv_surgeon.commands import rename_cmd
    from csv_surgeon.commands import dedupe_cmd
    from csv_surgeon.commands import fill_cmd
    from csv_surgeon.commands import cast_cmd
    from csv_surgeon.commands import slice_cmd
    from csv_surgeon.commands import drop_cmd
    from csv_surgeon.commands import stats_cmd
    from csv_surgeon.commands import pivot_cmd
    from csv_surgeon.commands import sample_cmd
    from csv_surgeon.commands import head_cmd
    from csv_surgeon.commands import join_cmd
    from csv_surgeon.commands import uniq_cmd
    from csv_surgeon.commands import freq_cmd
    from csv_surgeon.commands import flatten_cmd
    from csv_surgeon.commands import explode_cmd
    from csv_surgeon.commands import transpose_cmd
    from csv_surgeon.commands import convert_cmd
    from csv_surgeon.commands import reorder_cmd
    from csv_surgeon.commands import add_col_cmd
    from csv_surgeon.commands import merge_cmd
    from csv_surgeon.commands import split_cmd
    from csv_surgeon.commands import replace_cmd
    from csv_surgeon.commands import strip_cmd
    from csv_surgeon.commands import validate_cmd
    from csv_surgeon.commands import format_cmd
    from csv_surgeon.commands import diff_cmd
    from csv_surgeon.commands import normalize_cmd
    from csv_surgeon.commands import encode_cmd
    from csv_surgeon.commands import rename_cols_cmd
    from csv_surgeon.commands import truncate_cmd
    from csv_surgeon.commands import count_cmd
    from csv_surgeon.commands import clip_cmd
    from csv_surgeon.commands import shift_cmd
    from csv_surgeon.commands import round_cmd
    from csv_surgeon.commands import bucket_cmd
    from csv_surgeon.commands import percent_cmd
    from csv_surgeon.commands import zscore_cmd
    from csv_surgeon.commands import rank_cmd
    from csv_surgeon.commands import window_cmd
    from csv_surgeon.commands import cumsum_cmd
    from csv_surgeon.commands import lag_cmd
    from csv_surgeon.commands import movavg_cmd
    from csv_surgeon.commands import corr_cmd
    from csv_surgeon.commands import abs_cmd
    from csv_surgeon.commands import scale_cmd
    from csv_surgeon.commands import log_cmd
    from csv_surgeon.commands import pow_cmd
    from csv_surgeon.commands import interp_cmd
    from csv_surgeon.commands import impute_cmd
    from csv_surgeon.commands import clamp_cmd
    from csv_surgeon.commands import outlier_cmd
    from csv_surgeon.commands import shuffle_cmd
    from csv_surgeon.commands import copy_cmd
    from csv_surgeon.commands import mask_cmd
    from csv_surgeon.commands import extract_cmd
    from csv_surgeon.commands import sqrt_cmd
    from csv_surgeon.commands import hash_cmd
    from csv_surgeon.commands import bin_cmd

    aggregate_cmd.add_subparser(subparsers)
    sort_cmd.add_subparser(subparsers)
    rename_cmd.add_subparser(subparsers)
    dedupe_cmd.add_subparser(subparsers)
    fill_cmd.add_subparser(subparsers)
    cast_cmd.add_subparser(subparsers)
    slice_cmd.add_subparser(subparsers)
    drop_cmd.add_subparser(subparsers)
    stats_cmd.add_subparser(subparsers)
    pivot_cmd.add_subparser(subparsers)
    sample_cmd.add_subparser(subparsers)
    head_cmd.add_subparser(subparsers)
    join_cmd.add_subparser(subparsers)
    uniq_cmd.add_subparser(subparsers)
    freq_cmd.add_subparser(subparsers)
    flatten_cmd.add_subparser(subparsers)
    explode_cmd.add_subparser(subparsers)
    transpose_cmd.add_subparser(subparsers)
    convert_cmd.add_subparser(subparsers)
    reorder_cmd.add_subparser(subparsers)
    add_col_cmd.add_subparser(subparsers)
    merge_cmd.add_subparser(subparsers)
    split_cmd.add_subparser(subparsers)
    replace_cmd.add_subparser(subparsers)
    strip_cmd.add_subparser(subparsers)
    validate_cmd.add_subparser(subparsers)
    format_cmd.add_subparser(subparsers)
    diff_cmd.add_subparser(subparsers)
    normalize_cmd.add_subparser(subparsers)
    encode_cmd.add_subparser(subparsers)
    rename_cols_cmd.add_subparser(subparsers)
    truncate_cmd.add_subparser(subparsers)
    count_cmd.add_subparser(subparsers)
    clip_cmd.add_subparser(subparsers)
    shift_cmd.add_subparser(subparsers)
    round_cmd.add_subparser(subparsers)
    bucket_cmd.add_subparser(subparsers)
    percent_cmd.add_subparser(subparsers)
    zscore_cmd.add_subparser(subparsers)
    rank_cmd.add_subparser(subparsers)
    window_cmd.add_subparser(subparsers)
    cumsum_cmd.add_subparser(subparsers)
    lag_cmd.add_subparser(subparsers)
    movavg_cmd.add_subparser(subparsers)
    corr_cmd.add_subparser(subparsers)
    abs_cmd.add_subparser(subparsers)
    scale_cmd.add_subparser(subparsers)
    log_cmd.add_subparser(subparsers)
    pow_cmd.add_subparser(subparsers)
    interp_cmd.add_subparser(subparsers)
    impute_cmd.add_subparser(subparsers)
    clamp_cmd.add_subparser(subparsers)
    outlier_cmd.add_subparser(subparsers)
    shuffle_cmd.add_subparser(subparsers)
    copy_cmd.add_subparser(subparsers)
    mask_cmd.add_subparser(subparsers)
    extract_cmd.add_subparser(subparsers)
    sqrt_cmd.add_subparser(subparsers)
    hash_cmd.add_subparser(subparsers)
    bin_cmd.add_subparser(subparsers)
