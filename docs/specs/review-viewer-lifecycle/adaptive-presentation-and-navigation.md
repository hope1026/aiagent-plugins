# 적응형 표현과 탐색

## Requirements

### 복잡도 점수는 bundle 전체의 Requirement 8개 초과, Acceptance Criterion 8개 초과, Mermaid 2개 이상, 데이터·Interface 표 2개 이상, 여러 member·subsystem·actor·Place·상태 전이, bundle 200줄 초과, 미해결 clarification 또는 change history 다수 항목에 각각 1점을 부여하되 Review Viewer 자동 생성 조건으로 사용하지 않아야 한다.

### bundle 복잡도 점수가 2 이상이면 Forge는 Review Viewer가 검토에 도움이 될 수 있음을 사용자에게 알리고 필요하면 명시적으로 요청할 수 있다고 안내하되, Review Viewer를 자동 생성하지 않아야 한다.

### Build command는 `--offline`, `--mode spec|plan`, `--locale en|ko`, `--review-id`를 지원해야 한다. spec mode는 current spec과 선택적인 comparison source를 받고, plan mode는 primary source set과 plan이 선언한 Related Specs context를 결정적으로 해석하며, 기본 locale은 `en`으로 유지해야 한다.

### `--locale ko`에서는 tab을 `개요`, `요구사항`, `흐름`, `데이터와 인터페이스`, `승인 기준`, `변경 이력`으로 표시해야 한다.

### Review Viewer는 title·source·freshness·navigation의 stable shell landmark를 유지하되 content panel의 수, ID, 순서와 layout을 6개 고정 panel로 제한하지 않아야 한다. Presentation Plan이 선택한 component composition은 동일 source라도 문서 종류와 검토 목적에 따라 달라질 수 있어야 한다.

### Review Viewer는 원문 상세를 처음부터 펼치지 않고 요약, 시각 흐름, 상세 source, acceptance evidence 순서로 배치해야 한다.

### spec mode의 current·comparison statement deep link와 plan mode의 context statement·Task·Step deep link는 bundle path·member path·exact heading에서 계산한 내부 key를 포함해 DOM ID 충돌 없이 해당 Review Viewer의 panel과 대상을 열어야 한다. 화면에는 full statement와 path를 표시해야 한다.

### Acceptance Criterion 검토 checkbox와 Step 검토 checkbox는 bundle·member·statement 기반 내부 namespace와 종류를 구분해 localStorage에 저장해야 하며 내부 key를 표시하거나 제품 검증 PASS/FAIL로 표시하지 않아야 한다.

### Review Viewer가 source에서 계산한 Route, Task dependency, explicit statement coverage mapping 도식은 `Derived view`로 명시해야 한다.

### derived diagram은 Task 번호, 명시된 Route membership, 명시된 dependency, source-qualified full-statement mapping처럼 selected source에서 기계적으로 계산 가능한 정보만 포함해야 한다.

### Review Viewer는 source에 없는 새로운 런타임 책임, transaction 순서, 상태 전이 또는 설계 결정을 derived diagram에 추가하지 않아야 한다.

### 모든 diagram 앞에는 제목, 이 화면에서 확인할 것, 한 문장의 읽는 법을 표시해야 한다.

### 넓은 sequence diagram 앞에는 actor별 runtime 책임을 요약한 표를 먼저 제공해야 한다.

### 넓은 Mermaid diagram은 독립 가로 스크롤 wrapper 안에 표시하고 SVG를 viewport 폭에 맞춰 무조건 축소하지 않아야 한다.

### sequence diagram과 넓은 dependency diagram에는 읽을 수 있는 최소 폭을 적용해야 한다.

### 각 diagram은 title, description, `aria-label` 또는 동등한 접근성 연결을 가져야 한다.

### Mermaid parse나 render가 실패하면 오류 요약, 가능한 오류 line·column, 원문 source를 함께 표시해야 한다.

### HTML shell은 inline favicon을 포함해 로컬 브라우저 검증에서 favicon 404를 만들지 않아야 한다.

### 집계 수치와 상태 표는 tabular number를 사용해야 한다.

### 넓은 표는 독립 가로 스크롤 wrapper를 사용해 문서 전체 viewport 폭을 확장하지 않아야 한다.

### Review Viewer shell, template, style, script 또는 runtime 동작을 변경할 때는 desktop 1440px와 mobile 390px에서 tab, 표, diagram, deep link, checkbox를 검증해야 하지만, 고정 shell로 개별 `view.html`을 생성할 때는 이 검증을 반복하지 않아야 한다.

### mobile에서 sequence diagram 글자를 읽기 어려우면 책임 요약표 또는 세로 flowchart를 먼저 제공하고 원본 diagram은 가로 스크롤로 유지해야 한다.

### 승인된 component grammar와 profile로 개별 Review Viewer를 생성하는 작업은 UI 디자인 skill을 적용하지 않아야 하며, Review Viewer shell·component·profile·style·planner·interaction tooling을 변경할 때만 `web-app-design`을 적용해야 한다.

### agent는 수동 HTML content fragment, 문서별 HTML template, CSS 또는 script를 Review Viewer 입력으로 작성하지 않아야 한다. 문서별 판단이 필요하면 제한된 Presentation Plan만 선택하거나 생성해야 한다.

### Review Viewer의 Signature는 장식이나 고정 component 이름이 아니라 selected source와 intent에 맞는 state map, interface contract, dependency route, exception matrix, Acceptance Criterion coverage 같은 primary reading structure에서 만들어야 한다.

### diagram 추가는 제목, 읽는 법, mobile 대체 요약표와 한 묶음으로 검토해야 한다.

### Review Viewer의 각 content component 제목은 스캔 가능한 짧은 명사형 label을 사용하고, 사용자가 그 component에서 답을 찾을 질문은 제목 바로 아래의 종속 orientation 문장으로 표시해야 한다. 같은 component도 Presentation Plan의 intent에 맞는 orientation을 사용해야 한다.

### Review Viewer copy는 이 화면에서 확인할 것을 먼저 말하고, 번역해도 의미가 유지되는 label은 사용자 언어로 쓰며 고유 API·service·schema 이름만 원문으로 유지해야 한다.

### Review Viewer copy의 순서는 Presentation Plan이 primary review question에 맞춰 결정하되 첫 화면에서 핵심 판단 자료를 제시하고, source detail과 provenance로 추적 가능한 읽기 경로를 제공하며 각 diagram 앞에 한 문장의 읽는 법을 표시해야 한다.

### Review Viewer builder는 selected Markdown source를 Semantic IR로 해석하고, View Context로 Presentation Plan을 선택한 뒤 공통 component grammar로 HTML과 manifest를 생성해야 한다. Agent가 작성한 HTML content fragment나 source 밖의 보충 문장을 입력으로 요구하지 않아야 한다.

### builder는 해당 Review Viewer가 렌더링할 source Mermaid와 derived diagram을 합쳐 하나 이상 포함할 때만 Mermaid runtime asset을 embed하거나 CDN loader를 출력해야 한다. Diagram이 없는 snapshot은 runtime을 생략해야 하며, 생략 여부는 selected source bytes와 build option에서만 결정적으로 계산해야 한다. `--offline` snapshot은 runtime을 생략한 경우에도 외부 network 없이 열려야 한다.

### Review Viewer의 Overview panel은 source별 집계를 스캔 가능한 요약 지표로 먼저 제시하고 상세 집계 표를 그 아래에 유지해야 하며, 두 표시는 structured parser가 고정한 같은 집계 기준에서 계산해야 한다.

### 공통 renderer의 provenance와 reading-route 변경은 desktop 1440px와 mobile 390px 및 관련 Acceptance Criterion을 검증하되 개별 `view.html` 생성에 post-build 검증을 다시 도입하지 않아야 한다.

### View Context는 mode, document kind와 subtype, user intent, audience, locale, comparison·context source role과 export mode를 가져야 한다. `intent`는 `review`, `approval`, `implementation`, `comparison`, `execution`, `status` 중 하나여야 한다.

### 사용자의 Viewer 요청에 intent나 audience가 명시되면 그대로 사용하고, 생략되면 spec은 `review`, plan은 `execution`, audience는 `mixed`를 사용해야 한다. Default 선택은 HTML 생성 권한을 만들지 않아야 한다.

### Presentation Plan은 profile ID, primary question, ordered component instance, source entity·block reference, orientation과 disclosure policy만 가진 제한된 data contract여야 하며 HTML, CSS, JavaScript와 source 밖 본문을 포함하지 않아야 한다.

### Renderer는 최소한 `generic`, `spec.workflow`, `spec.api`, `spec.architecture`, `spec.policy`, `spec.migration`, `plan.execution`, `plan.status`, `comparison` profile을 제공해야 한다. 새 profile은 공통 component를 조합하고 문서별 template를 복사하지 않아야 한다.

### 공통 component grammar는 summary, outline, prose detail, metadata, state map, sequence, interface·schema table, decision·exception matrix, relation graph, route·dependency map, progress, Requirement·Acceptance Criterion coverage, provenance와 source detail을 제공해야 한다.

### 문서 종류와 intent에 따라 primary component, reading order, navigation, summary density와 diagram·table 비중은 달라질 수 있지만 typography role, palette, spacing, focus, freshness, provenance, deep link, overflow와 responsive interaction은 공통 visual system을 따라야 한다.

### Profile이 source block이나 entity를 사용하지 않으면 renderer는 이를 source detail 또는 generic detail component에 포함해야 하며, Presentation Plan은 selected source content coverage 100%를 만족해야 한다.

### 알려진 profile과 rule로 충분하지 않은 source에서는 agent가 Presentation Plan을 제안할 수 있지만 HTML을 직접 생성하지 않아야 한다. 제안 plan은 schema, allowed component, source reference, coverage와 no-new-meaning validation을 통과한 뒤에만 renderer 입력이 될 수 있어야 한다.

### 같은 selected source bytes, View Context, accepted Presentation Plan, renderer version, locale와 fixed generated timestamp는 byte-for-byte 같은 HTML을 만들어야 한다.

### Presentation Plan validator는 unknown profile·component, dangling source reference, duplicate exclusive block, uncovered source block, source 밖 prose, unsupported intent와 component contract 위반을 사람이 수정할 수 있는 진단으로 거부해야 한다.

### 같은 source는 intent만 바꿔 approval·implementation 또는 execution·status Review Viewer를 각각 생성할 수 있어야 하며 두 View는 source manifest와 provenance를 공유하면서 다른 primary composition을 가질 수 있어야 한다.

### `generic` fallback은 unknown kind·subtype, sparse source, profile selection 실패에서도 metadata, outline, 모든 source block, provenance와 freshness를 읽을 수 있게 표시하고 HTML 생성 자체를 실패시키지 않아야 한다.

### shell·component·profile·planner 변경의 UI 검증은 desktop 1440px와 mobile 390px에서 각 profile의 typical·empty·long·invalid diagram 상태, keyboard focus, navigation, disclosure, table·diagram overflow와 stable shell geometry를 포함해야 한다.

## Acceptance Criteria

### 복잡도 1점과 2점인 문서는 모두 Markdown source 검토 경로를 기본으로 사용하고, 2점인 문서에서는 Review Viewer의 효용만 안내하며, 사용자가 시각화를 명시적으로 요청한 문서만 Review Viewer 경로를 사용한다.

검증하는 요구사항:

- [Forge는 복잡도와 관계없이 Markdown을 source 검토의 기본 경로로 사용하고, Review Viewer는 요청형 보조 검토 화면으로만 사용해야 한다.](human-readable-review-viewer.md#forge는-복잡도와-관계없이-markdown을-source-검토의-기본-경로로-사용하고-review-viewer는-요청형-보조-검토-화면으로만-사용해야-한다)
- [복잡도 점수는 bundle 전체의 Requirement 8개 초과, Acceptance Criterion 8개 초과, Mermaid 2개 이상, 데이터·Interface 표 2개 이상, 여러 member·subsystem·actor·Place·상태 전이, bundle 200줄 초과, 미해결 clarification 또는 change history 다수 항목에 각각 1점을 부여하되 Review Viewer 자동 생성 조건으로 사용하지 않아야 한다.](adaptive-presentation-and-navigation.md#복잡도-점수는-bundle-전체의-requirement-8개-초과-acceptance-criterion-8개-초과-mermaid-2개-이상-데이터interface-표-2개-이상-여러-membersubsystemactorplace상태-전이-bundle-200줄-초과-미해결-clarification-또는-change-history-다수-항목에-각각-1점을-부여하되-review-viewer-자동-생성-조건으로-사용하지-않아야-한다)
- [bundle 복잡도 점수가 2 이상이면 Forge는 Review Viewer가 검토에 도움이 될 수 있음을 사용자에게 알리고 필요하면 명시적으로 요청할 수 있다고 안내하되, Review Viewer를 자동 생성하지 않아야 한다.](adaptive-presentation-and-navigation.md#bundle-복잡도-점수가-2-이상이면-forge는-review-viewer가-검토에-도움이-될-수-있음을-사용자에게-알리고-필요하면-명시적으로-요청할-수-있다고-안내하되-review-viewer를-자동-생성하지-않아야-한다)
- [사용자가 현재 spec이나 plan의 시각화 또는 Review Viewer 생성·갱신을 명시적으로 요청한 경우에만 Forge는 복잡도 점수와 관계없이 해당 Review Viewer를 생성하거나 갱신해야 한다.](human-readable-review-viewer.md#사용자가-현재-spec이나-plan의-시각화-또는-review-viewer-생성갱신을-명시적으로-요청한-경우에만-forge는-복잡도-점수와-관계없이-해당-review-viewer를-생성하거나-갱신해야-한다)

### `review-viewer`로 독립된 spec fixture와 plan fixture를 각각 `spec`, `plan` mode, `--locale ko`, 서로 다른 review ID로 build하면 `.forge/reviews/<review-id>/view.html`이 생성되고 tab label이 한국어로 표시되며 `combined` mode 요청은 거부된다.

검증하는 요구사항:

- [`review-viewer` skill은 사용자에게 Review Viewer로 소개하고, 서로 독립적인 `spec`과 `plan` 두 mode만 지원해야 한다.](human-readable-review-viewer.md#review-viewer-skill은-사용자에게-review-viewer로-소개하고-서로-독립적인-spec과-plan-두-mode만-지원해야-한다)
- [`spec` mode에서는 현재 valid Spec Bundle 전체를 primary source of truth로 사용하고, 사용자가 지정한 0개 이상의 comparison bundle을 비권위 비교 자료로 읽되 모든 내용에 bundle·member source role과 provenance를 표시해야 한다.](source-selection-and-freshness.md#spec-mode에서는-현재-valid-spec-bundle-전체를-primary-source-of-truth로-사용하고-사용자가-지정한-0개-이상의-comparison-bundle을-비권위-비교-자료로-읽되-모든-내용에-bundlemember-source-role과-provenance를-표시해야-한다)
- [`plan` mode에서는 `plan.md`와 존재하는 경우 같은 디렉터리의 `progress.md`, `tasks/*.md`를 primary source set으로 사용하고, plan의 `Related Specs` bundle 0개 이상을 제품 요구사항을 설명하는 context source로 읽되 plan source와 병합하거나 동일한 ownership으로 표시하지 않아야 한다.](source-selection-and-freshness.md#plan-mode에서는-planmd와-존재하는-경우-같은-디렉터리의-progressmd-tasksmd를-primary-source-set으로-사용하고-plan의-related-specs-bundle-0개-이상을-제품-요구사항을-설명하는-context-source로-읽되-plan-source와-병합하거나-동일한-ownership으로-표시하지-않아야-한다)
- [`spec`과 `plan` mode 출력은 모두 `.forge/reviews/<review-id>/view.html`을 사용하고, 동일한 `review-id`의 갱신은 사용자의 명시적 요청이 있을 때만 허용해야 한다.](human-readable-review-viewer.md#spec과-plan-mode-출력은-모두-forgereviewsreview-idviewhtml을-사용하고-동일한-review-id의-갱신은-사용자의-명시적-요청이-있을-때만-허용해야-한다)
- [Build command는 `--offline`, `--mode spec|plan`, `--locale en|ko`, `--review-id`를 지원해야 한다. spec mode는 current spec과 선택적인 comparison source를 받고, plan mode는 primary source set과 plan이 선언한 Related Specs context를 결정적으로 해석하며, 기본 locale은 `en`으로 유지해야 한다.](adaptive-presentation-and-navigation.md#build-command는-offline-mode-specplan-locale-enko-review-id를-지원해야-한다-spec-mode는-current-spec과-선택적인-comparison-source를-받고-plan-mode는-primary-source-set과-plan이-선언한-related-specs-context를-결정적으로-해석하며-기본-locale은-en으로-유지해야-한다)
- [`--locale ko`에서는 tab을 `개요`, `요구사항`, `흐름`, `데이터와 인터페이스`, `승인 기준`, `변경 이력`으로 표시해야 한다.](adaptive-presentation-and-navigation.md#locale-ko에서는-tab을-개요-요구사항-흐름-데이터와-인터페이스-승인-기준-변경-이력으로-표시해야-한다)

### spec mode와 plan mode에서 source Mermaid와 derived diagram을 표시하면 `Current spec source`, `Comparison source`, `Plan source`, `Related spec context`, `Derived view`가 해당 source가 존재하는 범위에서 구분되고 path가 표시되며 derived node·edge는 selected source에 명시된 관계만 포함한다.

검증하는 요구사항:

- [current bundle과 comparison bundle의 Mermaid는 source text를 byte-for-byte 변경하지 않고 재사용하며 각각 `Current spec source` 또는 `Comparison source`, bundle·member H1과 path를 표시해야 한다.](source-selection-and-freshness.md#current-bundle과-comparison-bundle의-mermaid는-source-text를-byte-for-byte-변경하지-않고-재사용하며-각각-current-spec-source-또는-comparison-source-bundlemember-h1과-path를-표시해야-한다)
- [plan primary set과 Related Specs bundle context에 작성된 Mermaid는 각 source에서 그대로 가져오고 각각 `Plan source` 또는 `Related spec context`, bundle·member H1과 path를 표시해야 한다.](source-selection-and-freshness.md#plan-primary-set과-related-specs-bundle-context에-작성된-mermaid는-각-source에서-그대로-가져오고-각각-plan-source-또는-related-spec-context-bundlemember-h1과-path를-표시해야-한다)
- [Review Viewer가 source에서 계산한 Route, Task dependency, explicit statement coverage mapping 도식은 `Derived view`로 명시해야 한다.](adaptive-presentation-and-navigation.md#review-viewer가-source에서-계산한-route-task-dependency-explicit-statement-coverage-mapping-도식은-derived-view로-명시해야-한다)
- [derived diagram은 Task 번호, 명시된 Route membership, 명시된 dependency, source-qualified full-statement mapping처럼 selected source에서 기계적으로 계산 가능한 정보만 포함해야 한다.](adaptive-presentation-and-navigation.md#derived-diagram은-task-번호-명시된-route-membership-명시된-dependency-source-qualified-full-statement-mapping처럼-selected-source에서-기계적으로-계산-가능한-정보만-포함해야-한다)
- [Review Viewer는 source에 없는 새로운 런타임 책임, transaction 순서, 상태 전이 또는 설계 결정을 derived diagram에 추가하지 않아야 한다.](adaptive-presentation-and-navigation.md#review-viewer는-source에-없는-새로운-런타임-책임-transaction-순서-상태-전이-또는-설계-결정을-derived-diagram에-추가하지-않아야-한다)

### 모든 diagram 앞에 제목, 이 화면에서 확인할 것, 한 문장의 읽는 법이 있고 넓은 sequence diagram 앞에는 runtime 책임 요약표가 먼저 표시된다.

검증하는 요구사항:

- [모든 diagram 앞에는 제목, 이 화면에서 확인할 것, 한 문장의 읽는 법을 표시해야 한다.](adaptive-presentation-and-navigation.md#모든-diagram-앞에는-제목-이-화면에서-확인할-것-한-문장의-읽는-법을-표시해야-한다)
- [넓은 sequence diagram 앞에는 actor별 runtime 책임을 요약한 표를 먼저 제공해야 한다.](adaptive-presentation-and-navigation.md#넓은-sequence-diagram-앞에는-actor별-runtime-책임을-요약한-표를-먼저-제공해야-한다)
- [Review Viewer의 각 content component 제목은 스캔 가능한 짧은 명사형 label을 사용하고, 사용자가 그 component에서 답을 찾을 질문은 제목 바로 아래의 종속 orientation 문장으로 표시해야 한다. 같은 component도 Presentation Plan의 intent에 맞는 orientation을 사용해야 한다.](adaptive-presentation-and-navigation.md#review-viewer의-각-content-component-제목은-스캔-가능한-짧은-명사형-label을-사용하고-사용자가-그-component에서-답을-찾을-질문은-제목-바로-아래의-종속-orientation-문장으로-표시해야-한다-같은-component도-presentation-plan의-intent에-맞는-orientation을-사용해야-한다)
- [Review Viewer copy는 이 화면에서 확인할 것을 먼저 말하고, 번역해도 의미가 유지되는 label은 사용자 언어로 쓰며 고유 API·service·schema 이름만 원문으로 유지해야 한다.](adaptive-presentation-and-navigation.md#review-viewer-copy는-이-화면에서-확인할-것을-먼저-말하고-번역해도-의미가-유지되는-label은-사용자-언어로-쓰며-고유-apiserviceschema-이름만-원문으로-유지해야-한다)
- [Review Viewer copy의 순서는 Presentation Plan이 primary review question에 맞춰 결정하되 첫 화면에서 핵심 판단 자료를 제시하고, source detail과 provenance로 추적 가능한 읽기 경로를 제공하며 각 diagram 앞에 한 문장의 읽는 법을 표시해야 한다.](adaptive-presentation-and-navigation.md#review-viewer-copy의-순서는-presentation-plan이-primary-review-question에-맞춰-결정하되-첫-화면에서-핵심-판단-자료를-제시하고-source-detail과-provenance로-추적-가능한-읽기-경로를-제공하며-각-diagram-앞에-한-문장의-읽는-법을-표시해야-한다)

### 390px viewport에서 넓은 sequence diagram과 표가 문서 viewport를 확장하지 않고 각 wrapper 안에서 가로 스크롤되며 책임 요약표를 먼저 읽을 수 있다.

검증하는 요구사항:

- [넓은 Mermaid diagram은 독립 가로 스크롤 wrapper 안에 표시하고 SVG를 viewport 폭에 맞춰 무조건 축소하지 않아야 한다.](adaptive-presentation-and-navigation.md#넓은-mermaid-diagram은-독립-가로-스크롤-wrapper-안에-표시하고-svg를-viewport-폭에-맞춰-무조건-축소하지-않아야-한다)
- [sequence diagram과 넓은 dependency diagram에는 읽을 수 있는 최소 폭을 적용해야 한다.](adaptive-presentation-and-navigation.md#sequence-diagram과-넓은-dependency-diagram에는-읽을-수-있는-최소-폭을-적용해야-한다)
- [넓은 표는 독립 가로 스크롤 wrapper를 사용해 문서 전체 viewport 폭을 확장하지 않아야 한다.](adaptive-presentation-and-navigation.md#넓은-표는-독립-가로-스크롤-wrapper를-사용해-문서-전체-viewport-폭을-확장하지-않아야-한다)
- [Review Viewer shell, template, style, script 또는 runtime 동작을 변경할 때는 desktop 1440px와 mobile 390px에서 tab, 표, diagram, deep link, checkbox를 검증해야 하지만, 고정 shell로 개별 `view.html`을 생성할 때는 이 검증을 반복하지 않아야 한다.](adaptive-presentation-and-navigation.md#review-viewer-shell-template-style-script-또는-runtime-동작을-변경할-때는-desktop-1440px와-mobile-390px에서-tab-표-diagram-deep-link-checkbox를-검증해야-하지만-고정-shell로-개별-viewhtml을-생성할-때는-이-검증을-반복하지-않아야-한다)
- [mobile에서 sequence diagram 글자를 읽기 어려우면 책임 요약표 또는 세로 flowchart를 먼저 제공하고 원본 diagram은 가로 스크롤로 유지해야 한다.](adaptive-presentation-and-navigation.md#mobile에서-sequence-diagram-글자를-읽기-어려우면-책임-요약표-또는-세로-flowchart를-먼저-제공하고-원본-diagram은-가로-스크롤로-유지해야-한다)

### diagram 접근성 이름, inline favicon, tabular number가 DOM과 computed style에 존재하고 favicon 404가 발생하지 않는다.

검증하는 요구사항:

- [각 diagram은 title, description, `aria-label` 또는 동등한 접근성 연결을 가져야 한다.](adaptive-presentation-and-navigation.md#각-diagram은-title-description-aria-label-또는-동등한-접근성-연결을-가져야-한다)
- [Mermaid parse나 render가 실패하면 오류 요약, 가능한 오류 line·column, 원문 source를 함께 표시해야 한다.](adaptive-presentation-and-navigation.md#mermaid-parse나-render가-실패하면-오류-요약-가능한-오류-linecolumn-원문-source를-함께-표시해야-한다)
- [HTML shell은 inline favicon을 포함해 로컬 브라우저 검증에서 favicon 404를 만들지 않아야 한다.](adaptive-presentation-and-navigation.md#html-shell은-inline-favicon을-포함해-로컬-브라우저-검증에서-favicon-404를-만들지-않아야-한다)
- [집계 수치와 상태 표는 tabular number를 사용해야 한다.](adaptive-presentation-and-navigation.md#집계-수치와-상태-표는-tabular-number를-사용해야-한다)

### 잘못된 Mermaid fixture를 열면 다른 panel은 정상 동작하고 오류 diagram에는 오류 요약, 가능한 line·column, 원문 source가 표시된다.

검증하는 요구사항:

- [Mermaid parse나 render가 실패하면 오류 요약, 가능한 오류 line·column, 원문 source를 함께 표시해야 한다.](adaptive-presentation-and-navigation.md#mermaid-parse나-render가-실패하면-오류-요약-가능한-오류-linecolumn-원문-source를-함께-표시해야-한다)

### current·comparison·context bundle에 같은 statement가 있고 plan의 Task·Step이 함께 있는 Review Viewer에서 deep link와 검토 checkbox를 변경하고 page를 reload하면 bundle·member·statement namespace별 target과 checkbox 상태가 충돌 없이 복원되며 화면에는 full statement와 path만 표시된다.

검증하는 요구사항:

- [spec mode의 current·comparison statement deep link와 plan mode의 context statement·Task·Step deep link는 bundle path·member path·exact heading에서 계산한 내부 key를 포함해 DOM ID 충돌 없이 해당 Review Viewer의 panel과 대상을 열어야 한다. 화면에는 full statement와 path를 표시해야 한다.](adaptive-presentation-and-navigation.md#spec-mode의-currentcomparison-statement-deep-link와-plan-mode의-context-statementtaskstep-deep-link는-bundle-pathmember-pathexact-heading에서-계산한-내부-key를-포함해-dom-id-충돌-없이-해당-review-viewer의-panel과-대상을-열어야-한다-화면에는-full-statement와-path를-표시해야-한다)
- [Acceptance Criterion 검토 checkbox와 Step 검토 checkbox는 bundle·member·statement 기반 내부 namespace와 종류를 구분해 localStorage에 저장해야 하며 내부 key를 표시하거나 제품 검증 PASS/FAIL로 표시하지 않아야 한다.](adaptive-presentation-and-navigation.md#acceptance-criterion-검토-checkbox와-step-검토-checkbox는-bundlememberstatement-기반-내부-namespace와-종류를-구분해-localstorage에-저장해야-하며-내부-key를-표시하거나-제품-검증-passfail로-표시하지-않아야-한다)

### 승인된 profile로 개별 Review Viewer를 생성할 때 UI 디자인 skill, 수동 HTML fragment, 문서별 template·CSS·script를 사용하지 않고 Semantic IR→Presentation Plan→component renderer가 HTML을 생성한다. Shell·component·profile·planner tooling 변경에만 `web-app-design`을 적용한다.

검증하는 요구사항:

- [승인된 component grammar와 profile로 개별 Review Viewer를 생성하는 작업은 UI 디자인 skill을 적용하지 않아야 하며, Review Viewer shell·component·profile·style·planner·interaction tooling을 변경할 때만 `web-app-design`을 적용해야 한다.](adaptive-presentation-and-navigation.md#승인된-component-grammar와-profile로-개별-review-viewer를-생성하는-작업은-ui-디자인-skill을-적용하지-않아야-하며-review-viewer-shellcomponentprofilestyleplannerinteraction-tooling을-변경할-때만-web-app-design을-적용해야-한다)
- [agent는 수동 HTML content fragment, 문서별 HTML template, CSS 또는 script를 Review Viewer 입력으로 작성하지 않아야 한다. 문서별 판단이 필요하면 제한된 Presentation Plan만 선택하거나 생성해야 한다.](adaptive-presentation-and-navigation.md#agent는-수동-html-content-fragment-문서별-html-template-css-또는-script를-review-viewer-입력으로-작성하지-않아야-한다-문서별-판단이-필요하면-제한된-presentation-plan만-선택하거나-생성해야-한다)
- [Review Viewer의 Signature는 장식이나 고정 component 이름이 아니라 selected source와 intent에 맞는 state map, interface contract, dependency route, exception matrix, Acceptance Criterion coverage 같은 primary reading structure에서 만들어야 한다.](adaptive-presentation-and-navigation.md#review-viewer의-signature는-장식이나-고정-component-이름이-아니라-selected-source와-intent에-맞는-state-map-interface-contract-dependency-route-exception-matrix-acceptance-criterion-coverage-같은-primary-reading-structure에서-만들어야-한다)
- [diagram 추가는 제목, 읽는 법, mobile 대체 요약표와 한 묶음으로 검토해야 한다.](adaptive-presentation-and-navigation.md#diagram-추가는-제목-읽는-법-mobile-대체-요약표와-한-묶음으로-검토해야-한다)
- [Review Viewer builder는 selected Markdown source를 Semantic IR로 해석하고, View Context로 Presentation Plan을 선택한 뒤 공통 component grammar로 HTML과 manifest를 생성해야 한다. Agent가 작성한 HTML content fragment나 source 밖의 보충 문장을 입력으로 요구하지 않아야 한다.](adaptive-presentation-and-navigation.md#review-viewer-builder는-selected-markdown-source를-semantic-ir로-해석하고-view-context로-presentation-plan을-선택한-뒤-공통-component-grammar로-html과-manifest를-생성해야-한다-agent가-작성한-html-content-fragment나-source-밖의-보충-문장을-입력으로-요구하지-않아야-한다)

### `.forge/reviews/<review-id>/view.html`의 CDN build와 `--offline` build가 모두 열리고 offline 파일에는 외부 Mermaid script 요청이 없으며 diagram이 렌더된다.

검증하는 요구사항:

- [`spec`과 `plan` mode 출력은 모두 `.forge/reviews/<review-id>/view.html`을 사용하고, 동일한 `review-id`의 갱신은 사용자의 명시적 요청이 있을 때만 허용해야 한다.](human-readable-review-viewer.md#spec과-plan-mode-출력은-모두-forgereviewsreview-idviewhtml을-사용하고-동일한-review-id의-갱신은-사용자의-명시적-요청이-있을-때만-허용해야-한다)
- [Build command는 `--offline`, `--mode spec|plan`, `--locale en|ko`, `--review-id`를 지원해야 한다. spec mode는 current spec과 선택적인 comparison source를 받고, plan mode는 primary source set과 plan이 선언한 Related Specs context를 결정적으로 해석하며, 기본 locale은 `en`으로 유지해야 한다.](adaptive-presentation-and-navigation.md#build-command는-offline-mode-specplan-locale-enko-review-id를-지원해야-한다-spec-mode는-current-spec과-선택적인-comparison-source를-받고-plan-mode는-primary-source-set과-plan이-선언한-related-specs-context를-결정적으로-해석하며-기본-locale은-en으로-유지해야-한다)

### plan mode의 execution과 status Viewer는 stable shell landmark와 source ownership을 공유하면서 서로 다른 primary component와 reading order를 가지며, 두 View 모두 plan source detail과 acceptance evidence로 이동할 수 있다.

검증하는 요구사항:

- [Review Viewer는 title·source·freshness·navigation의 stable shell landmark를 유지하되 content panel의 수, ID, 순서와 layout을 6개 고정 panel로 제한하지 않아야 한다. Presentation Plan이 선택한 component composition은 동일 source라도 문서 종류와 검토 목적에 따라 달라질 수 있어야 한다.](adaptive-presentation-and-navigation.md#review-viewer는-titlesourcefreshnessnavigation의-stable-shell-landmark를-유지하되-content-panel의-수-id-순서와-layout을-6개-고정-panel로-제한하지-않아야-한다-presentation-plan이-선택한-component-composition은-동일-source라도-문서-종류와-검토-목적에-따라-달라질-수-있어야-한다)
- [plan mode의 Overview는 목표, primary plan의 Task·Step 집계, context bundle별 Requirement·Acceptance Criterion 집계, 읽기 순서, 사용자 경험, 완료 상태를 분리해 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-mode의-overview는-목표-primary-plan의-taskstep-집계-context-bundle별-requirementacceptance-criterion-집계-읽기-순서-사용자-경험-완료-상태를-분리해-보여줘야-한다)
- [plan mode의 Requirements는 Global Constraints, 핵심 정책, Route별 적용 범위와 Related Specs의 full statement context를 member provenance와 함께 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-mode의-requirements는-global-constraints-핵심-정책-route별-적용-범위와-related-specs의-full-statement-context를-member-provenance와-함께-보여줘야-한다)
- [plan mode의 Flows는 Route map, Task dependency, runtime 또는 확장 흐름을 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-mode의-flows는-route-map-task-dependency-runtime-또는-확장-흐름을-보여줘야-한다)
- [plan mode의 Data & Interfaces는 runtime 책임, 서버 권위, 파일, Remote, transaction, Interface 계약을 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-mode의-data-interfaces는-runtime-책임-서버-권위-파일-remote-transaction-interface-계약을-보여줘야-한다)
- [plan mode의 Acceptance는 plan에 명시된 Related Specs의 Requirement·Acceptance statement link만 사용해 Requirement → Acceptance Criterion → Task → Step·검증 mapping을 보여주고, 관련 spec이 없으면 Task → Step·검증 mapping을 검토 상태와 함께 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-mode의-acceptance는-plan에-명시된-related-specs의-requirementacceptance-statement-link만-사용해-requirement-acceptance-criterion-task-step검증-mapping을-보여주고-관련-spec이-없으면-task-step검증-mapping을-검토-상태와-함께-보여줘야-한다)
- [plan mode의 History는 plan 상태, Task checkbox, Progress History, 선택적인 `progress.md`·`tasks/*.md`, primary·auxiliary·context source별 role·path·hash, checkpoint, 관련 commit, 재생성 command를 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-mode의-history는-plan-상태-task-checkbox-progress-history-선택적인-progressmdtasksmd-primaryauxiliarycontext-source별-rolepathhash-checkpoint-관련-commit-재생성-command를-보여줘야-한다)
- [Review Viewer는 원문 상세를 처음부터 펼치지 않고 요약, 시각 흐름, 상세 source, acceptance evidence 순서로 배치해야 한다.](adaptive-presentation-and-navigation.md#review-viewer는-원문-상세를-처음부터-펼치지-않고-요약-시각-흐름-상세-source-acceptance-evidence-순서로-배치해야-한다)

### Review Viewer shell·template·style·script·runtime 동작을 변경한 경우에만 desktop 1440px와 mobile 390px browser 검증에서 tab, namespaced deep link, checkbox persistence, diagram, table, print layout이 정상이며 Mermaid error가 0개임을 확인하고, 개별 View 생성에서는 해당 검증을 실행하지 않는다.

검증하는 요구사항:

- [Review Viewer shell, template, style, script 또는 runtime 동작을 변경할 때는 desktop 1440px와 mobile 390px에서 tab, 표, diagram, deep link, checkbox를 검증해야 하지만, 고정 shell로 개별 `view.html`을 생성할 때는 이 검증을 반복하지 않아야 한다.](adaptive-presentation-and-navigation.md#review-viewer-shell-template-style-script-또는-runtime-동작을-변경할-때는-desktop-1440px와-mobile-390px에서-tab-표-diagram-deep-link-checkbox를-검증해야-하지만-고정-shell로-개별-viewhtml을-생성할-때는-이-검증을-반복하지-않아야-한다)
- [생성된 개별 Review Viewer에는 별도 `--check`, source count·hash·Mermaid 일치 확인, unresolved placeholder·shell markup 검사 같은 post-build 검증을 수행하지 않아야 한다.](human-readable-review-viewer.md#생성된-개별-review-viewer에는-별도-check-source-counthashmermaid-일치-확인-unresolved-placeholdershell-markup-검사-같은-post-build-검증을-수행하지-않아야-한다)
- [생성된 개별 Review Viewer에는 desktop·390px mobile render, screenshot, layout, print, tab, deep link, checkbox persistence, Mermaid, offline, freshness 상태의 브라우저 검증을 수행하지 않아야 한다.](human-readable-review-viewer.md#생성된-개별-review-viewer에는-desktop390px-mobile-render-screenshot-layout-print-tab-deep-link-checkbox-persistence-mermaid-offline-freshness-상태의-브라우저-검증을-수행하지-않아야-한다)

### Review Viewer tooling fixture에 Markdown source와 View Context를 입력하면 Semantic IR, validated Presentation Plan, source manifest와 profile-specific HTML이 만들어지고 unresolved source reference·수동 content fragment·source 밖 의미가 0개다. 개별 View 생성 뒤에는 이 fixture를 반복하지 않는다.

검증하는 요구사항:

- [Review Viewer는 title·source·freshness·navigation의 stable shell landmark를 유지하되 content panel의 수, ID, 순서와 layout을 6개 고정 panel로 제한하지 않아야 한다. Presentation Plan이 선택한 component composition은 동일 source라도 문서 종류와 검토 목적에 따라 달라질 수 있어야 한다.](adaptive-presentation-and-navigation.md#review-viewer는-titlesourcefreshnessnavigation의-stable-shell-landmark를-유지하되-content-panel의-수-id-순서와-layout을-6개-고정-panel로-제한하지-않아야-한다-presentation-plan이-선택한-component-composition은-동일-source라도-문서-종류와-검토-목적에-따라-달라질-수-있어야-한다)
- [agent는 수동 HTML content fragment, 문서별 HTML template, CSS 또는 script를 Review Viewer 입력으로 작성하지 않아야 한다. 문서별 판단이 필요하면 제한된 Presentation Plan만 선택하거나 생성해야 한다.](adaptive-presentation-and-navigation.md#agent는-수동-html-content-fragment-문서별-html-template-css-또는-script를-review-viewer-입력으로-작성하지-않아야-한다-문서별-판단이-필요하면-제한된-presentation-plan만-선택하거나-생성해야-한다)
- [Review Viewer builder는 selected Markdown source를 Semantic IR로 해석하고, View Context로 Presentation Plan을 선택한 뒤 공통 component grammar로 HTML과 manifest를 생성해야 한다. Agent가 작성한 HTML content fragment나 source 밖의 보충 문장을 입력으로 요구하지 않아야 한다.](adaptive-presentation-and-navigation.md#review-viewer-builder는-selected-markdown-source를-semantic-ir로-해석하고-view-context로-presentation-plan을-선택한-뒤-공통-component-grammar로-html과-manifest를-생성해야-한다-agent가-작성한-html-content-fragment나-source-밖의-보충-문장을-입력으로-요구하지-않아야-한다)

### source Mermaid와 derived diagram이 모두 0개인 source set과 하나 이상인 source set을 각각 `--offline`으로 build하면 전자의 generated bytes에는 Mermaid runtime이 없고 후자에는 있으며, 두 snapshot 모두 network를 차단한 브라우저에서 오류 없이 열린다. CDN mode에서도 diagram이 0개인 snapshot에는 loader가 출력되지 않고, 같은 입력 재build diff는 0이다.

검증하는 요구사항:

- [builder는 해당 Review Viewer가 렌더링할 source Mermaid와 derived diagram을 합쳐 하나 이상 포함할 때만 Mermaid runtime asset을 embed하거나 CDN loader를 출력해야 한다. Diagram이 없는 snapshot은 runtime을 생략해야 하며, 생략 여부는 selected source bytes와 build option에서만 결정적으로 계산해야 한다. `--offline` snapshot은 runtime을 생략한 경우에도 외부 network 없이 열려야 한다.](adaptive-presentation-and-navigation.md#builder는-해당-review-viewer가-렌더링할-source-mermaid와-derived-diagram을-합쳐-하나-이상-포함할-때만-mermaid-runtime-asset을-embed하거나-cdn-loader를-출력해야-한다-diagram이-없는-snapshot은-runtime을-생략해야-하며-생략-여부는-selected-source-bytes와-build-option에서만-결정적으로-계산해야-한다-offline-snapshot은-runtime을-생략한-경우에도-외부-network-없이-열려야-한다)

### Spec mode와 plan mode의 Overview panel을 열면 source별 요약 지표가 먼저 보이고 상세 집계 표가 그 아래에 남으며 두 표시의 수치가 structured parser의 같은 집계 기준과 일치한다.

검증하는 요구사항:

- [Review Viewer의 Overview panel은 source별 집계를 스캔 가능한 요약 지표로 먼저 제시하고 상세 집계 표를 그 아래에 유지해야 하며, 두 표시는 structured parser가 고정한 같은 집계 기준에서 계산해야 한다.](adaptive-presentation-and-navigation.md#review-viewer의-overview-panel은-source별-집계를-스캔-가능한-요약-지표로-먼저-제시하고-상세-집계-표를-그-아래에-유지해야-하며-두-표시는-structured-parser가-고정한-같은-집계-기준에서-계산해야-한다)

### 공통 provenance와 reading-route 구현을 검증하면 desktop 1440px와 mobile 390px의 tab, 표, diagram, deep link와 checkbox가 동작하고 이후 개별 `view.html` 생성에는 post-build checker나 browser 검증이 추가되지 않는다.

검증하는 요구사항:

- [공통 renderer의 provenance와 reading-route 변경은 desktop 1440px와 mobile 390px 및 관련 Acceptance Criterion을 검증하되 개별 `view.html` 생성에 post-build 검증을 다시 도입하지 않아야 한다.](adaptive-presentation-and-navigation.md#공통-renderer의-provenance와-reading-route-변경은-desktop-1440px와-mobile-390px-및-관련-acceptance-criterion을-검증하되-개별-viewhtml-생성에-post-build-검증을-다시-도입하지-않아야-한다)

### 같은 workflow spec을 `approval`과 `implementation`, 같은 plan을 `execution`과 `status`로 build하면 stable shell·visual system·provenance는 같고 primary component, reading order, navigation과 summary density는 각 profile·intent 계약에 맞게 다르다.

검증하는 요구사항:

- [View Context는 mode, document kind와 subtype, user intent, audience, locale, comparison·context source role과 export mode를 가져야 한다. `intent`는 `review`, `approval`, `implementation`, `comparison`, `execution`, `status` 중 하나여야 한다.](adaptive-presentation-and-navigation.md#view-context는-mode-document-kind와-subtype-user-intent-audience-locale-comparisoncontext-source-role과-export-mode를-가져야-한다-intent는-review-approval-implementation-comparison-execution-status-중-하나여야-한다)
- [사용자의 Viewer 요청에 intent나 audience가 명시되면 그대로 사용하고, 생략되면 spec은 `review`, plan은 `execution`, audience는 `mixed`를 사용해야 한다. Default 선택은 HTML 생성 권한을 만들지 않아야 한다.](adaptive-presentation-and-navigation.md#사용자의-viewer-요청에-intent나-audience가-명시되면-그대로-사용하고-생략되면-spec은-review-plan은-execution-audience는-mixed를-사용해야-한다-default-선택은-html-생성-권한을-만들지-않아야-한다)
- [Presentation Plan은 profile ID, primary question, ordered component instance, source entity·block reference, orientation과 disclosure policy만 가진 제한된 data contract여야 하며 HTML, CSS, JavaScript와 source 밖 본문을 포함하지 않아야 한다.](adaptive-presentation-and-navigation.md#presentation-plan은-profile-id-primary-question-ordered-component-instance-source-entityblock-reference-orientation과-disclosure-policy만-가진-제한된-data-contract여야-하며-html-css-javascript와-source-밖-본문을-포함하지-않아야-한다)
- [Renderer는 최소한 `generic`, `spec.workflow`, `spec.api`, `spec.architecture`, `spec.policy`, `spec.migration`, `plan.execution`, `plan.status`, `comparison` profile을 제공해야 한다. 새 profile은 공통 component를 조합하고 문서별 template를 복사하지 않아야 한다.](adaptive-presentation-and-navigation.md#renderer는-최소한-generic-specworkflow-specapi-specarchitecture-specpolicy-specmigration-planexecution-planstatus-comparison-profile을-제공해야-한다-새-profile은-공통-component를-조합하고-문서별-template를-복사하지-않아야-한다)
- [공통 component grammar는 summary, outline, prose detail, metadata, state map, sequence, interface·schema table, decision·exception matrix, relation graph, route·dependency map, progress, Requirement·Acceptance Criterion coverage, provenance와 source detail을 제공해야 한다.](adaptive-presentation-and-navigation.md#공통-component-grammar는-summary-outline-prose-detail-metadata-state-map-sequence-interfaceschema-table-decisionexception-matrix-relation-graph-routedependency-map-progress-requirementacceptance-criterion-coverage-provenance와-source-detail을-제공해야-한다)
- [문서 종류와 intent에 따라 primary component, reading order, navigation, summary density와 diagram·table 비중은 달라질 수 있지만 typography role, palette, spacing, focus, freshness, provenance, deep link, overflow와 responsive interaction은 공통 visual system을 따라야 한다.](adaptive-presentation-and-navigation.md#문서-종류와-intent에-따라-primary-component-reading-order-navigation-summary-density와-diagramtable-비중은-달라질-수-있지만-typography-role-palette-spacing-focus-freshness-provenance-deep-link-overflow와-responsive-interaction은-공통-visual-system을-따라야-한다)

### Presentation Plan fixture에 HTML·CSS·script, source 밖 prose, unknown component, dangling reference, duplicate exclusive block과 uncovered block을 각각 주입하면 validator가 실패하고, allowed component와 valid source reference만 가진 plan은 deterministic renderer 입력으로 통과한다.

검증하는 요구사항:

- [Presentation Plan은 profile ID, primary question, ordered component instance, source entity·block reference, orientation과 disclosure policy만 가진 제한된 data contract여야 하며 HTML, CSS, JavaScript와 source 밖 본문을 포함하지 않아야 한다.](adaptive-presentation-and-navigation.md#presentation-plan은-profile-id-primary-question-ordered-component-instance-source-entityblock-reference-orientation과-disclosure-policy만-가진-제한된-data-contract여야-하며-html-css-javascript와-source-밖-본문을-포함하지-않아야-한다)
- [Renderer는 최소한 `generic`, `spec.workflow`, `spec.api`, `spec.architecture`, `spec.policy`, `spec.migration`, `plan.execution`, `plan.status`, `comparison` profile을 제공해야 한다. 새 profile은 공통 component를 조합하고 문서별 template를 복사하지 않아야 한다.](adaptive-presentation-and-navigation.md#renderer는-최소한-generic-specworkflow-specapi-specarchitecture-specpolicy-specmigration-planexecution-planstatus-comparison-profile을-제공해야-한다-새-profile은-공통-component를-조합하고-문서별-template를-복사하지-않아야-한다)
- [공통 component grammar는 summary, outline, prose detail, metadata, state map, sequence, interface·schema table, decision·exception matrix, relation graph, route·dependency map, progress, Requirement·Acceptance Criterion coverage, provenance와 source detail을 제공해야 한다.](adaptive-presentation-and-navigation.md#공통-component-grammar는-summary-outline-prose-detail-metadata-state-map-sequence-interfaceschema-table-decisionexception-matrix-relation-graph-routedependency-map-progress-requirementacceptance-criterion-coverage-provenance와-source-detail을-제공해야-한다)
- [문서 종류와 intent에 따라 primary component, reading order, navigation, summary density와 diagram·table 비중은 달라질 수 있지만 typography role, palette, spacing, focus, freshness, provenance, deep link, overflow와 responsive interaction은 공통 visual system을 따라야 한다.](adaptive-presentation-and-navigation.md#문서-종류와-intent에-따라-primary-component-reading-order-navigation-summary-density와-diagramtable-비중은-달라질-수-있지만-typography-role-palette-spacing-focus-freshness-provenance-deep-link-overflow와-responsive-interaction은-공통-visual-system을-따라야-한다)
- [Profile이 source block이나 entity를 사용하지 않으면 renderer는 이를 source detail 또는 generic detail component에 포함해야 하며, Presentation Plan은 selected source content coverage 100%를 만족해야 한다.](adaptive-presentation-and-navigation.md#profile이-source-block이나-entity를-사용하지-않으면-renderer는-이를-source-detail-또는-generic-detail-component에-포함해야-하며-presentation-plan은-selected-source-content-coverage-100를-만족해야-한다)
- [알려진 profile과 rule로 충분하지 않은 source에서는 agent가 Presentation Plan을 제안할 수 있지만 HTML을 직접 생성하지 않아야 한다. 제안 plan은 schema, allowed component, source reference, coverage와 no-new-meaning validation을 통과한 뒤에만 renderer 입력이 될 수 있어야 한다.](adaptive-presentation-and-navigation.md#알려진-profile과-rule로-충분하지-않은-source에서는-agent가-presentation-plan을-제안할-수-있지만-html을-직접-생성하지-않아야-한다-제안-plan은-schema-allowed-component-source-reference-coverage와-no-new-meaning-validation을-통과한-뒤에만-renderer-입력이-될-수-있어야-한다)
- [같은 selected source bytes, View Context, accepted Presentation Plan, renderer version, locale와 fixed generated timestamp는 byte-for-byte 같은 HTML을 만들어야 한다.](adaptive-presentation-and-navigation.md#같은-selected-source-bytes-view-context-accepted-presentation-plan-renderer-version-locale와-fixed-generated-timestamp는-byte-for-byte-같은-html을-만들어야-한다)
- [Presentation Plan validator는 unknown profile·component, dangling source reference, duplicate exclusive block, uncovered source block, source 밖 prose, unsupported intent와 component contract 위반을 사람이 수정할 수 있는 진단으로 거부해야 한다.](adaptive-presentation-and-navigation.md#presentation-plan-validator는-unknown-profilecomponent-dangling-source-reference-duplicate-exclusive-block-uncovered-source-block-source-밖-prose-unsupported-intent와-component-contract-위반을-사람이-수정할-수-있는-진단으로-거부해야-한다)

### 알려진 subtype은 해당 reusable profile을 사용하고 unknown subtype은 generic fallback으로 모든 content를 표시한다. Agent가 제안한 unusual source plan도 validation 뒤에만 렌더링되며, 어떤 profile·fallback도 사용자의 명시적 요청 전에 artifact를 생성하지 않는다.

검증하는 요구사항:

- [Renderer는 최소한 `generic`, `spec.workflow`, `spec.api`, `spec.architecture`, `spec.policy`, `spec.migration`, `plan.execution`, `plan.status`, `comparison` profile을 제공해야 한다. 새 profile은 공통 component를 조합하고 문서별 template를 복사하지 않아야 한다.](adaptive-presentation-and-navigation.md#renderer는-최소한-generic-specworkflow-specapi-specarchitecture-specpolicy-specmigration-planexecution-planstatus-comparison-profile을-제공해야-한다-새-profile은-공통-component를-조합하고-문서별-template를-복사하지-않아야-한다)
- [알려진 profile과 rule로 충분하지 않은 source에서는 agent가 Presentation Plan을 제안할 수 있지만 HTML을 직접 생성하지 않아야 한다. 제안 plan은 schema, allowed component, source reference, coverage와 no-new-meaning validation을 통과한 뒤에만 renderer 입력이 될 수 있어야 한다.](adaptive-presentation-and-navigation.md#알려진-profile과-rule로-충분하지-않은-source에서는-agent가-presentation-plan을-제안할-수-있지만-html을-직접-생성하지-않아야-한다-제안-plan은-schema-allowed-component-source-reference-coverage와-no-new-meaning-validation을-통과한-뒤에만-renderer-입력이-될-수-있어야-한다)
- [같은 source는 intent만 바꿔 approval·implementation 또는 execution·status Review Viewer를 각각 생성할 수 있어야 하며 두 View는 source manifest와 provenance를 공유하면서 다른 primary composition을 가질 수 있어야 한다.](adaptive-presentation-and-navigation.md#같은-source는-intent만-바꿔-approvalimplementation-또는-executionstatus-review-viewer를-각각-생성할-수-있어야-하며-두-view는-source-manifest와-provenance를-공유하면서-다른-primary-composition을-가질-수-있어야-한다)
- [`generic` fallback은 unknown kind·subtype, sparse source, profile selection 실패에서도 metadata, outline, 모든 source block, provenance와 freshness를 읽을 수 있게 표시하고 HTML 생성 자체를 실패시키지 않아야 한다.](adaptive-presentation-and-navigation.md#generic-fallback은-unknown-kindsubtype-sparse-source-profile-selection-실패에서도-metadata-outline-모든-source-block-provenance와-freshness를-읽을-수-있게-표시하고-html-생성-자체를-실패시키지-않아야-한다)
- [Presentation Plan 선택·제안·fallback과 profile complexity는 explicit request gate를 우회하지 않아야 하며, 사용자가 Viewer 생성을 명시하기 전에는 Semantic IR, Presentation Plan 또는 HTML artifact를 생성하지 않아야 한다.](human-readable-review-viewer.md#presentation-plan-선택제안fallback과-profile-complexity는-explicit-request-gate를-우회하지-않아야-하며-사용자가-viewer-생성을-명시하기-전에는-semantic-ir-presentation-plan-또는-html-artifact를-생성하지-않아야-한다)

### fixed timestamp를 사용한 동일 source·View Context·Presentation Plan 재build diff는 0이고, shell·component·profile·planner 변경은 desktop 1440px와 mobile 390px의 profile별 typical·empty·long·invalid diagram, keyboard, disclosure, overflow와 stable shell geometry 검증을 통과한다.

검증하는 요구사항:

- [같은 selected source bytes, View Context, accepted Presentation Plan, renderer version, locale와 fixed generated timestamp는 byte-for-byte 같은 HTML을 만들어야 한다.](adaptive-presentation-and-navigation.md#같은-selected-source-bytes-view-context-accepted-presentation-plan-renderer-version-locale와-fixed-generated-timestamp는-byte-for-byte-같은-html을-만들어야-한다)
- [shell·component·profile·planner 변경의 UI 검증은 desktop 1440px와 mobile 390px에서 각 profile의 typical·empty·long·invalid diagram 상태, keyboard focus, navigation, disclosure, table·diagram overflow와 stable shell geometry를 포함해야 한다.](adaptive-presentation-and-navigation.md#shellcomponentprofileplanner-변경의-ui-검증은-desktop-1440px와-mobile-390px에서-각-profile의-typicalemptylonginvalid-diagram-상태-keyboard-focus-navigation-disclosure-tablediagram-overflow와-stable-shell-geometry를-포함해야-한다)
