# `sample` — Randomly sample rows from a CSV

The `sample` command lets you draw a random subset of rows from any CSV file.
It supports both an **absolute count** (`-n`) and a **fractional** mode (`-f`).

## Synopsis

```
csv-surgeon sample [OPTIONS] INPUT
```

## Options

| Flag | Description |
|------|-------------|
| `-n N`, `--count N` | Sample exactly *N* rows (capped at total row count). |
| `-f F`, `--fraction F` | Sample a fraction *F* of rows where `0 < F ≤ 1`. |
| `-s SEED`, `--seed SEED` | Integer seed for reproducible sampling. |
| `-o FILE`, `--output FILE` | Write result to *FILE* instead of stdout. |

`-n` and `-f` are mutually exclusive; exactly one must be provided.

## Examples

### Sample 100 rows

```bash
csv-surgeon sample data.csv -n 100
```

### Sample 10 % of rows, reproducibly

```bash
csv-surgeon sample data.csv -f 0.1 --seed 42 -o sample.csv
```

### Pipe from stdin

```bash
cat data.csv | csv-surgeon sample - -n 50
```

## Notes

- Row **order** in the output is *not* guaranteed to match the original order
  (uses `random.sample`).
- The header row is always preserved.
- When `-n` exceeds the number of data rows the entire dataset is returned.
