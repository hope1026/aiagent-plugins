---
schema: forge/spec@3
role: root
status: implemented
language: en
kind: system
areas: ["forge"]
components: ["visual-docs"]
relatedSpecs: []
---
# Review Lifecycle Contract

## Documents

- root: [Review Lifecycle Contract](review-lifecycle-contract.md)

## Requirements

### Review sources preserve their semantic bundle path

The path remains visible while internal hashes are used only for freshness.

## Acceptance Criteria

### Inspecting a review source reports its semantic bundle path

Verifies:

- [Review sources preserve their semantic bundle path](review-lifecycle-contract.md#review-sources-preserve-their-semantic-bundle-path)

## Decisions & History

- 2026-08-09 [CURRENT] The review lifecycle uses bundle paths as human-readable identity.
