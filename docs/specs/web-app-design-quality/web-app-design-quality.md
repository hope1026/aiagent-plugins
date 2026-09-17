---
schema: forge/spec@3
role: root
status: approved
language: ko
kind: policy
areas: ["forge","design"]
components: ["verifying-work"]
relatedSpecs: [{"path":"docs/specs/forge-ui-design-skill-separation/","relation":"refines"}]
---

# Web App 디자인 품질 계약

## Documents

- root: [Web App 디자인 품질 계약](web-app-design-quality.md)

## Overview

`verifying-work`의 UI 참고 문서는 각 browser application의 제품 계약과 실제 변경 범위에 맞는 검증을 지원한다. 디자인 방향을 정하는 독립 스킬은 배포하지 않는다. 상태 보존, 실패 복구, 가독성과 접근성의 검증 기준을 유지하며 기존 bundle 경로는 소비자 링크를 위해 유지한다.

## Requirements

### `verifying-work`의 UI 검증은 특정 프로젝트의 명칭·정보 구조·기능 또는 수치를 범용 기본값으로 고정하지 않고 현재 제품의 사용자 작업, 기존 디자인 시스템과 실제 상태를 근거로 해야 한다.

### 새 화면과 구조 변경의 완료 검증은 typography, 정렬, 여백, 색상, 컴포넌트 비례와 정보 관계를 렌더링 결과에서 검토하고 주 작업과 관련 정보가 쉽게 보이는지 확인해야 한다.

### 각 정보 그룹은 현재 작업의 판단 관련성, 사용 빈도와 누락 결과에 따라 기본 표시, 명시적 상세 열기 후 표시 또는 예외 상태에서 항상 표시로 분류하고 오류와 차단 상태의 존재는 기본 화면에 유지해야 한다.

경로, timestamp, ID, 긴 값 전체와 설명 metadata는 정보 종류만으로 숨기지 않는다. 현재 판단에 필요하면 기본 화면에 두고, 그렇지 않으면 상세에 둔다. 오류와 차단의 전체 진단은 상세에 둘 수 있다.

### 색상은 기능 이름이나 action 동사가 아니라 semantic role에 따라 기존 제품 palette와 대응하고 제품이 지원하는 theme 사이에서 같은 의미를 유지해야 한다.

해당 제품에 존재하는 primary interaction, neutral action, premium identity, success, warning, info, system error와 destructive action을 대조한다. Add 또는 Create라는 이름만으로 success나 diff-add 색상을 사용하지 않는다.

### 제품 계약이 데이터 변경을 명시하지 않은 상세 열기, filter, group, pagination과 layout editing은 저장 데이터 mutation을 일으키지 않고 관련 입력 draft, focus, scroll과 live subscription을 의도하지 않게 잃지 않아야 한다.

상호작용 계약이 focus나 scroll 이동을 요구하면 그 의도된 변화는 허용하되 관계없는 화면 상태와 데이터 상태는 보존한다.

### 데이터 중심 화면은 실제 작업량과 관련 경계 상태에서 정보의 가독성과 비교·조작 품질을 확인하고 수치 측정은 진단이나 회귀 확인에 필요할 때 사용해야 한다.

밀도를 높이기 위해 주요 값을 metadata 크기로 낮추거나 오류와 차단 상태를 숨기지 않는다. 측정값은 목표 자체가 아니라 읽기, 비교와 조작 품질을 평가하는 증거로 사용한다.

### 재정렬 기능이 있는 화면은 drag source, 삽입 위치, 최종 순서, 이동 경계, 저장 중 상태와 저장 실패 복구를 검증하고 keyboard와 touch에서 같은 최종 결과를 제공해야 한다.

live data를 지원하면 재정렬 중 stable identity를 유지하고 이동 대상의 삭제나 동시 순서 변경을 제품 계약에 따라 처리한다.

### UI 변경은 영향받는 화면·상태와 제품의 접근성 목표를 실제로 검증하고 고정 선언문·전체 상태 조합·보편적인 픽셀 수치를 강제하지 않아야 한다.

## Acceptance Criteria

### 서로 다른 설정 화면, 데이터 작업 화면과 콘텐츠 편집 화면을 검증하면 각 제품의 작업과 디자인 시스템에 맞는 렌더링 증거를 확인하고 특정 프로젝트의 명칭이나 구조를 공통 요구사항으로 가져오지 않는다.

검증하는 요구사항:

- [`verifying-work`의 UI 검증은 특정 프로젝트의 명칭·정보 구조·기능 또는 수치를 범용 기본값으로 고정하지 않고 현재 제품의 사용자 작업, 기존 디자인 시스템과 실제 상태를 근거로 해야 한다.](web-app-design-quality.md#verifying-work의-ui-검증은-특정-프로젝트의-명칭정보-구조기능-또는-수치를-범용-기본값으로-고정하지-않고-현재-제품의-사용자-작업-기존-디자인-시스템과-실제-상태를-근거로-해야-한다)
- [새 화면과 구조 변경의 완료 검증은 typography, 정렬, 여백, 색상, 컴포넌트 비례와 정보 관계를 렌더링 결과에서 검토하고 주 작업과 관련 정보가 쉽게 보이는지 확인해야 한다.](web-app-design-quality.md#새-화면과-구조-변경의-완료-검증은-typography-정렬-여백-색상-컴포넌트-비례와-정보-관계를-렌더링-결과에서-검토하고-주-작업과-관련-정보가-쉽게-보이는지-확인해야-한다)

### 일반 상태와 오류·차단 상태를 정보량별 fixture와 지원 theme에서 렌더링하면 작업에 필요한 정보와 상태가 기본 화면에 보이고 상세 정보, semantic color와 정보 밀도가 해당 제품의 UX에 맞게 유지된다.

검증하는 요구사항:

- [각 정보 그룹은 현재 작업의 판단 관련성, 사용 빈도와 누락 결과에 따라 기본 표시, 명시적 상세 열기 후 표시 또는 예외 상태에서 항상 표시로 분류하고 오류와 차단 상태의 존재는 기본 화면에 유지해야 한다.](web-app-design-quality.md#각-정보-그룹은-현재-작업의-판단-관련성-사용-빈도와-누락-결과에-따라-기본-표시-명시적-상세-열기-후-표시-또는-예외-상태에서-항상-표시로-분류하고-오류와-차단-상태의-존재는-기본-화면에-유지해야-한다)
- [색상은 기능 이름이나 action 동사가 아니라 semantic role에 따라 기존 제품 palette와 대응하고 제품이 지원하는 theme 사이에서 같은 의미를 유지해야 한다.](web-app-design-quality.md#색상은-기능-이름이나-action-동사가-아니라-semantic-role에-따라-기존-제품-palette와-대응하고-제품이-지원하는-theme-사이에서-같은-의미를-유지해야-한다)
- [데이터 중심 화면은 실제 작업량과 관련 경계 상태에서 정보의 가독성과 비교·조작 품질을 확인하고 수치 측정은 진단이나 회귀 확인에 필요할 때 사용해야 한다.](web-app-design-quality.md#데이터-중심-화면은-실제-작업량과-관련-경계-상태에서-정보의-가독성과-비교조작-품질을-확인하고-수치-측정은-진단이나-회귀-확인에-필요할-때-사용해야-한다)

### 표시 방식 조작과 재정렬 기능을 각 입력 방식과 live update 조건에서 실행하면 명시된 데이터 변경만 발생하고 관련 화면 상태, 대상 identity, 최종 순서와 실패 복구가 제품 계약에 맞게 유지된다.

검증하는 요구사항:

- [제품 계약이 데이터 변경을 명시하지 않은 상세 열기, filter, group, pagination과 layout editing은 저장 데이터 mutation을 일으키지 않고 관련 입력 draft, focus, scroll과 live subscription을 의도하지 않게 잃지 않아야 한다.](web-app-design-quality.md#제품-계약이-데이터-변경을-명시하지-않은-상세-열기-filter-group-pagination과-layout-editing은-저장-데이터-mutation을-일으키지-않고-관련-입력-draft-focus-scroll과-live-subscription을-의도하지-않게-잃지-않아야-한다)
- [재정렬 기능이 있는 화면은 drag source, 삽입 위치, 최종 순서, 이동 경계, 저장 중 상태와 저장 실패 복구를 검증하고 keyboard와 touch에서 같은 최종 결과를 제공해야 한다.](web-app-design-quality.md#재정렬-기능이-있는-화면은-drag-source-삽입-위치-최종-순서-이동-경계-저장-중-상태와-저장-실패-복구를-검증하고-keyboard와-touch에서-같은-최종-결과를-제공해야-한다)

### 국소 수정과 구조 변경 사례를 수행하면 각 영향 범위의 가독성·상태·조작성과 접근성 목표를 확인하고 무관한 선언·측정 작업을 추가하지 않는다.

검증하는 요구사항:

- [UI 변경은 영향받는 화면·상태와 제품의 접근성 목표를 실제로 검증하고 고정 선언문·전체 상태 조합·보편적인 픽셀 수치를 강제하지 않아야 한다.](web-app-design-quality.md#ui-변경은-영향받는-화면상태와-제품의-접근성-목표를-실제로-검증하고-고정-선언문전체-상태-조합보편적인-픽셀-수치를-강제하지-않아야-한다)

## Decisions & History

- 2026-09-17 [CURRENT] 디자인 스킬 제거에 따라 이 계약의 검증 책임을 `verifying-work`의 UI 참고 문서로 옮긴다. 정보 노출, semantic color, 화면 상태 보존, 가독성과 재정렬 복구는 관련 기능과 변경 범위에 적용하며 별도 디자인 절차나 보편적 수치를 강제하지 않는다.
