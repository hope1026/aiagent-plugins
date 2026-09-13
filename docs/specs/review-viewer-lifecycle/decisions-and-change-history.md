# 현재 결정

## Decisions & History

- 2026-09-13 [CURRENT] Visual Docs는 명시적 요청 범위에서 원문을 보존하고 agent가 독자 질문·답·설명 순서·표현을 근거 기반 composition으로 작성해 공개 builder에 전달한다. Profile과 자동 관계 추출은 보조 수단이며 특정 heading이나 도표 수가 이해 품질을 결정하지 않는다. 별도 설명은 조건·예외·의무 강도·수치·상태를 보존하고 정확한 원문에 연결한다. 기계적 검증, 의미 검토, 실제 출력의 읽기·표시 검증을 분리하고 source-browser를 완성된 설명으로 표시하지 않는다. 재현성은 source·고정 composition·generator·build options에 적용한다. 네 kind의 source ownership, 요청형 생성, no manual HTML과 Markdown authority는 유지한다.
