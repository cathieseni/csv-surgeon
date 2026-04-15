# `head` — Print the First N Rows

The `head` command outputs the first *N* rows of a CSV file, preserving the
header. It is useful for quick inspection of large files.

## Usage

```
csv-surgeon head [OPTIONS] FILE
```

### Arguments

| Argument | Description |
|----------|-------------|
| `FILE`   | Path to the input CSV file. |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `-n N`, `--rows N` | `10` | Number of data rows to output. |
| `-o FILE`, `--output FILE` | stdout | Write result to `FILE` instead of stdout. |

## Examples

### Print the first 10 rows (default)

```bash
csv-surgeon head data.csv
```

### Print the first 5 rows

```bash
csv-surgeon head -n 5 data.csv
```

### Save the first 20 rows to a new file

```bash
csv-surgeon head -n 20 data.csv -o preview.csv
```

## Notes

- If the file has fewer rows than *N*, all rows are returned.
- Passing `--rows 0` outputs only the header with no data rows.
- The original file is never modified; use `-o` to persist results.
