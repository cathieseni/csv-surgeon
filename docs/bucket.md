# `bucket` — Bin numeric values into labeled ranges

Bin a numeric column into discrete labeled buckets based on provided bin edges.

## Usage

```
csv-surgeon bucket <input> --col COLUMN --bins EDGE [EDGE ...] [--labels LABEL [LABEL ...]] [--out-col NAME] [-o OUTPUT]
```

## Arguments

| Argument | Description |
|---|---|
| `input` | Input CSV file |
| `--col` | Column containing numeric values to bin |
| `--bins` | Bin edges (at least 2). Intervals are `[lo, hi)` except the last which is `[lo, hi]` |
| `--labels` | Optional labels for each bin. Count must equal `len(bins) - 1` |
| `--out-col` | Name of the new bucket column (default: `bucket`) |
| `-o / --output` | Write output to file instead of stdout |

## Examples

### Auto-generated labels

```bash
csv-surgeon bucket scores.csv --col score --bins 0 50 100
```

Output adds a `bucket` column with values like `[0.0,50.0)` or `[50.0,100.0]`.

### Custom labels

```bash
csv-surgeon bucket scores.csv --col score --bins 0 50 100 --labels low high
```

### Custom output column name

```bash
csv-surgeon bucket scores.csv --col score --bins 0 33 66 100 \
  --labels low medium high --out-col grade
```

## Notes

- Non-numeric values in the target column produce an empty string in the bucket column.
- Values outside all bin edges also produce an empty string.
- The last edge is inclusive: a value equal to the final edge falls into the last bucket.
