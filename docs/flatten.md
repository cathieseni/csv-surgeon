# `flatten` command

Split multi-value cells into separate rows, one value per row.

## Synopsis

```
csv-surgeon flatten [OPTIONS] INPUT
```

## Arguments

| Argument | Description |
|----------|-------------|
| `INPUT`  | Path to the input CSV file, or `-` to read from stdin. |

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `-c`, `--column COLUMN` | *(required)* | Column whose cells should be split into separate rows. |
| `-d`, `--delimiter SEP` | `\|` | Separator character used inside each cell. |
| `-o`, `--output FILE` | stdout | Write result to this file instead of stdout. |

## Examples

### Basic usage

Given `employees.csv`:

```
id,name,skills
1,Alice,python|sql|excel
2,Bob,java
3,Carol,python|rust
```

```bash
csv-surgeon flatten employees.csv -c skills
```

Output:

```
id,name,skills
1,Alice,python
1,Alice,sql
1,Alice,excel
2,Bob,java
3,Carol,python
3,Carol,rust
```

### Custom separator

```bash
csv-surgeon flatten employees.csv -c skills -d ';'
```

### Write to file

```bash
csv-surgeon flatten employees.csv -c skills -o flat.csv
```

## Notes

- Whitespace around each value is stripped automatically.
- Rows with an empty cell in the target column emit a single row with an empty value.
- All other columns are duplicated unchanged for every emitted row.
