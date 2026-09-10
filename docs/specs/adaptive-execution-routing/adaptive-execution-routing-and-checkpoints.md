---
schema: forge/spec@3
role: root
status: approved
language: ko
kind: policy
areas: ["forge","execution"]
components: ["executing-plans","adaptive-routing"]
relatedSpecs: []
---

# 적응형 실행 라우팅과 Checkpoint

## Documents

- root: [적응형 실행 라우팅과 Checkpoint](adaptive-execution-routing-and-checkpoints.md)

## Overview

실행 방식은 현재 작업과 앱의 기능에 맞춰 선택한다. 공통 tier 점수, 고정 인원, 태스크마다의 정형 원장 대신 독립성·검증·권한·복구 필요를 판단한다.

## Requirements

### Forge는 작업 독립성, 문맥 전달 비용, 검증 가능성과 사용자 설정을 고려해 실행 주체를 선택해야 한다.

### 모델 선택과 동시 실행 수는 현재 플랫폼 기능과 사용자 권한·설정을 따르고 고정 tier나 인원 상한을 추가하지 않아야 한다.

### 병렬 작업은 의존성과 쓰기 소유권의 충돌을 해소하고 각 결과와 통합의 검증 방법을 갖춰야 한다.

### Root는 위임 결과와 실제 증거를 검토하고 현재 통합 상태에 적용되는 검증을 바탕으로 완료를 판단해야 한다.

### 진행 기록은 기존 계획이나 앱 기록을 재사용하고 재개에 필요한 결과·증거·미해결 선택만 보존해야 한다.

### Agent는 승인된 안전한 작업을 계속하고 새로운 사용자 선택이나 권한 밖 효과에 의존하는 행동만 중단해야 한다.

### 반복 시도가 새 증거를 만들지 못하면 가설과 방법을 재검토하고 확인되지 않은 결과를 완료로 보고하지 않아야 한다.

### Visual Docs는 사용자 요청이 있을 때만 생성하거나 갱신하며 실행 기록이나 정본을 대체하지 않아야 한다.

## Decisions & History

- 2026-09-10 [CURRENT] 위임은 조정 비용보다 이득이 있을 때 사용한다. 현재 상태에 적용되는 증거를 재사용하며 상세 route 기록과 모델 등급은 필요한 작업에서만 선택한다.
