# `mask` — Redact or Replace Column Values

The `mask` command applies regex-based replacements to one or more columns,
making it easy to redact PII, anonymise data, or bulk-replace patterns.

## Synopsis

```
csv-surgeon mask [OPTIONS] SPEC [SPEC ...]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `SPEC`   | One or more masking specs in `COL:PATTERN:REPLACEMENT` format. |

### Spec format

```
COL:PATTERN:REPLACEMENT
```

* **COL** – header name of the column to mask.
* **PATTERN** – a Python `re` regular expression.
* **REPLACEMENT** – the string to substitute for each match (supports
  back-references such as `\\1`).

Use `\:` to include a literal colon inside any of the three fields.

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `-i / --input`  | `stdin`  | Input CSV file. |
| `-o / --output` | `stdout` | Output CSV file. |

## Examples

### Redact entire email column

```bash
csv-surgeon mask -i people.csv email:.+:REDACTED
```

### Mask all digits in an SSN column

```bash
csv-surgeon mask -i people.csv "ssn:\d:*"
```

Input:
```
name,ssn
Alice,123-45-6789
```

Output:
```
name,ssn
Alice,***-**-****
```

### Mask multiple columns at once

```bash
csv-surgeon mask -i people.csv \
  "email:.+:REDACTED" \
  "phone:\d{10}:HIDDEN"
```

### Write to a file instead of stdout

```bash
csv-surgeon mask -i people.csv -o masked.csv email:.+:***
```

## Notes

* Columns not listed in any spec are passed through unchanged.
* If a pattern does not match a value, that value is left as-is.
* Multiple specs are applied left-to-right; later specs see the output of
  earlier ones.
