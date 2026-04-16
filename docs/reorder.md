# `reorder` — Reorder CSV Columns

Reorder the columns of a CSV file into any desired sequence.

## Usage

```
csv-surgeon reorder <input> --columns <col1,col2,...> [-o <output>]
```

## Arguments

| Argument | Description |
|---|---|
| `input` | Path to input CSV file, or `-` for stdin. |
| `--columns` | Comma-separated list of column names in the desired order. |
| `-o / --output` | Output file path. Defaults to stdout. |

## Behaviour

- Columns listed in `--columns` appear first, in the given order.
- Any columns **not** listed are appended at the end in their original order.
- An error is raised if a listed column does not exist in the input.

## Examples

### Reorder to put `country` first

```bash
csv-surgeon reorder sales.csv --columns country,product,revenue
```

### Write to a new file

```bash
csv-surgeon reorder data.csv --columns z,y,x -o reordered.csv
```

### Read from stdin

```bash
cat data.csv | csv-surgeon reorder - --columns b,a
```
