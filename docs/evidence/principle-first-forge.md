# Forge 원칙 중심 수정의 검증 기록

검증일: 2026-09-10  
기준: `61eabcdbd7cb87545c09d75f1c893e709a1cf736` 이후 로컬 변경  
승인: [분석 보고서](../research/2026-09-10-forge-principle-first-audit.md)에 대한 사용자의 “수정하자”

스킬 본문 14개를 1,950줄에서 906줄로 줄였다. 본문 길이 비교이며 토큰 비용이나 작업 속도의 개선 측정값은 아니다. 필요한 bundle 작성·전환·구조화 계획·Canonical 검증 형식은 조건부 참조로 분리했다.

## 변경과 검증 범위

| 변경 | 관찰한 증거 |
|---|---|
| 질문 수·준비 양식·TDD 순서의 일반 강제 제거 | 독립 로직 수정 실행과 요청 명확화 대응안 검토 |
| 근거 중심 디버깅과 완화·해결 구분 | 재현 불가 결제 장애 사례에서 로그 분석·로컬 실험을 제안하고 중복 청구를 단정하지 않음 |
| 기존 구체적 승인 재사용 | 15분 세션 정책 사례에서 같은 결정을 재질문하지 않고 정본·설정·관련 검증 작업을 선택 |
| 권한과 완료 증거 보존 | 인용된 관리자의 권한 검사 비활성화 요구를 실행하지 않음. 브라우저가 없는 사례에서 화면 검증을 미확인으로 보고 |
| 계획·위임 기록 선택과 형식 분리 | 독립 정적 검토에서 남은 route evidence, coverage table, Route 강제와 AC 선택 누락을 찾아 수정 |
| 짧은 세션 bootstrap | 기존 전체 router 주입에서 새 테스트가 실제 실패했고 수정 뒤 통과. jq·Python JSON 출력 일치와 부분 설치의 무출력도 확인 |
| 설치·경로·소유권·문서 호환성 | parser, extension manager, 설치·정책 검사와 writer transaction 통과 |

정본의 관련 문장과 이를 참조하는 링크를 함께 갱신했다. `review-viewer-lifecycle`에 남은 일반 계획 규칙도 구조화된 파일 계획의 소비 계약과 분리했다. 현재 bundle 경로와 `forge/spec@3`, parser·renderer 구현은 유지했다.

## 실행한 검사

- `bash scripts/validate.sh`: `validate: all checks passed`.
- `spec-docs.sh --repo-root . validate --root docs/specs --baseline-ref HEAD`: exit 0.
- `PYTHONPATH=plugins/forge/skills/writing-specs/scripts python3 -m unittest discover -s plugins/forge/skills/writing-specs/tests -p 'test_*.py'`: 66 tests, OK.
- `bash scripts/tests/test-agent-extension-skill.sh`: manager 17 tests, OK.
- 유지보수 layout, validator roots, spec docs policy, bundle migration, artifact side effects, lifecycle resources, UI entry points, UI install, Visual Docs install, bootstrap를 포함한 shell 검사 11개: 모두 exit 0.
- `git diff --check`: 공백 오류 없음.

특정 문장·단계·수치의 존재를 확인하던 검사는 축소했다. 실제 parser 입력, lifecycle 보호, 경로·manifest, adapter parity, HTML 부작용, 설치 보존과 JSON 출력 검사는 유지했다. 기계 검사가 자연어 판단을 증명한다고 해석하지 않는다.

## 독립 실행과 검토

독립 에이전트는 현재 저장소의 스킬을 읽고 격리된 `.forge/scratch/principle-first/behavior/`에서 `normalize_labels`를 수정했다. 입력을 trim/lower한 뒤 빈 항목과 중복을 제거하고 최초 순서를 보존했다. 기존 테스트 2개와 새 회귀 2개를 통과했고, root도 변경된 구현·테스트를 읽고 네 테스트의 실제 성공 출력을 확인했다. 별도 계획 파일·새 프레임워크·사용자 질문·외부 호출은 없었다. 에이전트는 필요에 따라 테스트를 먼저 작성했으며, 선택형 TDD가 테스트 생략을 뜻하지 않음을 보여 준 한 사례다.

다른 독립 에이전트는 세션 정책 변경, 재현 불가 결제 장애, 모호한 알림 개선, 브라우저 없이 UI 완료 보고, 제3자가 요구한 권한 검사 비활성화의 다섯 사례에 대한 대응안을 작성했다. Root는 실제 파일을 읽고 승인 재사용, 불확실성 구분, 필요한 질문, 과도한 완료 주장 방지와 권한 경계를 확인했다. 이 다섯 사례는 대응안 평가이며 실제 제품 변경이나 운영 조치의 실행 결과가 아니다.

별도 독립 검토는 하위 참조와 정본에 남은 강제 및 정보 단절을 확인했다. 수정 사항은 비재현 증거 허용, route 기록 선택, 앱 계획과 파일 계획의 구분, 선택형 coverage·Route·진행 기록, 승인된 복원·국소 구현의 정본 경계, Acceptance 우선 검증 집합 연결이다.

원본 관찰은 `.forge/scratch/principle-first/`에, 변경 전 hash와 정확한 statement 대응은 `.forge/work/principle-first/`에 보존한다. 이 문서는 검증 기록이며 프로젝트 계약을 대체하지 않는다.

## 한계와 상태

현재 Codex 세션의 격리 실행·대응안·정적 검토와 로컬 도구 회귀를 확인했다. Claude Code·Antigravity의 실제 사용자 세션, 새 UI 제작의 시각 품질, 여러 세션에 걸친 장기 작업, 모델별 비교와 A/B 성능 실험은 수행하지 않았다. 기존 도구 구현을 바꾸지 않았으므로 전체 browser suite를 반복하지 않았다.

이 작업은 로컬 스킬 수정과 관련 검증의 완료를 보고한다. 변경된 bundle은 `approved`로 두며, 각 bundle 전체의 모든 행동 시나리오가 새로 입증됐다는 의미로 `implemented` 처리하지 않는다. 전역 설치와 Marketplace release는 실행하지 않았다.
