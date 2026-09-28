"""Bounded batch processing with an explicit publication manifest."""

import csv
import hashlib
import io
import json
from dataclasses import asdict
from pathlib import Path

from .mapping import apply_mapping, build_mapping
from .quality import evaluate
from .schema import detect_drift, profile_rows

MAX_BYTES = 10_000_000


def read_bounded(path: Path) -> bytes:
    with path.open("rb") as stream:
        content = stream.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise ValueError("source exceeds 10 MB batch limit")
    return content


def load_source(path: Path, content: bytes | None = None) -> tuple[list[str], list[dict[str, str]]]:
    content = read_bounded(path) if content is None else content
    if path.suffix.lower() == ".json":
        raw = json.loads(content.decode("utf-8-sig"))
        if not isinstance(raw, list) or any(not isinstance(row, dict) for row in raw):
            raise ValueError("JSON source must be an array of objects")
        fields = sorted({key for row in raw for key in row})
        rows = []
        for row in raw:
            if any(isinstance(v, (dict, list)) for v in row.values()):
                raise ValueError("nested JSON requires an explicit source adapter")
            rows.append({k: "" if v is None else str(v) for k, v in row.items()})
    elif path.suffix.lower() == ".csv":
        with io.StringIO(content.decode("utf-8-sig"), newline="") as stream:
            reader = csv.DictReader(stream, strict=True)
            fields = reader.fieldnames or []
            rows = list(reader)
        if any(None in row or any(v is None for v in row.values()) for row in rows):
            raise ValueError("ragged CSV record")
    else:
        raise ValueError("supported source formats: CSV, JSON")
    if not fields or any(not f.strip() for f in fields) or len(fields) != len(set(fields)):
        raise ValueError("source needs unique, non-empty headers")
    return fields, rows


def validate_contract(contract: dict, config: dict) -> tuple[list[str], dict]:
    if not isinstance(contract, dict) or not isinstance(config, dict):
        raise ValueError("contract and configuration must be objects")
    if set(contract) != {"fields", "quality"} or set(config) - {
        "expected_source_fields",
        "overrides",
    }:
        raise ValueError("unknown or missing configuration section")
    if not isinstance(contract["fields"], list) or any(
        not isinstance(f, dict) or set(f) != {"name"} or not isinstance(f["name"], str)
        for f in contract["fields"]
    ):
        raise ValueError("fields must be name-only objects")
    fields = [f["name"] for f in contract["fields"]]
    if (
        not fields
        or len(fields) != len(set(fields))
        or any(not isinstance(f, str) or not f for f in fields)
    ):
        raise ValueError("canonical field names must be unique and non-empty")
    rules = contract["quality"]
    if not isinstance(rules, dict):
        raise ValueError("quality must be an object")
    for group in ("required", "unique"):
        value = rules.get(group, [])
        if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
            raise ValueError("required and unique rules must be lists of field names")
    for group in ("allowed", "formats"):
        if not isinstance(rules.get(group, {}), dict):
            raise ValueError("allowed and formats rules must be objects")
    if any(
        not isinstance(v, list) or not v or any(not isinstance(x, str) for x in v)
        for v in rules.get("allowed", {}).values()
    ):
        raise ValueError("allowed domains must be nonempty lists of strings")
    if any(not isinstance(v, str) for v in rules.get("formats", {}).values()):
        raise ValueError("format names must be strings")
    expected = config.get("expected_source_fields", [])
    if not isinstance(expected, list) or any(not isinstance(v, str) or not v for v in expected):
        raise ValueError("expected source fields must be a list of names")
    overrides = config.get("overrides", {})
    if not isinstance(overrides, dict) or any(not isinstance(v, str) for v in overrides.values()):
        raise ValueError("overrides must map source names to target names")
    if set(rules) - {"required", "unique", "allowed", "formats"}:
        raise ValueError("unknown quality rule")
    for group in ("required", "unique", "allowed", "formats"):
        if set(rules.get(group, [])) - set(fields):
            raise ValueError("quality rule references unknown canonical field")
    if any(v not in {"email", "date"} for v in rules.get("formats", {}).values()):
        raise ValueError("unsupported format rule")
    return fields, rules


def run(
    input_csv: str | Path, contract_path: str | Path, config_path: str | Path, out_dir: str | Path
) -> dict:
    source = Path(input_csv)
    content = read_bounded(source)
    fields, rows = load_source(source, content)
    contract = json.loads(Path(contract_path).read_text(encoding="utf-8"))
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    targets, rules = validate_contract(contract, config)
    mappings = build_mapping(fields, targets, config.get("overrides"))
    normalized = apply_mapping(rows, mappings)
    drift = detect_drift(set(fields), set(config.get("expected_source_fields", fields)))
    blockers = [
        f"review mapping for {m.target}"
        for m in mappings
        if m.method not in {"override", "normalized-exact"}
    ]
    if drift["missing"]:
        blockers.append("expected source columns missing")
    issues = evaluate(
        normalized,
        rules.get("required", []),
        rules.get("unique", []),
        rules.get("allowed", {}),
        rules.get("formats", {}),
    )
    invalid = {i.row for i in issues}
    accepted = [row for i, row in enumerate(normalized, 1) if not blockers and i not in invalid]
    rejected = [
        {
            "source_row": i,
            "record": row,
            "reasons": blockers + [asdict(issue) for issue in issues if issue.row == i],
        }
        for i, row in enumerate(normalized, 1)
        if blockers or i in invalid
    ]
    fingerprint = hashlib.sha256(
        content + json.dumps([contract, config], sort_keys=True).encode()
    ).hexdigest()
    report = {
        "run_fingerprint": fingerprint,
        "records": len(rows),
        "accepted": len(accepted),
        "rejected": len(rejected),
        "status": "BLOCKED" if blockers else "REVIEW_REQUIRED" if rejected else "ACCEPTED",
        "blockers": blockers,
        "source_profile": [asdict(p) for p in profile_rows(rows)],
        "schema_drift": drift,
        "mappings": [asdict(m) for m in mappings],
        "quality": {"issue_count": len(issues), "issues": [asdict(i) for i in issues]},
    }
    # One immutable directory per invocation. Never overwrite a previous trusted result.
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=False)
    with (out / "normalized.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=targets)
        writer.writeheader()
        writer.writerows(accepted)
    (out / "rejected.json").write_text(json.dumps(rejected, indent=2), encoding="utf-8")
    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    hashes = {
        name: hashlib.sha256((out / name).read_bytes()).hexdigest()
        for name in ("normalized.csv", "rejected.json", "report.json")
    }
    # Consumers require this last-written marker and verify its content hashes.
    (out / "manifest.json").write_text(json.dumps({"files": hashes}, indent=2), encoding="utf-8")
    return report
