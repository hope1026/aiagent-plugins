# AI Workflow Orchestrator Design

**Date:** 2026-03-20
**Status:** Approved for planning
**Scope:** V1 product design for a local multi-project AI workflow orchestrator

## Overview

이 문서는 AI 에이전트를 이용해 개발 워크플로우를 진행하고, 그 진행 상태와 리뷰 사유, 변경 이유, 검증 근거를 시각적으로 추적할 수 있는 로컬 웹앱의 V1 설계를 정의한다.

V1의 우선순위는 범용 에이전트 플랫폼이 아니라 `workflow orchestrator first`이다. 즉, 핵심은 다음이다.

- 여러 로컬 프로젝트를 하나의 웹앱에서 관리
- `brief -> plan -> phase execution -> verification -> review -> reference sync` 흐름을 상태 머신으로 관리
- 각 단계의 근거, diff, preview, 리뷰 사유, 재계획 사유를 남김
- `Claude`, `Codex`, `Gemini`를 공통 실행 계층으로 감쌈
- 작업 완료 후 프로젝트의 정본 문서인 `reference`를 업데이트해 구현된 사실을 장기적으로 축적

## Product Goals

- AI 기반 개발 워크플로우를 단계별로 시각화한다.
- phase/task 단위 진행과 검증 gate를 관리한다.
- 리뷰와 수정의 이유를 구조적으로 기록한다.
- 코드 diff, 문서 diff, 이미지 preview, 테스트 evidence를 함께 보여준다.
- 작업 완료 시 프로젝트의 구현된 사실이 `.weppy/reference/`에 반영되도록 강제한다.
- 자동 진행 모드에서도 사용자가 반드시 알아야 할 사건을 놓치지 않게 한다.

## Non-Goals For V1

- 범용 노드 기반 자동화 빌더
- 중앙 서버 기반 팀 런타임
- 완전한 SaaS형 멀티 유저 권한 시스템
- 모든 외부 메신저에서 동등한 승인 UX 제공
- 모든 에이전트의 장기 세션을 완전하게 통합하는 범용 런타임

## Product Model

이 제품은 `멀티 프로젝트 로컬 웹앱`이다.

- 웹 UI는 브라우저에서 동작한다.
- 실제 workflow orchestration은 로컬 컨트롤 플레인 프로세스가 담당한다.
- 각 프로젝트는 로컬 레포 단위로 등록된다.
- 실제 코드 변경은 프로젝트 설정에 따라 `worktree/branch 격리` 또는 `현재 working tree 직접 수정`으로 수행된다.

## Planning Assumptions

구현 계획이 분산되지 않도록, V1 계획 수립 전 다음 가정을 고정한다.

- 런타임 스택은 `TypeScript` 기준으로 통일한다.
- 로컬 컨트롤 플레인은 `Node.js` 기반 백엔드 서비스로 둔다.
- 웹 UI는 별도 프론트엔드에서 로컬 컨트롤 플레인에 연결된다.
- V1의 에이전트 실행 기본값은 `ephemeral subprocess run`이다.
- 초기 adapter는 `Claude`, `Codex`, `Gemini`를 모두 지원하되, 공통 보장 범위는 `prompt/context injection`, `stdout/stderr capture`, `exit status`, `artifact attachment`까지로 제한한다.
- V1의 preview 범위는 `code`, `markdown`, `image`, `saved test/report artifacts`까지다.
- Slack과 Discord는 V1에서 `알림 + deep link` 중심으로 지원한다.
- reference dedup 검사는 V1에서 `ownership rule 검사`, `명시적 참조 검사`, `단순 중복 경고` 수준으로 제한한다.
- 프로젝트 레포 내부 `.weppy/`가 소스 오브 트루스이며, 앱 내부 저장소는 재생성 가능한 read model/cache만 담당한다.

## First Shippable Slice

첫 구현 계획은 아래 범위만을 대상으로 한다.

- 멀티 프로젝트 레지스트리와 프로젝트 전환
- `.weppy/workflows/` 및 `.weppy/reference/` 문서 모델
- `brief -> plan -> execution -> verification -> review -> reference sync` 상태 머신
- `Overview`, `Brief`, `Plan`, `Progress`, `Review`, `Diff`, `Reference` 탭
- `Codex`, `Claude`, `Gemini`의 ephemeral adapter
- 코드, 문서, 이미지, artifact preview
- review reason, retry, replan, rebrief, reference sync 타임라인
- in-app attention center
- Slack/Discord outbound notification and deep link

다음 항목은 첫 출하 범위에서 제외한다.

- session-backed long-running agent context
- 메신저 안에서의 완전한 승인 처리 UX
- 실시간 live browser preview 생성
- 완전 자동 semantic reference dedup
- 팀/서버 멀티유저 권한 시스템

## Core Concepts

### Brief

특정 workflow를 수행하기 위한 작업 문서다. 이번 변경의 목적, 범위, 완료 조건, 설계 방향, 디자인 메모를 담는다.

### Plan

brief를 실행 가능한 phase/task/gate 구조로 분해한 실행 문서다. 검증 조건, 되감기 정책, reviewer 구성을 포함한다.

### Reference

프로젝트에서 실제로 구현되어 확정된 내용을 기록하는 정본 문서군이다. 작업 종료 시 갱신되어야 하며, 프로젝트의 장기 지식 베이스 역할을 한다.

### Workflow

brief, plan, execution, review, verification, reference sync를 묶는 작업 단위다.

### Phase / Task

workflow를 실행 가능한 단위로 나눈 구조다. phase는 검증 gate를 가진 상위 단위이고, task는 구체 작업 단위다.

### Evidence

테스트 로그, 이미지, preview, review 결과, diff, 산출물 요약 등 완료를 증명하는 근거 묶음이다.

## Repository Layout

각 프로젝트 레포의 소스 오브 트루스는 레포 내부 파일이다.

```text
.weppy/
  workflows/
    <workflow-id>/
      workflow.md
      brief.md
      plan.md
      phases/
        phase-01-*.md
      tasks/
        task-001-*.md
      reviews/
        review-<timestamp>-<agent>.md
      events/
        000001-*.json
      evidence/
        test-<timestamp>.log
        preview-<timestamp>.png
      outputs/
        completion-report.md
        final-diff.patch
  reference/
    index.md
    ui/
    behavior/
    api/
    data-contract/
```

## Document Ownership Rules

`reference`는 중복 없는 정본 문서군이어야 한다. 이를 위해 다음 규칙을 둔다.

- 하나의 구현 사실은 하나의 reference 문서만 소유한다.
- `ui/`는 화면 구조와 인터랙션만 소유한다.
- `behavior/`는 상태 머신, 정책, 규칙만 소유한다.
- `api/`는 외부/내부 인터페이스 계약만 소유한다.
- `data-contract/`는 이벤트 스키마, 파일 포맷, payload 구조만 소유한다.
- 다른 문서는 동일한 설명을 반복하지 않고 링크와 참조로 연결한다.

## System Architecture

V1 시스템은 다음 구성요소로 나뉜다.

### Project Registry

- 등록된 로컬 프로젝트 목록 관리
- 프로젝트별 실행 정책, 알림 정책, 에이전트 설정 관리

### Workflow Engine

- workflow 상태 머신 실행
- phase/task 스케줄링
- verification gate 관리
- retry, replan, rebrief, reference sync 흐름 관리

### Agent Adapter Layer

- `Claude`, `Codex`, `Gemini` 실행 인터페이스 표준화
- 실행 역할별 context pack 구성
- 결과를 공통 이벤트 형식으로 정규화

### Repo Bridge

- worktree/branch 생성 및 정리
- 파일 변경 감시
- git diff 수집
- 테스트 실행
- artifact 저장

### Review Engine

- brief review, plan review, phase review, final review, reference review 실행
- reviewer 조합 관리
- 반려 사유와 수정 요구 구조화

### Canonical Reference Manager

- 구현 완료 후 영향받는 reference 문서 계산
- reference 갱신 초안 생성
- ownership과 dedup 검증 수행

### UI Read Model

- 이벤트와 문서를 화면용 모델로 재구성
- 실시간 진행, attention, diff, review timeline 구성

## Workflow State Machine

기본 상태는 다음과 같다.

- `Draft Brief`
- `Brief Review`
- `Brief Approved`
- `Draft Plan`
- `Plan Review`
- `Plan Approved`
- `Phase In Progress`
- `Phase Verification`
- `Phase Review`
- `Implementation Approved`
- `Reference Sync`
- `Reference Review`
- `Completed`

### Failure Classification

실패는 한 가지로 취급하지 않고 원인을 분류한다.

- `implementation_gap`
  현재 plan은 맞지만 구현이 부족함
- `plan_gap`
  plan이 완료 조건을 충분히 커버하지 못함
- `brief_gap`
  brief의 목표나 완료 조건이 잘못 정의됨
- `reference_gap`
  구현은 맞지만 reference 구조나 분리가 잘못됨
- `environment_gap`
  테스트 환경이나 실행 환경 문제

### Rewind Rules

- `implementation_gap` -> 현재 phase/task 재작업
- `plan_gap` -> `Draft Plan`으로 되감기
- `brief_gap` -> `Draft Brief`로 되감기
- `reference_gap` -> `Reference Sync` 재실행
- `environment_gap` -> 같은 단계에서 환경 수정 후 재실행

### Workflow Policies

프로젝트 또는 workflow별로 다음 정책을 가질 수 있다.

- `on_phase_gate_fail`
- `on_final_gate_fail`
- `max_task_retries`
- `max_phase_retries`
- `auto_escalate_to_replan_after`
- `auto_escalate_to_rebrief_when_acceptance_conflict`

## Reviews

리뷰는 상태별로 역할이 다르다.

### Brief Review

- 목표와 범위가 명확한지 검토
- acceptance criteria가 측정 가능한지 검토
- 디자인 의도와 구현 범위가 맞는지 검토

### Plan Review

- brief의 acceptance criteria가 phase gate에 매핑되는지 검토
- 테스트와 검증 조건이 충분한지 검토
- retry와 escalation 규칙이 타당한지 검토
- reviewer와 agent 조합이 타당한지 검토

### Phase Review

- 해당 phase 목표 달성 여부 검토
- 산출물과 evidence 검토
- 다음 phase로 진행 가능한지 검토

### Final Review

- 전체 brief acceptance criteria 충족 여부 검토
- 남은 리스크 및 누락 검토

### Reference Review

- `.weppy/reference/` 문서가 실제 구현과 일치하는지 검토
- ownership과 dedup 규칙 위반 여부 검토

## UI Information Architecture

V1은 다음 탭을 제공한다.

### Overview

- 현재 workflow 상태
- 활성 phase/task
- retry/replan/rebrief 횟수
- pending approvals
- must-see attention
- recent reference updates

### Brief

- `brief.md`
- brief review 결과
- 디자인 메모 및 acceptance criteria

### Plan

- `plan.md`
- phase/task 구조
- verification gate
- retry/escalation 정책
- plan review 결과
- plan revision diff

### Progress

- 현재 phase/task
- agent 실행 로그
- 테스트 진행 상태
- evidence 생성 현황
- 상태 전이 타임라인

### Review

- brief review
- plan review
- phase review
- final review
- reference review
- 반려 사유와 수정 이유 타임라인

### Diff

- code diff
- doc diff
- visual diff
- semantic change summary

### Reference

- `.weppy/reference/` 문서 탐색
- ownership 보기
- 이번 workflow가 변경한 reference 하이라이트
- 관련 code diff, review reason 링크

## Attention And Approval Model

workflow는 사람의 개입 방식을 정책으로 가진다.

- `approval_mode`: `manual | mixed | automatic`
- `approval_channels`: `in_app | slack | discord`
- `blocking_rules`
- `attention_rules`
- `digest_policy`

### Blocking Approval

사용자 응답 전까지 workflow를 멈춘다.

예시:

- 파괴적 명령
- 격리 전략 변경
- 대규모 reference 재구성
- 최종 완료 승인

### Non-blocking Attention

workflow는 계속 진행하지만 사용자가 나중에 꼭 확인해야 한다.

예시:

- 자동 replan 발생
- reviewer disagreement
- 큰 visual change
- reference ownership conflict가 자동 해소됨
- 실패 후 자동 복구됨

### Attention Center

자동 진행 모드에서도 사용자가 반드시 확인해야 하는 사건을 모아두는 UI를 제공한다.

V1에서는 채널별 기능 차이를 줄이기 위해 승인 처리의 최종 권한은 앱 내부에 둔다. Slack과 Discord는 우선 `알림 + deep link` 채널로 취급하고, 메신저 내부 승인 플로우는 후속 범위로 둔다.

## Agent Execution Model

V1은 에이전트를 직접 노출하기보다 공통 실행 모델로 감싼다.

### Agent Adapter

- `Claude`
- `Codex`
- `Gemini`

### Run Profile

실행 목적별 프로파일:

- `brief-writer`
- `plan-writer`
- `implementer`
- `test-runner`
- `brief-reviewer`
- `plan-reviewer`
- `phase-reviewer`
- `final-reviewer`
- `reference-syncer`
- `reference-reviewer`

### Context Pack

실행에 필요한 파일과 근거 묶음:

- brief
- plan
- selected source files
- git diff
- screenshots
- logs
- reference docs
- project settings

### Output Normalization

에이전트별 결과를 다음 공통 형식으로 정규화한다.

- `summary`
- `artifacts`
- `proposed_changes`
- `reason_codes`
- `review_decision`
- `required_human_attention`
- `raw_transcript_ref`

## Skill Injection Model

스킬 주입은 혼합형으로 지원한다.

우선순위는 다음과 같다.

1. `execution override`
2. `project-local instructions and skills`
3. `app-shared skill packs`
4. `base adapter prompts`

스킬 메타데이터는 최소한 다음 속성을 가진다.

- `scope`
- `intent`
- `safety_level`
- `agent_compatibility`
- `assets`

목표는 내부적으로 하나의 `Unified Skill Graph`를 구성하고, 실행 직전에 각 에이전트 형식으로 컴파일하는 것이다.

## Verification Model

완료 판단은 `worked`가 아니라 `proved` 기준으로 한다.

각 phase와 최종 완료에는 `Verification Bundle`이 필요하다.

### Verification Bundle

- test evidence
- review evidence
- diff evidence
- preview evidence
- completion evidence

### Required Completion Conditions

- brief acceptance criteria 충족
- 모든 required phase gate 통과
- final review 승인
- required evidence bundle 존재
- 영향받는 reference 문서 갱신 완료
- reference dedup/ownership 검사 통과
- required approval/attention 처리 완료
- completion report 생성 완료

하나라도 비어 있으면 `Completed`로 가지 않는다.

## Diff And Preview Model

`Diff` 탭은 단순 patch viewer가 아니라 다음 모드를 지원해야 한다.

- `Code Diff`
- `Doc Diff`
- `Visual Diff`
- `Semantic Summary`

각 핵심 변경 묶음은 가능한 한 변경 이유와 연결되어야 한다.

예시 메타데이터:

- source review
- reason code
- applied by
- validated by
- linked evidence

## Completion Report

workflow 종료 시 `completion-report.md`를 생성한다.

최소 포함 항목:

- workflow 목표
- 실제 변경 사항
- acceptance criteria 충족 여부
- retry/replan/rebrief 이력
- reviewer 요약
- changed files / changed reference docs
- 핵심 evidence 링크
- 남은 리스크

## External Inspiration And Constraints

설계 방향은 다음 외부 패턴을 참고했다.

- `obra/superpowers`: spec, plan, review, subagent 기반 개발 워크플로우
- `OpenHands`: 로컬/웹 UI 기반 에이전트 작업 관찰 패턴
- OpenAI `Responses API background mode`: 장기 작업 상태 추적 패턴
- Anthropic `Agent SDK`: tool permission, approval callback, project instruction 패턴
- Gemini CLI: project instruction 및 custom command 패턴

이 제품은 위 도구들을 그대로 복제하지 않고, 로컬 멀티 프로젝트 오케스트레이터에 맞게 추상화한다.

## Recommended Planning Boundaries

V1 계획은 다음 순서로 나누는 것이 적절하다.

1. 프로젝트 레지스트리와 `.weppy/` 문서 모델
2. workflow 상태 머신과 이벤트 로그
3. 탭 기반 UI read model
4. diff, review, evidence viewer
5. agent adapter v1
6. reference sync와 dedup 검사
7. approval/attention/notification 통합
