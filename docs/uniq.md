# `uniq` — Filter Consecutive Duplicate Rows

The `uniq` command removes consecutive duplicate values in a specified column,
behaving like the Unix `uniq` utility but operating on CSV data.

## Usage

```
csv-surgeon uniq [OPTIONS] INPUT
```

### Positional Arguments

| Argument | Description |
|----------|-------------|
| `INPUT`  | Path to the input CSV file. Use `-` to read from stdin. |

### Options

| Flag | Description |
|------|-------------|
| `-c`, `--column` | **(Required)** Column whose consecutive values are compared. |
| `-o`, `--output` | Write output to this file instead of stdout. |
| `--count` | Prepend a `__count__` column with the run length for each group. |

## Examples

### Basic deduplication of consecutive rows

```bash
csv-surgeon uniq data.csv --column city
```

**Input (`data.csv`):**
```
city,sales
NYC,100
NYC,200
LA,300
LA,400
NYC,500
```

**Output:**
```
city,sales
NYC,100
LA,300
NYC,500
```

Only the *first* row of each consecutive run is kept.

### Show run counts

```bash
csv-surgeon uniq data.csv --column city --count
```

**Output:**
```
__count__,city,sales
2,NYC,100
2,LA,300
1,NYC,500
```

### Pipe from another command

```bash
csv-surgeon sort data.csv --key city | csv-surgeon uniq - --column city --count
```

Sort first so that all identical cities are adjacent, then count unique groups.

## Notes

- Unlike `dedupe`, `uniq` only collapses **consecutive** duplicates — non-adjacent
  repeated values are preserved as separate groups.
- The first row of each run is used as the representative row in the output.
- `--count` inserts `__count__` as the leftmost column.
