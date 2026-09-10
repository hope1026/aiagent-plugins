# Forge 원칙 중심 실행 지침 적용

Status: complete

**Related Specs:**
- bundle: docs/specs/canonical-spec-workflow/
- bundle: docs/specs/adaptive-execution-routing/
- bundle: docs/specs/web-app-design-quality/
- bundle: docs/specs/forge-ui-design-skill-separation/
- bundle: docs/specs/forge-repository-maintenance/
- bundle: docs/specs/review-viewer-lifecycle/

**Goal:** 승인된 분석의 개선 방향을 적용해 결과·계약·증거 원칙은 보존하고 질문·TDD·실행 기록·스킬 형식의 불필요한 강제를 줄인다.

사용자의 2026-09-10 “수정하자”는 [분석 보고서](../../research/2026-09-10-forge-principle-first-audit.md)의 구체적인 개선 방향을 승인한다. 동일한 결정은 다시 질문하지 않는다. 구현, 로컬 검증과 문서 정합성을 다루며 배포·전역 설정 변경은 포함하지 않는다.

## Verification Scope

기존 implemented baseline의 영향 항목을 수정한다. 스킬의 의미는 실제 요청 시나리오로 검토하고, 기계 검사는 문서 파서·경로·설치·소유권·훅 출력 등 실행 가능한 계약을 검증한다. 전체 제품이나 모델별 성능 개선을 주장하지 않는다. Baseline hash와 exact statement 변경은 `.forge/work/principle-first/spec-delta.md`에 보존한다.

### Task 1: 승인 의미와 정본을 일치시킨다

목표 기여: 질문·검증·계획·위임·디자인·유지보수 계약의 충돌을 제거한다.

- [x] **Step 1:** baseline을 기록하고 승인 범위의 정확한 문장 변경과 링크 갱신을 반영한다.
- [x] **Step 2:** Markdown writer transaction을 통과한다.

### Task 2: 실행 스킬과 소비 문서를 축소한다

목표 기여: 기존 설치 이름과 데이터 형식을 유지하며 선택 가능한 수행 방법과 필수 원칙을 분리한다.

- [x] **Step 1:** 라우터·검증·TDD·디버깅·계획·위임·디자인·tone·유지보수 지침을 갱신한다.
- [x] **Step 2:** 필요한 상세 참조, bootstrap, manifest 설명과 README를 맞추고 manager로 adapter를 렌더링한다.

### Task 3: 결과 중심 검증을 수행한다

목표 기여: 절차 문구 존재 검사를 실제 구조·행동 증거로 대체하면서 기존 도구 계약을 보존한다.

- [x] **Step 1:** 관련 정책·설치·훅 검사와 parser·manager 회귀를 실행한다.
- [x] **Step 2:** 독립 시나리오 실행·검토로 과잉 절차와 계약·검증 누락을 함께 확인한다.
- [x] **Step 3:** 통합 검증 결과와 남은 한계를 기록한다.

## Progress History

- 시작: 분석 보고서의 개선안 승인. 기존 checkout에는 해당 조사 문서만 untracked 상태다.

- 완료: 공통 스킬과 조건부 참조, 소비 정본·exact 링크, bootstrap·정책 검사를 정리했다. Parser 66개, manager 17개, shell 검사 11개와 대표 독립 실행·대응안 검토를 확인했다. [검증 기록](../../evidence/principle-first-forge.md)에 관찰과 한계를 남긴다. 변경 bundle은 approved로 유지하고 전체 플랫폼 동작이나 성능 개선을 주장하지 않는다.
