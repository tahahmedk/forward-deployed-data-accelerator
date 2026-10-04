# ADR-002: Why ambiguous mappings require human approval

Status: accepted

Date: 2026-10-04

## The problem is meaning, not spelling

A field called "client_id" might identify a billing account, a person or a source-system
record. Similar names cannot settle that distinction. A wrong mapping can produce rows
that pass type and uniqueness checks while representing the wrong business entity.

I would rather leave that ambiguity visible in a handoff than turn a plausible guess
into a trusted customer dataset.

## Decision

Fuzzy matches are proposals. An ambiguous, fuzzy or unmapped canonical target blocks
trusted output until someone with domain knowledge approves an explicit mapping in
configuration. Approval is currently a reviewed source-to-target override, not a UI
workflow or an identity-backed approval record.

The reported score measures string similarity. A score of 0.9 does not mean a 90%
probability of semantic correctness; it has not been calibrated against customer labels.
Normalized exact matches are accepted automatically in this implementation, but even
an exact name match still depends on the business-grain assumptions made during discovery.

## Speed versus correctness

This adds a review step and may block an otherwise useful delivery over one unresolved
field. It is deliberately conservative. Silent semantic errors are harder to diagnose
after downstream systems have adopted a dataset than while the source owner is still
available to explain it.

Rejecting every proposal forever is not the goal. Once a mapping has been approved,
the configuration makes repeated delivery deterministic. A new source or a changed
contract should trigger review again rather than inherit approval by accident.

## Where automation helps

Automate profiling, candidate ranking, schema-drift detection and rule evaluation.
Show the reviewer competing candidates and the assumptions that need an answer.
Reuse approved mappings for compatible deliveries, with a versioned contract and
evidence of approval as a future extension.

Automatic acceptance could be appropriate for a tightly controlled source with a
published contract and measured mapping accuracy. The unfamiliar extracts targeted by
this project do not provide that evidence.
