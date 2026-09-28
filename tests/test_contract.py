import json
from pathlib import Path

import pytest

from fde_accel.pipeline import run, validate_contract


@pytest.mark.parametrize(
    "quality",
    [
        {"required": "id"},
        {"allowed": {"id": "abc"}},
        {"formats": {"id": ["email"]}},
        {"typo": []},
        {"required": ["unknown"]},
    ],
)
def test_bad_rule_shapes_fail(quality):
    with pytest.raises(ValueError):
        validate_contract({"fields": [{"name": "id"}], "quality": quality}, {})


def test_missing_expected_column_blocks_even_with_valid_mapping(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text("id\n1\n")
    contract = tmp_path / "contract.json"
    contract.write_text(json.dumps({"fields": [{"name": "id"}], "quality": {"required": ["id"]}}))
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"expected_source_fields": ["id", "missing"]}))
    report = run(source, contract, config, tmp_path / "out")
    assert report["status"] == "BLOCKED"
    assert report["accepted"] == 0


def test_failed_write_has_no_completion_manifest(tmp_path, monkeypatch):
    base = Path(__file__).parents[1]
    original = Path.write_text

    def fail_report(self, *args, **kwargs):
        if self.name == "report.json":
            raise OSError("synthetic disk failure")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_report)
    with pytest.raises(OSError):
        run(
            base / "examples/acme/input.csv",
            base / "contracts/customer.json",
            base / "examples/acme/config.json",
            tmp_path / "out",
        )
    assert not (tmp_path / "out/manifest.json").exists()
