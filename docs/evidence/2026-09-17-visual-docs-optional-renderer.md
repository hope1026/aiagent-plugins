# Visual Docs 선택형 렌더러 검증

## 변경 범위

일반 시각화는 앱과 모델이 처리하고, Forge 원문의 일회성 설명에는 의미·조건·상태·출처 보존만 적용한다. 관리형 renderer는 재생성 가능한 tracked Handbook, 명시적 freshness·재현성 요청과 기존 관리형 문서 갱신에 사용한다. 기존 CLI, parser, renderer, assets와 저장 형식은 변경하지 않았다.

사용자가 이 방향의 수정과 배포를 승인했다. 기준 commit은 `6f07e09`이며, 대상 계약은 `review-viewer-lifecycle/presentation-routing.md`, `forge-ui-design-skill-separation`의 시각화 라우팅, `semantic-spec-bundles`의 관리형 배포 범위다. 세 bundle은 기존 `approved` 상태를 유지한다. 전체 bundle 구현 완료를 주장하지 않는다.

## 실제 에이전트 실행

현재 Codex 환경에서 같은 기본 모델 설정을 상속한 별도 에이전트로 수행했다. Claude Code나 Antigravity의 실제 agent 실행, 인간 이해도 조사, 이전 버전 대비 시간·품질 A/B 측정은 수행하지 않았다.

| 시나리오 | 관찰 |
|---|---|
| 회의 5분 전, 예전 builder 사용 경험이 있는 대화 속 Brief를 표로 요청 | 파일·composition·builder·추가 질문 없이 대화 안의 표로 답했다. 관리자 승인, 만료 초대 재발급 예외, 결제 비범위와 제안 상태를 보존했다. |
| 회의 2분 전, 기존 session plan의 A→B→C를 도식 하나로 요청 | Mermaid 도식 하나로 표현하고 Route·새 파일·고정 캡션 패키지를 추가하지 않았다. |
| 시간 제한 아래 기존 관리형 경로와 동일 입력 재생성·최신성 검사를 요청 | 격리 fixture에서 공용 CLI로 준비, composition preflight, Handbook build와 freshness 검사를 수행했다. 고정 입력 재생성의 bytes 일치, source 변경 시 stale 및 HTML 미변경, source 복구 시 current를 확인했다. |

관리형 시나리오는 기계적 결과를 검증했다. `reading-check-required`를 보존하고 브라우저 표시나 인간 읽기 검증을 완료했다고 주장하지 않았다. 일회성 표와 도식은 요청 내용에 대조해 검토했으며 별도 브라우저 검사는 하지 않았다.

## 독립 리뷰

계획 참고문서에 남은 필수 도식 패키지와 관리형 흐름도의 이름 없는 분기를 발견해 수정했다. 관련 Semantic Spec의 four-kind 계약도 관리형 경로로 한정했다. 재검토에서 추가 actionable finding은 없었다. 일반 도식은 기본 기능으로, source-only 변경은 문서 자동 갱신 없이 처리하는 라우팅을 확인했다.

## 실행 검증

- `bash scripts/validate.sh`: `validate: all checks passed`.
- `bash plugins/forge/skills/writing-specs/scripts/spec-docs.sh --repo-root . validate --root docs/specs --baseline-ref HEAD`: exit 0.
- Visual Docs Python unittest discovery: 76 tests, OK.
- `test-build-visual-docs.sh`: 모든 검사 통과.
- `test-visual-docs-freshness.mjs`: 모든 검사 통과.
- `test-forge-visual-docs-install.sh`: Codex·Claude Code·Antigravity 격리 설치 및 동일 출력 검사 통과. 새 관리형 reference 포함 여부도 확인했다.
- Spec docs policy, artifact contract, lifecycle policy, UI skill routing 및 UI skill install 검사 통과.
- `git diff --check`: 오류 없음.

기존 renderer의 UI 코드는 변경하지 않아 로컬 browser 전체 회귀를 반복하지 않았다. 배포 commit의 원격 CI 결과는 GitHub Actions에서 확인한다.
