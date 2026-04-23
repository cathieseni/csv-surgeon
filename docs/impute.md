# `impute` — Fill Missing Values

The `impute` command replaces blank cells in one or more numeric columns using
a chosen statistical strategy.

## Synopsis

```
csv-surgeon impute <file> --columns <cols> [--strategy <s>] [--fill-value <v>] [-o <out>]
```

## Arguments

| Argument | Description |
|---|---|
| `file` | Input CSV file path |
| `--columns` | Comma-separated list of column names to impute |
| `--strategy` | `mean` (default), `median`, `mode`, or `constant` |
| `--fill-value` | Value used when `--strategy constant` (default `0`) |
| `-o / --output` | Write result to file instead of stdout |

## Strategies

| Strategy | Description |
|---|---|
| `mean` | Arithmetic mean of non-missing values |
| `median` | Median of non-missing values |
| `mode` | Most frequent non-missing value |
| `constant` | Fixed value supplied via `--fill-value` |

When all values in a column are missing the `--fill-value` is used as fallback
for every strategy.

## Examples

### Fill with column mean

```bash
csv-surgeon impute data.csv --columns score
```

### Fill multiple columns with median

```bash
csv-surgeon impute data.csv --columns score,age --strategy median
```

### Replace blanks with a constant

```bash
csv-surgeon impute data.csv --columns score --strategy constant --fill-value -1
```

### Write to a file

```bash
csv-surgeon impute data.csv --columns score -o imputed.csv
```

## Notes

- Non-numeric values already present in a column are **not** modified.
- Only **blank** (empty string) cells are replaced; whitespace-only cells are
  also treated as blank.
- Integer-like results (e.g. `20.0`) are written without a decimal point.
