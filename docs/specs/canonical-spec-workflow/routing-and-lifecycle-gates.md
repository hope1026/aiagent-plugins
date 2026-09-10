# 라우팅과 Lifecycle Gate

## Requirements

### Forge는 지속 계약 영향과 실행 복잡성을 별도로 판단하고 필요한 계약·계획·검증만 적용해야 한다.

### 기존 Canonical Spec의 exact normative statement를 추가·수정·제거하거나 외부 interface, 저장 데이터·schema, 사용자 workflow·상태 전이, 오류 의미, 보안·권한·개인정보·결제·규정 정책, cross-component 책임, 운영상 지속해야 할 release 계약 또는 사용자가 영구 보존을 지정한 결정을 변경하면 `Canonical Spec 영향: yes`로 분류해야 한다.

### 승인된 동작의 복원이나 code·test가 충분히 설명하는 국소 구현은 새 Canonical Spec 없이 실행하고 제품 결과나 지속 정책이 불명확할 때만 사용자 판단을 구해야 한다.

### 국소적·가역적인 작업은 직접 실행하고 결과와 회귀 위험에 적절한 검증을 적용하며 TDD·별도 정본·계획 파일·전체 UI 선언·새 테스트 프레임워크를 일률적으로 요구하지 않아야 한다.

### 지속 계약을 바꾸는 작업은 승인된 의미를 정본에 반영하고 실행 복잡성에 맞는 계획을 사용하며 계약 의미를 바꾸지 않는 작업에는 정본을 새로 만들지 않아야 한다.

### 실행 중 계약 의미·사용자 선택·조정·복구 필요가 바뀌면 영향받는 행동 전에 필요한 권한과 계획을 재평가해야 한다.

### Forge는 직접 확인 가능한 사실을 조사하고 결과·범위·권한을 바꾸는 미해결 사용자 선택만 질문하며 질문 수·유형·준비 양식을 강제하지 않아야 한다.

## Acceptance Criteria

### 정본 영향 yes|no와 복잡도 low|high의 네 fixture를 router pressure test에 입력하면 각각 spec-backed direct, full lifecycle, Quick, plan-only 경로로 분류되고 불필요한 artifact가 생성되지 않는다.

검증하는 요구사항:

- [Forge는 지속 계약 영향과 실행 복잡성을 별도로 판단하고 필요한 계약·계획·검증만 적용해야 한다.](routing-and-lifecycle-gates.md#forge는-지속-계약-영향과-실행-복잡성을-별도로-판단하고-필요한-계약계획검증만-적용해야-한다)
- [국소적·가역적인 작업은 직접 실행하고 결과와 회귀 위험에 적절한 검증을 적용하며 TDD·별도 정본·계획 파일·전체 UI 선언·새 테스트 프레임워크를 일률적으로 요구하지 않아야 한다.](routing-and-lifecycle-gates.md#국소적가역적인-작업은-직접-실행하고-결과와-회귀-위험에-적절한-검증을-적용하며-tdd별도-정본계획-파일전체-ui-선언새-테스트-프레임워크를-일률적으로-요구하지-않아야-한다)
- [지속 계약을 바꾸는 작업은 승인된 의미를 정본에 반영하고 실행 복잡성에 맞는 계획을 사용하며 계약 의미를 바꾸지 않는 작업에는 정본을 새로 만들지 않아야 한다.](routing-and-lifecycle-gates.md#지속-계약을-바꾸는-작업은-승인된-의미를-정본에-반영하고-실행-복잡성에-맞는-계획을-사용하며-계약-의미를-바꾸지-않는-작업에는-정본을-새로-만들지-않아야-한다)

### 한 컴포넌트의 명확하고 가역적인 국소 bug fixture를 실행하면 `docs/specs/`와 `docs/plans/` 변경 없이 원래 reproduction을 실패에서 성공으로 바꾸는 focused test가 fresh evidence로 기록된다.

검증하는 요구사항:

- [Forge는 요청의 목표와 관찰 가능한 완료 조건을 파악하고 재개·협업·검토에 필요한 경우에만 별도 작업 입력을 기록해야 한다.](canonical-spec-and-work-artifact-boundaries.md#forge는-요청의-목표와-관찰-가능한-완료-조건을-파악하고-재개협업검토에-필요한-경우에만-별도-작업-입력을-기록해야-한다)
- [승인된 동작의 복원이나 code·test가 충분히 설명하는 국소 구현은 새 Canonical Spec 없이 실행하고 제품 결과나 지속 정책이 불명확할 때만 사용자 판단을 구해야 한다.](routing-and-lifecycle-gates.md#승인된-동작의-복원이나-codetest가-충분히-설명하는-국소-구현은-새-canonical-spec-없이-실행하고-제품-결과나-지속-정책이-불명확할-때만-사용자-판단을-구해야-한다)
- [국소적·가역적인 작업은 직접 실행하고 결과와 회귀 위험에 적절한 검증을 적용하며 TDD·별도 정본·계획 파일·전체 UI 선언·새 테스트 프레임워크를 일률적으로 요구하지 않아야 한다.](routing-and-lifecycle-gates.md#국소적가역적인-작업은-직접-실행하고-결과와-회귀-위험에-적절한-검증을-적용하며-tdd별도-정본계획-파일전체-ui-선언새-테스트-프레임워크를-일률적으로-요구하지-않아야-한다)
- [모든 구현 완료 주장은 fresh command-level verification을 필요로 해야 한다. 승인된 Spec Delta를 구현한 작업은 bundle의 Canonical verification set을 full text와 member path로 식별해 실제 동작으로 검증해야 한다. Acceptance statement가 하나 이상 있으면 해당 Acceptance statement를 사용하고, 없으면 Requirement statement를 사용해야 한다. Quick 작업은 원래 reproduction, focused test, build·lint 중 주장에 맞는 증거만 요구하고 spec status 전환이나 전체 Canonical verification set 순회를 요구하지 않아야 한다.](verification-and-durable-authority.md#모든-구현-완료-주장은-fresh-command-level-verification을-필요로-해야-한다-승인된-spec-delta를-구현한-작업은-bundle의-canonical-verification-set을-full-text와-member-path로-식별해-실제-동작으로-검증해야-한다-acceptance-statement가-하나-이상-있으면-해당-acceptance-statement를-사용하고-없으면-requirement-statement를-사용해야-한다-quick-작업은-원래-reproduction-focused-test-buildlint-중-주장에-맞는-증거만-요구하고-spec-status-전환이나-전체-canonical-verification-set-순회를-요구하지-않아야-한다)

### 국소 UI 문구가 지속 정책을 바꾸는지 repository와 요청으로 확인할 수 없으면 agent는 사용자에게 원하는 의미를 확인하고 그 답에 맞춰 직접 실행하거나 계약을 갱신한다.

검증하는 요구사항:

- [기존 Canonical Spec의 exact normative statement를 추가·수정·제거하거나 외부 interface, 저장 데이터·schema, 사용자 workflow·상태 전이, 오류 의미, 보안·권한·개인정보·결제·규정 정책, cross-component 책임, 운영상 지속해야 할 release 계약 또는 사용자가 영구 보존을 지정한 결정을 변경하면 `Canonical Spec 영향: yes`로 분류해야 한다.](routing-and-lifecycle-gates.md#기존-canonical-spec의-exact-normative-statement를-추가수정제거하거나-외부-interface-저장-데이터schema-사용자-workflow상태-전이-오류-의미-보안권한개인정보결제규정-정책-cross-component-책임-운영상-지속해야-할-release-계약-또는-사용자가-영구-보존을-지정한-결정을-변경하면-canonical-spec-영향-yes로-분류해야-한다)
- [승인된 동작의 복원이나 code·test가 충분히 설명하는 국소 구현은 새 Canonical Spec 없이 실행하고 제품 결과나 지속 정책이 불명확할 때만 사용자 판단을 구해야 한다.](routing-and-lifecycle-gates.md#승인된-동작의-복원이나-codetest가-충분히-설명하는-국소-구현은-새-canonical-spec-없이-실행하고-제품-결과나-지속-정책이-불명확할-때만-사용자-판단을-구해야-한다)

### Quick로 시작한 fixture에서 cross-component contract와 migration 순서가 발견되면 agent는 다음 mutation 전에 full lifecycle로 승격하고, 이미 Quick로 시작했다는 이유로 분류를 유지하지 않는다.

검증하는 요구사항:

- [실행 중 계약 의미·사용자 선택·조정·복구 필요가 바뀌면 영향받는 행동 전에 필요한 권한과 계획을 재평가해야 한다.](routing-and-lifecycle-gates.md#실행-중-계약-의미사용자-선택조정복구-필요가-바뀌면-영향받는-행동-전에-필요한-권한과-계획을-재평가해야-한다)

### 기술 구조가 repository에 있고 원하는 결과만 불명확한 요청에서는 agent가 사실을 조사하고 중요한 선택만 질문하며 명확한 요청에는 불필요한 질문·Brief·계획 파일을 만들지 않는다.

검증하는 요구사항:

- [Forge는 요청의 목표와 관찰 가능한 완료 조건을 파악하고 재개·협업·검토에 필요한 경우에만 별도 작업 입력을 기록해야 한다.](canonical-spec-and-work-artifact-boundaries.md#forge는-요청의-목표와-관찰-가능한-완료-조건을-파악하고-재개협업검토에-필요한-경우에만-별도-작업-입력을-기록해야-한다)
- [승인된 동작의 복원이나 code·test가 충분히 설명하는 국소 구현은 새 Canonical Spec 없이 실행하고 제품 결과나 지속 정책이 불명확할 때만 사용자 판단을 구해야 한다.](routing-and-lifecycle-gates.md#승인된-동작의-복원이나-codetest가-충분히-설명하는-국소-구현은-새-canonical-spec-없이-실행하고-제품-결과나-지속-정책이-불명확할-때만-사용자-판단을-구해야-한다)
- [Forge의 실행 스킬과 소비 문서는 계약·제안·계획·증거의 권위와 결과 중심 검증 원칙을 일치시키고 방법·질문 형식·기록 양식을 보편적 의무로 만들지 않아야 한다.](verification-and-durable-authority.md#forge의-실행-스킬과-소비-문서는-계약제안계획증거의-권위와-결과-중심-검증-원칙을-일치시키고-방법질문-형식기록-양식을-보편적-의무로-만들지-않아야-한다)
- [Forge는 직접 확인 가능한 사실을 조사하고 결과·범위·권한을 바꾸는 미해결 사용자 선택만 질문하며 질문 수·유형·준비 양식을 강제하지 않아야 한다.](routing-and-lifecycle-gates.md#forge는-직접-확인-가능한-사실을-조사하고-결과범위권한을-바꾸는-미해결-사용자-선택만-질문하며-질문-수유형준비-양식을-강제하지-않아야-한다)
