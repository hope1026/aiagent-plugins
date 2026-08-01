---
schema: forge/spec@1
id: 001-valid-ko
status: approved
language: ko
kind: feature
areas: ["forge"]
components: ["spec-model"]
relatedSpecs: []
---
# 구조화 스펙 예제

## Overview

격리된 parser fixture다.

## Requirements

- R1. 시스템은 입력을 검증해야 한다.
- R2. 시스템은 결과를 보존해야 한다.

## Behavior & Flows

```mermaid
flowchart TD
    A[입력] -->>
```

## Data & Interfaces

입력은 UTF-8 Markdown이다.

## Acceptance Criteria

- AC1 (R1–R2): parser가 요구사항과 승인 기준을 보존한다.

## Decisions & History

- 2026-08-01: fixture를 추가했다.
