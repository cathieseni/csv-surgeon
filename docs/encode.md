# `encode` — Base64 Encode / Decode Columns

Base64-encode or decode one or more columns in a CSV file.

## Usage

```
csv-surgeon encode [OPTIONS] INPUT
```

## Options

| Flag | Description |
|------|-------------|
| `--columns`, `-c` | Comma-separated list of columns to process (**required**) |
| `--decode`, `-d` | Decode instead of encode |
| `--output`, `-o` | Write result to file (default: stdout) |

## Examples

### Encode a column

```bash
csv-surgeon encode data.csv --columns secret --output encoded.csv
```

Input:
```
name,secret
Alice,hello
Bob,world
```

Output:
```
name,secret
Alice,aGVsbG8=
Bob,d29ybGQ=
```

### Decode a column

```bash
csv-surgeon encode encoded.csv --columns secret --decode
```

Output:
```
name,secret
Alice,hello
Bob,world
```

### Encode multiple columns

```bash
csv-surgeon encode data.csv --columns "secret,token" --output out.csv
```

## Notes

- Columns not found in the header are silently skipped.
- Values that cannot be decoded (invalid base64) are left unchanged.
- Non-encoded columns pass through untouched.
