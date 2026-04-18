# `cumsum` — Cumulative Sum Columns

Add a running-total column for one or more numeric fields.

## Usage

```
csv-surgeon cumsum [OPTIONS] INPUT COL [COL ...]
```

### Positional arguments

| Argument | Description |
|----------|-------------|
| `INPUT`  | Path to the input CSV file |
| `COL`    | One or more column names to accumulate |

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `-o / --output` | stdout | Write result to file instead of stdout |

## Output columns

For each column `COL` a new column `COL_cumsum` is appended. Original columns are preserved unchanged.

Non-numeric values in a column are silently skipped (the accumulator keeps its previous value).

## Examples

### Running total of revenue

```bash
csv-surgeon cumsum sales.csv revenue
```

Input:
```
month,revenue
Jan,1000
Feb,2000
Mar,500
```

Output:
```
month,revenue,revenue_cumsum
Jan,1000,1000.0
Feb,2000,3000.0
Mar,500,3500.0
```

### Multiple columns at once

```bash
csv-surgeon cumsum sales.csv revenue units -o out.csv
```
