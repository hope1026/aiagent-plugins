# 호환성만 남은 형식과 렌더링 코드 제거

사용자는 기존 호환성이 목표가 아니며 불필요하게 남은 것은 제거해도 된다고 확인했다. 현재 작업 트리의 시각 템플릿 제거·컨텍스트 도구 변경안을 이어서 조사했다.

## 사용처 조사와 삭제

- `parse_plan_related_specs`, `parse_plan_governing_statements`의 production consumer는 이전에 제거한 Visual Docs였다. 남아 있는 호출은 전용 테스트뿐이었다. 두 함수와 관련 dataclass·보조 코드 585줄, 전용 테스트와 fixture, 고정 Plan 양식을 제거했다.
- `markdown_render.py`는 현재 import하는 production code나 테스트가 없었다. 파일을 제거했다.
- `mermaid.min.js`와 별도 라이선스는 이전 브라우저 renderer용이었다. 현재 Spec의 Mermaid 구문 검사는 별도의 `mermaid-validator.bundle.mjs`를 사용한다. 브라우저 runtime을 제거하고 build/checksum·설치 검사를 실제 validator 대상으로 정리했다. Validator의 third-party notice는 유지했다.
- `Task N`, `Step N`, `Related Specs`, `Governing statements`, 번호가 붙은 plan 디렉터리의 강제를 제거했다. 계획은 프로젝트 위치, 내용에 맞는 제목·체크리스트와 필요한 원문 링크를 사용한다.
- 스킬, 정본, README와 plugin 소개에서 기존 parser 호환성 유지를 목적처럼 표현한 문구를 제거했다. Maintenance adapter는 관리 도구로 다시 생성했다.

파일 삭제는 Git 이력으로 복구할 수 있다. 남은 rendering bytecode 두 파일은 `/tmp/forge-retired-spec-render-cache.wLAgSu`로 이동해 격리했다. 사용자 전역 설치본과 이전 출력은 수정하지 않았다.

## 유지한 기능

현재 Spec validator의 승인 상태, bundle 구성과 연결·경로·baseline 검사는 repository validation과 실제 작성·검증 경로에서 사용 중이다. 이 코드는 이전 버전의 입력을 받아들이는 compatibility adapter가 아니다. 이번 삭제 대상으로 보지 않았다. 기존 Spec 형식의 각 제약은 이후에도 작업 정확성과 문서 이해에 기여하는지 별도로 판단할 수 있으며 기존 호환성 자체는 보존 이유가 아니다.

선택형 원문 수집·변경 확인 도구도 사용 중이며 유지했다. 이전 증거 문서의 parser·test 수는 당시 실행 이력으로 남겼다.

## 검증

- Spec Python suite: 57 tests, OK. 제거한 Plan 전용 검사는 9개이며 단순 실패 무시가 아니라 소비 기능과 함께 제거했다.
- source-context suite: 13 tests, OK.
- Mermaid validator test: production 문서 구문 검사와 두 번의 독립 rebuild 비교·checksum 검사 통과.
- Spec policy·artifact·lifecycle·maintenance layout·bundle migration·UI routing·재설치·격리 설치/rollback 검사 통과.
- `bash scripts/validate.sh`: `validate: all checks passed`.
- 정본 writer transaction `validate --root docs/specs --baseline-ref HEAD`: exit 0.
- `git diff --check`: 오류 없음.

대화 이력 없이 수정된 writing-plans를 읽은 별도 agent에게 시간 제한이 있는 초대 재발급 작업 인계 계획을 요청했다. 승인된 정책과 기존 테스트를 한 번씩 참조하고, 정지·권한 검사 추가와 허용·거부·무료·24시간 검증을 세 항목으로 정리했다. 고정 Plan 필드와 요구사항 전문 반복, 파일 생성, 추가 승인 질문이 없었다. 이는 planning behavior 관찰이며 코드 구현·실행이나 사람 이해도 평가가 아니다.

배포, commit과 사용자 설치본 갱신은 수행하지 않았다.
