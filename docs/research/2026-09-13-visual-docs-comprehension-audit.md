# Visual Docs가 이해하기 쉬운 문서로 이어지지 않는 이유

작성: 2026-09-13. 조사 기준: `87cbe25`와 변경 없는 작업 트리. 범위는 조사와 개선 계획이며 스킬, 생성기, 정본, 설치 상태를 변경하지 않았다.

## 판단

Visual Docs는 원문을 안전하게 보존하고 탐색하는 기능을 갖췄지만, 독자가 알아야 할 내용을 선정하고 설명 순서를 설계하는 기능은 부족하다. 유형별 구성 선택과 일부 문법의 관계 추출이 그 역할을 대신하고 있다. 이 상태에서 profile, diagram, UI 검사만 추가하면 특정 사례는 좋아져도 일반적인 작업에서 이해하기 쉬운 문서를 보장하기 어렵다.

문제는 세 층으로 나뉜다.

1. **목적과 계약:** 독자 중심 구성을 요구하면서도 설명 입력은 기존 원문 참조와 고정 key로 제한한다. 원문 상세의 보존과 설명의 충실도를 분리하지 못했다.
2. **구현과 검증:** 내용을 보존하는 검사와 표현 컴포넌트 검사가 중심이다. 출력만 읽은 독자가 핵심 질문에 답할 수 있는지 확인하는 검증이 부족하다.
3. **적용 경로:** 저장소와 plugin cache는 같은 코드지만 사용자 스킬 복사본은 이전 코드다. 저장소 수정이 실제 사용 경로에 반영되었는지 별도 확인이 필요하다.

모든 책임을 버전 차이로 설명할 수 없다. 최신 저장소 코드에서도 아래 문제가 재현됐다.

## 확인한 범위와 한계

- `visual-docs/SKILL.md`, source loader, Semantic IR, planner, validator, component renderer, builder CLI를 읽었다.
- `docs/specs/review-viewer-lifecycle/`을 공유 parser로 inspect했다. 상태 `approved`, diagnostics 0이었다.
- 계획 007–009, 관련 commit 이력, 기존 pressure-test 기록, Python·browser 테스트의 기대 결과를 검토했다.
- 현재 Python 회귀 62개를 실행했고 모두 통과했다.
- 실제 PERKSTORM bundle과 격리 fixture로 제목, audience, intent, 표현 문법, validation을 비교했다. 원본은 변경하지 않았다.
- 이번 조사에서 새 HTML을 생성하거나 기존 HTML을 갱신하지 않았다. 기존 대화에서 `file://` 브라우저 열기가 정책에 의해 차단되었으며 우회하지 않았다. 아래 결과는 parser·planner·메모리상의 markup 관찰이다. 실제 화면, 모바일 가독성, 인간 독자의 이해 성과를 새로 검증한 결과는 아니다.

## 재현 결과

| 질문 | 실험과 관찰 | 의미 |
|---|---|---|
| 최신 코드로도 실제 목적 설명이 누락되는가 | 실제 bundle 10개 문서를 읽으면 `spec.system`이 선택되지만 overview lede가 없다. root 목적 heading은 `목적`이다. | 최신 버전으로 재생성하는 것만으로 목적 중심 개요가 보장되지 않는다. |
| 동일한 목적 설명의 제목만 바꾸면 달라지는가 | fixture에서 `Overview`는 lede 있음, `목적`은 없음. 본문은 동일하다. | `_system_overview`의 `heading_path == ("Overview",)` 조건에 의존한다. |
| 독자가 구성에 반영되는가 | 같은 system fixture의 `product`, `engineering`, `operations`에서 Presentation Plan 전체가 동일하다. | `audience`는 전달·기록되지만 현재 planner의 구성 선택에 사용되지 않는다. |
| 검토 목적이 읽기 경로에 반영되는가 | 같은 system fixture에서 `review`, `approval`, `implementation`은 question key만 다르고 component plan과 `render_components` 결과가 동일하다. | 일부 workflow/plan intent 분기는 있지만 system 전반의 목적별 구성이 구현된 것은 아니다. |
| 원문 보존 검사가 이해 가능한 구성을 보장하는가 | 모든 block을 단일 collapsed `source-detail`에 할당한 `generic` plan을 직접 validator에 넣으면 diagnostics 0이다. | 100% coverage와 schema 통과는 독자가 읽을 설명의 존재를 증명하지 못한다. CLI가 이 plan을 자동 선택했다는 뜻은 아니다. |
| 글로만 된 흐름을 가공하는가 | `접수 → 검토 → 완료`는 `ordered-flow` 1개, `접수 후 검토하고, 검토가 끝나면 완료한다.`는 0개다. | 현재 extractor는 명시된 특정 표기만 변환한다. 이는 현재의 보수적 계약에 부합하지만 일반적인 문장 해석 기능은 아니다. |
| 수정된 코드가 실제 설치에 반영됐는가 | `SKILL.md`와 `review_planner.py` SHA-256은 repository=plugin cache, user install만 다르다. | 중복 진입점의 차이는 확인했다. 과거 HTML 생성에 사용한 정확한 executable 경로는 manifest만으로 확정할 수 없다. |

추가 코드 관찰:

- `review_components.py::_summary`는 현재도 파일 label과 `blocks`, `entities` 개수를 출력한다.
- `_orientation`은 문서 내용이나 intent와 무관하게 “각 항목을 source path로 추적합니다”라는 고정 설명을 붙인다.
- `review_planner.py::PROFILE_COMPONENTS`와 `_INTENT_COMPONENTS`가 읽기 순서를 대부분 결정한다.
- `PresentationPlan`은 profile, question key, component/ref/orientation/disclosure만 받는다. 문서별 근거 있는 설명, 독자의 질문, 핵심 조건을 표현할 데이터 구조가 없다.
- 내부 renderer는 `presentation_plan` 인수를 받을 수 있지만 공개 builder CLI에는 agent가 작성한 plan을 읽는 옵션이 없고 `_context_and_plan`이 항상 자동 selector를 호출한다. 스펙의 “agent가 제안한 plan” 경로가 공개 생성 절차로 연결되지 않았다.
- validator는 reference 존재·중복·coverage 등을 검사한다. 유효한 참조가 붙은 설명이 실제 의미를 보존하는지 판정하는 기능은 아니다.

코드 위치: [planner](../../plugins/forge/skills/visual-docs/scripts/review_planner.py), [components](../../plugins/forge/skills/visual-docs/scripts/review_components.py), [IR](../../plugins/forge/skills/visual-docs/scripts/review_ir.py), [builder](../../plugins/forge/skills/visual-docs/scripts/build_review_viewer.py).

## 여러 번의 수정으로 해결되지 않은 이유

| 변경 | 해결한 범위 | 남은 범위 |
|---|---|---|
| `d6bc839`, `1642bb0` 및 후속 탐색 수정 | 네 document kind, Project Handbook, 탐색 구조 | 원본 문서 구조와 독자의 이해 구조를 구분하는 일반적인 편집 과정 |
| `c551ae9`, 계획 007 | custom system subtype의 generic fallback, system component와 탐색 | subtype에 상관없이 내용으로 구성하는 방식 |
| `d7ffdae` | 생성 전 profile·빈 component를 확인하는 스킬 지침 | 렌더러의 목적 적합성 검사와 읽기 성과 |
| `b7b1f7f`, 계획 008 | 화살표·표·명시적 link를 derived visual로 변환 | 일반 prose에 표현된 동작, 조건, 예외를 근거와 함께 설명하는 과정 |
| `0df340b` 계열, 계획 009 | 도표 runtime, 목적 먼저 표시, 실제 읽기 검증 지침 | 목적 추출의 heading 의존, 실제 의미를 평가하는 다양한 입력 |
| `a5ffaff`, `c1a4654` | 글자 역할 검토와 절차 간소화 | 출력 내용의 선정·연결·설명 책임 |

기존 pressure test는 자동 생성 금지, 수동 HTML 금지, fallback 중단, node 수 threshold 같은 규칙 준수를 주로 평가했다. 초기 기록에는 build 1회와 추가 browser 검사 금지도 있었다. 현재 스킬은 그 제한을 수정했으므로 과거 제한이 지금도 유효하다고 해석하면 안 된다.

현행 browser 테스트에는 목적 lede 표시, 요약과 diagram 순서, 모바일 overflow, 검색·키보드·deep link 등 유용한 검증이 있다. 그러나 fixture가 `Overview`, 화살표, 정해진 table header를 제공한다. 이 테스트의 성공을 일반적인 한국어 prose나 새로운 작업에서도 이해하기 쉽다는 증거로 확대할 수 없다.

반복된 실패의 공통 원인은 **읽기 목적에 맞는 설명을 만드는 일을 고정 profile과 기계적 추출에 맡기고, 그 결과를 component 존재와 source coverage 중심으로 승인한 것**으로 판단한다. 사용자 스킬 복사본의 차이는 이 문제와 별개의 적용 경로 문제다.

## 바꿔야 할 설계

입력의 진실과 출력의 설명을 분리한다.

1. source loader와 Semantic IR은 원문, 조건, 상태, 출처와 정확한 식별자를 보존한다.
2. agent는 요청과 원문을 읽고 독자의 핵심 질문, 필요한 배경, 설명 순서, 비교·흐름·예시를 선정한다.
3. 이 판단을 원문 근거가 연결된 제한된 composition 데이터로 저장한다. HTML/CSS/script를 작성하지 않는다.
4. 공통 renderer가 composition을 표현한다. profile은 시작점이며 필수 문서 순서가 아니다.
5. 기계적 검증, 의미 검토, 실제 읽기 검증을 구분해 수행한다.

설명에는 원문을 쉬운 말로 풀기, 여러 문서에 명시된 사실 묶기, 명시된 식에 값을 대입한 예시를 허용하는 방향을 제안한다. 단, 원문의 의무 강도·조건·예외·수치·확정 상태를 보존하고 각 설명에 근거를 연결한다. 정보가 부족하면 불명확함을 드러내며, 시각화를 위해 새 정책이나 원본 설명을 만들어 넣지 않는다.

참조 유효성만으로 의미 충실도를 자동 보장한다고 주장하지 않는다. 예시는 source 값과 가정을 구분하고, 조건부 경로를 무조건적인 순서로 바꾸지 않는다. 인용된 정본 문장은 원문 그대로 별도 접근 가능하게 한다.

재현성은 고정된 source와 저장된 composition, renderer version, build options에 대해 보장한다. 매번 agent가 새 설명을 작성해도 같은 bytes가 나온다는 요구는 두지 않는다. source 변경 시 관련 composition을 stale로 다루고 사용자 요청 없이 갱신하지 않는다.

## 정본과 조정할 내용

다음은 변경 제안이며 이번 조사에서 승인된 계약을 수정하지 않았다.

| 현재 계약·지침 | 조정 제안 |
|---|---|
| `Presentation Plan`은 기존 ref와 key만 허용 | source-grounded explanation과 읽기 목적을 검토 가능한 데이터로 허용하고 공개 build 입력으로 연결 |
| source 밖 prose 금지, 규범적 문장 paraphrase 금지 | 원문 인용은 exact 유지. 별도 설명은 근거·의무 강도·조건 보존을 전제로 허용. 근거 없는 의미는 계속 금지 |
| 같은 source와 context에서 visual candidate 결정적 선택 | 기계적 추출은 보조 기능으로 유지. 승인/검토된 composition을 고정한 렌더링을 재현성 경계로 사용 |
| 정해진 node 수와 우선순위로 diagram 포함 의무 | 이해에 도움이 되는 관계를 표현하고, 작은 문서는 간단한 설명만으로 충족 가능 |
| 고정 profile 순서와 원문을 접는 전역 정책 | 독자의 질문에 따라 순서·밀도·표현을 선택. 주요 답을 접힌 원문 탐색에 의존시키지 않음 |
| 전체 source block coverage 100% | 원문 상세의 접근 가능성은 유지. 첫 읽기 경로에 모든 원문과 수치를 나열할 의무와 분리 |
| generic 성공 fallback과 일부 quality stop 지침 병존 | 원문 보존용 fallback과 검증된 설명 문서의 상태를 구분. fallback을 완성된 Visual Docs로 오인시키지 않음 |

## 성공 기준

출력만 읽는 검토자가 해당 자료의 핵심 질문에 답하고, 중요한 조건·예외·확정 여부를 잘못 이해하지 않으며, 답의 근거를 찾아갈 수 있어야 한다. 첫 화면에 지정된 component가 있는 것만으로 통과시키지 않는다.

평가 source와 기대 답은 출력 생성 전에 정한다. 작성 과정에 사용하지 않은 다른 도메인·한국어 prose·긴 문서도 포함한다. 전후 결과를 같은 질문으로 비교하고 오답, 누락, 원문 탐색 의존, 표현상 오해를 기록한다. 중대한 의미 왜곡은 허용하지 않고 주요 질문 누락도 수정 대상으로 삼는다. 예쁜 화면이나 diagram 수는 성공 지표가 아니다.

## 증거와 후속 계획

- 실행: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/forge/skills/visual-docs/tests -p 'test_*.py'` → 62 tests, OK.
- 실행: `bash plugins/forge/skills/writing-specs/scripts/spec-docs.sh --repo-root . inspect --spec docs/specs/review-viewer-lifecycle --format json` → approved, diagnostics 0.
- 격리 비교 스크립트와 JSON: `.forge/scratch/visual-docs-comprehension-audit/probe.py`, `results.json`. 공유해야 할 관찰과 실행 조건은 이 문서에 보존했다.
- [Forge 플러그인 개선 계획](../plans/012-visual-docs-comprehension/plan.md). 스킬 지침·구성 생성 로직·렌더러·검증 방식을 수정하는 계획이다. 먼저 계약과 평가 기준을 맞춘 후 격리 fixture로 작은 end-to-end 경로를 검증하고 네 kind로 확장한다. 이번 요청은 계획까지다. 기존 프로젝트 HTML 재생성과 사용자 환경 설치는 개선 범위에 포함하지 않는다.
