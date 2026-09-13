# Forge 플러그인의 Visual Docs 구성·검증 기능 개선 계획

> Execute with the forge executing-plans skill.

Status: completed

**Related Specs:**
- bundle: docs/specs/review-viewer-lifecycle/

**Goal:** Forge 플러그인의 스킬 지침·구성 생성 로직·공통 렌더러·검증 방식을 수정해, 어떤 Brief·Plan·Spec·Project의 Visual Docs 요청에서도 원문에 근거한 이해하기 쉬운 문서를 구성하도록 한다.

**Approach:** 현재 실패를 평가 사례로 고정하고, 설명과 원문을 분리하는 계약 변경안을 검토한다. agent가 작성하는 제한된 composition과 공통 renderer를 격리 fixture에서 검증한 뒤 네 kind와 플러그인 패키지 검증으로 확장한다.

## 현재 범위와 조사 결과

조사와 계획 검토 후 사용자가 Forge 플러그인 수정과 배포를 승인했다. 이 계획의 구현과 패키지 배포를 진행한다. [조사 보고서](../../research/2026-09-13-visual-docs-comprehension-audit.md)가 baseline을 보존한다.

개선 대상은 `plugins/forge/`의 기능과 이를 검증하는 공통 도구다. 기존 프로젝트의 HTML 재생성이나 개별 문서 보정은 이 계획의 구현 목표와 완료 조건에 포함하지 않는다. 테스트용 HTML은 격리 fixture에서 플러그인의 출력 품질을 확인하는 증거로만 생성한다.

현재 구현 기준은 `87cbe25`다. Visual Docs Python 62개가 통과하는 상태에서 목적 heading 의존, system audience·intent 미반영, collapsed source-only plan의 validation 통과를 재현했다. repository와 plugin cache는 같고 사용자 스킬 복사본은 다르다. 보고서가 구체적인 실험과 한계를 보존한다.

사용자가 계획의 목적과 효과를 승인했으며, 정본 변경의 exact mapping은 작업 Delta에 보존했다. 구현은 생성 입력, 설명 허용 범위와 검증 계약을 바꾸므로 Canonical Spec impact가 있고 여러 계층이 연결되므로 execution complexity가 높다. Task 1에서 승인된 Spec Delta를 적용·검증했다. 현재 governing links는 보존할 기준과 변경을 검토할 기준이며, 기존 기준의 변경과 새 근거 기반 설명 계약을 함께 검증한다.

## Global Constraints

- 특정 게임, 도메인, 제목 alias 또는 profile 추가만으로 일반적인 문제를 해결했다고 판단하지 않는다.
- Brief·Plan·Spec·Project의 source ownership과 요청형 생성, 원문 상세, provenance, freshness, deep link를 유지한다. 새로운 combined kind를 추가하지 않는다.
- 설명을 만들기 위해 Canonical Spec에 불필요한 장식용 구조나 설명을 강제로 추가하지 않는다. source 사실이 부족하면 누락을 알린다.
- agent는 근거 있는 설명과 구성을 데이터로 작성한다. 생성 HTML·문서별 CSS·script는 직접 작성하지 않는다.
- 전면 재작성 전에 작은 완성 경로로 효과를 입증한다. 기존 parser, renderer, 탐색·접근성 코드는 재사용 가능성을 먼저 판단한다.
- 새 의무 조건, 인과 관계, 책임, 예외, 확정 상태를 발명하지 않는다. schema validation과 의미 검토의 한계를 구분한다.
- 외부 API 호출이나 별도 서비스, 모델별 강제 설정을 공통 실행 조건으로 추가하지 않는다. 현재 agent가 composition 작성 역할을 담당한다.
- 실제 사용자 설치 변경과 기존 프로젝트 Visual Docs 갱신은 이 개선 계획의 범위에서 제외한다. 사용자가 추가 승인한 commit·push·release는 검증과 version gate를 거쳐 진행한다.

## Verification Scope

세 검증을 분리한다. 기계적 검증은 스키마·출처·참조·누락·재현성을, 의미 검토는 조건·예외·의무 강도·수치·상태를, 읽기 검증은 출력만으로 핵심 질문에 답할 수 있는지를 확인한다. 하나의 통과를 다른 검증의 성공으로 대신하지 않는다.

기존 회귀는 유지한다. 새 구현 범위의 Acceptance를 Task 1에서 최종 연결하며 이 계획으로 bundle 전체를 implemented로 변경하지 않는다. 자료별 질문과 기대 답은 생성 전에 고정하고, 문서가 단순하면 간단한 구성도 통과시킨다. 모든 자료에 같은 섹션이나 diagram을 요구하지 않는다.

## 평가 자료

| 사례 | 독자가 확인할 핵심 | 반드시 잡아야 할 실패 |
|---|---|---|
| 짧은 Brief | 목표, 범위, 완료 조건 | 불필요하게 큰 문서와 장식 diagram |
| 실행 Plan | 다음 행동, 의존 작업, 완료 증거 | Task 목록을 옮겨 놓고 순서·막힘을 설명하지 않음 |
| prose로 쓴 workflow Spec | 정상 동작과 분기·예외 | 화살표 문법이 없다는 이유로 동작 설명이 사라짐 |
| 정책·비교 Spec | 조건별 적용 차이와 예외 | 서로 다른 조건을 같은 규칙으로 요약 |
| 장문 system Spec | 전체 목적, 주요 책임과 상호작용 | 파일·Requirement 수가 설명을 대신함 |
| Project Handbook | 목적, 기능과 책임 연결 | 폴더 나열·source code로 소유권 추측 |
| 서로 다른 독자·요청 목적 | 해당 독자가 판단할 내용 | label만 바뀌고 실질적 필요가 반영되지 않음 |
| 평가 전용 미사용 자료 | 새로운 도메인에서도 핵심 이해 | fixture 제목·schema 패턴·특정 도메인에만 맞음 |

한국어·영어, source diagram 있음·없음, 충분한 source·불충분한 source를 위 사례에 교차 배치한다. PERKSTORM은 실제 실패 사례 하나로 사용하고 CI fixture는 자체 완결 자료로 만든다. 독자나 목적이 실제로 요구를 바꾸지 않는 자료에는 인위적인 차이를 강제하지 않는다.

### Task 1: 설명 문서의 계약과 평가 기준을 확정한다

Governing statements:

- [서로 다른 독자 목적을 가진 동일 자료와 짧은 Brief를 composition으로 생성하면 필요한 질문과 답이 첫 읽기 경로에 반영되고 짧은 자료에는 불필요한 diagram과 고정 섹션이 강제되지 않는다.](../../specs/review-viewer-lifecycle/source-grounded-composition.md#서로-다른-독자-목적을-가진-동일-자료와-짧은-brief를-composition으로-생성하면-필요한-질문과-답이-첫-읽기-경로에-반영되고-짧은-자료에는-불필요한-diagram과-고정-섹션이-강제되지-않는다)
- [Composition과 Presentation Plan fixture에 executable markup, unknown component, dangling reference, 누락 원문과 오래된 source·context를 주입하면 validator가 실패한다. 근거가 연결된 별도 설명은 입력으로 허용하되 잘못된 의미를 기계적 통과만으로 승인하지 않는다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#composition과-presentation-plan-fixture에-executable-markup-unknown-component-dangling-reference-누락-원문과-오래된-sourcecontext를-주입하면-validator가-실패한다-근거가-연결된-별도-설명은-입력으로-허용하되-잘못된-의미를-기계적-통과만으로-승인하지-않는다)

**Files:** `docs/specs/review-viewer-lifecycle/`의 root·adaptive-presentation·source-selection·project-handbook 계약, `.forge/work/visual-docs-comprehension/spec-delta.md`, 이 계획.

**Dependencies:** 조사 결과. **Approval gate:** 사용자가 계획에 따른 수정·배포를 승인했고 해당 의미의 계약 변경안을 적용·검증했다.

원문 인용과 근거 있는 설명의 경계, 첫 읽기 경로와 전체 원문 접근의 차이, composition 입력·수명·재현성, fallback 품질 상태를 변경안으로 작성한다. 기존 고정 profile·threshold·요약 순서와 충돌하는 조항을 함께 정리한다. 단순히 새 조항을 덧붙이지 않는다.

- [x] **Step 1: 현재 계약과 새 목적의 충돌을 exact statement 단위로 제안한다.**
- [x] **Step 2: 평가 자료별 핵심 질문·기대 답·중대한 오해를 출력 생성 전에 정의한다.**
- [x] **Step 3: 승인된 변경을 적용하고 관련 링크와 계획의 Acceptance 연결을 갱신한다.**

**Verification:** 사람이 읽을 수 있는 Spec Delta, 보존/변경 구분, expected-answer rubric과 valid bundle. **Recovery:** 승인 전에는 제안 문서만 유지한다.

### Task 2: 최소 composition 입력과 근거 검증을 연결한다

Governing statements:

- [공개 CLI로 준비한 source·context에 맞는 composition을 입력하면 공통 renderer 출력이 생성되고, source 또는 context를 변경한 입력과 executable markup은 output 쓰기 전에 거부된다.](../../specs/review-viewer-lifecycle/source-grounded-composition.md#공개-cli로-준비한-sourcecontext에-맞는-composition을-입력하면-공통-renderer-출력이-생성되고-source-또는-context를-변경한-입력과-executable-markup은-output-쓰기-전에-거부된다)
- [같은 source와 고정 composition·generator·build options를 재사용하면 동일 출력이 생성되고, composition 없는 source-browser와 읽기 검증이 남은 설명 문서의 상태가 구분된다. Source나 composition 변경만으로 자동 갱신되지 않는다.](../../specs/review-viewer-lifecycle/source-grounded-composition.md#같은-source와-고정-compositiongeneratorbuild-options를-재사용하면-동일-출력이-생성되고-composition-없는-source-browser와-읽기-검증이-남은-설명-문서의-상태가-구분된다-source나-composition-변경만으로-자동-갱신되지-않는다)
- [Visual Docs tooling fixture에서 Markdown source와 View Context를 준비하고 composition을 공개 CLI로 전달하면 Semantic IR, 검증된 구성, manifest와 HTML이 만들어진다. 원문 밖 의미는 별도 의미 검토로 확인하고 개별 View 검증은 자료에 필요한 범위로 수행한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#visual-docs-tooling-fixture에서-markdown-source와-view-context를-준비하고-composition을-공개-cli로-전달하면-semantic-ir-검증된-구성-manifest와-html이-만들어진다-원문-밖-의미는-별도-의미-검토로-확인하고-개별-view-검증은-자료에-필요한-범위로-수행한다)
- [fixed timestamp와 같은 generator를 사용한 동일 source·View Context·고정 composition·Presentation Plan 재build diff는 0이고, shell·component·profile·planner 변경은 desktop 1440px와 mobile 390px의 관련 profile 상태, keyboard, disclosure, overflow와 stable shell geometry 검증을 통과한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#fixed-timestamp와-같은-generator를-사용한-동일-sourceview-context고정-compositionpresentation-plan-재build-diff는-0이고-shellcomponentprofileplanner-변경은-desktop-1440px와-mobile-390px의-관련-profile-상태-keyboard-disclosure-overflow와-stable-shell-geometry-검증을-통과한다)

**Files:** `plugins/forge/skills/visual-docs/scripts/review_planner.py`, `build_review_viewer.py`, `review_renderer.py`; 필요하면 작은 composition schema/validator 모듈과 그 테스트.

**Dependencies:** Task 1.

**Interfaces:** 이름은 Task 1에서 확정한다. 입력에는 source manifest/hash, 요청 목적·독자, 주요 질문, 순서가 있는 설명 section, 표현 선택, claim별 source ref, 필요시 명시적 node·edge·조건과 예시의 값/가정을 포함한다. 기존 IR을 바탕으로 원문 상세와 설명을 연결한다. 실행 가능한 markup은 허용하지 않는다.

공개 CLI에서 composition을 입력받는 경로와 read-only preflight를 실제로 연결한다. 스키마, source 변경, dangling ref, 누락된 근거, 지원하지 않는 표현을 진단한다. 유효한 source ref는 의미 정확성의 자동 증명이 아니라는 점을 유지한다. 의미 검토 결과와 기계적 통과를 분리한다.

- [x] **Step 1: 현재 source-only 통과와 공개 plan 입력 부재를 관찰 가능한 회귀 사례로 고정한다.**
- [x] **Step 2: 근거 있는 설명 데이터를 renderer까지 전달하고 preflight 결과를 구성 내용으로 검토 가능하게 만든다.**
- [x] **Step 3: 고정 composition 재build 동일성, source 변경 시 stale/재검토, 잘못된 입력 거부를 확인한다.**

**Verification:** 공개 진입점으로 하나의 입력이 끝까지 전달되고 source-only 보존 결과를 설명 문서 완료로 판정하지 않는다. **Recovery:** 기존 renderer 경로를 제거하지 않고 격리 fixture에서 먼저 검증한다.

### Task 3: 서로 다른 자료 두 개로 설명 생성부터 읽기까지 검증한다

Governing statements:

- [조건과 예외를 가진 prose workflow와 정책 fixture를 설명 문서로 생성하면 쉬운 설명과 비교에서 원문의 의미와 역할이 유지되고 각 근거와 exact 원문으로 이동할 수 있다. 가정이 있는 계산 예시는 source 값과 가정을 구분한다.](../../specs/review-viewer-lifecycle/source-grounded-composition.md#조건과-예외를-가진-prose-workflow와-정책-fixture를-설명-문서로-생성하면-쉬운-설명과-비교에서-원문의-의미와-역할이-유지되고-각-근거와-exact-원문으로-이동할-수-있다-가정이-있는-계산-예시는-source-값과-가정을-구분한다)
- [원문 coverage만 충족한 접힌 원문 화면과 유효한 근거가 붙었지만 의미가 틀린 설명을 평가하면 각각 질문 누락과 의미 왜곡으로 실패하고 schema 통과가 완료 증거로 사용되지 않는다.](../../specs/review-viewer-lifecycle/source-grounded-composition.md#원문-coverage만-충족한-접힌-원문-화면과-유효한-근거가-붙었지만-의미가-틀린-설명을-평가하면-각각-질문-누락과-의미-왜곡으로-실패하고-schema-통과가-완료-증거로-사용되지-않는다)
- [목적 설명이 있는 Spec과 plan의 Overview를 열면 목적과 핵심 내용이 집계보다 먼저 보이고 390px에서도 숫자 카드가 첫 읽기 화면을 차지하지 않으며 요약과 상세 수치가 같은 source 집계 기준과 일치한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#목적-설명이-있는-spec과-plan의-overview를-열면-목적과-핵심-내용이-집계보다-먼저-보이고-390px에서도-숫자-카드가-첫-읽기-화면을-차지하지-않으며-요약과-상세-수치가-같은-source-집계-기준과-일치한다)

**Files:** `visual-docs/SKILL.md`, 필요한 구성 작성 reference, `review_components.py`, 격리 평가 fixture. Shell 수정이 필요할 때만 `writing-specs/assets/viewer-template.html`을 포함한다.

**Dependencies:** Task 2.

agent가 원문을 읽어 주요 질문과 답, 필요한 배경, 설명 순서, 표현과 근거를 작성하도록 한다. parser의 heading alias나 domain profile이 설명의 유일한 근거가 되지 않게 한다. prose workflow와 조건 비교 자료로 먼저 검증하며, 하나는 한국어이고 둘 다 제작된 diagram을 원본 필수 조건으로 삼지 않는다.

- [x] **Step 1: 평가 질문을 기준으로 현재 출력과 제안 composition의 차이를 기록한다.**
- [x] **Step 2: 공통 prose·table·diagram 표현으로 두 자료를 끝까지 생성하고 중요한 답을 먼저 읽게 한다.**
- [x] **Step 3: 출력만 보는 검토로 질문 응답과 의미 보존을 확인하고 실패한 설명/표현을 수정한다.**

**Verification:** 두 자료에서 주요 질문에 답할 수 있고 예외·조건 왜곡이 없으며 근거로 이동한다. desktop·narrow에서 실제 읽기 순서도 확인한다. **Recovery:** 효과가 입증되지 않으면 Task 4로 확대하지 않고 composition 계약과 편집 절차를 재검토한다.

### Task 4: 네 kind와 다양한 요청으로 확대한다

Governing statements:

- [서로 다른 독자 목적을 가진 동일 자료와 짧은 Brief를 composition으로 생성하면 필요한 질문과 답이 첫 읽기 경로에 반영되고 짧은 자료에는 불필요한 diagram과 고정 섹션이 강제되지 않는다.](../../specs/review-viewer-lifecycle/source-grounded-composition.md#서로-다른-독자-목적을-가진-동일-자료와-짧은-brief를-composition으로-생성하면-필요한-질문과-답이-첫-읽기-경로에-반영되고-짧은-자료에는-불필요한-diagram과-고정-섹션이-강제되지-않는다)
- [조건과 예외를 가진 prose workflow와 정책 fixture를 설명 문서로 생성하면 쉬운 설명과 비교에서 원문의 의미와 역할이 유지되고 각 근거와 exact 원문으로 이동할 수 있다. 가정이 있는 계산 예시는 source 값과 가정을 구분한다.](../../specs/review-viewer-lifecycle/source-grounded-composition.md#조건과-예외를-가진-prose-workflow와-정책-fixture를-설명-문서로-생성하면-쉬운-설명과-비교에서-원문의-의미와-역할이-유지되고-각-근거와-exact-원문으로-이동할-수-있다-가정이-있는-계산-예시는-source-값과-가정을-구분한다)
- [Brief, Plan과 Spec fixture를 각각 `brief`, `plan`, `spec` kind로 build하면 서로 다른 `.forge/visual-docs/<view-id>/view.html`이 생성되고 Git 추적 파일은 변경되지 않으며 각 View가 kind에 맞는 primary composition과 source provenance를 표시한다.](../../specs/review-viewer-lifecycle/human-readable-review-viewer.md#brief-plan과-spec-fixture를-각각-brief-plan-spec-kind로-build하면-서로-다른-forgevisual-docsview-idviewhtml이-생성되고-git-추적-파일은-변경되지-않으며-각-view가-kind에-맞는-primary-composition과-source-provenance를-표시한다)

**Files:** `review_sources.py`, `review_ir.py`, `review_planner.py`, `review_components.py`, `review_renderer.py` 중 필요한 부분; Brief·Plan·Spec·Project fixture.

**Dependencies:** Task 3의 두 자료 읽기 검증.

기존 kind별 source ownership과 전체 상세 탐색을 유지하면서 첫 읽기 경로는 composition을 따른다. Project Map에 없는 책임을 만들지 않고 Plan context를 실행 증거로 오인하지 않게 한다. comparison 자료의 관계를 추측하지 않는다. 빈 primary section과 반복된 카드/집계는 제거하거나 보조 경로로 옮긴다.

- [x] **Step 1: 평가 자료의 Brief·Plan·장문 system·Project 입력을 지원한다.**
- [x] **Step 2: 요청 목적·독자 변경이 필요한 사례에서 설명·순서의 실질적 차이를 확인한다.**
- [x] **Step 3: source가 부족한 경우 사실을 만들지 않으며 짧은 자료는 간결하게 제공하는지 확인한다.**

**Verification:** 네 kind에서 핵심 답, source ownership, 전체 상세 접근과 provenance를 유지한다. **Recovery:** kind별 진입 경로를 순차 전환하며 실패한 kind를 검증 완료로 표시하지 않는다.

### Task 5: 이해 성과와 의미 충실도를 회귀 기준으로 만든다

Governing statements:

- [원문 coverage만 충족한 접힌 원문 화면과 유효한 근거가 붙었지만 의미가 틀린 설명을 평가하면 각각 질문 누락과 의미 왜곡으로 실패하고 schema 통과가 완료 증거로 사용되지 않는다.](../../specs/review-viewer-lifecycle/source-grounded-composition.md#원문-coverage만-충족한-접힌-원문-화면과-유효한-근거가-붙었지만-의미가-틀린-설명을-평가하면-각각-질문-누락과-의미-왜곡으로-실패하고-schema-통과가-완료-증거로-사용되지-않는다)
- [생성 전 고정한 질문과 기대 답으로 Brief·Plan·Spec·Project 및 작성에 쓰지 않은 자료의 출력을 평가하면 질문별 정답·오답·누락과 원문 탐색 의존이 기록되고 agent 평가와 실제 인간 관찰이 별도로 보고된다.](../../specs/review-viewer-lifecycle/source-grounded-composition.md#생성-전-고정한-질문과-기대-답으로-briefplanspecproject-및-작성에-쓰지-않은-자료의-출력을-평가하면-질문별-정답오답누락과-원문-탐색-의존이-기록되고-agent-평가와-실제-인간-관찰이-별도로-보고된다)
- [Visual Docs tooling 변경 fixture는 desktop 1440px와 mobile 390px에서 숨겨진 상세 선택, 빠른 탐색, deep link, checkbox persistence, diagram, table과 print의 필요한 상태를 통과한다. 유효한 Mermaid에는 표시된 오류가 없고 개별 View 생성 fixture도 요청 범위의 읽기·표시 확인을 수행한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#visual-docs-tooling-변경-fixture는-desktop-1440px와-mobile-390px에서-숨겨진-상세-선택-빠른-탐색-deep-link-checkbox-persistence-diagram-table과-print의-필요한-상태를-통과한다-유효한-mermaid에는-표시된-오류가-없고-개별-view-생성-fixture도-요청-범위의-읽기표시-확인을-수행한다)

**Files:** `visual-docs/tests/`의 unit·CLI·browser·평가 fixture, `scripts/tests/test-forge-artifact-contract.sh`, 필요한 CI 진입점, `docs/evidence/visual-docs-comprehension.md`.

**Dependencies:** Task 4. 기계적 회귀는 Task 2부터 각 변경과 함께 추가한다.

기존 coverage·출처·탐색 검증을 유지하고 제목만 다른 동일 내용, 조건부 흐름, 근거는 존재하지만 내용은 틀린 설명, 불완전 source를 검사한다. 작성자가 알고 있는 답을 스스로 설명하는 것만으로 완료하지 않는다. 독립 검토자는 출력만 보고 질문에 답하고 별도 기대 답과 비교한다. 새 agent 평가가 가능하면 유지보수 스킬의 pressure test로 실행하고, 인간 독자 관찰과 agent 평가를 구분해 기록한다.

- [x] **Step 1: 제작에 사용하지 않은 평가 자료로 전후 질문 응답과 원문 탐색 의존을 비교한다.**
- [x] **Step 2: 잘못된 의미를 중대한 실패로 처리하고, 질문 누락을 수정하며 검사 개수·diagram 수를 성과로 쓰지 않는다.**
- [x] **Step 3: desktop·390px·긴 표·분기·print·keyboard·deep link·offline·freshness와 관련 회귀를 검증한다.**

**Verification:** 핵심 질문 응답, 주요 조건·예외·확정 상태의 정확성, 근거 이동이 충족되어야 한다. 지침 문구 존재만 확인한 pressure test를 제품 이해 검증으로 보고하지 않는다. **Recovery:** 실패 자료, 오해와 원인을 evidence에 남기고 관련 단계로 돌아간다.

### Task 6: 플러그인 패키지에서도 수정된 기능이 동작하는지 검증한다

Governing statements:

- [같은 source와 고정 composition·generator·build options를 재사용하면 동일 출력이 생성되고, composition 없는 source-browser와 읽기 검증이 남은 설명 문서의 상태가 구분된다. Source나 composition 변경만으로 자동 갱신되지 않는다.](../../specs/review-viewer-lifecycle/source-grounded-composition.md#같은-source와-고정-compositiongeneratorbuild-options를-재사용하면-동일-출력이-생성되고-composition-없는-source-browser와-읽기-검증이-남은-설명-문서의-상태가-구분된다-source나-composition-변경만으로-자동-갱신되지-않는다)
- [fixed timestamp와 같은 generator를 사용한 동일 source·View Context·고정 composition·Presentation Plan 재build diff는 0이고, shell·component·profile·planner 변경은 desktop 1440px와 mobile 390px의 관련 profile 상태, keyboard, disclosure, overflow와 stable shell geometry 검증을 통과한다.](../../specs/review-viewer-lifecycle/adaptive-presentation-and-navigation.md#fixed-timestamp와-같은-generator를-사용한-동일-sourceview-context고정-compositionpresentation-plan-재build-diff는-0이고-shellcomponentprofileplanner-변경은-desktop-1440px와-mobile-390px의-관련-profile-상태-keyboard-disclosure-overflow와-stable-shell-geometry-검증을-통과한다)

**Files:** `scripts/install.sh`, `scripts/tests/test-forge-visual-docs-install.sh`, 필요한 manifests·README·build manifest provenance와 테스트.

**Dependencies:** Task 5.

repository와 plugin package를 구분할 수 있는 generator version·entry path 또는 동등한 provenance를 기록하는 방법을 확정한다. 패키지에 필요한 스킬·reference·script·asset이 모두 포함되는지 격리 설치로 검사한다. 사용자 환경의 복사본 갱신이나 기존 프로젝트 HTML 재생성을 완료 조건으로 삼지 않는다.

- [x] **Step 1: 격리 설치본으로 동일 source와 고정 composition의 결과를 검증한다.**
- [x] **Step 2: 패키지의 스킬·reference·script·asset 누락과 오래된 생성기 실행을 식별할 수 있는지 확인한다.**
- [x] **Step 3: 플러그인 validator와 관련 설치 회귀를 통과하고 변경 내용·검증 근거를 기록한다.**

**Verification:** 저장소와 격리 패키지에서 같은 수정 기능이 동작하고 모든 필요한 파일이 포함된다. 실제 배포는 별도 요청 시 유지보수 스킬의 release gate를 따른다. **Recovery:** 격리 fixture에서 패키징 누락을 수정하며 사용자 설치는 변경하지 않는다.

## 완료 판단과 실행 순서

Task 1 → 2 → 3을 첫 검토 지점으로 삼는다. 두 종류의 문서에서 이해 성과가 확인된 뒤 Task 4 → 5 → 6으로 확대한다. 이 순서가 실패하면 profile을 더 추가하며 진행하지 않는다.

플러그인 수정 완료에는 기계적 회귀, source fidelity, 질문 기반 읽기 검증과 격리 패키지 검증이 모두 필요하다. 기존 프로젝트 HTML의 재생성 여부는 완료 기준이 아니다. 인간 검토를 하지 않았다면 인간 이해 성과를 확인했다고 쓰지 않는다. browser가 없으면 표시 검증이 미완료임을 보고한다.

## Progress

- 2026-09-13: 조사 완료. 코드·계약·수정 이력·테스트 기대값 검토, Python 62개 PASS, 비교 probe 결과를 조사 보고서에 보존했다. 개선 계획만 작성했으며 Task 1–6의 구현은 미착수다.
- 2026-09-13: 사용자 정정에 따라 수정 대상을 Forge 플러그인으로 명시했다. 기존 프로젝트 HTML 재생성과 사용자 환경 설치를 구현 범위·완료 조건에서 제외하고 Task 6을 격리 패키지 검증으로 한정했다.

- 2026-09-13: 사용자 수정·배포 승인. Task 1 계약 적용 및 writer validation PASS. Tasks 2–4의 composition CLI·공통 renderer·네 kind 구현과 unit/CLI 74 tests PASS. Task 5 독립 작성·읽기 평가와 browser, Task 6 패키지 회귀 진행 중.

- 2026-09-13: Tasks 1–6 구현과 로컬 검증 완료. Brief 복수 block 충돌 회귀까지 포함한 Visual Docs Python 76개, Spec Python 66개, browser 18개, 세 export 패키지와 관련 policy 회귀 PASS. 독립 작성과 blind reader 평가 6개 질문 모두 일치. 증거: `docs/evidence/visual-docs-comprehension.md`. Forge 0.1.25의 commit·PR·원격 CI·Marketplace 배포를 사용자 승인 범위에서 진행한다.
