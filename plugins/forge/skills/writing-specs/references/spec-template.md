# Structured Spec Template

Use this exact `forge/spec@1` shape for `docs/specs/NNN-<slug>/spec.md`. The restricted frontmatter has exactly eight keys. Values are a scalar or a JSON-compatible one-line collection; YAML anchors, tags, block scalars, aliases, implicit dates, and additional keys are forbidden.

## Language rules

- Keep the six canonical `##` headings below exactly as written. Localize ordinary prose and labels.
- Preserve R/AC IDs, lifecycle values, history tags, code identifiers, commands, and established technical names.
- Use EARS as a semantic discipline in the user's language. Every AC states a precondition, action, and observable outcome.

## Lifecycle

The frontmatter `status` field moves `draft → approved → implemented`. Only explicit user approval sets `approved`; only `verifying-work` sets `implemented` after every AC passes. Any body, metadata, or status edit is incomplete until repository validation and the matching Spec Pages build/check transaction pass.

## Template

````markdown
---
schema: forge/spec@1
id: NNN-<slug>
status: draft
language: ko
kind: <feature|system|interface|policy>
areas: ["<area>"]
components: ["<component>"]
relatedSpecs: []
---
# <사용자 언어의 기능 이름>

## Overview

<목적과 범위. 일반적인 설명은 사용자의 언어로 쓴다.>

<비목표 레이블>:
- <의도적으로 포함하지 않는 범위>

## Requirements

<R은 Requirement이며 필요한 동작 또는 제약이라는 짧은 설명.>

- R1. <조건 또는 사건과 필요한 시스템 동작>
- R2. <예외 조건과 필요한 응답>

## Behavior & Flows

<source-owned Mermaid 또는 동작 설명. 다이어그램 밖 의미를 추론하지 않는다.>

## Data & Interfaces

<entity, field, API, event 계약. 식별자는 원문을 보존한다.>

## Acceptance Criteria

<AC는 Acceptance Criterion이며 인용한 요구사항을 만족하는 관찰 가능한 증거라는 짧은 설명.>

- AC1 (R1): <선행조건, 행동, 관찰 가능한 결과>

## Decisions & History

<append-only 결정 기록.>

- YYYY-MM-DD [DECISION] <결정과 이유>
````

## Frontmatter fields

| Field | Contract |
|---|---|
| `schema` | exact `forge/spec@1` |
| `id` | exact containing directory name |
| `status` | `draft`, `approved`, or `implemented` |
| `language` | v1 supports `en` or `ko` |
| `kind` | exact enum `feature`, `system`, `interface`, or `policy` |
| `areas` | JSON string array |
| `components` | JSON string array |
| `relatedSpecs` | JSON object array with explicit typed relations |

## Traceability rules

- IDs are ordered, unique, and never renumbered or reused.
- Removed requirements remain as `REMOVED — <reason>` tombstones.
- Every active R is covered by at least one AC. Every AC cites existing active R IDs.
- `approved` and `implemented` history is append-only when compared with the explicit Git baseline.
- `[NEEDS CLARIFICATION: ...]` is allowed only while `status` is `draft`.

## History tags

Use `[DECISION]`, `[CLARIFIED]`, `[CHANGE]`, `[DRIFT]`, and `[REJECTED]`. Record added, modified, or removed requirement IDs without renumbering prior IDs.
