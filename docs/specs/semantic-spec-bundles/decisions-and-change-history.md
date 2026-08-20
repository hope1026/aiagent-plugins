# 현재 결정

## Decisions & History

- 2026-08-20 [CURRENT] 하나의 Canonical Spec은 의미 기반 directory 안의 설명적인 Markdown 파일들로 구성하고 bundle·member path와 완전한 Requirement 문장으로 추적한다. Requirement는 필수이고 `Acceptance Criteria`는 bundle 단위로 선택하며, 사용한 bundle만 모든 Requirement에 대한 Acceptance coverage를 유지한다. Placeholder Requirement와 source 일치만 반복하는 Acceptance는 계약으로 사용하지 않는다. 일반 lifecycle은 Markdown-only이고 명시적 `visual-docs` 요청만 비추적 local View 또는 재생 가능한 tracked Project Handbook을 생성하며, exact path transition은 one-to-one `superseded`와 coordinated many-to-one `merged`를 지원한다.
