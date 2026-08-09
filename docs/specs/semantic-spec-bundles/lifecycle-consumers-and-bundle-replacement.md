# Lifecycle Consumer와 Bundle 교체

## Requirements

### `writing-plans`, `executing-plans`, `verifying-work`와 다른 Forge lifecycle skill은 공통 bundle parser가 반환한 root metadata, member 목록, statement와 status를 사용해야 한다.

### Forge lifecycle skill은 일반적인 작성·변경·승인·handoff·checkpoint·status 전환에서 Markdown source만 생성하거나 변경해야 한다.

### Source 변경, lifecycle status, 문서 복잡도, Mermaid·표, approval 요청, handoff와 기존 HTML 존재를 Review Viewer 생성 또는 갱신 권한으로 해석하지 않아야 한다.

### Review Viewer는 사용자가 현재 source set의 시각화, 생성 또는 갱신을 명시한 경우에만 별도 viewer 계약에 따라 생성해야 한다.

### Source 변경은 저장된 Review Viewer를 자동 갱신하지 않아야 하며 stale 사실은 보고할 수 있지만 재생성에는 별도의 명시적 사용자 요청이 필요해야 한다.

### Bundle parser와 validator, Review Viewer parser·renderer·component asset은 Forge plugin 배포에 포함되고 Claude Code, Codex, Antigravity에서 같은 Spec Bundle과 explicit Viewer request 계약을 사용해야 한다.

### 활성 Spec Bundle은 현재 유효한 제품·시스템 동작과 제약만 source of truth로 제공하고 완료된 실행 과정과 일회성 수치는 plan, ADR, evidence 또는 Git 이력에만 두어야 한다.

### `approved` 또는 `implemented` baseline bundle을 새 semantic path로 교체할 때는 `docs/specs/.bundle-transitions.json`에 exact baseline bundle path와 bundle hash를 가진 one-to-one `superseded` transition을 선언해야 한다.

### Bundle transition record는 `fromSourcePath`, `fromSourceSha256`, `disposition`, `toBundlePath`, `evidencePath`, `reason`만 사용하고 두 source path를 normalized repository-relative semantic bundle directory로 제한해야 한다.

### Validator는 transition의 baseline bundle hash, current target path·status, append-only record prefix, evidence file, unique source·target과 one-step 관계를 검증하고 replacement bundle의 일반 validation도 별도로 수행해야 한다.

## Acceptance Criteria

### Spec 작성·승인·status 전환과 plan 작성·checkpoint fixture를 실행하면 변경된 tracked artifact는 Markdown뿐이고 HTML 생성 count는 0이며, 명시적인 Viewer 요청에서만 비추적 Review Viewer가 생성된다.

검증하는 요구사항:

- [Forge lifecycle skill은 일반적인 작성·변경·승인·handoff·checkpoint·status 전환에서 Markdown source만 생성하거나 변경해야 한다.](lifecycle-consumers-and-bundle-replacement.md#forge-lifecycle-skill은-일반적인-작성변경승인handoffcheckpointstatus-전환에서-markdown-source만-생성하거나-변경해야-한다)
- [Source 변경, lifecycle status, 문서 복잡도, Mermaid·표, approval 요청, handoff와 기존 HTML 존재를 Review Viewer 생성 또는 갱신 권한으로 해석하지 않아야 한다.](lifecycle-consumers-and-bundle-replacement.md#source-변경-lifecycle-status-문서-복잡도-mermaid표-approval-요청-handoff와-기존-html-존재를-review-viewer-생성-또는-갱신-권한으로-해석하지-않아야-한다)
- [Review Viewer는 사용자가 현재 source set의 시각화, 생성 또는 갱신을 명시한 경우에만 별도 viewer 계약에 따라 생성해야 한다.](lifecycle-consumers-and-bundle-replacement.md#review-viewer는-사용자가-현재-source-set의-시각화-생성-또는-갱신을-명시한-경우에만-별도-viewer-계약에-따라-생성해야-한다)
- [Source 변경은 저장된 Review Viewer를 자동 갱신하지 않아야 하며 stale 사실은 보고할 수 있지만 재생성에는 별도의 명시적 사용자 요청이 필요해야 한다.](lifecycle-consumers-and-bundle-replacement.md#source-변경은-저장된-review-viewer를-자동-갱신하지-않아야-하며-stale-사실은-보고할-수-있지만-재생성에는-별도의-명시적-사용자-요청이-필요해야-한다)

### 세 agent용 설치 fixture에서 같은 bundle을 validate·inspect하고 Review Viewer source로 읽으면 동일한 bundle·member path와 full statement 결과가 나오며 일반 validation은 HTML을 생성하지 않는다.

검증하는 요구사항:

- [`writing-plans`, `executing-plans`, `verifying-work`와 다른 Forge lifecycle skill은 공통 bundle parser가 반환한 root metadata, member 목록, statement와 status를 사용해야 한다.](lifecycle-consumers-and-bundle-replacement.md#writing-plans-executing-plans-verifying-work와-다른-forge-lifecycle-skill은-공통-bundle-parser가-반환한-root-metadata-member-목록-statement와-status를-사용해야-한다)
- [Bundle parser와 validator, Review Viewer parser·renderer·component asset은 Forge plugin 배포에 포함되고 Claude Code, Codex, Antigravity에서 같은 Spec Bundle과 explicit Viewer request 계약을 사용해야 한다.](lifecycle-consumers-and-bundle-replacement.md#bundle-parser와-validator-review-viewer-parserrenderercomponent-asset은-forge-plugin-배포에-포함되고-claude-code-codex-antigravity에서-같은-spec-bundle과-explicit-viewer-request-계약을-사용해야-한다)

### Current source audit를 실행하면 Canonical Spec에는 현재 동작과 제약만 남고 대체된 실행 과정이나 일회성 수치는 active statement와 설명에 나타나지 않는다.

검증하는 요구사항:

- [활성 Spec Bundle은 현재 유효한 제품·시스템 동작과 제약만 source of truth로 제공하고 완료된 실행 과정과 일회성 수치는 plan, ADR, evidence 또는 Git 이력에만 두어야 한다.](lifecycle-consumers-and-bundle-replacement.md#활성-spec-bundle은-현재-유효한-제품시스템-동작과-제약만-source-of-truth로-제공하고-완료된-실행-과정과-일회성-수치는-plan-adr-evidence-또는-git-이력에만-두어야-한다)

### Approved bundle replacement fixture에서 exact baseline path·hash와 evidence를 가진 one-to-one transition만 교체를 허용하고 hash·target·prefix·evidence·관계가 잘못된 fixture는 원래 bundle을 유지한 채 실패한다.

검증하는 요구사항:

- [`approved` 또는 `implemented` baseline bundle을 새 semantic path로 교체할 때는 `docs/specs/.bundle-transitions.json`에 exact baseline bundle path와 bundle hash를 가진 one-to-one `superseded` transition을 선언해야 한다.](lifecycle-consumers-and-bundle-replacement.md#approved-또는-implemented-baseline-bundle을-새-semantic-path로-교체할-때는-docsspecsbundle-transitionsjson에-exact-baseline-bundle-path와-bundle-hash를-가진-one-to-one-superseded-transition을-선언해야-한다)
- [Bundle transition record는 `fromSourcePath`, `fromSourceSha256`, `disposition`, `toBundlePath`, `evidencePath`, `reason`만 사용하고 두 source path를 normalized repository-relative semantic bundle directory로 제한해야 한다.](lifecycle-consumers-and-bundle-replacement.md#bundle-transition-record는-fromsourcepath-fromsourcesha256-disposition-tobundlepath-evidencepath-reason만-사용하고-두-source-path를-normalized-repository-relative-semantic-bundle-directory로-제한해야-한다)
- [Validator는 transition의 baseline bundle hash, current target path·status, append-only record prefix, evidence file, unique source·target과 one-step 관계를 검증하고 replacement bundle의 일반 validation도 별도로 수행해야 한다.](lifecycle-consumers-and-bundle-replacement.md#validator는-transition의-baseline-bundle-hash-current-target-pathstatus-append-only-record-prefix-evidence-file-unique-sourcetarget과-one-step-관계를-검증하고-replacement-bundle의-일반-validation도-별도로-수행해야-한다)
