# `outlier` — Flag or Remove Outlier Rows

Detect rows where a numeric column contains an outlier value, then either
**flag** them with an extra `outlier` column or **remove** them entirely.

## Synopsis

```
csv-surgeon outlier <input> --column <col> [options]
```

## Options

| Option | Default | Description |
|---|---|---|
| `--column` | *(required)* | Numeric column to inspect |
| `--method` | `iqr` | Detection method: `iqr` or `zscore` |
| `--k` | `1.5` | IQR multiplier (used with `--method iqr`) |
| `--threshold` | `3.0` | Z-score threshold (used with `--method zscore`) |
| `--action` | `flag` | `flag` adds an `outlier` column; `remove` drops the row |
| `--output`, `-o` | stdout | Write result to file instead of stdout |

## Detection Methods

### IQR (Interquartile Range)

A value is an outlier if it falls outside the "fence":

```
lower_fence = Q1 - k * IQR
upper_fence = Q3 + k * IQR
```

where `IQR = Q3 - Q1`.  The default `k=1.5` is the classic Tukey rule.

### Z-Score

A value is an outlier if its absolute z-score exceeds the threshold:

```
|z| = |(x - mean) / stdev| > threshold
```

Rows whose column value cannot be parsed as a number are never flagged.

## Examples

### Flag outliers (default)

```bash
csv-surgeon outlier scores.csv --column score
```

Input:
```
player,score
alice,50
bob,55
eve,300
```

Output:
```
player,score,outlier
alice,50,0
bob,55,0
eve,300,1
```

### Remove outliers

```bash
csv-surgeon outlier scores.csv --column score --action remove
```

Output:
```
player,score
alice,50
bob,55
```

### Use z-score method with custom threshold

```bash
csv-surgeon outlier data.csv --column revenue --method zscore --threshold 2.5
```

### Strict IQR (k=1.0)

```bash
csv-surgeon outlier data.csv --column price --k 1.0
```

### Save to file

```bash
csv-surgeon outlier data.csv --column value -o cleaned.csv
```
