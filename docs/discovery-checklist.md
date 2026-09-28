# Customer discovery checklist

## Data contract
- What is the business grain of each record?
- Which identifiers are stable, unique, and durable?
- Which fields are authoritative versus descriptive?
- What is the expected delivery cadence and lateness tolerance?

## Operational reality
- How are files delivered today?
- What happens when a file is late, partial, duplicated, or resent?
- Who can validate ambiguous mappings?
- Which failures should block ingestion versus generate a warning?

## Security and deployment
- Does data contain PII, PHI, financial, or regulated attributes?
- What region and retention constraints apply?
- Which credentials and network paths are available?
- What evidence is required for audit and support?

## Exit criteria
The integration is ready when mapping confidence is understood, required quality checks pass, drift behavior is defined, ownership is documented, and replay/recovery have been tested.
