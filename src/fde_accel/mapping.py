"""Fuzzy matching proposes mappings; only explicit or exact matches are trusted."""

import re
from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass(frozen=True)
class Mapping:
    source: str | None
    target: str
    confidence: float
    method: str


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def build_mapping(
    source_fields: list[str],
    target_fields: list[str],
    overrides: dict[str, str] | None = None,
    threshold: float = 0.58,
) -> list[Mapping]:
    overrides = overrides or {}
    if not 0 <= threshold <= 1:
        raise ValueError("mapping threshold must be between zero and one")
    if len(set(overrides.values())) != len(overrides):
        raise ValueError("multiple overrides for one target")
    if set(overrides) - set(source_fields) or set(overrides.values()) - set(target_fields):
        raise ValueError("override references an unknown source or target")
    reverse = {target: source for source, target in overrides.items()}
    result = []
    for target in target_fields:
        if target in reverse:
            result.append(Mapping(reverse[target], target, 1.0, "override"))
            continue
        exact = sorted(s for s in source_fields if _norm(s) == _norm(target))
        if len(exact) == 1:
            result.append(Mapping(exact[0], target, 1.0, "normalized-exact"))
            continue
        ranked = sorted(
            ((SequenceMatcher(None, _norm(s), _norm(target)).ratio(), s) for s in source_fields),
            key=lambda x: (-x[0], x[1]),
        )
        if len(exact) > 1 or (len(ranked) > 1 and ranked[0][0] == ranked[1][0]):
            result.append(Mapping(None, target, 0.0, "ambiguous"))
        elif ranked and ranked[0][0] >= threshold:
            result.append(Mapping(ranked[0][1], target, round(ranked[0][0], 3), "fuzzy"))
        else:
            result.append(Mapping(None, target, 0.0, "unmapped"))
    trusted = [m.source for m in result if m.method in {"override", "normalized-exact"}]
    if len(trusted) != len(set(trusted)):
        raise ValueError("one source cannot silently populate multiple canonical fields")
    return result


def apply_mapping(rows: list[dict[str, str]], mappings: list[Mapping]) -> list[dict[str, str]]:
    return [
        {m.target: row.get(m.source, "").strip() if m.source else "" for m in mappings}
        for row in rows
    ]
