# `hash` — Hash Column Values

Replace column values with their cryptographic hash digest.
Useful for anonymising PII before sharing datasets.

## Usage

```
csv-surgeon hash <input> --columns <cols> [--algo <algo>] [--output <file>]
```

## Arguments

| Argument | Description |
|---|---|
| `input` | Path to input CSV file, or `-` for stdin |
| `--columns` | Comma-separated list of columns to hash (required) |
| `--algo` | Hash algorithm: `md5`, `sha1`, `sha256` (default: `sha256`) |
| `--output` / `-o` | Output file path (default: stdout) |

## Examples

### Hash an email column

```bash
csv-surgeon hash people.csv --columns email
```

Input:
```
name,email
Alice,alice@example.com
Bob,bob@example.com
```

Output:
```
name,email
Alice,3d879c8f...
Bob,8e9a1b2c...
```

### Hash multiple columns with MD5

```bash
csv-surgeon hash people.csv --columns email,phone --algo md5
```

### Write to a file

```bash
csv-surgeon hash people.csv --columns email --output anonymised.csv
```

## Notes

- Non-existent columns are silently treated as empty strings.
- The original column is replaced in-place; no new column is added.
- Hash output is always a lowercase hex digest string.
