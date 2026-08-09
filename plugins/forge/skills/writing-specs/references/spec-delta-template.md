# Spec Delta Template

A Spec Delta is a non-authoritative approval proposal for a new or changed Canonical Spec Bundle. Keep it in the conversation or at `.forge/work/<work-id>/spec-delta.md`. It never replaces the current approved or implemented bundle before explicit approval and a passing writer transaction.

Use the user's language for human-readable content. Preserve bundle and member paths, exact Requirement and Acceptance headings, lifecycle tokens, code identifiers, commands, protocol values, and exact user-facing copy.

```markdown
# Spec Delta: <bundle path or new bundle title>

Baseline:
- bundle path: <existing normalized bundle directory path, or `new`>
- bundle SHA-256: <existing inspect hash, or `new`>
- lifecycle: <approved|implemented|new>

## Goal

<The durable project authority this proposal adds or changes.>

## Scope

- <Links to affected Requirement and Acceptance headings, or the complete new bundle.>

## Out of Scope

- <Contracts and execution details this proposal does not change.>

## Proposed Contract Changes

- MODIFIED: [<exact statement heading>](<member-path>#<exact-anchor>) → <Exact intended meaning after approval.>
- ADDED: `<member-path>` → `### <complete statement heading>`
- REMOVED: [<exact statement heading>](<member-path>#<exact-anchor>) → <Reason retained in the proposal, Git history, or validated transition evidence.>
- MOVED: `<old-member-path>` → `<new-member-path>` with unchanged statement text.
- CURRENT DECISION: <How the active bundle states the adopted contract after approval.>

For a new Canonical Spec, include the complete proposed `forge/spec@3` bundle here. Show the bundle directory, every descriptive filename, and the full Markdown content of every member with lifecycle `status: approved` in the root.

## Done Checks

- The user explicitly approves this exact proposal.
- The baseline bundle SHA-256 still matches immediately before application.
- The approved meaning is applied without extra semantic changes.
- Every acceptance-to-requirement link resolves by exact member path, heading text, and anchor.
- Repository Markdown validation passes before implementation handoff.
```

Do not use `Requirements` or `Acceptance Criteria` as Spec Delta headings. Those headings carry normative authority only inside a Canonical Spec Bundle. Links to affected full statements do not grant the Delta authority.
