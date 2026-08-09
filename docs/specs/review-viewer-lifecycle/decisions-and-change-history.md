# 결정과 변경 이력

## Decisions & History

- 2026-07-12 [DECISION] 기존 `spec-viewer`를 `spec`, `plan`, `combined` mode를 가진 lifecycle review viewer로 확장한다. 별도 `plan-viewer`를 만들지 않는다.
- 2026-07-12 [DECISION] spec과 plan은 각각 source of truth로 유지하고 Viewer는 읽기 전용 파생 산출물로 유지한다.
- 2026-07-12 [DECISION] Viewer HTML은 기본적으로 커밋하지 않는다. 대신 source 변경과 checkpoint마다 자동 재생성하고 source hash·freshness·rebuild command로 최신성을 관리한다.
- 2026-07-12 [DECISION] 6개 panel ID를 mode 전체에서 유지하고 label과 copy만 locale에 맞게 바꾼다.
- 2026-07-12 [DECISION] scale fixture는 Task 22개, Step 110개, R 190개, AC 105개, spec Mermaid 9개와 8개 Expedition Route를 사용한다.
- 2026-07-12 [DECISION] source Mermaid, plan Mermaid, derived diagram을 명확히 구분하고 derived diagram에는 기계적으로 계산 가능한 관계만 허용한다.
- 2026-07-12 [DECISION] Viewer의 정보 순서는 요약표 → 시각 흐름 → 상세 Task → AC evidence → 원문 source로 고정한다.
- 2026-07-12 [REJECTED] 별도 `plan-viewer` skill: shell과 locale·mobile·검증 로직이 중복된다.
- 2026-07-12 [REJECTED] generated HTML을 기본 커밋: 큰 binary-like diff와 source drift를 만들 수 있다.
- 2026-07-12 [REJECTED] Notion·Google Docs·별도 docs site를 필수 검토 경로로 사용: source 동기화와 운영 부담이 증가한다.
- 2026-07-12 [DECISION] 사용자가 Viewer 명시 요청 정책 change delta를 승인했다.
- 2026-07-13 [DECISION] plan 진행 상태는 기본적으로 `plan.md`에 기록하고, 긴 실행 기록은 `progress.md`, 독립 소유권이 필요한 큰 Task만 `tasks/*.md`로 분리한다.
- 2026-07-13 [DECISION] plan은 경로와 ID 면에서 spec에 종속되지 않고 `Related Specs`로 0개 이상의 spec을 참조할 수 있지만, 제품 동작 변경에는 기존 approved spec gate를 유지한다.
- 2026-07-13 [DECISION] 사용자가 독립 spec·plan 문서 구조, combined Viewer 제거, plan 진행 기록 구조, 열람 시 SHA-256 freshness 검증 변경안을 승인했다.
- 2026-07-13 [DECISION] 사용자가 Markdown source의 정확성 검증은 유지하되 생성된 개별 HTML View의 post-build 레이아웃 검증은 제외하는 변경을 승인했다.
- 2026-07-31 [APPROVED] 사용자가 R57과 AC14의 `web-app-design`·`website-design` Viewer routing delta를 승인하고 구현 계획 진행을 요청했다.
- 2026-08-01 [DECISION] spec mode는 current structured spec을 primary로, 선택된 comparison source를 비권위 비교 자료로 사용한다. plan mode는 `plan.md`·선택적 `progress.md`·`tasks/*.md`를 primary set으로, Related Specs 0..N를 provenance가 표시된 context로 사용한다.
- 2026-08-01 [DECISION] Review Viewer panel content는 deterministic structured parser가 Markdown source에서 생성하며 수동 HTML content fragment 입력을 제거한다.
- 2026-08-01 [DECISION] 상시 Spec Pages는 Review Viewer와 다른 artifact이며 `docs/specs/semantic-spec-bundles/semantic-spec-bundle-contract.md`가 lifecycle·경로·검증 계약을 소유한다.
- 2026-08-01 [APPROVED] 사용자가 요청형 Review Viewer, `.forge/reviews/` 비추적 output, structured source provenance와 상시 Spec Pages 분리를 승인하고 구현 진행을 요청했다.
- 2026-08-03 [DECISION] Mermaid runtime은 렌더링할 diagram이 있을 때만 embed한다. 측정에서 40줄 fixture spec의 `--offline` snapshot이 3.59MB로 나왔고, 원인은 diagram 유무와 무관한 runtime 인라인이었다.
- 2026-08-03 [DECISION] panel 제목은 명사형 label로 되돌리고 기존 질문 문장은 제목 아래 orientation 문장으로 유지한다. 질문형 제목의 방향 제시 효과는 남기면서 목차와 tab의 스캔 비용을 줄인다.
- 2026-08-03 [DECISION] provenance는 panel·source group당 1회로 축약하되 manifest와 History panel의 전체 기록은 유지한다. 40줄 fixture에서도 같은 출처 문자열이 6회 반복돼 실제 규모에서는 소음이 된다.
- 2026-08-03 [APPROVED] 사용자가 조건부 Mermaid runtime, Overview 요약 지표, provenance 반복 축약과 명사형 panel 제목 delta를 승인하고 계획 작성을 요청했다.
- 2026-08-04 [APPROVED] 사용자가 adaptive Presentation Plan 기반 Review Viewer와 explicit-request-only HTML 생성 경계를 승인하고 구현 진행을 요청했다.
- 2026-08-09 [APPROVED] 사용자가 사람이 이해할 수 있는 Spec Bundle과 문장 기반 추적성 Spec Delta를 승인하고 구현 진행을 요청했다.
- 2026-08-09 [CHANGE] 단일 문서와 숫자 clause namespace를 multi-file Spec Bundle, member path와 완전한 문장 기반 계약으로 교체했다.
