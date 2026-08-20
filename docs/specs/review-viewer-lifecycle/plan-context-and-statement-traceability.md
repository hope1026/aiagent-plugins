# Plan Context와 문장 추적성

## Requirements

### Forge는 `docs/plans/PPP-<slug>/plan.md`를 작업 단위의 목표, Route, Task, 파일, Interface, 검증 절차의 source of truth로 유지해야 하며 plan 번호는 spec 번호와 독립적으로 부여해야 한다.

### plan kind의 Overview는 목표, primary plan의 Task·Step 집계, context bundle별 Requirement·Acceptance Criterion 집계, 읽기 순서, 사용자 경험, 완료 상태를 분리해 보여줘야 한다.

### plan kind의 Requirements는 Global Constraints, 핵심 정책, Route별 적용 범위와 Related Specs의 full statement context를 member provenance와 함께 보여줘야 한다.

### plan kind의 Flows는 Route map, Task dependency, runtime 또는 확장 흐름을 보여줘야 한다.

### plan kind의 Data & Interfaces는 runtime 책임, 서버 권위, 파일, Remote, transaction, Interface 계약을 보여줘야 한다.

### plan kind의 Acceptance는 plan에 명시된 Related Specs의 statement link만 사용해야 한다. Acceptance statement가 있는 bundle은 Requirement → Acceptance Criterion → Task → Step·검증 mapping을, Acceptance statement가 없는 bundle은 Requirement → Task → Step·검증 mapping을 보여주고, 관련 spec이 없으면 Task → Step·검증 mapping을 검토 상태와 함께 보여줘야 한다.

### plan kind의 History는 plan 상태, Task checkbox, Progress History, 선택적인 `progress.md`·`tasks/*.md`, primary·auxiliary·context source별 role·path·hash, checkpoint, 관련 commit, 재생성 command를 보여줘야 한다.

### `writing-plans`는 6~10개의 Route 또는 Milestone으로 Task를 묶고 각 Task가 하나의 primary Route에 속하도록 작성해야 한다.

### 큰 plan fixture의 Task는 의미 있는 Route로 묶여 실행 순서와 dependency가 표시되어야 한다.

### plan kind는 plan에 명시된 bundle path, member statement link와 Task·Step 관계만 사용해야 한다. Acceptance statement가 있는 bundle은 Requirement → Acceptance Criterion → Task → Step deep link를, Acceptance statement가 없는 bundle은 Requirement → Task → Step deep link를 만들고, plan에 없는 cross-source 관계를 추론하지 않아야 한다.

### `writing-plans`는 목표와 완료 상태, `Related Specs`, Implementation Route 또는 Milestone, Task dependency, Runtime responsibility, 주요 데이터 흐름, Place 또는 platform 확장 지점, Task별 검증 mapping, checkpoint와 사용자 검토 시점을 plan 필수 구조로 요구해야 한다. 관련 spec이 있으면 Task별 `Governing statements`가 member path·anchor와 exact heading link로 필요한 Requirement·Acceptance Criterion을 직접 참조해야 한다.

### `writing-plans`는 Related Spec에 Acceptance statement가 하나 이상 있으면 모든 Acceptance statement를 Task에 매핑하고, 없으면 모든 Requirement statement를 Task에 매핑해야 한다. 각 mapped statement는 statement coverage table과 Task의 `Governing statements:`에서 member path·anchor·exact heading link로 추적되어야 한다.

### 복잡한 plan은 Task dependency 또는 Route map, runtime responsibility 또는 transaction flow, 확장 구조 또는 multi-Place flow의 세 diagram 관점을 포함해야 한다.

### `writing-plans`는 큰 Task 집합을 한 diagram에 평면적으로 연결하지 않고 먼저 6~10개의 의미 있는 Route로 묶도록 요구해야 한다.

### plan의 diagram과 책임 표는 plan에서 선택한 언어로 작성하되 Related Specs context에서 인용한 값과 API, service, schema, code identifier는 원문을 유지하고 source provenance를 표시해야 한다.

### spec은 프로젝트 수명 동안 영구 관리하고, plan은 작업 단위로 생성하며 작업 종료 뒤 보존 가치가 없으면 plan 디렉터리 전체를 삭제할 수 있어야 한다.

### Plan은 `Related Specs`에서 0개 이상의 unique normalized bundle directory path를 canonical entry로 선언해야 한다. 각 governed Task의 `Governing statements`는 선언된 bundle 안의 exact Requirement·Acceptance statement를 repository-contained Markdown link로 참조해야 한다. Plan의 경로·번호·수명 주기는 특정 spec에 종속시키지 않아야 한다.

### 제품 동작을 변경하는 plan은 하나 이상의 approved spec을 참조해야 하며, spec 없이 작성하는 plan은 Forge ceremony floor에 해당하는 작업이나 제품 동작을 바꾸지 않는 운영·조사 작업으로 제한해야 한다.

### plan의 진행 상태는 기본적으로 `plan.md`의 Task checkbox와 `Progress History`에서 관리하고, 기록이 길거나 여러 실행 주체가 독립적으로 갱신할 때만 같은 plan 디렉터리의 `progress.md`를 사용해야 한다.

### Task별 독립 소유권·병렬 실행·독립 승인이 필요한 큰 plan만 `docs/plans/PPP-<slug>/tasks/*.md`로 Task를 분리하고, 작은 plan은 단일 `plan.md`를 유지해야 한다.

### 삭제 예정 plan의 영구 보존 가치가 있는 제품 결정은 삭제 전에 governing spec, ADR 또는 동등한 영구 문서로 이전해야 한다.

## Acceptance Criteria

### Acceptance statement가 있는 bundle과 없는 bundle을 함께 참조하는 `plan.md`, `progress.md`, `tasks/*.md` fixture를 plan kind로 build하면 primary Task·Step count와 context bundle·member별 Requirement·Acceptance Criterion count가 분리되고, plan에 명시된 full-statement link만 사용해 각각 Requirement → Acceptance Criterion → Task → Step과 Requirement → Task → Step mapping이 만들어진다.

검증하는 요구사항:

- [`plan` kind에서는 `plan.md`와 존재하는 경우 같은 디렉터리의 `progress.md`, `tasks/*.md`를 primary source set으로 사용하고, plan의 `Related Specs` bundle 0개 이상을 제품 요구사항을 설명하는 context source로 읽되 plan source와 병합하거나 동일한 ownership으로 표시하지 않아야 한다.](source-selection-and-freshness.md#plan-kind에서는-planmd와-존재하는-경우-같은-디렉터리의-progressmd-tasksmd를-primary-source-set으로-사용하고-plan의-related-specs-bundle-0개-이상을-제품-요구사항을-설명하는-context-source로-읽되-plan-source와-병합하거나-동일한-ownership으로-표시하지-않아야-한다)
- [plan kind의 Overview는 목표, primary plan의 Task·Step 집계, context bundle별 Requirement·Acceptance Criterion 집계, 읽기 순서, 사용자 경험, 완료 상태를 분리해 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-kind의-overview는-목표-primary-plan의-taskstep-집계-context-bundle별-requirementacceptance-criterion-집계-읽기-순서-사용자-경험-완료-상태를-분리해-보여줘야-한다)
- [plan kind의 Requirements는 Global Constraints, 핵심 정책, Route별 적용 범위와 Related Specs의 full statement context를 member provenance와 함께 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-kind의-requirements는-global-constraints-핵심-정책-route별-적용-범위와-related-specs의-full-statement-context를-member-provenance와-함께-보여줘야-한다)
- [plan kind의 Acceptance는 plan에 명시된 Related Specs의 statement link만 사용해야 한다. Acceptance statement가 있는 bundle은 Requirement → Acceptance Criterion → Task → Step·검증 mapping을, Acceptance statement가 없는 bundle은 Requirement → Task → Step·검증 mapping을 보여주고, 관련 spec이 없으면 Task → Step·검증 mapping을 검토 상태와 함께 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-kind의-acceptance는-plan에-명시된-related-specs의-statement-link만-사용해야-한다-acceptance-statement가-있는-bundle은-requirement-acceptance-criterion-task-step검증-mapping을-acceptance-statement가-없는-bundle은-requirement-task-step검증-mapping을-보여주고-관련-spec이-없으면-task-step검증-mapping을-검토-상태와-함께-보여줘야-한다)
- [`writing-plans`는 Related Spec에 Acceptance statement가 하나 이상 있으면 모든 Acceptance statement를 Task에 매핑하고, 없으면 모든 Requirement statement를 Task에 매핑해야 한다. 각 mapped statement는 statement coverage table과 Task의 `Governing statements:`에서 member path·anchor·exact heading link로 추적되어야 한다.](plan-context-and-statement-traceability.md#writing-plans는-related-spec에-acceptance-statement가-하나-이상-있으면-모든-acceptance-statement를-task에-매핑하고-없으면-모든-requirement-statement를-task에-매핑해야-한다-각-mapped-statement는-statement-coverage-table과-task의-governing-statements에서-member-pathanchorexact-heading-link로-추적되어야-한다)
- [plan kind의 History는 plan 상태, Task checkbox, Progress History, 선택적인 `progress.md`·`tasks/*.md`, primary·auxiliary·context source별 role·path·hash, checkpoint, 관련 commit, 재생성 command를 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-kind의-history는-plan-상태-task-checkbox-progress-history-선택적인-progressmdtasksmd-primaryauxiliarycontext-source별-rolepathhash-checkpoint-관련-commit-재생성-command를-보여줘야-한다)
- [Visual Docs는 원문 상세를 처음부터 펼치지 않고 요약, 시각 흐름, 상세 source, acceptance evidence 순서로 배치해야 한다.](adaptive-presentation-and-navigation.md#visual-docs는-원문-상세를-처음부터-펼치지-않고-요약-시각-흐름-상세-source-acceptance-evidence-순서로-배치해야-한다)
- [Visual Docs는 spec kind에서 current bundle과 comparison bundle의 Requirement·Acceptance Criterion·Mermaid 수를 bundle과 member별로 분리하고, plan kind에서 primary source set의 Task·Step·Mermaid 수와 Related Specs context의 Requirement·Acceptance Criterion·Mermaid 수를 source별로 분리해 summary에 표시해야 한다.](source-selection-and-freshness.md#visual-docs는-spec-kind에서-current-bundle과-comparison-bundle의-requirementacceptance-criterionmermaid-수를-bundle과-member별로-분리하고-plan-kind에서-primary-source-set의-taskstepmermaid-수와-related-specs-context의-requirementacceptance-criterionmermaid-수를-source별로-분리해-summary에-표시해야-한다)
- [집계 기준은 structured parser가 인식한 `### Task N` heading, `Step N` checkbox, Requirements와 Acceptance Criteria 아래의 unique full-statement H3, Mermaid fence 수로 고정해야 한다. plan primary set 안의 Task·Step은 중복 제거하고 context statement는 bundle path·member path·statement kind·exact heading에서 계산한 내부 namespace로 구분하되 이를 화면 label로 노출하지 않아야 한다.](source-selection-and-freshness.md#집계-기준은-structured-parser가-인식한-task-n-heading-step-n-checkbox-requirements와-acceptance-criteria-아래의-unique-full-statement-h3-mermaid-fence-수로-고정해야-한다-plan-primary-set-안의-taskstep은-중복-제거하고-context-statement는-bundle-pathmember-pathstatement-kindexact-heading에서-계산한-내부-namespace로-구분하되-이를-화면-label로-노출하지-않아야-한다)
- [plan kind는 plan에 명시된 bundle path, member statement link와 Task·Step 관계만 사용해야 한다. Acceptance statement가 있는 bundle은 Requirement → Acceptance Criterion → Task → Step deep link를, Acceptance statement가 없는 bundle은 Requirement → Task → Step deep link를 만들고, plan에 없는 cross-source 관계를 추론하지 않아야 한다.](plan-context-and-statement-traceability.md#plan-kind는-plan에-명시된-bundle-path-member-statement-link와-taskstep-관계만-사용해야-한다-acceptance-statement가-있는-bundle은-requirement-acceptance-criterion-task-step-deep-link를-acceptance-statement가-없는-bundle은-requirement-task-step-deep-link를-만들고-plan에-없는-cross-source-관계를-추론하지-않아야-한다)
- [spec kind의 current·comparison statement deep link와 plan kind의 context statement·Task·Step deep link는 bundle path·member path·exact heading에서 계산한 내부 key를 포함해 DOM ID 충돌 없이 해당 Visual Docs의 panel과 대상을 열어야 한다. 화면에는 full statement와 path를 표시해야 한다.](adaptive-presentation-and-navigation.md#spec-kind의-currentcomparison-statement-deep-link와-plan-kind의-context-statementtaskstep-deep-link는-bundle-pathmember-pathexact-heading에서-계산한-내부-key를-포함해-dom-id-충돌-없이-해당-visual-docs의-panel과-대상을-열어야-한다-화면에는-full-statement와-path를-표시해야-한다)
- [Acceptance Criterion 검토 checkbox와 Step 검토 checkbox는 bundle·member·statement 기반 내부 namespace와 종류를 구분해 localStorage에 저장해야 하며 내부 key를 표시하거나 제품 검증 PASS/FAIL로 표시하지 않아야 한다.](adaptive-presentation-and-navigation.md#acceptance-criterion-검토-checkbox와-step-검토-checkbox는-bundlememberstatement-기반-내부-namespace와-종류를-구분해-localstorage에-저장해야-하며-내부-key를-표시하거나-제품-검증-passfail로-표시하지-않아야-한다)

### Related Specs context가 있는 large-plan fixture의 Task가 의미 있는 Route로 표시되고 Route 순서와 Task membership이 plan primary source set과 일치하며 context source가 Route membership을 바꾸지 않는다.

검증하는 요구사항:

- [Scale fixture는 여러 member와 Mermaid를 가진 current bundle, 여러 Task와 Step을 가진 독립 plan primary set과 Related Specs context 0..N을 사용하며, 각 Visual Docs 집계는 source role별 실제 수와 정확히 일치해야 한다.](source-selection-and-freshness.md#scale-fixture는-여러-member와-mermaid를-가진-current-bundle-여러-task와-step을-가진-독립-plan-primary-set과-related-specs-context-0n을-사용하며-각-visual-docs-집계는-source-role별-실제-수와-정확히-일치해야-한다)
- [`writing-plans`는 6~10개의 Route 또는 Milestone으로 Task를 묶고 각 Task가 하나의 primary Route에 속하도록 작성해야 한다.](plan-context-and-statement-traceability.md#writing-plans는-610개의-route-또는-milestone으로-task를-묶고-각-task가-하나의-primary-route에-속하도록-작성해야-한다)
- [큰 plan fixture의 Task는 의미 있는 Route로 묶여 실행 순서와 dependency가 표시되어야 한다.](plan-context-and-statement-traceability.md#큰-plan-fixture의-task는-의미-있는-route로-묶여-실행-순서와-dependency가-표시되어야-한다)

### 복잡한 plan을 작성하면 독립 plan path, 선택적인 bundle-path `Related Specs`, Task별 `Governing statements`, 필수 구조, 6~10 Route grouping, plan source로부터 만든 diagram 관점, checkpoint가 존재하고 Task 분리는 독립 소유권·병렬 실행·독립 승인 조건에서만 사용된다.

검증하는 요구사항:

- [`writing-plans`는 목표와 완료 상태, `Related Specs`, Implementation Route 또는 Milestone, Task dependency, Runtime responsibility, 주요 데이터 흐름, Place 또는 platform 확장 지점, Task별 검증 mapping, checkpoint와 사용자 검토 시점을 plan 필수 구조로 요구해야 한다. 관련 spec이 있으면 Task별 `Governing statements`가 member path·anchor와 exact heading link로 필요한 Requirement·Acceptance Criterion을 직접 참조해야 한다.](plan-context-and-statement-traceability.md#writing-plans는-목표와-완료-상태-related-specs-implementation-route-또는-milestone-task-dependency-runtime-responsibility-주요-데이터-흐름-place-또는-platform-확장-지점-task별-검증-mapping-checkpoint와-사용자-검토-시점을-plan-필수-구조로-요구해야-한다-관련-spec이-있으면-task별-governing-statements가-member-pathanchor와-exact-heading-link로-필요한-requirementacceptance-criterion을-직접-참조해야-한다)
- [`writing-plans`는 Related Spec에 Acceptance statement가 하나 이상 있으면 모든 Acceptance statement를 Task에 매핑하고, 없으면 모든 Requirement statement를 Task에 매핑해야 한다. 각 mapped statement는 statement coverage table과 Task의 `Governing statements:`에서 member path·anchor·exact heading link로 추적되어야 한다.](plan-context-and-statement-traceability.md#writing-plans는-related-spec에-acceptance-statement가-하나-이상-있으면-모든-acceptance-statement를-task에-매핑하고-없으면-모든-requirement-statement를-task에-매핑해야-한다-각-mapped-statement는-statement-coverage-table과-task의-governing-statements에서-member-pathanchorexact-heading-link로-추적되어야-한다)
- [복잡한 plan은 Task dependency 또는 Route map, runtime responsibility 또는 transaction flow, 확장 구조 또는 multi-Place flow의 세 diagram 관점을 포함해야 한다.](plan-context-and-statement-traceability.md#복잡한-plan은-task-dependency-또는-route-map-runtime-responsibility-또는-transaction-flow-확장-구조-또는-multi-place-flow의-세-diagram-관점을-포함해야-한다)
- [`writing-plans`는 큰 Task 집합을 한 diagram에 평면적으로 연결하지 않고 먼저 6~10개의 의미 있는 Route로 묶도록 요구해야 한다.](plan-context-and-statement-traceability.md#writing-plans는-큰-task-집합을-한-diagram에-평면적으로-연결하지-않고-먼저-610개의-의미-있는-route로-묶도록-요구해야-한다)
- [plan의 diagram과 책임 표는 plan에서 선택한 언어로 작성하되 Related Specs context에서 인용한 값과 API, service, schema, code identifier는 원문을 유지하고 source provenance를 표시해야 한다.](plan-context-and-statement-traceability.md#plan의-diagram과-책임-표는-plan에서-선택한-언어로-작성하되-related-specs-context에서-인용한-값과-api-service-schema-code-identifier는-원문을-유지하고-source-provenance를-표시해야-한다)
- [Plan은 `Related Specs`에서 0개 이상의 unique normalized bundle directory path를 canonical entry로 선언해야 한다. 각 governed Task의 `Governing statements`는 선언된 bundle 안의 exact Requirement·Acceptance statement를 repository-contained Markdown link로 참조해야 한다. Plan의 경로·번호·수명 주기는 특정 spec에 종속시키지 않아야 한다.](plan-context-and-statement-traceability.md#plan은-related-specs에서-0개-이상의-unique-normalized-bundle-directory-path를-canonical-entry로-선언해야-한다-각-governed-task의-governing-statements는-선언된-bundle-안의-exact-requirementacceptance-statement를-repository-contained-markdown-link로-참조해야-한다-plan의-경로번호수명-주기는-특정-spec에-종속시키지-않아야-한다)
- [제품 동작을 변경하는 plan은 하나 이상의 approved spec을 참조해야 하며, spec 없이 작성하는 plan은 Forge ceremony floor에 해당하는 작업이나 제품 동작을 바꾸지 않는 운영·조사 작업으로 제한해야 한다.](plan-context-and-statement-traceability.md#제품-동작을-변경하는-plan은-하나-이상의-approved-spec을-참조해야-하며-spec-없이-작성하는-plan은-forge-ceremony-floor에-해당하는-작업이나-제품-동작을-바꾸지-않는-운영조사-작업으로-제한해야-한다)
- [plan의 진행 상태는 기본적으로 `plan.md`의 Task checkbox와 `Progress History`에서 관리하고, 기록이 길거나 여러 실행 주체가 독립적으로 갱신할 때만 같은 plan 디렉터리의 `progress.md`를 사용해야 한다.](plan-context-and-statement-traceability.md#plan의-진행-상태는-기본적으로-planmd의-task-checkbox와-progress-history에서-관리하고-기록이-길거나-여러-실행-주체가-독립적으로-갱신할-때만-같은-plan-디렉터리의-progressmd를-사용해야-한다)
- [Task별 독립 소유권·병렬 실행·독립 승인이 필요한 큰 plan만 `docs/plans/PPP-<slug>/tasks/*.md`로 Task를 분리하고, 작은 plan은 단일 `plan.md`를 유지해야 한다.](plan-context-and-statement-traceability.md#task별-독립-소유권병렬-실행독립-승인이-필요한-큰-plan만-docsplansppp-slugtasksmd로-task를-분리하고-작은-plan은-단일-planmd를-유지해야-한다)

### 저장된 plan kind Visual Docs가 있는 Task checkpoint에서 primary set이나 Related Specs context가 변경되어도 자동 갱신하지 않고 Markdown으로 보고하며, 사용자가 갱신을 명시적으로 요청한 경우에만 current primary set과 context sources를 포함해 같은 view-id를 재생성한다.

검증하는 요구사항:

- [`executing-plans`는 Visual Docs가 이미 존재하더라도 사용자의 명시적 요청이 없는 한 Task checkpoint 후 plan kind Visual Docs나 Project Handbook을 갱신하지 않아야 한다.](human-readable-review-viewer.md#executing-plans는-visual-docs가-이미-존재하더라도-사용자의-명시적-요청이-없는-한-task-checkpoint-후-plan-kind-visual-docs나-project-handbook을-갱신하지-않아야-한다)
- [사용자가 현재 Brief, Plan, Spec 또는 Project의 시각화나 Visual Docs 생성·갱신을 명시적으로 요청한 경우에만 Forge는 복잡도 점수와 관계없이 해당 Visual Docs를 생성하거나 갱신해야 한다.](human-readable-review-viewer.md#사용자가-현재-brief-plan-spec-또는-project의-시각화나-visual-docs-생성갱신을-명시적으로-요청한-경우에만-forge는-복잡도-점수와-관계없이-해당-visual-docs를-생성하거나-갱신해야-한다)
- [`plan` kind에서는 `plan.md`와 존재하는 경우 같은 디렉터리의 `progress.md`, `tasks/*.md`를 primary source set으로 사용하고, plan의 `Related Specs` bundle 0개 이상을 제품 요구사항을 설명하는 context source로 읽되 plan source와 병합하거나 동일한 ownership으로 표시하지 않아야 한다.](source-selection-and-freshness.md#plan-kind에서는-planmd와-존재하는-경우-같은-디렉터리의-progressmd-tasksmd를-primary-source-set으로-사용하고-plan의-related-specs-bundle-0개-이상을-제품-요구사항을-설명하는-context-source로-읽되-plan-source와-병합하거나-동일한-ownership으로-표시하지-않아야-한다)
- [저장된 Visual Docs의 source가 변경되면 Forge는 그 Visual Docs가 stale임을 사용자에게 알릴 수 있지만, 명시적 요청 전에는 stale Visual Docs를 갱신하거나 현재 검토 화면으로 제시하지 않아야 한다.](human-readable-review-viewer.md#저장된-visual-docs의-source가-변경되면-forge는-그-visual-docs가-stale임을-사용자에게-알릴-수-있지만-명시적-요청-전에는-stale-visual-docs를-갱신하거나-현재-검토-화면으로-제시하지-않아야-한다)

### 관련 spec이 없는 운영 plan, 하나의 approved bundle을 참조하는 기능 plan, 여러 approved bundle을 참조하는 교차 기능 plan을 canonical Related Specs 문법으로 작성하면 모두 독립 plan 경로를 유지한다. 중복·존재하지 않는 bundle, 존재하지 않거나 link text가 다른 statement, repository path escape와 approved bundle 없이 제품 동작을 변경하려는 plan은 작성 단계에서 거부된다.

검증하는 요구사항:

- [Plan은 `Related Specs`에서 0개 이상의 unique normalized bundle directory path를 canonical entry로 선언해야 한다. 각 governed Task의 `Governing statements`는 선언된 bundle 안의 exact Requirement·Acceptance statement를 repository-contained Markdown link로 참조해야 한다. Plan의 경로·번호·수명 주기는 특정 spec에 종속시키지 않아야 한다.](plan-context-and-statement-traceability.md#plan은-related-specs에서-0개-이상의-unique-normalized-bundle-directory-path를-canonical-entry로-선언해야-한다-각-governed-task의-governing-statements는-선언된-bundle-안의-exact-requirementacceptance-statement를-repository-contained-markdown-link로-참조해야-한다-plan의-경로번호수명-주기는-특정-spec에-종속시키지-않아야-한다)
- [제품 동작을 변경하는 plan은 하나 이상의 approved spec을 참조해야 하며, spec 없이 작성하는 plan은 Forge ceremony floor에 해당하는 작업이나 제품 동작을 바꾸지 않는 운영·조사 작업으로 제한해야 한다.](plan-context-and-statement-traceability.md#제품-동작을-변경하는-plan은-하나-이상의-approved-spec을-참조해야-하며-spec-없이-작성하는-plan은-forge-ceremony-floor에-해당하는-작업이나-제품-동작을-바꾸지-않는-운영조사-작업으로-제한해야-한다)

### 작은 plan의 진행 상태는 `plan.md`만으로 관리되고, 긴 checkpoint fixture는 `progress.md`, 독립 소유권이 있는 큰 Task fixture는 `tasks/*.md`를 사용하며, plan 삭제 전 영구 결정이 governing spec 또는 ADR로 이전됐는지 확인된다.

검증하는 요구사항:

- [plan의 진행 상태는 기본적으로 `plan.md`의 Task checkbox와 `Progress History`에서 관리하고, 기록이 길거나 여러 실행 주체가 독립적으로 갱신할 때만 같은 plan 디렉터리의 `progress.md`를 사용해야 한다.](plan-context-and-statement-traceability.md#plan의-진행-상태는-기본적으로-planmd의-task-checkbox와-progress-history에서-관리하고-기록이-길거나-여러-실행-주체가-독립적으로-갱신할-때만-같은-plan-디렉터리의-progressmd를-사용해야-한다)
- [Task별 독립 소유권·병렬 실행·독립 승인이 필요한 큰 plan만 `docs/plans/PPP-<slug>/tasks/*.md`로 Task를 분리하고, 작은 plan은 단일 `plan.md`를 유지해야 한다.](plan-context-and-statement-traceability.md#task별-독립-소유권병렬-실행독립-승인이-필요한-큰-plan만-docsplansppp-slugtasksmd로-task를-분리하고-작은-plan은-단일-planmd를-유지해야-한다)
- [삭제 예정 plan의 영구 보존 가치가 있는 제품 결정은 삭제 전에 governing spec, ADR 또는 동등한 영구 문서로 이전해야 한다.](plan-context-and-statement-traceability.md#삭제-예정-plan의-영구-보존-가치가-있는-제품-결정은-삭제-전에-governing-spec-adr-또는-동등한-영구-문서로-이전해야-한다)
