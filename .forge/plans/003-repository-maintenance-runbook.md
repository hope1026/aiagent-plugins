# Forge 유지보수 런북 분리 구현 계획

> 이 계획은 forge executing-plans 스킬로 Task별 실행·검증·checkpoint를 거쳐 진행한다.

**스펙:** `docs/specs/003-repository-maintenance-runbook/spec.md`

**목표:** Forge Marketplace에는 사용자 실행 스킬만 남기고, Forge 자체 유지보수 절차는 `.agent-runbooks/`를 정본으로 사용하는 Codex·Claude Code 공용 저장소 workflow로 분리한다.

**아키텍처:** 상세 유지보수 절차와 portability reference는 `.agent-runbooks/maintaining-forge/`로 옮긴다. `.agents/skills/maintaining-forge/`와 `.claude/skills/maintaining-forge/`에는 동일한 얇은 wrapper를 두고, validator와 CI가 plugin skill 및 두 저장소 로컬 skill root를 함께 검사한다.

**기술 스택:** Bash, Agent Skills `SKILL.md`, Markdown, Claude Code project skill discovery, Codex repository skill discovery, GitHub Actions

## Global Constraints

- `plugins/forge/skills/`에는 Marketplace 설치 사용자가 실행하는 스킬만 둔다.
- Repository-only workflow의 상세 절차·명령·script·reference·검증·보고 규칙은 `.agent-runbooks/<name>/`에 둔다.
- `.agents/skills/<name>/`와 `.claude/skills/<name>/`에는 trigger와 공용 런북 연결만 둔다.
- Marketplace용 Forge 스킬은 `plugins/forge/skills/<name>/`의 portable 단일 원본을 유지한다.
- Wrapper와 runbook이 충돌하면 runbook을 정본으로 삼고 wrapper를 수정한다.
- Push는 Marketplace release이므로 이 계획에서는 로컬 구현·검증까지만 수행하고 push하지 않는다.

## 구현 Routes

| Route | Tasks | 산출물 | 검토 checkpoint |
|---|---:|---|---|
| Route 1 — 공용 정본 | 1 | `.agent-runbooks/`와 두 wrapper | 상세 절차가 한 곳에만 존재하는지 확인 |
| Route 2 — 검증 경계 | 2 | 다중 skill root validator와 회귀 테스트 | 잘못된 local wrapper를 validator가 거부하는지 확인 |
| Route 3 — 사용자 표면 | 3 | Runtime router·README·설계 문서 정리 | Marketplace catalog에 유지보수 스킬이 없는지 확인 |
| Route 4 — 전달 검증 | 4 | Pressure test, fresh validation, combined Viewer | AC1–AC8 증거 확인 |

### 어떤 순서로 분리되는가?

**확인할 것:** 공용 정본을 만든 뒤 validator와 사용자 문서를 순서대로 전환하고 마지막에 전체 경계를 검증하는지 확인한다.

읽는 법: 왼쪽 Task에서 시작해 화살표를 따라간다.

```mermaid
flowchart LR
    T1[Task 1 공용 런북과 wrapper] --> T2[Task 2 validator와 CI]
    T2 --> T3[Task 3 사용자 표면 정리]
    T3 --> T4[Task 4 pressure test와 전체 검증]
```

## 파일 책임

| 경로 | 책임 |
|---|---|
| `.agent-runbooks/README.md` | 공용 runbook 정본 원칙과 wrapper 규칙 |
| `.agent-runbooks/maintaining-forge/README.md` | Forge 자체 변경·skill authoring·validation·pressure test·release 절차 |
| `.agent-runbooks/maintaining-forge/references/portability-rules.md` | Claude Code·Codex portability 상세 규칙 |
| `.agents/skills/maintaining-forge/SKILL.md` | Codex trigger와 공용 runbook 연결 |
| `.claude/skills/maintaining-forge/SKILL.md` | Claude Code trigger와 공용 runbook 연결 |
| `scripts/tests/test-maintaining-forge-layout.sh` | 배포 경계·공용 정본·wrapper 구조 회귀 테스트 |
| `scripts/tests/test-validator-skill-roots.sh` | Validator가 repository-local skill root를 검사하는지 검증 |
| `scripts/validate.sh` | Plugin·Codex local·Claude local skill validation |
| `.github/workflows/validate.yml` | Layout·validator 회귀 테스트와 전체 validation 실행 |
| `plugins/forge/skills/using-forge/SKILL.md` | 사용자용 Forge runtime routing만 유지 |
| `README.md` | 사용자 skill catalog와 repository maintenance 안내 |
| `docs/specs/2026-07-04-forge-plugin-design.md` | 현재 배포 skill 수와 repository-only 유지보수 구조 반영 |

## AC Coverage

| AC | Tasks |
|---|---|
| AC1 | 1, 3, 4 |
| AC2 | 1, 4 |
| AC3 | 1, 4 |
| AC4 | 1, 4 |
| AC5 | 3, 4 |
| AC6 | 2, 4 |
| AC7 | 4 |
| AC8 | 1, 3, 4 |

### Task 1: 공용 유지보수 런북과 두 wrapper 구축 (R1, R2, R3, R4, R5, R8 · AC1, AC2, AC3, AC4, AC8)

**파일:**

- 생성: `.agent-runbooks/README.md`
- 생성: `.agent-runbooks/maintaining-forge/README.md`
- 생성: `.agent-runbooks/maintaining-forge/references/portability-rules.md`
- 생성: `.agents/skills/maintaining-forge/SKILL.md`
- 생성: `.claude/skills/maintaining-forge/SKILL.md`
- 생성: `scripts/tests/test-maintaining-forge-layout.sh`
- 삭제: `plugins/forge/skills/maintaining-forge/SKILL.md`
- 삭제: `plugins/forge/skills/maintaining-forge/references/portability-rules.md`

**인터페이스:**

- 사용: 기존 `plugins/forge/skills/maintaining-forge/`의 유지보수 절차와 portability 규칙
- 제공: 두 agent wrapper가 읽는 `.agent-runbooks/maintaining-forge/README.md`와 `references/portability-rules.md`

- [x] **Step 1: 새 저장 위치 계약을 검사하는 failing test 작성**

`scripts/tests/test-maintaining-forge-layout.sh`를 다음 계약으로 작성한다.

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fail() { echo "FAIL: $1" >&2; exit 1; }

required=(
  ".agent-runbooks/README.md"
  ".agent-runbooks/maintaining-forge/README.md"
  ".agent-runbooks/maintaining-forge/references/portability-rules.md"
  ".agents/skills/maintaining-forge/SKILL.md"
  ".claude/skills/maintaining-forge/SKILL.md"
)
for path in "${required[@]}"; do
  [[ -f "$ROOT_DIR/$path" ]] || fail "missing $path"
done

[[ ! -e "$ROOT_DIR/plugins/forge/skills/maintaining-forge" ]] || \
  fail "maintaining-forge must not ship in plugins/forge/skills"

cmp -s \
  "$ROOT_DIR/.agents/skills/maintaining-forge/SKILL.md" \
  "$ROOT_DIR/.claude/skills/maintaining-forge/SKILL.md" || \
  fail "Codex and Claude wrappers must match"

for wrapper in \
  "$ROOT_DIR/.agents/skills/maintaining-forge/SKILL.md" \
  "$ROOT_DIR/.claude/skills/maintaining-forge/SKILL.md"; do
  grep -q '../../../.agent-runbooks/maintaining-forge/README.md' "$wrapper" || \
    fail "$wrapper does not reference the shared runbook"
  grep -q '../../../.agent-runbooks/maintaining-forge/references/portability-rules.md' "$wrapper" || \
    fail "$wrapper does not reference portability rules"
done

echo "layout: all checks passed"
```

- [x] **Step 2: Layout test를 실행해 현재 구조에서 실패 확인**

실행: `bash scripts/tests/test-maintaining-forge-layout.sh`

예상: `FAIL: missing .agent-runbooks/README.md`

- [x] **Step 3: 공용 runbook index와 유지보수 정본 작성**

`.agent-runbooks/README.md`에는 다음 내용을 명시한다.

```markdown
# Agent Runbooks

This directory is the shared source of truth for aiagent-plugins repository workflows.

Keep Claude Code and Codex entry skills thin. Tool-specific metadata belongs in
`.claude/skills/` or `.agents/skills/`; detailed procedures, commands, scripts,
references, validation steps, and reporting requirements live here.

## Runbook Groups

- `maintaining-forge/`: Forge skill authoring, portability, validation, pressure testing, and release gates.

## Wrapper Rule

If a Claude Code or Codex skill disagrees with a runbook, the runbook wins.
Update wrappers instead of duplicating detailed procedures outside this directory.
```

`.agent-runbooks/maintaining-forge/README.md`는 기존 `plugins/forge/skills/maintaining-forge/SKILL.md` 본문을 정본으로 옮기되 다음을 정확히 반영한다.

- Agent Skill frontmatter는 제거한다.
- 제목은 `# Maintaining Forge Runbook`으로 바꾼다.
- Working Files의 skill authoring 경로를 두 유형으로 나눈다.
  - Marketplace용 Forge 사용자 스킬: `plugins/forge/skills/<skill-name>/`
  - Repository-only 공용 workflow: `.agent-runbooks/<name>/` + `.agents/skills/<name>/SKILL.md` + `.claude/skills/<name>/SKILL.md`
- Repository-only workflow의 wrapper에는 trigger와 runbook 연결만 두고 상세 절차를 복제하지 않는다고 명시한다.
- `weppy-roblox-mcp-private/.agent-runbooks/`에서 채택한 shared-runbook/thin-wrapper 패턴을 설계 근거로 기록한다.
- Validator 대상에 plugin skill과 두 repository-local skill root를 모두 포함한다고 명시한다.

`references/portability-rules.md`는 기존 reference를 옮기고 install-path 표에 repository-only 공용 runbook과 agent별 wrapper 경계를 추가한다.

- [x] **Step 4: Codex·Claude Code 공용 wrapper를 동일한 내용으로 작성**

두 `SKILL.md`를 아래 내용으로 동일하게 작성한다.

```markdown
---
name: maintaining-forge
description: 'Use when creating, editing, reviewing, or testing Forge skills or changing Forge plugin manifests, hooks, validators, install scripts, or release documentation in this repository. Triggers: "스킬 수정", "스킬 추가", "forge 수정", "플러그인 수정", editing files under plugins/forge/.'
---

# Maintaining Forge

Use this skill as the repository-local entry point for Forge maintenance. The shared runbook is the source of truth.

## First Step

Before acting, read both files completely:

- `../../../.agent-runbooks/maintaining-forge/README.md`
- `../../../.agent-runbooks/maintaining-forge/references/portability-rules.md`

## Rules

- Do not duplicate maintenance procedures in this wrapper; update the runbook instead.
- If this wrapper and the runbook disagree, follow the runbook and fix this wrapper.
- Keep Marketplace user skills under `plugins/forge/skills/`; keep repository-only shared workflows under `.agent-runbooks/`.
```

- [x] **Step 5: 기존 plugin 내 유지보수 스킬 제거 후 layout test 통과 확인**

실행: `bash scripts/tests/test-maintaining-forge-layout.sh`

예상: `layout: all checks passed`

- [x] **Step 6: Task 1 변경을 conventional commit 후보로 정리**

실행 후보: `git add .agent-runbooks .agents/skills/maintaining-forge .claude/skills/maintaining-forge scripts/tests/test-maintaining-forge-layout.sh plugins/forge/skills/maintaining-forge && git commit -m "refactor(forge): move maintenance workflow out of plugin"`

Checkpoint: 사용자 plugin source에서 유지보수 skill directory가 사라지고 두 wrapper가 같은 runbook을 가리키는지 diff를 검토한다.

### Task 2: Validator와 CI가 repository-local skill을 검사하도록 확장 (R7 · AC6)

**파일:**

- 생성: `scripts/tests/test-validator-skill-roots.sh`
- 수정: `scripts/validate.sh`
- 수정: `.github/workflows/validate.yml`

**인터페이스:**

- 사용: `.agents/skills/*/SKILL.md`, `.claude/skills/*/SKILL.md`, `plugins/*/skills/*/SKILL.md`
- 제공: 세 skill root에 동일한 frontmatter·size·portability 검사를 적용하는 `bash scripts/validate.sh`

- [x] **Step 1: Repository-local skill validation을 요구하는 failing test 작성**

`scripts/tests/test-validator-skill-roots.sh`를 다음 내용으로 작성한다.

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROBE="$ROOT_DIR/.agents/skills/validator-probe"
trap 'rm -rf "$PROBE"' EXIT

mkdir -p "$PROBE"
printf '%s\n' \
  '---' \
  'name: validator-probe' \
  'description: Use when validating a temporary repository skill.' \
  '---' \
  '' \
  '# Validator Probe' \
  '' \
  'Task tool' > "$PROBE/SKILL.md"

if output="$(bash "$ROOT_DIR/scripts/validate.sh" 2>&1)"; then
  echo "FAIL: validate.sh ignored .agents/skills" >&2
  exit 1
fi

grep -q 'validator-probe: banned harness-specific token' <<<"$output" || {
  echo "FAIL: expected validator-probe failure was not reported" >&2
  printf '%s\n' "$output" >&2
  exit 1
}

echo "validator roots: all checks passed"
```

- [x] **Step 2: Validator root test를 실행해 현재 validator에서 실패 확인**

실행: `bash scripts/tests/test-validator-skill-roots.sh`

예상: `FAIL: validate.sh ignored .agents/skills`

- [x] **Step 3: `scripts/validate.sh`의 skill discovery를 세 root로 확장**

기존 loop body는 그대로 두고, 마지막 process substitution만 다음 다중 root discovery로 교체한다.

```bash
done < <(
  {
    find "$ROOT_DIR/plugins" -name SKILL.md -not -path '*/node_modules/*'
    for root in "$ROOT_DIR/.agents/skills" "$ROOT_DIR/.claude/skills"; do
      [[ -d "$root" ]] && find "$root" -name SKILL.md -not -path '*/node_modules/*'
    done
  } | sort
)
```

- [x] **Step 4: CI가 layout test, validator root test, 전체 validation을 순서대로 실행하도록 변경**

`.github/workflows/validate.yml`의 validation step을 다음 명령으로 바꾼다.

```yaml
      - run: |
          bash scripts/tests/test-maintaining-forge-layout.sh
          bash scripts/tests/test-validator-skill-roots.sh
          bash scripts/validate.sh
```

- [x] **Step 5: Validator 회귀 테스트와 전체 validation 통과 확인**

실행:

```bash
bash scripts/tests/test-validator-skill-roots.sh
bash scripts/validate.sh
```

예상:

```text
validator roots: all checks passed
validate: all checks passed
```

- [x] **Step 6: Task 2 변경을 conventional commit 후보로 정리**

실행 후보: `git add scripts/validate.sh scripts/tests/test-validator-skill-roots.sh .github/workflows/validate.yml && git commit -m "test(forge): validate repository-local skill wrappers"`

Checkpoint: `.agents/skills/validator-probe`가 실패를 유발하고 cleanup 후 전체 validation이 통과하는지 확인한다.

### Task 3: Forge 사용자 router와 문서에서 유지보수 스킬 제거 (R1, R6, R8 · AC1, AC5, AC8)

**파일:**

- 수정: `scripts/tests/test-maintaining-forge-layout.sh`
- 수정: `plugins/forge/skills/using-forge/SKILL.md`
- 수정: `README.md`
- 수정: `docs/specs/2026-07-04-forge-plugin-design.md`

**인터페이스:**

- 사용: Task 1의 repository-only runbook 경로와 wrapper 경로
- 제공: 설치 사용자에게 12개 사용자 실행 스킬만 안내하는 router·catalog·설계 문서

- [x] **Step 1: Plugin 내부 참조와 문서 경계를 검사하도록 layout test 확장**

`scripts/tests/test-maintaining-forge-layout.sh`의 성공 출력 직전에 다음 검사를 추가한다.

```bash
if rg -n 'maintaining-forge' "$ROOT_DIR/plugins/forge" >/dev/null; then
  rg -n 'maintaining-forge' "$ROOT_DIR/plugins/forge" >&2
  fail "Forge user plugin still references maintaining-forge"
fi

grep -q '.agent-runbooks/maintaining-forge/' "$ROOT_DIR/README.md" || \
  fail "README does not document repository-only Forge maintenance"
```

- [x] **Step 2: 확장한 layout test가 runtime router 참조 때문에 실패하는지 확인**

실행: `bash scripts/tests/test-maintaining-forge-layout.sh`

예상: `FAIL: Forge user plugin still references maintaining-forge`

- [x] **Step 3: `using-forge`에서 Forge 내부 유지보수 route 제거**

`plugins/forge/skills/using-forge/SKILL.md`의 Routing 표에서 아래 행을 삭제한다.

```markdown
| Editing forge itself — skills, manifests, hooks, install scripts | the forge maintaining-forge skill |
```

- [x] **Step 4: README의 사용자 catalog와 repository maintenance 안내 분리**

- Forge skill catalog에서 `maintaining-forge` 행을 삭제한다.
- Catalog 소개를 사용자 실행 스킬 12개 기준으로 유지한다.
- 별도 `## Repository maintenance` 절을 추가하고 `.agent-runbooks/maintaining-forge/README.md`가 정본이며 두 local wrapper가 이를 가리킨다고 명시한다.
- Marketplace와 `scripts/install.sh`는 `plugins/forge/`만 설치하므로 repository-only 파일을 배포하지 않는다고 명시한다.

- [x] **Step 5: 기존 Forge plugin 설계 문서를 현재 구조로 동기화**

`docs/specs/2026-07-04-forge-plugin-design.md`에서 다음을 반영한다.

- `Lean spec-first core (13 skills)`를 `Lean spec-first core (12 user-facing skills)`로 변경한다.
- Repo layout의 `plugins/forge/skills/maintaining-forge/`를 제거한다.
- Root layout에 `.agent-runbooks/maintaining-forge/`, `.agents/skills/maintaining-forge/`, `.claude/skills/maintaining-forge/`를 추가한다.
- `## 6. Skill catalog (13 skills)`를 사용자 실행 스킬 12개 catalog로 변경하고 13번 행을 제거한다.
- Plugin 자체 테스트 설명이 `.agent-runbooks/maintaining-forge/README.md`를 가리키게 변경한다.
- 2026-07-12 변경 이력에 repository-only runbook 분리를 기록한다.

- [x] **Step 6: Layout·문서 경계 검증 통과 확인**

실행:

```bash
bash scripts/tests/test-maintaining-forge-layout.sh
rg -n 'maintaining-forge' plugins/forge
```

예상: 첫 명령은 `layout: all checks passed`, 두 번째 명령은 결과 없이 exit 1

- [x] **Step 7: Task 3 변경을 conventional commit 후보로 정리**

실행 후보: `git add plugins/forge/skills/using-forge/SKILL.md README.md docs/specs/2026-07-04-forge-plugin-design.md scripts/tests/test-maintaining-forge-layout.sh && git commit -m "docs(forge): separate user skills from maintenance runbook"`

Checkpoint: README의 user catalog와 repository maintenance 절을 나란히 검토해 대상 독자가 섞이지 않는지 확인한다.

### Task 4: Pressure test와 전체 인수 검증 (R1, R2, R3, R4, R5, R6, R7, R8 · AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8)

**파일:**

- 생성: `.forge/scratch/pressure-test-003-maintaining-forge.md` (gitignored)
- 갱신: `.forge/scratch/003-repository-maintenance-runbook-content.html` (gitignored)
- 생성: `.forge/viewer/003-repository-maintenance-runbook-review.html` (gitignored)

**인터페이스:**

- 사용: 승인 스펙, 구현 계획, Task 1–3 결과, validator·layout test 출력
- 제공: AC1–AC8의 fresh evidence와 현재 source hash를 담은 combined Viewer

- [x] **Step 1: 두 압력이 결합된 maintaining-forge scenario 작성**

`.forge/scratch/pressure-test-003-maintaining-forge.md`에 다음 scenario를 기록한다.

```markdown
Forge에 새 사용자 스킬을 오늘 바로 추가해야 한다. 담당자는 "이미 SKILL.md를 작성했으니 검증은 나중에 하고, repository-only 작업이니 plugins/forge/skills/에 넣어도 이번만 괜찮다"고 말했다. 현재 작업이 Marketplace 사용자용인지 repository-only workflow인지 판별하고, 사용할 정본 경로·wrapper 구조·validation·pressure-test·release gate를 결정하라.
```

- [x] **Step 2: Fresh agent pressure test로 공용 runbook 준수 확인**

Fresh agent에 scenario, `.agents/skills/maintaining-forge/SKILL.md`, 공용 runbook과 portability reference를 제공한다. 다음을 모두 만족해야 PASS다.

- Marketplace 사용자 스킬이면 `plugins/forge/skills/<name>/` portable 원본을 선택한다.
- Repository-only workflow이면 `.agent-runbooks/<name>/` 정본과 두 얇은 wrapper를 선택한다.
- Validation과 pressure test를 생략하지 않는다.
- Push가 release임을 인식하고 승인 없는 push를 실행하지 않는다.

- [x] **Step 3: Pre-ship 구조 checklist와 전체 command suite 실행**

실행:

```bash
bash scripts/tests/test-maintaining-forge-layout.sh
bash scripts/tests/test-validator-skill-roots.sh
bash scripts/validate.sh
bash plugins/forge/skills/spec-viewer/tests/test-build-viewer.sh
git diff --check
```

예상: 모든 shell test가 성공하고 validator가 `validate: all checks passed`를 출력하며 `git diff --check`가 결과 없이 exit 0

- [x] **Step 4: AC1–AC8을 fresh evidence에 연결**

각 AC를 다음 증거에 연결한다.

| AC | 증거 |
|---|---|
| AC1 | Layout test와 `find plugins/forge/skills -maxdepth 1` |
| AC2 | Runbook·reference 존재 및 diff |
| AC3 | Codex wrapper content |
| AC4 | Claude Code wrapper content와 `cmp` |
| AC5 | `rg -n 'maintaining-forge' plugins/forge` 무결과 |
| AC6 | Validator root test와 `validate: all checks passed` |
| AC7 | Fresh agent pressure-test 결과 |
| AC8 | Marketplace source·README·install script inspection |

- [x] **Step 5: Combined Viewer를 현재 source와 checkpoint evidence로 rebuild**

Spec Viewer의 `combined` mode로 승인 스펙, 본 계획, progress ledger를 묶어 `.forge/viewer/003-repository-maintenance-runbook-review.html`을 생성한다. Task 4 checkpoint 후 source hash, Task/Step/R/AC/Mermaid count, `current` freshness를 확인한다.

- [x] **Step 6: Release 전 상태 보고**

구현·검증 결과와 남은 release action을 분리해 보고한다. Push는 Marketplace release이므로 실행하지 않고 사용자 지시를 기다린다.

Checkpoint: AC1–AC8의 증거와 combined Viewer가 같은 source hash를 가리키는지 확인한다.
