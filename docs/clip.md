# `clip` — Clamp Numeric Column Values

The `clip` command clamps values in one or more numeric columns to a specified
`[min, max]` range. Values below the lower bound are raised to it; values above
the upper bound are lowered to it. Non-numeric values are left untouched.

## Usage

```
csv-surgeon clip <input> --spec COL:MIN:MAX [--spec ...] [-o OUTPUT]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `input` | Path to the input CSV file |
| `--spec COL:MIN:MAX` | Column name and bounds (repeatable). Leave a bound empty to omit it. |
| `-o / --output` | Write result to file instead of stdout |

## Examples

### Clamp a score column to 0–100

```bash
csv-surgeon clip grades.csv --spec score:0:100
```

**Input**
```
name,score
Alice,120
Bob,75
Carol,-5
```

**Output**
```
name,score
Alice,100
Bob,75
Carol,0
```

### Only apply a lower bound

```bash
csv-surgeon clip prices.csv --spec price:0:
```

### Clamp multiple columns

```bash
csv-surgeon clip data.csv --spec age:0:120 --spec score:0:100 -o clipped.csv
```

## Notes

- Bounds are inclusive.
- Integer-valued results are written without a decimal point (`75`, not `75.0`).
- Rows where the target column is absent or non-numeric are passed through unchanged.
