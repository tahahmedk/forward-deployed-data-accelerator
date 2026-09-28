# Integration runbook

1. Use the discovery checklist to establish grain, stable identifiers and domain owner.
2. Work in a restricted staging area. Never add real customer data to this repository.
3. Create a canonical contract and expected-source-field list. Configure explicit semantic
   overrides; a fuzzy similarity score is not business approval.
4. Run into a new output directory. Review report.json: missing columns and unresolved
   mappings block delivery; unexpected columns require review but do not alone reject rows.
5. Review rejected.json with the domain owner. Duplicate identifiers quarantine all
   participants; ask the owner to resolve them rather than choosing the first.
6. Approve mappings in configuration and correct the source. Do not edit normalized.csv
   to bypass the contract. Re-run into a fresh directory and compare counts/fingerprint.
7. Before consuming normalized.csv, require manifest.json and verify its SHA-256 hashes.
   A missing or mismatched manifest means the delivery is incomplete; ignore it and rerun.
8. Gate cutover on the agreed acceptance threshold, not exit code. Document who approves
   review-required deliveries and who owns late/missing files.
9. Set retention and access controls for rejected records and staging files. Diagnostics
   omit values, but quarantine files intentionally retain rejected canonical records.

For replay, reuse the source and configuration in a new directory and compare artifact
bytes. For rollback, point the consumer back to the last approved immutable delivery;
there is no database rollback implementation in this batch toolkit.
