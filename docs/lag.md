# `lag` — Add Lag Columns

The `lag` command appends new columns containing the value of a numeric (or any) column from a previous row.

## Usage

```
csv-surgeon lag <input> --columns <cols> [--periods N] [--fill VALUE] [--output <out>]
```

## Arguments

| Argument | Description |
|---|---|
| `input` | Path to the input CSV file |
| `--columns`, `-c` | Comma-separated list of columns to lag |
| `--periods`, `-n` | Number of rows to look back (default: `1`) |
| `--fill` | Value to use when no previous row exists (default: empty string) |
| `--output`, `-o` | Output file path (default: stdout) |

## Examples

### Lag a single column by 1 period

```
csv-surgeon lag prices.csv --columns close
```

Input:
```
date,close
2024-01-01,100
2024-01-02,105
2024-01-03,102
```

Output:
```
date,close,close_lag1
2024-01-01,100,
2024-01-02,105,100
2024-01-03,102,105
```

### Lag by 2 periods with a fill value

```
csv-surgeon lag prices.csv --columns close --periods 2 --fill NA
```

### Lag multiple columns

```
csv-surgeon lag data.csv --columns open,close --periods 1
```

Adds `open_lag1` and `close_lag1` columns.

## Notes

- The new column is named `<column>_lag<periods>` (e.g. `price_lag1`).
- Non-numeric values are supported; the raw string from the previous row is used.
- Rows with no available prior row receive the `--fill` value.
