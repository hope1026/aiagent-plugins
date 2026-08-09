# 결정과 변경 이력

## Decisions & History

- 2026-08-01 [DECISION] 구조화 spec authoring과 validation은 기존 `writing-specs`가 소유하고 별도 spec authoring skill을 추가하지 않는다.
- 2026-08-01 [DECISION] per-spec `index.html`과 `docs/specs/index.html`은 spec 변경과 항상 함께 갱신되는 committed Spec Pages로 유지한다.
- 2026-08-01 [DECISION] 요청형 Review Viewer와 상시 Spec Pages는 같은 parser·rendering 기반을 재사용할 수 있지만 생성 trigger, 경로, Git 정책과 freshness 상태를 분리한다.
- 2026-08-01 [REJECTED] `spec-portal`을 장기 workflow skill로 유지: migration 이후 별도 orchestration 책임이 남고 `writing-specs`와 중복된다.
- 2026-08-01 [DECISION] Review Viewer의 `.forge/reviews/` 비커밋 전환은 lifecycle Viewer를 소유하는 `002`의 별도 승인 delta에서 처리하고, 이 spec은 Spec Pages build를 Viewer 생성 권한으로 해석하지 않는다.
- 2026-08-01 [APPROVED] 사용자가 구조화 Spec 계약, 상시 Spec Pages, 일괄 Forge migration과 요청형 Review Viewer 경계를 승인하고 구현 진행을 요청했다.
- 2026-08-02 [APPROVED] 사용자가 current-state spec supersession delta를 검토하고 구현 진행을 승인했다.
- 2026-08-03 [DECISION] Mermaid runtime은 page에 렌더링할 diagram이 있을 때만 embed한다. 측정 결과 diagram이 없는 spec의 page도 runtime 3.48MB를 무조건 포함해 3KB source가 3.58MB page가 됐고, 실제 프로젝트에서 35개 중 20개가 diagram 0개였다.
- 2026-08-03 [DECISION] 빈 `Behavior & Flows` section을 그대로 노출하는 대신 frontmatter `relatedSpecs`에서 파생한 관계 도식을 `Derived view`로 표시한다. 파생 입력을 frontmatter 명시 관계로 제한해 "source에 없는 관계를 추가하지 않는다"는 비목표를 유지한다.
- 2026-08-04 [APPROVED] 사용자가 flexible Markdown source, Markdown-only lifecycle과 명시적 `review-viewer` 요청에 한정된 HTML 생성을 승인하고 구현 진행을 요청했다.
- 2026-08-09 [APPROVED] 사용자가 사람이 이해할 수 있는 Spec Bundle과 문장 기반 추적성 Spec Delta를 승인하고 구현 진행을 요청했다.
- 2026-08-09 [CHANGE] 숫자 identifier와 범용 파일명을 의미 기반 bundle path, descriptive filename과 문장 link로 교체했다.
