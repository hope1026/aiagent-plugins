# Forge 완성도와 스펙 정확성을 우선하는 작업·검증 개선 계획

> 계획 작성 요청에 따른 제안이다. 사용자가 실행을 요청하면 the forge executing-plans skill로 진행한다. 이 계획은 현재 정본을 대체하거나 구현 완료를 선언하지 않는다.

Status: complete

**Related Specs:**

- bundle: docs/specs/canonical-spec-workflow/
- bundle: docs/specs/semantic-spec-bundles/
- bundle: docs/specs/forge-repository-maintenance/

**Goal:** 작업을 끝까지 완성하고 스펙을 정확한 SOT로 유지하면서, 결과를 증명하는 데 기여하지 않는 반복 조사·검증·문서화를 줄인다.
**Approach:** 우선순위와 검증 범위를 정본에서 정의하고, 관련 스킬에 동일하게 적용한 뒤, 문서 작성 기준·상태 보호·실제 작업 시나리오로 효과를 확인한다.

## 우선순위와 기대 결과

1. **작업 완성도와 스펙 정확성:** 요청한 결과, 직접·간접 영향, 필수 검증을 충족해야 완료한다. 시간 절약을 이유로 실패·미확인 동작·스펙 충돌을 남긴 채 완료 처리하지 않는다.
2. **필요한 만큼의 절차:** 위 조건을 만족하는 범위에서 가장 작고 직접적인 확인 방법을 선택한다. 동일한 사실을 재확인하거나 변경과 관계없는 전체 검증을 반복하지 않는다.

변경 줄 수, 파일 수 또는 “간단하다”는 표현만으로 검증을 줄이지 않는다. 한 줄짜리 권한·결제·저장 정책 변경도 지속 계약에 영향을 준다. 반대로 기능 의미가 그대로인 오탈자 수정은 해당 결과를 확인하면 끝낼 수 있다.

완료를 판단하는 공통 조건은 요청 범위 충족, 영향받는 계약의 일치, 그 주장을 뒷받침하는 증거, 완료 판단에 영향을 주는 미해결 문제가 없는 것이다. 테스트 수나 문서 수를 완성도의 대리 지표로 삼지 않는다.

## 작업별 적용안

이 표는 Task 1에서 정본 변경안으로 확정할 제안이다. 기존 두 축 분류를 유지하며 별도의 등급·점수 입력 절차를 추가하지 않는다.

| 작업 | 스펙 확인 범위 | 검증과 완료 범위 |
|---|---|---|
| 오탈자·서식·표현 스타일 | 변경 문맥과 이미 알려진 제약. 계약 의미가 그대로면 별도 스펙 전체 조회 없음 | diff 또는 실제 표시 확인. 의미 없는 신규 테스트·새 테스트 도구 없음 |
| 국소 리팩터링·동작 없는 설정 | 관련 불변 조건과 호출자·설정 소비자 | 기존 관련 테스트 또는 설정의 parse·실행 확인. 새 동작이나 보호 공백이 없으면 테스트 추가를 의무화하지 않음 |
| 기존 계약의 버그 복원 | 해당 요구사항과 영향을 받는 인접 계약 | 원래 재현, 기대 동작 관찰, 관련 회귀. 동일한 테스트가 이를 모두 증명하면 실행 한 번의 결과를 함께 사용 |
| 승인된 기능의 부분 구현 | 이번 구현 항목과 직접·간접 의존 항목 | 구현한 계약과 회귀 경계. 완료 범위를 부분 작업으로 한정하고 bundle 전체 상태는 자동 승격하지 않음 |
| 기능·정책·공개 API의 의미 변경 | 소유 bundle, 바뀌는 문장, 같은 계약을 설명하거나 소비하는 관련 문서 | 승인 의미 반영과 writer transaction, 영향 항목의 동작 검증·회귀 |
| 공통 구조·저장 형식·여러 컴포넌트 변경 | 영향받는 책임·인터페이스·상태·데이터 경계 | 필요한 통합·호환·오류·복구 경로와 관련 전체 suite |
| bundle 전체 구현 완료 선언 | 해당 bundle의 Canonical verification set 전체 | 전체 집합과 관련 회귀 증거를 충족한 뒤에만 implemented로 전환 |

코드와 테스트가 현재 기대를 서로 복제하고 있는지만 확인해서는 안 된다. 기대 결과는 승인된 계약과 사용자 요청에서 가져오고, 재현이나 관찰로 실제 동작과 대조한다. 스펙이 잘못됐다는 근거가 생기면 코드에 맞춰 조용히 바꾸지 않고 계약 수정으로 분류한다.

## 확인·재실행·종료 규칙 제안

- **내용 확인과 검증 실행을 구분한다.** 관련 스펙을 읽는 행위가 전역 상태 조사, 전체 Acceptance 순회, 모든 테스트 실행을 뜻하지 않는다.
- **스펙 재사용:** 같은 작업에서 읽은 관련 계약이 유효하고 바뀌지 않았다면 사용한다. 영향 범위 확대, 관련 source 변경, 문서 충돌, 재개 후 문맥 손실 때 필요한 부분만 다시 확인한다.
- **증거 재사용:** 실제 출력과 성공·실패를 확인했고 관련 구현·테스트·입력·설정·환경이 그대로면 단계 전환과 최종 보고에서 같은 증거를 사용한다. 단순히 시간이 지났거나 다른 스킬이 시작됐다는 이유로 재실행하지 않는다.
- **증거 무효화:** 동작에 영향을 주는 코드·테스트·의존성·설정·환경 변경, 새 실패, 증거가 다루지 않는 영향이 발견되면 관련 범위만 다시 검증한다. diff·현재 문맥으로 판정 가능한 작업에 매번 저장소 전체 hash나 별도 추적 시스템을 만들지 않는다.
- **위임 결과:** root가 diff와 실제 실행 출력을 확인하고 현재 통합 상태에도 적용됨을 판단해야 한다. worker의 성공 요약만으로 완료하지 않는다. 통합 영향이나 확인되지 않은 상태가 있으면 root가 영향 검증을 실행한다.
- **확대:** 공개 계약, 권한·데이터 손실 가능성, 공통 의존성, 호환성, 재현 실패 또는 불명확한 영향 범위를 근거로 검증을 넓힌다. 구체적 불확실성을 조사해 범위를 좁힐 수 있으면 먼저 좁힌다.
- **종료:** 요청과 관련 계약을 충족하고 필요한 증거가 확보되면 종료한다. 동일 suite 반복, 무관한 주변 기능 조사, 양식을 채우기 위한 테스트 추가를 이어가지 않는다.
- **기록:** 작은 작업은 변경 결과·검증 결과를 짧게 보고한다. 재개·협업·계약 변경·구현 상태 전환에 필요한 경우에만 기존 plan·Delta·evidence 기록을 확장한다. 매 작업마다 스펙 상태표를 만들지 않는다.
- **필수 검사 유지:** 프로젝트에서 요구하는 검사와 배포 gate는 충족한다. 줄일 필요가 있으면 규칙 자체를 별도 변경하며, 작업자가 임의 생략하지 않는다.

## 현재 근거와 개선 경계

- 완료된 [009 계획](../009-forge-purpose-alignment/plan.md)에 Quick·부분 검증·증거 재사용이 이미 포함되어 있다. 이번 작업은 그 결과를 이어받아 우선순위, 범위 확대와 종료 조건, 부분 작업과 전체 lifecycle의 차이를 명확히 한다.
- `verifying-work`는 미구현 approved baseline의 변경에 전체 집합을 요구하고, `writing-plans`는 전체 구현과 부분 변경을 다른 표현으로 설명한다. `executing-plans`의 매 Task fresh verification 문구와 증거 재사용 문구도 해석이 일치하도록 정리한다.
- 앞선 WEPPY 조사에서는 36개 bundle·63개 문서, 7개 draft, 매우 긴 요구사항 제목, MCP와 Playtest의 tier 설명 차이를 확인했다. 이는 당시 작업 중인 checkout의 관찰이며 제품 전체 동작 검증 결과가 아니다. 실행 시 선택한 사례만 다시 확인한다.
- 현재 `inspect`도 내부에서 repository validation을 수행한다. 이를 매 Task마다 반복하도록 새 규칙을 만들지 않는다. 이번에는 호출 필요성을 줄이며, 새로운 캐시·배치 CLI·성능 최적화는 실제 병목이 별도로 확인되면 후속 작업으로 다룬다.
- 임시 fixture에서 기존 approved bundle의 draft 강등이 validation을 통과하는 것을 확인했다. 상태 강등은 기계적으로 차단할 수 있다. 자연어 계약의 정확성과 사람의 승인 여부는 구조 검사만으로 증명할 수 없으므로 의미 검토·승인 절차의 책임을 분명히 한다.

## Global Constraints

- 사용자는 이 계획의 Forge 스킬·정본·검증기 구현, commit, PR push·merge와 Marketplace 배포까지 승인했다. 검증 완료 뒤 `main`에 병합하고 push 기반 배포 상태를 확인한다.
- 실행 단계의 범위는 Forge의 작업·검증·스펙 작성 지침과 좁은 lifecycle 보호 보강이다. 새 스펙 상태 대시보드, 상시 전역 감사, 요구사항별 영구 증거 DB, 강제 자동 HTML 생성은 도입하지 않는다.
- `weppy-roblox-mcp-private`는 참고 사례로 읽는다. 해당 프로젝트의 draft 일괄 승인, 문서 전체 재작성, 코드 수정은 포함하지 않는다.
- 기존 semantic bundle path, exact statement link, Markdown SOT와 요청형 Visual Docs 경계를 유지한다. 이번 계획에 statement ID·새 anchor 체계·schema migration을 포함하지 않는다.
- 사용자 언어의 계획·보고와 English 배포 스킬을 유지한다. 정본의 의미 변경은 구체적인 Delta에 반영한다. 이 계획의 구체적인 제안이 이후 승인되면 같은 의미를 다시 승인받지 않는다.
- 코드 검증기는 focused TDD로 수정한다. 스킬 지침은 실제 시나리오로 확인하며 문구 존재 검사만으로 행동 준수를 주장하지 않는다.
- 각 Task 완료는 이 plan에 기록한다. 파일이 겹치는 지침·정본 수정은 순차 실행하고, 독립 pressure test만 필요할 때 별도 agent에 위임한다.

## Verification Scope

계획 작성 기준 HEAD: `a8a6361a1140d600cb1ea266c24a63cbc3506fbf`.

관련 bundle은 inspect 결과 모두 `forge/spec@3`, `implemented`, diagnostics 0이다.

| Bundle | Baseline SHA-256 |
|---|---|
| `docs/specs/canonical-spec-workflow/` | `ec45bc2e417f2012f0bfd93ddaf18cf9a9e29f58aa53700b23520a18ad29d3d7` |
| `docs/specs/semantic-spec-bundles/` | `e7fbc94bfe55dddce299b515299cf3a292b0cccf98097eb8845228908d644e00` |
| `docs/specs/forge-repository-maintenance/` | `3d946501c95539ebfe2816ffd9e841c02391b183f9fc1c685e2342d2290bd42f` |

현재 단계는 계획의 완결성·경로·문장 연결을 검토한다. 아래 연결은 기존 계약의 보존 기준이며, 새로운 우선순위·부분 완료·상태 강등 차단의 정확한 의미는 Task 1의 Delta와 새 검증 문장으로 추가한다. 실행 전 baseline이 달라졌으면 영향받은 제안과 연결만 갱신한다.

실행 완료는 직접·간접 영향 항목과 아래 시나리오가 증명하는 범위로 한정한다. 변경된 전체 bundle의 lifecycle을 올릴 때는 현재 승인된 검증 규칙에 필요한 증거를 별도로 충족한다. 계획의 일부 테스트 성공으로 관련 bundle 전체가 implemented라고 주장하지 않는다.

## Statement Coverage

| Statement | Task | Verification |
|---|---|---|
| [하나의 지속적인 business rule을 바꾸지만 구현이 국소적인 fixture에서 agent는 bundle·member path와 exact statement를 가진 Spec Delta를 먼저 제시하고, 사용자 승인 전 기존 Canonical Spec을 대체하지 않으며, 승인·validation 뒤 Execution Plan 없이 구현하고 영향받는 Canonical verification set을 검증한다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#하나의-지속적인-business-rule을-바꾸지만-구현이-국소적인-fixture에서-agent는-bundlemember-path와-exact-statement를-가진-spec-delta를-먼저-제시하고-사용자-승인-전-기존-canonical-spec을-대체하지-않으며-승인validation-뒤-execution-plan-없이-구현하고-영향받는-canonical-verification-set을-검증한다) | 1, 5 | 작은 지속 계약 변경의 승인·검증 경계 |
| [Quick, 기존 정본 복구, 승인된 Spec Delta 구현의 세 verification fixture에서 각각 focused command, 원래 reproduction과 영향받는 계약, 영향받는 Canonical verification set과 command evidence가 요구되며 Quick fixture에는 전체 spec status 전환이 발생하지 않는다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#quick-기존-정본-복구-승인된-spec-delta-구현의-세-verification-fixture에서-각각-focused-command-원래-reproduction과-영향받는-계약-영향받는-canonical-verification-set과-command-evidence가-요구되며-quick-fixture에는-전체-spec-status-전환이-발생하지-않는다) | 1, 2, 5 | 작업별 증거 범위·부분 완료·불필요한 반복 없음 |
| [한 컴포넌트의 명확하고 가역적인 국소 bug fixture를 실행하면 `docs/specs/`와 `docs/plans/` 변경 없이 원래 reproduction을 실패에서 성공으로 바꾸는 focused test가 fresh evidence로 기록된다.](../../specs/canonical-spec-workflow/routing-and-lifecycle-gates.md#한-컴포넌트의-명확하고-가역적인-국소-bug-fixture를-실행하면-docsspecs와-docsplans-변경-없이-원래-reproduction을-실패에서-성공으로-바꾸는-focused-test가-fresh-evidence로-기록된다) | 2, 5 | 국소 결함 재현·회귀와 불필요한 artifact 없음 |
| [Quick로 시작한 fixture에서 cross-component contract와 migration 순서가 발견되면 agent는 다음 mutation 전에 full lifecycle로 승격하고, 이미 Quick로 시작했다는 이유로 분류를 유지하지 않는다.](../../specs/canonical-spec-workflow/routing-and-lifecycle-gates.md#quick로-시작한-fixture에서-cross-component-contract와-migration-순서가-발견되면-agent는-다음-mutation-전에-full-lifecycle로-승격하고-이미-quick로-시작했다는-이유로-분류를-유지하지-않는다) | 2, 5 | 작은 시작 이후 발견된 공통 계약 영향의 확대 |
| [`Acceptance Criteria`를 생략한 valid one-file bundle과 Acceptance statement를 포함한 valid five-file bundle을 `forge/spec@3`로 작성하면 두 bundle 모두 bundle·member path identity, root metadata, 완전한 `Documents`, 의미 filename과 deterministic bundle hash가 검증되고, five-file bundle만 statement link coverage를 요구하며 서로 다른 추가 section·Mermaid·표 위치를 사용해도 validation이 통과한다.](../../specs/semantic-spec-bundles/authoring-and-file-organization.md#acceptance-criteria를-생략한-valid-one-file-bundle과-acceptance-statement를-포함한-valid-five-file-bundle을-forgespec3로-작성하면-두-bundle-모두-bundlemember-path-identity-root-metadata-완전한-documents-의미-filename과-deterministic-bundle-hash가-검증되고-five-file-bundle만-statement-link-coverage를-요구하며-서로-다른-추가-sectionmermaid표-위치를-사용해도-validation이-통과한다) | 3, 5 | 한 파일·여러 member·Requirement-only의 호환성 |
| [Current source audit를 실행하면 Canonical Spec에는 현재 동작과 제약만 남고 대체된 실행 과정이나 일회성 수치는 active statement와 설명에 나타나지 않는다.](../../specs/semantic-spec-bundles/lifecycle-consumers-and-bundle-replacement.md#current-source-audit를-실행하면-canonical-spec에는-현재-동작과-제약만-남고-대체된-실행-과정이나-일회성-수치는-active-statement와-설명에-나타나지-않는다) | 3, 5 | 현재 계약의 읽기 품질과 이력 분리 |
| [Approved bundle을 읽는 `writing-plans`와 implemented status를 기록하는 `verifying-work` fixture가 공통 parser의 root frontmatter status, bundle·member path와 full statement만으로 lifecycle gate를 적용한다.](../../specs/semantic-spec-bundles/statement-traceability-and-validation.md#approved-bundle을-읽는-writing-plans와-implemented-status를-기록하는-verifying-work-fixture가-공통-parser의-root-frontmatter-status-bundlemember-path와-full-statement만으로-lifecycle-gate를-적용한다) | 4, 5 | lifecycle 판정·신규 상태 강등 회귀 사례 |
| [Approved bundle transition fixture에서 exact one-to-one replacement와 coordinated many-to-one merge만 허용하고 invalid group은 baseline authority를 유지한 채 실패한다.](../../specs/semantic-spec-bundles/lifecycle-consumers-and-bundle-replacement.md#approved-bundle-transition-fixture에서-exact-one-to-one-replacement와-coordinated-many-to-one-merge만-허용하고-invalid-group은-baseline-authority를-유지한-채-실패한다) | 4, 5 | 기존 정상 교체·잘못된 교체 차단 보존 |
| [Claude Code, Codex, Antigravity를 가정한 동일 pressure scenario에서 모든 Forge skill이 path·full-statement 용어, 같은 네 경로와 승격 조건을 선택하고 harness-specific 기능 부재가 spec·plan 필요 여부를 바꾸지 않는다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#claude-code-codex-antigravity를-가정한-동일-pressure-scenario에서-모든-forge-skill이-pathfull-statement-용어-같은-네-경로와-승격-조건을-선택하고-harness-specific-기능-부재가-specplan-필요-여부를-바꾸지-않는다) | 5 | 세 플랫폼 문맥에서 동일한 판단 기준 |
| [현실적인 pressure scenario에서 agent가 canonical source만 수정하고 validation·pressure-test·version gate·push authorization gate를 유지한다.](../../specs/forge-repository-maintenance/forge-repository-maintenance-contract.md#현실적인-pressure-scenario에서-agent가-canonical-source만-수정하고-validationpressure-testversion-gatepush-authorization-gate를-유지한다) | 5 | 정본·검증·배포 gate 보존 |
| [정적 문구 수정, 국소 버그 복원, approved bundle의 부분 구현과 작은 권한 정책 변경 fixture를 실행하면 각 작업은 결과와 위험에 맞는 검증을 사용하고 유효한 증거를 중복 실행하지 않으며, 필요한 계약 검증을 생략하거나 부분 결과로 bundle 전체를 implemented 처리하지 않는다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#정적-문구-수정-국소-버그-복원-approved-bundle의-부분-구현과-작은-권한-정책-변경-fixture를-실행하면-각-작업은-결과와-위험에-맞는-검증을-사용하고-유효한-증거를-중복-실행하지-않으며-필요한-계약-검증을-생략하거나-부분-결과로-bundle-전체를-implemented-처리하지-않는다) | 1, 2, 5 | 작업별 검증·증거 재사용·부분 완료 |
| [여러 조건과 세부 수치를 한 제목에 누적한 Requirement와 관련 bundle에 중복된 공개 tier 계약을 수정하면 각 heading은 독립적인 계약을 표현하고 세부 내용은 본문에 보존되며 owning bundle과 consumer의 승인된 의미가 일치한다.](../../specs/semantic-spec-bundles/authoring-and-file-organization.md#여러-조건과-세부-수치를-한-제목에-누적한-requirement와-관련-bundle에-중복된-공개-tier-계약을-수정하면-각-heading은-독립적인-계약을-표현하고-세부-내용은-본문에-보존되며-owning-bundle과-consumer의-승인된-의미가-일치한다) | 1, 3, 5 | 읽을 수 있는 Requirement와 관련 계약 정합성 |
| [approved와 implemented baseline을 같은 path에서 draft로 바꾸면 validation은 lifecycle downgrade 진단으로 실패하고, implemented에서 approved로 돌아가거나 신규 draft를 추가하는 fixture는 성공한다.](../../specs/semantic-spec-bundles/lifecycle-consumers-and-bundle-replacement.md#approved와-implemented-baseline을-같은-path에서-draft로-바꾸면-validation은-lifecycle-downgrade-진단으로-실패하고-implemented에서-approved로-돌아가거나-신규-draft를-추가하는-fixture는-성공한다) | 1, 4, 5 | active lifecycle 강등 차단과 정상 전환 보존 |

## Tasks

### Task 1: 우선순위와 작업별 완료 범위를 정본 변경안으로 확정한다

Governing statements:

- [하나의 지속적인 business rule을 바꾸지만 구현이 국소적인 fixture에서 agent는 bundle·member path와 exact statement를 가진 Spec Delta를 먼저 제시하고, 사용자 승인 전 기존 Canonical Spec을 대체하지 않으며, 승인·validation 뒤 Execution Plan 없이 구현하고 영향받는 Canonical verification set을 검증한다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#하나의-지속적인-business-rule을-바꾸지만-구현이-국소적인-fixture에서-agent는-bundlemember-path와-exact-statement를-가진-spec-delta를-먼저-제시하고-사용자-승인-전-기존-canonical-spec을-대체하지-않으며-승인validation-뒤-execution-plan-없이-구현하고-영향받는-canonical-verification-set을-검증한다)
- [Quick, 기존 정본 복구, 승인된 Spec Delta 구현의 세 verification fixture에서 각각 focused command, 원래 reproduction과 영향받는 계약, 영향받는 Canonical verification set과 command evidence가 요구되며 Quick fixture에는 전체 spec status 전환이 발생하지 않는다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#quick-기존-정본-복구-승인된-spec-delta-구현의-세-verification-fixture에서-각각-focused-command-원래-reproduction과-영향받는-계약-영향받는-canonical-verification-set과-command-evidence가-요구되며-quick-fixture에는-전체-spec-status-전환이-발생하지-않는다)
- [정적 문구 수정, 국소 버그 복원, approved bundle의 부분 구현과 작은 권한 정책 변경 fixture를 실행하면 각 작업은 결과와 위험에 맞는 검증을 사용하고 유효한 증거를 중복 실행하지 않으며, 필요한 계약 검증을 생략하거나 부분 결과로 bundle 전체를 implemented 처리하지 않는다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#정적-문구-수정-국소-버그-복원-approved-bundle의-부분-구현과-작은-권한-정책-변경-fixture를-실행하면-각-작업은-결과와-위험에-맞는-검증을-사용하고-유효한-증거를-중복-실행하지-않으며-필요한-계약-검증을-생략하거나-부분-결과로-bundle-전체를-implemented-처리하지-않는다)
- [여러 조건과 세부 수치를 한 제목에 누적한 Requirement와 관련 bundle에 중복된 공개 tier 계약을 수정하면 각 heading은 독립적인 계약을 표현하고 세부 내용은 본문에 보존되며 owning bundle과 consumer의 승인된 의미가 일치한다.](../../specs/semantic-spec-bundles/authoring-and-file-organization.md#여러-조건과-세부-수치를-한-제목에-누적한-requirement와-관련-bundle에-중복된-공개-tier-계약을-수정하면-각-heading은-독립적인-계약을-표현하고-세부-내용은-본문에-보존되며-owning-bundle과-consumer의-승인된-의미가-일치한다)
- [approved와 implemented baseline을 같은 path에서 draft로 바꾸면 validation은 lifecycle downgrade 진단으로 실패하고, implemented에서 approved로 돌아가거나 신규 draft를 추가하는 fixture는 성공한다.](../../specs/semantic-spec-bundles/lifecycle-consumers-and-bundle-replacement.md#approved와-implemented-baseline을-같은-path에서-draft로-바꾸면-validation은-lifecycle-downgrade-진단으로-실패하고-implemented에서-approved로-돌아가거나-신규-draft를-추가하는-fixture는-성공한다)

**Files:** `docs/specs/canonical-spec-workflow/`, `docs/specs/semantic-spec-bundles/`, `.forge/work/quality-first-verification/spec-delta.md`, 이 plan.
**Interfaces:** 기존 두 축 분류와 lifecycle 값을 유지한다. “관련 계약 확인 / Markdown 구조 검사 / 동작 검증 / 전체 구현 상태 전환”의 목적·실행 시점을 구분한다.
**Dependencies:** 없음.
**Verification:** 승인될 정확한 문장과 작업별 표가 일치한다. 부분 구현 완료가 전체 상태 승격으로 이어지지 않고, 검증 범위를 줄여도 미해결 계약 위반을 완료로 처리하지 않는다. 정본 반영 뒤 writer transaction이 diagnostics 0으로 끝난다.
**Recovery:** 적용 전 source를 보존하고 baseline 변화 시 영향받은 Delta를 갱신한다.
**Approval gate:** 제안된 정확한 계약 의미. 이후 대화에서 이미 승인된 구체 내용은 재승인받지 않는다.

- [x] **Step 1:** 이 계획의 제안과 현재 규칙의 차이를 exact Delta로 정리하고 신규 검증 사례를 정의한다.
- [x] **Step 2:** 승인된 범위를 반영하고 exact statement 연결과 writer transaction을 확인한다.

### Task 2: 작업 스킬에 검증 선택·재사용·확대·종료 기준을 적용한다

Governing statements:

- [Quick, 기존 정본 복구, 승인된 Spec Delta 구현의 세 verification fixture에서 각각 focused command, 원래 reproduction과 영향받는 계약, 영향받는 Canonical verification set과 command evidence가 요구되며 Quick fixture에는 전체 spec status 전환이 발생하지 않는다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#quick-기존-정본-복구-승인된-spec-delta-구현의-세-verification-fixture에서-각각-focused-command-원래-reproduction과-영향받는-계약-영향받는-canonical-verification-set과-command-evidence가-요구되며-quick-fixture에는-전체-spec-status-전환이-발생하지-않는다)
- [한 컴포넌트의 명확하고 가역적인 국소 bug fixture를 실행하면 `docs/specs/`와 `docs/plans/` 변경 없이 원래 reproduction을 실패에서 성공으로 바꾸는 focused test가 fresh evidence로 기록된다.](../../specs/canonical-spec-workflow/routing-and-lifecycle-gates.md#한-컴포넌트의-명확하고-가역적인-국소-bug-fixture를-실행하면-docsspecs와-docsplans-변경-없이-원래-reproduction을-실패에서-성공으로-바꾸는-focused-test가-fresh-evidence로-기록된다)
- [Quick로 시작한 fixture에서 cross-component contract와 migration 순서가 발견되면 agent는 다음 mutation 전에 full lifecycle로 승격하고, 이미 Quick로 시작했다는 이유로 분류를 유지하지 않는다.](../../specs/canonical-spec-workflow/routing-and-lifecycle-gates.md#quick로-시작한-fixture에서-cross-component-contract와-migration-순서가-발견되면-agent는-다음-mutation-전에-full-lifecycle로-승격하고-이미-quick로-시작했다는-이유로-분류를-유지하지-않는다)
- [정적 문구 수정, 국소 버그 복원, approved bundle의 부분 구현과 작은 권한 정책 변경 fixture를 실행하면 각 작업은 결과와 위험에 맞는 검증을 사용하고 유효한 증거를 중복 실행하지 않으며, 필요한 계약 검증을 생략하거나 부분 결과로 bundle 전체를 implemented 처리하지 않는다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#정적-문구-수정-국소-버그-복원-approved-bundle의-부분-구현과-작은-권한-정책-변경-fixture를-실행하면-각-작업은-결과와-위험에-맞는-검증을-사용하고-유효한-증거를-중복-실행하지-않으며-필요한-계약-검증을-생략하거나-부분-결과로-bundle-전체를-implemented-처리하지-않는다)

**Files:** `plugins/forge/skills/using-forge/SKILL.md`, `plugins/forge/skills/verifying-work/SKILL.md`, `plugins/forge/skills/systematic-debugging/SKILL.md`, `plugins/forge/skills/test-driven-development/SKILL.md`, `plugins/forge/skills/writing-plans/SKILL.md`, `plugins/forge/skills/executing-plans/SKILL.md`, `plugins/forge/skills/writing-plans/references/plan-visual-structure.md`, `plugins/forge/skills/executing-plans/references/adaptive-routing.md`.
**Interfaces:** router는 영향 범위 판단, verifying-work는 공통 증거·완료 기준을 소유한다. 전문 스킬은 이를 참조하고 전문 검증만 추가한다. 재사용을 위한 새 필수 양식이나 점수표는 만들지 않는다.
**Dependencies:** Task 1.
**Verification:** 아래 시나리오의 단순 변경·국소 결함·부분 구현·공통 영향·증거 재사용 판단을 자체 검토하고, Task 5에서 실제 pressure test로 확인한다. 한 번의 재현 테스트로 충족되는 관찰을 별도 중복 실행으로 요구하지 않는다.
**Recovery:** 충돌하는 문구가 남으면 owning skill의 기준으로 정리하고 영향받은 시나리오만 재검토한다.
**Approval gate:** Task 1에서 승인된 의미 내에서는 없음.

- [x] **Step 1:** 반복 실행이나 전체 검증으로 해석되는 문구를 찾아 공통 기준으로 교체한다.
- [x] **Step 2:** 작은 작업과 위험한 작은 변경을 비교 검토하고, 빠른 처리 때문에 필요한 보호가 빠지지 않는지 확인한다.

계획 템플릿과 현재 parser가 받는 정확한 `Governing statements:` 표기를 일치시킨다. 이 계획 작성 중 확인한 형식 불일치이며, 지침이 만드는 정상 문서가 불필요한 재작업 없이 검증되어야 한다.

### Task 3: 스펙을 짧고 정확하게 작성하고 영향받는 계약을 함께 확인하게 한다

Governing statements:

- [`Acceptance Criteria`를 생략한 valid one-file bundle과 Acceptance statement를 포함한 valid five-file bundle을 `forge/spec@3`로 작성하면 두 bundle 모두 bundle·member path identity, root metadata, 완전한 `Documents`, 의미 filename과 deterministic bundle hash가 검증되고, five-file bundle만 statement link coverage를 요구하며 서로 다른 추가 section·Mermaid·표 위치를 사용해도 validation이 통과한다.](../../specs/semantic-spec-bundles/authoring-and-file-organization.md#acceptance-criteria를-생략한-valid-one-file-bundle과-acceptance-statement를-포함한-valid-five-file-bundle을-forgespec3로-작성하면-두-bundle-모두-bundlemember-path-identity-root-metadata-완전한-documents-의미-filename과-deterministic-bundle-hash가-검증되고-five-file-bundle만-statement-link-coverage를-요구하며-서로-다른-추가-sectionmermaid표-위치를-사용해도-validation이-통과한다)
- [Current source audit를 실행하면 Canonical Spec에는 현재 동작과 제약만 남고 대체된 실행 과정이나 일회성 수치는 active statement와 설명에 나타나지 않는다.](../../specs/semantic-spec-bundles/lifecycle-consumers-and-bundle-replacement.md#current-source-audit를-실행하면-canonical-spec에는-현재-동작과-제약만-남고-대체된-실행-과정이나-일회성-수치는-active-statement와-설명에-나타나지-않는다)
- [여러 조건과 세부 수치를 한 제목에 누적한 Requirement와 관련 bundle에 중복된 공개 tier 계약을 수정하면 각 heading은 독립적인 계약을 표현하고 세부 내용은 본문에 보존되며 owning bundle과 consumer의 승인된 의미가 일치한다.](../../specs/semantic-spec-bundles/authoring-and-file-organization.md#여러-조건과-세부-수치를-한-제목에-누적한-requirement와-관련-bundle에-중복된-공개-tier-계약을-수정하면-각-heading은-독립적인-계약을-표현하고-세부-내용은-본문에-보존되며-owning-bundle과-consumer의-승인된-의미가-일치한다)

**Files:** `plugins/forge/skills/writing-specs/SKILL.md`, `plugins/forge/skills/writing-specs/references/spec-template.md`, `plugins/forge/skills/writing-specs/references/spec-delta-template.md`, Task 1에서 승인한 관련 정본.
**Interfaces:** 완전한 문장의 heading·exact links를 유지한다. 한 요구사항은 독립적으로 판단 가능한 한 조건·동작을 설명하고, 수치·예시·예외·상세는 본문 또는 독립 요구사항에 둔다. 목적·담당 범위와 필수 제약을 앞에서 이해할 수 있게 한다.
**Dependencies:** Task 1, Task 2.
**Verification:** 긴 제목·draft의 정본 주장·중복된 tier 설명 사례를 익명화한 임시 문서로 비교한다. 읽기 편하게 줄이는 과정에서 의미·예외·검증 가능성을 잃지 않고, 변경한 heading의 모든 참조가 해석된다.
**Recovery:** 의미 보존이 불명확한 축약은 원문을 유지하고 해당 판단만 Delta에 남긴다.
**Approval gate:** 승인 범위 밖의 요구 의미 변경만 해당한다.

- [x] **Step 1:** 신규·변경 문서에 적용할 작성 기준과 서로 다른 문서의 같은 계약을 대조할 시점을 추가한다.
- [x] **Step 2:** 참고 사례를 임시 복사본에서 검토하고 의미·lifecycle·링크 보존 결과를 기록한다.

추가 제약: 자연어 제목 길이를 일률적인 실패 기준으로 삼지 않는다. 모든 작업에서 전역 중복 검색을 하지 않는다. 공개 계약·권한·저장 형식·책임 경계를 바꿀 때 owning bundle과 해당 계약을 소비하거나 반복하는 문서까지 확인한다. draft를 승인된 근거 없이 승격하지 않는다.

### Task 4: 기존 SOT의 상태 후퇴를 검증기에서 차단한다

Governing statements:

- [Approved bundle을 읽는 `writing-plans`와 implemented status를 기록하는 `verifying-work` fixture가 공통 parser의 root frontmatter status, bundle·member path와 full statement만으로 lifecycle gate를 적용한다.](../../specs/semantic-spec-bundles/statement-traceability-and-validation.md#approved-bundle을-읽는-writing-plans와-implemented-status를-기록하는-verifying-work-fixture가-공통-parser의-root-frontmatter-status-bundlemember-path와-full-statement만으로-lifecycle-gate를-적용한다)
- [Approved bundle transition fixture에서 exact one-to-one replacement와 coordinated many-to-one merge만 허용하고 invalid group은 baseline authority를 유지한 채 실패한다.](../../specs/semantic-spec-bundles/lifecycle-consumers-and-bundle-replacement.md#approved-bundle-transition-fixture에서-exact-one-to-one-replacement와-coordinated-many-to-one-merge만-허용하고-invalid-group은-baseline-authority를-유지한-채-실패한다)
- [approved와 implemented baseline을 같은 path에서 draft로 바꾸면 validation은 lifecycle downgrade 진단으로 실패하고, implemented에서 approved로 돌아가거나 신규 draft를 추가하는 fixture는 성공한다.](../../specs/semantic-spec-bundles/lifecycle-consumers-and-bundle-replacement.md#approved와-implemented-baseline을-같은-path에서-draft로-바꾸면-validation은-lifecycle-downgrade-진단으로-실패하고-implemented에서-approved로-돌아가거나-신규-draft를-추가하는-fixture는-성공한다)

**Files:** `plugins/forge/skills/writing-specs/scripts/spec_validate.py`, `plugins/forge/skills/writing-specs/tests/test_spec_bundle_validate.py`, `plugins/forge/skills/writing-specs/tests/test_spec_docs_cli.py`; 새 진단을 설명하는 승인된 정본.
**Interfaces:** baseline-aware validation에서 기존 approved 또는 implemented bundle을 draft로 내리는 변경을 거부한다. `implemented → approved`는 승인된 계약 변경의 정상 경로로 보존한다. 신규 draft·draft 편집·기존 transition 계약도 보존한다.
**Dependencies:** Task 1.
**Verification:** 상태 강등 실패, 정상 변경·신규 draft 성공, 잘못된 transition 실패를 실제 임시 Git repository로 검증한다. baseline 없는 validation의 보장 범위를 과장하지 않는다.
**Recovery:** 새로운 진단으로 기존 정상 변경이 막히면 해당 사례를 실패 테스트로 추가하고 조건을 좁힌다.
**Approval gate:** Task 1에서 정해진 상태 계약 내에서는 없음.

- [x] **Step 1:** 두 active 상태의 draft 강등을 허용하는 현재 동작을 RED로 고정한다.
- [x] **Step 2:** 좁은 조건으로 차단하고 관련 validator·CLI·transition 회귀를 통과한다.

같은 상태에서 자연어 본문이 변경됐다는 사실만으로 의미의 옳고 그름이나 승인 여부를 기계 판정하지 않는다. 그 부분은 Delta 비교·승인·내용 검토가 담당한다. 이번 작업에 모든 코드 수정의 승인 증명 파일이나 전역 감사 체계를 추가하지 않는다.

### Task 5: 실제 작업 시나리오로 완성도 보존과 과잉 절차 감소를 함께 검증한다

Governing statements:

- [하나의 지속적인 business rule을 바꾸지만 구현이 국소적인 fixture에서 agent는 bundle·member path와 exact statement를 가진 Spec Delta를 먼저 제시하고, 사용자 승인 전 기존 Canonical Spec을 대체하지 않으며, 승인·validation 뒤 Execution Plan 없이 구현하고 영향받는 Canonical verification set을 검증한다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#하나의-지속적인-business-rule을-바꾸지만-구현이-국소적인-fixture에서-agent는-bundlemember-path와-exact-statement를-가진-spec-delta를-먼저-제시하고-사용자-승인-전-기존-canonical-spec을-대체하지-않으며-승인validation-뒤-execution-plan-없이-구현하고-영향받는-canonical-verification-set을-검증한다)
- [Quick, 기존 정본 복구, 승인된 Spec Delta 구현의 세 verification fixture에서 각각 focused command, 원래 reproduction과 영향받는 계약, 영향받는 Canonical verification set과 command evidence가 요구되며 Quick fixture에는 전체 spec status 전환이 발생하지 않는다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#quick-기존-정본-복구-승인된-spec-delta-구현의-세-verification-fixture에서-각각-focused-command-원래-reproduction과-영향받는-계약-영향받는-canonical-verification-set과-command-evidence가-요구되며-quick-fixture에는-전체-spec-status-전환이-발생하지-않는다)
- [한 컴포넌트의 명확하고 가역적인 국소 bug fixture를 실행하면 `docs/specs/`와 `docs/plans/` 변경 없이 원래 reproduction을 실패에서 성공으로 바꾸는 focused test가 fresh evidence로 기록된다.](../../specs/canonical-spec-workflow/routing-and-lifecycle-gates.md#한-컴포넌트의-명확하고-가역적인-국소-bug-fixture를-실행하면-docsspecs와-docsplans-변경-없이-원래-reproduction을-실패에서-성공으로-바꾸는-focused-test가-fresh-evidence로-기록된다)
- [Quick로 시작한 fixture에서 cross-component contract와 migration 순서가 발견되면 agent는 다음 mutation 전에 full lifecycle로 승격하고, 이미 Quick로 시작했다는 이유로 분류를 유지하지 않는다.](../../specs/canonical-spec-workflow/routing-and-lifecycle-gates.md#quick로-시작한-fixture에서-cross-component-contract와-migration-순서가-발견되면-agent는-다음-mutation-전에-full-lifecycle로-승격하고-이미-quick로-시작했다는-이유로-분류를-유지하지-않는다)
- [`Acceptance Criteria`를 생략한 valid one-file bundle과 Acceptance statement를 포함한 valid five-file bundle을 `forge/spec@3`로 작성하면 두 bundle 모두 bundle·member path identity, root metadata, 완전한 `Documents`, 의미 filename과 deterministic bundle hash가 검증되고, five-file bundle만 statement link coverage를 요구하며 서로 다른 추가 section·Mermaid·표 위치를 사용해도 validation이 통과한다.](../../specs/semantic-spec-bundles/authoring-and-file-organization.md#acceptance-criteria를-생략한-valid-one-file-bundle과-acceptance-statement를-포함한-valid-five-file-bundle을-forgespec3로-작성하면-두-bundle-모두-bundlemember-path-identity-root-metadata-완전한-documents-의미-filename과-deterministic-bundle-hash가-검증되고-five-file-bundle만-statement-link-coverage를-요구하며-서로-다른-추가-sectionmermaid표-위치를-사용해도-validation이-통과한다)
- [Current source audit를 실행하면 Canonical Spec에는 현재 동작과 제약만 남고 대체된 실행 과정이나 일회성 수치는 active statement와 설명에 나타나지 않는다.](../../specs/semantic-spec-bundles/lifecycle-consumers-and-bundle-replacement.md#current-source-audit를-실행하면-canonical-spec에는-현재-동작과-제약만-남고-대체된-실행-과정이나-일회성-수치는-active-statement와-설명에-나타나지-않는다)
- [Approved bundle을 읽는 `writing-plans`와 implemented status를 기록하는 `verifying-work` fixture가 공통 parser의 root frontmatter status, bundle·member path와 full statement만으로 lifecycle gate를 적용한다.](../../specs/semantic-spec-bundles/statement-traceability-and-validation.md#approved-bundle을-읽는-writing-plans와-implemented-status를-기록하는-verifying-work-fixture가-공통-parser의-root-frontmatter-status-bundlemember-path와-full-statement만으로-lifecycle-gate를-적용한다)
- [Approved bundle transition fixture에서 exact one-to-one replacement와 coordinated many-to-one merge만 허용하고 invalid group은 baseline authority를 유지한 채 실패한다.](../../specs/semantic-spec-bundles/lifecycle-consumers-and-bundle-replacement.md#approved-bundle-transition-fixture에서-exact-one-to-one-replacement와-coordinated-many-to-one-merge만-허용하고-invalid-group은-baseline-authority를-유지한-채-실패한다)
- [Claude Code, Codex, Antigravity를 가정한 동일 pressure scenario에서 모든 Forge skill이 path·full-statement 용어, 같은 네 경로와 승격 조건을 선택하고 harness-specific 기능 부재가 spec·plan 필요 여부를 바꾸지 않는다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#claude-code-codex-antigravity를-가정한-동일-pressure-scenario에서-모든-forge-skill이-pathfull-statement-용어-같은-네-경로와-승격-조건을-선택하고-harness-specific-기능-부재가-specplan-필요-여부를-바꾸지-않는다)
- [현실적인 pressure scenario에서 agent가 canonical source만 수정하고 validation·pressure-test·version gate·push authorization gate를 유지한다.](../../specs/forge-repository-maintenance/forge-repository-maintenance-contract.md#현실적인-pressure-scenario에서-agent가-canonical-source만-수정하고-validationpressure-testversion-gatepush-authorization-gate를-유지한다)
- [정적 문구 수정, 국소 버그 복원, approved bundle의 부분 구현과 작은 권한 정책 변경 fixture를 실행하면 각 작업은 결과와 위험에 맞는 검증을 사용하고 유효한 증거를 중복 실행하지 않으며, 필요한 계약 검증을 생략하거나 부분 결과로 bundle 전체를 implemented 처리하지 않는다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#정적-문구-수정-국소-버그-복원-approved-bundle의-부분-구현과-작은-권한-정책-변경-fixture를-실행하면-각-작업은-결과와-위험에-맞는-검증을-사용하고-유효한-증거를-중복-실행하지-않으며-필요한-계약-검증을-생략하거나-부분-결과로-bundle-전체를-implemented-처리하지-않는다)
- [여러 조건과 세부 수치를 한 제목에 누적한 Requirement와 관련 bundle에 중복된 공개 tier 계약을 수정하면 각 heading은 독립적인 계약을 표현하고 세부 내용은 본문에 보존되며 owning bundle과 consumer의 승인된 의미가 일치한다.](../../specs/semantic-spec-bundles/authoring-and-file-organization.md#여러-조건과-세부-수치를-한-제목에-누적한-requirement와-관련-bundle에-중복된-공개-tier-계약을-수정하면-각-heading은-독립적인-계약을-표현하고-세부-내용은-본문에-보존되며-owning-bundle과-consumer의-승인된-의미가-일치한다)
- [approved와 implemented baseline을 같은 path에서 draft로 바꾸면 validation은 lifecycle downgrade 진단으로 실패하고, implemented에서 approved로 돌아가거나 신규 draft를 추가하는 fixture는 성공한다.](../../specs/semantic-spec-bundles/lifecycle-consumers-and-bundle-replacement.md#approved와-implemented-baseline을-같은-path에서-draft로-바꾸면-validation은-lifecycle-downgrade-진단으로-실패하고-implemented에서-approved로-돌아가거나-신규-draft를-추가하는-fixture는-성공한다)

**Files:** `scripts/tests/test-forge-lifecycle-policy.sh`, `scripts/tests/test-forge-spec-docs-policy.sh`, `README.md`, 필요한 portability reference 원본, 이 plan의 Progress History. 임시 pressure transcript는 `.forge/scratch/quality-first-verification/`에 둔다.
**Interfaces:** 정책의 기계 검사와 agent 행동 검증을 구분한다. 포터빌리티 reference는 소유 canonical source에서 수정하고 필요할 때 manager로 adapter parity를 확인한다.
**Dependencies:** Tasks 2, 3, 4.
**Verification:** 아래 각 시나리오에서 요청 결과·관련 계약·필요한 검증을 만족하고, 표에 적힌 불필요한 작업을 추가하지 않는다. 지침 변경에 맞춘 새 agent pressure test와 실제 transcript 검토를 수행한다. 도구가 없는 플랫폼은 문맥 모사와 native 실행을 구분해 보고한다.
**Recovery:** 실패한 판단의 owning skill을 수정하고 해당 시나리오와 직접 영향받은 회귀만 다시 실행한다.
**Approval gate:** 없음. 사용자가 이 변경의 push·merge·배포를 명시적으로 승인했다.

- [x] **Step 1:** 정책 검사·README·portability 설명을 승인된 의미에 맞추고 아래 시나리오를 실행한다.
- [x] **Step 2:** 필요한 회귀와 최종 validation을 통과한 뒤 결과·한계·남은 작업을 보고한다.
- [x] **Step 3:** PR을 `main`에 병합하고 push 기반 배포 workflow 성공을 확인한 뒤 계획을 완료 처리한다.

## 작업 시나리오와 완료 판단

| 시나리오 | 반드시 확인할 결과 | 과잉 작업 방지 |
|---|---|---|
| README 오탈자·정적 label·CSS 간격 | 의미 보존과 실제 변경 결과 | 새 테스트 프레임워크·spec 전체 inspect·전체 suite 없음 |
| 국소 off-by-one 버그 | 원래 실패가 성공으로 바뀌고 관련 계약·회귀 충족 | 하나의 실행으로 증명된 결과를 역할별로 반복 실행하지 않음 |
| 한 줄짜리 권한·요금 정책 | 지속 계약 변경으로 분류하고 승인·관련 경계 검증 | 줄 수로 Quick 처리하지 않음; 무관한 전체 UI 검사 없음 |
| approved bundle의 기능 일부 구현 | 선택한 기능·의존 항목 검증과 부분 완료 보고 | 전체 bundle 상태를 올리거나 무관한 미구현 항목을 강제 구현하지 않음 |
| Quick 중 공통 API·저장 형식 영향 발견 | 영향과 필요 경로를 재분류하고 통합·회귀 확대 | 처음 분류를 고집하거나 근거 없이 저장소 전체를 조사하지 않음 |
| 테스트 통과 후 스킬 전환·최종 보고 | 실제 출력과 현재 상태를 확인해 같은 증거 사용 | 같은 suite 재실행 없음 |
| 테스트 통과 후 관련 설정·의존성 변경 | 기존 증거의 영향 부분 무효화와 필요한 재실행 | 과거 PASS 재사용 금지; 영향 없는 검사 중복 없음 |
| 새 실패·불안정 재현·검증 불가 환경 | 실패 원인 또는 미확인 범위를 드러내고 완료 판단 조정 | 통과할 때까지 무의미한 재실행·근거 없는 완료 없음 |
| 서로 다른 스펙의 Basic/Pro 계약 충돌 | 소유권과 승인된 의미 확인 후 관련 문서를 함께 정리 | 코드 동작에 맞춘 무승인 스펙 수정·전체 스펙 일괄 재작성 없음 |
| draft 강등·긴 요구사항 정리 | 상태 후퇴 차단, 의미·링크·가독성 보존 | draft 일괄 승인·새 locator schema 없음 |

각 pressure scenario는 필요한 구현·검증·문서화가 빠졌는지와 불필요한 추가 작업을 했는지를 함께 판정한다. 실행 횟수나 처리 시간의 고정 상한으로 품질을 제한하지 않는다. 충분한 범위와 증거가 확보됐는데도 더 진행하면 그 추가 작업의 구체적 근거를 확인한다.

## 실행 단계의 검증 명령

아래는 구현 후 사용할 명령이며 계획 작성만으로 전부 실행하지 않는다.

- Task 1·3의 정본 변경: `bash plugins/forge/skills/writing-specs/scripts/spec-docs.sh --repo-root . validate --root docs/specs --baseline-ref HEAD`.
- Task 4의 focused 검사: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/forge/skills/writing-specs/tests -p 'test_spec_bundle_validate.py'`.
- Task 4 변경이 반영된 최종 writer 회귀: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/forge/skills/writing-specs/tests -p 'test_spec_*.py'`.
- Task 5의 정책 검사: `bash scripts/tests/test-forge-lifecycle-policy.sh`, `bash scripts/tests/test-forge-spec-docs-policy.sh`.
- 최종 로컬 gate: `bash scripts/validate.sh` → `validate: all checks passed`.
- 변경이 없는 상태에서 확보한 결과를 다음 단계와 최종 보고에 재사용한다. 새 변경·실패·새 영향이 생기면 해당 검사만 갱신한다.
- Outgoing 변경의 version gate를 통과하고 PR을 `main`에 병합한 뒤 push 기반 배포 검증이 성공해야 완료한다.

## Progress History

- 2026-09-06: 사용자의 우선순위와 앞선 조사 결과를 반영해 계획을 작성했다. 기존 세 bundle의 implemented 상태·hash·diagnostics 0을 확인했다. 계획의 Governing statements 표기는 parser 계약에 맞췄으며, 템플릿 불일치 정리는 Task 2에 포함했다. 구현 Tasks는 시작하지 않았다.
- 2026-09-06: 공통 plan parser로 Related Spec 3개·Task statement 연결 19개를 확인했다. 모든 Markdown 대상·anchor, Task 1–5의 미착수 상태와 proposed 상태 검사가 PASS했다. 계획 작성 범위에 맞춰 구현용 테스트 suite는 실행하지 않았다.
- 2026-09-06: 사용자가 수정·push·merge·배포까지 승인했다. Task 1·2·3은 정본과 스킬 문구가 긴밀히 연결되어 root 순차 실행, Task 4는 focused TDD, Task 5는 통합 검증과 release로 routing했다.
- 2026-09-06: Tasks 1–4를 완료했다. Canonical workflow와 semantic bundle 정본을 적용했고, 부분 완료·증거 재사용·검증 종료·Requirement 가독성·관련 계약 정합성 지침을 배포 스킬과 portability reference에 반영했다. Active bundle draft 강등 RED를 unit·CLI에서 확인한 뒤 validator와 PR/push baseline CI를 구현했으며 focused 29 tests, 전체 spec 66 tests, lifecycle/spec policy와 writer transaction이 PASS했다.
- 2026-09-06: 새 agent pressure test에서 다섯 작업 유형의 비례 검증을 확인했다. 발견된 CI baseline 누락, 계획 템플릿 설명, `relevant source` 표현을 수정하고 영향 검증을 다시 통과했다.
- 2026-09-06: Task 5의 로컬 검증을 완료했다. Forge 0.1.21로 version을 올렸고 GitHub Actions main job과 같은 로컬 명령, Visual Docs Python 62 tests, extension manager 17 tests, browser 13 tests, 모든 정책·설치·bundle·writer 검증이 PASS했다. Push·PR·merge와 원격 workflow 확인을 release checkpoint로 남겼다.
- 2026-09-06: PR #4를 `main` merge commit `6f16f1e`로 병합해 Forge 0.1.21을 배포했다. Main push workflow `34022652862`의 validate와 browser job이 모두 PASS해 release checkpoint를 닫고 계획을 완료했다.
