# `sqrt` — Add square-root columns

Compute the square root of one or more numeric columns and append the results
as new columns.

## Synopsis

```
csv-surgeon sqrt [--suffix SUFFIX] [-o OUTPUT] <file> <columns>
```

## Arguments

| Argument | Description |
|----------|-------------|
| `file` | Input CSV file |
| `columns` | Comma-separated list of column names to take the square root of |

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--suffix` | `_sqrt` | Suffix appended to the source column name for the new column |
| `-o / --output` | stdout | Write output to this file instead of stdout |

## Behaviour

- For each column listed, a new column named `<column><suffix>` is appended.
- If the value cannot be converted to a float, the new column is left **empty**.
- If the value is **negative**, the new column is left **empty** (imaginary
  results are not supported).
- The original column is preserved unchanged.
- Columns are appended in the order they are specified.

## Examples

### Basic usage

```bash
csv-surgeon sqrt data.csv score
```

Input:
```
name,score
alice,9
bob,16
carol,25
```

Output:
```
name,score,score_sqrt
alice,9,3.0
bob,16,4.0
carol,25,5.0
```

### Custom suffix

```bash
csv-surgeon sqrt data.csv score --suffix _root
```

### Multiple columns

```bash
csv-surgeon sqrt data.csv width,height
```

### Write to file

```bash
csv-surgeon sqrt data.csv score -o enriched.csv
```
