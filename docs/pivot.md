# `pivot` command

Pivot a CSV by grouping rows on one or more index columns and spreading the
unique values of a *columns* column across new output columns.

## Synopsis

```
csv-surgeon pivot INPUT \
  --index INDEX_COLS \
  --columns COL \
  --values VAL_COL \
  [--aggfunc {first,sum,count,mean}] \
  [-o OUTPUT]
```

## Options

| Flag | Description |
|------|-------------|
| `INPUT` | Path to the input CSV file |
| `--index` | Comma-separated list of columns that form the row key |
| `--columns` | Column whose unique values become new column headers |
| `--values` | Column whose values populate the pivot cells |
| `--aggfunc` | How to aggregate duplicate entries: `first` (default), `sum`, `count`, `mean` |
| `-o / --output` | Write result to this file instead of stdout |

## Example

Given `sales.csv`:

```
region,product,revenue
East,A,100
East,B,200
West,A,300
West,B,400
```

```bash
csv-surgeon pivot sales.csv --index region --columns product --values revenue
```

Output:

```
region,A,B
East,100,200
West,300,400
```

## Aggregation

When multiple rows share the same index key **and** columns value, use
`--aggfunc` to control how those duplicates are combined:

```bash
csv-surgeon pivot sales.csv \
  --index region \
  --columns product \
  --values revenue \
  --aggfunc sum
```
