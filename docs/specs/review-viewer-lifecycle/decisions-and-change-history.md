# 현재 결정

## Decisions & History

- 2026-08-09 [CURRENT] `visual-docs`는 Brief와 Plan의 Work View, 독립 Spec View와 Project Handbook을 하나의 source-backed renderer로 제공한다. Canonical Spec은 규범적 계약, Project Map은 사람이 작성한 프로젝트·구조 설명, repository scan은 derived evidence를 소유한다. Local View는 `.forge/visual-docs/`에 비추적으로 저장하고 Project Handbook만 `docs/project-viewer/index.html`의 재생 가능한 tracked HTML로 허용하며, 모든 생성과 갱신은 사용자의 명시적 요청을 요구한다.
