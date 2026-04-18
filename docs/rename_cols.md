# rename-cols

Rename CSV column headers by **position index** or **regex pattern**.

## Usage

```
csv-surgeon rename-cols [OPTIONS] INPUT SPEC [SPEC ...]
```

### Options

| Flag | Description |
|------|-------------|
| `-o, --output FILE` | Write result to FILE instead of stdout |

## Spec formats

### Index-based

Use `INDEX:NEW_NAME` where `INDEX` is zero-based (negative indices supported).

```bash
# Rename column 0 to 'identifier'
csv-surgeon rename-cols data.csv 0:identifier

# Rename last column to 'points'
csv-surgeon rename-cols data.csv -1:points
```

### Regex-based

Use `s/PATTERN/REPLACEMENT/` (sed-style) to rename all columns matching a pattern.

```bash
# Strip 'user_' prefix from all column names
csv-surgeon rename-cols data.csv 's/user_//'

# Replace spaces with underscores
csv-surgeon rename-cols data.csv 's/ /_/g'
```

## Chaining specs

Multiple specs are applied **in order**:

```bash
csv-surgeon rename-cols data.csv 0:id 's/score/points/'
```

## Examples

**Input** (`data.csv`):
```
id,user_name,score
1,Alice,90
2,Bob,80
```

```bash
csv-surgeon rename-cols data.csv 's/user_//' 2:points
```

**Output**:
```
id,name,points
1,Alice,90
2,Bob,80
```
