# `add-col` — Add New Columns

Add one or more new columns to every row of a CSV file.

## Usage

```
csv-surgeon add-col <input> -s NAME=VALUE [-s ...] [-o OUTPUT]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `input` | Path to the input CSV file |
| `-s`, `--spec` | Column spec in `NAME=VALUE` format (repeatable) |
| `-o`, `--output` | Write output to file instead of stdout |

## Value Templates

The `VALUE` part of a spec can reference existing column names using Python
`str.format` syntax: `{column_name}`.

## Examples

### Add a constant column

```bash
csv-surgeon add-col data.csv -s status=active
```

Input:
```
name,age
Alice,30
Bob,25
```

Output:
```
name,age,status
Alice,30,active
Bob,25,active
```

### Add a derived column using a template

```bash
csv-surgeon add-col data.csv -s label="{name}({age})"
```

Output:
```
name,age,label
Alice,30,Alice(30)
Bob,25,Bob(25)
```

### Add multiple columns at once

```bash
csv-surgeon add-col data.csv -s status=active -s source=import -o out.csv
```

## Notes

- If a template references a column that does not exist, the placeholder is kept as-is.
- Existing columns are never overwritten; if a spec name matches an existing column the value is updated in place.
