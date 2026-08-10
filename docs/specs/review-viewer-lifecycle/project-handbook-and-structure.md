# Project Handbook과 구조 설명

## Overview

Project Handbook은 파일 위치 목록이 아니라 프로젝트 목적, 주요 기능, Spec과 구조별 책임을 사람이 이해할 수 있게 연결하는 시각 문서다. `forge/project-map@1`은 사람이 작성한 프로젝트와 구조 설명을 소유하고, Canonical Spec은 규범적 계약을 소유하며, repository scan은 계산 가능한 evidence만 제공한다.

`Spec Guide`라는 별도 문서 종류나 authority는 두지 않는다. 독립 Spec View와 Project Handbook의 Spec 상세는 같은 normalized Spec content와 renderer를 사용한다.

## Requirements

### Project Handbook을 생성할 때 Forge는 tracked `docs/project/project-map.md`의 `forge/project-map@1` frontmatter, 프로젝트 설명 section, Spec inventory와 Structure entry를 primary navigation source로 사용해야 한다.

### `forge/project-map@1` source는 프로젝트 H1, `Project Overview`, `Key Capabilities`, `Specs`, `Structure` section을 가지며 Specs는 normalized unique `docs/specs/<semantic-bundle-name>/` path를 선언해야 한다.

### 각 Structure entry는 repository-contained path, 사람이 작성한 Purpose와 Owns, 0개 이상의 Entry Points, Depends On과 Related Specs를 표현하고, 관련 contract authority가 있으면 exact Canonical Spec statement link를 근거로 가져야 한다.

### Project Handbook builder는 Structure path와 Entry Point 존재, Spec Bundle lifecycle `approved|implemented`, unique path와 repository containment를 검증하고 누락·중복·path escape·dangling Spec 또는 statement link를 거부해야 한다.

### Visual Docs는 폴더명, 파일 위치, import·require edge 또는 source code만으로 Purpose와 Owns prose를 만들지 않아야 하며 Project Map에 설명이 없으면 누락 진단을 표시해야 한다.

### Repository scan에서 계산한 파일 목록, import·require edge와 source hash는 `Derived evidence`로 표시하고 Project Map의 Purpose, Owns 또는 Spec relation을 대체하지 않아야 한다.

### Project Handbook의 primary navigation은 개요, 설계 기준, 프로젝트 구조를 고정된 좌측 탐색으로 제공하고 선택한 항목의 내용을 우측 상세에 표시하며 프로젝트 목적, 핵심 기능과 사용자 흐름, 상위 영역 책임을 diagnostic count나 contract lifecycle 수치보다 먼저 보여줘야 한다.

### Project Handbook의 좌측 탐색은 Spec bundle·member·section과 Structure entry를 의미 기반 계층 node로 표시하고 검색, 현재 선택 상태, deep link와 표준 tree keyboard interaction을 지원해야 한다.

### Project Handbook의 Spec 탐색은 각 bundle의 title, Overview, 담당 영역, 관련 Spec과 source path를 요약하고 선택한 우측 상세에서 bundle의 모든 member와 Requirement·Acceptance Criteria를 source provenance와 함께 탐색할 수 있게 해야 한다.

### Project Handbook의 Spec 상세와 같은 bundle을 독립 spec kind로 생성한 View는 같은 Semantic IR entity, full statement, Mermaid bytes와 source provenance를 사용해야 한다.

### Project Handbook의 reader-facing label은 `프로젝트 한눈에`, `Spec`, `Requirement`, `Acceptance Criteria`, `Behavior & Flows`, `Launch Baseline`, `Purpose`, `Owns`, `Entry Points`와 `Developer information` 대신 각각 `개요`, `설계 기준`, `필수 사항`, `완료 기준`, `동작과 흐름`, `출시 기준`, `역할`, `담당 범위`, `주요 파일`과 `출처·검증`을 사용하되 exact normative statement와 identifier는 변경하지 않아야 한다.

### Project Handbook의 구조 상세는 선택한 Structure entry의 역할과 담당 범위를 먼저 표시하고 주요 파일, dependency evidence와 하위 파일 목록을 그 뒤에 표시해야 한다.

### Runtime mirror, validation, drift, source hash, source record와 plan·contract lifecycle 집계는 primary navigation에서 제외하고 현재 선택 항목에 해당하는 `출처·검증` detail route 또는 panel에서 provenance와 함께 표시해야 한다.

### Project Handbook은 하나의 `Complete Spec details` disclosure 없이 선언된 모든 Spec의 전체 내용을 좌측 탐색과 선택형 우측 상세에서 탐색할 수 있어야 하며 Overview와 Structure에 Requirement·Acceptance Criteria 본문을 복제하지 않아야 한다.

### Project Handbook은 desktop working width에서 좌측 탐색과 우측 상세를 side-by-side로 유지하고 narrow viewport에서는 탐색과 상세을 한 화면씩 표시하며 상세에서 탐색으로 돌아가는 명시적 action을 제공해야 한다.

## Acceptance Criteria

### Project Map의 Structure entry에 Purpose 또는 Owns가 없거나 path·Entry Point가 존재하지 않거나 Spec·statement link가 dangling인 fixture는 Project Handbook build에 실패하고 source를 수정할 수 있는 path-qualified 진단을 반환한다.

검증하는 요구사항:

- [Project Handbook을 생성할 때 Forge는 tracked `docs/project/project-map.md`의 `forge/project-map@1` frontmatter, 프로젝트 설명 section, Spec inventory와 Structure entry를 primary navigation source로 사용해야 한다.](project-handbook-and-structure.md#project-handbook을-생성할-때-forge는-tracked-docsprojectproject-mapmd의-forgeproject-map1-frontmatter-프로젝트-설명-section-spec-inventory와-structure-entry를-primary-navigation-source로-사용해야-한다)
- [`forge/project-map@1` source는 프로젝트 H1, `Project Overview`, `Key Capabilities`, `Specs`, `Structure` section을 가지며 Specs는 normalized unique `docs/specs/<semantic-bundle-name>/` path를 선언해야 한다.](project-handbook-and-structure.md#forgeproject-map1-source는-프로젝트-h1-project-overview-key-capabilities-specs-structure-section을-가지며-specs는-normalized-unique-docsspecssemantic-bundle-name-path를-선언해야-한다)
- [각 Structure entry는 repository-contained path, 사람이 작성한 Purpose와 Owns, 0개 이상의 Entry Points, Depends On과 Related Specs를 표현하고, 관련 contract authority가 있으면 exact Canonical Spec statement link를 근거로 가져야 한다.](project-handbook-and-structure.md#각-structure-entry는-repository-contained-path-사람이-작성한-purpose와-owns-0개-이상의-entry-points-depends-on과-related-specs를-표현하고-관련-contract-authority가-있으면-exact-canonical-spec-statement-link를-근거로-가져야-한다)
- [Project Handbook builder는 Structure path와 Entry Point 존재, Spec Bundle lifecycle `approved|implemented`, unique path와 repository containment를 검증하고 누락·중복·path escape·dangling Spec 또는 statement link를 거부해야 한다.](project-handbook-and-structure.md#project-handbook-builder는-structure-path와-entry-point-존재-spec-bundle-lifecycle-approvedimplemented-unique-path와-repository-containment를-검증하고-누락중복path-escapedangling-spec-또는-statement-link를-거부해야-한다)
- [Visual Docs는 폴더명, 파일 위치, import·require edge 또는 source code만으로 Purpose와 Owns prose를 만들지 않아야 하며 Project Map에 설명이 없으면 누락 진단을 표시해야 한다.](project-handbook-and-structure.md#visual-docs는-폴더명-파일-위치-importrequire-edge-또는-source-code만으로-purpose와-owns-prose를-만들지-않아야-하며-project-map에-설명이-없으면-누락-진단을-표시해야-한다)

### 같은 Spec Bundle을 Project Handbook의 설계 기준 상세와 독립 spec kind로 build하면 member path, full Requirement·Acceptance heading, Mermaid SHA-256과 provenance가 일치하고 Project Handbook 개요에는 해당 statement 본문이 중복되지 않는다.

검증하는 요구사항:

- [Project Handbook의 Spec 탐색은 각 bundle의 title, Overview, 담당 영역, 관련 Spec과 source path를 요약하고 선택한 우측 상세에서 bundle의 모든 member와 Requirement·Acceptance Criteria를 source provenance와 함께 탐색할 수 있게 해야 한다.](project-handbook-and-structure.md#project-handbook의-spec-탐색은-각-bundle의-title-overview-담당-영역-관련-spec과-source-path를-요약하고-선택한-우측-상세에서-bundle의-모든-member와-requirementacceptance-criteria를-source-provenance와-함께-탐색할-수-있게-해야-한다)
- [Project Handbook의 Spec 상세와 같은 bundle을 독립 spec kind로 생성한 View는 같은 Semantic IR entity, full statement, Mermaid bytes와 source provenance를 사용해야 한다.](project-handbook-and-structure.md#project-handbook의-spec-상세와-같은-bundle을-독립-spec-kind로-생성한-view는-같은-semantic-ir-entity-full-statement-mermaid-bytes와-source-provenance를-사용해야-한다)
- [Project Handbook은 하나의 `Complete Spec details` disclosure 없이 선언된 모든 Spec의 전체 내용을 좌측 탐색과 선택형 우측 상세에서 탐색할 수 있어야 하며 Overview와 Structure에 Requirement·Acceptance Criteria 본문을 복제하지 않아야 한다.](project-handbook-and-structure.md#project-handbook은-하나의-complete-spec-details-disclosure-없이-선언된-모든-spec의-전체-내용을-좌측-탐색과-선택형-우측-상세에서-탐색할-수-있어야-하며-overview와-structure에-requirementacceptance-criteria-본문을-복제하지-않아야-한다)

### Project Map과 repository evidence를 가진 Project Handbook에서 Structure node를 선택하면 역할과 담당 범위가 주요 파일보다 먼저 표시되고 출처·검증을 열면 해당 node의 Runtime mirror, validation, drift, source hash와 lifecycle evidence만 확인되며 narrow viewport에서도 탐색으로 돌아갈 수 있다.

검증하는 요구사항:

- [Repository scan에서 계산한 파일 목록, import·require edge와 source hash는 `Derived evidence`로 표시하고 Project Map의 Purpose, Owns 또는 Spec relation을 대체하지 않아야 한다.](project-handbook-and-structure.md#repository-scan에서-계산한-파일-목록-importrequire-edge와-source-hash는-derived-evidence로-표시하고-project-map의-purpose-owns-또는-spec-relation을-대체하지-않아야-한다)
- [Project Handbook의 primary navigation은 개요, 설계 기준, 프로젝트 구조를 고정된 좌측 탐색으로 제공하고 선택한 항목의 내용을 우측 상세에 표시하며 프로젝트 목적, 핵심 기능과 사용자 흐름, 상위 영역 책임을 diagnostic count나 contract lifecycle 수치보다 먼저 보여줘야 한다.](project-handbook-and-structure.md#project-handbook의-primary-navigation은-개요-설계-기준-프로젝트-구조를-고정된-좌측-탐색으로-제공하고-선택한-항목의-내용을-우측-상세에-표시하며-프로젝트-목적-핵심-기능과-사용자-흐름-상위-영역-책임을-diagnostic-count나-contract-lifecycle-수치보다-먼저-보여줘야-한다)
- [Project Handbook의 좌측 탐색은 Spec bundle·member·section과 Structure entry를 의미 기반 계층 node로 표시하고 검색, 현재 선택 상태, deep link와 표준 tree keyboard interaction을 지원해야 한다.](project-handbook-and-structure.md#project-handbook의-좌측-탐색은-spec-bundlemembersection과-structure-entry를-의미-기반-계층-node로-표시하고-검색-현재-선택-상태-deep-link와-표준-tree-keyboard-interaction을-지원해야-한다)
- [Project Handbook의 reader-facing label은 `프로젝트 한눈에`, `Spec`, `Requirement`, `Acceptance Criteria`, `Behavior & Flows`, `Launch Baseline`, `Purpose`, `Owns`, `Entry Points`와 `Developer information` 대신 각각 `개요`, `설계 기준`, `필수 사항`, `완료 기준`, `동작과 흐름`, `출시 기준`, `역할`, `담당 범위`, `주요 파일`과 `출처·검증`을 사용하되 exact normative statement와 identifier는 변경하지 않아야 한다.](project-handbook-and-structure.md#project-handbook의-reader-facing-label은-프로젝트-한눈에-spec-requirement-acceptance-criteria-behavior-flows-launch-baseline-purpose-owns-entry-points와-developer-information-대신-각각-개요-설계-기준-필수-사항-완료-기준-동작과-흐름-출시-기준-역할-담당-범위-주요-파일과-출처검증을-사용하되-exact-normative-statement와-identifier는-변경하지-않아야-한다)
- [Project Handbook의 구조 상세는 선택한 Structure entry의 역할과 담당 범위를 먼저 표시하고 주요 파일, dependency evidence와 하위 파일 목록을 그 뒤에 표시해야 한다.](project-handbook-and-structure.md#project-handbook의-구조-상세는-선택한-structure-entry의-역할과-담당-범위를-먼저-표시하고-주요-파일-dependency-evidence와-하위-파일-목록을-그-뒤에-표시해야-한다)
- [Runtime mirror, validation, drift, source hash, source record와 plan·contract lifecycle 집계는 primary navigation에서 제외하고 현재 선택 항목에 해당하는 `출처·검증` detail route 또는 panel에서 provenance와 함께 표시해야 한다.](project-handbook-and-structure.md#runtime-mirror-validation-drift-source-hash-source-record와-plancontract-lifecycle-집계는-primary-navigation에서-제외하고-현재-선택-항목에-해당하는-출처검증-detail-route-또는-panel에서-provenance와-함께-표시해야-한다)
- [Project Handbook은 desktop working width에서 좌측 탐색과 우측 상세를 side-by-side로 유지하고 narrow viewport에서는 탐색과 상세을 한 화면씩 표시하며 상세에서 탐색으로 돌아가는 명시적 action을 제공해야 한다.](project-handbook-and-structure.md#project-handbook은-desktop-working-width에서-좌측-탐색과-우측-상세를-side-by-side로-유지하고-narrow-viewport에서는-탐색과-상세을-한-화면씩-표시하며-상세에서-탐색으로-돌아가는-명시적-action을-제공해야-한다)
