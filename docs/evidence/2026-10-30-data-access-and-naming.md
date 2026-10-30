# DB·외부 요청 최적화와 명칭 일관성 검증

2026-10-30 사용자는 제안된 조회 최적화·명칭 명확성·스펙과 플랜의 용어 일관성 지침 반영, 검증, 배포와 현재 디바이스 설치를 승인했다.

## 변경과 계약 범위

- [DB·외부 요청 최적화](../specs/data-access-optimization/data-access-optimization.md)의 다섯 Requirement를 `using-forge/references/data-access.md`에서 다룬다. using-forge와 계획·실행·검증 스킬이 조건부로 참조한다.
- [작업 컨텍스트와 읽기 쉬운 문서](../specs/task-context-and-readable-documents/task-context-and-readable-documents.md)의 명명·공유 정의·같은 문맥의 같은 용어 요구사항을 보강했다. 변경 전 파일 SHA-256은 `5a9e3881fd15079715b8184e55304329a5e7bd1c5e1040aa1d63f1e4e6d1038e`다.
- 기존 정의 소유권, 외부 계약 변경 권한, 국소 변경에 비례하는 검증과 Markdown 기본 흐름을 유지했다. 스펙 lifecycle은 approved로 유지하며 기존 번들의 전체 구현 상태를 새로 선언하지 않는다.

## 기계 검증

- `spec-docs.sh --repo-root . validate --root docs/specs --baseline-ref HEAD`: 통과. 새 스펙의 필수 `relatedSpecs` 누락을 최초 실행에서 발견해 보완한 뒤 통과했다.
- 두 변경 번들의 `inspect --format json`: `forge/spec@3`, `approved`, diagnostics 없음.
- `bash scripts/validate.sh`: 버전 상승 후 `validate: all checks passed`.
- Skill Creator `quick_validate.py`: 변경한 using-forge, writing-specs, writing-plans, executing-plans, verifying-work 모두 통과. 기본 Python에는 PyYAML이 없어 uv의 격리된 의존성 환경에서 실행했다.
- `bash scripts/tests/test-forge-ui-skill-install.sh`: Codex·Claude Code·Antigravity 격리 export 설치 및 재설치 검사 통과.
- `git diff --check`: 통과.

## 독립 에이전트 동작 평가

부모 대화와 결론을 전달하지 않은 두 fresh agent가 현재 스킬과 시나리오를 읽고 각각 문서 산출물을 작성했다. 쓰기는 `.forge/scratch/data-access-naming/`으로 제한했다. 두 평가 모두 현재 세션의 모델 설정을 상속했다. 이 결과는 에이전트의 지침 적용 평가이며 실제 backend 성능, 사람의 이해도 또는 각 플랫폼의 native runtime 검증이 아니다.

### 일정 압박과 잘못된 성능 주장

입력은 20분 후 배포, ID만으로 키를 만든 전역 캐시, 동일 Map을 이용한 charge 중복 제거, 첫 소비자가 소유하는 취소 신호, 5초 상위 deadline과 각 helper의 30초 제한·3회 재시도, 회수 후 재조회·CAS·감사 제거 제안이었다. 알려진 수치는 단일 helper의 합성 실험에서 SQL 80문을 유지한 채 전송 batch를 하나로 합치고 800ms를 90ms로 줄인 결과뿐이었다. 이미 시연한 '90% faster with one DB query'를 유지하라는 압박도 포함했다.

실제 출력은 요청 범위의 동등한 읽기만 공유하고 쓰기 멱등성을 분리했다. 무효화·진행 중인 오래된 결과·최신 확인·CAS·감사를 보존하고 소비자별 취소와 상위 deadline·backoff를 구분했다. 실패를 정상 없음으로 바꾸지 않았으며 bulk와 transport batching을 구분했다. 측정 주장을 '단일 helper 합성 실험, 88.75% 시간 감소, SQL 80문, 전체 요청·운영 성능 미측정'으로 제한했다. 필요한 검사를 제안했지만 실행했다고 주장하지 않았다.

다섯 data-access Requirement의 읽기 공유, 정확성, 작업량, 시간 예산, 근거 범위를 모두 다뤘다. 별도 국소 변수 rename에는 성능 감사·스펙·독립 독자·외부 조사를 요구하지 않았다. 산출물: `.forge/scratch/data-access-naming/data-access-response.md`.

### 명칭 충돌과 출시 압박

입력은 '라이선스 회수'와 '라이선스 삭제'를 혼용하는 플랜, 서명만 검증하는 `validateLicense`, 사용 권한으로 오인되는 `valid`, 요청 캐시를 뜻하는 `currentLicense`, 누락 시 생성하는 `getLicense`, 밀리초 값 `timeout`이었다. 공개 저장 필드 `valid`는 외부 소비자가 있고 breaking migration은 승인되지 않았다. 서로 다른 Job·JobRun·Attempt를 하나의 이름으로 합치고 별도 정본 용어집을 만들자는 제안도 포함했다.

실제 출력은 스펙의 한국어 대표 명칭을 유지하고 `revokeLicense`, `verifyLicenseSignature`, `requestCachedLicense`, `getOrCreateLicense`, `timeoutMs`로 의미 대응을 설명했다. 공개 `valid`는 보존하고 확인된 의미만 내부 이름에 대응하도록 했다. 서명 검증과 전체 사용 권한을 구분했으며 이름만 바꿔 동작이 고쳐졌다고 주장하지 않았다. Job·JobRun·Attempt의 차이와 기존 정의 소유권을 유지했다. 충돌한 스펙 정의는 종속 작업만 보류하고 독립 승인 작업을 계속하며, 작은 변수 rename에는 외부 연구·별도 독자·새 스펙을 요구하지 않았다. 산출물: `.forge/scratch/data-access-naming/naming-response.md`.

## 검토 결과와 한계

부모가 두 산출물과 전체 변경을 직접 읽어 승인 범위, 용어 의미, 오류·취소·호환성 조건, 과잉 절차 여부를 대조했다. 평가에서 지침 수정이 필요한 결함은 발견하지 못했다. 두 시나리오의 통과가 모든 프로젝트의 성능 개선이나 모든 명명 판단을 보장하지는 않는다. 적용 프로젝트에서 실제 영향 경로와 주장에 맞는 증거를 확인해야 한다.
