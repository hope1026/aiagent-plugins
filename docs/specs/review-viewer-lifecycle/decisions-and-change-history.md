# 현재 결정

## Decisions & History

- 2026-09-17 [CURRENT] 일반 시각화는 앱 기능과 모델 판단에 맡긴다. Forge 원문을 시각화할 때는 의미·조건·상태·출처를 보존하되 표현과 도구를 자유롭게 선택하고 별도 source 파일이나 composition을 강제하지 않는다. 기존 공용 renderer는 재생성 가능한 tracked Project Handbook, 명시적 freshness·재현성 요청과 기존 관리형 문서 갱신에 선택적으로 사용한다. 네 kind, CLI, manifest, no manual generated HTML과 재현성 계약은 관리형 경로 안에서 유지한다. 양 경로 모두 Markdown authority, 요청에 따른 생성·갱신과 실제 읽기 검증을 유지한다.
- 2026-09-17 디자인 스킬 제거에 따라 공용 tooling UI 검증은 `verifying-work`의 선택형 UI 참고 문서로 연결한다. 개별 문서 제작과 공용 renderer의 나머지 계약은 유지한다.
