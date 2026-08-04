---
schema: forge/spec@2
id: 001-valid-ko
status: draft
language: ko
kind: system
subtype: API Viewer
areas: ["forge"]
components: ["spec-model"]
relatedSpecs: []
---
# 잘못된 subtype 스펙

## Requirements

- R1. subtype은 lowercase kebab-case여야 한다.

## Acceptance Criteria

- AC1 (R1): 공백과 대문자가 있는 subtype을 읽으면 진단을 반환한다.

## Decisions & History

- 2026-08-04 [DECISION] invalid subtype fixture를 추가했다.
