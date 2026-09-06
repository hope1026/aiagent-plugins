# 현재 결정

## Decisions & History

- 2026-09-04 [CURRENT] `visual-docs`는 Brief와 Plan의 Work View, 독립 Spec View와 Project Handbook을 하나의 source-backed renderer로 제공한다. Source에 명시된 순서, 계층, 소유, 의존과 mapping 관계가 객관적 threshold를 충족하면 relation shape에 맞는 flowchart·sequence, structure map, dependency·coverage graph 또는 comparison matrix를 primary reading path에 포함한다. 관계가 없는 단순 prose와 short list에는 diagram을 만들지 않으며, derived visual은 source 밖 의미를 추가하지 않고 text·table 대체 경로와 provenance를 함께 제공한다. 모든 생성과 갱신은 사용자의 명시적 요청을 요구한다.
