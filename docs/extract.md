# `extract` — Extract Columns

Extract a subset of columns from a CSV file, discarding all others.

## Synopsis

```
csv-surgeon extract <input> -c <columns> [-o <output>]
```

## Arguments

| Argument | Description |
|---|---|
| `input` | Path to the input CSV file |
| `-c`, `--columns` | Comma-separated list of column names to keep |
| `-o`, `--output` | Output file path (default: stdout) |

## Examples

### Extract two columns to stdout

```bash
csv-surgeon extract data.csv -c name,age
```

Input (`data.csv`):

```
name,age,city,salary
Alice,30,NYC,90000
Bob,25,LA,75000
```

Output:

```
name,age
Alice,30
Bob,25
```

### Extract to a file

```bash
csv-surgeon extract data.csv -c name,city -o extracted.csv
```

## Notes

- Column order in the output follows the order specified in `-c`.
- An error is raised if any requested column is not present in the input.
- Duplicate column names in `-c` are preserved as-is.
