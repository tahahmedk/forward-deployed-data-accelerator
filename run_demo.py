import json
from pathlib import Path
from uuid import uuid4

from fde_accel.pipeline import run

if __name__ == "__main__":
    base = Path(__file__).parent
    report = run(
        base / "examples/acme/input.csv",
        base / "contracts/customer.json",
        base / "examples/acme/config.json",
        base / "out" / uuid4().hex,
    )
    print(
        json.dumps(
            {k: report[k] for k in ("records", "accepted", "rejected", "status", "schema_drift")},
            indent=2,
        )
    )
