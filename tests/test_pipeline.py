import csv
import json
from pathlib import Path

import pytest

from fde_accel.mapping import build_mapping
from fde_accel.pipeline import load_source, run
from fde_accel.schema import profile_rows

BASE = Path(__file__).parents[1]


def demo(out):
    return run(
        BASE / "examples/acme/input.csv",
        BASE / "contracts/customer.json",
        BASE / "examples/acme/config.json",
        out,
    )


def test_invalid_records_never_reach_trusted_output(tmp_path):
    report = demo(tmp_path / "run")
    assert (report["records"], report["accepted"], report["rejected"]) == (4, 1, 3)
    with (tmp_path / "run/normalized.csv").open() as stream:
        assert [r["customer_id"] for r in csv.DictReader(stream)] == ["1001"]
    assert len(json.loads((tmp_path / "run/rejected.json").read_text())) == 3
    assert (tmp_path / "run/manifest.json").exists()


def test_outputs_deterministic_and_never_overwritten(tmp_path):
    assert demo(tmp_path / "a") == demo(tmp_path / "b")
    for path in (tmp_path / "a").iterdir():
        assert path.read_bytes() == (tmp_path / "b" / path.name).read_bytes()
    with pytest.raises(FileExistsError):
        demo(tmp_path / "a")


@pytest.mark.parametrize("text", ["a,a\n1,2\n", "a,b\n1\n", "a,b\n1,2,3\n", ""])
def test_malformed_csv_fails_before_publication(tmp_path, text):
    source = tmp_path / "bad.csv"
    source.write_text(text)
    with pytest.raises(ValueError):
        load_source(source)


def test_json_and_mixed_types(tmp_path):
    source = tmp_path / "source.json"
    source.write_text('[{"id": 1, "v": null}, {"id": "x", "v": true}]')
    fields, rows = load_source(source)
    assert fields == ["id", "v"]
    assert profile_rows(rows)[0].inferred_type == "mixed"


def test_fuzzy_mapping_blocks_publication(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text("customerid,name\n1,A\n")
    contract = tmp_path / "contract.json"
    contract.write_text(
        json.dumps(
            {
                "fields": [{"name": "customer_id"}, {"name": "customer_name"}],
                "quality": {"required": ["customer_id"]},
            }
        )
    )
    config = tmp_path / "config.json"
    config.write_text("{}")
    report = run(source, contract, config, tmp_path / "run")
    assert report["status"] == "BLOCKED"
    assert report["accepted"] == 0


def test_override_validation_and_ambiguity():
    with pytest.raises(ValueError):
        build_mapping(["a"], ["id"], {"missing": "id"})
    with pytest.raises(ValueError):
        build_mapping(["a", "b"], ["id"], {"a": "id", "b": "id"})
    assert build_mapping(["user_id", "User ID"], ["userid"])[0].method == "ambiguous"


def test_empty_header_only_csv_retains_schema(tmp_path):
    source = tmp_path / "empty.csv"
    source.write_text("a,b\n")
    assert load_source(source) == (["a", "b"], [])
