# Local validation evidence

Validated on 2026-09-28 with Python 3.12.14 on Windows.

- `python -m pytest -q`: **21 passed**.
- `python -m ruff check .`: passed.
- `python -m ruff format --check .`: passed.
- Representative demo: passed, producing one accepted and three rejected records.
- Package wheel build and contents inspection: passed.
- CI YAML parsing and local Markdown link checks: passed.

Dependency versions used for the suite are recorded in `requirements-dev.lock.txt`.
The CI matrix also targets Python 3.11 and 3.13; local validation alone does not
establish those results. This evidence is not a throughput, availability or production
deployment claim.
