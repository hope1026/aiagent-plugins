# Source 선택과 Freshness

## Requirements

### Review Viewer는 source별 role, bundle·root·member path, 생성 당시 member·bundle SHA-256, 생성 시각, mode, locale, 집계 수치를 manifest에 기록하고 열람 시점 hash와 비교해 `current`, `stale`, `unverified` freshness를 표시해야 한다. 화면의 주 label은 bundle H1, member H1, path와 full statement이고 hash나 내부 key를 identity label로 사용하지 않아야 한다.

### `spec` mode에서는 현재 valid Spec Bundle 전체를 primary source of truth로 사용하고, 사용자가 지정한 0개 이상의 comparison bundle을 비권위 비교 자료로 읽되 모든 내용에 bundle·member source role과 provenance를 표시해야 한다.

### `plan` mode에서는 `plan.md`와 존재하는 경우 같은 디렉터리의 `progress.md`, `tasks/*.md`를 primary source set으로 사용하고, plan의 `Related Specs` bundle 0개 이상을 제품 요구사항을 설명하는 context source로 읽되 plan source와 병합하거나 동일한 ownership으로 표시하지 않아야 한다.

### Review Viewer는 spec mode에서 current bundle과 comparison bundle의 Requirement·Acceptance Criterion·Mermaid 수를 bundle과 member별로 분리하고, plan mode에서 primary source set의 Task·Step·Mermaid 수와 Related Specs context의 Requirement·Acceptance Criterion·Mermaid 수를 source별로 분리해 summary에 표시해야 한다.

### 집계 기준은 structured parser가 인식한 `### Task N` heading, `Step N` checkbox, Requirements와 Acceptance Criteria 아래의 unique full-statement H3, Mermaid fence 수로 고정해야 한다. plan primary set 안의 Task·Step은 중복 제거하고 context statement는 bundle path·member path·statement kind·exact heading에서 계산한 내부 namespace로 구분하되 이를 화면 label로 노출하지 않아야 한다.

### scale fixture는 current bundle에 Requirement 190개, Acceptance Criterion 105개, member 5개와 Mermaid 9개를 두고 독립된 plan primary set에 Task 22개, Step 110개와 Related Specs context 0..N을 두며, 각 Review Viewer 집계는 source role별 실제 수와 정확히 일치해야 한다.

### current bundle과 comparison bundle의 Mermaid는 source text를 byte-for-byte 변경하지 않고 재사용하며 각각 `Current spec source` 또는 `Comparison source`, bundle·member H1과 path를 표시해야 한다.

### plan primary set과 Related Specs bundle context에 작성된 Mermaid는 각 source에서 그대로 가져오고 각각 `Plan source` 또는 `Related spec context`, bundle·member H1과 path를 표시해야 한다.

### Review Viewer는 생성 시점에 각 source의 role, bundle·root·member path, 내부 namespace와 member·bundle SHA-256을 manifest에 기록하되 생성 시점 freshness를 열람 시점의 최신성 보장으로 표시하거나 hash·namespace를 사용자-facing identity로 사용하지 않아야 한다.

### Review Viewer를 HTTP 또는 HTTPS의 same-origin에서 열면 repository 내부의 각 source를 `cache: no-store`로 읽고 Web Crypto API로 SHA-256을 다시 계산해 manifest의 hash와 자동 비교해야 한다.

### `file://` 또는 브라우저 보안 정책으로 source 자동 읽기가 실패하면 Review Viewer는 `unverified`를 표시하고 bundle path와 서로 다른 semantic member filename으로 로컬 Markdown source set을 선택·matching할 수 있어야 한다.

### 수동 freshness 검증을 위해 선택한 파일 내용은 브라우저 밖으로 업로드하거나 전송하지 않아야 한다.

### source별 freshness를 각각 표시하고 primary set과 comparison·context set의 aggregate freshness를 분리해야 한다. 각 set은 하나라도 `stale`이면 `stale`, stale 없이 하나라도 검증하지 못하면 `unverified`, 모든 source가 일치할 때만 `current`로 표시해야 한다.

### source fetch 실패, 누락, 파일명 충돌 또는 hash 계산 실패를 `current`로 간주하지 말고 source별 실패 원인과 다시 검증할 방법을 표시해야 한다.

### command-line freshness check는 로컬 Review Viewer manifest의 source hash와 현재 Markdown source를 비교해 모두 일치하면 성공하고, stale·누락·manifest 오류가 있으면 실패해야 한다. 이 checker는 사용자가 요청한 Review Viewer를 자동 갱신하는 trigger로 사용하지 않아야 한다.

### 같은 source의 provenance는 한 panel의 연속 block 묶음에서 첫 block에 한 번만 표시하고 source가 바뀔 때 다시 표시해야 하며, source role과 bundle·member namespace 구분 및 manifest의 전체 provenance는 보존해야 한다.

### Semantic IR은 bundle·member metadata, source별 outline, 원문 순서의 prose·table·code·Mermaid block, full-statement Requirement·Acceptance Criterion, Task·Step·decision·interface entity, explicit relation과 provenance를 표현해야 한다.

### Parser는 selected bundle의 모든 member block을 Semantic IR에 정확히 한 번 보존하고 각 entity와 relation을 bundle path·member path·internal namespace·line anchor에 연결해야 하며, 인식하지 못한 Markdown도 generic block으로 보존해야 한다.

## Acceptance Criteria

### current structured spec과 comparison source가 있는 fixture를 spec mode로 build하면 deterministic parser가 각 source의 Requirement·Acceptance Criterion·Mermaid를 분리하고 `Current spec source`와 `Comparison source` provenance를 표시하며 각 Mermaid text의 SHA-256이 source fence와 일치한다.

검증하는 요구사항:

- [`spec` mode에서는 현재 valid Spec Bundle 전체를 primary source of truth로 사용하고, 사용자가 지정한 0개 이상의 comparison bundle을 비권위 비교 자료로 읽되 모든 내용에 bundle·member source role과 provenance를 표시해야 한다.](source-selection-and-freshness.md#spec-mode에서는-현재-valid-spec-bundle-전체를-primary-source-of-truth로-사용하고-사용자가-지정한-0개-이상의-comparison-bundle을-비권위-비교-자료로-읽되-모든-내용에-bundlemember-source-role과-provenance를-표시해야-한다)
- [current bundle과 comparison bundle의 Mermaid는 source text를 byte-for-byte 변경하지 않고 재사용하며 각각 `Current spec source` 또는 `Comparison source`, bundle·member H1과 path를 표시해야 한다.](source-selection-and-freshness.md#current-bundle과-comparison-bundle의-mermaid는-source-text를-byte-for-byte-변경하지-않고-재사용하며-각각-current-spec-source-또는-comparison-source-bundlemember-h1과-path를-표시해야-한다)
- [Review Viewer builder는 selected Markdown source를 Semantic IR로 해석하고, View Context로 Presentation Plan을 선택한 뒤 공통 component grammar로 HTML과 manifest를 생성해야 한다. Agent가 작성한 HTML content fragment나 source 밖의 보충 문장을 입력으로 요구하지 않아야 한다.](adaptive-presentation-and-navigation.md#review-viewer-builder는-selected-markdown-source를-semantic-ir로-해석하고-view-context로-presentation-plan을-선택한-뒤-공통-component-grammar로-html과-manifest를-생성해야-한다-agent가-작성한-html-content-fragment나-source-밖의-보충-문장을-입력으로-요구하지-않아야-한다)

### History panel에서 source role·bundle·root·member path, 생성 당시 member·bundle hash, mode, locale, source별 counts, 생성 시각, checkpoint, commit, rebuild command를 확인할 수 있고 primary와 comparison·context freshness가 각각 `unverified`, `stale`, `current`로 표시된다. 일반 panel은 H1, path와 full statement를 주 label로 사용한다.

검증하는 요구사항:

- [Review Viewer는 source별 role, bundle·root·member path, 생성 당시 member·bundle SHA-256, 생성 시각, mode, locale, 집계 수치를 manifest에 기록하고 열람 시점 hash와 비교해 `current`, `stale`, `unverified` freshness를 표시해야 한다. 화면의 주 label은 bundle H1, member H1, path와 full statement이고 hash나 내부 key를 identity label로 사용하지 않아야 한다.](source-selection-and-freshness.md#review-viewer는-source별-role-bundlerootmember-path-생성-당시-memberbundle-sha-256-생성-시각-mode-locale-집계-수치를-manifest에-기록하고-열람-시점-hash와-비교해-current-stale-unverified-freshness를-표시해야-한다-화면의-주-label은-bundle-h1-member-h1-path와-full-statement이고-hash나-내부-key를-identity-label로-사용하지-않아야-한다)
- [plan mode의 History는 plan 상태, Task checkbox, Progress History, 선택적인 `progress.md`·`tasks/*.md`, primary·auxiliary·context source별 role·path·hash, checkpoint, 관련 commit, 재생성 command를 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-mode의-history는-plan-상태-task-checkbox-progress-history-선택적인-progressmdtasksmd-primaryauxiliarycontext-source별-rolepathhash-checkpoint-관련-commit-재생성-command를-보여줘야-한다)
- [Review Viewer는 생성 시점에 각 source의 role, bundle·root·member path, 내부 namespace와 member·bundle SHA-256을 manifest에 기록하되 생성 시점 freshness를 열람 시점의 최신성 보장으로 표시하거나 hash·namespace를 사용자-facing identity로 사용하지 않아야 한다.](source-selection-and-freshness.md#review-viewer는-생성-시점에-각-source의-role-bundlerootmember-path-내부-namespace와-memberbundle-sha-256을-manifest에-기록하되-생성-시점-freshness를-열람-시점의-최신성-보장으로-표시하거나-hashnamespace를-사용자-facing-identity로-사용하지-않아야-한다)
- [Review Viewer를 HTTP 또는 HTTPS의 same-origin에서 열면 repository 내부의 각 source를 `cache: no-store`로 읽고 Web Crypto API로 SHA-256을 다시 계산해 manifest의 hash와 자동 비교해야 한다.](source-selection-and-freshness.md#review-viewer를-http-또는-https의-same-origin에서-열면-repository-내부의-각-source를-cache-no-store로-읽고-web-crypto-api로-sha-256을-다시-계산해-manifest의-hash와-자동-비교해야-한다)
- [`file://` 또는 브라우저 보안 정책으로 source 자동 읽기가 실패하면 Review Viewer는 `unverified`를 표시하고 bundle path와 서로 다른 semantic member filename으로 로컬 Markdown source set을 선택·matching할 수 있어야 한다.](source-selection-and-freshness.md#file-또는-브라우저-보안-정책으로-source-자동-읽기가-실패하면-review-viewer는-unverified를-표시하고-bundle-path와-서로-다른-semantic-member-filename으로-로컬-markdown-source-set을-선택matching할-수-있어야-한다)
- [수동 freshness 검증을 위해 선택한 파일 내용은 브라우저 밖으로 업로드하거나 전송하지 않아야 한다.](source-selection-and-freshness.md#수동-freshness-검증을-위해-선택한-파일-내용은-브라우저-밖으로-업로드하거나-전송하지-않아야-한다)
- [source별 freshness를 각각 표시하고 primary set과 comparison·context set의 aggregate freshness를 분리해야 한다. 각 set은 하나라도 `stale`이면 `stale`, stale 없이 하나라도 검증하지 못하면 `unverified`, 모든 source가 일치할 때만 `current`로 표시해야 한다.](source-selection-and-freshness.md#source별-freshness를-각각-표시하고-primary-set과-comparisoncontext-set의-aggregate-freshness를-분리해야-한다-각-set은-하나라도-stale이면-stale-stale-없이-하나라도-검증하지-못하면-unverified-모든-source가-일치할-때만-current로-표시해야-한다)
- [source fetch 실패, 누락, 파일명 충돌 또는 hash 계산 실패를 `current`로 간주하지 말고 source별 실패 원인과 다시 검증할 방법을 표시해야 한다.](source-selection-and-freshness.md#source-fetch-실패-누락-파일명-충돌-또는-hash-계산-실패를-current로-간주하지-말고-source별-실패-원인과-다시-검증할-방법을-표시해야-한다)

### HTTP same-origin으로 Review Viewer를 열고 source를 변경하지 않은 경우 role별 `cache: no-store` fetch와 Web Crypto SHA-256 비교 뒤 `current`가 표시되고, source 한 바이트를 변경하면 해당 source set이 `stale`로 표시된다.

검증하는 요구사항:

- [Review Viewer는 생성 시점에 각 source의 role, bundle·root·member path, 내부 namespace와 member·bundle SHA-256을 manifest에 기록하되 생성 시점 freshness를 열람 시점의 최신성 보장으로 표시하거나 hash·namespace를 사용자-facing identity로 사용하지 않아야 한다.](source-selection-and-freshness.md#review-viewer는-생성-시점에-각-source의-role-bundlerootmember-path-내부-namespace와-memberbundle-sha-256을-manifest에-기록하되-생성-시점-freshness를-열람-시점의-최신성-보장으로-표시하거나-hashnamespace를-사용자-facing-identity로-사용하지-않아야-한다)
- [Review Viewer를 HTTP 또는 HTTPS의 same-origin에서 열면 repository 내부의 각 source를 `cache: no-store`로 읽고 Web Crypto API로 SHA-256을 다시 계산해 manifest의 hash와 자동 비교해야 한다.](source-selection-and-freshness.md#review-viewer를-http-또는-https의-same-origin에서-열면-repository-내부의-각-source를-cache-no-store로-읽고-web-crypto-api로-sha-256을-다시-계산해-manifest의-hash와-자동-비교해야-한다)

### `file://`에서 자동 source 접근이 실패하면 `unverified`와 파일 선택 동작이 표시되고, bundle path와 semantic filename에 맞는 여러 member를 선택하면 로컬 브라우저 안에서만 member·bundle hash가 계산되어 상태가 갱신되며 네트워크 전송이 발생하지 않는다.

검증하는 요구사항:

- [`file://` 또는 브라우저 보안 정책으로 source 자동 읽기가 실패하면 Review Viewer는 `unverified`를 표시하고 bundle path와 서로 다른 semantic member filename으로 로컬 Markdown source set을 선택·matching할 수 있어야 한다.](source-selection-and-freshness.md#file-또는-브라우저-보안-정책으로-source-자동-읽기가-실패하면-review-viewer는-unverified를-표시하고-bundle-path와-서로-다른-semantic-member-filename으로-로컬-markdown-source-set을-선택matching할-수-있어야-한다)
- [수동 freshness 검증을 위해 선택한 파일 내용은 브라우저 밖으로 업로드하거나 전송하지 않아야 한다.](source-selection-and-freshness.md#수동-freshness-검증을-위해-선택한-파일-내용은-브라우저-밖으로-업로드하거나-전송하지-않아야-한다)

### primary plan set과 Related Specs context를 가진 Review Viewer에서 primary와 context aggregate 상태가 분리되고, 각 set 안에서 모두 일치하면 `current`, 하나가 다르면 `stale`, stale 없이 하나가 누락되면 `unverified`가 표시되며 각 source 행에 개별 상태와 실패 원인이 나타난다.

검증하는 요구사항:

- [source별 freshness를 각각 표시하고 primary set과 comparison·context set의 aggregate freshness를 분리해야 한다. 각 set은 하나라도 `stale`이면 `stale`, stale 없이 하나라도 검증하지 못하면 `unverified`, 모든 source가 일치할 때만 `current`로 표시해야 한다.](source-selection-and-freshness.md#source별-freshness를-각각-표시하고-primary-set과-comparisoncontext-set의-aggregate-freshness를-분리해야-한다-각-set은-하나라도-stale이면-stale-stale-없이-하나라도-검증하지-못하면-unverified-모든-source가-일치할-때만-current로-표시해야-한다)
- [source fetch 실패, 누락, 파일명 충돌 또는 hash 계산 실패를 `current`로 간주하지 말고 source별 실패 원인과 다시 검증할 방법을 표시해야 한다.](source-selection-and-freshness.md#source-fetch-실패-누락-파일명-충돌-또는-hash-계산-실패를-current로-간주하지-말고-source별-실패-원인과-다시-검증할-방법을-표시해야-한다)

### `--check`를 현재 로컬 Review Viewer에 실행하면 exit code 0을 반환하고, source 변경·누락·manifest 오류 fixture에서는 non-zero를 반환하지만 Review Viewer를 자동 재생성하지 않는다.

검증하는 요구사항:

- [command-line freshness check는 로컬 Review Viewer manifest의 source hash와 현재 Markdown source를 비교해 모두 일치하면 성공하고, stale·누락·manifest 오류가 있으면 실패해야 한다. 이 checker는 사용자가 요청한 Review Viewer를 자동 갱신하는 trigger로 사용하지 않아야 한다.](source-selection-and-freshness.md#command-line-freshness-check는-로컬-review-viewer-manifest의-source-hash와-현재-markdown-source를-비교해-모두-일치하면-성공하고-stale누락manifest-오류가-있으면-실패해야-한다-이-checker는-사용자가-요청한-review-viewer를-자동-갱신하는-trigger로-사용하지-않아야-한다)

### 여러 block이 같은 bundle member를 인용하는 fixture에서 각 panel의 provenance 표시 횟수가 source group당 1회로 줄고, source role이 바뀌는 지점에서 다시 나타나며, primary·comparison·context 구분과 statement deep link 대상이 축약 전과 동일하다. Manifest와 History panel에는 모든 source의 role·bundle·member path·hash가 그대로 남고 일반 panel의 주 label은 H1·path·full statement다.

검증하는 요구사항:

- [Review Viewer의 각 content component 제목은 스캔 가능한 짧은 명사형 label을 사용하고, 사용자가 그 component에서 답을 찾을 질문은 제목 바로 아래의 종속 orientation 문장으로 표시해야 한다. 같은 component도 Presentation Plan의 intent에 맞는 orientation을 사용해야 한다.](adaptive-presentation-and-navigation.md#review-viewer의-각-content-component-제목은-스캔-가능한-짧은-명사형-label을-사용하고-사용자가-그-component에서-답을-찾을-질문은-제목-바로-아래의-종속-orientation-문장으로-표시해야-한다-같은-component도-presentation-plan의-intent에-맞는-orientation을-사용해야-한다)
- [같은 source의 provenance는 한 panel의 연속 block 묶음에서 첫 block에 한 번만 표시하고 source가 바뀔 때 다시 표시해야 하며, source role과 bundle·member namespace 구분 및 manifest의 전체 provenance는 보존해야 한다.](source-selection-and-freshness.md#같은-source의-provenance는-한-panel의-연속-block-묶음에서-첫-block에-한-번만-표시하고-source가-바뀔-때-다시-표시해야-하며-source-role과-bundlemember-namespace-구분-및-manifest의-전체-provenance는-보존해야-한다)

### 자유로운 section 순서와 여러 member를 가진 workflow·API·architecture bundle과 plan fixture를 parse하면 root·member metadata, outline, 모든 prose·table·code·Mermaid block과 full-statement entity가 bundle·member-qualified anchor를 갖고 Semantic IR에 정확히 한 번 존재하며 content coverage가 100%다.

검증하는 요구사항:

- [Semantic IR은 bundle·member metadata, source별 outline, 원문 순서의 prose·table·code·Mermaid block, full-statement Requirement·Acceptance Criterion, Task·Step·decision·interface entity, explicit relation과 provenance를 표현해야 한다.](source-selection-and-freshness.md#semantic-ir은-bundlemember-metadata-source별-outline-원문-순서의-prosetablecodemermaid-block-full-statement-requirementacceptance-criterion-taskstepdecisioninterface-entity-explicit-relation과-provenance를-표현해야-한다)
- [Parser는 selected bundle의 모든 member block을 Semantic IR에 정확히 한 번 보존하고 각 entity와 relation을 bundle path·member path·internal namespace·line anchor에 연결해야 하며, 인식하지 못한 Markdown도 generic block으로 보존해야 한다.](source-selection-and-freshness.md#parser는-selected-bundle의-모든-member-block을-semantic-ir에-정확히-한-번-보존하고-각-entity와-relation을-bundle-pathmember-pathinternal-namespaceline-anchor에-연결해야-하며-인식하지-못한-markdown도-generic-block으로-보존해야-한다)
- [Profile이 source block이나 entity를 사용하지 않으면 renderer는 이를 source detail 또는 generic detail component에 포함해야 하며, Presentation Plan은 selected source content coverage 100%를 만족해야 한다.](adaptive-presentation-and-navigation.md#profile이-source-block이나-entity를-사용하지-않으면-renderer는-이를-source-detail-또는-generic-detail-component에-포함해야-하며-presentation-plan은-selected-source-content-coverage-100를-만족해야-한다)
