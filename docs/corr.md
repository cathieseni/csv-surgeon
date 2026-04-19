# corr — Pairwise Pearson Correlation

Compute the Pearson correlation coefficient between every pair of numeric columns.

## Usage

```
csv-surgeon corr [OPTIONS] INPUT
```

## Arguments

| Argument | Description |
|----------|-------------|
| `INPUT`  | Path to the input CSV file |

## Options

| Option | Description |
|--------|-------------|
| `-c`, `--columns` | Comma-separated list of columns to include (default: all numeric) |
| `-o`, `--output`  | Write output to file instead of stdout |

## Output

Produces a CSV with three columns:

- `col_a` — first column name
- `col_b` — second column name
- `correlation` — Pearson r value (6 decimal places)

The matrix includes self-correlations (always `1.000000`) and is symmetric.

## Examples

### All numeric columns

```bash
csv-surgeon corr data.csv
```

```
col_a,col_b,correlation
x,x,1.000000
x,y,1.000000
x,z,-1.000000
y,x,1.000000
...
```

### Specific columns

```bash
csv-surgeon corr data.csv -c price,quantity
```

### Save to file

```bash
csv-surgeon corr data.csv -o correlation_matrix.csv
```

## Notes

- Rows with non-numeric values in any selected column are skipped.
- If a column has zero variance the correlation is reported as `nan`.
- Requires at least 2 valid rows to compute a meaningful result.
