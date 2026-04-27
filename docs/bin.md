# `bin` — Assign rows to equal-width numeric bins

The `bin` command partitions a numeric column into **equal-width intervals** and
appends a new column containing the bin label for each row.

## Usage

```
csv-surgeon bin <input> --column <col> [options]
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--column` | *(required)* | Numeric column to bin |
| `--bins` | `5` | Number of equal-width bins |
| `--label` | `bin` | Name of the new label column |
| `--output`, `-o` | stdout | Write result to this file |

## Bin label format

Each bin is labelled as a half-open interval `[lo, hi)`.  
The **last** bin is fully closed: `[lo, hi]`.

Values that cannot be parsed as a number receive an empty string.

## Examples

### Basic binning

```bash
csv-surgeon bin data.csv --column score --bins 4
```

Input:

```
name,score
Alice,12
Bob,37
Carol,55
Dave,88
```

Output:

```
name,score,bin
Alice,12,[12, 31.5)
Bob,37,[31.5, 51)
Carol,55,[51, 70.5)
Dave,88,[70.5, 88]
```

### Custom label column

```bash
csv-surgeon bin data.csv --column score --bins 3 --label grade_band
```

### Write to file

```bash
csv-surgeon bin data.csv --column score --bins 5 -o binned.csv
```

## Notes

- When all values in the column are identical the edges are shifted by ±0.5 so
  that a valid range still exists.
- Non-numeric values are silently ignored when computing edges and receive an
  empty bin label.
