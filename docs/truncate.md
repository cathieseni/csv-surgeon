# `truncate` — Truncate String Columns

Shorten the values in one or more columns to a maximum character length.

## Usage

```
csv-surgeon truncate <input> --spec COL:N [--spec COL:N ...] [-o OUTPUT] [--suffix SUFFIX]
```

## Arguments

| Argument | Description |
|---|---|
| `input` | Path to the input CSV file |
| `--spec COL:N` | Column name and max length (repeatable) |
| `-o / --output` | Output file path (default: stdout) |
| `--suffix` | String appended to truncated values (default: `""`) |

## Examples

### Truncate a single column

```bash
csv-surgeon truncate people.csv --spec name:10
```

### Truncate multiple columns with ellipsis suffix

```bash
csv-surgeon truncate people.csv --spec name:8 --spec bio:20 --suffix ...
```

### Write to a file

```bash
csv-surgeon truncate people.csv --spec description:50 -o out.csv
```

## Notes

- Values shorter than or equal to `N` are left unchanged.
- Columns not present in the CSV are silently ignored.
- `--suffix` is appended **after** truncation, so the total length will be `N + len(suffix)`.
