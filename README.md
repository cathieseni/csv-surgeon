# csv-surgeon

> CLI tool for in-place CSV transformations with a chainable filter DSL

---

## Installation

```bash
pip install csv-surgeon
```

Or with [pipx](https://pypa.github.io/pipx/) for isolated installs:

```bash
pipx install csv-surgeon
```

---

## Usage

```bash
csv-surgeon [OPTIONS] <file.csv>
```

### Example

Filter rows, rename a column, and drop another — all in one pass:

```bash
csv-surgeon data.csv \
  --filter "age > 18" \
  --filter "country == 'US'" \
  --rename "full_name:name" \
  --drop "internal_id" \
  --in-place
```

Transformations are applied in the order they are declared, making it easy to build readable, chainable pipelines directly from the command line.

### Common Options

| Option | Description |
|---|---|
| `--filter <expr>` | Keep rows matching the expression |
| `--rename <old:new>` | Rename a column |
| `--drop <col>` | Remove a column |
| `--in-place` | Overwrite the source file |
| `--output <file>` | Write result to a new file |
| `--dry-run` | Preview changes without writing |

---

## License

[MIT](LICENSE) © csv-surgeon contributors