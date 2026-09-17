# 시각 문서의 제작 경로

이 문서는 자유 작성과 관리형 문서의 선택 및 공통 의미 보존 계약을 소유한다. 나머지 member의 renderer·source schema·manifest·출력 lifecycle 계약은 관리형 경로에 적용한다.

## Requirements

### Forge는 일반 시각화 요청을 전용 Visual Docs 제작 절차에 강제 라우팅하지 않아야 한다.

Forge 원문이나 관리형 문서와 무관한 설명, 표, 도식과 시각화는 현재 앱의 기능과 모델의 판단으로 처리한다. Forge 원문의 시각화에만 visual-docs의 의미 보존 지침을 적용한다.

### Forge 원문의 일회성 시각화는 요청에 맞는 표현과 도구를 선택하고 관리형 빌드 입력을 필수로 만들지 않아야 한다.

대화 안의 표·Mermaid·시각화 또는 직접 작성한 HTML·CSS·JavaScript를 사용할 수 있다. Brief 파일, Project Map, composition JSON, 공용 renderer와 manifest를 일괄 요구하지 않는다. 파일이 필요한 경우 기존 프로젝트 관례나 사용자 경로를 사용하고 기본 로컬 HTML은 .forge/visual-docs/<view-id>/view.html에 둔다. 자유 작성 결과는 직접 수정할 수 있으며 관리형 freshness·재현성 보장을 주장하지 않는다.

### Forge 원문의 시각화는 원문의 권위와 조건을 보존하고 요청한 결과의 의미와 표시를 검증해야 한다.

원문 링크와 필요한 인용으로 핵심 설명을 추적한다. 조건·예외·수치·책임·확정 상태와 Brief·Plan·Spec 역할을 유지하며 근거 없는 정책이나 승인을 만들지 않는다. 설명을 정본으로 승격하지 않는다. 실제 제공 표면에서 핵심 내용과 가독성을 확인하고 미검증 범위를 밝힌다. 모든 주장에 JSON 인용이나 별도 검토 양식을 강제하지 않는다.

### 재생성 가능한 Project Handbook이나 관리형 검증을 요청한 경우 Forge는 기존 관리형 renderer 경로를 선택해야 한다.

명시적인 동일 입력 재생성, source freshness 검사, 기존 관리형 문서 갱신 또는 tracked Project Handbook 요청은 관리형 경로에 해당한다. 일반 프로젝트 구조 설명이나 핸드북이라는 단어만으로 해당 절차를 강제하지 않는다. 관리형 경로에서만 네 kind, 구조화 source, composition, build, manifest와 freshness 계약을 적용한다. 기존 관리형 HTML은 직접 수정하지 않고 입력이나 tooling을 고쳐 재생성한다. CLI와 기존 저장 형식은 유지한다.

### 완료된 시각 문서는 원문 변경만으로 자동 갱신하지 않아야 한다.

진행 중인 시각화 요청은 필요한 수정과 검증을 포함한다. 일반 Spec·Plan 작업이 시각 문서 생성 요청을 대신하지 않는다. 관리형 또는 자유 작성 경로를 정하기 위해 이미 구체적인 요청을 다시 승인받지 않는다.

## Acceptance Criteria

### 시간이 제한된 일반 도식 요청을 처리하면 Visual Docs reference나 builder 없이 요청한 표면에 답을 제공한다.

검증하는 요구사항:

- [Forge는 일반 시각화 요청을 전용 Visual Docs 제작 절차에 강제 라우팅하지 않아야 한다.](presentation-routing.md#forge는-일반-시각화-요청을-전용-visual-docs-제작-절차에-강제-라우팅하지-않아야-한다)

### 대화 속 Brief나 조건과 예외가 있는 Spec의 일회성 시각화를 요청하면 별도 source 파일과 composition 없이 표현을 선택하고 핵심 조건과 출처를 보존한다.

검증하는 요구사항:

- [Forge 원문의 일회성 시각화는 요청에 맞는 표현과 도구를 선택하고 관리형 빌드 입력을 필수로 만들지 않아야 한다.](presentation-routing.md#forge-원문의-일회성-시각화는-요청에-맞는-표현과-도구를-선택하고-관리형-빌드-입력을-필수로-만들지-않아야-한다)
- [Forge 원문의 시각화는 원문의 권위와 조건을 보존하고 요청한 결과의 의미와 표시를 검증해야 한다.](presentation-routing.md#forge-원문의-시각화는-원문의-권위와-조건을-보존하고-요청한-결과의-의미와-표시를-검증해야-한다)

### 동일 입력으로 재생성하는 tracked Handbook과 기존 관리형 문서의 갱신 요청은 공용 builder와 freshness 검증을 사용하고 생성 HTML을 직접 수정하지 않는다.

검증하는 요구사항:

- [재생성 가능한 Project Handbook이나 관리형 검증을 요청한 경우 Forge는 기존 관리형 renderer 경로를 선택해야 한다.](presentation-routing.md#재생성-가능한-project-handbook이나-관리형-검증을-요청한-경우-forge는-기존-관리형-renderer-경로를-선택해야-한다)

### 완료 문서의 source만 변경한 작업은 시각 문서를 갱신하지 않고 이미 요청한 시각 문서의 교정은 추가 승인 없이 수행한다.

검증하는 요구사항:

- [완료된 시각 문서는 원문 변경만으로 자동 갱신하지 않아야 한다.](presentation-routing.md#완료된-시각-문서는-원문-변경만으로-자동-갱신하지-않아야-한다)
