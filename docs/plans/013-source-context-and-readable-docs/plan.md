# 작업 컨텍스트와 사람용 설명의 첫 적용

Status: complete

**Related Specs:**
- bundle: docs/specs/task-context-and-readable-documents/

**Goal:** 같은 원문으로 AI가 출처 추적 기능을 사용할 수 있고 사람이 기능의 범위와 한계를 이해할 수 있는 첫 사례를 구현하고 검증한다.

**Approach:** 선택형 source snapshot 도구를 구현하고, 내용 중심 작성·읽기 지침을 연결하며, 별도 작업자와 독자로 평가한다. 이전 턴의 시각 템플릿 삭제 변경안을 이어받는다.

## 범위

고정 renderer는 복구하지 않는다. 기존 forge/spec@3와 저장형 Plan parser는 유지한다. 출처·변경 확인을 화면과 분리하고 일반 Markdown·코드도 읽는다. 배포·설치본 갱신·push는 포함하지 않는다.

### Task 1: 목적과 출처 추적의 계약을 명확히 한다

Governing statements:

- [Forge는 하나의 원문에서 작업 컨텍스트와 독자 설명을 제공해야 한다.](../../specs/task-context-and-readable-documents/task-context-and-readable-documents.md#forge는-하나의-원문에서-작업-컨텍스트와-독자-설명을-제공해야-한다)

- [x] **Step 1: 사용자 승인 범위를 정본에 기록하고 기존 삭제 변경안과의 관계를 명시한다.**
- [x] **Step 2: 정본과 관련 계약을 validate한다.**

### Task 2: 표현 형식에 독립적인 원문 수집과 변경 확인을 구현한다

Governing statements:

- [선택형 컨텍스트 도구는 문서 형식에 의존하지 않고 선택한 원문과 변경 근거를 보존해야 한다.](../../specs/task-context-and-readable-documents/task-context-and-readable-documents.md#선택형-컨텍스트-도구는-문서-형식에-의존하지-않고-선택한-원문과-변경-근거를-보존해야-한다)
- [원문 변경 검사는 선택한 파일과 산출물의 변경 여부만 판단하고 내용을 갱신하지 않아야 한다.](../../specs/task-context-and-readable-documents/task-context-and-readable-documents.md#원문-변경-검사는-선택한-파일과-산출물의-변경-여부만-판단하고-내용을-갱신하지-않아야-한다)

- [x] **Step 1: readonly capture·check와 의미 있는 경계·변경 회귀를 구현한다.**
- [x] **Step 2: 설치본에서도 같은 입력을 수집하고 변경을 확인할 수 있는지 검증한다.**

### Task 3: 필요한 컨텍스트와 읽기 쉬운 설명을 만드는 지침을 연결한다

Governing statements:

- [작업 컨텍스트는 목표에 관련된 조건과 예외를 포함하고 필요한 원문으로 확장할 수 있어야 한다.](../../specs/task-context-and-readable-documents/task-context-and-readable-documents.md#작업-컨텍스트는-목표에-관련된-조건과-예외를-포함하고-필요한-원문으로-확장할-수-있어야-한다)
- [문서 품질은 독자의 이해와 작업 결과로 검증해야 한다.](../../specs/task-context-and-readable-documents/task-context-and-readable-documents.md#문서-품질은-독자의-이해와-작업-결과로-검증해야-한다)

- [x] **Step 1: 작성·실행·시각화·검증 지침을 내용과 소비자 중심으로 연결한다.**
- [x] **Step 2: 실제 기능의 사람용 설명을 작성하고 별도 작업·읽기 평가를 수행한다.**
- [x] **Step 3: 파서·설치 회귀와 repository validation을 확인하고 결과를 기록한다.**

## 복구와 완료 근거

변경은 현재 작업 트리에서 검토하고 필요한 경우 해당 diff만 복원한다. 이전 턴의 삭제 변경안과 사용자 파일을 전체 reset하지 않는다. 같은 근거가 유지되는 검사는 재사용한다. 별도 agent 실행, 테스트 결과와 한계는 docs/evidence에 보존한다.

완료 근거는 [첫 적용 검증](../../evidence/2026-09-21-context-and-reader-pilot.md)에 기록했다. 새 helper의 13개 검사와 기존 66개 parser 검사가 통과했고 세 agent용 격리 설치에서도 동작했다. 별도 구현 작업자, 설명 독자와 스펙·계획 작성자 평가를 수행했다. 기존 schema 전체 이관과 배포는 완료 범위가 아니다.
