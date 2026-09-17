# Plan Context와 문장 추적성

적용 범위: 이 문서의 구조화 source·renderer·composition·freshness 계약은 [관리형 제작 경로](presentation-routing.md)에 적용한다. 일회성 자유 작성에는 해당 빌드 절차나 표현 제약을 강제하지 않는다.

## Requirements

이 문서의 plan kind는 Visual Docs가 읽는 구조화된 파일 계획을 뜻한다. 일반 작업의 계획은 앱이나 기존 기록에 둘 수 있고, 시각 문서 요청 없이 이 형식을 강제하지 않는다.

### Forge의 구조화된 파일 계획은 `docs/plans/PPP-<slug>/plan.md`를 실행 source로 사용하고 plan 번호는 spec과 독립적으로 부여해야 한다.

### plan kind의 Overview는 목표, primary plan의 Task·Step 집계, context bundle별 Requirement·Acceptance Criterion 집계, 읽기 순서, 사용자 경험, 완료 상태를 분리해 보여줘야 한다.

### plan kind의 Requirements는 Global Constraints, 핵심 정책, Route별 적용 범위와 Related Specs의 full statement context를 member provenance와 함께 보여줘야 한다.

### plan kind의 Flows는 Route map, Task dependency, runtime 또는 확장 흐름을 보여줘야 한다.

### plan kind의 Data & Interfaces는 runtime 책임, 서버 권위, 파일, Remote, transaction, Interface 계약을 보여줘야 한다.

### plan kind의 Acceptance는 plan에 명시된 Related Specs의 statement link만 사용해야 한다. Acceptance statement가 있는 bundle은 Requirement → Acceptance Criterion → Task → Step·검증 mapping을, Acceptance statement가 없는 bundle은 Requirement → Task → Step·검증 mapping을 보여주고, 관련 spec이 없으면 Task → Step·검증 mapping을 검토 상태와 함께 보여줘야 한다.

### plan kind의 History는 plan 상태, Task checkbox, Progress History, 선택적인 `progress.md`·`tasks/*.md`, primary·auxiliary·context source별 role·path·hash, checkpoint, 관련 commit, 재생성 command를 보여줘야 한다.

### 구조화된 파일 계획에서 Route나 Milestone을 사용하면 실제 단계를 표현하고 각 Task의 primary Route를 명확히 해야 한다.

### Route를 사용하는 큰 plan fixture는 source의 단계와 Task dependency를 의미 있게 표시해야 한다.

### plan kind는 plan에 명시된 bundle path, member statement link와 Task·Step 관계만 사용해야 한다. Acceptance statement가 있는 bundle은 Requirement → Acceptance Criterion → Task → Step deep link를, Acceptance statement가 없는 bundle은 Requirement → Task → Step deep link를 만들고, plan에 없는 cross-source 관계를 추론하지 않아야 한다.

### 구조화된 파일 계획은 목표·산출물·검증을 명확히 하고 파일 경계·의존성·Interface·복구·승인 정보와 diagram은 실행이나 검토에 필요한 만큼 포함해야 한다.

### 계획의 계약 검증 범위는 완료 주장에 맞게 선택하고 구조화된 파일 계획은 해당 Governing statements 링크와 회귀 증거를 연결하며 coverage table은 검토에 도움이 될 때 사용해야 한다.

### 계획의 diagram은 검토에 도움이 되는 source 관계를 설명할 때 사용하고 단계를 채우기 위한 diagram을 만들지 않아야 한다.

### 구조화된 파일 계획에서 큰 Task 집합을 diagram으로 표시할 때는 읽기 쉬운 실제 단계나 관계로 구성하고 의미 없는 평면 연결을 피해야 한다.

### plan의 diagram과 책임 표는 plan에서 선택한 언어로 작성하되 Related Specs context에서 인용한 값과 API, service, schema, code identifier는 원문을 유지하고 source provenance를 표시해야 한다.

### spec은 프로젝트 수명 동안 영구 관리하고, plan은 작업 단위로 생성하며 작업 종료 뒤 보존 가치가 없으면 plan 디렉터리 전체를 삭제할 수 있어야 한다.

### 구조화된 파일 계획은 `Related Specs`에 0개 이상의 unique normalized bundle path를 선언하고 governed Task의 `Governing statements`를 선언된 bundle의 exact statement에 연결해야 한다.

### 계획이 지속 계약 의미를 바꾸면 승인된 Canonical Spec을 참조하고 승인 동작의 복원이나 code·test로 충분한 국소 구현에는 새 정본을 요구하지 않아야 한다.

### 진행 기록은 앱이나 기존 작업 기록을 재사용하고 구조화된 파일 계획을 보존할 때 Task checkbox·Progress History 또는 같은 디렉터리의 progress 기록을 활용해야 한다.

### 구조화된 파일 계획의 Task는 독립 소유권이나 검토·복구에 도움이 될 때 같은 plan 디렉터리의 `tasks/*.md`로 분리할 수 있어야 한다.

### 삭제 예정 plan의 영구 보존 가치가 있는 제품 결정은 삭제 전에 governing spec, ADR 또는 동등한 영구 문서로 이전해야 한다.

## Acceptance Criteria

### Acceptance statement가 있는 bundle과 없는 bundle을 함께 참조하는 `plan.md`, `progress.md`, `tasks/*.md` fixture를 plan kind로 build하면 primary Task·Step count와 context bundle·member별 Requirement·Acceptance Criterion count가 분리되고, plan에 명시된 full-statement link만 사용해 각각 Requirement → Acceptance Criterion → Task → Step과 Requirement → Task → Step mapping이 만들어진다.

검증하는 요구사항:

- [`plan` kind에서는 `plan.md`와 존재하는 경우 같은 디렉터리의 `progress.md`, `tasks/*.md`를 primary source set으로 사용하고, plan의 `Related Specs` bundle 0개 이상을 제품 요구사항을 설명하는 context source로 읽되 plan source와 병합하거나 동일한 ownership으로 표시하지 않아야 한다.](source-selection-and-freshness.md#plan-kind에서는-planmd와-존재하는-경우-같은-디렉터리의-progressmd-tasksmd를-primary-source-set으로-사용하고-plan의-related-specs-bundle-0개-이상을-제품-요구사항을-설명하는-context-source로-읽되-plan-source와-병합하거나-동일한-ownership으로-표시하지-않아야-한다)
- [plan kind의 Overview는 목표, primary plan의 Task·Step 집계, context bundle별 Requirement·Acceptance Criterion 집계, 읽기 순서, 사용자 경험, 완료 상태를 분리해 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-kind의-overview는-목표-primary-plan의-taskstep-집계-context-bundle별-requirementacceptance-criterion-집계-읽기-순서-사용자-경험-완료-상태를-분리해-보여줘야-한다)
- [plan kind의 Requirements는 Global Constraints, 핵심 정책, Route별 적용 범위와 Related Specs의 full statement context를 member provenance와 함께 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-kind의-requirements는-global-constraints-핵심-정책-route별-적용-범위와-related-specs의-full-statement-context를-member-provenance와-함께-보여줘야-한다)
- [plan kind의 Acceptance는 plan에 명시된 Related Specs의 statement link만 사용해야 한다. Acceptance statement가 있는 bundle은 Requirement → Acceptance Criterion → Task → Step·검증 mapping을, Acceptance statement가 없는 bundle은 Requirement → Task → Step·검증 mapping을 보여주고, 관련 spec이 없으면 Task → Step·검증 mapping을 검토 상태와 함께 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-kind의-acceptance는-plan에-명시된-related-specs의-statement-link만-사용해야-한다-acceptance-statement가-있는-bundle은-requirement-acceptance-criterion-task-step검증-mapping을-acceptance-statement가-없는-bundle은-requirement-task-step검증-mapping을-보여주고-관련-spec이-없으면-task-step검증-mapping을-검토-상태와-함께-보여줘야-한다)
- [계획의 계약 검증 범위는 완료 주장에 맞게 선택하고 구조화된 파일 계획은 해당 Governing statements 링크와 회귀 증거를 연결하며 coverage table은 검토에 도움이 될 때 사용해야 한다.](plan-context-and-statement-traceability.md#계획의-계약-검증-범위는-완료-주장에-맞게-선택하고-구조화된-파일-계획은-해당-governing-statements-링크와-회귀-증거를-연결하며-coverage-table은-검토에-도움이-될-때-사용해야-한다)
- [plan kind의 History는 plan 상태, Task checkbox, Progress History, 선택적인 `progress.md`·`tasks/*.md`, primary·auxiliary·context source별 role·path·hash, checkpoint, 관련 commit, 재생성 command를 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-kind의-history는-plan-상태-task-checkbox-progress-history-선택적인-progressmdtasksmd-primaryauxiliarycontext-source별-rolepathhash-checkpoint-관련-commit-재생성-command를-보여줘야-한다)
- [Visual Docs는 독자의 핵심 질문에 답하는 설명을 먼저 제공하고, 원문 상세와 검증 근거는 그 설명에서 찾아갈 수 있게 배치해야 한다. 설명 순서와 disclosure는 내용과 요청 목적에 따라 결정해야 한다.](adaptive-presentation-and-navigation.md#visual-docs는-독자의-핵심-질문에-답하는-설명을-먼저-제공하고-원문-상세와-검증-근거는-그-설명에서-찾아갈-수-있게-배치해야-한다-설명-순서와-disclosure는-내용과-요청-목적에-따라-결정해야-한다)
- [Visual Docs는 spec kind에서 current bundle과 comparison bundle의 Requirement·Acceptance Criterion·Mermaid 수를 bundle과 member별로 분리하고, plan kind에서 primary source set의 Task·Step·Mermaid 수와 Related Specs context의 Requirement·Acceptance Criterion·Mermaid 수를 source별로 분리해 summary에 표시해야 한다.](source-selection-and-freshness.md#visual-docs는-spec-kind에서-current-bundle과-comparison-bundle의-requirementacceptance-criterionmermaid-수를-bundle과-member별로-분리하고-plan-kind에서-primary-source-set의-taskstepmermaid-수와-related-specs-context의-requirementacceptance-criterionmermaid-수를-source별로-분리해-summary에-표시해야-한다)
- [집계 기준은 structured parser가 인식한 `### Task N` heading, `Step N` checkbox, Requirements와 Acceptance Criteria 아래의 unique full-statement H3, Mermaid fence 수로 고정해야 한다. plan primary set 안의 Task·Step은 중복 제거하고 context statement는 bundle path·member path·statement kind·exact heading에서 계산한 내부 namespace로 구분하되 이를 화면 label로 노출하지 않아야 한다.](source-selection-and-freshness.md#집계-기준은-structured-parser가-인식한-task-n-heading-step-n-checkbox-requirements와-acceptance-criteria-아래의-unique-full-statement-h3-mermaid-fence-수로-고정해야-한다-plan-primary-set-안의-taskstep은-중복-제거하고-context-statement는-bundle-pathmember-pathstatement-kindexact-heading에서-계산한-내부-namespace로-구분하되-이를-화면-label로-노출하지-않아야-한다)
- [plan kind는 plan에 명시된 bundle path, member statement link와 Task·Step 관계만 사용해야 한다. Acceptance statement가 있는 bundle은 Requirement → Acceptance Criterion → Task → Step deep link를, Acceptance statement가 없는 bundle은 Requirement → Task → Step deep link를 만들고, plan에 없는 cross-source 관계를 추론하지 않아야 한다.](plan-context-and-statement-traceability.md#plan-kind는-plan에-명시된-bundle-path-member-statement-link와-taskstep-관계만-사용해야-한다-acceptance-statement가-있는-bundle은-requirement-acceptance-criterion-task-step-deep-link를-acceptance-statement가-없는-bundle은-requirement-task-step-deep-link를-만들고-plan에-없는-cross-source-관계를-추론하지-않아야-한다)
- [spec kind의 current·comparison statement deep link와 plan kind의 context statement·Task·Step deep link는 bundle path·member path·exact heading에서 계산한 내부 key를 포함해 DOM ID 충돌 없이 해당 Visual Docs의 panel과 대상을 열어야 한다. 화면에는 full statement와 path를 표시해야 한다.](adaptive-presentation-and-navigation.md#spec-kind의-currentcomparison-statement-deep-link와-plan-kind의-context-statementtaskstep-deep-link는-bundle-pathmember-pathexact-heading에서-계산한-내부-key를-포함해-dom-id-충돌-없이-해당-visual-docs의-panel과-대상을-열어야-한다-화면에는-full-statement와-path를-표시해야-한다)
- [Acceptance Criterion 검토 checkbox와 Step 검토 checkbox는 bundle·member·statement 기반 내부 namespace와 종류를 구분해 localStorage에 저장해야 하며 내부 key를 표시하거나 제품 검증 PASS/FAIL로 표시하지 않아야 한다.](adaptive-presentation-and-navigation.md#acceptance-criterion-검토-checkbox와-step-검토-checkbox는-bundlememberstatement-기반-내부-namespace와-종류를-구분해-localstorage에-저장해야-하며-내부-key를-표시하거나-제품-검증-passfail로-표시하지-않아야-한다)

### Related Specs context가 있는 large-plan fixture의 Task가 의미 있는 Route로 표시되고 Route 순서와 Task membership이 plan primary source set과 일치하며 context source가 Route membership을 바꾸지 않는다.

검증하는 요구사항:

- [Scale fixture는 여러 member와 Mermaid를 가진 current bundle, 여러 Task와 Step을 가진 독립 plan primary set과 Related Specs context 0..N을 사용하며, 각 Visual Docs 집계는 source role별 실제 수와 정확히 일치해야 한다.](source-selection-and-freshness.md#scale-fixture는-여러-member와-mermaid를-가진-current-bundle-여러-task와-step을-가진-독립-plan-primary-set과-related-specs-context-0n을-사용하며-각-visual-docs-집계는-source-role별-실제-수와-정확히-일치해야-한다)
- [구조화된 파일 계획에서 Route나 Milestone을 사용하면 실제 단계를 표현하고 각 Task의 primary Route를 명확히 해야 한다.](plan-context-and-statement-traceability.md#구조화된-파일-계획에서-route나-milestone을-사용하면-실제-단계를-표현하고-각-task의-primary-route를-명확히-해야-한다)
- [Route를 사용하는 큰 plan fixture는 source의 단계와 Task dependency를 의미 있게 표시해야 한다.](plan-context-and-statement-traceability.md#route를-사용하는-큰-plan-fixture는-source의-단계와-task-dependency를-의미-있게-표시해야-한다)

### 복잡한 plan fixture에는 독립 경로, 선택적인 Related Specs, 변경 범위에 맞는 Governing statements, 실행 가능한 Task와 검증, 실제 단계의 Route와 checkpoint가 존재하며 불필요한 전체 구현 코드나 관계가 없는 diagram이 추가되지 않는다.

검증하는 요구사항:

- [구조화된 파일 계획은 목표·산출물·검증을 명확히 하고 파일 경계·의존성·Interface·복구·승인 정보와 diagram은 실행이나 검토에 필요한 만큼 포함해야 한다.](plan-context-and-statement-traceability.md#구조화된-파일-계획은-목표산출물검증을-명확히-하고-파일-경계의존성interface복구승인-정보와-diagram은-실행이나-검토에-필요한-만큼-포함해야-한다)
- [계획의 계약 검증 범위는 완료 주장에 맞게 선택하고 구조화된 파일 계획은 해당 Governing statements 링크와 회귀 증거를 연결하며 coverage table은 검토에 도움이 될 때 사용해야 한다.](plan-context-and-statement-traceability.md#계획의-계약-검증-범위는-완료-주장에-맞게-선택하고-구조화된-파일-계획은-해당-governing-statements-링크와-회귀-증거를-연결하며-coverage-table은-검토에-도움이-될-때-사용해야-한다)
- [계획의 diagram은 검토에 도움이 되는 source 관계를 설명할 때 사용하고 단계를 채우기 위한 diagram을 만들지 않아야 한다.](plan-context-and-statement-traceability.md#계획의-diagram은-검토에-도움이-되는-source-관계를-설명할-때-사용하고-단계를-채우기-위한-diagram을-만들지-않아야-한다)
- [구조화된 파일 계획에서 큰 Task 집합을 diagram으로 표시할 때는 읽기 쉬운 실제 단계나 관계로 구성하고 의미 없는 평면 연결을 피해야 한다.](plan-context-and-statement-traceability.md#구조화된-파일-계획에서-큰-task-집합을-diagram으로-표시할-때는-읽기-쉬운-실제-단계나-관계로-구성하고-의미-없는-평면-연결을-피해야-한다)
- [plan의 diagram과 책임 표는 plan에서 선택한 언어로 작성하되 Related Specs context에서 인용한 값과 API, service, schema, code identifier는 원문을 유지하고 source provenance를 표시해야 한다.](plan-context-and-statement-traceability.md#plan의-diagram과-책임-표는-plan에서-선택한-언어로-작성하되-related-specs-context에서-인용한-값과-api-service-schema-code-identifier는-원문을-유지하고-source-provenance를-표시해야-한다)
- [구조화된 파일 계획은 `Related Specs`에 0개 이상의 unique normalized bundle path를 선언하고 governed Task의 `Governing statements`를 선언된 bundle의 exact statement에 연결해야 한다.](plan-context-and-statement-traceability.md#구조화된-파일-계획은-related-specs에-0개-이상의-unique-normalized-bundle-path를-선언하고-governed-task의-governing-statements를-선언된-bundle의-exact-statement에-연결해야-한다)
- [계획이 지속 계약 의미를 바꾸면 승인된 Canonical Spec을 참조하고 승인 동작의 복원이나 code·test로 충분한 국소 구현에는 새 정본을 요구하지 않아야 한다.](plan-context-and-statement-traceability.md#계획이-지속-계약-의미를-바꾸면-승인된-canonical-spec을-참조하고-승인-동작의-복원이나-codetest로-충분한-국소-구현에는-새-정본을-요구하지-않아야-한다)
- [진행 기록은 앱이나 기존 작업 기록을 재사용하고 구조화된 파일 계획을 보존할 때 Task checkbox·Progress History 또는 같은 디렉터리의 progress 기록을 활용해야 한다.](plan-context-and-statement-traceability.md#진행-기록은-앱이나-기존-작업-기록을-재사용하고-구조화된-파일-계획을-보존할-때-task-checkboxprogress-history-또는-같은-디렉터리의-progress-기록을-활용해야-한다)
- [구조화된 파일 계획의 Task는 독립 소유권이나 검토·복구에 도움이 될 때 같은 plan 디렉터리의 `tasks/*.md`로 분리할 수 있어야 한다.](plan-context-and-statement-traceability.md#구조화된-파일-계획의-task는-독립-소유권이나-검토복구에-도움이-될-때-같은-plan-디렉터리의-tasksmd로-분리할-수-있어야-한다)

### 저장된 plan kind Visual Docs가 있는 Task checkpoint에서 primary set이나 Related Specs context가 변경되어도 자동 갱신하지 않고 Markdown으로 보고하며, 사용자가 갱신을 명시적으로 요청한 경우에만 current primary set과 context sources를 포함해 같은 view-id를 재생성한다.

검증하는 요구사항:

- [`executing-plans`는 Visual Docs가 이미 존재하더라도 사용자의 명시적 요청이 없는 한 Task checkpoint 후 plan kind Visual Docs나 Project Handbook을 갱신하지 않아야 한다.](human-readable-review-viewer.md#executing-plans는-visual-docs가-이미-존재하더라도-사용자의-명시적-요청이-없는-한-task-checkpoint-후-plan-kind-visual-docs나-project-handbook을-갱신하지-않아야-한다)
- [사용자가 현재 Brief, Plan, Spec 또는 Project의 시각화나 Visual Docs 생성·갱신을 명시적으로 요청한 경우에만 Forge는 복잡도 점수와 관계없이 해당 Visual Docs를 생성하거나 갱신해야 한다.](human-readable-review-viewer.md#사용자가-현재-brief-plan-spec-또는-project의-시각화나-visual-docs-생성갱신을-명시적으로-요청한-경우에만-forge는-복잡도-점수와-관계없이-해당-visual-docs를-생성하거나-갱신해야-한다)
- [`plan` kind에서는 `plan.md`와 존재하는 경우 같은 디렉터리의 `progress.md`, `tasks/*.md`를 primary source set으로 사용하고, plan의 `Related Specs` bundle 0개 이상을 제품 요구사항을 설명하는 context source로 읽되 plan source와 병합하거나 동일한 ownership으로 표시하지 않아야 한다.](source-selection-and-freshness.md#plan-kind에서는-planmd와-존재하는-경우-같은-디렉터리의-progressmd-tasksmd를-primary-source-set으로-사용하고-plan의-related-specs-bundle-0개-이상을-제품-요구사항을-설명하는-context-source로-읽되-plan-source와-병합하거나-동일한-ownership으로-표시하지-않아야-한다)
- [저장된 Visual Docs의 source가 변경되면 Forge는 그 Visual Docs가 stale임을 사용자에게 알릴 수 있지만, 명시적 요청 전에는 stale Visual Docs를 갱신하거나 현재 검토 화면으로 제시하지 않아야 한다.](human-readable-review-viewer.md#저장된-visual-docs의-source가-변경되면-forge는-그-visual-docs가-stale임을-사용자에게-알릴-수-있지만-명시적-요청-전에는-stale-visual-docs를-갱신하거나-현재-검토-화면으로-제시하지-않아야-한다)

### 정본이 필요 없는 구현·복원·운영 계획과 승인된 bundle을 참조하는 계약 변경 계획은 독립 경로를 유지하고 잘못된 bundle·statement 링크·path escape 및 승인되지 않은 지속 계약 변경은 거부된다.

검증하는 요구사항:

- [구조화된 파일 계획은 `Related Specs`에 0개 이상의 unique normalized bundle path를 선언하고 governed Task의 `Governing statements`를 선언된 bundle의 exact statement에 연결해야 한다.](plan-context-and-statement-traceability.md#구조화된-파일-계획은-related-specs에-0개-이상의-unique-normalized-bundle-path를-선언하고-governed-task의-governing-statements를-선언된-bundle의-exact-statement에-연결해야-한다)
- [계획이 지속 계약 의미를 바꾸면 승인된 Canonical Spec을 참조하고 승인 동작의 복원이나 code·test로 충분한 국소 구현에는 새 정본을 요구하지 않아야 한다.](plan-context-and-statement-traceability.md#계획이-지속-계약-의미를-바꾸면-승인된-canonical-spec을-참조하고-승인-동작의-복원이나-codetest로-충분한-국소-구현에는-새-정본을-요구하지-않아야-한다)

### 앱 계획과 구조화된 파일 계획을 사용하는 사례에서 기존 진행 기록을 재사용하고 필요한 경우에만 progress·Task 파일을 추가하며 plan 삭제 전 영구 결정은 정본이나 ADR에 보존한다.

검증하는 요구사항:

- [진행 기록은 앱이나 기존 작업 기록을 재사용하고 구조화된 파일 계획을 보존할 때 Task checkbox·Progress History 또는 같은 디렉터리의 progress 기록을 활용해야 한다.](plan-context-and-statement-traceability.md#진행-기록은-앱이나-기존-작업-기록을-재사용하고-구조화된-파일-계획을-보존할-때-task-checkboxprogress-history-또는-같은-디렉터리의-progress-기록을-활용해야-한다)
- [구조화된 파일 계획의 Task는 독립 소유권이나 검토·복구에 도움이 될 때 같은 plan 디렉터리의 `tasks/*.md`로 분리할 수 있어야 한다.](plan-context-and-statement-traceability.md#구조화된-파일-계획의-task는-독립-소유권이나-검토복구에-도움이-될-때-같은-plan-디렉터리의-tasksmd로-분리할-수-있어야-한다)
- [삭제 예정 plan의 영구 보존 가치가 있는 제품 결정은 삭제 전에 governing spec, ADR 또는 동등한 영구 문서로 이전해야 한다.](plan-context-and-statement-traceability.md#삭제-예정-plan의-영구-보존-가치가-있는-제품-결정은-삭제-전에-governing-spec-adr-또는-동등한-영구-문서로-이전해야-한다)
