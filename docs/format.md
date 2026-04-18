# `format` — Pad / Align Column Values

The `format` command pads or aligns values in one or more columns to a fixed
character width. This is useful for producing human-readable output or
pre-processing data for fixed-width downstream consumers.

## Usage

```
csv-surgeon format <input> -s COL:WIDTH[:ALIGN] [-s ...] [-o OUTPUT]
```

### Arguments

| Argument | Description |
|---|---|
| `input` | Path to the input CSV file |
| `-s`, `--spec` | Format spec (repeatable). See below. |
| `-o`, `--output` | Output file path. Defaults to stdout. |

### Format Spec Syntax

```
COL:WIDTH[:ALIGN]
```

- **COL** – column name.
- **WIDTH** – target width as a positive integer.
- **ALIGN** – optional alignment character:
  - `l` – left-align (default)
  - `r` – right-align
  - `c` – center

Values shorter than `WIDTH` are padded with spaces. Values longer than `WIDTH`
are left unchanged.

## Examples

### Left-pad the `name` column to 10 characters

```bash
csv-surgeon format data.csv -s name:10
```

### Right-align `age` and center `city`

```bash
csv-surgeon format data.csv -s age:5:r -s city:12:c
```

### Write result to a file

```bash
csv-surgeon format data.csv -s score:8:r -o formatted.csv
```

## Notes

- Columns not mentioned in any `--spec` are passed through unchanged.
- Specifying an unknown column name is silently ignored.
