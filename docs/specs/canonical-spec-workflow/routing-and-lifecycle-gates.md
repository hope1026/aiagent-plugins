# 라우팅과 Lifecycle Gate

## Requirements

### Forge router는 모든 실행 요청을 `Canonical Spec 영향: yes|no`와 `Execution complexity: low|high`의 두 축으로 분류한 뒤 해당 경로를 선택해야 한다.

### 기존 Canonical Spec의 exact normative statement를 추가·수정·제거하거나 외부 interface, 저장 데이터·schema, 사용자 workflow·상태 전이, 오류 의미, 보안·권한·개인정보·결제·규정 정책, cross-component 책임, 운영상 지속해야 할 release 계약 또는 사용자가 영구 보존을 지정한 결정을 변경하면 `Canonical Spec 영향: yes`로 분류해야 한다.

### 기존 Canonical Spec과 구현의 불일치를 원래 승인 동작으로 복구하거나, 정본으로 보존할 의도 없이 code·test가 완전히 설명하는 국소 구현·표현을 변경하는 작업은 `Canonical Spec 영향: no`로 분류할 수 있어야 한다. 정본 가치가 불명확하면 구현 전에 사용자에게 하나의 분류 질문을 해야 한다.

### `Canonical Spec 영향: no`이고 `Execution complexity: low`이며 범위가 국소적·가역적이고 focused command로 결과를 증명할 수 있는 작업은 Quick 경로를 사용해야 한다. Quick 경로는 Canonical Spec, Spec Delta와 Execution Plan을 만들지 않고 관련 debugging, TDD, design 또는 tone skill을 적용해 바로 실행한 뒤 fresh verification을 수행해야 한다.

### `Canonical Spec 영향: yes`이고 복잡도가 낮으면 Spec Delta 승인·Canonical Spec 반영 뒤 Execution Plan 없이 실행해야 한다. 정본 영향이 없고 복잡도가 높으면 Change Brief와 Execution Plan을 사용할 수 있으나 Canonical Spec을 만들지 않아야 한다. 두 축이 모두 높으면 승인된 Canonical Spec과 Execution Plan을 모두 사용해야 한다.

### Quick 또는 plan-only 실행 중 정본 영향 조건, 새 사용자 선택, 여러 컴포넌트 의존성, migration·release 순서 또는 rollback 위험이 발견되면 다음 mutation 전에 작업을 재분류하고 필요한 Spec Delta 또는 Execution Plan 경로로 승격해야 한다.

### Forge는 Change Brief를 확정하거나 그 작업의 Plan·mutation으로 진행하기 전에 repository에서 확인 가능한 사실을 먼저 조사해야 한다. `Goal`, `Scope`, `Out of Scope`, `Done Checks` 또는 두 축 route를 신뢰성 있게 판정할 수 없고 그 모호성이 관찰 결과, 범위, 정본 권위, 안전, 파괴적·외부 효과를 바꿀 때만 한 메시지에 하나의 blocking user-owned choice를 질문해야 한다. Repository에서 확인 가능한 사실, 결과에 영향이 작은 구현 선호 또는 국소적·가역적인 안전한 기본값은 질문하지 않아야 한다. 답을 초안에 반영한 뒤 Goal을 한 문장으로 설명할 수 있고, Scope와 Out of Scope가 충돌하지 않으며, Done Checks가 관찰 가능하고, Canonical Spec 영향과 Execution complexity를 판정할 수 있을 때만 ready로 간주해야 한다.

## Acceptance Criteria

### 정본 영향 yes|no와 복잡도 low|high의 네 fixture를 router pressure test에 입력하면 각각 spec-backed direct, full lifecycle, Quick, plan-only 경로로 분류되고 불필요한 artifact가 생성되지 않는다.

검증하는 요구사항:

- [Forge router는 모든 실행 요청을 `Canonical Spec 영향: yes|no`와 `Execution complexity: low|high`의 두 축으로 분류한 뒤 해당 경로를 선택해야 한다.](routing-and-lifecycle-gates.md#forge-router는-모든-실행-요청을-canonical-spec-영향-yesno와-execution-complexity-lowhigh의-두-축으로-분류한-뒤-해당-경로를-선택해야-한다)
- [`Canonical Spec 영향: no`이고 `Execution complexity: low`이며 범위가 국소적·가역적이고 focused command로 결과를 증명할 수 있는 작업은 Quick 경로를 사용해야 한다. Quick 경로는 Canonical Spec, Spec Delta와 Execution Plan을 만들지 않고 관련 debugging, TDD, design 또는 tone skill을 적용해 바로 실행한 뒤 fresh verification을 수행해야 한다.](routing-and-lifecycle-gates.md#canonical-spec-영향-no이고-execution-complexity-low이며-범위가-국소적가역적이고-focused-command로-결과를-증명할-수-있는-작업은-quick-경로를-사용해야-한다-quick-경로는-canonical-spec-spec-delta와-execution-plan을-만들지-않고-관련-debugging-tdd-design-또는-tone-skill을-적용해-바로-실행한-뒤-fresh-verification을-수행해야-한다)
- [`Canonical Spec 영향: yes`이고 복잡도가 낮으면 Spec Delta 승인·Canonical Spec 반영 뒤 Execution Plan 없이 실행해야 한다. 정본 영향이 없고 복잡도가 높으면 Change Brief와 Execution Plan을 사용할 수 있으나 Canonical Spec을 만들지 않아야 한다. 두 축이 모두 높으면 승인된 Canonical Spec과 Execution Plan을 모두 사용해야 한다.](routing-and-lifecycle-gates.md#canonical-spec-영향-yes이고-복잡도가-낮으면-spec-delta-승인canonical-spec-반영-뒤-execution-plan-없이-실행해야-한다-정본-영향이-없고-복잡도가-높으면-change-brief와-execution-plan을-사용할-수-있으나-canonical-spec을-만들지-않아야-한다-두-축이-모두-높으면-승인된-canonical-spec과-execution-plan을-모두-사용해야-한다)

### 한 컴포넌트의 명확하고 가역적인 국소 bug fixture를 실행하면 `docs/specs/`와 `docs/plans/` 변경 없이 원래 reproduction을 실패에서 성공으로 바꾸는 focused test가 fresh evidence로 기록된다.

검증하는 요구사항:

- [Forge는 사용자 요청과 확인한 repository context로 Change Brief 초안을 구성해야 하며, 요구가 대화만으로 충분히 명확한 작업은 Change Brief 파일을 만들지 않아야 한다. 재개, 위임, 여러 범위 조정 또는 명시적 사용자 검토에 독립 문서가 필요한 경우에만 `Goal`, `Scope`, `Out of Scope`, `Done Checks`를 가진 Change Brief를 만들 수 있어야 한다.](canonical-spec-and-work-artifact-boundaries.md#forge는-사용자-요청과-확인한-repository-context로-change-brief-초안을-구성해야-하며-요구가-대화만으로-충분히-명확한-작업은-change-brief-파일을-만들지-않아야-한다-재개-위임-여러-범위-조정-또는-명시적-사용자-검토에-독립-문서가-필요한-경우에만-goal-scope-out-of-scope-done-checks를-가진-change-brief를-만들-수-있어야-한다)
- [기존 Canonical Spec과 구현의 불일치를 원래 승인 동작으로 복구하거나, 정본으로 보존할 의도 없이 code·test가 완전히 설명하는 국소 구현·표현을 변경하는 작업은 `Canonical Spec 영향: no`로 분류할 수 있어야 한다. 정본 가치가 불명확하면 구현 전에 사용자에게 하나의 분류 질문을 해야 한다.](routing-and-lifecycle-gates.md#기존-canonical-spec과-구현의-불일치를-원래-승인-동작으로-복구하거나-정본으로-보존할-의도-없이-codetest가-완전히-설명하는-국소-구현표현을-변경하는-작업은-canonical-spec-영향-no로-분류할-수-있어야-한다-정본-가치가-불명확하면-구현-전에-사용자에게-하나의-분류-질문을-해야-한다)
- [`Canonical Spec 영향: no`이고 `Execution complexity: low`이며 범위가 국소적·가역적이고 focused command로 결과를 증명할 수 있는 작업은 Quick 경로를 사용해야 한다. Quick 경로는 Canonical Spec, Spec Delta와 Execution Plan을 만들지 않고 관련 debugging, TDD, design 또는 tone skill을 적용해 바로 실행한 뒤 fresh verification을 수행해야 한다.](routing-and-lifecycle-gates.md#canonical-spec-영향-no이고-execution-complexity-low이며-범위가-국소적가역적이고-focused-command로-결과를-증명할-수-있는-작업은-quick-경로를-사용해야-한다-quick-경로는-canonical-spec-spec-delta와-execution-plan을-만들지-않고-관련-debugging-tdd-design-또는-tone-skill을-적용해-바로-실행한-뒤-fresh-verification을-수행해야-한다)
- [모든 구현 완료 주장은 fresh command-level verification을 필요로 해야 한다. 승인된 Spec Delta를 구현한 작업은 영향받는 Acceptance statement를 full text와 member path로 식별해 실제 동작으로 검증해야 하며, Quick 작업은 원래 reproduction, focused test, build·lint 중 주장에 맞는 증거만 요구하고 spec status 전환이나 전체 Acceptance 순회를 요구하지 않아야 한다.](verification-and-durable-authority.md#모든-구현-완료-주장은-fresh-command-level-verification을-필요로-해야-한다-승인된-spec-delta를-구현한-작업은-영향받는-acceptance-statement를-full-text와-member-path로-식별해-실제-동작으로-검증해야-하며-quick-작업은-원래-reproduction-focused-test-buildlint-중-주장에-맞는-증거만-요구하고-spec-status-전환이나-전체-acceptance-순회를-요구하지-않아야-한다)

### 국소 UI 문구가 일회성 표현인지 지속해야 할 정책인지 요청만으로 판별할 수 없는 fixture에서 agent는 mutation 전에 사용자에게 하나의 정본 분류 질문을 하고 답에 따라 Quick 또는 Spec Delta 경로를 선택한다.

검증하는 요구사항:

- [기존 Canonical Spec의 exact normative statement를 추가·수정·제거하거나 외부 interface, 저장 데이터·schema, 사용자 workflow·상태 전이, 오류 의미, 보안·권한·개인정보·결제·규정 정책, cross-component 책임, 운영상 지속해야 할 release 계약 또는 사용자가 영구 보존을 지정한 결정을 변경하면 `Canonical Spec 영향: yes`로 분류해야 한다.](routing-and-lifecycle-gates.md#기존-canonical-spec의-exact-normative-statement를-추가수정제거하거나-외부-interface-저장-데이터schema-사용자-workflow상태-전이-오류-의미-보안권한개인정보결제규정-정책-cross-component-책임-운영상-지속해야-할-release-계약-또는-사용자가-영구-보존을-지정한-결정을-변경하면-canonical-spec-영향-yes로-분류해야-한다)
- [기존 Canonical Spec과 구현의 불일치를 원래 승인 동작으로 복구하거나, 정본으로 보존할 의도 없이 code·test가 완전히 설명하는 국소 구현·표현을 변경하는 작업은 `Canonical Spec 영향: no`로 분류할 수 있어야 한다. 정본 가치가 불명확하면 구현 전에 사용자에게 하나의 분류 질문을 해야 한다.](routing-and-lifecycle-gates.md#기존-canonical-spec과-구현의-불일치를-원래-승인-동작으로-복구하거나-정본으로-보존할-의도-없이-codetest가-완전히-설명하는-국소-구현표현을-변경하는-작업은-canonical-spec-영향-no로-분류할-수-있어야-한다-정본-가치가-불명확하면-구현-전에-사용자에게-하나의-분류-질문을-해야-한다)

### Quick로 시작한 fixture에서 cross-component contract와 migration 순서가 발견되면 agent는 다음 mutation 전에 full lifecycle로 승격하고, 이미 Quick로 시작했다는 이유로 분류를 유지하지 않는다.

검증하는 요구사항:

- [Quick 또는 plan-only 실행 중 정본 영향 조건, 새 사용자 선택, 여러 컴포넌트 의존성, migration·release 순서 또는 rollback 위험이 발견되면 다음 mutation 전에 작업을 재분류하고 필요한 Spec Delta 또는 Execution Plan 경로로 승격해야 한다.](routing-and-lifecycle-gates.md#quick-또는-plan-only-실행-중-정본-영향-조건-새-사용자-선택-여러-컴포넌트-의존성-migrationrelease-순서-또는-rollback-위험이-발견되면-다음-mutation-전에-작업을-재분류하고-필요한-spec-delta-또는-execution-plan-경로로-승격해야-한다)

### 기존 기술 구조는 repository에서 확인할 수 있지만 원하는 사용자 결과와 범위가 불명확한 fixture를 입력하면 agent는 repository 사실을 사용자에게 묻지 않고 먼저 조사하며, 실행 결과를 바꾸는 user-owned choice만 한 메시지에 하나씩 질문한다. 답변 뒤 `Goal`, `Scope`, `Out of Scope`, 관찰 가능한 `Done Checks`와 두 축 분류가 모두 준비되기 전에는 Plan 또는 mutation으로 진행하지 않는다. 같은 fixture가 처음부터 충분히 명확하면 질문하지 않고, 재개·위임·범위 조정·명시적 검토에 독립 문서가 필요하지 않은 한 Change Brief 파일도 만들지 않는다.

검증하는 요구사항:

- [Forge는 사용자 요청과 확인한 repository context로 Change Brief 초안을 구성해야 하며, 요구가 대화만으로 충분히 명확한 작업은 Change Brief 파일을 만들지 않아야 한다. 재개, 위임, 여러 범위 조정 또는 명시적 사용자 검토에 독립 문서가 필요한 경우에만 `Goal`, `Scope`, `Out of Scope`, `Done Checks`를 가진 Change Brief를 만들 수 있어야 한다.](canonical-spec-and-work-artifact-boundaries.md#forge는-사용자-요청과-확인한-repository-context로-change-brief-초안을-구성해야-하며-요구가-대화만으로-충분히-명확한-작업은-change-brief-파일을-만들지-않아야-한다-재개-위임-여러-범위-조정-또는-명시적-사용자-검토에-독립-문서가-필요한-경우에만-goal-scope-out-of-scope-done-checks를-가진-change-brief를-만들-수-있어야-한다)
- [기존 Canonical Spec과 구현의 불일치를 원래 승인 동작으로 복구하거나, 정본으로 보존할 의도 없이 code·test가 완전히 설명하는 국소 구현·표현을 변경하는 작업은 `Canonical Spec 영향: no`로 분류할 수 있어야 한다. 정본 가치가 불명확하면 구현 전에 사용자에게 하나의 분류 질문을 해야 한다.](routing-and-lifecycle-gates.md#기존-canonical-spec과-구현의-불일치를-원래-승인-동작으로-복구하거나-정본으로-보존할-의도-없이-codetest가-완전히-설명하는-국소-구현표현을-변경하는-작업은-canonical-spec-영향-no로-분류할-수-있어야-한다-정본-가치가-불명확하면-구현-전에-사용자에게-하나의-분류-질문을-해야-한다)
- [`using-forge`, `writing-specs`, `writing-plans`, `executing-plans`, `systematic-debugging`, `verifying-work`와 관련 portability·README 문서는 `Spec Bundle`, `bundle path`, `member path`, `Requirement statement`, `Acceptance statement`, 두 축 분류, Change Brief readiness, Brief clarification·Canonical classification·Spec clarification의 경계, Quick 승격 조건과 검증 경계를 동일하게 사용하고 숫자 ID를 사용자-facing 설명에 사용하지 않아야 한다.](verification-and-durable-authority.md#using-forge-writing-specs-writing-plans-executing-plans-systematic-debugging-verifying-work와-관련-portabilityreadme-문서는-spec-bundle-bundle-path-member-path-requirement-statement-acceptance-statement-두-축-분류-change-brief-readiness-brief-clarificationcanonical-classificationspec-clarification의-경계-quick-승격-조건과-검증-경계를-동일하게-사용하고-숫자-id를-사용자-facing-설명에-사용하지-않아야-한다)
- [Forge는 Change Brief를 확정하거나 그 작업의 Plan·mutation으로 진행하기 전에 repository에서 확인 가능한 사실을 먼저 조사해야 한다. `Goal`, `Scope`, `Out of Scope`, `Done Checks` 또는 두 축 route를 신뢰성 있게 판정할 수 없고 그 모호성이 관찰 결과, 범위, 정본 권위, 안전, 파괴적·외부 효과를 바꿀 때만 한 메시지에 하나의 blocking user-owned choice를 질문해야 한다. Repository에서 확인 가능한 사실, 결과에 영향이 작은 구현 선호 또는 국소적·가역적인 안전한 기본값은 질문하지 않아야 한다. 답을 초안에 반영한 뒤 Goal을 한 문장으로 설명할 수 있고, Scope와 Out of Scope가 충돌하지 않으며, Done Checks가 관찰 가능하고, Canonical Spec 영향과 Execution complexity를 판정할 수 있을 때만 ready로 간주해야 한다.](routing-and-lifecycle-gates.md#forge는-change-brief를-확정하거나-그-작업의-planmutation으로-진행하기-전에-repository에서-확인-가능한-사실을-먼저-조사해야-한다-goal-scope-out-of-scope-done-checks-또는-두-축-route를-신뢰성-있게-판정할-수-없고-그-모호성이-관찰-결과-범위-정본-권위-안전-파괴적외부-효과를-바꿀-때만-한-메시지에-하나의-blocking-user-owned-choice를-질문해야-한다-repository에서-확인-가능한-사실-결과에-영향이-작은-구현-선호-또는-국소적가역적인-안전한-기본값은-질문하지-않아야-한다-답을-초안에-반영한-뒤-goal을-한-문장으로-설명할-수-있고-scope와-out-of-scope가-충돌하지-않으며-done-checks가-관찰-가능하고-canonical-spec-영향과-execution-complexity를-판정할-수-있을-때만-ready로-간주해야-한다)
