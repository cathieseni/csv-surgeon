# `explode` — Split multi-value cells into separate rows

The `explode` command takes a column whose cells contain multiple values
separated by a delimiter and produces one output row per value, duplicating
all other column values.

## Synopsis

```
csv-surgeon explode <input> -c <column> [-s <sep>] [-o <output>]
```

## Arguments

| Flag | Long | Default | Description |
|------|------|---------|-------------|
| (positional) | | | Input CSV file, or `-` for stdin |
| `-c` | `--column` | *(required)* | Column whose values should be exploded |
| `-s` | `--sep` | `\|` | Delimiter used inside the cell |
| `-o` | `--output` | stdout | Write result to this file |

## Examples

### Basic usage

Given `employees.csv`:

```
employee,skills
Alice,python|sql|pandas
Bob,java
```

```bash
csv-surgeon explode employees.csv -c skills
```

Output:

```
employee,skills
Alice,python
Alice,sql
Alice,pandas
Bob,java
```

### Custom separator

```bash
csv-surgeon explode data.csv -c tags -s ';'
```

### Write to file

```bash
csv-surgeon explode data.csv -c tags -o exploded.csv
```

### Explode multiple columns

If you need to explode more than one column, chain the command or pipe the
output of one `explode` into another:

```bash
csv-surgeon explode data.csv -c tags | csv-surgeon explode - -c categories -s ';'
```

## Notes

- Cells that are **empty** produce a single row with an empty string value.
- Leading and trailing whitespace around each split value is stripped.
- All other columns are copied verbatim to every expanded row.
- If the specified column does not exist in the file, the command exits with a
  non-zero status and prints an error message listing the available columns.
