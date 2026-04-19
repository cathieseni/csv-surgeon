# `scale` — Multiply numeric columns by a factor

Multiply one or more numeric columns by a constant factor.

## Usage

```
csv-surgeon scale COL:FACTOR [COL:FACTOR ...] [-i INPUT] [-o OUTPUT]
```

## Arguments

| Argument | Description |
|---|---|
| `COL:FACTOR` | Column name and multiplier (e.g. `price:2.5`). Repeat for multiple columns. |
| `-i / --input` | Input CSV file (default: stdin). |
| `-o / --output` | Output CSV file (default: stdout). |

## Examples

### Double the `price` column

```bash
csv-surgeon scale price:2 -i products.csv
```

### Scale multiple columns

```bash
csv-surgeon scale revenue:0.001 cost:0.001 -i financials.csv -o scaled.csv
```

### Chain with filter

```bash
csv-surgeon filter 'region=EU' -i sales.csv | csv-surgeon scale amount:1.1
```

## Notes

- Non-numeric values in the target column are left unchanged.
- The factor may be any valid float, including negative values.
- Column names not present in the CSV are silently ignored.
