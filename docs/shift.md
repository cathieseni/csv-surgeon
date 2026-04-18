# `shift` — Shift or Scale Numeric Column Values

Apply arithmetic transformations to one or more numeric columns.

## Usage

```
csv-surgeon shift <input> --spec COL:OP:VALUE [--spec ...] [-o OUTPUT]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `input`  | Path to the input CSV file |
| `--spec` | Transformation spec in `COL:OP:VALUE` format (repeatable) |
| `-o / --output` | Output file path. Defaults to stdout |

## Supported Operations

| Op  | Description        |
|-----|--------------------|
| `add` | Add a constant   |
| `sub` | Subtract a constant |
| `mul` | Multiply by a factor |
| `div` | Divide by a factor |

## Examples

### Add 10 to all prices

```bash
csv-surgeon shift data.csv --spec price:add:10
```

### Apply multiple transformations

```bash
csv-surgeon shift data.csv --spec price:mul:1.1 --spec qty:sub:1 -o updated.csv
```

### Input

```
name,price,qty
Apple,10,3
Banana,5,7
```

### Output (`--spec price:add:10`)

```
name,price,qty
Apple,20,3
Banana,15,7
```

## Notes

- Non-numeric cells in the target column are left unchanged.
- Missing columns are silently skipped.
- Integer results are written without a decimal point; fractional results keep the decimal.
