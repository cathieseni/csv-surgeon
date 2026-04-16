# `merge` — Vertically merge two CSV files

Stack two CSV files on top of each other (union / UNION ALL in SQL terms).

## Usage

```
csv-surgeon merge [OPTIONS] FILE OTHER
```

### Arguments

| Argument | Description |
|----------|-------------|
| `FILE`   | Primary CSV file |
| `OTHER`  | CSV file whose rows are appended |

### Options

| Option | Description |
|--------|-------------|
| `-o, --output FILE` | Write result to file instead of stdout |
| `--fill` | Fill missing columns with empty string; by default mismatched schemas raise an error |

## Examples

### Same schema

```bash
csv-surgeon merge employees_2023.csv employees_2024.csv -o all_employees.csv
```

### Different schemas (fill gaps)

```bash
csv-surgeon merge base.csv extra.csv --fill
```

Columns present in one file but not the other will be filled with `""` for rows
that lack them.  The output column order is: all columns from `FILE` first,
followed by any additional columns found only in `OTHER`.

## Notes

- Duplicate rows are **not** removed; use `dedupe` afterwards if needed.
- Without `--fill`, both files must have **identical** column sets (order does not matter).
