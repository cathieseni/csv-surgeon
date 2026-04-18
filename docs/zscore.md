# zscore

Append z-score normalised column(s) for one or more numeric fields.

## Usage

```
csv-surgeon zscore [--suffix SUFFIX] [--places PLACES] [-o OUTPUT] input columns...
```

## Arguments

| Argument | Description |
|---|---|
| `input` | Path to the input CSV file |
| `columns` | One or more column names to compute z-scores for |

## Options

| Option | Default | Description |
|---|---|---|
| `--suffix` | `_zscore` | Suffix appended to each new column name |
| `--places` | `4` | Number of decimal places to round the result |
| `-o / --output` | stdout | Write output to this file instead of stdout |

## How it works

For each specified column the command computes the population mean (μ) and
standard deviation (σ) across all rows, then emits a new column where each
value is:

```
z = (x - μ) / σ
```

Rows where the value cannot be parsed as a number receive an empty string in
the new column.  If all values in a column are identical (σ = 0) the standard
deviation is treated as 1 to avoid division by zero.

## Examples

```bash
# Add score_zscore column, write to stdout
csv-surgeon zscore data.csv score

# Multiple columns, custom suffix, 2 decimal places
csv-surgeon zscore data.csv height weight --suffix _z --places 2

# Write result to a new file
csv-surgeon zscore data.csv price --output normalised.csv
```

## Example output

Given `data.csv`:

```
name,score
alice,10
bob,20
carol,30
```

Running `csv-surgeon zscore data.csv score` produces:

```
name,score,score_zscore
alice,10,-1.2247
bob,20,0.0
carol,30,1.2247
```
