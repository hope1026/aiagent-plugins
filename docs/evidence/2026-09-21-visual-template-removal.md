# 시각 템플릿 제거 검증

사용자의 시각 템플릿 제거 요청에 따라 고정 HTML 셸과 이를 사용하는 관리형 renderer, composition 입력, freshness runtime, 전용 테스트·fixture와 Plan 시각화 참고 구조를 제거했다. `visual-docs`는 표현 선택, 원문 의미 보존과 읽기 검증 지침으로 유지한다. README, lifecycle skill, 관련 정본, 설치 검사와 CI 호출을 같은 범위로 갱신했다.

기준 commit은 `abfed39`다. 기존 프로젝트의 HTML·문서와 사용자 전역 설치본은 수정하지 않았다. 삭제한 추적 파일은 Git 이력에서 복원할 수 있다. 과거 구현 계획과 evidence는 당시 renderer의 기록이며 현재 제작 지침이 아니다.

## 계약 범위

- `review-viewer-lifecycle`: 고정 화면과 관리형 빌드 계약을 제거하고 자유 작성, 원문 보존, 기존 산출물 갱신과 프로젝트별 최신성·재현성 검증으로 변경했다. 기존 비시각적 구조화 Plan 요구사항은 유지했다.
- `semantic-spec-bundles`: renderer 배포 요구를 제거했다. Bundle parser·validator, 구조화 Spec과 Plan의 구문은 유지했다. 계약을 변경했으므로 `implemented`에서 `approved`로 되돌렸다.
- `forge-ui-design-skill-separation`: 시각화 라우팅과 UI 검증 설명을 맞추고 `approved`를 유지했다.

전체 bundle의 구현 완료를 주장하지 않는다. 구조화 템플릿의 추가 완화는 이번 구현 범위에 포함하지 않는다.

## 관찰한 결과

- `bash scripts/validate.sh`: `validate: all checks passed`.
- `spec-docs.sh --repo-root . validate --root docs/specs --baseline-ref HEAD`: exit 0.
- 남아 있는 writing-specs Python suite: 66 tests, OK. Spec Bundle과 Plan의 해석·검증 회귀를 확인했다.
- Spec docs policy, artifact contract, lifecycle resource, maintenance layout, spec migration, UI routing 검사: 통과.
- UI skill 재설치 검사: Codex·Claude Code·Antigravity 격리 대상에 구버전 시각 템플릿을 넣은 뒤 두 차례 설치했다. 시각화 배포 파일은 `SKILL.md`만 남고 별도 사용자 스킬은 보존됐다.
- 격리 설치 검사: 세 대상의 bundle inspect와 transition parser 출력이 동일했다. 경로 이탈·부분 복사 실패·교체 실패·중단 시 복원 검사도 통과했다.
- 확장 관리 도구로 repository-local maintenance adapter를 다시 생성하고 `status: PASS`를 확인했다.
- `git diff --check`: 오류 없음.

## 새 에이전트 실행

현재 모델·환경에서 대화 이력을 전달하지 않은 새 에이전트가 수정한 `visual-docs/SKILL.md`를 읽고 두 상황에 응답했다.

첫 상황은 회의 3분 전, 이미 승인된 운영자 초대 정책을 작은 표로 설명하는 요청이었다. 운영자만 초대, 24시간 만료, 운영자의 재발급, 결제 없음의 네 사실을 보존하고 파일·빌드·추가 승인 없이 표를 제공했다.

둘째 상황은 별도 generator가 없는 이전 Forge HTML Handbook의 이름 변경과 기존 탐색 기능 보존 요청이었다. 직접 HTML 수정, 연결된 식별자와 탐색 동작 확인, 무효한 생성기·최신성 보장 제거를 제시했다. 원문 revision/hash 비교의 범위와 실제 내용 대조를 구분했으며, 실제 HTML이 주어지지 않은 상황에서 수정·렌더링 완료를 주장하지 않았다.

이는 지침의 행동 관찰이다. 기존 HTML의 실제 변환이나 브라우저 테스트, Claude Code·Antigravity의 native agent 실행, 인간 이해도 측정은 수행하지 않았다. 이번 변경은 UI 구현의 변경이 아니라 해당 renderer의 제거이므로 삭제된 browser suite를 반복하지 않았다.

## 호환성

이전 `build-visual-docs.sh`와 자동 freshness UI는 더 이상 기본 배포에 포함되지 않는다. 기존 문서를 갱신할 때는 프로젝트가 유지하는 generator 또는 직접 작성 방식으로 처리하며, 재현성과 최신성이 필요하면 실제로 제공하는 방법을 검증한다. 배포·설치 갱신은 아직 수행하지 않았다.
