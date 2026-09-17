# 적응형 표현과 탐색

적용 범위: 이 문서의 구조화 source·renderer·composition·freshness 계약은 [관리형 제작 경로](presentation-routing.md)에 적용한다. 일회성 자유 작성에는 해당 빌드 절차나 표현 제약을 강제하지 않는다.

## Requirements

### 복잡도 점수는 bundle 전체의 Requirement 8개 초과, Acceptance Criterion 8개 초과, Mermaid 2개 이상, 데이터·Interface 표 2개 이상, 여러 member·subsystem·actor·Place·상태 전이, bundle 200줄 초과, 미해결 clarification 또는 change history 다수 항목에 각각 1점을 부여하되 Visual Docs 자동 생성 조건으로 사용하지 않아야 한다.

### bundle 복잡도 점수가 2 이상이면 Forge는 Visual Docs가 검토에 도움이 될 수 있음을 사용자에게 알리고 필요하면 명시적으로 요청할 수 있다고 안내하되, Visual Docs를 자동 생성하지 않아야 한다.

### `build-visual-docs.sh`는 `--kind brief|plan|spec|project`, `--locale en|ko`, `--view-id`, `--offline`, kind별 하나의 primary source selector와 허용된 context selector를 지원하고 기본 locale은 `en`으로 유지해야 한다.

### `--locale ko`에서는 tab을 `개요`, `요구사항`, `흐름`, `데이터와 인터페이스`, `승인 기준`, `변경 이력`으로 표시해야 한다.

### Visual Docs는 title·source·freshness·navigation의 stable shell landmark를 유지하되 content panel의 수, ID, 순서와 layout을 6개 고정 panel로 제한하지 않아야 한다. Presentation Plan이 선택한 component composition은 동일 source라도 문서 종류와 검토 목적에 따라 달라질 수 있어야 한다.

### Visual Docs는 독자의 핵심 질문에 답하는 설명을 먼저 제공하고, 원문 상세와 검증 근거는 그 설명에서 찾아갈 수 있게 배치해야 한다. 설명 순서와 disclosure는 내용과 요청 목적에 따라 결정해야 한다.

### spec kind의 current·comparison statement deep link와 plan kind의 context statement·Task·Step deep link는 bundle path·member path·exact heading에서 계산한 내부 key를 포함해 DOM ID 충돌 없이 해당 Visual Docs의 panel과 대상을 열어야 한다. 화면에는 full statement와 path를 표시해야 한다.

### Acceptance Criterion 검토 checkbox와 Step 검토 checkbox는 bundle·member·statement 기반 내부 namespace와 종류를 구분해 localStorage에 저장해야 하며 내부 key를 표시하거나 제품 검증 PASS/FAIL로 표시하지 않아야 한다.

### Visual Docs가 source에서 계산한 Route, Task dependency, explicit statement coverage mapping 도식은 `Derived view`로 명시해야 한다.

### 자동 추출한 derived diagram은 selected source에서 기계적으로 계산 가능한 관계만 포함하고, agent가 prose의 명시된 관계를 설명하는 diagram은 근거와 조건을 보존한 composition으로 입력해야 한다.

기계적으로 계산 가능한 정보에는 source의 독립된 arrow-delimited 상태·흐름, table의 actor·responsibility·ownership·dependency pair, Project Map Structure와 Depends On, plan Route·Task dependency, Requirement·Acceptance coverage link가 포함된다. 일반 설명 문장이나 Markdown link 안의 화살표를 독립된 흐름으로 간주하지 않으며 여러 조건의 경로를 합치지 않는다.

### Visual Docs는 source에 없는 새로운 런타임 책임, transaction 순서, 상태 전이 또는 설계 결정을 derived diagram에 추가하지 않아야 한다.

### 모든 diagram 앞에는 제목, 이 화면에서 확인할 것, 한 문장의 읽는 법을 표시해야 한다.

### 넓은 sequence diagram 앞에는 actor별 runtime 책임을 요약한 표를 먼저 제공해야 한다.

### 넓은 Mermaid diagram은 독립 가로 스크롤 wrapper 안에 표시하고 SVG를 viewport 폭에 맞춰 무조건 축소하지 않아야 한다.

### sequence diagram과 넓은 dependency diagram에는 읽을 수 있는 최소 폭을 적용해야 한다.

### 각 diagram은 title, description, `aria-label` 또는 동등한 접근성 연결을 가져야 한다.

### Mermaid parse나 render가 실패하면 오류 요약, 가능한 오류 line·column, 원문 source를 함께 표시해야 한다.

### HTML shell은 inline favicon을 포함해 로컬 브라우저 검증에서 favicon 404를 만들지 않아야 한다.

### 집계 수치와 상태 표는 tabular number를 사용해야 한다.

### 넓은 표는 독립 가로 스크롤 wrapper를 사용해 문서 전체 viewport 폭을 확장하지 않아야 한다.

### Visual Docs shell, template, style, script 또는 runtime을 변경하면 desktop 1440px와 mobile 390px에서 해당 탐색, 표, diagram, deep link와 checkbox를 검증해야 한다. 개별 View 생성은 자료와 요청의 복잡도에 맞는 읽기·표시 검증을 적용하고 공통 tooling의 전체 회귀를 기계적으로 반복하지 않아야 한다.

### mobile에서 sequence diagram 글자를 읽기 어려우면 책임 요약표 또는 세로 flowchart를 먼저 제공하고 원본 diagram은 가로 스크롤로 유지해야 한다.

### 승인된 component grammar와 profile로 개별 Visual Docs를 생성하는 작업은 UI 디자인 skill을 적용하지 않아야 하며, Visual Docs shell·component·profile·style·planner·interaction tooling을 변경할 때만 `web-app-design`을 적용해야 한다.

### agent는 수동 HTML content fragment, 문서별 HTML template, CSS 또는 script를 Visual Docs 입력으로 작성하지 않아야 한다. 문서별 설명과 판단은 source-grounded composition 데이터로 작성해야 한다.

### Visual Docs의 Signature는 장식이나 고정 component 이름이 아니라 selected source와 intent에 맞는 state map, interface contract, dependency route, exception matrix, Acceptance Criterion coverage 같은 primary reading structure에서 만들어야 한다.

Composition은 독자 질문에 도움이 되는 관계를 flowchart·sequence, tree·structure map, dependency·coverage graph 또는 comparison matrix로 선택할 수 있다. 짧은 설명이나 표로 충분하면 도표를 생략한다.

### diagram 추가는 제목, 읽는 법, mobile 대체 요약표와 한 묶음으로 검토해야 한다.

### Visual Docs의 각 content component 제목은 스캔 가능한 짧은 명사형 label을 사용하고, 사용자가 그 component에서 답을 찾을 질문은 제목 바로 아래의 종속 orientation 문장으로 표시해야 한다. 같은 component도 Presentation Plan의 intent에 맞는 orientation을 사용해야 한다.

### Visual Docs copy는 이 화면에서 확인할 것을 먼저 말하고, 번역해도 의미가 유지되는 label은 사용자 언어로 쓰며 고유 API·service·schema 이름만 원문으로 유지해야 한다.

### Visual Docs copy의 순서는 composition이 독자의 핵심 질문에 맞춰 결정하되 첫 화면에서 주요 답을 제시하고, source detail과 provenance로 추적 가능한 읽기 경로를 제공하며 각 diagram에 읽는 법을 표시해야 한다.

### Visual Docs builder는 selected Markdown을 Semantic IR로 보존하고 agent가 작성한 source-grounded composition을 공개 CLI 입력으로 받아 View Context와 함께 검증한 뒤 공통 renderer로 HTML과 manifest를 생성해야 한다.

### builder는 실제 렌더링할 source Mermaid와 composition의 derived diagram이 하나 이상일 때만 Mermaid runtime을 포함해야 한다. 포함 여부는 source, 고정 composition과 build option으로 결정하고 diagram 없는 offline snapshot은 외부 network 없이 열려야 한다.

Runtime 포함 여부는 원문 상세와 검증된 composition이 실제로 렌더링할 diagram을 함께 계산해 결정한다.

### Visual Docs의 Overview는 source가 제공하는 목적과 핵심 내용을 먼저 제시하고 source별 집계는 보조 정보로 배치해야 한다. 요약과 상세 집계는 structured parser의 같은 기준에서 계산하고 모든 원문 상세로 이동할 수 있어야 한다.

### 공통 renderer의 provenance와 reading-route 변경은 desktop 1440px와 mobile 390px 및 관련 검증 항목으로 확인해야 한다. 이후 개별 View에서는 해당 자료의 읽기 품질을 확인하되 변경되지 않은 공통 구현의 전체 회귀는 반복하지 않아야 한다.

### View Context는 `brief`, `plan`, `spec`, `project` 중 하나인 kind, subtype, user intent, audience, locale, comparison·context source role과 export mode를 가져야 한다. `intent`는 `review`, `approval`, `implementation`, `comparison`, `execution`, `status` 중 하나여야 한다.

### 사용자의 Visual Docs 요청에 intent나 audience가 명시되면 그대로 사용하고, 생략되면 brief·spec·project는 `review`, plan은 `execution`, audience는 `mixed`를 사용해야 한다. Default 선택은 HTML 생성 권한을 만들지 않아야 한다.

### Presentation Plan은 원문 탐색용 component와 source reference를 표현하고 source-grounded composition은 독자 질문, 설명 순서, 근거가 연결된 설명과 표현 선택을 담는 제한된 data contract여야 한다. 두 입력 모두 HTML, CSS와 JavaScript를 포함하지 않아야 한다.

### Renderer는 최소한 `generic`, `brief.summary`, `spec.system`, `spec.workflow`, `spec.api`, `spec.architecture`, `spec.policy`, `spec.migration`, `plan.execution`, `plan.status`, `project.handbook`, `project.structure`, `project.spec-detail`, `comparison` profile을 제공해야 한다. 새 profile은 공통 component를 조합하고 문서별 template를 복사하지 않아야 한다.

### 공통 component grammar는 summary, outline, prose detail, metadata, system-overview, state map, sequence, runtime-responsibility, interface·schema table, decision·exception matrix, relation graph, route·dependency map, progress, Requirement·Acceptance Criterion coverage, provenance, source detail, spec-navigator, project-overview, capability-map, structure-responsibility, spec-index와 developer-information을 제공해야 한다.

### kind가 system이고 subtype이 전용 profile로 등록되지 않은 Spec은 자동 원문 탐색의 기본값으로 spec.system을 우선 선택하되, 설명 문서의 primary reading route는 composition의 독자 질문과 source에 따라 결정해야 한다.

### 독립 spec kind의 spec.system View는 desktop에서 member·section을 검색하고 선택하는 좌측 탐색과 선택한 내용을 표시하는 우측 상세를 함께 제공하고 narrow viewport에서는 탐색과 상세를 한 화면씩 표시하며 목록으로 돌아가는 명시적 action을 제공해야 한다.

### system-overview는 heading 언어와 이름에 의존하지 않고 composition에 근거가 연결된 목적 설명과 핵심 동작을 먼저 보여줘야 한다. member 탐색과 집계는 보조 정보로 제공하고 상세에서 정확한 원문과 provenance로 이동할 수 있어야 한다.

### state-map, runtime-responsibility, interface-table과 acceptance-coverage는 각 source entity 관계에 맞는 flow, responsibility table, interface table과 coverage grouping을 렌더링하고 같은 source-block 카드 목록을 서로 다른 component 이름으로 반복하지 않아야 한다.

관계형 source가 있으면 해당 component는 text card보다 먼저 실제 visual reading structure를 렌더링한다.

### Presentation Plan의 node·edge 수 threshold와 자동 visual candidate는 구성의 보조 정보로 사용해야 하며 diagram을 의무화하거나 완성 품질로 간주하지 않아야 한다. Composition은 독자 질문과 관계의 의미에 따라 prose, table 또는 diagram을 선택해야 한다.

### 자동 visual candidate 추출은 같은 selected source bytes와 View Context에서 결정적으로 동작해야 한다. 최종 visual의 종류, label과 순서는 고정된 composition과 renderer version에 따라 재현되고 source 근거와 Derived view provenance를 표시해야 한다.

### 관계를 나타내지 않는 단일 문장, 짧은 일차원 목록 또는 두 node 이하의 단순 연결은 diagram으로 강제하지 않고 읽기 쉬운 prose, list 또는 table로 유지해야 한다.

### Derived visual의 원문 인용과 identifier는 exact source를 유지하고 별도 설명 label은 근거와 의미를 보존해야 한다. 같은 관계의 text 또는 table summary를 제공해 mobile과 print에서도 이해할 수 있어야 한다.

### 문서 종류와 intent에 따라 primary component, reading order, navigation, summary density와 diagram·table 비중은 달라질 수 있지만 typography role, palette, spacing, focus, freshness, provenance, deep link, overflow와 responsive interaction은 공통 visual system을 따라야 한다.

### Profile 또는 composition의 첫 읽기 경로가 선택하지 않은 source block과 entity도 원문 상세에서 모두 접근할 수 있어야 한다. 원문 coverage 100%는 설명의 질문 충족이나 이해 품질과 별도로 검사해야 한다.

### agent는 문서 종류와 무관하게 독자 질문과 source를 바탕으로 composition을 작성하고 공개 builder에 전달해야 한다. Builder는 schema와 reference를 검사하고 의미 충실도는 별도 검토해야 하며 HTML을 직접 생성하거나 source 보강을 강제하지 않아야 한다.

### 같은 selected source bytes, View Context, 고정 composition과 Presentation Plan, generator version, build options와 fixed generated timestamp는 byte-for-byte 같은 HTML을 만들어야 한다. Agent가 composition을 새로 작성한 결과의 동일성은 요구하지 않아야 한다.

### Presentation Plan과 composition validator는 unknown schema·component, dangling reference, 중복 exclusive block, 누락 원문, 근거 없는 claim, context·source hash 불일치와 executable markup을 수정 가능한 진단으로 거부해야 한다. 참조 유효성을 의미 정확성의 증거로 간주하지 않아야 한다.

### 같은 source는 intent만 바꿔 approval·implementation 또는 execution·status Visual Docs를 각각 생성할 수 있어야 하며 두 View는 source manifest와 provenance를 공유하면서 다른 primary composition을 가질 수 있어야 한다.

### `generic` fallback은 지원되는 kind의 unknown subtype, sparse source 또는 profile 선택 실패에서 모든 원문, provenance와 freshness를 제공하는 source-browser로 표시해야 한다. 설명이 없는 fallback을 완성된 이해 문서로 표시하지 않아야 한다.

### shell·component·profile·planner 변경의 UI 검증은 desktop 1440px와 mobile 390px에서 각 profile의 typical·empty·long·invalid diagram 상태, keyboard focus, navigation, disclosure, table·diagram overflow와 stable shell geometry를 포함해야 한다.

## Acceptance Criteria

### 복잡도 1점과 2점인 문서는 모두 Markdown source 검토 경로를 기본으로 사용하고, 2점인 문서에서는 Visual Docs의 효용만 안내하며, 사용자가 시각화를 명시적으로 요청한 문서만 Visual Docs 경로를 사용한다.

검증하는 요구사항:

- [Forge는 복잡도와 관계없이 Markdown을 source 검토의 기본 경로로 사용하고, Visual Docs는 요청형 보조 검토 화면으로만 사용해야 한다.](human-readable-review-viewer.md#forge는-복잡도와-관계없이-markdown을-source-검토의-기본-경로로-사용하고-visual-docs는-요청형-보조-검토-화면으로만-사용해야-한다)
- [복잡도 점수는 bundle 전체의 Requirement 8개 초과, Acceptance Criterion 8개 초과, Mermaid 2개 이상, 데이터·Interface 표 2개 이상, 여러 member·subsystem·actor·Place·상태 전이, bundle 200줄 초과, 미해결 clarification 또는 change history 다수 항목에 각각 1점을 부여하되 Visual Docs 자동 생성 조건으로 사용하지 않아야 한다.](adaptive-presentation-and-navigation.md#복잡도-점수는-bundle-전체의-requirement-8개-초과-acceptance-criterion-8개-초과-mermaid-2개-이상-데이터interface-표-2개-이상-여러-membersubsystemactorplace상태-전이-bundle-200줄-초과-미해결-clarification-또는-change-history-다수-항목에-각각-1점을-부여하되-visual-docs-자동-생성-조건으로-사용하지-않아야-한다)
- [bundle 복잡도 점수가 2 이상이면 Forge는 Visual Docs가 검토에 도움이 될 수 있음을 사용자에게 알리고 필요하면 명시적으로 요청할 수 있다고 안내하되, Visual Docs를 자동 생성하지 않아야 한다.](adaptive-presentation-and-navigation.md#bundle-복잡도-점수가-2-이상이면-forge는-visual-docs가-검토에-도움이-될-수-있음을-사용자에게-알리고-필요하면-명시적으로-요청할-수-있다고-안내하되-visual-docs를-자동-생성하지-않아야-한다)
- [사용자가 현재 Brief, Plan, Spec 또는 Project의 시각화나 Visual Docs 생성·갱신을 명시적으로 요청한 경우에만 Forge는 복잡도 점수와 관계없이 해당 Visual Docs를 생성하거나 갱신해야 한다.](human-readable-review-viewer.md#사용자가-현재-brief-plan-spec-또는-project의-시각화나-visual-docs-생성갱신을-명시적으로-요청한-경우에만-forge는-복잡도-점수와-관계없이-해당-visual-docs를-생성하거나-갱신해야-한다)

### `visual-docs`로 독립된 spec fixture와 plan fixture를 각각 `spec`, `plan` kind, `--locale ko`, 서로 다른 review ID로 build하면 `.forge/visual-docs/<view-id>/view.html`이 생성되고 tab label이 한국어로 표시되며 `combined` kind 요청은 거부된다.

검증하는 요구사항:

- [`visual-docs` skill은 `brief`, `plan`, `spec`, `project` 네 document kind를 지원하고 Brief와 Plan은 Work View, Spec은 독립 Spec View, Project는 Project Handbook으로 표시해야 한다.](human-readable-review-viewer.md#visual-docs-skill은-brief-plan-spec-project-네-document-kind를-지원하고-brief와-plan은-work-view-spec은-독립-spec-view-project는-project-handbook으로-표시해야-한다)
- [Visual Docs는 임의 source를 합치는 `combined` kind를 지원하지 않고, project kind에서는 Project Map이 명시적으로 선언한 project source와 Spec Bundle만 읽어야 한다.](human-readable-review-viewer.md#visual-docs는-임의-source를-합치는-combined-kind를-지원하지-않고-project-kind에서는-project-map이-명시적으로-선언한-project-source와-spec-bundle만-읽어야-한다)
- [`spec` kind에서는 현재 valid Spec Bundle 전체를 primary source of truth로 사용하고, 사용자가 지정한 0개 이상의 comparison bundle을 비권위 비교 자료로 읽되 모든 내용에 bundle·member source role과 provenance를 표시해야 한다.](source-selection-and-freshness.md#spec-kind에서는-현재-valid-spec-bundle-전체를-primary-source-of-truth로-사용하고-사용자가-지정한-0개-이상의-comparison-bundle을-비권위-비교-자료로-읽되-모든-내용에-bundlemember-source-role과-provenance를-표시해야-한다)
- [`plan` kind에서는 `plan.md`와 존재하는 경우 같은 디렉터리의 `progress.md`, `tasks/*.md`를 primary source set으로 사용하고, plan의 `Related Specs` bundle 0개 이상을 제품 요구사항을 설명하는 context source로 읽되 plan source와 병합하거나 동일한 ownership으로 표시하지 않아야 한다.](source-selection-and-freshness.md#plan-kind에서는-planmd와-존재하는-경우-같은-디렉터리의-progressmd-tasksmd를-primary-source-set으로-사용하고-plan의-related-specs-bundle-0개-이상을-제품-요구사항을-설명하는-context-source로-읽되-plan-source와-병합하거나-동일한-ownership으로-표시하지-않아야-한다)
- [Brief, Plan과 Spec의 독립 View는 `.forge/visual-docs/<view-id>/view.html`에 저장하고 Git 비추적 상태로 유지해야 한다.](human-readable-review-viewer.md#brief-plan과-spec의-독립-view는-forgevisual-docsview-idviewhtml에-저장하고-git-비추적-상태로-유지해야-한다)
- [`build-visual-docs.sh`는 `--kind brief|plan|spec|project`, `--locale en|ko`, `--view-id`, `--offline`, kind별 하나의 primary source selector와 허용된 context selector를 지원하고 기본 locale은 `en`으로 유지해야 한다.](adaptive-presentation-and-navigation.md#build-visual-docssh는-kind-briefplanspecproject-locale-enko-view-id-offline-kind별-하나의-primary-source-selector와-허용된-context-selector를-지원하고-기본-locale은-en으로-유지해야-한다)
- [`--locale ko`에서는 tab을 `개요`, `요구사항`, `흐름`, `데이터와 인터페이스`, `승인 기준`, `변경 이력`으로 표시해야 한다.](adaptive-presentation-and-navigation.md#locale-ko에서는-tab을-개요-요구사항-흐름-데이터와-인터페이스-승인-기준-변경-이력으로-표시해야-한다)

### spec kind와 plan kind에서 source Mermaid와 derived diagram을 표시하면 `Current spec source`, `Comparison source`, `Plan source`, `Related spec context`, `Derived view`가 해당 source가 존재하는 범위에서 구분되고 path가 표시되며 derived node·edge는 selected source에 명시된 관계만 포함한다.

검증하는 요구사항:

- [current bundle과 comparison bundle의 Mermaid는 source text를 byte-for-byte 변경하지 않고 재사용하며 각각 `Current spec source` 또는 `Comparison source`, bundle·member H1과 path를 표시해야 한다.](source-selection-and-freshness.md#current-bundle과-comparison-bundle의-mermaid는-source-text를-byte-for-byte-변경하지-않고-재사용하며-각각-current-spec-source-또는-comparison-source-bundlemember-h1과-path를-표시해야-한다)
- [plan primary set과 Related Specs bundle context에 작성된 Mermaid는 각 source에서 그대로 가져오고 각각 `Plan source` 또는 `Related spec context`, bundle·member H1과 path를 표시해야 한다.](source-selection-and-freshness.md#plan-primary-set과-related-specs-bundle-context에-작성된-mermaid는-각-source에서-그대로-가져오고-각각-plan-source-또는-related-spec-context-bundlemember-h1과-path를-표시해야-한다)
- [Visual Docs가 source에서 계산한 Route, Task dependency, explicit statement coverage mapping 도식은 `Derived view`로 명시해야 한다.](adaptive-presentation-and-navigation.md#visual-docs가-source에서-계산한-route-task-dependency-explicit-statement-coverage-mapping-도식은-derived-view로-명시해야-한다)
- [자동 추출한 derived diagram은 selected source에서 기계적으로 계산 가능한 관계만 포함하고, agent가 prose의 명시된 관계를 설명하는 diagram은 근거와 조건을 보존한 composition으로 입력해야 한다.](adaptive-presentation-and-navigation.md#자동-추출한-derived-diagram은-selected-source에서-기계적으로-계산-가능한-관계만-포함하고-agent가-prose의-명시된-관계를-설명하는-diagram은-근거와-조건을-보존한-composition으로-입력해야-한다)
- [Visual Docs는 source에 없는 새로운 런타임 책임, transaction 순서, 상태 전이 또는 설계 결정을 derived diagram에 추가하지 않아야 한다.](adaptive-presentation-and-navigation.md#visual-docs는-source에-없는-새로운-런타임-책임-transaction-순서-상태-전이-또는-설계-결정을-derived-diagram에-추가하지-않아야-한다)

### 모든 diagram 앞에 제목, 이 화면에서 확인할 것, 한 문장의 읽는 법이 있고 넓은 sequence diagram 앞에는 runtime 책임 요약표가 먼저 표시된다.

검증하는 요구사항:

- [모든 diagram 앞에는 제목, 이 화면에서 확인할 것, 한 문장의 읽는 법을 표시해야 한다.](adaptive-presentation-and-navigation.md#모든-diagram-앞에는-제목-이-화면에서-확인할-것-한-문장의-읽는-법을-표시해야-한다)
- [넓은 sequence diagram 앞에는 actor별 runtime 책임을 요약한 표를 먼저 제공해야 한다.](adaptive-presentation-and-navigation.md#넓은-sequence-diagram-앞에는-actor별-runtime-책임을-요약한-표를-먼저-제공해야-한다)
- [Visual Docs의 각 content component 제목은 스캔 가능한 짧은 명사형 label을 사용하고, 사용자가 그 component에서 답을 찾을 질문은 제목 바로 아래의 종속 orientation 문장으로 표시해야 한다. 같은 component도 Presentation Plan의 intent에 맞는 orientation을 사용해야 한다.](adaptive-presentation-and-navigation.md#visual-docs의-각-content-component-제목은-스캔-가능한-짧은-명사형-label을-사용하고-사용자가-그-component에서-답을-찾을-질문은-제목-바로-아래의-종속-orientation-문장으로-표시해야-한다-같은-component도-presentation-plan의-intent에-맞는-orientation을-사용해야-한다)
- [Visual Docs copy는 이 화면에서 확인할 것을 먼저 말하고, 번역해도 의미가 유지되는 label은 사용자 언어로 쓰며 고유 API·service·schema 이름만 원문으로 유지해야 한다.](adaptive-presentation-and-navigation.md#visual-docs-copy는-이-화면에서-확인할-것을-먼저-말하고-번역해도-의미가-유지되는-label은-사용자-언어로-쓰며-고유-apiserviceschema-이름만-원문으로-유지해야-한다)
- [Visual Docs copy의 순서는 composition이 독자의 핵심 질문에 맞춰 결정하되 첫 화면에서 주요 답을 제시하고, source detail과 provenance로 추적 가능한 읽기 경로를 제공하며 각 diagram에 읽는 법을 표시해야 한다.](adaptive-presentation-and-navigation.md#visual-docs-copy의-순서는-composition이-독자의-핵심-질문에-맞춰-결정하되-첫-화면에서-주요-답을-제시하고-source-detail과-provenance로-추적-가능한-읽기-경로를-제공하며-각-diagram에-읽는-법을-표시해야-한다)

### 390px viewport에서 넓은 sequence diagram과 표가 문서 viewport를 확장하지 않고 각 wrapper 안에서 가로 스크롤되며 책임 요약표를 먼저 읽을 수 있다.

검증하는 요구사항:

- [넓은 Mermaid diagram은 독립 가로 스크롤 wrapper 안에 표시하고 SVG를 viewport 폭에 맞춰 무조건 축소하지 않아야 한다.](adaptive-presentation-and-navigation.md#넓은-mermaid-diagram은-독립-가로-스크롤-wrapper-안에-표시하고-svg를-viewport-폭에-맞춰-무조건-축소하지-않아야-한다)
- [sequence diagram과 넓은 dependency diagram에는 읽을 수 있는 최소 폭을 적용해야 한다.](adaptive-presentation-and-navigation.md#sequence-diagram과-넓은-dependency-diagram에는-읽을-수-있는-최소-폭을-적용해야-한다)
- [넓은 표는 독립 가로 스크롤 wrapper를 사용해 문서 전체 viewport 폭을 확장하지 않아야 한다.](adaptive-presentation-and-navigation.md#넓은-표는-독립-가로-스크롤-wrapper를-사용해-문서-전체-viewport-폭을-확장하지-않아야-한다)
- [Visual Docs shell, template, style, script 또는 runtime을 변경하면 desktop 1440px와 mobile 390px에서 해당 탐색, 표, diagram, deep link와 checkbox를 검증해야 한다. 개별 View 생성은 자료와 요청의 복잡도에 맞는 읽기·표시 검증을 적용하고 공통 tooling의 전체 회귀를 기계적으로 반복하지 않아야 한다.](adaptive-presentation-and-navigation.md#visual-docs-shell-template-style-script-또는-runtime을-변경하면-desktop-1440px와-mobile-390px에서-해당-탐색-표-diagram-deep-link와-checkbox를-검증해야-한다-개별-view-생성은-자료와-요청의-복잡도에-맞는-읽기표시-검증을-적용하고-공통-tooling의-전체-회귀를-기계적으로-반복하지-않아야-한다)
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

### current·comparison·context bundle에 같은 statement가 있고 plan의 Task·Step이 함께 있는 Visual Docs에서 deep link와 검토 checkbox를 변경하고 page를 reload하면 bundle·member·statement namespace별 target과 checkbox 상태가 충돌 없이 복원되며 화면에는 full statement와 path만 표시된다.

검증하는 요구사항:

- [spec kind의 current·comparison statement deep link와 plan kind의 context statement·Task·Step deep link는 bundle path·member path·exact heading에서 계산한 내부 key를 포함해 DOM ID 충돌 없이 해당 Visual Docs의 panel과 대상을 열어야 한다. 화면에는 full statement와 path를 표시해야 한다.](adaptive-presentation-and-navigation.md#spec-kind의-currentcomparison-statement-deep-link와-plan-kind의-context-statementtaskstep-deep-link는-bundle-pathmember-pathexact-heading에서-계산한-내부-key를-포함해-dom-id-충돌-없이-해당-visual-docs의-panel과-대상을-열어야-한다-화면에는-full-statement와-path를-표시해야-한다)
- [Acceptance Criterion 검토 checkbox와 Step 검토 checkbox는 bundle·member·statement 기반 내부 namespace와 종류를 구분해 localStorage에 저장해야 하며 내부 key를 표시하거나 제품 검증 PASS/FAIL로 표시하지 않아야 한다.](adaptive-presentation-and-navigation.md#acceptance-criterion-검토-checkbox와-step-검토-checkbox는-bundlememberstatement-기반-내부-namespace와-종류를-구분해-localstorage에-저장해야-하며-내부-key를-표시하거나-제품-검증-passfail로-표시하지-않아야-한다)

### 승인된 component grammar로 개별 Visual Docs를 생성할 때 UI 디자인 skill과 수동 HTML fragment·문서별 template·CSS·script를 사용하지 않고 Semantic IR과 composition을 공통 renderer에 전달한다. Shell·component·profile·planner tooling 변경에만 `web-app-design`을 적용한다.

검증하는 요구사항:

- [승인된 component grammar와 profile로 개별 Visual Docs를 생성하는 작업은 UI 디자인 skill을 적용하지 않아야 하며, Visual Docs shell·component·profile·style·planner·interaction tooling을 변경할 때만 `web-app-design`을 적용해야 한다.](adaptive-presentation-and-navigation.md#승인된-component-grammar와-profile로-개별-visual-docs를-생성하는-작업은-ui-디자인-skill을-적용하지-않아야-하며-visual-docs-shellcomponentprofilestyleplannerinteraction-tooling을-변경할-때만-web-app-design을-적용해야-한다)
- [agent는 수동 HTML content fragment, 문서별 HTML template, CSS 또는 script를 Visual Docs 입력으로 작성하지 않아야 한다. 문서별 설명과 판단은 source-grounded composition 데이터로 작성해야 한다.](adaptive-presentation-and-navigation.md#agent는-수동-html-content-fragment-문서별-html-template-css-또는-script를-visual-docs-입력으로-작성하지-않아야-한다-문서별-설명과-판단은-source-grounded-composition-데이터로-작성해야-한다)
- [Visual Docs의 Signature는 장식이나 고정 component 이름이 아니라 selected source와 intent에 맞는 state map, interface contract, dependency route, exception matrix, Acceptance Criterion coverage 같은 primary reading structure에서 만들어야 한다.](adaptive-presentation-and-navigation.md#visual-docs의-signature는-장식이나-고정-component-이름이-아니라-selected-source와-intent에-맞는-state-map-interface-contract-dependency-route-exception-matrix-acceptance-criterion-coverage-같은-primary-reading-structure에서-만들어야-한다)
- [diagram 추가는 제목, 읽는 법, mobile 대체 요약표와 한 묶음으로 검토해야 한다.](adaptive-presentation-and-navigation.md#diagram-추가는-제목-읽는-법-mobile-대체-요약표와-한-묶음으로-검토해야-한다)
- [Visual Docs builder는 selected Markdown을 Semantic IR로 보존하고 agent가 작성한 source-grounded composition을 공개 CLI 입력으로 받아 View Context와 함께 검증한 뒤 공통 renderer로 HTML과 manifest를 생성해야 한다.](adaptive-presentation-and-navigation.md#visual-docs-builder는-selected-markdown을-semantic-ir로-보존하고-agent가-작성한-source-grounded-composition을-공개-cli-입력으로-받아-view-context와-함께-검증한-뒤-공통-renderer로-html과-manifest를-생성해야-한다)

### `.forge/visual-docs/<view-id>/view.html`의 CDN build와 `--offline` build가 모두 열리고 offline 파일에는 외부 Mermaid script 요청이 없으며 diagram이 렌더된다.

검증하는 요구사항:

- [Brief, Plan과 Spec의 독립 View는 `.forge/visual-docs/<view-id>/view.html`에 저장하고 Git 비추적 상태로 유지해야 한다.](human-readable-review-viewer.md#brief-plan과-spec의-독립-view는-forgevisual-docsview-idviewhtml에-저장하고-git-비추적-상태로-유지해야-한다)
- [`build-visual-docs.sh`는 `--kind brief|plan|spec|project`, `--locale en|ko`, `--view-id`, `--offline`, kind별 하나의 primary source selector와 허용된 context selector를 지원하고 기본 locale은 `en`으로 유지해야 한다.](adaptive-presentation-and-navigation.md#build-visual-docssh는-kind-briefplanspecproject-locale-enko-view-id-offline-kind별-하나의-primary-source-selector와-허용된-context-selector를-지원하고-기본-locale은-en으로-유지해야-한다)

### plan kind의 execution과 status Viewer는 stable shell landmark와 source ownership을 공유하면서 서로 다른 primary component와 reading order를 가지며, 두 View 모두 plan source detail과 acceptance evidence로 이동할 수 있다.

검증하는 요구사항:

- [Visual Docs는 title·source·freshness·navigation의 stable shell landmark를 유지하되 content panel의 수, ID, 순서와 layout을 6개 고정 panel로 제한하지 않아야 한다. Presentation Plan이 선택한 component composition은 동일 source라도 문서 종류와 검토 목적에 따라 달라질 수 있어야 한다.](adaptive-presentation-and-navigation.md#visual-docs는-titlesourcefreshnessnavigation의-stable-shell-landmark를-유지하되-content-panel의-수-id-순서와-layout을-6개-고정-panel로-제한하지-않아야-한다-presentation-plan이-선택한-component-composition은-동일-source라도-문서-종류와-검토-목적에-따라-달라질-수-있어야-한다)
- [plan kind의 Overview는 목표, primary plan의 Task·Step 집계, context bundle별 Requirement·Acceptance Criterion 집계, 읽기 순서, 사용자 경험, 완료 상태를 분리해 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-kind의-overview는-목표-primary-plan의-taskstep-집계-context-bundle별-requirementacceptance-criterion-집계-읽기-순서-사용자-경험-완료-상태를-분리해-보여줘야-한다)
- [plan kind의 Requirements는 Global Constraints, 핵심 정책, Route별 적용 범위와 Related Specs의 full statement context를 member provenance와 함께 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-kind의-requirements는-global-constraints-핵심-정책-route별-적용-범위와-related-specs의-full-statement-context를-member-provenance와-함께-보여줘야-한다)
- [plan kind의 Flows는 Route map, Task dependency, runtime 또는 확장 흐름을 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-kind의-flows는-route-map-task-dependency-runtime-또는-확장-흐름을-보여줘야-한다)
- [plan kind의 Data & Interfaces는 runtime 책임, 서버 권위, 파일, Remote, transaction, Interface 계약을 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-kind의-data-interfaces는-runtime-책임-서버-권위-파일-remote-transaction-interface-계약을-보여줘야-한다)
- [plan kind의 Acceptance는 plan에 명시된 Related Specs의 statement link만 사용해야 한다. Acceptance statement가 있는 bundle은 Requirement → Acceptance Criterion → Task → Step·검증 mapping을, Acceptance statement가 없는 bundle은 Requirement → Task → Step·검증 mapping을 보여주고, 관련 spec이 없으면 Task → Step·검증 mapping을 검토 상태와 함께 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-kind의-acceptance는-plan에-명시된-related-specs의-statement-link만-사용해야-한다-acceptance-statement가-있는-bundle은-requirement-acceptance-criterion-task-step검증-mapping을-acceptance-statement가-없는-bundle은-requirement-task-step검증-mapping을-보여주고-관련-spec이-없으면-task-step검증-mapping을-검토-상태와-함께-보여줘야-한다)
- [plan kind의 History는 plan 상태, Task checkbox, Progress History, 선택적인 `progress.md`·`tasks/*.md`, primary·auxiliary·context source별 role·path·hash, checkpoint, 관련 commit, 재생성 command를 보여줘야 한다.](plan-context-and-statement-traceability.md#plan-kind의-history는-plan-상태-task-checkbox-progress-history-선택적인-progressmdtasksmd-primaryauxiliarycontext-source별-rolepathhash-checkpoint-관련-commit-재생성-command를-보여줘야-한다)
- [Visual Docs는 독자의 핵심 질문에 답하는 설명을 먼저 제공하고, 원문 상세와 검증 근거는 그 설명에서 찾아갈 수 있게 배치해야 한다. 설명 순서와 disclosure는 내용과 요청 목적에 따라 결정해야 한다.](adaptive-presentation-and-navigation.md#visual-docs는-독자의-핵심-질문에-답하는-설명을-먼저-제공하고-원문-상세와-검증-근거는-그-설명에서-찾아갈-수-있게-배치해야-한다-설명-순서와-disclosure는-내용과-요청-목적에-따라-결정해야-한다)

### Visual Docs tooling 변경 fixture는 desktop 1440px와 mobile 390px에서 숨겨진 상세 선택, 빠른 탐색, deep link, checkbox persistence, diagram, table과 print의 필요한 상태를 통과한다. 유효한 Mermaid에는 표시된 오류가 없고 개별 View 생성 fixture도 요청 범위의 읽기·표시 확인을 수행한다.

검증하는 요구사항:

- [Visual Docs shell, template, style, script 또는 runtime을 변경하면 desktop 1440px와 mobile 390px에서 해당 탐색, 표, diagram, deep link와 checkbox를 검증해야 한다. 개별 View 생성은 자료와 요청의 복잡도에 맞는 읽기·표시 검증을 적용하고 공통 tooling의 전체 회귀를 기계적으로 반복하지 않아야 한다.](adaptive-presentation-and-navigation.md#visual-docs-shell-template-style-script-또는-runtime을-변경하면-desktop-1440px와-mobile-390px에서-해당-탐색-표-diagram-deep-link와-checkbox를-검증해야-한다-개별-view-생성은-자료와-요청의-복잡도에-맞는-읽기표시-검증을-적용하고-공통-tooling의-전체-회귀를-기계적으로-반복하지-않아야-한다)
- [개별 Visual Docs의 검증은 요청한 결과를 직접 증명하는 최소 범위로 선택해야 한다. 동일한 변경 상태에서 이미 통과한 검증은 재사용할 수 있고, 새 변경·실패·미해결 위험이 있을 때만 필요한 증거를 다시 수집해야 한다.](human-readable-review-viewer.md#개별-visual-docs의-검증은-요청한-결과를-직접-증명하는-최소-범위로-선택해야-한다-동일한-변경-상태에서-이미-통과한-검증은-재사용할-수-있고-새-변경실패미해결-위험이-있을-때만-필요한-증거를-다시-수집해야-한다)
- [개별 Visual Docs는 실제 화면의 읽기 순서와 핵심 내용을 확인해야 하며, 복잡한 자료·새 구성·도표가 있으면 desktop과 narrow viewport에서 도표 의미, 탐색과 가독성을 확인해야 한다. 검증 실패는 같은 요청 안에서 원본 또는 공통 tooling을 수정하고 재생성해 해결하되 생성 HTML을 직접 편집하지 않아야 한다.](human-readable-review-viewer.md#개별-visual-docs는-실제-화면의-읽기-순서와-핵심-내용을-확인해야-하며-복잡한-자료새-구성도표가-있으면-desktop과-narrow-viewport에서-도표-의미-탐색과-가독성을-확인해야-한다-검증-실패는-같은-요청-안에서-원본-또는-공통-tooling을-수정하고-재생성해-해결하되-생성-html을-직접-편집하지-않아야-한다)

### Visual Docs tooling fixture에서 Markdown source와 View Context를 준비하고 composition을 공개 CLI로 전달하면 Semantic IR, 검증된 구성, manifest와 HTML이 만들어진다. 원문 밖 의미는 별도 의미 검토로 확인하고 개별 View 검증은 자료에 필요한 범위로 수행한다.

검증하는 요구사항:

- [Visual Docs는 title·source·freshness·navigation의 stable shell landmark를 유지하되 content panel의 수, ID, 순서와 layout을 6개 고정 panel로 제한하지 않아야 한다. Presentation Plan이 선택한 component composition은 동일 source라도 문서 종류와 검토 목적에 따라 달라질 수 있어야 한다.](adaptive-presentation-and-navigation.md#visual-docs는-titlesourcefreshnessnavigation의-stable-shell-landmark를-유지하되-content-panel의-수-id-순서와-layout을-6개-고정-panel로-제한하지-않아야-한다-presentation-plan이-선택한-component-composition은-동일-source라도-문서-종류와-검토-목적에-따라-달라질-수-있어야-한다)
- [agent는 수동 HTML content fragment, 문서별 HTML template, CSS 또는 script를 Visual Docs 입력으로 작성하지 않아야 한다. 문서별 설명과 판단은 source-grounded composition 데이터로 작성해야 한다.](adaptive-presentation-and-navigation.md#agent는-수동-html-content-fragment-문서별-html-template-css-또는-script를-visual-docs-입력으로-작성하지-않아야-한다-문서별-설명과-판단은-source-grounded-composition-데이터로-작성해야-한다)
- [Visual Docs builder는 selected Markdown을 Semantic IR로 보존하고 agent가 작성한 source-grounded composition을 공개 CLI 입력으로 받아 View Context와 함께 검증한 뒤 공통 renderer로 HTML과 manifest를 생성해야 한다.](adaptive-presentation-and-navigation.md#visual-docs-builder는-selected-markdown을-semantic-ir로-보존하고-agent가-작성한-source-grounded-composition을-공개-cli-입력으로-받아-view-context와-함께-검증한-뒤-공통-renderer로-html과-manifest를-생성해야-한다)

### 실제로 렌더링할 source Mermaid와 composition·자동 추출 derived diagram이 모두 0개인 구성과 하나 이상인 구성을 각각 offline으로 build하면 전자는 Mermaid runtime이 없고 후자는 있으며 network를 차단한 브라우저에서 열린다. CDN mode의 diagram 없는 구성에도 loader가 없다.

검증하는 요구사항:

- [builder는 실제 렌더링할 source Mermaid와 composition의 derived diagram이 하나 이상일 때만 Mermaid runtime을 포함해야 한다. 포함 여부는 source, 고정 composition과 build option으로 결정하고 diagram 없는 offline snapshot은 외부 network 없이 열려야 한다.](adaptive-presentation-and-navigation.md#builder는-실제-렌더링할-source-mermaid와-composition의-derived-diagram이-하나-이상일-때만-mermaid-runtime을-포함해야-한다-포함-여부는-source-고정-composition과-build-option으로-결정하고-diagram-없는-offline-snapshot은-외부-network-없이-열려야-한다)

### 목적 설명이 있는 Spec과 plan의 Overview를 열면 목적과 핵심 내용이 집계보다 먼저 보이고 390px에서도 숫자 카드가 첫 읽기 화면을 차지하지 않으며 요약과 상세 수치가 같은 source 집계 기준과 일치한다.

검증하는 요구사항:

- [Visual Docs의 Overview는 source가 제공하는 목적과 핵심 내용을 먼저 제시하고 source별 집계는 보조 정보로 배치해야 한다. 요약과 상세 집계는 structured parser의 같은 기준에서 계산하고 모든 원문 상세로 이동할 수 있어야 한다.](adaptive-presentation-and-navigation.md#visual-docs의-overview는-source가-제공하는-목적과-핵심-내용을-먼저-제시하고-source별-집계는-보조-정보로-배치해야-한다-요약과-상세-집계는-structured-parser의-같은-기준에서-계산하고-모든-원문-상세로-이동할-수-있어야-한다)

### 공통 provenance와 reading-route 구현을 검증하면 desktop 1440px와 mobile 390px의 탐색, 표, diagram, deep link와 checkbox가 동작하며 개별 View는 해당 자료의 읽기·표시를 확인하고 변경되지 않은 공통 회귀를 반복하지 않는다.

검증하는 요구사항:

- [공통 renderer의 provenance와 reading-route 변경은 desktop 1440px와 mobile 390px 및 관련 검증 항목으로 확인해야 한다. 이후 개별 View에서는 해당 자료의 읽기 품질을 확인하되 변경되지 않은 공통 구현의 전체 회귀는 반복하지 않아야 한다.](adaptive-presentation-and-navigation.md#공통-renderer의-provenance와-reading-route-변경은-desktop-1440px와-mobile-390px-및-관련-검증-항목으로-확인해야-한다-이후-개별-view에서는-해당-자료의-읽기-품질을-확인하되-변경되지-않은-공통-구현의-전체-회귀는-반복하지-않아야-한다)

### 같은 workflow spec을 `approval`과 `implementation`, 같은 plan을 `execution`과 `status`로 build하면 stable shell·visual system·provenance는 같고 primary component, reading order, navigation과 summary density는 각 profile·intent 계약에 맞게 다르다.

검증하는 요구사항:

- [View Context는 `brief`, `plan`, `spec`, `project` 중 하나인 kind, subtype, user intent, audience, locale, comparison·context source role과 export mode를 가져야 한다. `intent`는 `review`, `approval`, `implementation`, `comparison`, `execution`, `status` 중 하나여야 한다.](adaptive-presentation-and-navigation.md#view-context는-brief-plan-spec-project-중-하나인-kind-subtype-user-intent-audience-locale-comparisoncontext-source-role과-export-mode를-가져야-한다-intent는-review-approval-implementation-comparison-execution-status-중-하나여야-한다)
- [사용자의 Visual Docs 요청에 intent나 audience가 명시되면 그대로 사용하고, 생략되면 brief·spec·project는 `review`, plan은 `execution`, audience는 `mixed`를 사용해야 한다. Default 선택은 HTML 생성 권한을 만들지 않아야 한다.](adaptive-presentation-and-navigation.md#사용자의-visual-docs-요청에-intent나-audience가-명시되면-그대로-사용하고-생략되면-briefspecproject는-review-plan은-execution-audience는-mixed를-사용해야-한다-default-선택은-html-생성-권한을-만들지-않아야-한다)
- [Presentation Plan은 원문 탐색용 component와 source reference를 표현하고 source-grounded composition은 독자 질문, 설명 순서, 근거가 연결된 설명과 표현 선택을 담는 제한된 data contract여야 한다. 두 입력 모두 HTML, CSS와 JavaScript를 포함하지 않아야 한다.](adaptive-presentation-and-navigation.md#presentation-plan은-원문-탐색용-component와-source-reference를-표현하고-source-grounded-composition은-독자-질문-설명-순서-근거가-연결된-설명과-표현-선택을-담는-제한된-data-contract여야-한다-두-입력-모두-html-css와-javascript를-포함하지-않아야-한다)
- [Renderer는 최소한 `generic`, `brief.summary`, `spec.system`, `spec.workflow`, `spec.api`, `spec.architecture`, `spec.policy`, `spec.migration`, `plan.execution`, `plan.status`, `project.handbook`, `project.structure`, `project.spec-detail`, `comparison` profile을 제공해야 한다. 새 profile은 공통 component를 조합하고 문서별 template를 복사하지 않아야 한다.](adaptive-presentation-and-navigation.md#renderer는-최소한-generic-briefsummary-specsystem-specworkflow-specapi-specarchitecture-specpolicy-specmigration-planexecution-planstatus-projecthandbook-projectstructure-projectspec-detail-comparison-profile을-제공해야-한다-새-profile은-공통-component를-조합하고-문서별-template를-복사하지-않아야-한다)
- [공통 component grammar는 summary, outline, prose detail, metadata, system-overview, state map, sequence, runtime-responsibility, interface·schema table, decision·exception matrix, relation graph, route·dependency map, progress, Requirement·Acceptance Criterion coverage, provenance, source detail, spec-navigator, project-overview, capability-map, structure-responsibility, spec-index와 developer-information을 제공해야 한다.](adaptive-presentation-and-navigation.md#공통-component-grammar는-summary-outline-prose-detail-metadata-system-overview-state-map-sequence-runtime-responsibility-interfaceschema-table-decisionexception-matrix-relation-graph-routedependency-map-progress-requirementacceptance-criterion-coverage-provenance-source-detail-spec-navigator-project-overview-capability-map-structure-responsibility-spec-index와-developer-information을-제공해야-한다)
- [문서 종류와 intent에 따라 primary component, reading order, navigation, summary density와 diagram·table 비중은 달라질 수 있지만 typography role, palette, spacing, focus, freshness, provenance, deep link, overflow와 responsive interaction은 공통 visual system을 따라야 한다.](adaptive-presentation-and-navigation.md#문서-종류와-intent에-따라-primary-component-reading-order-navigation-summary-density와-diagramtable-비중은-달라질-수-있지만-typography-role-palette-spacing-focus-freshness-provenance-deep-link-overflow와-responsive-interaction은-공통-visual-system을-따라야-한다)

### Composition과 Presentation Plan fixture에 executable markup, unknown component, dangling reference, 누락 원문과 오래된 source·context를 주입하면 validator가 실패한다. 근거가 연결된 별도 설명은 입력으로 허용하되 잘못된 의미를 기계적 통과만으로 승인하지 않는다.

검증하는 요구사항:

- [Presentation Plan은 원문 탐색용 component와 source reference를 표현하고 source-grounded composition은 독자 질문, 설명 순서, 근거가 연결된 설명과 표현 선택을 담는 제한된 data contract여야 한다. 두 입력 모두 HTML, CSS와 JavaScript를 포함하지 않아야 한다.](adaptive-presentation-and-navigation.md#presentation-plan은-원문-탐색용-component와-source-reference를-표현하고-source-grounded-composition은-독자-질문-설명-순서-근거가-연결된-설명과-표현-선택을-담는-제한된-data-contract여야-한다-두-입력-모두-html-css와-javascript를-포함하지-않아야-한다)
- [Renderer는 최소한 `generic`, `brief.summary`, `spec.system`, `spec.workflow`, `spec.api`, `spec.architecture`, `spec.policy`, `spec.migration`, `plan.execution`, `plan.status`, `project.handbook`, `project.structure`, `project.spec-detail`, `comparison` profile을 제공해야 한다. 새 profile은 공통 component를 조합하고 문서별 template를 복사하지 않아야 한다.](adaptive-presentation-and-navigation.md#renderer는-최소한-generic-briefsummary-specsystem-specworkflow-specapi-specarchitecture-specpolicy-specmigration-planexecution-planstatus-projecthandbook-projectstructure-projectspec-detail-comparison-profile을-제공해야-한다-새-profile은-공통-component를-조합하고-문서별-template를-복사하지-않아야-한다)
- [공통 component grammar는 summary, outline, prose detail, metadata, system-overview, state map, sequence, runtime-responsibility, interface·schema table, decision·exception matrix, relation graph, route·dependency map, progress, Requirement·Acceptance Criterion coverage, provenance, source detail, spec-navigator, project-overview, capability-map, structure-responsibility, spec-index와 developer-information을 제공해야 한다.](adaptive-presentation-and-navigation.md#공통-component-grammar는-summary-outline-prose-detail-metadata-system-overview-state-map-sequence-runtime-responsibility-interfaceschema-table-decisionexception-matrix-relation-graph-routedependency-map-progress-requirementacceptance-criterion-coverage-provenance-source-detail-spec-navigator-project-overview-capability-map-structure-responsibility-spec-index와-developer-information을-제공해야-한다)
- [문서 종류와 intent에 따라 primary component, reading order, navigation, summary density와 diagram·table 비중은 달라질 수 있지만 typography role, palette, spacing, focus, freshness, provenance, deep link, overflow와 responsive interaction은 공통 visual system을 따라야 한다.](adaptive-presentation-and-navigation.md#문서-종류와-intent에-따라-primary-component-reading-order-navigation-summary-density와-diagramtable-비중은-달라질-수-있지만-typography-role-palette-spacing-focus-freshness-provenance-deep-link-overflow와-responsive-interaction은-공통-visual-system을-따라야-한다)
- [Profile 또는 composition의 첫 읽기 경로가 선택하지 않은 source block과 entity도 원문 상세에서 모두 접근할 수 있어야 한다. 원문 coverage 100%는 설명의 질문 충족이나 이해 품질과 별도로 검사해야 한다.](adaptive-presentation-and-navigation.md#profile-또는-composition의-첫-읽기-경로가-선택하지-않은-source-block과-entity도-원문-상세에서-모두-접근할-수-있어야-한다-원문-coverage-100는-설명의-질문-충족이나-이해-품질과-별도로-검사해야-한다)
- [agent는 문서 종류와 무관하게 독자 질문과 source를 바탕으로 composition을 작성하고 공개 builder에 전달해야 한다. Builder는 schema와 reference를 검사하고 의미 충실도는 별도 검토해야 하며 HTML을 직접 생성하거나 source 보강을 강제하지 않아야 한다.](adaptive-presentation-and-navigation.md#agent는-문서-종류와-무관하게-독자-질문과-source를-바탕으로-composition을-작성하고-공개-builder에-전달해야-한다-builder는-schema와-reference를-검사하고-의미-충실도는-별도-검토해야-하며-html을-직접-생성하거나-source-보강을-강제하지-않아야-한다)
- [같은 selected source bytes, View Context, 고정 composition과 Presentation Plan, generator version, build options와 fixed generated timestamp는 byte-for-byte 같은 HTML을 만들어야 한다. Agent가 composition을 새로 작성한 결과의 동일성은 요구하지 않아야 한다.](adaptive-presentation-and-navigation.md#같은-selected-source-bytes-view-context-고정-composition과-presentation-plan-generator-version-build-options와-fixed-generated-timestamp는-byte-for-byte-같은-html을-만들어야-한다-agent가-composition을-새로-작성한-결과의-동일성은-요구하지-않아야-한다)
- [Presentation Plan과 composition validator는 unknown schema·component, dangling reference, 중복 exclusive block, 누락 원문, 근거 없는 claim, context·source hash 불일치와 executable markup을 수정 가능한 진단으로 거부해야 한다. 참조 유효성을 의미 정확성의 증거로 간주하지 않아야 한다.](adaptive-presentation-and-navigation.md#presentation-plan과-composition-validator는-unknown-schemacomponent-dangling-reference-중복-exclusive-block-누락-원문-근거-없는-claim-contextsource-hash-불일치와-executable-markup을-수정-가능한-진단으로-거부해야-한다-참조-유효성을-의미-정확성의-증거로-간주하지-않아야-한다)

### 같은 source를 알려진 subtype과 unknown subtype으로 준비하면 각 원문 탐색 profile이 내용을 보존하고 공개 composition 입력이 설명 순서를 결정한다. 설명 없는 fallback은 source-browser로 표시되며 어떤 경로도 명시적 요청 전에 artifact를 생성하지 않는다.

검증하는 요구사항:

- [Renderer는 최소한 `generic`, `brief.summary`, `spec.system`, `spec.workflow`, `spec.api`, `spec.architecture`, `spec.policy`, `spec.migration`, `plan.execution`, `plan.status`, `project.handbook`, `project.structure`, `project.spec-detail`, `comparison` profile을 제공해야 한다. 새 profile은 공통 component를 조합하고 문서별 template를 복사하지 않아야 한다.](adaptive-presentation-and-navigation.md#renderer는-최소한-generic-briefsummary-specsystem-specworkflow-specapi-specarchitecture-specpolicy-specmigration-planexecution-planstatus-projecthandbook-projectstructure-projectspec-detail-comparison-profile을-제공해야-한다-새-profile은-공통-component를-조합하고-문서별-template를-복사하지-않아야-한다)
- [agent는 문서 종류와 무관하게 독자 질문과 source를 바탕으로 composition을 작성하고 공개 builder에 전달해야 한다. Builder는 schema와 reference를 검사하고 의미 충실도는 별도 검토해야 하며 HTML을 직접 생성하거나 source 보강을 강제하지 않아야 한다.](adaptive-presentation-and-navigation.md#agent는-문서-종류와-무관하게-독자-질문과-source를-바탕으로-composition을-작성하고-공개-builder에-전달해야-한다-builder는-schema와-reference를-검사하고-의미-충실도는-별도-검토해야-하며-html을-직접-생성하거나-source-보강을-강제하지-않아야-한다)
- [같은 source는 intent만 바꿔 approval·implementation 또는 execution·status Visual Docs를 각각 생성할 수 있어야 하며 두 View는 source manifest와 provenance를 공유하면서 다른 primary composition을 가질 수 있어야 한다.](adaptive-presentation-and-navigation.md#같은-source는-intent만-바꿔-approvalimplementation-또는-executionstatus-visual-docs를-각각-생성할-수-있어야-하며-두-view는-source-manifest와-provenance를-공유하면서-다른-primary-composition을-가질-수-있어야-한다)
- [`generic` fallback은 지원되는 kind의 unknown subtype, sparse source 또는 profile 선택 실패에서 모든 원문, provenance와 freshness를 제공하는 source-browser로 표시해야 한다. 설명이 없는 fallback을 완성된 이해 문서로 표시하지 않아야 한다.](adaptive-presentation-and-navigation.md#generic-fallback은-지원되는-kind의-unknown-subtype-sparse-source-또는-profile-선택-실패에서-모든-원문-provenance와-freshness를-제공하는-source-browser로-표시해야-한다-설명이-없는-fallback을-완성된-이해-문서로-표시하지-않아야-한다)
- [Presentation Plan 선택·제안·fallback과 profile complexity는 explicit request gate를 우회하지 않아야 하며, 사용자가 Visual Docs 생성을 명시하기 전에는 Semantic IR, Presentation Plan 또는 HTML artifact를 생성하지 않아야 한다.](human-readable-review-viewer.md#presentation-plan-선택제안fallback과-profile-complexity는-explicit-request-gate를-우회하지-않아야-하며-사용자가-visual-docs-생성을-명시하기-전에는-semantic-ir-presentation-plan-또는-html-artifact를-생성하지-않아야-한다)

### 10개 이상의 member, 60개 이상의 Requirement, 15개 이상의 Acceptance와 source Mermaid 0개를 가진 system fixture를 review intent로 build하면 spec.system이 선택되고 system overview, member·section 검색 탐색, source 표에서 계산한 책임·interface, Requirement·Acceptance coverage와 전체 source detail이 중복 없이 표시된다.

검증하는 요구사항:

- [kind가 system이고 subtype이 전용 profile로 등록되지 않은 Spec은 자동 원문 탐색의 기본값으로 spec.system을 우선 선택하되, 설명 문서의 primary reading route는 composition의 독자 질문과 source에 따라 결정해야 한다.](adaptive-presentation-and-navigation.md#kind가-system이고-subtype이-전용-profile로-등록되지-않은-spec은-자동-원문-탐색의-기본값으로-specsystem을-우선-선택하되-설명-문서의-primary-reading-route는-composition의-독자-질문과-source에-따라-결정해야-한다)
- [독립 spec kind의 spec.system View는 desktop에서 member·section을 검색하고 선택하는 좌측 탐색과 선택한 내용을 표시하는 우측 상세를 함께 제공하고 narrow viewport에서는 탐색과 상세를 한 화면씩 표시하며 목록으로 돌아가는 명시적 action을 제공해야 한다.](adaptive-presentation-and-navigation.md#독립-spec-kind의-specsystem-view는-desktop에서-membersection을-검색하고-선택하는-좌측-탐색과-선택한-내용을-표시하는-우측-상세를-함께-제공하고-narrow-viewport에서는-탐색과-상세를-한-화면씩-표시하며-목록으로-돌아가는-명시적-action을-제공해야-한다)
- [system-overview는 heading 언어와 이름에 의존하지 않고 composition에 근거가 연결된 목적 설명과 핵심 동작을 먼저 보여줘야 한다. member 탐색과 집계는 보조 정보로 제공하고 상세에서 정확한 원문과 provenance로 이동할 수 있어야 한다.](adaptive-presentation-and-navigation.md#system-overview는-heading-언어와-이름에-의존하지-않고-composition에-근거가-연결된-목적-설명과-핵심-동작을-먼저-보여줘야-한다-member-탐색과-집계는-보조-정보로-제공하고-상세에서-정확한-원문과-provenance로-이동할-수-있어야-한다)
- [state-map, runtime-responsibility, interface-table과 acceptance-coverage는 각 source entity 관계에 맞는 flow, responsibility table, interface table과 coverage grouping을 렌더링하고 같은 source-block 카드 목록을 서로 다른 component 이름으로 반복하지 않아야 한다.](adaptive-presentation-and-navigation.md#state-map-runtime-responsibility-interface-table과-acceptance-coverage는-각-source-entity-관계에-맞는-flow-responsibility-table-interface-table과-coverage-grouping을-렌더링하고-같은-source-block-카드-목록을-서로-다른-component-이름으로-반복하지-않아야-한다)
- [Renderer는 최소한 `generic`, `brief.summary`, `spec.system`, `spec.workflow`, `spec.api`, `spec.architecture`, `spec.policy`, `spec.migration`, `plan.execution`, `plan.status`, `project.handbook`, `project.structure`, `project.spec-detail`, `comparison` profile을 제공해야 한다. 새 profile은 공통 component를 조합하고 문서별 template를 복사하지 않아야 한다.](adaptive-presentation-and-navigation.md#renderer는-최소한-generic-briefsummary-specsystem-specworkflow-specapi-specarchitecture-specpolicy-specmigration-planexecution-planstatus-projecthandbook-projectstructure-projectspec-detail-comparison-profile을-제공해야-한다-새-profile은-공통-component를-조합하고-문서별-template를-복사하지-않아야-한다)
- [공통 component grammar는 summary, outline, prose detail, metadata, system-overview, state map, sequence, runtime-responsibility, interface·schema table, decision·exception matrix, relation graph, route·dependency map, progress, Requirement·Acceptance Criterion coverage, provenance, source detail, spec-navigator, project-overview, capability-map, structure-responsibility, spec-index와 developer-information을 제공해야 한다.](adaptive-presentation-and-navigation.md#공통-component-grammar는-summary-outline-prose-detail-metadata-system-overview-state-map-sequence-runtime-responsibility-interfaceschema-table-decisionexception-matrix-relation-graph-routedependency-map-progress-requirementacceptance-criterion-coverage-provenance-source-detail-spec-navigator-project-overview-capability-map-structure-responsibility-spec-index와-developer-information을-제공해야-한다)

### source Mermaid가 없지만 명시된 상태 흐름, ownership table, dependency와 Requirement·Acceptance mapping을 가진 fixture를 build하면 flowchart, structure·responsibility map과 coverage visual이 Derived view로 표시되고 각 node와 edge가 source 값과 일치한다.

검증하는 요구사항:

- [자동 추출한 derived diagram은 selected source에서 기계적으로 계산 가능한 관계만 포함하고, agent가 prose의 명시된 관계를 설명하는 diagram은 근거와 조건을 보존한 composition으로 입력해야 한다.](adaptive-presentation-and-navigation.md#자동-추출한-derived-diagram은-selected-source에서-기계적으로-계산-가능한-관계만-포함하고-agent가-prose의-명시된-관계를-설명하는-diagram은-근거와-조건을-보존한-composition으로-입력해야-한다)
- [Visual Docs는 source에 없는 새로운 런타임 책임, transaction 순서, 상태 전이 또는 설계 결정을 derived diagram에 추가하지 않아야 한다.](adaptive-presentation-and-navigation.md#visual-docs는-source에-없는-새로운-런타임-책임-transaction-순서-상태-전이-또는-설계-결정을-derived-diagram에-추가하지-않아야-한다)
- [Visual Docs의 Signature는 장식이나 고정 component 이름이 아니라 selected source와 intent에 맞는 state map, interface contract, dependency route, exception matrix, Acceptance Criterion coverage 같은 primary reading structure에서 만들어야 한다.](adaptive-presentation-and-navigation.md#visual-docs의-signature는-장식이나-고정-component-이름이-아니라-selected-source와-intent에-맞는-state-map-interface-contract-dependency-route-exception-matrix-acceptance-criterion-coverage-같은-primary-reading-structure에서-만들어야-한다)
- [builder는 실제 렌더링할 source Mermaid와 composition의 derived diagram이 하나 이상일 때만 Mermaid runtime을 포함해야 한다. 포함 여부는 source, 고정 composition과 build option으로 결정하고 diagram 없는 offline snapshot은 외부 network 없이 열려야 한다.](adaptive-presentation-and-navigation.md#builder는-실제-렌더링할-source-mermaid와-composition의-derived-diagram이-하나-이상일-때만-mermaid-runtime을-포함해야-한다-포함-여부는-source-고정-composition과-build-option으로-결정하고-diagram-없는-offline-snapshot은-외부-network-없이-열려야-한다)
- [state-map, runtime-responsibility, interface-table과 acceptance-coverage는 각 source entity 관계에 맞는 flow, responsibility table, interface table과 coverage grouping을 렌더링하고 같은 source-block 카드 목록을 서로 다른 component 이름으로 반복하지 않아야 한다.](adaptive-presentation-and-navigation.md#state-map-runtime-responsibility-interface-table과-acceptance-coverage는-각-source-entity-관계에-맞는-flow-responsibility-table-interface-table과-coverage-grouping을-렌더링하고-같은-source-block-카드-목록을-서로-다른-component-이름으로-반복하지-않아야-한다)
- [Presentation Plan의 node·edge 수 threshold와 자동 visual candidate는 구성의 보조 정보로 사용해야 하며 diagram을 의무화하거나 완성 품질로 간주하지 않아야 한다. Composition은 독자 질문과 관계의 의미에 따라 prose, table 또는 diagram을 선택해야 한다.](adaptive-presentation-and-navigation.md#presentation-plan의-nodeedge-수-threshold와-자동-visual-candidate는-구성의-보조-정보로-사용해야-하며-diagram을-의무화하거나-완성-품질로-간주하지-않아야-한다-composition은-독자-질문과-관계의-의미에-따라-prose-table-또는-diagram을-선택해야-한다)
- [자동 visual candidate 추출은 같은 selected source bytes와 View Context에서 결정적으로 동작해야 한다. 최종 visual의 종류, label과 순서는 고정된 composition과 renderer version에 따라 재현되고 source 근거와 Derived view provenance를 표시해야 한다.](adaptive-presentation-and-navigation.md#자동-visual-candidate-추출은-같은-selected-source-bytes와-view-context에서-결정적으로-동작해야-한다-최종-visual의-종류-label과-순서는-고정된-composition과-renderer-version에-따라-재현되고-source-근거와-derived-view-provenance를-표시해야-한다)
- [Derived visual의 원문 인용과 identifier는 exact source를 유지하고 별도 설명 label은 근거와 의미를 보존해야 한다. 같은 관계의 text 또는 table summary를 제공해 mobile과 print에서도 이해할 수 있어야 한다.](adaptive-presentation-and-navigation.md#derived-visual의-원문-인용과-identifier는-exact-source를-유지하고-별도-설명-label은-근거와-의미를-보존해야-한다-같은-관계의-text-또는-table-summary를-제공해-mobile과-print에서도-이해할-수-있어야-한다)

### 관계형 source가 없는 prose·short-list fixture를 build하면 장식용 diagram과 Mermaid runtime이 생성되지 않고 기존 text reading path와 content coverage가 유지된다.

검증하는 요구사항:

- [관계를 나타내지 않는 단일 문장, 짧은 일차원 목록 또는 두 node 이하의 단순 연결은 diagram으로 강제하지 않고 읽기 쉬운 prose, list 또는 table로 유지해야 한다.](adaptive-presentation-and-navigation.md#관계를-나타내지-않는-단일-문장-짧은-일차원-목록-또는-두-node-이하의-단순-연결은-diagram으로-강제하지-않고-읽기-쉬운-prose-list-또는-table로-유지해야-한다)
- [builder는 실제 렌더링할 source Mermaid와 composition의 derived diagram이 하나 이상일 때만 Mermaid runtime을 포함해야 한다. 포함 여부는 source, 고정 composition과 build option으로 결정하고 diagram 없는 offline snapshot은 외부 network 없이 열려야 한다.](adaptive-presentation-and-navigation.md#builder는-실제-렌더링할-source-mermaid와-composition의-derived-diagram이-하나-이상일-때만-mermaid-runtime을-포함해야-한다-포함-여부는-source-고정-composition과-build-option으로-결정하고-diagram-없는-offline-snapshot은-외부-network-없이-열려야-한다)

### fixed timestamp와 같은 generator를 사용한 동일 source·View Context·고정 composition·Presentation Plan 재build diff는 0이고, shell·component·profile·planner 변경은 desktop 1440px와 mobile 390px의 관련 profile 상태, keyboard, disclosure, overflow와 stable shell geometry 검증을 통과한다.

검증하는 요구사항:

- [같은 selected source bytes, View Context, 고정 composition과 Presentation Plan, generator version, build options와 fixed generated timestamp는 byte-for-byte 같은 HTML을 만들어야 한다. Agent가 composition을 새로 작성한 결과의 동일성은 요구하지 않아야 한다.](adaptive-presentation-and-navigation.md#같은-selected-source-bytes-view-context-고정-composition과-presentation-plan-generator-version-build-options와-fixed-generated-timestamp는-byte-for-byte-같은-html을-만들어야-한다-agent가-composition을-새로-작성한-결과의-동일성은-요구하지-않아야-한다)
- [shell·component·profile·planner 변경의 UI 검증은 desktop 1440px와 mobile 390px에서 각 profile의 typical·empty·long·invalid diagram 상태, keyboard focus, navigation, disclosure, table·diagram overflow와 stable shell geometry를 포함해야 한다.](adaptive-presentation-and-navigation.md#shellcomponentprofileplanner-변경의-ui-검증은-desktop-1440px와-mobile-390px에서-각-profile의-typicalemptylonginvalid-diagram-상태-keyboard-focus-navigation-disclosure-tablediagram-overflow와-stable-shell-geometry를-포함해야-한다)
