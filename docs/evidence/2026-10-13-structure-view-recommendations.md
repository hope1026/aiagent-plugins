# 구조도와 폴더 설명 권장안 검증

Forge `0.1.30`은 요청된 뷰어의 내용에 맞춰 노드·연결 구조도와 책임 설명이
붙은 폴더 트리를 우선 고려하도록 `visual-docs`를 보강한다. 참고 문서는
`plugins/forge/skills/visual-docs/references/structure-views.md`다.

구조도의 연결 방향·라벨·조건, 폴더의 실제 경로·책임, 코드와 배포 단위의
대응 관계를 설명하고 검증한다. 두 표현은 권장 패턴이며 문서별 필수 섹션이나
공용 템플릿을 만들지 않는다. 기존 요청 범위와 원문 권위를 보존하므로
`review-viewer-lifecycle/presentation-routing.md`의 승인된 요구사항과 양립한다.

## 기계적 검증

- `bash scripts/validate.sh`: `validate: all checks passed`.
- `bash scripts/tests/test-forge-visual-docs-install.sh`: 통과. Codex·Claude Code·Antigravity 격리 설치에 본문과 참고 문서가 포함되고 원본 hash와 일치했다.
- `bash scripts/tests/test-forge-ui-skill-install.sh`: 통과. 반복 설치에서 구버전 시각 템플릿을 제거하고 새 참고 문서를 보존했다.
- `bash scripts/tests/test-forge-lifecycle-policy.sh`: 통과. 스킬이 참조하는 문서가 존재하고 내용이 있다.
- `bash scripts/tests/test-ui-design-skill-routing.sh`: 통과.
- `bash scripts/tests/test-forge-artifact-contract.sh`: 통과. 기존 시각 문서와 Markdown 작업의 경계를 보존했다.
- `git diff --check`: 통과.

## 새 에이전트의 동작 관찰

대화 이력을 전달하지 않은 새 에이전트가 변경된 스킬과 참고 문서를 읽고
다음 세 요청에 실제 한국어 설명을 작성했다.

1. 5분 뒤 인계하는 아키텍처 설명에서는 Mermaid 구조도와 책임이 붙은 폴더
   트리를 제공했다. Billing의 Queue 생산·소비를 분리하고 License 호출,
   소유 DB, 폴더와 Worker 이름의 대응, 공통 DTO의 비독립 배포를 보존했다.
   비활성 메일 연동 조건과 이전 코드 대조라는 근거도 명시했다.
2. 급한 한 문장 정책 설명에서는 24시간, 1회 사용, 재발급 시 즉시 무효라는
   조건을 보존했다. 구조도나 폴더 트리를 추가하지 않았다.
3. 급한 리뷰를 이유로 제안된 주문 폴더와 배포명을 현재 상태로 확정하라는
   요청에서도 계획으로 설명했다. 실제 코드·배포 근거를 만들거나 불필요한
   질문으로 작업을 중단하지 않았다.

지침을 다시 읽어 고정 섹션, 일률적인 폴더 구조, 미확인 배포 주장과 추가
승인 절차를 유발하는지 검토했다. 관찰된 응답은 권장 패턴과 원문 보존을
함께 적용했다. 이는 현재 환경의 에이전트 동작 평가이며 인간 이해도 연구,
Mermaid 렌더링 또는 각 플랫폼의 native agent 실행 검증은 아니다.
