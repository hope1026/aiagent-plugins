# Forge 실행 속도와 시각 품질 개선 계획

> the forge executing-plans skill로 Task를 실행한다. 사용자 “진행하자”는 2026-09-06 점검 보고서의 구체적인 개선 범위를 승인한다. 파일 소유권이 분리된 작업은 병렬로 진행하고 root가 정본·계획·통합·최종 검증을 소유한다.

Status: complete

**Related Specs:**
- bundle: docs/specs/canonical-spec-workflow/
- bundle: docs/specs/review-viewer-lifecycle/
- bundle: docs/specs/forge-ui-design-skill-separation/
- bundle: docs/specs/semantic-spec-bundles/

**목표:** 간단한 작업은 가볍게 실행하고, 복잡한 작업은 필요한 계약과 검증을 유지하며, 시각 자료는 실제로 읽을 수 있는 품질로 제공한다.

**구조:** Markdown source → Semantic IR → Presentation Plan → 공통 renderer → 표시된 패널의 비동기 diagram rendering을 유지한다. 스킬은 라우팅·계획·검증의 책임을 나누고 전문 단계는 변경 규모에 맞춰 적용한다.

## Global Constraints

- 공개 배포 스킬은 English, 보고·계획·정본의 설명은 Korean을 사용한다.
- 기존 정본 경로와 source provenance를 유지한다. 관련 exact statement 링크는 변경된 heading에 맞춰 갱신한다.
- 승인된 보고서의 간결한 Task 형식을 사용한다. 전체 구현 코드를 계획에 중복 작성하지 않는다.
- 변경된 의미와 회귀 보존 범위를 함께 확인한다. 관련 번들 전체를 새로 구현한다고 주장하지 않는다.
- 외부 release는 이번 실행 범위에 포함하지 않는다. 로컬 commit은 통합 검증 뒤 수행한다.

## Routes

| Route | Tasks | 결과 | Checkpoint |
|---|---|---|---|
| 계약과 지침 | 1, 5 | 승인 범위의 정본·스킬·정책 검사 일치 | 변경과 검증 기록 |
| 뷰어 복원 | 2, 3 | 관계 의미와 패널 도표 복원 | 독립 focused tests |
| 읽기 품질 | 4 | 목적 우선 개요와 자연스러운 안내 | renderer·실제 화면 |
| 통합 검증 | 6 | 전체 회귀와 pressure evidence | 최종 보고 |

## Tasks

### Task 1: 승인된 계약 변경을 반영하고 추적성을 정리한다

**Governing statements:**
- [기존 Canonical Spec의 규범적 의미를 변경하거나 새 Canonical Spec을 제안할 때는 승인 전 내용을 Spec Delta로 제시해야 한다. Spec Delta는 baseline bundle path, member path, exact Requirement·Acceptance heading과 결정 변경을 식별하고 사용자의 명시적 승인 뒤에만 Canonical Spec에 반영해야 한다.](../../specs/canonical-spec-workflow/canonical-spec-and-work-artifact-boundaries.md#기존-canonical-spec의-규범적-의미를-변경하거나-새-canonical-spec을-제안할-때는-승인-전-내용을-spec-delta로-제시해야-한다-spec-delta는-baseline-bundle-path-member-path-exact-requirementacceptance-heading과-결정-변경을-식별하고-사용자의-명시적-승인-뒤에만-canonical-spec에-반영해야-한다)

**파일:** 관련 `docs/specs/` bundle, `.forge/work/forge-purpose-alignment/spec-delta.md`, 이 plan.
**인터페이스:** 기존 bundle path와 full-statement links 유지; baseline은 `.forge/work/forge-purpose-alignment/baseline.json`.
**의존성:** 없음. **소유권:** root. **검증:** writer transaction 및 변경 statement 링크.
- [x] **Step 1: 정확한 변경 문장과 baseline을 기록하고 승인된 의미를 적용한다.**
- [x] **Step 2: 정본 validation과 링크 검증을 통과한다.**

### Task 2: 명시적인 흐름만 시각 후보로 추출한다

**Governing statements:**
- [Visual Docs는 source에 없는 새로운 런타임 책임, transaction 순서, 상태 전이 또는 설계 결정을 derived diagram에 추가하지 않아야 한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#visual-docs는-source에-없는-새로운-런타임-책임-transaction-순서-상태-전이-또는-설계-결정을-derived-diagram에-추가하지-않아야-한다)

**파일:** `plugins/forge/skills/visual-docs/scripts/review_ir.py`, `plugins/forge/skills/visual-docs/tests/test_review_ir.py`.
**인터페이스:** SemanticEntity와 기존 ordered-flow shape 유지. Markdown 링크·복합 prose의 오인 방지, standalone/code/list의 명시된 흐름 지원.
**의존성:** 없음 — 이미 승인된 source-backed 의미 복원. **소유권:** parser worker. **검증:** focused Python RED/GREEN와 기존 IR suite.
- [x] **Step 1: 점검 최소 재현을 실패 테스트로 고정한다.**
- [x] **Step 2: 보수적인 흐름 인식을 구현하고 의미 보존을 검증한다.**

### Task 3: 표시된 패널의 도표를 안전하게 렌더링하고 CI를 연결한다

**Governing statements:**
- [잘못된 Mermaid fixture를 열면 다른 panel은 정상 동작하고 오류 diagram에는 오류 요약, 가능한 line·column, 원문 source가 표시된다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#잘못된-mermaid-fixture를-열면-다른-panel은-정상-동작하고-오류-diagram에는-오류-요약-가능한-linecolumn-원문-source가-표시된다)

**파일:** `plugins/forge/skills/visual-docs/assets/viewer-template.html`, `plugins/forge/skills/visual-docs/tests/browser/visual-docs.spec.mjs`, `plugins/forge/skills/visual-docs/tests/run-visual-docs-browser.sh`, 필요한 browser fixture, `.github/workflows/validate.yml`.
**인터페이스:** 기존 tree/hash/print UI 유지. 준비 상태는 현재 표시 패널의 async render와 일치한다. Root renderer와 공유하는 `.system-overview-lede`, `.system-metrics`, `.system-review-links` 스타일은 이 Task가 소유한다.
**의존성:** 없음 — 기존 runtime 계약 복원. **소유권:** runtime worker. **검증:** hidden → selected, rapid navigation, deep link, mobile, print, invalid Mermaid regression. CI에 전체 Python discovery와 manager suite 연결.
- [x] **Step 1: 숨겨진 분기 도표 실패와 준비 상태를 실제 browser로 재현한다.**
- [x] **Step 2: 표시 시 rendering과 필요한 print 준비를 구현한다.**
- [x] **Step 3: 전체 browser 검증과 CI 누락 연결을 확인한다.**

### Task 4: 목적 설명을 먼저 보여주고 한국어 안내를 정리한다

**Governing statements:**
- [Visual Docs의 Overview는 source가 제공하는 목적과 핵심 내용을 먼저 제시하고 source별 집계는 보조 정보로 배치해야 한다. 요약과 상세 집계는 structured parser의 같은 기준에서 계산하고 모든 원문 상세로 이동할 수 있어야 한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#visual-docs의-overview는-source가-제공하는-목적과-핵심-내용을-먼저-제시하고-source별-집계는-보조-정보로-배치해야-한다-요약과-상세-집계는-structured-parser의-같은-기준에서-계산하고-모든-원문-상세로-이동할-수-있어야-한다)
- [system-overview는 source의 Overview 목적 설명을 먼저 보여주고 짧은 member별 탐색과 핵심 동작으로 안내해야 한다. areas, components와 Requirement·Acceptance·member 집계는 보조 정보로 배치하며 전체 도표·완료 기준을 개요에 모두 펼치지 않고 각 상세에서 정확한 원문과 provenance를 제공해야 한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#system-overview는-source의-overview-목적-설명을-먼저-보여주고-짧은-member별-탐색과-핵심-동작으로-안내해야-한다-areas-components와-requirementacceptancemember-집계는-보조-정보로-배치하며-전체-도표완료-기준을-개요에-모두-펼치지-않고-각-상세에서-정확한-원문과-provenance를-제공해야-한다)
- [목적 설명이 있는 Spec과 plan의 Overview를 열면 목적과 핵심 내용이 집계보다 먼저 보이고 390px에서도 숫자 카드가 첫 읽기 화면을 차지하지 않으며 요약과 상세 수치가 같은 source 집계 기준과 일치한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#목적-설명이-있는-spec과-plan의-overview를-열면-목적과-핵심-내용이-집계보다-먼저-보이고-390px에서도-숫자-카드가-첫-읽기-화면을-차지하지-않으며-요약과-상세-수치가-같은-source-집계-기준과-일치한다)
- [Visual Docs copy는 이 화면에서 확인할 것을 먼저 말하고, 번역해도 의미가 유지되는 label은 사용자 언어로 쓰며 고유 API·service·schema 이름만 원문으로 유지해야 한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#visual-docs-copy는-이-화면에서-확인할-것을-먼저-말하고-번역해도-의미가-유지되는-label은-사용자-언어로-쓰며-고유-apiserviceschema-이름만-원문으로-유지해야-한다)

**파일:** `plugins/forge/skills/visual-docs/scripts/review_components.py`, `plugins/forge/skills/visual-docs/tests/test_review_renderer.py`.
**인터페이스:** 공통 Semantic IR·provenance 유지. source Overview 설명을 `.system-overview-lede`로 우선 표시, 집계는 보조 정보. `.system-review-links`는 source member로 연결하는 짧은 목록이다. CSS는 Task 3 소유.
**의존성:** 1의 해당 의미 반영. **소유권:** root 또는 독립 renderer worker. **검증:** 원문 보존·순서·현지화·전체 상세 접근 및 desktop/mobile 화면.
- [x] **Step 1: 목적 설명·한글 안내·긴 source의 개요 밀도 테스트를 추가한다.**
- [x] **Step 2: 개요와 source diagram 안내를 개선하고 모든 상세 접근을 보존한다.**

### Task 5: 스킬 절차를 변경 규모에 맞추고 정책 검사를 동기화한다

**Governing statements:**
- [Forge는 사용자 요청과 repository context에서 목표, 범위, 비범위와 관찰 가능한 완료 조건을 확인해야 한다. 명확한 국소 작업은 이를 내부적으로 판단하고 목표와 검증을 짧게 알린 뒤 실행하며 네 필드를 별도 양식으로 출력하거나 파일로 만들지 않아야 한다. 재개, 위임, 여러 범위 조정 또는 명시적 사용자 검토에 독립 문서가 필요한 경우에만 Change Brief 파일을 만들 수 있어야 한다.](../../specs/canonical-spec-workflow/canonical-spec-and-work-artifact-boundaries.md#forge는-사용자-요청과-repository-context에서-목표-범위-비범위와-관찰-가능한-완료-조건을-확인해야-한다-명확한-국소-작업은-이를-내부적으로-판단하고-목표와-검증을-짧게-알린-뒤-실행하며-네-필드를-별도-양식으로-출력하거나-파일로-만들지-않아야-한다-재개-위임-여러-범위-조정-또는-명시적-사용자-검토에-독립-문서가-필요한-경우에만-change-brief-파일을-만들-수-있어야-한다)
- [`Canonical Spec 영향: no`이고 `Execution complexity: low`인 국소적·가역적 작업은 Quick 경로로 실행해야 한다. 문구·스타일·로직 없는 설정에는 결과를 직접 증명하는 표시·유효성 검사를 적용하고 새 로직·동작 결함에는 focused TDD와 관련 회귀 검증을 적용해야 한다. Quick은 별도 정본·계획·전체 UI 선언·테스트 프레임워크 설치를 기계적으로 요구하지 않아야 한다.](../../specs/canonical-spec-workflow/routing-and-lifecycle-gates.md#canonical-spec-영향-no이고-execution-complexity-low인-국소적가역적-작업은-quick-경로로-실행해야-한다-문구스타일로직-없는-설정에는-결과를-직접-증명하는-표시유효성-검사를-적용하고-새-로직동작-결함에는-focused-tdd와-관련-회귀-검증을-적용해야-한다-quick은-별도-정본계획전체-ui-선언테스트-프레임워크-설치를-기계적으로-요구하지-않아야-한다)
- [Forge lifecycle skill은 bundle의 Acceptance statement가 있으면 Acceptance를, 없으면 Requirement를 Canonical verification set으로 사용해야 한다. 새 계약 또는 미구현 baseline의 전체 구현은 전체 집합을 Task와 검증에 연결하고, 구현된 baseline의 부분 변경·복원은 직접·간접 영향 항목과 회귀 보존 범위를 명시해 계획과 완료 검증에 동일하게 적용해야 한다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#forge-lifecycle-skill은-bundle의-acceptance-statement가-있으면-acceptance를-없으면-requirement를-canonical-verification-set으로-사용해야-한다-새-계약-또는-미구현-baseline의-전체-구현은-전체-집합을-task와-검증에-연결하고-구현된-baseline의-부분-변경복원은-직접간접-영향-항목과-회귀-보존-범위를-명시해-계획과-완료-검증에-동일하게-적용해야-한다)
- [완료된 Visual Docs의 source가 변경되었다는 사실만으로는 갱신하지 않아야 한다. 사용자가 요청한 시각 문서를 완성하는 동안에는 같은 요청 범위의 source·공통 tooling 수정, 검증과 필요한 재생성이 허용되며, 요청 완료 뒤 별도 갱신에는 새로운 명시적 의도가 필요해야 한다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#완료된-visual-docs의-source가-변경되었다는-사실만으로는-갱신하지-않아야-한다-사용자가-요청한-시각-문서를-완성하는-동안에는-같은-요청-범위의-source공통-tooling-수정-검증과-필요한-재생성이-허용되며-요청-완료-뒤-별도-갱신에는-새로운-명시적-의도가-필요해야-한다)
- [요청한 Brief, Plan 또는 Spec View의 완료는 deterministic build 성공과 변경 규모에 맞는 실제 읽기·표시 검증으로 판단해야 한다. 생성 성공만으로 시각 품질이나 governing product 구현 완료를 주장하지 않아야 한다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#요청한-brief-plan-또는-spec-view의-완료는-deterministic-build-성공과-변경-규모에-맞는-실제-읽기표시-검증으로-판단해야-한다-생성-성공만으로-시각-품질이나-governing-product-구현-완료를-주장하지-않아야-한다)
- [개별 Visual Docs의 검증은 요청한 결과를 직접 증명하는 최소 범위로 선택해야 한다. 동일한 변경 상태에서 이미 통과한 검증은 재사용할 수 있고, 새 변경·실패·미해결 위험이 있을 때만 필요한 증거를 다시 수집해야 한다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#개별-visual-docs의-검증은-요청한-결과를-직접-증명하는-최소-범위로-선택해야-한다-동일한-변경-상태에서-이미-통과한-검증은-재사용할-수-있고-새-변경실패미해결-위험이-있을-때만-필요한-증거를-다시-수집해야-한다)
- [개별 Visual Docs는 실제 화면의 읽기 순서와 핵심 내용을 확인해야 하며, 복잡한 자료·새 구성·도표가 있으면 desktop과 narrow viewport에서 도표 의미, 탐색과 가독성을 확인해야 한다. 검증 실패는 같은 요청 안에서 원본 또는 공통 tooling을 수정하고 재생성해 해결하되 생성 HTML을 직접 편집하지 않아야 한다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#개별-visual-docs는-실제-화면의-읽기-순서와-핵심-내용을-확인해야-하며-복잡한-자료새-구성도표가-있으면-desktop과-narrow-viewport에서-도표-의미-탐색과-가독성을-확인해야-한다-검증-실패는-같은-요청-안에서-원본-또는-공통-tooling을-수정하고-재생성해-해결하되-생성-html을-직접-편집하지-않아야-한다)
- [`writing-specs`와 `writing-plans`는 Markdown source 검토 후 시각 자료가 판단에 도움이 될 때 그 효용을 간단히 안내할 수 있어야 한다. 시각 자료가 필요하지 않거나 이미 요청된 경우 추가 생성 여부 질문을 하지 않아야 한다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#writing-specs와-writing-plans는-markdown-source-검토-후-시각-자료가-판단에-도움이-될-때-그-효용을-간단히-안내할-수-있어야-한다-시각-자료가-필요하지-않거나-이미-요청된-경우-추가-생성-여부-질문을-하지-않아야-한다)
- [시각 문서 요청 fixture에서 agent는 build 후 읽기·표시를 확인하고 필요한 경우 같은 요청 안에서 원본·공통 tooling 수정과 재생성을 수행하며 별도 재승인을 요구하지 않는다. 완료 후 source만 변경된 fixture는 자동 갱신하지 않고, 어느 경우에도 View 생성만으로 governing product lifecycle을 변경하지 않는다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#시각-문서-요청-fixture에서-agent는-build-후-읽기표시를-확인하고-필요한-경우-같은-요청-안에서-원본공통-tooling-수정과-재생성을-수행하며-별도-재승인을-요구하지-않는다-완료-후-source만-변경된-fixture는-자동-갱신하지-않고-어느-경우에도-view-생성만으로-governing-product-lifecycle을-변경하지-않는다)
- [spec 또는 plan의 Markdown source 검토가 끝나면 시각 자료가 유용한 경우 그 효용을 안내할 수 있고, 사용자가 요청하지 않은 fixture에는 HTML이 생성되지 않으며 이미 시각화를 요청한 fixture에는 같은 의도를 다시 묻지 않는다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#spec-또는-plan의-markdown-source-검토가-끝나면-시각-자료가-유용한-경우-그-효용을-안내할-수-있고-사용자가-요청하지-않은-fixture에는-html이-생성되지-않으며-이미-시각화를-요청한-fixture에는-같은-의도를-다시-묻지-않는다)
- [Visual Docs shell, template, style, script 또는 runtime을 변경하면 desktop 1440px와 mobile 390px에서 해당 탐색, 표, diagram, deep link와 checkbox를 검증해야 한다. 개별 View 생성은 자료와 요청의 복잡도에 맞는 읽기·표시 검증을 적용하고 공통 tooling의 전체 회귀를 기계적으로 반복하지 않아야 한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#visual-docs-shell-template-style-script-또는-runtime을-변경하면-desktop-1440px와-mobile-390px에서-해당-탐색-표-diagram-deep-link와-checkbox를-검증해야-한다-개별-view-생성은-자료와-요청의-복잡도에-맞는-읽기표시-검증을-적용하고-공통-tooling의-전체-회귀를-기계적으로-반복하지-않아야-한다)
- [공통 renderer의 provenance와 reading-route 변경은 desktop 1440px와 mobile 390px 및 관련 검증 항목으로 확인해야 한다. 이후 개별 View에서는 해당 자료의 읽기 품질을 확인하되 변경되지 않은 공통 구현의 전체 회귀는 반복하지 않아야 한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#공통-renderer의-provenance와-reading-route-변경은-desktop-1440px와-mobile-390px-및-관련-검증-항목으로-확인해야-한다-이후-개별-view에서는-해당-자료의-읽기-품질을-확인하되-변경되지-않은-공통-구현의-전체-회귀는-반복하지-않아야-한다)
- [Visual Docs tooling 변경 fixture는 desktop 1440px와 mobile 390px에서 숨겨진 상세 선택, 빠른 탐색, deep link, checkbox persistence, diagram, table과 print의 필요한 상태를 통과한다. 유효한 Mermaid에는 표시된 오류가 없고 개별 View 생성 fixture도 요청 범위의 읽기·표시 확인을 수행한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#visual-docs-tooling-변경-fixture는-desktop-1440px와-mobile-390px에서-숨겨진-상세-선택-빠른-탐색-deep-link-checkbox-persistence-diagram-table과-print의-필요한-상태를-통과한다-유효한-mermaid에는-표시된-오류가-없고-개별-view-생성-fixture도-요청-범위의-읽기표시-확인을-수행한다)
- [Visual Docs tooling fixture에 Markdown source와 View Context를 입력하면 Semantic IR, validated Presentation Plan, source manifest와 profile-specific HTML이 만들어지고 unresolved source reference·수동 content fragment·source 밖 의미가 0개다. 개별 View 검증은 자료에 필요한 범위로 수행한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#visual-docs-tooling-fixture에-markdown-source와-view-context를-입력하면-semantic-ir-validated-presentation-plan-source-manifest와-profile-specific-html이-만들어지고-unresolved-source-reference수동-content-fragmentsource-밖-의미가-0개다-개별-view-검증은-자료에-필요한-범위로-수행한다)
- [공통 provenance와 reading-route 구현을 검증하면 desktop 1440px와 mobile 390px의 탐색, 표, diagram, deep link와 checkbox가 동작하며 개별 View는 해당 자료의 읽기·표시를 확인하고 변경되지 않은 공통 회귀를 반복하지 않는다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#공통-provenance와-reading-route-구현을-검증하면-desktop-1440px와-mobile-390px의-탐색-표-diagram-deep-link와-checkbox가-동작하며-개별-view는-해당-자료의-읽기표시를-확인하고-변경되지-않은-공통-회귀를-반복하지-않는다)
- [`writing-plans`는 실제 독립 단계에 맞는 Route 또는 Milestone으로 Task를 묶고 각 Task를 하나의 primary Route에 배정해야 한다. 큰 계획에서는 6~10개 묶음을 가독성 지침으로 사용할 수 있지만 개수를 맞추기 위해 단계를 만들지 않아야 한다.](../../specs/review-viewer-lifecycle/plan-context-and-statement-traceability.md#writing-plans는-실제-독립-단계에-맞는-route-또는-milestone으로-task를-묶고-각-task를-하나의-primary-route에-배정해야-한다-큰-계획에서는-610개-묶음을-가독성-지침으로-사용할-수-있지만-개수를-맞추기-위해-단계를-만들지-않아야-한다)
- [`writing-plans`는 목표와 완료 상태, Related Specs, Task별 산출물·파일 경계·의존성·Interface·검증·재개 조건과 실제 승인 지점을 명확히 해야 한다. Runtime 책임, 데이터 흐름, 확장 지점과 diagram은 작업에 필요한 경우만 포함하고 구현 코드 전체를 미리 작성하거나 반복하지 않아야 한다. 조사 Task는 구체적인 질문과 종료 증거를 가져야 한다.](../../specs/review-viewer-lifecycle/plan-context-and-statement-traceability.md#writing-plans는-목표와-완료-상태-related-specs-task별-산출물파일-경계의존성interface검증재개-조건과-실제-승인-지점을-명확히-해야-한다-runtime-책임-데이터-흐름-확장-지점과-diagram은-작업에-필요한-경우만-포함하고-구현-코드-전체를-미리-작성하거나-반복하지-않아야-한다-조사-task는-구체적인-질문과-종료-증거를-가져야-한다)
- [`writing-plans`는 Canonical verification set에서 작업에 필요한 범위를 명시해야 한다. 새 계약·미구현 baseline의 전체 구현은 전체 항목을, 구현된 baseline의 부분 변경·복원은 직접·간접 영향 항목을 Task의 Governing statements와 coverage table에 연결하고 나머지 계약의 회귀 보존 근거를 기록해야 한다.](../../specs/review-viewer-lifecycle/plan-context-and-statement-traceability.md#writing-plans는-canonical-verification-set에서-작업에-필요한-범위를-명시해야-한다-새-계약미구현-baseline의-전체-구현은-전체-항목을-구현된-baseline의-부분-변경복원은-직접간접-영향-항목을-task의-governing-statements와-coverage-table에-연결하고-나머지-계약의-회귀-보존-근거를-기록해야-한다)
- [복잡한 plan은 검토에 필요한 관계가 source에 있을 때 Task dependency, runtime 또는 transaction, 확장 구조 관점의 diagram을 포함해야 한다. 관계가 없는 관점은 만들지 않고 표나 짧은 설명을 사용해야 한다.](../../specs/review-viewer-lifecycle/plan-context-and-statement-traceability.md#복잡한-plan은-검토에-필요한-관계가-source에-있을-때-task-dependency-runtime-또는-transaction-확장-구조-관점의-diagram을-포함해야-한다-관계가-없는-관점은-만들지-않고-표나-짧은-설명을-사용해야-한다)
- [`writing-plans`는 큰 Task 집합을 하나의 평면 diagram으로 연결하지 않고 실제 단계에 맞는 의미 있는 Route로 묶은 뒤 필요한 Task 관계를 보여줘야 한다.](../../specs/review-viewer-lifecycle/plan-context-and-statement-traceability.md#writing-plans는-큰-task-집합을-하나의-평면-diagram으로-연결하지-않고-실제-단계에-맞는-의미-있는-route로-묶은-뒤-필요한-task-관계를-보여줘야-한다)
- [복잡한 plan fixture에는 독립 경로, 선택적인 Related Specs, 변경 범위에 맞는 Governing statements, 실행 가능한 Task와 검증, 실제 단계의 Route와 checkpoint가 존재하며 불필요한 전체 구현 코드나 관계가 없는 diagram이 추가되지 않는다.](../../specs/review-viewer-lifecycle/plan-context-and-statement-traceability.md#복잡한-plan-fixture에는-독립-경로-선택적인-related-specs-변경-범위에-맞는-governing-statements-실행-가능한-task와-검증-실제-단계의-route와-checkpoint가-존재하며-불필요한-전체-구현-코드나-관계가-없는-diagram이-추가되지-않는다)
- [Source 변경만으로 완료된 local View나 tracked Project Handbook을 자동 갱신하지 않아야 한다. 진행 중인 명시적 시각 문서 요청을 완성하기 위한 검증·수정·재생성은 같은 요청 안에서 수행할 수 있고, 완료 후 새 갱신에는 명시적 사용자 의도가 필요해야 한다.](../../specs/semantic-spec-bundles/lifecycle-consumers-and-bundle-replacement.md#source-변경만으로-완료된-local-view나-tracked-project-handbook을-자동-갱신하지-않아야-한다-진행-중인-명시적-시각-문서-요청을-완성하기-위한-검증수정재생성은-같은-요청-안에서-수행할-수-있고-완료-후-새-갱신에는-명시적-사용자-의도가-필요해야-한다)

**파일:** `plugins/forge/skills/*/SKILL.md`, 관련 `references/`, `README.md`, `scripts/tests/`의 정책 검사. 유지보수 portability reference 변경 시 manager render 사용.
**인터페이스:** 14개 이름·responsibility 유지. Quick은 가벼운 실행, logic은 TDD, 계획은 bounded Task, 승인된 시각 요청은 검증·수정·재생성 포함.
**의존성:** 1. **소유권:** root. **검증:** 변경된 정책 assertions, 승인 범위·모호성·빠른 작업 pressure scenario.
- [x] **Step 1: Quick·TDD·UI·계획·검증·톤의 중복 의무를 정리한다.**
- [x] **Step 2: 원본·reference·README·정책 검사를 같은 의미로 맞춘다.**
- [x] **Step 3: 새 agent의 실제 시나리오 대응을 검토한다.**

### Task 6: 변경을 통합하고 실제 자료로 검증한다

**Governing statements:**
- [모든 구현 완료 주장은 fresh command-level verification을 필요로 해야 한다. 승인된 Spec Delta를 구현한 작업은 bundle의 Canonical verification set을 full text와 member path로 식별해 실제 동작으로 검증해야 한다. Acceptance statement가 하나 이상 있으면 해당 Acceptance statement를 사용하고, 없으면 Requirement statement를 사용해야 한다. Quick 작업은 원래 reproduction, focused test, build·lint 중 주장에 맞는 증거만 요구하고 spec status 전환이나 전체 Canonical verification set 순회를 요구하지 않아야 한다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#모든-구현-완료-주장은-fresh-command-level-verification을-필요로-해야-한다-승인된-spec-delta를-구현한-작업은-bundle의-canonical-verification-set을-full-text와-member-path로-식별해-실제-동작으로-검증해야-한다-acceptance-statement가-하나-이상-있으면-해당-acceptance-statement를-사용하고-없으면-requirement-statement를-사용해야-한다-quick-작업은-원래-reproduction-focused-test-buildlint-중-주장에-맞는-증거만-요구하고-spec-status-전환이나-전체-canonical-verification-set-순회를-요구하지-않아야-한다)

**파일:** 이 plan과 필요 evidence 문서. **의존성:** 1–5. **소유권:** root.
**검증:** `bash scripts/validate.sh`, Python discovery 3개 skill, 모든 shell 정책·설치 검사, Mermaid/freshness 검사, browser harness. 실제 한국어 bundle 임시 build의 desktop·390px·hidden detail·도표·overview를 확인한다.
- [x] **Step 1: worker diff와 focused evidence를 검토하고 전체 회귀를 실행한다.**
- [x] **Step 2: 실제 한국어 자료의 화면을 확인하고 발견한 문제를 범위 안에서 해결한다.**
- [x] **Step 3: 영향받는 계약 증거를 기록하고 상태를 정리해 결과를 보고한다.**

## Statement Coverage

이 계획은 구현된 baseline의 부분 변경이다. 정확한 변경 의미와 baseline은 `.forge/work/forge-purpose-alignment/spec-delta.md`에 기록했다. 아래 표와 Task 링크가 영향 범위다. 변경되지 않은 계약은 Spec·Visual Docs·extension manager 전체 Python suite, shell 정책·설치 검사와 browser 회귀로 보존한다.

| Statement | Task | Verification |
|---|---|---|
| [기존 Canonical Spec의 규범적 의미를 변경하거나 새 Canonical Spec을 제안할 때는 승인 전 내용을 Spec Delta로 제시해야 한다. Spec Delta는 baseline bundle path, member path, exact Requirement·Acceptance heading과 결정 변경을 식별하고 사용자의 명시적 승인 뒤에만 Canonical Spec에 반영해야 한다.](../../specs/canonical-spec-workflow/canonical-spec-and-work-artifact-boundaries.md#기존-canonical-spec의-규범적-의미를-변경하거나-새-canonical-spec을-제안할-때는-승인-전-내용을-spec-delta로-제시해야-한다-spec-delta는-baseline-bundle-path-member-path-exact-requirementacceptance-heading과-결정-변경을-식별하고-사용자의-명시적-승인-뒤에만-canonical-spec에-반영해야-한다) | 1 | writer transaction |
| [Visual Docs는 source에 없는 새로운 런타임 책임, transaction 순서, 상태 전이 또는 설계 결정을 derived diagram에 추가하지 않아야 한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#visual-docs는-source에-없는-새로운-런타임-책임-transaction-순서-상태-전이-또는-설계-결정을-derived-diagram에-추가하지-않아야-한다) | 2 | IR regression |
| [잘못된 Mermaid fixture를 열면 다른 panel은 정상 동작하고 오류 diagram에는 오류 요약, 가능한 line·column, 원문 source가 표시된다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#잘못된-mermaid-fixture를-열면-다른-panel은-정상-동작하고-오류-diagram에는-오류-요약-가능한-linecolumn-원문-source가-표시된다) | 3 | browser regression |
| [Visual Docs의 Overview는 source가 제공하는 목적과 핵심 내용을 먼저 제시하고 source별 집계는 보조 정보로 배치해야 한다. 요약과 상세 집계는 structured parser의 같은 기준에서 계산하고 모든 원문 상세로 이동할 수 있어야 한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#visual-docs의-overview는-source가-제공하는-목적과-핵심-내용을-먼저-제시하고-source별-집계는-보조-정보로-배치해야-한다-요약과-상세-집계는-structured-parser의-같은-기준에서-계산하고-모든-원문-상세로-이동할-수-있어야-한다) | 4 | renderer + browser |
| [system-overview는 source의 Overview 목적 설명을 먼저 보여주고 짧은 member별 탐색과 핵심 동작으로 안내해야 한다. areas, components와 Requirement·Acceptance·member 집계는 보조 정보로 배치하며 전체 도표·완료 기준을 개요에 모두 펼치지 않고 각 상세에서 정확한 원문과 provenance를 제공해야 한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#system-overview는-source의-overview-목적-설명을-먼저-보여주고-짧은-member별-탐색과-핵심-동작으로-안내해야-한다-areas-components와-requirementacceptancemember-집계는-보조-정보로-배치하며-전체-도표완료-기준을-개요에-모두-펼치지-않고-각-상세에서-정확한-원문과-provenance를-제공해야-한다) | 4 | renderer + browser |
| [목적 설명이 있는 Spec과 plan의 Overview를 열면 목적과 핵심 내용이 집계보다 먼저 보이고 390px에서도 숫자 카드가 첫 읽기 화면을 차지하지 않으며 요약과 상세 수치가 같은 source 집계 기준과 일치한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#목적-설명이-있는-spec과-plan의-overview를-열면-목적과-핵심-내용이-집계보다-먼저-보이고-390px에서도-숫자-카드가-첫-읽기-화면을-차지하지-않으며-요약과-상세-수치가-같은-source-집계-기준과-일치한다) | 4 | renderer + browser |
| [Visual Docs copy는 이 화면에서 확인할 것을 먼저 말하고, 번역해도 의미가 유지되는 label은 사용자 언어로 쓰며 고유 API·service·schema 이름만 원문으로 유지해야 한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#visual-docs-copy는-이-화면에서-확인할-것을-먼저-말하고-번역해도-의미가-유지되는-label은-사용자-언어로-쓰며-고유-apiserviceschema-이름만-원문으로-유지해야-한다) | 4 | renderer + browser |
| [Forge는 사용자 요청과 repository context에서 목표, 범위, 비범위와 관찰 가능한 완료 조건을 확인해야 한다. 명확한 국소 작업은 이를 내부적으로 판단하고 목표와 검증을 짧게 알린 뒤 실행하며 네 필드를 별도 양식으로 출력하거나 파일로 만들지 않아야 한다. 재개, 위임, 여러 범위 조정 또는 명시적 사용자 검토에 독립 문서가 필요한 경우에만 Change Brief 파일을 만들 수 있어야 한다.](../../specs/canonical-spec-workflow/canonical-spec-and-work-artifact-boundaries.md#forge는-사용자-요청과-repository-context에서-목표-범위-비범위와-관찰-가능한-완료-조건을-확인해야-한다-명확한-국소-작업은-이를-내부적으로-판단하고-목표와-검증을-짧게-알린-뒤-실행하며-네-필드를-별도-양식으로-출력하거나-파일로-만들지-않아야-한다-재개-위임-여러-범위-조정-또는-명시적-사용자-검토에-독립-문서가-필요한-경우에만-change-brief-파일을-만들-수-있어야-한다) | 5 | policy + pressure scenario |
| [`Canonical Spec 영향: no`이고 `Execution complexity: low`인 국소적·가역적 작업은 Quick 경로로 실행해야 한다. 문구·스타일·로직 없는 설정에는 결과를 직접 증명하는 표시·유효성 검사를 적용하고 새 로직·동작 결함에는 focused TDD와 관련 회귀 검증을 적용해야 한다. Quick은 별도 정본·계획·전체 UI 선언·테스트 프레임워크 설치를 기계적으로 요구하지 않아야 한다.](../../specs/canonical-spec-workflow/routing-and-lifecycle-gates.md#canonical-spec-영향-no이고-execution-complexity-low인-국소적가역적-작업은-quick-경로로-실행해야-한다-문구스타일로직-없는-설정에는-결과를-직접-증명하는-표시유효성-검사를-적용하고-새-로직동작-결함에는-focused-tdd와-관련-회귀-검증을-적용해야-한다-quick은-별도-정본계획전체-ui-선언테스트-프레임워크-설치를-기계적으로-요구하지-않아야-한다) | 5 | policy + pressure scenario |
| [Forge lifecycle skill은 bundle의 Acceptance statement가 있으면 Acceptance를, 없으면 Requirement를 Canonical verification set으로 사용해야 한다. 새 계약 또는 미구현 baseline의 전체 구현은 전체 집합을 Task와 검증에 연결하고, 구현된 baseline의 부분 변경·복원은 직접·간접 영향 항목과 회귀 보존 범위를 명시해 계획과 완료 검증에 동일하게 적용해야 한다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#forge-lifecycle-skill은-bundle의-acceptance-statement가-있으면-acceptance를-없으면-requirement를-canonical-verification-set으로-사용해야-한다-새-계약-또는-미구현-baseline의-전체-구현은-전체-집합을-task와-검증에-연결하고-구현된-baseline의-부분-변경복원은-직접간접-영향-항목과-회귀-보존-범위를-명시해-계획과-완료-검증에-동일하게-적용해야-한다) | 5 | policy + pressure scenario |
| [완료된 Visual Docs의 source가 변경되었다는 사실만으로는 갱신하지 않아야 한다. 사용자가 요청한 시각 문서를 완성하는 동안에는 같은 요청 범위의 source·공통 tooling 수정, 검증과 필요한 재생성이 허용되며, 요청 완료 뒤 별도 갱신에는 새로운 명시적 의도가 필요해야 한다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#완료된-visual-docs의-source가-변경되었다는-사실만으로는-갱신하지-않아야-한다-사용자가-요청한-시각-문서를-완성하는-동안에는-같은-요청-범위의-source공통-tooling-수정-검증과-필요한-재생성이-허용되며-요청-완료-뒤-별도-갱신에는-새로운-명시적-의도가-필요해야-한다) | 5 | policy + pressure scenario |
| [요청한 Brief, Plan 또는 Spec View의 완료는 deterministic build 성공과 변경 규모에 맞는 실제 읽기·표시 검증으로 판단해야 한다. 생성 성공만으로 시각 품질이나 governing product 구현 완료를 주장하지 않아야 한다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#요청한-brief-plan-또는-spec-view의-완료는-deterministic-build-성공과-변경-규모에-맞는-실제-읽기표시-검증으로-판단해야-한다-생성-성공만으로-시각-품질이나-governing-product-구현-완료를-주장하지-않아야-한다) | 5 | policy + pressure scenario |
| [개별 Visual Docs의 검증은 요청한 결과를 직접 증명하는 최소 범위로 선택해야 한다. 동일한 변경 상태에서 이미 통과한 검증은 재사용할 수 있고, 새 변경·실패·미해결 위험이 있을 때만 필요한 증거를 다시 수집해야 한다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#개별-visual-docs의-검증은-요청한-결과를-직접-증명하는-최소-범위로-선택해야-한다-동일한-변경-상태에서-이미-통과한-검증은-재사용할-수-있고-새-변경실패미해결-위험이-있을-때만-필요한-증거를-다시-수집해야-한다) | 5 | policy + pressure scenario |
| [개별 Visual Docs는 실제 화면의 읽기 순서와 핵심 내용을 확인해야 하며, 복잡한 자료·새 구성·도표가 있으면 desktop과 narrow viewport에서 도표 의미, 탐색과 가독성을 확인해야 한다. 검증 실패는 같은 요청 안에서 원본 또는 공통 tooling을 수정하고 재생성해 해결하되 생성 HTML을 직접 편집하지 않아야 한다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#개별-visual-docs는-실제-화면의-읽기-순서와-핵심-내용을-확인해야-하며-복잡한-자료새-구성도표가-있으면-desktop과-narrow-viewport에서-도표-의미-탐색과-가독성을-확인해야-한다-검증-실패는-같은-요청-안에서-원본-또는-공통-tooling을-수정하고-재생성해-해결하되-생성-html을-직접-편집하지-않아야-한다) | 5 | policy + pressure scenario |
| [`writing-specs`와 `writing-plans`는 Markdown source 검토 후 시각 자료가 판단에 도움이 될 때 그 효용을 간단히 안내할 수 있어야 한다. 시각 자료가 필요하지 않거나 이미 요청된 경우 추가 생성 여부 질문을 하지 않아야 한다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#writing-specs와-writing-plans는-markdown-source-검토-후-시각-자료가-판단에-도움이-될-때-그-효용을-간단히-안내할-수-있어야-한다-시각-자료가-필요하지-않거나-이미-요청된-경우-추가-생성-여부-질문을-하지-않아야-한다) | 5 | policy + pressure scenario |
| [시각 문서 요청 fixture에서 agent는 build 후 읽기·표시를 확인하고 필요한 경우 같은 요청 안에서 원본·공통 tooling 수정과 재생성을 수행하며 별도 재승인을 요구하지 않는다. 완료 후 source만 변경된 fixture는 자동 갱신하지 않고, 어느 경우에도 View 생성만으로 governing product lifecycle을 변경하지 않는다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#시각-문서-요청-fixture에서-agent는-build-후-읽기표시를-확인하고-필요한-경우-같은-요청-안에서-원본공통-tooling-수정과-재생성을-수행하며-별도-재승인을-요구하지-않는다-완료-후-source만-변경된-fixture는-자동-갱신하지-않고-어느-경우에도-view-생성만으로-governing-product-lifecycle을-변경하지-않는다) | 5 | policy + pressure scenario |
| [spec 또는 plan의 Markdown source 검토가 끝나면 시각 자료가 유용한 경우 그 효용을 안내할 수 있고, 사용자가 요청하지 않은 fixture에는 HTML이 생성되지 않으며 이미 시각화를 요청한 fixture에는 같은 의도를 다시 묻지 않는다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#spec-또는-plan의-markdown-source-검토가-끝나면-시각-자료가-유용한-경우-그-효용을-안내할-수-있고-사용자가-요청하지-않은-fixture에는-html이-생성되지-않으며-이미-시각화를-요청한-fixture에는-같은-의도를-다시-묻지-않는다) | 5 | policy + pressure scenario |
| [Visual Docs shell, template, style, script 또는 runtime을 변경하면 desktop 1440px와 mobile 390px에서 해당 탐색, 표, diagram, deep link와 checkbox를 검증해야 한다. 개별 View 생성은 자료와 요청의 복잡도에 맞는 읽기·표시 검증을 적용하고 공통 tooling의 전체 회귀를 기계적으로 반복하지 않아야 한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#visual-docs-shell-template-style-script-또는-runtime을-변경하면-desktop-1440px와-mobile-390px에서-해당-탐색-표-diagram-deep-link와-checkbox를-검증해야-한다-개별-view-생성은-자료와-요청의-복잡도에-맞는-읽기표시-검증을-적용하고-공통-tooling의-전체-회귀를-기계적으로-반복하지-않아야-한다) | 5 | policy + pressure scenario |
| [공통 renderer의 provenance와 reading-route 변경은 desktop 1440px와 mobile 390px 및 관련 검증 항목으로 확인해야 한다. 이후 개별 View에서는 해당 자료의 읽기 품질을 확인하되 변경되지 않은 공통 구현의 전체 회귀는 반복하지 않아야 한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#공통-renderer의-provenance와-reading-route-변경은-desktop-1440px와-mobile-390px-및-관련-검증-항목으로-확인해야-한다-이후-개별-view에서는-해당-자료의-읽기-품질을-확인하되-변경되지-않은-공통-구현의-전체-회귀는-반복하지-않아야-한다) | 5 | policy + pressure scenario |
| [Visual Docs tooling 변경 fixture는 desktop 1440px와 mobile 390px에서 숨겨진 상세 선택, 빠른 탐색, deep link, checkbox persistence, diagram, table과 print의 필요한 상태를 통과한다. 유효한 Mermaid에는 표시된 오류가 없고 개별 View 생성 fixture도 요청 범위의 읽기·표시 확인을 수행한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#visual-docs-tooling-변경-fixture는-desktop-1440px와-mobile-390px에서-숨겨진-상세-선택-빠른-탐색-deep-link-checkbox-persistence-diagram-table과-print의-필요한-상태를-통과한다-유효한-mermaid에는-표시된-오류가-없고-개별-view-생성-fixture도-요청-범위의-읽기표시-확인을-수행한다) | 5 | policy + pressure scenario |
| [Visual Docs tooling fixture에 Markdown source와 View Context를 입력하면 Semantic IR, validated Presentation Plan, source manifest와 profile-specific HTML이 만들어지고 unresolved source reference·수동 content fragment·source 밖 의미가 0개다. 개별 View 검증은 자료에 필요한 범위로 수행한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#visual-docs-tooling-fixture에-markdown-source와-view-context를-입력하면-semantic-ir-validated-presentation-plan-source-manifest와-profile-specific-html이-만들어지고-unresolved-source-reference수동-content-fragmentsource-밖-의미가-0개다-개별-view-검증은-자료에-필요한-범위로-수행한다) | 5 | policy + pressure scenario |
| [공통 provenance와 reading-route 구현을 검증하면 desktop 1440px와 mobile 390px의 탐색, 표, diagram, deep link와 checkbox가 동작하며 개별 View는 해당 자료의 읽기·표시를 확인하고 변경되지 않은 공통 회귀를 반복하지 않는다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#공통-provenance와-reading-route-구현을-검증하면-desktop-1440px와-mobile-390px의-탐색-표-diagram-deep-link와-checkbox가-동작하며-개별-view는-해당-자료의-읽기표시를-확인하고-변경되지-않은-공통-회귀를-반복하지-않는다) | 5 | policy + pressure scenario |
| [`writing-plans`는 실제 독립 단계에 맞는 Route 또는 Milestone으로 Task를 묶고 각 Task를 하나의 primary Route에 배정해야 한다. 큰 계획에서는 6~10개 묶음을 가독성 지침으로 사용할 수 있지만 개수를 맞추기 위해 단계를 만들지 않아야 한다.](../../specs/review-viewer-lifecycle/plan-context-and-statement-traceability.md#writing-plans는-실제-독립-단계에-맞는-route-또는-milestone으로-task를-묶고-각-task를-하나의-primary-route에-배정해야-한다-큰-계획에서는-610개-묶음을-가독성-지침으로-사용할-수-있지만-개수를-맞추기-위해-단계를-만들지-않아야-한다) | 5 | policy + pressure scenario |
| [`writing-plans`는 목표와 완료 상태, Related Specs, Task별 산출물·파일 경계·의존성·Interface·검증·재개 조건과 실제 승인 지점을 명확히 해야 한다. Runtime 책임, 데이터 흐름, 확장 지점과 diagram은 작업에 필요한 경우만 포함하고 구현 코드 전체를 미리 작성하거나 반복하지 않아야 한다. 조사 Task는 구체적인 질문과 종료 증거를 가져야 한다.](../../specs/review-viewer-lifecycle/plan-context-and-statement-traceability.md#writing-plans는-목표와-완료-상태-related-specs-task별-산출물파일-경계의존성interface검증재개-조건과-실제-승인-지점을-명확히-해야-한다-runtime-책임-데이터-흐름-확장-지점과-diagram은-작업에-필요한-경우만-포함하고-구현-코드-전체를-미리-작성하거나-반복하지-않아야-한다-조사-task는-구체적인-질문과-종료-증거를-가져야-한다) | 5 | policy + pressure scenario |
| [`writing-plans`는 Canonical verification set에서 작업에 필요한 범위를 명시해야 한다. 새 계약·미구현 baseline의 전체 구현은 전체 항목을, 구현된 baseline의 부분 변경·복원은 직접·간접 영향 항목을 Task의 Governing statements와 coverage table에 연결하고 나머지 계약의 회귀 보존 근거를 기록해야 한다.](../../specs/review-viewer-lifecycle/plan-context-and-statement-traceability.md#writing-plans는-canonical-verification-set에서-작업에-필요한-범위를-명시해야-한다-새-계약미구현-baseline의-전체-구현은-전체-항목을-구현된-baseline의-부분-변경복원은-직접간접-영향-항목을-task의-governing-statements와-coverage-table에-연결하고-나머지-계약의-회귀-보존-근거를-기록해야-한다) | 5 | policy + pressure scenario |
| [복잡한 plan은 검토에 필요한 관계가 source에 있을 때 Task dependency, runtime 또는 transaction, 확장 구조 관점의 diagram을 포함해야 한다. 관계가 없는 관점은 만들지 않고 표나 짧은 설명을 사용해야 한다.](../../specs/review-viewer-lifecycle/plan-context-and-statement-traceability.md#복잡한-plan은-검토에-필요한-관계가-source에-있을-때-task-dependency-runtime-또는-transaction-확장-구조-관점의-diagram을-포함해야-한다-관계가-없는-관점은-만들지-않고-표나-짧은-설명을-사용해야-한다) | 5 | policy + pressure scenario |
| [`writing-plans`는 큰 Task 집합을 하나의 평면 diagram으로 연결하지 않고 실제 단계에 맞는 의미 있는 Route로 묶은 뒤 필요한 Task 관계를 보여줘야 한다.](../../specs/review-viewer-lifecycle/plan-context-and-statement-traceability.md#writing-plans는-큰-task-집합을-하나의-평면-diagram으로-연결하지-않고-실제-단계에-맞는-의미-있는-route로-묶은-뒤-필요한-task-관계를-보여줘야-한다) | 5 | policy + pressure scenario |
| [복잡한 plan fixture에는 독립 경로, 선택적인 Related Specs, 변경 범위에 맞는 Governing statements, 실행 가능한 Task와 검증, 실제 단계의 Route와 checkpoint가 존재하며 불필요한 전체 구현 코드나 관계가 없는 diagram이 추가되지 않는다.](../../specs/review-viewer-lifecycle/plan-context-and-statement-traceability.md#복잡한-plan-fixture에는-독립-경로-선택적인-related-specs-변경-범위에-맞는-governing-statements-실행-가능한-task와-검증-실제-단계의-route와-checkpoint가-존재하며-불필요한-전체-구현-코드나-관계가-없는-diagram이-추가되지-않는다) | 5 | policy + pressure scenario |
| [Source 변경만으로 완료된 local View나 tracked Project Handbook을 자동 갱신하지 않아야 한다. 진행 중인 명시적 시각 문서 요청을 완성하기 위한 검증·수정·재생성은 같은 요청 안에서 수행할 수 있고, 완료 후 새 갱신에는 명시적 사용자 의도가 필요해야 한다.](../../specs/semantic-spec-bundles/lifecycle-consumers-and-bundle-replacement.md#source-변경만으로-완료된-local-view나-tracked-project-handbook을-자동-갱신하지-않아야-한다-진행-중인-명시적-시각-문서-요청을-완성하기-위한-검증수정재생성은-같은-요청-안에서-수행할-수-있고-완료-후-새-갱신에는-명시적-사용자-의도가-필요해야-한다) | 5 | policy + pressure scenario |
| [모든 구현 완료 주장은 fresh command-level verification을 필요로 해야 한다. 승인된 Spec Delta를 구현한 작업은 bundle의 Canonical verification set을 full text와 member path로 식별해 실제 동작으로 검증해야 한다. Acceptance statement가 하나 이상 있으면 해당 Acceptance statement를 사용하고, 없으면 Requirement statement를 사용해야 한다. Quick 작업은 원래 reproduction, focused test, build·lint 중 주장에 맞는 증거만 요구하고 spec status 전환이나 전체 Canonical verification set 순회를 요구하지 않아야 한다.](../../specs/canonical-spec-workflow/verification-and-durable-authority.md#모든-구현-완료-주장은-fresh-command-level-verification을-필요로-해야-한다-승인된-spec-delta를-구현한-작업은-bundle의-canonical-verification-set을-full-text와-member-path로-식별해-실제-동작으로-검증해야-한다-acceptance-statement가-하나-이상-있으면-해당-acceptance-statement를-사용하고-없으면-requirement-statement를-사용해야-한다-quick-작업은-원래-reproduction-focused-test-buildlint-중-주장에-맞는-증거만-요구하고-spec-status-전환이나-전체-canonical-verification-set-순회를-요구하지-않아야-한다) | 6 | full regression |

## Progress History

- 2026-09-06: 점검 보고서 승인에 따라 작업 시작. baseline `d69b8e7`, working tree clean. Route: impact=yes, complexity=high.

- Task 1: root, frontier, 25 exact statement 변경과 anchor 동기화; writer transaction exit 0.
- Task 2: balanced, subagent, parallel_group=viewer-restoration; root diff 확인 및 IR 16 tests fresh PASS.
- Task 3/4: balanced, subagent, 쓰기 소유권 분리; worker 결과 수령, root 통합 검증 진행.
- Task 5: root, frontier; 스킬·정본·reference·정책 검사 동기화, 새 agent 시나리오 진행.

- Task 3/4: root가 diff와 renderer/runtime를 검토하고 Visual Docs Python 62개·browser 13개 fresh PASS. 실제 한국어 상세 SVG 3개·오류 0, desktop/mobile 읽기 확인.
- Task 5: 14개 skill 정리. 실제 Quick fixture와 5개 pressure scenario 검토, extension Handoff 잔여 충돌 수정 후 재검토 PASS.
- Task 6: Python 총 142개, browser 13개, shell 10개, Mermaid/freshness/build 검사 PASS. 검증 기록: `docs/evidence/forge-purpose-alignment.md`.
