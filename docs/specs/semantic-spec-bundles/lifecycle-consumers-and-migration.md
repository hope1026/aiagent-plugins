# Lifecycle Consumer와 Migration

## Requirements

### `writing-plans`, `executing-plans`, `verifying-work`와 다른 Forge lifecycle skill은 단일 `spec.md`, `id` 또는 literal `Status:` 검색 대신 공통 bundle parser가 반환한 root metadata, member 목록, statement와 status를 사용해야 한다.

### `writing-specs`, `writing-plans`, `executing-plans`, `verifying-work`와 다른 Forge lifecycle skill은 일반적인 작성·변경·승인·handoff·checkpoint·status 전환에서 Markdown source만 생성하거나 변경해야 한다.

### spec 또는 plan source 변경, lifecycle status 변경, 문서 복잡도, Mermaid·표 존재, approval 요청, handoff와 기존 HTML 존재를 HTML 생성 또는 갱신 권한으로 해석하지 않아야 한다.

### HTML은 사용자가 현재 source set에 대해 `review-viewer` skill 사용, 시각화, Viewer 생성 또는 Viewer 갱신 의도를 명시한 경우에만 생성할 수 있어야 한다.

### Forge는 source 옆 `index.html`·`view.html`, repository-wide spec catalog HTML과 plan별 상시 HTML을 생성하거나 Git 추적 산출물로 요구하지 않아야 한다.

### spec과 plan의 일반 탐색·검토 경로는 bundle root의 `Documents`, repository의 Markdown member와 link여야 하며 HTML catalog의 존재 또는 freshness가 lifecycle gate가 되지 않아야 한다.

### 명시적으로 생성된 Review Viewer는 읽기 전용 파생 artifact이고 Markdown source를 직접 수정하거나 별도 의미 정본이 되지 않아야 한다.

### source 변경은 기존 Review Viewer를 자동 갱신하지 않아야 하며, stale 사실은 보고할 수 있지만 재생성에는 별도의 명시적 사용자 요청이 필요해야 한다.

### 요청형 Review Viewer의 경로, Git 정책, bundle source manifest, freshness와 adaptive rendering은 `docs/specs/review-viewer-lifecycle/` bundle이 단독으로 소유해야 한다.

### 한국어 source를 요청형 Review Viewer로 생성하면 UI 설명은 한국어를 사용하고 API, protocol, service, schema와 code identifier는 원문을 유지해야 한다.

### Markdown source 작성이나 validation은 Review Viewer 생성 요청으로 간주하지 않아야 한다.

### Review Viewer는 사용자가 현재 spec 또는 plan source set의 Viewer 생성·갱신을 명시적으로 요청한 경우에만 별도 lifecycle viewer 계약에 따라 생성해야 한다.

### source 변경은 기존 Review Viewer를 자동 갱신하지 않으며 Markdown과 Review Viewer freshness를 하나의 lifecycle 상태로 합치지 않아야 한다.

### Forge repository의 활성 spec, lifecycle skill, validator, fixture와 plan consumer는 한 breaking migration release에서 `forge/spec@3`, Spec Bundle과 path·statement link contract로 전환되어야 하며 cutover 뒤 v2 reader·writer, legacy body status gate와 자동 Spec Pages build 경로를 허용하지 않아야 한다.

### 기존 프로젝트 migration은 repository별 승인된 일회성 plan으로 모든 v2 source를 isolated candidate의 bundle로 변환하고 link, plan trace, instruction과 fixture를 atomic하게 전환해야 한다. 임시 converter는 cutover 완료 전에 제거하고 production workflow에 v2 compatibility branch를 남기지 않아야 한다.

### Migration은 source path·SHA-256, 새 bundle·member path, exact statement 대응, schema·status resolution, link rewrite와 rollback point를 기록해야 하며 broken link, duplicate statement, missing coverage 또는 transition 실패가 있으면 기존 구조를 제거하지 않아야 한다.

### 이 Forge 변경의 구현·완료 범위는 `weppy-roblox-mcp-private`를 수정하지 않아야 한다. 해당 repository의 기존 spec migration은 Forge tooling 구현과 검증 뒤 그 repository가 소유하는 별도 governing spec과 일회성 cutover plan에서 수행해야 한다.

### Marketplace 사용자 workflow이므로 bundle parser와 validator, Review Viewer parser·renderer·component asset은 Forge plugin 배포에 포함되고 Claude Code, Codex, Antigravity에서 동일한 Spec Bundle source와 explicit Viewer request contract를 사용해야 한다.

### 활성 Spec Bundle은 현재 유효한 제품·시스템 동작과 제약을 source of truth로 제공해야 한다. 완료된 일회성 작업의 실행 과정, 변환 수치와 rollback evidence는 plan, ADR 또는 별도 evidence 문서에 보존하고 활성 statement와 설명에 현재 동작처럼 남기지 않아야 한다.

### baseline의 `approved` 또는 `implemented` source를 새 bundle path로 교체할 때는 `docs/specs/.bundle-transitions.json`에 exact baseline source path와 SHA-256을 가진 one-to-one `superseded` transition을 선언해야 한다. 선언이 없거나 baseline bytes와 일치하지 않으면 validator는 삭제·rename을 거부해야 한다. Replacement 없는 retirement, 여러 source의 merge, baseline에 이미 존재하는 target으로의 이동과 같은 diff 안의 multi-hop transition은 허용하지 않아야 한다.

### `docs/specs/.bundle-transitions.json`은 repository 안의 regular non-symlink file이고 `schema: forge/spec-bundle-transitions@1`과 `transitions`만 가져야 한다. 각 record는 `fromSourcePath`, `fromSourceSha256`, `disposition`, `toBundlePath`, `evidencePath`, `reason`만 가지며 author-facing ID를 포함하지 않아야 한다. Path는 normalized repository-relative POSIX path이고 symlink와 escape를 허용하지 않아야 한다. `fromSourcePath`는 historical v2 migration에서 file, v3 이후에는 bundle directory일 수 있고 `toBundlePath`는 항상 현재 v3 bundle directory여야 한다.

### validator는 baseline source bytes나 bundle hash가 transition record와 정확히 일치하고 current target bundle의 path와 status가 유효한지 확인해야 한다. Current transition 배열은 baseline sequence를 exact prefix로 보존해야 하며 record replay, duplicate source·target, same-diff chain, missing evidence와 old path reference를 실패로 처리해야 한다. 유효한 transition도 replacement bundle validation을 면제하지 않아야 한다.

### current-state replacement는 승인 뒤 isolated candidate에서 path transition append, old source 제거, reference 갱신과 replacement bundle validation을 한 commit으로 수행해야 한다. Candidate gate가 실패하면 production root fingerprint를 유지하고 Review Viewer는 별도 명시 요청이 없으면 생성하지 않아야 한다.

## Acceptance Criteria

### spec 작성·승인·implemented 전환과 plan 작성·checkpoint fixture를 실행하면 변경된 tracked artifact는 Markdown뿐이고 HTML 생성 count는 0이다. 이어 사용자가 `review-viewer`를 명시적으로 요청하면 `.forge/reviews/<review-id>/view.html` 한 개만 비추적 상태로 생성된다.

검증하는 요구사항:

- [`writing-specs`, `writing-plans`, `executing-plans`, `verifying-work`와 다른 Forge lifecycle skill은 일반적인 작성·변경·승인·handoff·checkpoint·status 전환에서 Markdown source만 생성하거나 변경해야 한다.](lifecycle-consumers-and-migration.md#writing-specs-writing-plans-executing-plans-verifying-work와-다른-forge-lifecycle-skill은-일반적인-작성변경승인handoffcheckpointstatus-전환에서-markdown-source만-생성하거나-변경해야-한다)
- [spec 또는 plan source 변경, lifecycle status 변경, 문서 복잡도, Mermaid·표 존재, approval 요청, handoff와 기존 HTML 존재를 HTML 생성 또는 갱신 권한으로 해석하지 않아야 한다.](lifecycle-consumers-and-migration.md#spec-또는-plan-source-변경-lifecycle-status-변경-문서-복잡도-mermaid표-존재-approval-요청-handoff와-기존-html-존재를-html-생성-또는-갱신-권한으로-해석하지-않아야-한다)
- [HTML은 사용자가 현재 source set에 대해 `review-viewer` skill 사용, 시각화, Viewer 생성 또는 Viewer 갱신 의도를 명시한 경우에만 생성할 수 있어야 한다.](lifecycle-consumers-and-migration.md#html은-사용자가-현재-source-set에-대해-review-viewer-skill-사용-시각화-viewer-생성-또는-viewer-갱신-의도를-명시한-경우에만-생성할-수-있어야-한다)
- [Forge는 source 옆 `index.html`·`view.html`, repository-wide spec catalog HTML과 plan별 상시 HTML을 생성하거나 Git 추적 산출물로 요구하지 않아야 한다.](lifecycle-consumers-and-migration.md#forge는-source-옆-indexhtmlviewhtml-repository-wide-spec-catalog-html과-plan별-상시-html을-생성하거나-git-추적-산출물로-요구하지-않아야-한다)
- [spec과 plan의 일반 탐색·검토 경로는 bundle root의 `Documents`, repository의 Markdown member와 link여야 하며 HTML catalog의 존재 또는 freshness가 lifecycle gate가 되지 않아야 한다.](lifecycle-consumers-and-migration.md#spec과-plan의-일반-탐색검토-경로는-bundle-root의-documents-repository의-markdown-member와-link여야-하며-html-catalog의-존재-또는-freshness가-lifecycle-gate가-되지-않아야-한다)
- [명시적으로 생성된 Review Viewer는 읽기 전용 파생 artifact이고 Markdown source를 직접 수정하거나 별도 의미 정본이 되지 않아야 한다.](lifecycle-consumers-and-migration.md#명시적으로-생성된-review-viewer는-읽기-전용-파생-artifact이고-markdown-source를-직접-수정하거나-별도-의미-정본이-되지-않아야-한다)
- [source 변경은 기존 Review Viewer를 자동 갱신하지 않아야 하며, stale 사실은 보고할 수 있지만 재생성에는 별도의 명시적 사용자 요청이 필요해야 한다.](lifecycle-consumers-and-migration.md#source-변경은-기존-review-viewer를-자동-갱신하지-않아야-하며-stale-사실은-보고할-수-있지만-재생성에는-별도의-명시적-사용자-요청이-필요해야-한다)
- [요청형 Review Viewer의 경로, Git 정책, bundle source manifest, freshness와 adaptive rendering은 `docs/specs/review-viewer-lifecycle/` bundle이 단독으로 소유해야 한다.](lifecycle-consumers-and-migration.md#요청형-review-viewer의-경로-git-정책-bundle-source-manifest-freshness와-adaptive-rendering은-docsspecsreview-viewer-lifecycle-bundle이-단독으로-소유해야-한다)
- [한국어 source를 요청형 Review Viewer로 생성하면 UI 설명은 한국어를 사용하고 API, protocol, service, schema와 code identifier는 원문을 유지해야 한다.](lifecycle-consumers-and-migration.md#한국어-source를-요청형-review-viewer로-생성하면-ui-설명은-한국어를-사용하고-api-protocol-service-schema와-code-identifier는-원문을-유지해야-한다)

### 복잡한 source, Mermaid·표 포함 source, approval, handoff, stale Viewer와 기존 source-adjacent HTML fixture가 있어도 명시 요청 전에는 HTML을 생성·갱신하지 않고 lifecycle gate는 Markdown validation만으로 판정된다.

검증하는 요구사항:

- [spec 또는 plan source 변경, lifecycle status 변경, 문서 복잡도, Mermaid·표 존재, approval 요청, handoff와 기존 HTML 존재를 HTML 생성 또는 갱신 권한으로 해석하지 않아야 한다.](lifecycle-consumers-and-migration.md#spec-또는-plan-source-변경-lifecycle-status-변경-문서-복잡도-mermaid표-존재-approval-요청-handoff와-기존-html-존재를-html-생성-또는-갱신-권한으로-해석하지-않아야-한다)
- [HTML은 사용자가 현재 source set에 대해 `review-viewer` skill 사용, 시각화, Viewer 생성 또는 Viewer 갱신 의도를 명시한 경우에만 생성할 수 있어야 한다.](lifecycle-consumers-and-migration.md#html은-사용자가-현재-source-set에-대해-review-viewer-skill-사용-시각화-viewer-생성-또는-viewer-갱신-의도를-명시한-경우에만-생성할-수-있어야-한다)
- [Forge는 source 옆 `index.html`·`view.html`, repository-wide spec catalog HTML과 plan별 상시 HTML을 생성하거나 Git 추적 산출물로 요구하지 않아야 한다.](lifecycle-consumers-and-migration.md#forge는-source-옆-indexhtmlviewhtml-repository-wide-spec-catalog-html과-plan별-상시-html을-생성하거나-git-추적-산출물로-요구하지-않아야-한다)
- [spec과 plan의 일반 탐색·검토 경로는 bundle root의 `Documents`, repository의 Markdown member와 link여야 하며 HTML catalog의 존재 또는 freshness가 lifecycle gate가 되지 않아야 한다.](lifecycle-consumers-and-migration.md#spec과-plan의-일반-탐색검토-경로는-bundle-root의-documents-repository의-markdown-member와-link여야-하며-html-catalog의-존재-또는-freshness가-lifecycle-gate가-되지-않아야-한다)
- [명시적으로 생성된 Review Viewer는 읽기 전용 파생 artifact이고 Markdown source를 직접 수정하거나 별도 의미 정본이 되지 않아야 한다.](lifecycle-consumers-and-migration.md#명시적으로-생성된-review-viewer는-읽기-전용-파생-artifact이고-markdown-source를-직접-수정하거나-별도-의미-정본이-되지-않아야-한다)
- [source 변경은 기존 Review Viewer를 자동 갱신하지 않아야 하며, stale 사실은 보고할 수 있지만 재생성에는 별도의 명시적 사용자 요청이 필요해야 한다.](lifecycle-consumers-and-migration.md#source-변경은-기존-review-viewer를-자동-갱신하지-않아야-하며-stale-사실은-보고할-수-있지만-재생성에는-별도의-명시적-사용자-요청이-필요해야-한다)
- [요청형 Review Viewer의 경로, Git 정책, bundle source manifest, freshness와 adaptive rendering은 `docs/specs/review-viewer-lifecycle/` bundle이 단독으로 소유해야 한다.](lifecycle-consumers-and-migration.md#요청형-review-viewer의-경로-git-정책-bundle-source-manifest-freshness와-adaptive-rendering은-docsspecsreview-viewer-lifecycle-bundle이-단독으로-소유해야-한다)

### 한국어 source의 요청형 Review Viewer는 한국어 UI 설명과 원문의 API·schema identifier를 함께 표시한다.

검증하는 요구사항:

- [한국어 source를 요청형 Review Viewer로 생성하면 UI 설명은 한국어를 사용하고 API, protocol, service, schema와 code identifier는 원문을 유지해야 한다.](lifecycle-consumers-and-migration.md#한국어-source를-요청형-review-viewer로-생성하면-ui-설명은-한국어를-사용하고-api-protocol-service-schema와-code-identifier는-원문을-유지해야-한다)

### 여러 Spec Bundle과 plan을 탐색하는 기본 workflow가 root `Documents`, member path와 relation link만 사용하고 HTML catalog의 누락을 오류로 처리하지 않는다.

검증하는 요구사항:

- [spec과 plan의 일반 탐색·검토 경로는 bundle root의 `Documents`, repository의 Markdown member와 link여야 하며 HTML catalog의 존재 또는 freshness가 lifecycle gate가 되지 않아야 한다.](lifecycle-consumers-and-migration.md#spec과-plan의-일반-탐색검토-경로는-bundle-root의-documents-repository의-markdown-member와-link여야-하며-html-catalog의-존재-또는-freshness가-lifecycle-gate가-되지-않아야-한다)

### 명시적으로 생성한 Review Viewer는 bundle source를 편집하지 않고 manifest·freshness·adaptive rendering 계약을 `docs/specs/review-viewer-lifecycle/`에 위임하며 Git 비추적 상태를 유지한다.

검증하는 요구사항:

- [명시적으로 생성된 Review Viewer는 읽기 전용 파생 artifact이고 Markdown source를 직접 수정하거나 별도 의미 정본이 되지 않아야 한다.](lifecycle-consumers-and-migration.md#명시적으로-생성된-review-viewer는-읽기-전용-파생-artifact이고-markdown-source를-직접-수정하거나-별도-의미-정본이-되지-않아야-한다)
- [source 변경은 기존 Review Viewer를 자동 갱신하지 않아야 하며, stale 사실은 보고할 수 있지만 재생성에는 별도의 명시적 사용자 요청이 필요해야 한다.](lifecycle-consumers-and-migration.md#source-변경은-기존-review-viewer를-자동-갱신하지-않아야-하며-stale-사실은-보고할-수-있지만-재생성에는-별도의-명시적-사용자-요청이-필요해야-한다)
- [요청형 Review Viewer의 경로, Git 정책, bundle source manifest, freshness와 adaptive rendering은 `docs/specs/review-viewer-lifecycle/` bundle이 단독으로 소유해야 한다.](lifecycle-consumers-and-migration.md#요청형-review-viewer의-경로-git-정책-bundle-source-manifest-freshness와-adaptive-rendering은-docsspecsreview-viewer-lifecycle-bundle이-단독으로-소유해야-한다)
- [한국어 source를 요청형 Review Viewer로 생성하면 UI 설명은 한국어를 사용하고 API, protocol, service, schema와 code identifier는 원문을 유지해야 한다.](lifecycle-consumers-and-migration.md#한국어-source를-요청형-review-viewer로-생성하면-ui-설명은-한국어를-사용하고-api-protocol-service-schema와-code-identifier는-원문을-유지해야-한다)

### spec 또는 plan source를 변경·validate해도 Review Viewer가 생성·갱신되지 않고, 사용자가 현재 source set의 Viewer를 명시적으로 요청한 뒤에만 생성된다.

검증하는 요구사항:

- [Markdown source 작성이나 validation은 Review Viewer 생성 요청으로 간주하지 않아야 한다.](lifecycle-consumers-and-migration.md#markdown-source-작성이나-validation은-review-viewer-생성-요청으로-간주하지-않아야-한다)
- [Review Viewer는 사용자가 현재 spec 또는 plan source set의 Viewer 생성·갱신을 명시적으로 요청한 경우에만 별도 lifecycle viewer 계약에 따라 생성해야 한다.](lifecycle-consumers-and-migration.md#review-viewer는-사용자가-현재-spec-또는-plan-source-set의-viewer-생성갱신을-명시적으로-요청한-경우에만-별도-lifecycle-viewer-계약에-따라-생성해야-한다)
- [source 변경은 기존 Review Viewer를 자동 갱신하지 않으며 Markdown과 Review Viewer freshness를 하나의 lifecycle 상태로 합치지 않아야 한다.](lifecycle-consumers-and-migration.md#source-변경은-기존-review-viewer를-자동-갱신하지-않으며-markdown과-review-viewer-freshness를-하나의-lifecycle-상태로-합치지-않아야-한다)

### Forge migration candidate에서 활성 spec과 lifecycle consumer가 `forge/spec@3`, bundle path와 statement link contract를 사용하고 v2 reader·writer, 자동 Spec Pages build·check 경로와 tracked generated HTML이 0개다.

검증하는 요구사항:

- [Forge repository의 활성 spec, lifecycle skill, validator, fixture와 plan consumer는 한 breaking migration release에서 `forge/spec@3`, Spec Bundle과 path·statement link contract로 전환되어야 하며 cutover 뒤 v2 reader·writer, legacy body status gate와 자동 Spec Pages build 경로를 허용하지 않아야 한다.](lifecycle-consumers-and-migration.md#forge-repository의-활성-spec-lifecycle-skill-validator-fixture와-plan-consumer는-한-breaking-migration-release에서-forgespec3-spec-bundle과-pathstatement-link-contract로-전환되어야-하며-cutover-뒤-v2-readerwriter-legacy-body-status-gate와-자동-spec-pages-build-경로를-허용하지-않아야-한다)

### Migration fixture가 source path·SHA-256, 새 bundle·member path, exact statement mapping, schema·status resolution, link rewrite와 rollback point를 기록하고 validation 실패 시 기존 구조를 유지하며 성공할 때만 한 cutover로 전환하고 `weppy-roblox-mcp-private`를 변경하지 않는다.

검증하는 요구사항:

- [기존 프로젝트 migration은 repository별 승인된 일회성 plan으로 모든 v2 source를 isolated candidate의 bundle로 변환하고 link, plan trace, instruction과 fixture를 atomic하게 전환해야 한다. 임시 converter는 cutover 완료 전에 제거하고 production workflow에 v2 compatibility branch를 남기지 않아야 한다.](lifecycle-consumers-and-migration.md#기존-프로젝트-migration은-repository별-승인된-일회성-plan으로-모든-v2-source를-isolated-candidate의-bundle로-변환하고-link-plan-trace-instruction과-fixture를-atomic하게-전환해야-한다-임시-converter는-cutover-완료-전에-제거하고-production-workflow에-v2-compatibility-branch를-남기지-않아야-한다)
- [Migration은 source path·SHA-256, 새 bundle·member path, exact statement 대응, schema·status resolution, link rewrite와 rollback point를 기록해야 하며 broken link, duplicate statement, missing coverage 또는 transition 실패가 있으면 기존 구조를 제거하지 않아야 한다.](lifecycle-consumers-and-migration.md#migration은-source-pathsha-256-새-bundlemember-path-exact-statement-대응-schemastatus-resolution-link-rewrite와-rollback-point를-기록해야-하며-broken-link-duplicate-statement-missing-coverage-또는-transition-실패가-있으면-기존-구조를-제거하지-않아야-한다)
- [이 Forge 변경의 구현·완료 범위는 `weppy-roblox-mcp-private`를 수정하지 않아야 한다. 해당 repository의 기존 spec migration은 Forge tooling 구현과 검증 뒤 그 repository가 소유하는 별도 governing spec과 일회성 cutover plan에서 수행해야 한다.](lifecycle-consumers-and-migration.md#이-forge-변경의-구현완료-범위는-weppy-roblox-mcp-private를-수정하지-않아야-한다-해당-repository의-기존-spec-migration은-forge-tooling-구현과-검증-뒤-그-repository가-소유하는-별도-governing-spec과-일회성-cutover-plan에서-수행해야-한다)

### plugin 설치와 repository validator를 Claude Code·Codex·Antigravity 지원 경로에서 검사하면 bundle parser·validator와 요청형 Review Viewer parser·renderer·asset이 발견되고 동일 multi-file fixture 결과를 내며 v2 reader와 자동 Spec Pages builder는 설치되지 않는다.

검증하는 요구사항:

- [Marketplace 사용자 workflow이므로 bundle parser와 validator, Review Viewer parser·renderer·component asset은 Forge plugin 배포에 포함되고 Claude Code, Codex, Antigravity에서 동일한 Spec Bundle source와 explicit Viewer request contract를 사용해야 한다.](lifecycle-consumers-and-migration.md#marketplace-사용자-workflow이므로-bundle-parser와-validator-review-viewer-parserrenderercomponent-asset은-forge-plugin-배포에-포함되고-claude-code-codex-antigravity에서-동일한-spec-bundle-source와-explicit-viewer-request-contract를-사용해야-한다)

### baseline source를 새 approved bundle로 교체하는 fixture에서 exact `fromSourcePath`·SHA-256, `toBundlePath`와 evidence를 가진 append-only path transition을 함께 적용하면 repository validation이 통과한다. Invalid JSON, duplicate·unknown key, wrong type, uppercase·short hash, empty string, manifest-file symlink, absolute·drive·UNC·backslash·dot-segment·record-path symlink, 잘못된 schema·disposition·target·evidence를 각각 주입하면 정렬된 deterministic 진단과 non-zero exit가 발생한다.

검증하는 요구사항:

- [사용자 언어, EARS 의미 규칙과 Acceptance Criterion의 선행조건·행동·관찰 결과는 유지해야 한다. 같은 bundle path로 활성 상태인 `approved` 또는 `implemented` spec의 Decisions & History는 append-only이며 제거된 계약은 active statement가 아니라 history에 기록해야 한다. 명시적으로 교체되는 bundle은 검증된 path transition 기록을 따라야 한다.](authoring-and-file-organization.md#사용자-언어-ears-의미-규칙과-acceptance-criterion의-선행조건행동관찰-결과는-유지해야-한다-같은-bundle-path로-활성-상태인-approved-또는-implemented-spec의-decisions-history는-append-only이며-제거된-계약은-active-statement가-아니라-history에-기록해야-한다-명시적으로-교체되는-bundle은-검증된-path-transition-기록을-따라야-한다)
- [활성 Spec Bundle은 현재 유효한 제품·시스템 동작과 제약을 source of truth로 제공해야 한다. 완료된 일회성 작업의 실행 과정, 변환 수치와 rollback evidence는 plan, ADR 또는 별도 evidence 문서에 보존하고 활성 statement와 설명에 현재 동작처럼 남기지 않아야 한다.](lifecycle-consumers-and-migration.md#활성-spec-bundle은-현재-유효한-제품시스템-동작과-제약을-source-of-truth로-제공해야-한다-완료된-일회성-작업의-실행-과정-변환-수치와-rollback-evidence는-plan-adr-또는-별도-evidence-문서에-보존하고-활성-statement와-설명에-현재-동작처럼-남기지-않아야-한다)
- [baseline의 `approved` 또는 `implemented` source를 새 bundle path로 교체할 때는 `docs/specs/.bundle-transitions.json`에 exact baseline source path와 SHA-256을 가진 one-to-one `superseded` transition을 선언해야 한다. 선언이 없거나 baseline bytes와 일치하지 않으면 validator는 삭제·rename을 거부해야 한다. Replacement 없는 retirement, 여러 source의 merge, baseline에 이미 존재하는 target으로의 이동과 같은 diff 안의 multi-hop transition은 허용하지 않아야 한다.](lifecycle-consumers-and-migration.md#baseline의-approved-또는-implemented-source를-새-bundle-path로-교체할-때는-docsspecsbundle-transitionsjson에-exact-baseline-source-path와-sha-256을-가진-one-to-one-superseded-transition을-선언해야-한다-선언이-없거나-baseline-bytes와-일치하지-않으면-validator는-삭제rename을-거부해야-한다-replacement-없는-retirement-여러-source의-merge-baseline에-이미-존재하는-target으로의-이동과-같은-diff-안의-multi-hop-transition은-허용하지-않아야-한다)
- [`docs/specs/.bundle-transitions.json`은 repository 안의 regular non-symlink file이고 `schema: forge/spec-bundle-transitions@1`과 `transitions`만 가져야 한다. 각 record는 `fromSourcePath`, `fromSourceSha256`, `disposition`, `toBundlePath`, `evidencePath`, `reason`만 가지며 author-facing ID를 포함하지 않아야 한다. Path는 normalized repository-relative POSIX path이고 symlink와 escape를 허용하지 않아야 한다. `fromSourcePath`는 historical v2 migration에서 file, v3 이후에는 bundle directory일 수 있고 `toBundlePath`는 항상 현재 v3 bundle directory여야 한다.](lifecycle-consumers-and-migration.md#docsspecsbundle-transitionsjson은-repository-안의-regular-non-symlink-file이고-schema-forgespec-bundle-transitions1과-transitions만-가져야-한다-각-record는-fromsourcepath-fromsourcesha256-disposition-tobundlepath-evidencepath-reason만-가지며-author-facing-id를-포함하지-않아야-한다-path는-normalized-repository-relative-posix-path이고-symlink와-escape를-허용하지-않아야-한다-fromsourcepath는-historical-v2-migration에서-file-v3-이후에는-bundle-directory일-수-있고-tobundlepath는-항상-현재-v3-bundle-directory여야-한다)

### transition binding·replay·duplicate·chain·missing evidence·old path reference fixture는 validation에 실패하고, 유효한 replacement bundle과 reference만 남긴 candidate는 HTML build 없이 통과한다.

검증하는 요구사항:

- [validator는 baseline source bytes나 bundle hash가 transition record와 정확히 일치하고 current target bundle의 path와 status가 유효한지 확인해야 한다. Current transition 배열은 baseline sequence를 exact prefix로 보존해야 하며 record replay, duplicate source·target, same-diff chain, missing evidence와 old path reference를 실패로 처리해야 한다. 유효한 transition도 replacement bundle validation을 면제하지 않아야 한다.](lifecycle-consumers-and-migration.md#validator는-baseline-source-bytes나-bundle-hash가-transition-record와-정확히-일치하고-current-target-bundle의-path와-status가-유효한지-확인해야-한다-current-transition-배열은-baseline-sequence를-exact-prefix로-보존해야-하며-record-replay-duplicate-sourcetarget-same-diff-chain-missing-evidence와-old-path-reference를-실패로-처리해야-한다-유효한-transition도-replacement-bundle-validation을-면제하지-않아야-한다)

### current-state replacement 승인 전에는 production source를 변경하지 않고, 승인 뒤 isolated candidate의 bundle validation 실패는 production fingerprint를 보존한다. 성공한 candidate에는 현재 bundle 계약과 evidence만 남고 Review Viewer 생성 count는 0이다.

검증하는 요구사항:

- [활성 Spec Bundle은 현재 유효한 제품·시스템 동작과 제약을 source of truth로 제공해야 한다. 완료된 일회성 작업의 실행 과정, 변환 수치와 rollback evidence는 plan, ADR 또는 별도 evidence 문서에 보존하고 활성 statement와 설명에 현재 동작처럼 남기지 않아야 한다.](lifecycle-consumers-and-migration.md#활성-spec-bundle은-현재-유효한-제품시스템-동작과-제약을-source-of-truth로-제공해야-한다-완료된-일회성-작업의-실행-과정-변환-수치와-rollback-evidence는-plan-adr-또는-별도-evidence-문서에-보존하고-활성-statement와-설명에-현재-동작처럼-남기지-않아야-한다)
- [current-state replacement는 승인 뒤 isolated candidate에서 path transition append, old source 제거, reference 갱신과 replacement bundle validation을 한 commit으로 수행해야 한다. Candidate gate가 실패하면 production root fingerprint를 유지하고 Review Viewer는 별도 명시 요청이 없으면 생성하지 않아야 한다.](lifecycle-consumers-and-migration.md#current-state-replacement는-승인-뒤-isolated-candidate에서-path-transition-append-old-source-제거-reference-갱신과-replacement-bundle-validation을-한-commit으로-수행해야-한다-candidate-gate가-실패하면-production-root-fingerprint를-유지하고-review-viewer는-별도-명시-요청이-없으면-생성하지-않아야-한다)
