"""CSV filter DSL parser for csv-surgeon.

Supports chainable filter expressions like:
  col:name == 'Alice'
  col:age > 30
  col:status != 'inactive'
"""

import re
from dataclasses import dataclass
from typing import Any

SUPPORTED_OPS = ("==", "!=", ">=", "<=", ">", "<", "contains", "startswith", "endswith")

FILTER_PATTERN = re.compile(
    r'^col:(?P<column>\w+)\s+(?P<op>' + "|".join(re.escape(op) for op in SUPPORTED_OPS) + r')\s+(?P<value>.+)$'
)


@dataclass
class FilterExpression:
    column: str
    op: str
    value: Any

    def matches(self, row: dict) -> bool:
        """Return True if the given CSV row dict satisfies this filter."""
        if self.column not in row:
            raise KeyError(f"Column '{self.column}' not found in row.")
        cell = row[self.column]
        val = self.value

        # Attempt numeric comparison when both sides look numeric
        try:
            cell_num = float(cell)
            val_num = float(val)
            cell, val = cell_num, val_num
        except (ValueError, TypeError):
            cell = str(cell)
            val = str(val)

        ops = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            "contains": lambda a, b: str(b) in str(a),
            "startswith": lambda a, b: str(a).startswith(str(b)),
            "endswith": lambda a, b: str(a).endswith(str(b)),
        }
        return ops[self.op](cell, val)


def parse_filter(expression: str) -> FilterExpression:
    """Parse a single filter expression string into a FilterExpression."""
    expr = expression.strip()
    match = FILTER_PATTERN.match(expr)
    if not match:
        raise ValueError(
            f"Invalid filter expression: '{expression}'.\n"
            f"Expected format: col:<column> <op> <value>\n"
            f"Supported ops: {', '.join(SUPPORTED_OPS)}"
        )
    column = match.group("column")
    op = match.group("op")
    raw_value = match.group("value").strip()
    # Strip surrounding quotes if present
    if (raw_value.startswith("'") and raw_value.endswith("'")) or \
       (raw_value.startswith('"') and raw_value.endswith('"')):
        raw_value = raw_value[1:-1]
    return FilterExpression(column=column, op=op, value=raw_value)


def parse_filters(expressions: list[str]) -> list[FilterExpression]:
    """Parse multiple filter expressions (ANDed together)."""
    return [parse_filter(expr) for expr in expressions]
