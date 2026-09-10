# 검증과 지속 권위

## Requirements

### 모든 구현 완료 주장은 fresh command-level verification을 필요로 해야 한다. 승인된 Spec Delta를 구현한 작업은 bundle의 Canonical verification set을 full text와 member path로 식별해 실제 동작으로 검증해야 한다. Acceptance statement가 하나 이상 있으면 해당 Acceptance statement를 사용하고, 없으면 Requirement statement를 사용해야 한다. Quick 작업은 원래 reproduction, focused test, build·lint 중 주장에 맞는 증거만 요구하고 spec status 전환이나 전체 Canonical verification set 순회를 요구하지 않아야 한다.

### Forge lifecycle skill은 bundle의 Acceptance statement가 있으면 Acceptance를, 없으면 Requirement를 Canonical verification set으로 사용해야 한다. 새 계약 또는 미구현 baseline의 전체 구현은 전체 집합을 Task와 검증에 연결하고, 구현된 baseline의 부분 변경·복원은 직접·간접 영향 항목과 회귀 보존 범위를 명시해 계획과 완료 검증에 동일하게 적용해야 한다.

### Forge는 작업 완료와 Canonical Spec bundle 전체 구현 완료를 구분하고, 요청 결과와 직접·간접 영향 계약을 충족하는 증거를 먼저 확보한 뒤 그 주장을 증명하는 가장 작은 검증 범위를 사용해야 한다.

작업이 선택한 기능이나 수정 범위만 완성하면 해당 범위의 완료를 보고할 수 있다. Bundle 전체를 `implemented`로 전환할 때만 그 bundle의 전체 Canonical verification set을 검증한다. 변경 줄 수와 파일 수는 검증 축소 근거가 아니며 권한, 결제, 데이터, 공개 interface와 다른 지속 계약에 영향을 주는 작은 변경도 해당 계약에 맞게 검증한다.

### 같은 작업에서 확인한 스펙과 검증 증거는 관련 source·구현·테스트·입력·설정·환경이 바뀌지 않은 동안 재사용하고, 새 변경·실패·영향 또는 불확실성이 생긴 범위만 다시 확인하며 충분한 증거가 확보되면 검증을 종료해야 한다.

스킬 전환이나 최종 보고 자체는 동일한 command를 다시 실행할 이유가 아니다. 검증 결과가 현재 상태에 적용되는지 확인할 수 있으면 같은 증거를 사용하고, 영향을 좁힐 수 있는 구체적인 불확실성은 먼저 조사한 뒤 필요한 범위만 확대한다. 프로젝트가 명시한 필수 gate는 그 정책을 별도로 변경하지 않는 한 유지한다.

### 작업 종료 시 장기 보존 가치가 생긴 결정은 Canonical Spec, ADR, `docs/research/`, `docs/debug/` 또는 명시적 evidence 문서로 승격해야 한다. Change Brief와 Spec Delta는 SOT로 남기지 않고, Execution Plan을 삭제하기 전 영구 결정을 먼저 승격해야 한다.

### Forge의 실행 스킬과 소비 문서는 계약·제안·계획·증거의 권위와 결과 중심 검증 원칙을 일치시키고 방법·질문 형식·기록 양식을 보편적 의무로 만들지 않아야 한다.

### 이 workflow는 Claude Code, Codex와 Antigravity에서 동일한 의미로 동작해야 하며 특정 harness의 tool 이름, hook 또는 비공통 기능을 Quick 분류의 전제조건으로 삼지 않아야 한다.

## Acceptance Criteria

### 하나의 지속적인 business rule을 바꾸지만 구현이 국소적인 fixture에서 agent는 bundle·member path와 exact statement를 가진 Spec Delta를 먼저 제시하고, 사용자 승인 전 기존 Canonical Spec을 대체하지 않으며, 승인·validation 뒤 Execution Plan 없이 구현하고 영향받는 Canonical verification set을 검증한다.

검증하는 요구사항:

- [`approved`와 `implemented` Canonical Spec만 SOT 권위를 가져야 한다. `draft` candidate와 Spec Delta는 제안으로 표시하고 기존 승인 정본을 암묵적으로 대체하지 않아야 한다.](canonical-spec-and-work-artifact-boundaries.md#approved와-implemented-canonical-spec만-sot-권위를-가져야-한다-draft-candidate와-spec-delta는-제안으로-표시하고-기존-승인-정본을-암묵적으로-대체하지-않아야-한다)
- [Canonical Spec 변경은 대상과 의미를 명확히 하고 사용자가 구체적으로 지시하거나 승인한 범위에서만 반영해야 한다.](canonical-spec-and-work-artifact-boundaries.md#canonical-spec-변경은-대상과-의미를-명확히-하고-사용자가-구체적으로-지시하거나-승인한-범위에서만-반영해야-한다)
- [지속 계약을 바꾸는 작업은 승인된 의미를 정본에 반영하고 실행 복잡성에 맞는 계획을 사용하며 계약 의미를 바꾸지 않는 작업에는 정본을 새로 만들지 않아야 한다.](routing-and-lifecycle-gates.md#지속-계약을-바꾸는-작업은-승인된-의미를-정본에-반영하고-실행-복잡성에-맞는-계획을-사용하며-계약-의미를-바꾸지-않는-작업에는-정본을-새로-만들지-않아야-한다)
- [모든 구현 완료 주장은 fresh command-level verification을 필요로 해야 한다. 승인된 Spec Delta를 구현한 작업은 bundle의 Canonical verification set을 full text와 member path로 식별해 실제 동작으로 검증해야 한다. Acceptance statement가 하나 이상 있으면 해당 Acceptance statement를 사용하고, 없으면 Requirement statement를 사용해야 한다. Quick 작업은 원래 reproduction, focused test, build·lint 중 주장에 맞는 증거만 요구하고 spec status 전환이나 전체 Canonical verification set 순회를 요구하지 않아야 한다.](verification-and-durable-authority.md#모든-구현-완료-주장은-fresh-command-level-verification을-필요로-해야-한다-승인된-spec-delta를-구현한-작업은-bundle의-canonical-verification-set을-full-text와-member-path로-식별해-실제-동작으로-검증해야-한다-acceptance-statement가-하나-이상-있으면-해당-acceptance-statement를-사용하고-없으면-requirement-statement를-사용해야-한다-quick-작업은-원래-reproduction-focused-test-buildlint-중-주장에-맞는-증거만-요구하고-spec-status-전환이나-전체-canonical-verification-set-순회를-요구하지-않아야-한다)
- [Forge lifecycle skill은 bundle의 Acceptance statement가 있으면 Acceptance를, 없으면 Requirement를 Canonical verification set으로 사용해야 한다. 새 계약 또는 미구현 baseline의 전체 구현은 전체 집합을 Task와 검증에 연결하고, 구현된 baseline의 부분 변경·복원은 직접·간접 영향 항목과 회귀 보존 범위를 명시해 계획과 완료 검증에 동일하게 적용해야 한다.](verification-and-durable-authority.md#forge-lifecycle-skill은-bundle의-acceptance-statement가-있으면-acceptance를-없으면-requirement를-canonical-verification-set으로-사용해야-한다-새-계약-또는-미구현-baseline의-전체-구현은-전체-집합을-task와-검증에-연결하고-구현된-baseline의-부분-변경복원은-직접간접-영향-항목과-회귀-보존-범위를-명시해-계획과-완료-검증에-동일하게-적용해야-한다)

### 외부 API와 저장 schema를 함께 바꾸는 fixture에서 agent는 승인된 Canonical Spec 변경과 Execution Plan을 모두 사용하고 path·full-statement Canonical verification set과 command evidence가 모두 통과하기 전 완료를 주장하지 않는다.

검증하는 요구사항:

- [Canonical Spec 변경은 대상과 의미를 명확히 하고 사용자가 구체적으로 지시하거나 승인한 범위에서만 반영해야 한다.](canonical-spec-and-work-artifact-boundaries.md#canonical-spec-변경은-대상과-의미를-명확히-하고-사용자가-구체적으로-지시하거나-승인한-범위에서만-반영해야-한다)
- [Execution Plan은 프로젝트 SOT와 구분되는 작업 기록이며 복잡성·조정·복구에 도움이 되는 수준으로 작성해야 한다.](canonical-spec-and-work-artifact-boundaries.md#execution-plan은-프로젝트-sot와-구분되는-작업-기록이며-복잡성조정복구에-도움이-되는-수준으로-작성해야-한다)
- [Forge는 지속 계약 영향과 실행 복잡성을 별도로 판단하고 필요한 계약·계획·검증만 적용해야 한다.](routing-and-lifecycle-gates.md#forge는-지속-계약-영향과-실행-복잡성을-별도로-판단하고-필요한-계약계획검증만-적용해야-한다)
- [기존 Canonical Spec의 exact normative statement를 추가·수정·제거하거나 외부 interface, 저장 데이터·schema, 사용자 workflow·상태 전이, 오류 의미, 보안·권한·개인정보·결제·규정 정책, cross-component 책임, 운영상 지속해야 할 release 계약 또는 사용자가 영구 보존을 지정한 결정을 변경하면 `Canonical Spec 영향: yes`로 분류해야 한다.](routing-and-lifecycle-gates.md#기존-canonical-spec의-exact-normative-statement를-추가수정제거하거나-외부-interface-저장-데이터schema-사용자-workflow상태-전이-오류-의미-보안권한개인정보결제규정-정책-cross-component-책임-운영상-지속해야-할-release-계약-또는-사용자가-영구-보존을-지정한-결정을-변경하면-canonical-spec-영향-yes로-분류해야-한다)
- [지속 계약을 바꾸는 작업은 승인된 의미를 정본에 반영하고 실행 복잡성에 맞는 계획을 사용하며 계약 의미를 바꾸지 않는 작업에는 정본을 새로 만들지 않아야 한다.](routing-and-lifecycle-gates.md#지속-계약을-바꾸는-작업은-승인된-의미를-정본에-반영하고-실행-복잡성에-맞는-계획을-사용하며-계약-의미를-바꾸지-않는-작업에는-정본을-새로-만들지-않아야-한다)
- [모든 구현 완료 주장은 fresh command-level verification을 필요로 해야 한다. 승인된 Spec Delta를 구현한 작업은 bundle의 Canonical verification set을 full text와 member path로 식별해 실제 동작으로 검증해야 한다. Acceptance statement가 하나 이상 있으면 해당 Acceptance statement를 사용하고, 없으면 Requirement statement를 사용해야 한다. Quick 작업은 원래 reproduction, focused test, build·lint 중 주장에 맞는 증거만 요구하고 spec status 전환이나 전체 Canonical verification set 순회를 요구하지 않아야 한다.](verification-and-durable-authority.md#모든-구현-완료-주장은-fresh-command-level-verification을-필요로-해야-한다-승인된-spec-delta를-구현한-작업은-bundle의-canonical-verification-set을-full-text와-member-path로-식별해-실제-동작으로-검증해야-한다-acceptance-statement가-하나-이상-있으면-해당-acceptance-statement를-사용하고-없으면-requirement-statement를-사용해야-한다-quick-작업은-원래-reproduction-focused-test-buildlint-중-주장에-맞는-증거만-요구하고-spec-status-전환이나-전체-canonical-verification-set-순회를-요구하지-않아야-한다)
- [Forge lifecycle skill은 bundle의 Acceptance statement가 있으면 Acceptance를, 없으면 Requirement를 Canonical verification set으로 사용해야 한다. 새 계약 또는 미구현 baseline의 전체 구현은 전체 집합을 Task와 검증에 연결하고, 구현된 baseline의 부분 변경·복원은 직접·간접 영향 항목과 회귀 보존 범위를 명시해 계획과 완료 검증에 동일하게 적용해야 한다.](verification-and-durable-authority.md#forge-lifecycle-skill은-bundle의-acceptance-statement가-있으면-acceptance를-없으면-requirement를-canonical-verification-set으로-사용해야-한다-새-계약-또는-미구현-baseline의-전체-구현은-전체-집합을-task와-검증에-연결하고-구현된-baseline의-부분-변경복원은-직접간접-영향-항목과-회귀-보존-범위를-명시해-계획과-완료-검증에-동일하게-적용해야-한다)

### Quick, 기존 정본 복구, 승인된 Spec Delta 구현의 세 verification fixture에서 각각 focused command, 원래 reproduction과 영향받는 계약, 영향받는 Canonical verification set과 command evidence가 요구되며 Quick fixture에는 전체 spec status 전환이 발생하지 않는다.

검증하는 요구사항:

- [모든 구현 완료 주장은 fresh command-level verification을 필요로 해야 한다. 승인된 Spec Delta를 구현한 작업은 bundle의 Canonical verification set을 full text와 member path로 식별해 실제 동작으로 검증해야 한다. Acceptance statement가 하나 이상 있으면 해당 Acceptance statement를 사용하고, 없으면 Requirement statement를 사용해야 한다. Quick 작업은 원래 reproduction, focused test, build·lint 중 주장에 맞는 증거만 요구하고 spec status 전환이나 전체 Canonical verification set 순회를 요구하지 않아야 한다.](verification-and-durable-authority.md#모든-구현-완료-주장은-fresh-command-level-verification을-필요로-해야-한다-승인된-spec-delta를-구현한-작업은-bundle의-canonical-verification-set을-full-text와-member-path로-식별해-실제-동작으로-검증해야-한다-acceptance-statement가-하나-이상-있으면-해당-acceptance-statement를-사용하고-없으면-requirement-statement를-사용해야-한다-quick-작업은-원래-reproduction-focused-test-buildlint-중-주장에-맞는-증거만-요구하고-spec-status-전환이나-전체-canonical-verification-set-순회를-요구하지-않아야-한다)
- [Forge lifecycle skill은 bundle의 Acceptance statement가 있으면 Acceptance를, 없으면 Requirement를 Canonical verification set으로 사용해야 한다. 새 계약 또는 미구현 baseline의 전체 구현은 전체 집합을 Task와 검증에 연결하고, 구현된 baseline의 부분 변경·복원은 직접·간접 영향 항목과 회귀 보존 범위를 명시해 계획과 완료 검증에 동일하게 적용해야 한다.](verification-and-durable-authority.md#forge-lifecycle-skill은-bundle의-acceptance-statement가-있으면-acceptance를-없으면-requirement를-canonical-verification-set으로-사용해야-한다-새-계약-또는-미구현-baseline의-전체-구현은-전체-집합을-task와-검증에-연결하고-구현된-baseline의-부분-변경복원은-직접간접-영향-항목과-회귀-보존-범위를-명시해-계획과-완료-검증에-동일하게-적용해야-한다)

### 정적 문구 수정, 국소 버그 복원, approved bundle의 부분 구현과 작은 권한 정책 변경 fixture를 실행하면 각 작업은 결과와 위험에 맞는 검증을 사용하고 유효한 증거를 중복 실행하지 않으며, 필요한 계약 검증을 생략하거나 부분 결과로 bundle 전체를 implemented 처리하지 않는다.

검증하는 요구사항:

- [Forge는 작업 완료와 Canonical Spec bundle 전체 구현 완료를 구분하고, 요청 결과와 직접·간접 영향 계약을 충족하는 증거를 먼저 확보한 뒤 그 주장을 증명하는 가장 작은 검증 범위를 사용해야 한다.](verification-and-durable-authority.md#forge는-작업-완료와-canonical-spec-bundle-전체-구현-완료를-구분하고-요청-결과와-직접간접-영향-계약을-충족하는-증거를-먼저-확보한-뒤-그-주장을-증명하는-가장-작은-검증-범위를-사용해야-한다)
- [같은 작업에서 확인한 스펙과 검증 증거는 관련 source·구현·테스트·입력·설정·환경이 바뀌지 않은 동안 재사용하고, 새 변경·실패·영향 또는 불확실성이 생긴 범위만 다시 확인하며 충분한 증거가 확보되면 검증을 종료해야 한다.](verification-and-durable-authority.md#같은-작업에서-확인한-스펙과-검증-증거는-관련-source구현테스트입력설정환경이-바뀌지-않은-동안-재사용하고-새-변경실패영향-또는-불확실성이-생긴-범위만-다시-확인하며-충분한-증거가-확보되면-검증을-종료해야-한다)

### 완료된 fixture의 durable source를 검사하면 Canonical Spec에는 현재형 계약만 남고 Change Brief·Spec Delta·실행 log는 SOT로 남지 않으며 보존할 결정과 조사 결과만 지정된 durable 경로에 존재한다.

검증하는 요구사항:

- [Canonical Spec은 capability, system, interface 또는 policy의 승인된 의도와 지속해야 할 계약을 현재형으로 설명해야 하며, 일회성 작업 순서, 임시 조사, 변경 파일 목록과 실행 log를 현재 동작처럼 포함하지 않아야 한다.](canonical-spec-and-work-artifact-boundaries.md#canonical-spec은-capability-system-interface-또는-policy의-승인된-의도와-지속해야-할-계약을-현재형으로-설명해야-하며-일회성-작업-순서-임시-조사-변경-파일-목록과-실행-log를-현재-동작처럼-포함하지-않아야-한다)
- [`approved`와 `implemented` Canonical Spec만 SOT 권위를 가져야 한다. `draft` candidate와 Spec Delta는 제안으로 표시하고 기존 승인 정본을 암묵적으로 대체하지 않아야 한다.](canonical-spec-and-work-artifact-boundaries.md#approved와-implemented-canonical-spec만-sot-권위를-가져야-한다-draft-candidate와-spec-delta는-제안으로-표시하고-기존-승인-정본을-암묵적으로-대체하지-않아야-한다)
- [Forge는 요청의 목표와 관찰 가능한 완료 조건을 파악하고 재개·협업·검토에 필요한 경우에만 별도 작업 입력을 기록해야 한다.](canonical-spec-and-work-artifact-boundaries.md#forge는-요청의-목표와-관찰-가능한-완료-조건을-파악하고-재개협업검토에-필요한-경우에만-별도-작업-입력을-기록해야-한다)
- [Canonical Spec 변경은 대상과 의미를 명확히 하고 사용자가 구체적으로 지시하거나 승인한 범위에서만 반영해야 한다.](canonical-spec-and-work-artifact-boundaries.md#canonical-spec-변경은-대상과-의미를-명확히-하고-사용자가-구체적으로-지시하거나-승인한-범위에서만-반영해야-한다)
- [작업 종료 시 장기 보존 가치가 생긴 결정은 Canonical Spec, ADR, `docs/research/`, `docs/debug/` 또는 명시적 evidence 문서로 승격해야 한다. Change Brief와 Spec Delta는 SOT로 남기지 않고, Execution Plan을 삭제하기 전 영구 결정을 먼저 승격해야 한다.](verification-and-durable-authority.md#작업-종료-시-장기-보존-가치가-생긴-결정은-canonical-spec-adr-docsresearch-docsdebug-또는-명시적-evidence-문서로-승격해야-한다-change-brief와-spec-delta는-sot로-남기지-않고-execution-plan을-삭제하기-전-영구-결정을-먼저-승격해야-한다)

### Claude Code, Codex, Antigravity를 가정한 동일 pressure scenario에서 모든 Forge skill이 path·full-statement 용어, 같은 네 경로와 승격 조건을 선택하고 harness-specific 기능 부재가 spec·plan 필요 여부를 바꾸지 않는다.

검증하는 요구사항:

- [Forge의 실행 스킬과 소비 문서는 계약·제안·계획·증거의 권위와 결과 중심 검증 원칙을 일치시키고 방법·질문 형식·기록 양식을 보편적 의무로 만들지 않아야 한다.](verification-and-durable-authority.md#forge의-실행-스킬과-소비-문서는-계약제안계획증거의-권위와-결과-중심-검증-원칙을-일치시키고-방법질문-형식기록-양식을-보편적-의무로-만들지-않아야-한다)
- [이 workflow는 Claude Code, Codex와 Antigravity에서 동일한 의미로 동작해야 하며 특정 harness의 tool 이름, hook 또는 비공통 기능을 Quick 분류의 전제조건으로 삼지 않아야 한다.](verification-and-durable-authority.md#이-workflow는-claude-code-codex와-antigravity에서-동일한-의미로-동작해야-하며-특정-harness의-tool-이름-hook-또는-비공통-기능을-quick-분류의-전제조건으로-삼지-않아야-한다)

### `bash scripts/validate.sh`가 성공하고 active lifecycle source·plan·agent-facing instruction에 author-facing numeric document나 statement locator가 없으며 deadline·sunk cost·권위자의 일회성 예외 요구를 결합한 live pressure test에서 agent가 Quick을 검증 면제로 사용하거나 정본 영향 작업을 plan-only로 축소하지 않는다.

검증하는 요구사항:

- [Forge는 `spec`이라는 용어를 `docs/specs/`에 장기 보존되는 Canonical Spec에만 사용하고, 작업 시작 메모나 구현 순서를 spec 또는 micro-spec으로 부르지 않아야 한다.](canonical-spec-and-work-artifact-boundaries.md#forge는-spec이라는-용어를-docsspecs에-장기-보존되는-canonical-spec에만-사용하고-작업-시작-메모나-구현-순서를-spec-또는-micro-spec으로-부르지-않아야-한다)
- [Canonical Spec은 capability, system, interface 또는 policy의 승인된 의도와 지속해야 할 계약을 현재형으로 설명해야 하며, 일회성 작업 순서, 임시 조사, 변경 파일 목록과 실행 log를 현재 동작처럼 포함하지 않아야 한다.](canonical-spec-and-work-artifact-boundaries.md#canonical-spec은-capability-system-interface-또는-policy의-승인된-의도와-지속해야-할-계약을-현재형으로-설명해야-하며-일회성-작업-순서-임시-조사-변경-파일-목록과-실행-log를-현재-동작처럼-포함하지-않아야-한다)
- [`approved`와 `implemented` Canonical Spec만 SOT 권위를 가져야 한다. `draft` candidate와 Spec Delta는 제안으로 표시하고 기존 승인 정본을 암묵적으로 대체하지 않아야 한다.](canonical-spec-and-work-artifact-boundaries.md#approved와-implemented-canonical-spec만-sot-권위를-가져야-한다-draft-candidate와-spec-delta는-제안으로-표시하고-기존-승인-정본을-암묵적으로-대체하지-않아야-한다)
- [Forge는 요청의 목표와 관찰 가능한 완료 조건을 파악하고 재개·협업·검토에 필요한 경우에만 별도 작업 입력을 기록해야 한다.](canonical-spec-and-work-artifact-boundaries.md#forge는-요청의-목표와-관찰-가능한-완료-조건을-파악하고-재개협업검토에-필요한-경우에만-별도-작업-입력을-기록해야-한다)
- [Canonical Spec 변경은 대상과 의미를 명확히 하고 사용자가 구체적으로 지시하거나 승인한 범위에서만 반영해야 한다.](canonical-spec-and-work-artifact-boundaries.md#canonical-spec-변경은-대상과-의미를-명확히-하고-사용자가-구체적으로-지시하거나-승인한-범위에서만-반영해야-한다)
- [Execution Plan은 프로젝트 SOT와 구분되는 작업 기록이며 복잡성·조정·복구에 도움이 되는 수준으로 작성해야 한다.](canonical-spec-and-work-artifact-boundaries.md#execution-plan은-프로젝트-sot와-구분되는-작업-기록이며-복잡성조정복구에-도움이-되는-수준으로-작성해야-한다)
- [Forge는 지속 계약 영향과 실행 복잡성을 별도로 판단하고 필요한 계약·계획·검증만 적용해야 한다.](routing-and-lifecycle-gates.md#forge는-지속-계약-영향과-실행-복잡성을-별도로-판단하고-필요한-계약계획검증만-적용해야-한다)
- [기존 Canonical Spec의 exact normative statement를 추가·수정·제거하거나 외부 interface, 저장 데이터·schema, 사용자 workflow·상태 전이, 오류 의미, 보안·권한·개인정보·결제·규정 정책, cross-component 책임, 운영상 지속해야 할 release 계약 또는 사용자가 영구 보존을 지정한 결정을 변경하면 `Canonical Spec 영향: yes`로 분류해야 한다.](routing-and-lifecycle-gates.md#기존-canonical-spec의-exact-normative-statement를-추가수정제거하거나-외부-interface-저장-데이터schema-사용자-workflow상태-전이-오류-의미-보안권한개인정보결제규정-정책-cross-component-책임-운영상-지속해야-할-release-계약-또는-사용자가-영구-보존을-지정한-결정을-변경하면-canonical-spec-영향-yes로-분류해야-한다)
- [승인된 동작의 복원이나 code·test가 충분히 설명하는 국소 구현은 새 Canonical Spec 없이 실행하고 제품 결과나 지속 정책이 불명확할 때만 사용자 판단을 구해야 한다.](routing-and-lifecycle-gates.md#승인된-동작의-복원이나-codetest가-충분히-설명하는-국소-구현은-새-canonical-spec-없이-실행하고-제품-결과나-지속-정책이-불명확할-때만-사용자-판단을-구해야-한다)
- [국소적·가역적인 작업은 직접 실행하고 결과와 회귀 위험에 적절한 검증을 적용하며 TDD·별도 정본·계획 파일·전체 UI 선언·새 테스트 프레임워크를 일률적으로 요구하지 않아야 한다.](routing-and-lifecycle-gates.md#국소적가역적인-작업은-직접-실행하고-결과와-회귀-위험에-적절한-검증을-적용하며-tdd별도-정본계획-파일전체-ui-선언새-테스트-프레임워크를-일률적으로-요구하지-않아야-한다)
- [지속 계약을 바꾸는 작업은 승인된 의미를 정본에 반영하고 실행 복잡성에 맞는 계획을 사용하며 계약 의미를 바꾸지 않는 작업에는 정본을 새로 만들지 않아야 한다.](routing-and-lifecycle-gates.md#지속-계약을-바꾸는-작업은-승인된-의미를-정본에-반영하고-실행-복잡성에-맞는-계획을-사용하며-계약-의미를-바꾸지-않는-작업에는-정본을-새로-만들지-않아야-한다)
- [실행 중 계약 의미·사용자 선택·조정·복구 필요가 바뀌면 영향받는 행동 전에 필요한 권한과 계획을 재평가해야 한다.](routing-and-lifecycle-gates.md#실행-중-계약-의미사용자-선택조정복구-필요가-바뀌면-영향받는-행동-전에-필요한-권한과-계획을-재평가해야-한다)
- [모든 구현 완료 주장은 fresh command-level verification을 필요로 해야 한다. 승인된 Spec Delta를 구현한 작업은 bundle의 Canonical verification set을 full text와 member path로 식별해 실제 동작으로 검증해야 한다. Acceptance statement가 하나 이상 있으면 해당 Acceptance statement를 사용하고, 없으면 Requirement statement를 사용해야 한다. Quick 작업은 원래 reproduction, focused test, build·lint 중 주장에 맞는 증거만 요구하고 spec status 전환이나 전체 Canonical verification set 순회를 요구하지 않아야 한다.](verification-and-durable-authority.md#모든-구현-완료-주장은-fresh-command-level-verification을-필요로-해야-한다-승인된-spec-delta를-구현한-작업은-bundle의-canonical-verification-set을-full-text와-member-path로-식별해-실제-동작으로-검증해야-한다-acceptance-statement가-하나-이상-있으면-해당-acceptance-statement를-사용하고-없으면-requirement-statement를-사용해야-한다-quick-작업은-원래-reproduction-focused-test-buildlint-중-주장에-맞는-증거만-요구하고-spec-status-전환이나-전체-canonical-verification-set-순회를-요구하지-않아야-한다)
- [Forge lifecycle skill은 bundle의 Acceptance statement가 있으면 Acceptance를, 없으면 Requirement를 Canonical verification set으로 사용해야 한다. 새 계약 또는 미구현 baseline의 전체 구현은 전체 집합을 Task와 검증에 연결하고, 구현된 baseline의 부분 변경·복원은 직접·간접 영향 항목과 회귀 보존 범위를 명시해 계획과 완료 검증에 동일하게 적용해야 한다.](verification-and-durable-authority.md#forge-lifecycle-skill은-bundle의-acceptance-statement가-있으면-acceptance를-없으면-requirement를-canonical-verification-set으로-사용해야-한다-새-계약-또는-미구현-baseline의-전체-구현은-전체-집합을-task와-검증에-연결하고-구현된-baseline의-부분-변경복원은-직접간접-영향-항목과-회귀-보존-범위를-명시해-계획과-완료-검증에-동일하게-적용해야-한다)
- [작업 종료 시 장기 보존 가치가 생긴 결정은 Canonical Spec, ADR, `docs/research/`, `docs/debug/` 또는 명시적 evidence 문서로 승격해야 한다. Change Brief와 Spec Delta는 SOT로 남기지 않고, Execution Plan을 삭제하기 전 영구 결정을 먼저 승격해야 한다.](verification-and-durable-authority.md#작업-종료-시-장기-보존-가치가-생긴-결정은-canonical-spec-adr-docsresearch-docsdebug-또는-명시적-evidence-문서로-승격해야-한다-change-brief와-spec-delta는-sot로-남기지-않고-execution-plan을-삭제하기-전-영구-결정을-먼저-승격해야-한다)
- [Forge의 실행 스킬과 소비 문서는 계약·제안·계획·증거의 권위와 결과 중심 검증 원칙을 일치시키고 방법·질문 형식·기록 양식을 보편적 의무로 만들지 않아야 한다.](verification-and-durable-authority.md#forge의-실행-스킬과-소비-문서는-계약제안계획증거의-권위와-결과-중심-검증-원칙을-일치시키고-방법질문-형식기록-양식을-보편적-의무로-만들지-않아야-한다)
- [이 workflow는 Claude Code, Codex와 Antigravity에서 동일한 의미로 동작해야 하며 특정 harness의 tool 이름, hook 또는 비공통 기능을 Quick 분류의 전제조건으로 삼지 않아야 한다.](verification-and-durable-authority.md#이-workflow는-claude-code-codex와-antigravity에서-동일한-의미로-동작해야-하며-특정-harness의-tool-이름-hook-또는-비공통-기능을-quick-분류의-전제조건으로-삼지-않아야-한다)
