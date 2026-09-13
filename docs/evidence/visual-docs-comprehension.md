# Forge Visual Docs 구성 기능 검증

기준: 계획 012, baseline `87cbe25`, Forge `0.1.25` 배포 준비. 사용자 요청은 Forge 플러그인 수정과 배포이며 기존 프로젝트 HTML 재생성과 사용자 설치 변경은 제외했다.

## 변경 결과

- `--prepare --format json`이 원문·역할·정확한 구절·fingerprint·View Context를 읽기 전용으로 제공한다.
- agent가 독자의 질문, 쉬운 설명, 표·조건부 관계·예시와 근거를 composition으로 작성한다. `--composition`이 공개 생성 경로에 연결된다.
- exact source quote와 raw-source fingerprint, context, 질문의 answer block, 표와 graph의 참조를 검사하고 실패하면 기존 output을 보존한다.
- 설명이 첫 읽기 경로가 되고 전체 원문과 기존 탐색·deep link는 접근 가능하게 유지한다. 특정 문서 heading, domain profile, diagram node 수가 설명의 필수 조건이 아니다.
- 생성 결과는 source-browser와 reading-check-required를 구분한다. schema나 quote 검사로 의미 충실도 또는 인간 이해를 보장한다고 표시하지 않는다.
- 원문과 저장한 composition의 freshness, frozen composition과 generator digest를 기록한다. Project Handbook이 자체 출력이나 `.forge/`를 근거로 수집하는 문제와 Brief의 같은 heading 아래 여러 block이 entity key를 공유해 준비를 거부하던 문제도 재현·수정했다.

## 기계적·표시 검증

| 실행 | 결과와 범위 |
|---|---|
| `python3 -m unittest discover -s plugins/forge/skills/visual-docs/tests -p 'test_*.py'` | 76 PASS. 새 composition 및 네 kind의 공개 CLI, 원문 불변·재현성·오류 시 출력 보존·입력 freshness, Brief list 뒤 prose block 보존 포함 |
| writing-specs Python discovery | 66 PASS |
| `bash plugins/forge/skills/visual-docs/tests/run-visual-docs-browser.sh` | 18 PASS. 기존 13개와 새 읽기·표·도표·출처·JSON freshness 5개 |
| `bash scripts/tests/test-forge-visual-docs-install.sh` | Codex·Claude·Antigravity 격리 export의 모듈/reference, prepare·composition·freshness, 출력 동등성 PASS |
| `test-build-visual-docs.sh`, JS freshness, Mermaid validator | PASS |
| extension-manager, maintenance layout, validator roots, spec policy·migration·lifecycle, artifact authority, bootstrap, UI routing·install | PASS. extension-manager Python 17개 포함 |
| writer transaction, repository validator, plan parser와 exact governing links | PASS |

브라우저는 desktop과 390px에서 질문 이동과 reload, 근거 펼치기, 닫힌 원문 영역 자동 열기, 조건을 포함한 SVG, 문서 가로 overflow, 구성 JSON 변경과 원복의 stale/current를 확인했다. 기존 빠른 탐색·hidden diagram·print 회귀도 유지했다. 서버 준비 중 일시적인 curl 연결 실패는 harness 재시도 후 정상 준비되었고 테스트는 모두 통과했다.

원문 탐색을 보존하는 기본 renderer의 일부 고정 profile과 문법 extractor는 남아 있다. 사람에게 제공하는 설명은 새 composition 경로가 담당하며, 기본 source-browser만 생성한 것을 이해 문서 완료로 취급하지 않는다.

## 독립 작성과 읽기 평가

제작에 사용하지 않은 한국어 `보고서 내보내기` source를 격리 저장소에 준비했다. 원문에는 필수 정보 보완, 재시도, 취소와 미정인 보관 기간을 prose로 작성했고 diagram은 넣지 않았다. 새 agent에게 배포 기한과 기존 양식 재사용 압력을 함께 주고 최신 Visual Docs 스킬을 적용하게 했다.

작성 agent는 prepare → composition → 의미 대조 → preflight → offline build → freshness를 수행했다. source는 수정하지 않았고 HTML도 직접 편집하지 않았다. 부모가 만든 fixture에 baseline commit이 없어 한 번 중단됐으며, 부모가 fixture의 docs만 commit으로 초기화한 뒤 진행했다. 이 중단은 사용자 프로젝트의 Git 작업이나 플러그인 결함으로 기록하지 않는다.

다른 새 agent에게는 근거 disclosure와 전체 source를 제외한 설명 텍스트만 제공했다. 아래 질문은 평가 전에 정했다.

| 질문 | 검토자의 답 | 대조 |
|---|---|---|
| 필수 정보가 없으면 대기열에 넣는가 | 넣지 않고 보완 요청 | 일치 |
| 최초 시도를 포함한 최대 횟수와 오류 범위 | 총 3번. 일시적 오류와 일반 오류 표현 차이는 미해결 | 일치 |
| 파일 생성 후 주소 제공 전 취소 가능한가 | 명시되지 않아 확정할 수 없음 | 일치 |
| 주소 보관 기간은 얼마인가 | 미정 | 일치 |
| 파일 형식은 무엇인가 | CSV 또는 PDF | 일치 |
| 추가로 결정할 운영 기준은 무엇인가 | 필수 정보 목록, 오류 범위, 중간 취소 구간, 보관·만료 기준 | 일치 |

6개 답 모두 원문 기대와 일치했고, 원문의 공백이나 표현 차이를 임의 정책으로 채우지 않았다. 작성자는 표와 예시를 선택했고 도표를 억지로 추가하지 않았다. fixture와 고정 composition은 `plugins/forge/skills/visual-docs/tests/fixtures/comprehension/held-out-export/`에 보존했다. 보존 후에는 새 평가 자료로 간주하지 않는다.

부모도 격리 HTTP 서버에서 실제 브라우저의 설명·질문·표·예시·미정 항목과 제목/본문/출처 위계를 확인했다. 이것은 에이전트의 출력 검토이며 인간 대상 사용성 시험이 아니다. 기존 사용자 HTML의 `file://` 차단을 우회한 것이 아니라, 이번 기능 테스트를 위해 별도로 만든 fixture의 화면을 확인했다.

## 수용 범위와 한계

새 `source-grounded-composition.md`의 여섯 Acceptance를 공개 CLI, 네 kind, prose workflow·policy, 예시·근거 검증, 재현성·freshness, 독립 읽기 평가로 확인했다. 기존 bundle의 탐색·권위·원문 보존 회귀는 관련 테스트로 보존했으며 bundle 전체를 implemented로 바꾸지 않았다.

source quote가 존재해도 잘못된 설명을 인용할 수 있으므로 semantic entailment 자동 검증을 구현했다고 주장하지 않는다. 사람이 읽는 모든 문서의 이해 성과를 보장하는 시험도 아니다. 스킬이 실제 설명을 작성하고 자료별 의미·읽기 검증을 수행하도록 변경했으며 그 경로가 실행되는 것을 확인했다.

사용자 스킬 복사본은 수정하지 않았다. 배포 대상은 Marketplace가 제공하는 Forge 패키지다. 실제 배포 commit과 원격 CI 결과는 release task의 실행 결과로 확인한다.
