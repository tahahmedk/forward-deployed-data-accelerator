import re
from collections import Counter
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class QualityIssue:
    rule: str
    field: str
    row: int | None
    detail: str


def evaluate(
    rows: list[dict[str, str]],
    required: list[str],
    unique: list[str],
    allowed: dict[str, list[str]],
    formats: dict[str, str] | None = None,
) -> list[QualityIssue]:
    issues = []
    counts = {field: Counter(row.get(field, "").strip() for row in rows) for field in unique}
    for i, row in enumerate(rows, start=1):
        for field in required:
            if not row.get(field, "").strip():
                issues.append(QualityIssue("required", field, i, "value is missing"))
        for field, values in allowed.items():
            value = row.get(field, "").strip()
            if value and value not in values:
                issues.append(
                    QualityIssue("allowed-values", field, i, "value is outside the contract domain")
                )
        for field in unique:
            value = row.get(field, "").strip()
            if value and counts[field][value] > 1:
                issues.append(
                    QualityIssue("unique", field, i, "all rows sharing this key are quarantined")
                )
        for field, fmt in (formats or {}).items():
            value = row.get(field, "")
            if not value:
                continue
            valid = True
            if fmt == "email":
                valid = re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value) is not None
            elif fmt == "date":
                try:
                    valid = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
                    date.fromisoformat(value)
                except ValueError:
                    valid = False
            if not valid:
                issues.append(QualityIssue("format", field, i, f"expected {fmt}"))
    return issues
