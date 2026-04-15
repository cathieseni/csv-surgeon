# `join` command

Join two CSV files on a shared key column.

## Syntax

```
csv-surgeon join <left> <right> --key <column> [--how {left,inner}] [-o <output>]
```

## Arguments

| Argument | Description |
|---|---|
| `left` | Primary CSV file (use `-` for stdin). |
| `right` | Secondary CSV file to join against. |
| `--key`, `-k` | Column name present in **both** files to join on. |
| `--how` | Join strategy: `left` (default) or `inner`. |
| `--output`, `-o` | Destination file (default: stdout). |

## Join strategies

- **left** – Every row from the left file is kept. Rows with no match in the
  right file receive empty strings for the right-only columns.
- **inner** – Only rows that have a matching key in the right file are emitted.

## Examples

### Basic left join

```bash
csv-surgeon join employees.csv departments.csv --key id
```

`employees.csv`

```
id,name
1,Alice
2,Bob
3,Carol
```

`departments.csv`

```
id,dept
1,Engineering
2,Marketing
```

Output:

```
id,name,dept
1,Alice,Engineering
2,Bob,Marketing
3,Carol,
```

### Inner join to a file

```bash
csv-surgeon join employees.csv departments.csv --key id --how inner -o matched.csv
```

Output (`matched.csv`):

```
id,name,dept
1,Alice,Engineering
2,Bob,Marketing
```

## Notes

- Column names that exist in **both** files (other than the key) are taken from
  the left file; the right-file copy is ignored to avoid duplicates.
- When the right file has multiple rows with the same key value, each matching
  pair produces a separate output row (one-to-many expansion).
