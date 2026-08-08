# Spec Delta Template

A Spec Delta is a non-authoritative approval proposal for a new or changed Canonical Spec. Keep it in the conversation or at `.forge/work/<work-id>/spec-delta.md`. It never replaces the current approved or implemented source before explicit approval and a passing writer transaction.

Use the user's language for human-readable content. Preserve Canonical Spec IDs, R and AC IDs, lifecycle tokens, code identifiers, commands, protocol values, and exact user-facing copy.

```markdown
# <Canonical Spec ID> Spec Delta

Baseline:
- path: <existing Canonical Spec path, or `new`>
- source SHA-256: <existing inspect hash, or `new`>
- lifecycle: <approved|implemented|new>

## Goal

<The durable project authority this proposal adds or changes.>

## Scope

- <Affected R and AC IDs, or the identity of the complete new Canonical Spec.>

## Out of Scope

- <Contracts and execution details this proposal does not change.>

## Proposed Contract Changes

- MODIFIED Rn: <Exact intended meaning after approval.>
- ADDED Rn: <Exact intended meaning after approval.>
- REMOVED Rn: <Tombstone reason.>
- MODIFIED ACn: <Precondition, action, and observable outcome.>
- HISTORY: <Proposed dated change entry.>

For a new Canonical Spec, include the complete proposed `forge/spec@2` Markdown here with lifecycle `status: approved`.

## Done Checks

- The user explicitly approves this exact proposal.
- The baseline SHA-256 still matches immediately before application.
- The approved meaning is applied to the Canonical Spec without extra semantic changes.
- Repository Markdown validation passes before implementation handoff.
```

Do not use `Requirements` or `Acceptance Criteria` as Spec Delta headings. Those headings carry normative authority only inside a Canonical Spec. Referring to affected R and AC IDs does not grant the Delta authority.
