---
schema: forge/spec@2
id: 001-valid-feature
status: approved
language: en
kind: system
areas: ["forge"]
components: ["spec-docs"]
relatedSpecs: [{"id":"002-implemented-context","relation":"dependsOn"}]
---
# 001-valid-feature

## Overview

Repository validator fixture.

## Requirements

- R1. The system validates repository contracts.
- R2. The system preserves deterministic results.

## Behavior & Flows

```mermaid
flowchart TD
    A[Input] --> B[Validate]
```

## Data & Interfaces

See [implemented context](../002-implemented-context/spec.md).

`[inline code is not a link](missing-inline.md)`

```text
[fenced example is not a link](missing-fence.md)
```

## Acceptance Criteria

- AC1 (R1–R2): Validation returns deterministic evidence.

## Decisions & History

- 2026-08-01 [DECISION] baseline decision.
