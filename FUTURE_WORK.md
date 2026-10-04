# Future work

The next improvements should make the integration handoff more defensible. None of
these capabilities is implemented yet.

## 1. Version contracts and mapping approval

Record contract versions and the source/target assumptions behind approved overrides.
Define which changes are compatible and which invalidate previous approval.

Done when a renamed field, changed business grain or altered domain produces a clear
review decision, and a historical delivery can be reproduced against its original
contract and mapping revision.

## 2. Stream larger deliveries without weakening validation

Profile and validate in bounded chunks, using a disk-backed uniqueness index to find
duplicate keys across chunks. Preserve the rule that all duplicate participants are
quarantined rather than allowing the first chunk to win.

Done when peak memory stays bounded and adversarial cross-chunk duplicate tests produce
the same accepted/rejected decisions as the current batch implementation.

## 3. Publish immutable deliveries to object storage

Introduce a storage adapter and publish a final manifest with conditional creation.
Treat interruption, concurrent publication and reader hash verification as part of
the contract.

Done when failure-injection tests show that consumers cannot mistake a partial upload
for a completed delivery and a retry cannot overwrite an approved version.
