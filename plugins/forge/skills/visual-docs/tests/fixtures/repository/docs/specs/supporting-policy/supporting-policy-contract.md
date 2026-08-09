---
schema: forge/spec@3
role: root
status: implemented
language: en
kind: policy
areas: ["forge"]
components: ["visual-docs"]
relatedSpecs: []
---
# Supporting Policy Contract

## Documents

- root: [Supporting Policy Contract](supporting-policy-contract.md)

## Requirements

### Review inputs remain inside the repository

Review source paths cannot escape the selected repository.

## Acceptance Criteria

### Repository-contained review inputs load successfully

Verifies:

- [Review inputs remain inside the repository](supporting-policy-contract.md#review-inputs-remain-inside-the-repository)

## Decisions & History

- 2026-08-09 [CURRENT] Repository containment is enforced before source loading.
