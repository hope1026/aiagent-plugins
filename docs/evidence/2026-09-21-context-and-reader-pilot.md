# 같은 원문으로 작업과 이해를 지원한 첫 적용

사용자가 승인한 방향은 정확한 작업, AI에게 충분한 컨텍스트, 사람에게 이해하기 쉬운 설명을 함께 제공하는 것이다. 앞선 시각 템플릿 제거 변경안을 이어받아, 고정 renderer를 복구하지 않고 원문·변경 추적을 선택형 도구로 분리했다.

## 구현한 범위

- `using-forge`는 요청에 필요한 계약·조건·예외·코드·테스트를 선택하고 관련 의존성을 따라 읽도록 안내한다. 원문, 승인된 의도, 관찰한 구현과 검증 결과를 구분한다.
- `source_context.py`의 readonly capture/check는 일반 UTF-8 파일을 그대로 전달하고 source와 artifact의 byte 변경을 구분한다. 원문 작성 형식은 요구하지 않는다.
- 스펙은 설명부터 작성하고 parser metadata를 맞추도록 바꿨다. 첫 예시는 단일 파일·Requirement-only bundle이다. 계획 예시는 필수 interface 구문만 보여주고 작업에 필요 없는 필드와 고정 Step 수를 제거했다.
- `visual-docs`와 `verifying-work`는 독자의 질문, 기대 사실, 원문 의미와 별도 읽기 평가를 사용한다. 저장된 원문 위치·hash는 설명의 정확성이나 dependency 완전성을 대신하지 않는다.

정본은 [작업 컨텍스트와 읽기 쉬운 문서](../specs/task-context-and-readable-documents/task-context-and-readable-documents.md), 사람용 안내는 [원문 추적 기능 안내](../guides/source-context.md)다. 기존 `forge/spec@3`와 저장형 Plan parser는 유지했다. 이 단계는 전체 문서 schema 이관이나 일반적인 이해도 향상 입증이 아니다.

## 기계적 결과

- source-context suite: 13 tests, OK. 무손실 텍스트·CRLF, 입력 순서 독립성, 제목 언어·section 순서 변경, 원문·artifact 변경 분리, 삭제·읽기 실패, 비선택 dependency 한계, path·symlink·snapshot·byte budget을 검사했다.
- 기존 writing-specs suite: 66 tests, OK.
- Spec policy, artifact contract, lifecycle references, maintenance layout, bundle migration, UI routing 검사: 통과.
- 격리 설치·재설치: Codex·Claude Code·Antigravity export에서 같은 source capture가 동일했다. 설치한 도구의 check는 초기 exit 0, 원문 변경 후 exit 1이고 snapshot을 쓰지 않았다. 기존 rollback 검사와 제거된 시각 템플릿 정리 검사도 통과했다.
- `bash scripts/validate.sh`: `validate: all checks passed`.
- `spec-docs.sh --repo-root . validate --root docs/specs --baseline-ref HEAD`: exit 0.
- `git diff --check`: 오류 없음.

원문 추적 안내 자체도 계약·구현을 source로, 안내를 artifact로 묶었다. 로컬 `.forge/work/source-context-pilot/source-context-guide.json`에 기록했고 세 파일 모두 `unchanged`, exit 0을 관찰했다. 이 기록은 선택한 bytes가 같음을 확인하며 설명의 의미 검토를 대체하지 않는다.

## 독립 작업자 사례

현재 모델과 환경을 사용하되 대화 이력을 주지 않은 작업자에게 회의 전 짧은 시간 안에 초대 재발급 함수를 정책대로 수정하고 다음 작업자와 사람에게 인계하도록 요청했다. 쓰기는 `.forge/scratch/context-pilot/execution`으로 제한했다.

입력은 특정 schema가 없는 README, 초대 정책, 연결된 별도 권한 정책과 작은 Python 함수였다. 승인 정책은 정지 상태 우선 거부, owner/admin만 허용, 다음으로 미만료 거부, 성공 시 무료 24시간 재발급이었다. 기존 함수는 만료만 확인해 역할과 정지를 무시했다.

작업자는 연결된 권한 정책을 함께 읽고 정지 → 역할 → 만료 순서로 검사를 추가했다. 수정 전에는 16개 입력 조합 중 12개가 실패했고, 수정 후 네 테스트의 16개 조합이 모두 통과했다고 보고했다. 통합 검토에서 실제 코드와 테스트를 읽고 네 테스트를 다시 실행해 통과를 확인했다.

작업자는 실제 capture/check를 사용했다. 수정 전 snapshot의 check는 `invite.py`만 `changed`, exit 1이었고 정책은 unchanged였다. 수정 후 snapshot은 README·두 정책·코드·테스트와 설명 artifact가 모두 unchanged, exit 0이었다. 주 작업자도 두 check 결과를 직접 확인했다.

전달한 도구 컨텍스트의 정본 문구가 작업 중 명확화되었을 때도 작업자는 hash 변경을 발견하고 해당 원문을 대조했다. 초대 정책과 동작에는 영향이 없으므로 전체 작업을 반복하지 않았다.

## 설명만 읽은 평가

먼저 원문 추적 안내에 대한 질문과 기대 사실을 정의한 뒤, 별도 독자에게 안내만 읽게 했다. 연결된 정본·구현과 기대 답은 제공하지 않았다. 선택형 사용, source/artifact 차이, unchanged의 한계, 비선택 dependency, 설명 재검토, 크기 제한, 삭제 결과, 승인 역할의 여덟 질문에 모두 맞게 답했다. 독자가 “틀린 설명은 수정해야 한다”는 조치가 간접적으로 표현됐다고 지적해 해당 문장을 명시적으로 고쳤다.

같은 독자가 초대 사례의 설명만 읽고 성공 조건, 겹친 오류의 우선순위, 비용·기간, 기존 결함과 변경, 외부 시스템 미검증 범위와 hash의 한계에 관한 일곱 질문에도 맞게 답했다. 정책·코드·테스트를 읽지 않았으며 테스트 통과 사실은 설명의 보고를 읽은 것이지 자신이 실행한 결과가 아님을 구분했다.

이는 에이전트 독자의 답변 관찰이다. 사람의 이해도 실험이나 이전 버전과의 시간·비용·품질 비교는 아니다. 실제 HTML/브라우저 UI도 이번 사례에 포함하지 않았다.

## 작성 지침 사례

새 작업자는 승인된 초대 정책을 단일 스펙과 짧은 parser용 계획으로 작성하라는 요청을 받았다. 시간 압박과 짧은 인계 요구가 함께 있었으며 구현은 금지했다.

결과는 49줄 단일 Spec과 28줄 Plan이었다. 한국어 동작 설명과 오류 충돌 예시를 먼저 제시했고, 계획은 한 Task와 두 Step으로 작성했다. 불필요한 Acceptance member, coverage table, 파일·복구·승인 필드는 추가하지 않았다. 추가 승인 질문도 없었다.

주 작업자가 산출물을 읽고 격리 root의 spec validate와 Plan reference parser를 실행했다. 관련 bundle 1개, 정확한 statement link 6개와 diagnostics 0을 확인했다. 신규 격리 root에는 Git baseline이 없으므로 기존 계약 변경의 baseline transaction을 수행했다고 주장하지 않았다.

## 한계와 다음 판단

첫 적용에서는 조건·예외가 별도 문서에 있어도 AI가 작업에 반영하고, 사람이 읽을 설명에 중요한 사실과 검증 범위를 보존했다. 실제 시각 계산·초대 저장·전송·결제 연동, native Claude Code/Antigravity agent 실행은 평가하지 않았다. 설치 export의 동작과 에이전트의 native 동작은 구분한다.

현재 정확한 Requirement heading 링크와 최소 metadata는 기존 parser 호환성으로 남아 있다. 이 규칙까지 없애는 변경은 별도 소비자·참조 이관이 필요하다. 다음 평가에는 실제 프로젝트의 더 큰 변경, 불충분한 문서와 충돌하는 계약을 포함해야 하며 이번 사례만으로 보편적인 품질 향상을 주장하지 않는다. 배포·사용자 설치본 갱신·push는 수행하지 않았다.
