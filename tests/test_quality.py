from fde_accel.quality import evaluate


def test_rejects_all_duplicate_participants():
    rows = [{"id": "1", "status": "active"}, {"id": "1", "status": "paused"}]
    issues = evaluate(rows, ["id"], ["id"], {"status": ["active", "inactive"]})
    assert len(issues) == 3
    assert {i.row for i in issues if i.rule == "unique"} == {1, 2}


def test_required_whitespace_and_format_failures():
    issues = evaluate(
        [{"id": " ", "email": "invalid", "date": "2026-02-30"}],
        ["id"],
        [],
        {},
        {"email": "email", "date": "date"},
    )
    assert {i.rule for i in issues} == {"required", "format"}
