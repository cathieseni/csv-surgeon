# `movavg` — Moving Average Column

Appends a rolling moving-average column for a chosen numeric field.

## Usage

```
csv-surgeon movavg <input> --col <column> [--window N] [--out-col NAME] [-o output]
```

## Arguments

| Argument | Description | Default |
|---|---|---|
| `input` | Path to input CSV | *(required)* |
| `--col` | Source numeric column | *(required)* |
| `--window` | Rolling window size | `3` |
| `--out-col` | Name of the new column | `<col>_mavg` |
| `-o / --output` | Output file path | stdout |

## Examples

### Basic 3-period moving average

```bash
csv-surgeon movavg prices.csv --col close
```

Input:
```
date,close
2024-01-01,100
2024-01-02,110
2024-01-03,105
2024-01-04,120
```

Output:
```
date,close,close_mavg
2024-01-01,100,100
2024-01-02,110,105
2024-01-03,105,105
2024-01-04,120,111.667
```

### Custom window and column name

```bash
csv-surgeon movavg prices.csv --col close --window 5 --out-col ma5 -o prices_ma.csv
```

## Notes

- Non-numeric values in the source column are ignored when computing the average for that window position.
- The window is a *trailing* window; early rows use whatever values are available.
