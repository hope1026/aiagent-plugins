# 의미 기반 Spec Bundle 검증 기록

이 문서는 현재 Forge의 Spec Bundle 계약을 구현한 candidate의 검증 결과만 기록한다. Canonical Spec이나 Execution Plan을 대신하지 않는다.

## 권위와 범위

- 승인일: 2026-08-09
- 실행 계획: `docs/plans/013-semantic-spec-bundle-migration/plan.md`
- Canonical source: `docs/specs/` 아래 의미 기반 Spec Bundle 아홉 개
- Review Viewer HTML 생성 권한: 없음
- Release와 push 권한: 없음

## 현재 bundle 구성

| bundle | root와 member |
|---|---|
| `docs/specs/tone-overlay-skills/` | `tone-overlay-skill-contract.md` |
| `docs/specs/review-viewer-lifecycle/` | `human-readable-review-viewer.md`, `source-selection-and-freshness.md`, `adaptive-presentation-and-navigation.md`, `plan-context-and-statement-traceability.md`, `decisions-and-change-history.md` |
| `docs/specs/forge-repository-maintenance/` | `forge-repository-maintenance-contract.md` |
| `docs/specs/adaptive-execution-routing/` | `adaptive-execution-routing-and-checkpoints.md` |
| `docs/specs/cross-agent-extension-creation/` | `cross-agent-extension-creation.md` |
| `docs/specs/forge-ui-design-skill-separation/` | `forge-ui-design-skill-separation.md` |
| `docs/specs/legacy-ui-design-skill-removal/` | `legacy-ui-design-skill-removal.md` |
| `docs/specs/semantic-spec-bundles/` | `semantic-spec-bundle-contract.md`, `authoring-and-file-organization.md`, `statement-traceability-and-validation.md`, `lifecycle-consumers-and-migration.md`, `decisions-and-change-history.md` |
| `docs/specs/canonical-spec-workflow/` | `canonical-spec-and-work-artifact-boundaries.md`, `routing-and-lifecycle-gates.md`, `verification-and-durable-authority.md`, `decisions-and-change-history.md` |

## 검증 기준

- 모든 bundle directory와 member filename은 내용을 설명하는 lowercase kebab-case를 사용한다.
- Root의 `Documents` inventory는 모든 Markdown member를 정확히 한 번 선언한다.
- Requirement와 Acceptance Criterion은 완전한 H3 문장으로 작성하고 Acceptance는 exact member path·heading anchor·link text로 Requirement를 참조한다.
- Parser, validator, plan trace, Review Viewer source와 renderer는 bundle·member path와 완전한 문장을 공통 계약으로 사용한다.
- 현재 runtime, skill, 문서, plan과 정상 fixture에는 이전 schema나 숫자 locator 호환 경로가 없다.
- 일반 검증 과정은 Review Viewer HTML을 생성하지 않는다.

## Fresh evidence

- writing-specs v3-only Python suite: 56 tests PASS.
- 아홉 Spec Bundle repository validation: PASS.
- Canonical source migration gate: PASS.
- Review source·IR·planner focused suite: 후속 통합 검증에서 갱신한다.
- Renderer·freshness·distribution·pressure suite: 후속 통합 검증에서 갱신한다.

## 진행 기록

- 2026-08-09: bundle model·repository validator와 full-statement plan trace를 구현했다.
- 2026-08-09: 아홉 Canonical Spec을 의미 기반 bundle와 설명적인 member filename으로 정리했다.
- 2026-08-09: 현재 트리에서 이전 parser, 정상 호환 경로, 전용 fixture와 대체된 실행 문서를 제거했다.
