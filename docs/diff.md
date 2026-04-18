# `diff` — Compare Two CSV Files

Show rows that were added or removed between two CSV files with identical schemas.

## Usage

```
csv-surgeon diff <file_a> <file_b> [--keys COL,...] [--output FILE]
```

## Arguments

| Argument | Description |
|---|---|
| `file_a` | Base (original) CSV file |
| `file_b` | Comparison (new) CSV file |
| `--keys` | Comma-separated columns used as row identity (default: all columns) |
| `--output` / `-o` | Write result to file instead of stdout |

## Output

The output is a CSV with an extra leading column `_diff` whose value is either
`added` (row exists only in `file_b`) or `removed` (row exists only in `file_a`).
Rows present in both files are omitted.

## Examples

### Basic diff

```bash
csv-surgeon diff employees_2023.csv employees_2024.csv
```

```
_diff,id,name,dept
removed,3,Carol,HR
added,7,Dave,Eng
```

### Using explicit key columns

```bash
csv-surgeon diff old.csv new.csv --keys id
```

Only the `id` column is used to determine row identity; other columns are ignored
for matching purposes.

### Writing to a file

```bash
csv-surgeon diff old.csv new.csv --output changes.csv
```

## Notes

- Both files **must** share the same header (column names and order).
- If `--keys` is omitted every column value must match for rows to be considered identical.
