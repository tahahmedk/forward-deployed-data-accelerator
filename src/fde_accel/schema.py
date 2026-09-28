import math
from collections import Counter
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class FieldProfile:
    name: str
    inferred_type: str
    null_rate: float
    observed_types: dict[str, int]


def infer_scalar(value: str) -> str:
    value = value.strip()
    if not value:
        return "null"
    if value.lower() in {"true", "false"}:
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        if math.isfinite(float(value)):
            return "float"
    except ValueError:
        pass
    try:
        date.fromisoformat(value)
        return "date"
    except ValueError:
        return "string"


def profile_rows(rows: list[dict[str, str]]) -> list[FieldProfile]:
    result = []
    for field in sorted({k for row in rows for k in row}):
        values = [row.get(field, "") for row in rows]
        observed = Counter(infer_scalar(v) for v in values if v.strip())
        inferred = next(iter(observed)) if len(observed) == 1 else "mixed" if observed else "null"
        null_rate = sum(not v.strip() for v in values) / max(len(values), 1)
        result.append(
            FieldProfile(field, inferred, round(null_rate, 3), dict(sorted(observed.items())))
        )
    return result


def detect_drift(actual_fields: set[str], expected_fields: set[str]) -> dict[str, list[str]]:
    return {
        "missing": sorted(expected_fields - actual_fields),
        "unexpected": sorted(actual_fields - expected_fields),
    }
