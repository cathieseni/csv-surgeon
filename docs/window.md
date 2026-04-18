# `window` — Rolling Window Aggregate

Add a new column containing a rolling (sliding-window) aggregate over a numeric column.

## Usage

```
csv-surgeon window <input> --col <column> --size <n> [--func sum|mean|min|max] [--out-col <name>] [-o <output>]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `input` | yes | Input CSV file |
| `--col` | yes | Column to aggregate |
| `--size` | yes | Number of rows in the rolling window |
| `--func` | no | Aggregation function: `sum`, `mean`, `min`, `max` (default: `mean`) |
| `--out-col` | no | Name of the output column (default: `<col>_<func>_<size>`) |
| `-o / --output` | no | Write result to file instead of stdout |

## Examples

### Rolling 3-row mean

```
csv-surgeon window sales.csv --col revenue --size 3
```

Adds column `revenue_mean_3`.

### Rolling 5-row sum to file

```
csv-surgeon window sales.csv --col revenue --size 5 --func sum -o out.csv
```

### Custom output column name

```
csv-surgeon window data.csv --col price --size 7 --func min --out-col price_7d_low
```

## Notes

- Non-numeric values in `--col` are treated as `NaN` and excluded from the window calculation.
- The window is a trailing window: for row *i* it covers rows `max(0, i-size+1)` through `i`.
- If all values in the current window are non-numeric the output cell is empty.
