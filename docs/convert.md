# `convert` — Transform column values

The `convert` subcommand applies named string or date transformations to one or more columns in-place.

## Usage

```
csv-surgeon convert <file> COL:TRANSFORM [COL:TRANSFORM ...] [-o OUTPUT]
```

| Argument | Description |
|---|---|
| `file` | Input CSV file path, or `-` for stdin. |
| `COL:TRANSFORM` | One or more column/transform pairs (see below). |
| `-o`, `--output` | Write result to this file instead of stdout. |

## Available transforms

| Name | Description | Example spec |
|---|---|---|
| `upper` | Convert to UPPER CASE | `name:upper` |
| `lower` | Convert to lower case | `name:lower` |
| `title` | Convert to Title Case | `city:title` |
| `strip` | Remove leading/trailing whitespace | `notes:strip` |
| `date` | Reformat an ISO-8601 datetime string | `created_at:date:%d/%m/%Y` |

### `date` transform

The `date` transform parses the column value as an ISO-8601 datetime (e.g. `2024-03-15` or `2024-03-15T08:00:00`) and reformats it using a `strftime` pattern:

```
COL:date:FORMAT
```

The default format (when omitted) is `%Y-%m-%d`.

If the value cannot be parsed it is left unchanged.

## Examples

### Uppercase a single column

```bash
csv-surgeon convert people.csv name:upper
```

### Apply multiple transforms at once

```bash
csv-surgeon convert people.csv name:title city:lower
```

### Reformat a date column and save to a new file

```bash
csv-surgeon convert orders.csv created_at:date:%d/%m/%Y -o orders_formatted.csv
```

### Read from stdin

```bash
cat people.csv | csv-surgeon convert - name:upper
```

## Notes

- Columns listed in a spec that do not exist in the CSV are silently ignored.
- Multiple specs are applied in the order they are given.
- The header row is never modified.
