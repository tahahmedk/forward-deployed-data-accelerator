# ADR-001: Validation defines the trust boundary
Status: accepted.

A report of errors is insufficient if downstream consumers still receive invalid rows.
The pipeline emits separate accepted and rejected artifacts. Every participant in a
duplicate-key group is rejected to avoid file-order-based authority decisions.

Fuzzy mappings are proposals only. All canonical fields need an explicit override or a
unique normalized exact match before any row is trusted. Unknown configurations fail
rather than silently disabling checks.

Outputs use a fresh directory and a final hash manifest. Readers verify the manifest
before ingestion. This avoids stale output reuse and detects incomplete writes without
pretending multiple files form a filesystem transaction. Production object-store
publication needs conditional writes, retention policy and a durable delivery registry.
