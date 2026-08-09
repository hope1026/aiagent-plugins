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

### Project Handbook의 primary navigation은 프로젝트 한눈에, Spec, 구조를 제공하고 프로젝트 목적, 핵심 기능과 사용자 흐름, 상위 영역 책임을 diagnostic count나 contract lifecycle 수치보다 먼저 보여줘야 한다.

### Project Handbook의 Spec 목록은 각 bundle의 title, Overview, 담당 영역, 관련 Spec과 source path를 요약하고 선택한 Spec 상세에서는 bundle의 모든 member와 Requirement·Acceptance Criteria를 source provenance와 함께 표시해야 한다.

### Project Handbook의 Spec 상세와 같은 bundle을 독립 spec kind로 생성한 View는 같은 Semantic IR entity, full statement, Mermaid bytes와 source provenance를 사용해야 한다.

### Project Handbook의 구조 화면은 상위 Structure entry의 Purpose와 Owns를 먼저 표시하고 Entry Points, dependency evidence와 하위 파일 목록은 disclosure 뒤에 표시해야 한다.

### Runtime mirror, validation, drift, source hash, plan과 contract lifecycle 집계는 primary navigation에서 제외하고 source에 존재할 때만 접힌 `Developer information`에서 provenance와 함께 표시해야 한다.

### Project Handbook은 선언된 모든 Spec의 전체 내용을 탐색할 수 있어야 하지만 Overview와 Structure에 Requirement·Acceptance Criteria 본문을 복제하지 않고 Spec 상세 deep link를 사용해야 한다.

## Acceptance Criteria

### Project Map의 Structure entry에 Purpose 또는 Owns가 없거나 path·Entry Point가 존재하지 않거나 Spec·statement link가 dangling인 fixture는 Project Handbook build에 실패하고 source를 수정할 수 있는 path-qualified 진단을 반환한다.

검증하는 요구사항:

- [Project Handbook을 생성할 때 Forge는 tracked `docs/project/project-map.md`의 `forge/project-map@1` frontmatter, 프로젝트 설명 section, Spec inventory와 Structure entry를 primary navigation source로 사용해야 한다.](project-handbook-and-structure.md#project-handbook을-생성할-때-forge는-tracked-docsprojectproject-mapmd의-forgeproject-map1-frontmatter-프로젝트-설명-section-spec-inventory와-structure-entry를-primary-navigation-source로-사용해야-한다)
- [`forge/project-map@1` source는 프로젝트 H1, `Project Overview`, `Key Capabilities`, `Specs`, `Structure` section을 가지며 Specs는 normalized unique `docs/specs/<semantic-bundle-name>/` path를 선언해야 한다.](project-handbook-and-structure.md#forgeproject-map1-source는-프로젝트-h1-project-overview-key-capabilities-specs-structure-section을-가지며-specs는-normalized-unique-docsspecssemantic-bundle-name-path를-선언해야-한다)
- [각 Structure entry는 repository-contained path, 사람이 작성한 Purpose와 Owns, 0개 이상의 Entry Points, Depends On과 Related Specs를 표현하고, 관련 contract authority가 있으면 exact Canonical Spec statement link를 근거로 가져야 한다.](project-handbook-and-structure.md#각-structure-entry는-repository-contained-path-사람이-작성한-purpose와-owns-0개-이상의-entry-points-depends-on과-related-specs를-표현하고-관련-contract-authority가-있으면-exact-canonical-spec-statement-link를-근거로-가져야-한다)
- [Project Handbook builder는 Structure path와 Entry Point 존재, Spec Bundle lifecycle `approved|implemented`, unique path와 repository containment를 검증하고 누락·중복·path escape·dangling Spec 또는 statement link를 거부해야 한다.](project-handbook-and-structure.md#project-handbook-builder는-structure-path와-entry-point-존재-spec-bundle-lifecycle-approvedimplemented-unique-path와-repository-containment를-검증하고-누락중복path-escapedangling-spec-또는-statement-link를-거부해야-한다)
- [Visual Docs는 폴더명, 파일 위치, import·require edge 또는 source code만으로 Purpose와 Owns prose를 만들지 않아야 하며 Project Map에 설명이 없으면 누락 진단을 표시해야 한다.](project-handbook-and-structure.md#visual-docs는-폴더명-파일-위치-importrequire-edge-또는-source-code만으로-purpose와-owns-prose를-만들지-않아야-하며-project-map에-설명이-없으면-누락-진단을-표시해야-한다)

### 같은 Spec Bundle을 Project Handbook의 Spec 상세와 독립 spec kind로 build하면 member path, full Requirement·Acceptance heading, Mermaid SHA-256과 provenance가 일치하고 Project Handbook Overview에는 해당 statement 본문이 중복되지 않는다.

검증하는 요구사항:

- [Project Handbook의 Spec 목록은 각 bundle의 title, Overview, 담당 영역, 관련 Spec과 source path를 요약하고 선택한 Spec 상세에서는 bundle의 모든 member와 Requirement·Acceptance Criteria를 source provenance와 함께 표시해야 한다.](project-handbook-and-structure.md#project-handbook의-spec-목록은-각-bundle의-title-overview-담당-영역-관련-spec과-source-path를-요약하고-선택한-spec-상세에서는-bundle의-모든-member와-requirementacceptance-criteria를-source-provenance와-함께-표시해야-한다)
- [Project Handbook의 Spec 상세와 같은 bundle을 독립 spec kind로 생성한 View는 같은 Semantic IR entity, full statement, Mermaid bytes와 source provenance를 사용해야 한다.](project-handbook-and-structure.md#project-handbook의-spec-상세와-같은-bundle을-독립-spec-kind로-생성한-view는-같은-semantic-ir-entity-full-statement-mermaid-bytes와-source-provenance를-사용해야-한다)
- [Project Handbook은 선언된 모든 Spec의 전체 내용을 탐색할 수 있어야 하지만 Overview와 Structure에 Requirement·Acceptance Criteria 본문을 복제하지 않고 Spec 상세 deep link를 사용해야 한다.](project-handbook-and-structure.md#project-handbook은-선언된-모든-spec의-전체-내용을-탐색할-수-있어야-하지만-overview와-structure에-requirementacceptance-criteria-본문을-복제하지-않고-spec-상세-deep-link를-사용해야-한다)

### Project Map과 repository evidence를 가진 Project Handbook에서 폴더별 Purpose와 Owns가 파일 목록보다 먼저 표시되고 Runtime mirror, validation, drift, source hash와 lifecycle count는 primary navigation에 없으며 접힌 Developer information에서만 확인된다.

검증하는 요구사항:

- [Repository scan에서 계산한 파일 목록, import·require edge와 source hash는 `Derived evidence`로 표시하고 Project Map의 Purpose, Owns 또는 Spec relation을 대체하지 않아야 한다.](project-handbook-and-structure.md#repository-scan에서-계산한-파일-목록-importrequire-edge와-source-hash는-derived-evidence로-표시하고-project-map의-purpose-owns-또는-spec-relation을-대체하지-않아야-한다)
- [Project Handbook의 primary navigation은 프로젝트 한눈에, Spec, 구조를 제공하고 프로젝트 목적, 핵심 기능과 사용자 흐름, 상위 영역 책임을 diagnostic count나 contract lifecycle 수치보다 먼저 보여줘야 한다.](project-handbook-and-structure.md#project-handbook의-primary-navigation은-프로젝트-한눈에-spec-구조를-제공하고-프로젝트-목적-핵심-기능과-사용자-흐름-상위-영역-책임을-diagnostic-count나-contract-lifecycle-수치보다-먼저-보여줘야-한다)
- [Project Handbook의 구조 화면은 상위 Structure entry의 Purpose와 Owns를 먼저 표시하고 Entry Points, dependency evidence와 하위 파일 목록은 disclosure 뒤에 표시해야 한다.](project-handbook-and-structure.md#project-handbook의-구조-화면은-상위-structure-entry의-purpose와-owns를-먼저-표시하고-entry-points-dependency-evidence와-하위-파일-목록은-disclosure-뒤에-표시해야-한다)
- [Runtime mirror, validation, drift, source hash, plan과 contract lifecycle 집계는 primary navigation에서 제외하고 source에 존재할 때만 접힌 `Developer information`에서 provenance와 함께 표시해야 한다.](project-handbook-and-structure.md#runtime-mirror-validation-drift-source-hash-plan과-contract-lifecycle-집계는-primary-navigation에서-제외하고-source에-존재할-때만-접힌-developer-information에서-provenance와-함께-표시해야-한다)
