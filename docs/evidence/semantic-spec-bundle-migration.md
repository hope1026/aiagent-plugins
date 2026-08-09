# Spec Bundle migration evidence

이 문서는 숫자 ID 기반 `forge/spec@2` source를 의미 기반 `forge/spec@3` Spec Bundle로 바꾸는 일회성 migration의 baseline과 검증 결과를 보존한다. Canonical Spec이나 Execution Plan을 대신하지 않는다.

## 승인과 실행 source

- 승인일: 2026-08-09
- 승인된 변경안: `.forge/work/spec-bundle-semantic-trace/spec-delta.md`
- 실행 계획: `docs/plans/013-semantic-spec-bundle-migration/plan.md`
- Review Viewer 생성 권한: 없음
- Release와 push 권한: 없음

## 원본 baseline

| 기존 source | 승인 전 lifecycle | 승인 전 source SHA-256 | 새 bundle |
|---|---|---|---|
| `docs/specs/001-tone-overlays/spec.md` | `implemented` | Git baseline에서 candidate 생성 시 기록 | `docs/specs/tone-overlay-skills/` |
| `docs/specs/002-lifecycle-review-viewer/spec.md` | `implemented` | `7d6f19aa2ab044d3ad0d066e284ffb4cc8d68340259a8b0cea8c5c709d327b63` | `docs/specs/review-viewer-lifecycle/` |
| `docs/specs/003-repository-maintenance-runbook/spec.md` | `implemented` | Git baseline에서 candidate 생성 시 기록 | `docs/specs/forge-repository-maintenance/` |
| `docs/specs/004-adaptive-execution-routing/spec.md` | `implemented` | Git baseline에서 candidate 생성 시 기록 | `docs/specs/adaptive-execution-routing/` |
| `docs/specs/005-agent-extension-creation/spec.md` | `implemented` | Git baseline에서 candidate 생성 시 기록 | `docs/specs/cross-agent-extension-creation/` |
| `docs/specs/006-ui-design-skill-split/spec.md` | `implemented` | Git baseline에서 candidate 생성 시 기록 | `docs/specs/forge-ui-design-skill-separation/` |
| `docs/specs/007-ui-design-removal/spec.md` | `implemented` | Git baseline에서 candidate 생성 시 기록 | `docs/specs/legacy-ui-design-skill-removal/` |
| `docs/specs/008-structured-spec-pages/spec.md` | `implemented` | `fbafc2f9df344911b876c7f278613087d777c2e0215d79986d761557567f3c2f` | `docs/specs/semantic-spec-bundles/` |
| `docs/specs/009-canonical-spec-work-artifacts/spec.md` | `implemented` | `2cef63228ed054d75e322885653f043328921b48280934837cef4118c233709a` | `docs/specs/canonical-spec-workflow/` |

표에서 “candidate 생성 시 기록”으로 표시한 값은 계획 commit의 Git object bytes에서 계산해 candidate validation 전에 이 문서에 추가한다. 작업 디렉터리의 변경된 bytes를 baseline으로 사용하지 않는다.

## 대상 member 구성

| 새 bundle | root와 member |
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

## Statement migration rule

- 기존 active Requirement와 Acceptance Criterion의 규범 문장은 숫자 ID, `MODIFIED`·`ADDED` 표시와 list marker를 제거한 H3 heading으로 이동한다.
- 기존 Acceptance Criterion이 참조한 각 Requirement는 같은 bundle의 member path, heading anchor와 exact link text로 연결한다.
- 기존 `REMOVED` tombstone은 active statement로 이동하지 않고 `Decisions & History`의 과거 변경 기록으로만 보존한다.
- 이 migration을 승인한 Spec Delta가 명시적으로 바꾼 문장 외에는 규범적 의미를 변경하지 않는다.
- v2 raw bytes와 old ID는 Git history와 이 evidence의 mapping에서만 보존한다.

## Candidate gate

Candidate는 다음 결과를 이 문서에 추가한 뒤에만 production root로 승격할 수 있다.

- 계획 commit의 HEAD, index, tracked bytes와 untracked bytes fingerprint
- 9개 old source의 Git object SHA-256
- 9개 target bundle의 `bundleSha256`
- old R·AC에서 member path·exact statement로의 완전한 mapping
- unit, repository, install, pressure, rollback validation command와 결과
- active source·plan·skill·fixture의 legacy author-facing ID inventory 0개
- Review Viewer 생성 count 0개
- production root fingerprint unchanged 또는 verified candidate fast-forward 결과

## 진행 기록

- 2026-08-09: 사용자가 exact Spec Delta를 승인했다.
- 2026-08-09: 세 governing source에 승인 의미를 bootstrap 형식으로 반영하고 repository writer transaction을 통과했다.
