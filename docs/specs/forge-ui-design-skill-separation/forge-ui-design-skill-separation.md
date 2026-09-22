---
schema: forge/spec@3
role: root
status: approved
language: ko
kind: policy
areas: ["forge","design"]
components: ["using-forge","visual-docs","verifying-work"]
relatedSpecs: [{"path":"docs/specs/review-viewer-lifecycle/","relation":"relatedTo"}]
---

# Forge UI 디자인 스킬 분리

## Documents

- root: [Forge UI 디자인 스킬 분리](forge-ui-design-skill-separation.md)

## Overview

Forge는 범용 디자인 스킬을 기본 패키지에서 분리한다. 시각 방향과 구현은 기존 제품 시스템, 사용자 요구와 사용 가능한 전문 지침에 맡기고, Forge는 계약·작업 진행·결과 검증을 담당한다. 별도 디자인 패키지의 생성이나 설치는 필수 조건이 아니다. 기존 bundle 경로는 소비자 링크를 위해 유지한다.

## Requirements

### Forge는 `web-app-design`, `website-design`과 별도 UI compatibility router를 기본 배포에 포함하지 않아야 한다.

Source, manifest, installer의 신규 배포 결과와 skill catalog를 일치시킨다. 사용자 전역 경로의 기존 개별 설치본은 소유권이 확인되지 않은 채 삭제하지 않는다. 수동 개발 설치의 잔여 사본은 출처를 확인한 뒤 검색 경로 밖에 보관할 수 있도록 안내한다.

### `using-forge`는 UI 작업에 기존 제품 시스템과 사용자가 선택한 사용 가능한 디자인 지침을 활용하고 외부 디자인 스킬 설치를 필수로 요구하지 않아야 한다.

### 요청의 surface는 기존 제품에서 확인하고 결과를 바꾸는 미해결 선택만 질문하며 native mobile·desktop을 web 스킬에 강제 라우팅하지 않아야 한다.

### Forge 원문의 시각화에는 `visual-docs`의 의미 보존 지침을 적용하고 요청한 결과의 UI 변경은 `verifying-work`의 UI 검증 지침으로 확인해야 한다.

일반 도식은 현재 앱 기능을 사용한다. Forge 원문은 의미와 출처를 보존하며 자유롭게 표현한다. Forge 전용 시각 템플릿과 renderer는 요구하지 않는다. HTML이라는 이유만으로 별도 디자인 절차를 요구하지 않는다.

### `verifying-work`는 UI 검증이 필요한 작업에서만 참고 문서를 읽어 상태 보존, 재정렬 복구, 접근성과 실제 렌더링을 영향 범위에 맞게 확인해야 한다.

### 디자인 품질 완료 주장은 영향 범위의 역할 일관성과 계층 구분을 실제 렌더링에서 확인한 증거를 포함해야 한다.

관련 대표 요소, 상태와 viewport에서 가독성·계층·의도된 차이를 확인한다. Computed style이나 폰트 수치는 진단에 필요할 때만 기록하고 담당 작업에서 이미 확보한 증거를 재사용한다.

## Acceptance Criteria

### 세 agent용 격리 설치를 반복하면 제거된 디자인 스킬은 없고 `visual-docs`, `verifying-work`와 UI 검증 참고 문서는 동일하게 배포된다.

검증하는 요구사항:

- [Forge는 `web-app-design`, `website-design`과 별도 UI compatibility router를 기본 배포에 포함하지 않아야 한다.](forge-ui-design-skill-separation.md#forge는-web-app-design-website-design과-별도-ui-compatibility-router를-기본-배포에-포함하지-않아야-한다)

### app·website·native 요청에 외부 디자인 스킬이 없는 경우에도 기존 제품과 사용자 요구를 조사해 작업을 진행하고 불필요한 설치나 디자인 절차를 요구하지 않는다.

검증하는 요구사항:

- [`using-forge`는 UI 작업에 기존 제품 시스템과 사용자가 선택한 사용 가능한 디자인 지침을 활용하고 외부 디자인 스킬 설치를 필수로 요구하지 않아야 한다.](forge-ui-design-skill-separation.md#using-forge는-ui-작업에-기존-제품-시스템과-사용자가-선택한-사용-가능한-디자인-지침을-활용하고-외부-디자인-스킬-설치를-필수로-요구하지-않아야-한다)
- [요청의 surface는 기존 제품에서 확인하고 결과를 바꾸는 미해결 선택만 질문하며 native mobile·desktop을 web 스킬에 강제 라우팅하지 않아야 한다.](forge-ui-design-skill-separation.md#요청의-surface는-기존-제품에서-확인하고-결과를-바꾸는-미해결-선택만-질문하며-native-mobiledesktop을-web-스킬에-강제-라우팅하지-않아야-한다)

### 일반 도식, Forge 원문 설명과 해당 문서의 UI 변경을 처리하면 각각 기본 기능, `visual-docs`의 의미 보존, 영향받는 UI 동작 검증을 적용한다.

검증하는 요구사항:

- [Forge 원문의 시각화에는 `visual-docs`의 의미 보존 지침을 적용하고 요청한 결과의 UI 변경은 `verifying-work`의 UI 검증 지침으로 확인해야 한다.](forge-ui-design-skill-separation.md#forge-원문의-시각화에는-visual-docs의-의미-보존-지침을-적용하고-요청한-결과의-ui-변경은-verifying-work의-ui-검증-지침으로-확인해야-한다)
- [`verifying-work`는 UI 검증이 필요한 작업에서만 참고 문서를 읽어 상태 보존, 재정렬 복구, 접근성과 실제 렌더링을 영향 범위에 맞게 확인해야 한다.](forge-ui-design-skill-separation.md#verifying-work는-ui-검증이-필요한-작업에서만-참고-문서를-읽어-상태-보존-재정렬-복구-접근성과-실제-렌더링을-영향-범위에-맞게-확인해야-한다)

### 국소 UI 수정과 일부 화면만 관찰한 완료 주장을 검토하면 필요한 상태·역할만 확인하고 미관찰 범위를 완료로 보고하지 않는다.

검증하는 요구사항:

- [`verifying-work`는 UI 검증이 필요한 작업에서만 참고 문서를 읽어 상태 보존, 재정렬 복구, 접근성과 실제 렌더링을 영향 범위에 맞게 확인해야 한다.](forge-ui-design-skill-separation.md#verifying-work는-ui-검증이-필요한-작업에서만-참고-문서를-읽어-상태-보존-재정렬-복구-접근성과-실제-렌더링을-영향-범위에-맞게-확인해야-한다)
- [디자인 품질 완료 주장은 영향 범위의 역할 일관성과 계층 구분을 실제 렌더링에서 확인한 증거를 포함해야 한다.](forge-ui-design-skill-separation.md#디자인-품질-완료-주장은-영향-범위의-역할-일관성과-계층-구분을-실제-렌더링에서-확인한-증거를-포함해야-한다)

## Decisions & History

- 2026-09-21 [CURRENT] 범용 디자인 스킬을 기본 배포에서 분리하고 시각 템플릿과 공용 renderer도 제거한다. UI의 상태·동작·렌더링 검증은 `verifying-work`의 선택형 참고 문서에 보존하며 `visual-docs`는 내용에 맞춘 표현과 의미·출처 보존을 담당한다. 외부 디자인 스킬이나 신규 패키지는 필수가 아니다.
