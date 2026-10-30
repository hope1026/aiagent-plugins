# DB and External Request Optimization

Use when implementing, changing, or evaluating a path that reads a database or
calls an external API. Review the affected call path, including its consumers;
unrelated work needs no performance audit, cache layer, or benchmark suite.
Follow the project's owning contracts for freshness, isolation and side effects.

## Reuse reads within a valid scope

Trace calls across helpers and loops. Pass already read and verified data to
consumers explicitly or through request-scoped context instead of fetching it
again in each function. Equivalent concurrent reads may share an in-flight
operation as well as its result.

Identify conditions that affect equivalence: tenant, user, owner, permissions,
environment, provider/account, resource ID, query, version and transaction
context where relevant. An identical ID alone is not a reuse key. Do not turn
failure or an uncertain outcome into success or confirmed absence; a failed
in-flight entry must not silently become a reusable successful result.

Keep read sharing distinct from write idempotency. Equal write arguments can
represent separate intentions. Use the operation's authorized idempotency and
reconciliation contract rather than deduplicating side effects as reads.

## Preserve freshness and atomic protection

After relevant writes, ownership or permission changes, revocation, deletion,
source revalidation, or a transaction boundary, reassess whether earlier
evidence remains valid. Invalidate or reload affected data. Preserve required
before/after checks and reconciliation after a lost acknowledgement.

Current authorization, ownership, revocation, balance and commit conditions
remain protected by the owning contract's fresh checks and atomic guards or
compare-and-set operations. Consolidate reads only when equivalent protection
is demonstrated. Resolve conflicts within the allowed retry budget; do not
blindly repeat a write or external side effect with an unknown outcome.

Extending request-scoped reuse into cross-request caching changes its lifetime
and isolation. Establish authorized expiry, invalidation and isolation rules
through the forge writing-specs skill when this changes a durable contract.
Do not weaken locks, idempotency, required audit, outbox or persistence guarantees
to meet a latency target.

## Bound round trips and total work

Inspect N+1 paths, fields and ranges actually needed, and bulk or batch reads.
Respect binding, page and response-size limits; handle missing items and partial
failures without turning them into normal empty results. Parallelize independent
calls with bounded concurrency. Batching and parallelism are not deduplication;
fewer network round trips do not necessarily mean fewer SQL statements or less
database work.

Propagate the parent request's remaining deadline, cancellation and provider
backoff. Avoid fresh full timeouts and nested retries at each helper. Review
external waits while locks or long transactions are held. Define cancellation
ownership for shared work: one consumer leaving must not incorrectly cancel
other consumers, while parent cancellation still applies to work it owns.

## Prove the claimed improvement

Compare before and after with equivalent inputs, conditions and measurement
boundaries. Distinguish physical DB round trips, SQL statements, external calls,
retry counts and elapsed time. Check growth with item count and affected
concurrent-change, error and cancellation behavior in proportion to the change.
Use existing instrumentation and focused checks where sufficient.

Label partial-path measurements and synthetic delays accurately; neither proves
whole-request production latency. If comparable measurement is unavailable,
report the structural change and unverified performance benefit. Keep raw keys,
tokens and personal data out of instrumentation.
