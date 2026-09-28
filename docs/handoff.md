# Synthetic integration handoff

## Scenario and assumptions
An unfamiliar customer supplies a flat customer export. Each row should represent one
customer; customer_id is intended to be stable and unique. These assumptions need domain
owner confirmation before deployment. Blank email is permitted; status is required.
The expected contract accepts ISO calendar dates only.

## Evidence from the fixture
Four source rows, one accepted, three quarantined. Identifier 1002 appears twice, so both
records are rejected. The fourth row has no identifier. One duplicate also has an unknown
status and a non-ISO date. LegacyFlag is unexpected and appears in drift diagnostics.

## Open decisions
- Which source record is authoritative for duplicated identifiers?
- Is a source-system date-format conversion approved, and how is ambiguity handled?
- Does LegacyFlag affect customer lifecycle semantics?
- Is this a snapshot or an incremental delivery? How are deletions represented?

## Acceptance and operational ownership
A proposed first cutover requires zero unresolved mappings, no missing expected columns,
and a domain-owner decision for every rejected record. Those are recommendations for the
synthetic scenario, not a claimed customer agreement. Assign named owners during real
discovery: data steward for semantics, integration owner for deliveries, platform owner
for credentials/retention and incident response. Record the approved contract revision,
source fingerprint, accepted/rejected counts and rollback delivery in the handoff ticket.
