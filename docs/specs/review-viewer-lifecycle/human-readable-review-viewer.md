---
schema: forge/spec@3
role: root
status: approved
language: ko
kind: system
areas: ["forge","visual-docs"]
components: ["visual-docs","writing-specs","writing-plans","executing-plans"]
relatedSpecs: [{"path":"docs/specs/semantic-spec-bundles/","relation":"relatedTo"}]
---

# 사람 중심 Visual Docs

## Documents

- root: [사람 중심 Visual Docs](human-readable-review-viewer.md)
- contract: [시각 문서의 제작 경로](presentation-routing.md)
- contract: [Plan Context와 문장 추적성](plan-context-and-statement-traceability.md)
- history: [현재 결정](decisions-and-change-history.md)

## 목적과 범위

Forge 원문의 시각화는 독자가 이해해야 할 내용과 요청한 결과에 맞춰 작성한다. 표, 도식, 앱 기능과 직접 작성한 HTML을 사용할 수 있다. Forge는 고정 화면, 문서별 템플릿, 공용 renderer와 전용 composition 입력을 제공하지 않는다.

[시각 문서의 제작 경로](presentation-routing.md)는 표현의 자유, 원문의 의미 보존, 기존 문서의 갱신과 실제 읽기 검증을 다룬다. [Plan Context와 문장 추적성](plan-context-and-statement-traceability.md)은 목표·의존성·검증과 필요한 원문 참조를 다루며 고정 Plan 문법을 요구하지 않는다. 시각화를 위해 스펙이나 계획의 내용을 특정 형식으로 다시 작성할 필요는 없다.

시각 문서는 파생 설명이다. 승인된 Canonical Spec의 권위와 계획의 실행 역할을 바꾸지 않으며 제품 구현 완료의 증거를 대신하지 않는다. 일반 Spec·Plan 작업은 Markdown을 기본으로 사용한다.

## 저장과 갱신

대화로 충분하면 파일을 만들지 않는다. 파일이 필요하면 사용자가 지정한 경로나 프로젝트 관례를 따르고, 로컬 HTML의 기본 경로는 `.forge/visual-docs/<view-id>/view.html`이다. 공유하는 Handbook은 프로젝트의 문서 경로와 버전 관리 관례를 따른다. 시각 문서의 위치나 Git 추적 여부가 정본 권위를 만들지 않는다.

기존 문서는 갱신 요청이 있을 때 원문과 해당 프로젝트의 제작 방식을 확인하고 수정한다. 프로젝트가 관리하는 generator가 있으면 활용할 수 있다. Forge의 이전 builder는 배포하지 않으며, 갱신한 결과에 더 이상 유효하지 않은 생성기·최신성 보장을 남기지 않는다.
