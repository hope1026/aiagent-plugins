# 현재 결정

## Decisions & History

- 2026-08-20 [CURRENT] Forge는 지속할 프로젝트 계약만 semantic Spec Bundle에 보존하고 Canonical Spec 영향과 실행 복잡도를 독립적으로 분류한다. 변경 추적은 bundle path·member path·완전한 문장을 사용하며, Canonical verification set은 Acceptance statement가 있으면 Acceptance를, 없으면 Requirement를 사용한다. Plan과 lifecycle verification은 같은 fallback을 적용한다. Visual Docs의 생성 조건과 HTML artifact lifecycle은 `docs/specs/review-viewer-lifecycle/`이 소유한다.
