# `log` — Logarithmic Transformation

Apply a logarithm function to one or more numeric columns.

## Usage

```
csv-surgeon log <input> --columns <cols> [--base e|2|10] [--output <file>]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `input` | Path to the input CSV file |
| `--columns` | Comma-separated list of column names to transform |
| `--base` | Logarithm base: `e` (natural, default), `2`, or `10` |
| `--output` / `-o` | Output file path (default: stdout) |

## Examples

### Natural log of a single column

```bash
csv-surgeon log data.csv --columns price
```

### Log base 10 of multiple columns

```bash
csv-surgeon log data.csv --columns revenue,cost --base 10
```

### Save result to a file

```bash
csv-surgeon log data.csv --columns score --base 2 --output result.csv
```

## Notes

- All values in the target columns must be **positive numbers**. Non-positive values raise an error.
- Non-target columns are passed through unchanged.
- The output preserves the original column order.
