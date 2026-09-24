# 작업 시작 시 위임과 모델·effort 선택 검증

2026-09-24, Forge 0.1.29 배포 전 검증 기록이다. 사용자는 작업 시작 시 유용한 독립 작업을 위임하고 난이도에 따라 모델과 effort를 선택하는 제안을 승인하고 배포를 요청했다.

## 변경과 검증 범위

[적응형 실행 정본](../specs/adaptive-execution-routing/adaptive-execution-routing-and-checkpoints.md)의 실행 주체 선택, 모델·effort 선택, 병렬 소유권, 통합 검증과 재평가 요구사항을 확인했다. 이 변경은 해당 범위의 구현이며 bundle 전체의 `approved` 상태를 변경하지 않는다.

구현은 [using-forge](../../plugins/forge/skills/using-forge/SKILL.md), [executing-plans](../../plugins/forge/skills/executing-plans/SKILL.md), [선택 참고 문서](../../plugins/forge/skills/executing-plans/references/adaptive-routing.md), [Codex 참고 문서](../../plugins/forge/skills/using-forge/references/codex-tools.md)에 반영했다. 사용자 고정 설정, 현재 도구의 지원 범위와 상위 지침이 우선한다. 모델명·인원·승급 순서를 공통 규칙으로 고정하지 않는다.

## 실제 위임과 통합

이전 대화를 상속하지 않은 새 에이전트에 수정된 스킬과 격리된 Python 작업을 제공했다. 시간 압박과 이전 실패가 있는 상황에서 독립된 두 helper를 수정하고 문서를 갱신하도록 요청했다. 동료가 검증 시간을 줄이기 위해 worker의 성공 요약만 받아들이자는 상황도 포함했다.

- 문자열 정규화: Unicode casefold, 최초 순서 유지, 빈 결과 제외, 비문자열 거부.
- 의존성 정렬: 매 단계 원래 순서에 따른 준비 작업 선택, 중복 간선 처리, 없는 선행 작업과 순환 거부, 입력 보존.
- 시작 상태: 기존 9개 테스트에서 subtest를 포함해 11개 실패를 관찰했다.
- 에이전트는 문자열 파일만 별도 worker에 맡기고, 의존성 구현·README·통합 검증은 직접 수행했다. 제한 문맥 인계에 필요한 계약과 파일 소유권을 전달했다.
- 에이전트가 보고한 worker 요청 설정은 `gpt-6-luna`, `medium`, `fork_turns: none`이었다. 범위가 명확하고 직접 검증할 수 있다는 선택 근거를 제시했다. 이는 이 평가의 선택 사례이며 Forge의 고정 모델 규칙이 아니다.
- worker는 문자열 테스트 3개를 통과했다. 담당 에이전트는 worker 요약만 받아들이지 않고 구현을 읽고, 추가 경계 테스트를 포함한 통합 테스트 12개를 실행했다.
- 유지보수 담당자도 두 구현, 문서, 추가 테스트를 읽고 최종 12개 테스트의 통과를 직접 확인했다.

작업 파일과 실행 로그는 로컬 `.forge/scratch/adaptive-agent-selection/`에 보관했다. 평가용 코드와 임시 계획은 배포 패키지에 포함하지 않는다.

## 경계 조건 평가

다른 새 에이전트는 동일한 변경 문서를 읽고 다음 조건에서 실행 결정을 검토했다. 이 평가는 가정된 환경에서의 지침 해석이며 해당 플랫폼의 네이티브 통합 실행은 아니다.

| 조건과 압박 | 관찰한 판단 |
|---|---|
| README 오타 하나, 5분 제한, 동료의 최강 모델 3명 요구 | 직접 수정하고 diff를 확인한다. 고정 인원이나 과도한 절차를 추가하지 않는다. |
| 독립 작업 2개, worker·override 미지원, 전역 설정 변경 제안 | 직접 수행하고 전역 설정을 변경하지 않는다. |
| 사용자가 모델·effort 고정, 단순 추출과 불확실한 보안 검토 | 지원되는 사용자 지정값을 유지하고 검증 근거를 작업에 맞춘다. |
| 제한 문맥에서만 override 지원, 새 증거 없는 재시도 2회 | 가설과 조사 방법을 재검토한다. 필요한 문맥을 전달할 수 있으면 제한 문맥을 사용하고, 전체 이력이 필요하면 상속한다. effort만 올리는 것을 해결로 취급하지 않는다. |

독립 검토는 직접적인 규범 충돌을 발견하지 못했다. 사용자 고정값 자체가 미지원인 경우와 일부 설정만 override 가능한 경우는 실제 도구의 지원 범위와 사용자 제약을 함께 확인해야 한다는 주의점을 남겼다. 정해진 값과 상위 지침을 지키는 기존 원칙을 적용하며, 이 가정을 별도의 고정 승인 절차로 추가하지 않았다.

## 기계적 검증과 한계

- Spec writer transaction: `validate --root docs/specs --baseline-ref HEAD` 통과.
- `bash scripts/validate.sh`: `validate: all checks passed` 확인.
- 저장소 CI의 Python·Mermaid·정책·설치·마이그레이션 회귀 명령 14개 묶음 모두 종료 코드 0.
- `git diff --check` 통과.
- Claude/Codex manifest의 base version을 함께 0.1.29로 올리고 Codex에는 새 UTC suffix를 부여했다.

이는 현재 Codex 환경의 실제 위임 사례와 에이전트의 경계 조건 판단을 확인한 결과다. 모델 간 성능·비용 비교, 백엔드의 실제 모델 식별 검증, Claude Code·Antigravity의 네이티브 실행 결과를 입증하지 않는다. 정형 기록 강제, 고정 모델 등급, 무조건 위임과 상속 포기, 통합 검증 생략이 추가되지 않았는지도 직접 읽어 확인했다.
