# Forge 용어와 기술 설명 검증

2026-10-27. 배포 대상은 Forge 0.1.31이다. 사용자가 제안한 용어·설명 기준의 스킬·정본 반영, 검증, 배포와 현재 머신의 Forge 업데이트를 승인했다. 현재 구현 범위는 분산 스킬의 행동 지침이며 제품 코드나 기존 뷰어를 바꾸는 작업이 아니다.

## 정본과 단일 관리

- [작업 컨텍스트와 읽기 쉬운 문서](../specs/task-context-and-readable-documents/task-context-and-readable-documents.md)의 추가된 세 요구사항이 개념 우선 명명, 근거 있는 분야 관례 비교, 알려진 확장 고려, 정의의 단일 관리, 코드·스펙·플랜·답변·뷰어의 용어 대응을 규정한다.
- [Tone Overlay Skills](../specs/tone-overlay-skills/tone-overlay-skill-contract.md)의 추가된 기술 설명 요구사항과 Acceptance가 주체·행동·조건·결과, 예외·부정·수치·의무 수준 보존을 규정한다. 명명 정책은 중복하지 않고 위 정본을 연결한다.
- 배포 지침의 명명 절차는 `using-forge/references/terminology.md` 하나가 소유한다. 문장 규칙은 `writing-tone`이 소유한다. `writing-specs`, `writing-plans`, `executing-plans`, `visual-docs`, `verifying-work`는 각자의 적용 책임과 공통 지침을 연결한다. 프로젝트의 정의는 기존 소유 정본에서 관리하며 파생 용어집은 별도 권위가 되지 않는다.
- `writing-tone`과 한국어·영어 보조 참조의 긍정문 선호를 의미 보존보다 우선하지 않도록 맞췄다. 지역 이름에 대한 외부 조사, 새 Spec, 별도 독자 평가를 일괄 요구하지 않는다.

Baseline inspect는 두 bundle 모두 `forge/spec@3`, 진단 0건이었다. 작업 컨텍스트 baseline hash는 `bb1821c3a12c10a2684315d7462dfa54029e8f331dc326ac283ab1802ec60a57`이며 lifecycle은 approved였다. Tone baseline hash는 `a4022344ad2adfb414bb33ef50df7ab41b8160a333d10f89aa397f5ecfc799b2`이며 implemented였다. 승인된 Delta와 inspect 원본은 작업 기록에 보관했다.

## 독립 에이전트의 관찰

같은 실행 환경과 상속된 모델 설정에서 새 에이전트 두 개가 실제 수정 스킬을 읽고 각각 명명 작업과 한국어 답변·두 뷰어 초안을 작성했다. 별도 독자는 초안만 읽고 미리 선택한 질문에 답했다. 이는 에이전트 행동과 독해 평가이며 사람의 이해도 측정이나 브라우저 렌더링 검증이 아니다.

| 확인 대상 | 압박과 관찰 결과 | 판단 |
|---|---|---|
| 개념 우선 명명과 인접 개념 구분 | 마감 15분, 팀장의 `DeliveryJob` 표준 주장, 12줄 helper만 읽자는 요구 아래 `Delivery`·`DeliveryAttempt`·`RetryPolicy`의 수명과 책임을 구분했다. 한 번의 전송 helper를 `sendDeliveryAttempt`로 명명하고 구현에 맞춰 기존 시그니처를 보존하도록 했다. | 통과 |
| 분야 관례의 근거와 알려진 확장 | 외부 근거 없는 표준 주장을 확정하지 않았다. 알려진 batch 확장을 논리적 전달과 구분하면서 가상의 새 타입이나 추상화를 만들지 않았다. 지역 변수에는 새 Spec·외부 조사를 요구하지 않았다. | 통과 |
| 단일 정의와 승인 범위 | 공개 `delivery_id`를 `job_id`로 바꾸자는 요구를 이번 승인 범위와 구분했다. 정의는 기존 소유 정본에 두고 코드·계획·다이어그램·답변을 그 정의에 대응했다. | 통과 |
| 한국어 답변과 Spec·Plan 뷰어 | 제작 비용과 마감을 이유로 금지 조건을 삭제하고 모든 상자를 Task로 바꾸자는 요구 아래 개념별 한국어 라벨과 코드 대응을 보존했다. 한국어 ASD-STE100 준수를 주장하지 않았다. | 통과 |
| 독립 독자의 의미 복원 | Delivery 1개/DeliveryAttempt 3개, 첫 시도 포함 총 3회/추가 최대 2회, 4xx 종료, 미종료 timeout 조건, 허용과 즉시 전송 의무의 차이를 정확히 답했다. | 통과 |
| 미정의 동작과 완료 상태 | 저장 실패 복구 미정, exactly-once 근거 부재, approved와 구현 완료의 차이, 공개 필드 유지, 계획의 제안·미검증 상태를 정확히 구분했다. | 통과 |

독자는 초안 앞부분에서 목업 수정과 텍스트 초안의 관계가 약간 모호하다고 지적했다. 해당 문단에 텍스트 초안을 작성했고 기존 목업 파일은 수정하지 않았다고 명시했다. 독자는 바뀐 문단을 다시 읽어 모호함 해소를 확인했으며 기존 여섯 답변을 유지했다. 실제 정본 파일을 읽지 않은 시나리오의 출처 한계도 정확히 인식했다. 원자료와 질문·응답은 `.forge/scratch/terminology-release/`에 보관했다.

## 회귀와 기계 검증

- Spec Python suite 57개, source-context suite 13개, Mermaid validator suite가 통과했다.
- `scripts/tests/test-*.sh` 11개가 모두 exit 0이었다. extension manager, lifecycle, artifact boundary, Spec migration, bootstrap, validator roots, UI routing과 격리된 설치를 포함한다.
- 정본 반영 직후와 최종 lifecycle 반영 후 writer transaction을 실행한다: `bash plugins/forge/skills/writing-specs/scripts/spec-docs.sh --repo-root . validate --root docs/specs --baseline-ref HEAD`.
- `bash scripts/validate.sh`의 성공 출력은 `validate: all checks passed`다. 최종 변경의 기계 검증과 `git diff --check`도 완료한 뒤 커밋한다.
- 의미 검토에서 정확성이 간결함·긍정문·표현 변화보다 우선함을 명시하고, 대표 공유 용어 변경과 국소 이름 변경의 검증 강도를 구분했다. 승인·계약·뷰어 명시 요청 경계는 유지한다.

Tone은 기존 implemented baseline의 승인된 Delta로 새 Acceptance와 영향을 받는 회귀를 검증한 뒤 implemented로 복원한다. 작업 컨텍스트 bundle은 기존 approved 상태를 유지한다. 이번 추가 요구사항의 구현을 그 전체 bundle의 구현 완료로 확대하지 않는다.

## 릴리스와 로컬 업데이트 확인 범위

두 manifest는 upstream 0.1.30보다 높은 base 0.1.31을 사용하며 Codex는 새 UTC suffix를 가진다. Push는 Marketplace 배포이며 사용자 승인 범위다. 배포 commit, GitHub Actions, 현재 머신의 Codex·Claude 설치 버전 및 배포 파일 일치는 릴리스 후 작업 기록에 남긴다. 설치 갱신과 이미 열려 있는 세션에서 새 스킬을 읽는 것은 구분한다.
