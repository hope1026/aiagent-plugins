# Forge 유지보수 런북 분리

Status: approved

## Overview

Forge 플러그인은 설치 사용자가 프로젝트에서 실행하는 스킬만 배포한다. Forge 자체를 개선하거나 배포 구조를 수정하는 절차는 이 저장소의 `.agent-runbooks/`를 정본으로 삼고, Codex와 Claude Code의 저장소 로컬 스킬은 동일한 런북을 읽는 얇은 진입점으로 유지한다.

이 문서에서 `R`은 Requirement(필수 동작 또는 제약), `AC`는 Acceptance Criterion(요구사항 충족을 관찰할 수 있는 증거)을 뜻한다.

범위에 포함하지 않는 항목:

- Forge 사용자 실행 스킬의 spec-first 동작 변경
- Marketplace 설치 명령이나 플러그인 이름 변경
- 저장소 전용 유지보수 스킬을 사용자 환경에 전역 설치하는 기능
- Forge 외 다른 플러그인을 위한 저장소 런북 추가

## Requirements

- R1. Forge Marketplace 패키지를 구성할 때 `plugins/forge/skills/`에는 설치 사용자가 실행하는 스킬만 존재해야 하며, `maintaining-forge`와 그 유지보수 전용 reference는 포함하지 않아야 한다.
- R2. `.agent-runbooks/README.md`는 저장소 공용 런북의 목적과 wrapper 규칙을 설명해야 한다. Forge 자체의 스킬, manifest, hook, validator, 설치 스크립트 또는 배포 문서를 변경할 때 에이전트가 따를 공용 절차는 `.agent-runbooks/maintaining-forge/README.md`를 단일 정본으로 사용해야 한다.
- R3. `maintaining-forge`는 스킬 작성·검토 절차의 일부로 repository-only workflow의 공용 런북 패턴을 설명해야 한다. 상세 절차·명령·script·reference·검증·보고 규칙은 `.agent-runbooks/<name>/`에 두고, `.agents/skills/<name>/`과 `.claude/skills/<name>/`에는 trigger와 공용 런북 연결만 남겨야 한다. Marketplace에 배포하는 Forge 사용자 스킬은 기존처럼 `plugins/forge/skills/<name>/`의 portable 단일 원본을 사용해야 한다.
- R4. Codex가 이 저장소에서 Forge 유지보수 작업을 인식할 수 있도록 `.agents/skills/maintaining-forge/SKILL.md`를 제공하고, 해당 wrapper는 공용 런북과 필요한 reference를 읽도록 안내해야 한다.
- R5. Claude Code가 이 저장소에서 같은 작업을 인식할 수 있도록 `.claude/skills/maintaining-forge/SKILL.md`를 제공하고, Codex wrapper와 동일한 공용 런북을 사용해야 한다.
- R6. Forge 사용자용 router, skill catalog 및 설계 문서는 `maintaining-forge`를 배포 스킬로 안내하지 않아야 하며, 저장소 유지보수 문서는 이를 repository-only runbook으로 안내해야 한다.
- R7. 저장소 validator는 `plugins/*/skills/`, `.agents/skills/`, `.claude/skills/`의 `SKILL.md`를 검사하고, 두 `maintaining-forge` wrapper가 공용 런북을 가리키는지 확인해야 한다.
- R8. Marketplace 설치와 로컬 개발 설치는 기존처럼 `plugins/forge/`의 사용자 실행 스킬만 설치해야 하며, `.agent-runbooks/`, `.agents/skills/`, `.claude/skills/`의 저장소 전용 파일을 사용자 플러그인에 복사하지 않아야 한다.

## Behavior & Flows

Forge 사용자는 Marketplace에서 `plugins/forge/`만 설치하고 사용자 실행 스킬만 발견한다. 저장소 기여자는 저장소 안에서 Forge 유지보수 작업을 요청하면 Codex 또는 Claude Code의 로컬 wrapper가 활성화되고, 두 wrapper 모두 `.agent-runbooks/maintaining-forge/README.md`의 동일한 절차를 따른다.

이 구조는 같은 workspace level의 `weppy-roblox-mcp-private`가 사용하는 패턴을 따른다. `.agent-runbooks/`가 상세 절차의 정본이고, `.agents/skills/`와 `.claude/skills/`는 같은 경로를 가리키는 에이전트별 진입점이다. Forge의 스킬 작성 절차는 이 패턴을 repository-only workflow에 적용하되, 사용자에게 배포하는 portable plugin skill과 혼동하지 않도록 두 유형의 경계를 명시한다.

분리 방식 비교:

| 방식 | 장점 | 단점 | 결정 |
|---|---|---|---|
| `.agent-runbooks/` 공용 정본 + 에이전트별 얇은 wrapper | 절차 중복 없이 두 에이전트가 자동 발견하며 Marketplace에서 자연스럽게 제외됨 | wrapper 두 개의 연결 상태를 검증해야 함 | 채택 |
| `.agents/skills/`에만 저장 | Codex 구성이 단순함 | Claude Code가 자동 발견하지 못하고 공용 정본이 아님 | 제외 |
| 별도 `forge-maintainer` 플러그인 | 독립 설치와 versioning 가능 | 사용자용 Marketplace에 유지보수 개념이 다시 노출되고 현재 요구보다 무거움 | 제외 |

## Data & Interfaces

| 역할 | 경로 | 배포 여부 | 책임 |
|---|---|---|---|
| 런북 index | `.agent-runbooks/README.md` | 배포하지 않음 | 공용 정본 원칙과 wrapper 규칙 설명 |
| 공용 런북 | `.agent-runbooks/maintaining-forge/README.md` | 배포하지 않음 | Forge 자체 변경·검증·pressure test·release 절차의 정본 |
| 공용 reference | `.agent-runbooks/maintaining-forge/references/portability-rules.md` | 배포하지 않음 | Claude Code와 Codex 사이 portability 규칙 |
| Codex wrapper | `.agents/skills/maintaining-forge/SKILL.md` | 배포하지 않음 | 저장소 로컬 trigger와 공용 런북 연결 |
| Claude Code wrapper | `.claude/skills/maintaining-forge/SKILL.md` | 배포하지 않음 | 저장소 로컬 trigger와 공용 런북 연결 |
| 사용자 스킬 | `plugins/forge/skills/*/SKILL.md` | 배포함 | 설치 사용자가 프로젝트에서 실행하는 Forge workflow |

Wrapper 계약:

| 항목 | 요구사항 |
|---|---|
| frontmatter | `name`과 `description`만 포함하고 `name`은 `maintaining-forge` 사용 |
| trigger | Forge 스킬·manifest·hook·validator·설치 스크립트·배포 문서 변경 및 검토 상황 포함 |
| 본문 | 작업 전에 공용 런북과 portability reference를 읽도록 지시 |
| 정본 규칙 | wrapper와 런북이 충돌하면 런북을 따르고 wrapper를 수정 |

스킬 작성 시 저장 위치 결정:

| 스킬 유형 | 상세 절차 정본 | 에이전트 진입점 |
|---|---|---|
| Marketplace에 배포하는 Forge 사용자 스킬 | `plugins/forge/skills/<name>/` | 같은 portable `SKILL.md`를 Claude Code와 Codex가 사용 |
| 이 저장소에서만 사용하는 공용 workflow | `.agent-runbooks/<name>/` | `.agents/skills/<name>/SKILL.md`, `.claude/skills/<name>/SKILL.md`의 얇은 wrapper |

## Acceptance Criteria

- AC1 (R1, R8): 깨끗한 checkout에서 Forge Marketplace source와 로컬 설치 source를 검사하면 `plugins/forge/skills/maintaining-forge`가 없고, 설치 대상 목록에도 저장소 전용 런북과 wrapper가 나타나지 않는다.
- AC2 (R2, R3): `.agent-runbooks/README.md`, `.agent-runbooks/maintaining-forge/README.md`, `.agent-runbooks/maintaining-forge/references/portability-rules.md`가 존재한다. Root index는 공용 정본과 wrapper 규칙을 설명하고, 유지보수 런북과 reference에는 기존 절차, portability 규칙, 사용자 배포 스킬과 repository-only workflow의 저장 위치 결정 규칙이 누락 없이 옮겨져 있다.
- AC3 (R4): Codex 저장소 로컬 skill 경로의 `maintaining-forge` wrapper를 읽으면 공용 런북과 portability reference를 작업 전에 읽으라는 지시가 확인된다.
- AC4 (R5): Claude Code 저장소 로컬 skill 경로의 `maintaining-forge` wrapper를 읽으면 AC3과 동일한 공용 원본을 가리키며 별도 유지보수 절차를 포함하지 않는다.
- AC5 (R6): `plugins/forge/skills/using-forge/SKILL.md`, Forge 사용자 skill catalog 및 현재 설계 문서를 검사하면 `maintaining-forge`가 사용자 배포 스킬이나 Forge 내부 router 대상으로 남아 있지 않다.
- AC6 (R7): 저장소 root에서 `bash scripts/validate.sh`를 실행하면 플러그인 스킬과 두 저장소 로컬 wrapper를 모두 검사한 뒤 `validate: all checks passed`를 출력한다.
- AC7 (R2, R4, R5): Forge 자체 변경을 가정한 Codex·Claude Code pressure test에서 각 에이전트가 동일한 `.agent-runbooks/maintaining-forge/README.md`를 정본으로 선택하고 validation 및 release gate를 건너뛰지 않는다.
- AC8 (R1, R6, R8): Forge 플러그인의 배포 파일 목록과 README를 검토하면 사용자 실행 스킬과 저장소 유지보수 절차의 경계가 일치하고, 설치 사용자에게 repository-only 스킬이 노출되지 않는다.

## Decisions & History

- 2026-07-12 [DECISION] Forge는 사용자 실행용 플러그인으로 한정하고, Forge 자체 개선 절차는 저장소 전용으로 분리한다.
- 2026-07-12 [DECISION] Codex와 Claude Code가 같은 절차를 사용하도록 `.agent-runbooks/`를 공용 정본으로 채택한다.
- 2026-07-12 [DECISION] `.agents/skills/`와 `.claude/skills/`에는 공용 런북을 연결하는 얇은 `maintaining-forge` wrapper만 둔다.
- 2026-07-12 [DECISION] 공용 런북과 얇은 에이전트별 wrapper의 구조는 sibling repository `weppy-roblox-mcp-private`의 검증된 패턴을 따른다.
- 2026-07-12 [CHANGE] 기존 Forge 설계의 13번째 배포 스킬 `maintaining-forge`를 사용자 플러그인에서 제거하고 repository-only runbook으로 재분류한다.
- 2026-07-12 [DECISION] 사용자가 본 스펙을 승인하여 구현 계획 수립을 시작한다.
