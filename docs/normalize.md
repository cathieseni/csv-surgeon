# `normalize` — Normalize Numeric Columns

Normalize one or more numeric columns in a CSV file using either
**min-max scaling** (default) or **z-score standardization**.

## Usage

```
csv-surgeon normalize [OPTIONS] FILE
```

## Options

| Flag | Description |
|------|-------------|
| `-c`, `--columns` | Comma-separated list of columns to normalize (**required**) |
| `--method` | `minmax` (default) or `zscore` |
| `-o`, `--output` | Output file path (default: stdout) |

## Methods

### `minmax`

Scales each value to the range **[0, 1]**:

```
x' = (x - min) / (max - min)
```

### `zscore`

Standardizes each value to have **mean 0** and **standard deviation 1**:

```
x' = (x - mean) / std
```

## Examples

### Normalize a single column (min-max)

```bash
csv-surgeon normalize scores.csv -c score
```

### Normalize multiple columns with z-score

```bash
csv-surgeon normalize data.csv -c height,weight --method zscore -o normalized.csv
```

### Input

```
name,score
Alice,10
Bob,20
Carol,30
```

### Output (minmax)

```
name,score
Alice,0.0
Bob,0.5
Carol,1.0
```

## Notes

- Non-numeric values in a target column are left unchanged.
- Columns not listed with `-c` are passed through unmodified.
- When all values in a column are identical, the denominator is treated as `1.0` to avoid division by zero.
