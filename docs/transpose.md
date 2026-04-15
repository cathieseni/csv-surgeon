# `transpose` command

Pivot a CSV so that **rows become columns** and **columns become rows**.

The first column of the output always contains the original header names;
each subsequent column corresponds to one data row from the input.

## Usage

```
csv-surgeon transpose [OPTIONS] FILE
```

### Positional arguments

| Argument | Description |
|----------|-------------|
| `FILE`   | Input CSV file. Use `-` to read from *stdin*. |

### Options

| Flag | Description |
|------|-------------|
| `-o FILE`, `--output FILE` | Write the result to `FILE` instead of *stdout*. |

## Example

Given `people.csv`:

```csv
name,age,city
Alice,30,NY
Bob,25,LA
```

Running:

```bash
csv-surgeon transpose people.csv
```

Produces:

```csv
name,Alice,Bob
age,30,25
city,NY,LA
```

## Notes

* The transposed output has **no header row** of its own — the first column
  serves that purpose.
* If the input has *N* columns and *M* data rows, the output has *N* rows
  and *M + 1* columns (the extra column is the field-name column).
* Missing values are replaced with an empty string.
