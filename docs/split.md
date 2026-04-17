# `split` — Split CSV by Column Values

The `split` command partitions a CSV file into multiple output files, one per unique value in a chosen column.

## Usage

```
csv-surgeon split <input> --by COLUMN [--outdir DIR] [--prefix PREFIX]
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `input` | yes | — | Path to input CSV file |
| `--by` | yes | — | Column whose values determine the split |
| `--outdir` | no | `.` | Directory to write output files into |
| `--prefix` | no | `` | String prepended to each output filename |

## Output

Each unique value in `--by` produces a file named `<prefix><value>.csv` inside `--outdir`.  
The command prints one output path per file to stdout.

## Examples

### Split employees by department

```bash
csv-surgeon split employees.csv --by dept --outdir out/
```

Given:

```
name,dept
Alice,Eng
Bob,HR
Carol,Eng
```

Produces:
- `out/Eng.csv`
- `out/HR.csv`

### Add a filename prefix

```bash
csv-surgeon split sales.csv --by region --outdir splits/ --prefix sales_
```

Produces files like `splits/sales_North.csv`, `splits/sales_South.csv`, etc.

## Notes

- Spaces in column values are replaced with `_` in filenames.
- The output directory is created automatically if it does not exist.
- Row order within each output file matches the original file.
