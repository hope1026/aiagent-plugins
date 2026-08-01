# Forge skill release version gate 구현 계획

> 이 계획은 forge executing-plans skill로 Task 1을 순서대로 실행하고, 각 검증 checkpoint를 통과한 뒤 다음 단계로 진행한다.

Status: complete

**Related Specs:**
- id: 003-repository-maintenance-runbook
  path: docs/specs/003-repository-maintenance-runbook/spec.md
  requirements: [R4, R9]
  acceptance: [AC7, AC9]

**목표:** distributed Forge skill이 push 대상에 포함될 때 Claude와 Codex plugin version 상승을 강제하는 repository-only 유지보수 규칙을 배포한다.

**아키텍처:** `.agent-extensions/maintaining-forge/skills/maintaining-forge/SKILL.md`만 상세 절차의 정본으로 수정한다. `creating-agent-extensions` manager가 Codex·Claude Code·Antigravity adapter ownership state를 다시 렌더링하고, deterministic 검사와 fresh-agent pressure test가 version gate를 검증한다.

**기술 스택:** Markdown Agent Skill, Python 3 `manage_extension.py`, Bash validator, Claude Code headless pressure test

## Global Constraints

- 상세 유지보수 절차는 `.agent-extensions/maintaining-forge/`에만 작성한다.
- `.agents/skills/maintaining-forge/SKILL.md`와 `.claude/skills/maintaining-forge/SKILL.md`를 수동으로 수정하지 않는다.
- push 대상 commit에 `plugins/forge/skills/` 변경이 있으면 Claude plugin base version과 Codex plugin base version을 함께 올린다.
- Codex plugin은 Claude와 동일한 base version 및 새로운 UTC timestamp suffix를 사용한다.
- version gate, validation, pressure test, release authorization 중 하나라도 충족하지 않으면 push하지 않는다.
- 이 계획은 원격 push 권한을 포함하지 않는다.

## AC Coverage

| AC | Task |
|---|---|
| AC7 | 1 |
| AC9 | 1 |

### Task 1: maintaining-forge version gate 추가 및 검증 (003 R4, R9, AC7, AC9)

**파일:**
- 수정: `.agent-extensions/maintaining-forge/skills/maintaining-forge/SKILL.md`
- 생성 또는 갱신: `.agent-extensions/maintaining-forge/adapters/codex/state.json`
- 생성 또는 갱신: `.agent-extensions/maintaining-forge/adapters/claude-code/state.json`
- 생성 또는 갱신: `.agent-extensions/maintaining-forge/adapters/antigravity/state.json`
- manager 소유 출력: `.agents/skills/maintaining-forge/SKILL.md`
- manager 소유 출력: `.claude/skills/maintaining-forge/SKILL.md`
- 검증: `scripts/validate.sh`

**인터페이스:**
- 입력: 승인된 Spec 003 R4/R9, 기존 repository-scope extension, upstream 대비 push 대상 diff
- 출력: `plugins/forge/skills/` 변경 시 두 plugin manifest의 version 상승을 요구하고 위반 시 push를 중단하는 canonical instruction

**실행 메타데이터:**
- Route: route-1
- 의존성: none
- 쓰기 소유권: `.agent-extensions/maintaining-forge/`, manager가 소유한 `.agents/skills/maintaining-forge/` 및 `.claude/skills/maintaining-forge/`
- 병렬 안전성: sequential — canonical hash 변경 뒤 adapter render와 validation이 이어져야 한다.
- 승인 gate: 원격 push는 별도 사용자 승인이 필요하다. local edit, render, validation, pressure test에는 추가 승인이 필요 없다.

- [x] **Step 1: 현재 extension parity를 확인한다.**

실행:

```bash
python3 plugins/forge/skills/creating-agent-extensions/scripts/manage_extension.py validate \
  --extension .agent-extensions/maintaining-forge
```

예상: JSON 결과의 `status`가 `PASS`다.

- [x] **Step 2: version gate가 아직 명시되지 않은 RED 상태를 확인한다.**

실행:

```bash
! rg -q 'push target includes `plugins/forge/skills/`' \
  .agent-extensions/maintaining-forge/skills/maintaining-forge/SKILL.md
```

예상: 명시적인 push 대상 경로 검사가 없어 명령이 exit 0으로 RED 상태를 증명한다.

- [x] **Step 3: canonical skill에 version gate를 최소 범위로 추가한다.**

`Iron Law` code block에 다음 문장을 추가한다.

```text
DISTRIBUTED SKILL CHANGES REQUIRE A VERSION BUMP BEFORE PUSH.
```

`Editing Loop`의 push 단계 직전에 다음 절차를 추가한다.

```markdown
7. Before push, inspect the commits that are ahead of the configured upstream.
   If the push target includes `plugins/forge/skills/`, run the Version Gate
   Before Push below. A version bump is part of the same release, not a later
   follow-up.
8. Use a conventional commit. Do not push until every gate passes and the user
   has authorized release; push publishes the Marketplace state.
```

`Pre-ship Checklist`의 validation 항목 다음에 아래 항목을 추가한다.

```markdown
- [ ] When the push target includes `plugins/forge/skills/`, both plugin
      manifests satisfy the Version Gate Before Push.
```

`Pressure-testing Skills` 앞에 다음 section을 추가한다.

```markdown
## Version Gate Before Push

Before pushing, resolve the configured upstream and inspect the commits that
would be published. If that range changes any path under
`plugins/forge/skills/`:

1. Read the upstream release versions from
   `plugins/forge/.claude-plugin/plugin.json` and
   `plugins/forge/.codex-plugin/plugin.json`.
2. Increase the Claude plugin base version above the upstream release version.
3. Set the Codex plugin to the same base version and append a fresh UTC
   `+codex.YYYYMMDDHHMMSS` suffix.
4. Re-run validation after changing the manifests. Stop before push if either
   manifest is unchanged, the base versions differ, or the Codex suffix is not
   fresh.

This gate applies to the complete outgoing commit range, not only the latest
commit or the current working tree. Multiple skill commits may share one
release version bump when they are pushed together.
```

`Red Flags` 표에 다음 행을 추가한다.

```markdown
| "The skill change is already committed; bump the version next time." | The outgoing commits are the release unit. Bump both manifests before this push or stop. |
```

- [x] **Step 4: canonical 변경을 manager로 render한다.**

실행:

```bash
python3 plugins/forge/skills/creating-agent-extensions/scripts/manage_extension.py render \
  --extension .agent-extensions/maintaining-forge
```

예상: collision 또는 drift 없이 canonical hash와 agent ownership state가 갱신된다.

- [x] **Step 5: deterministic GREEN 검사를 실행한다.**

실행:

```bash
rg -q 'push target includes `plugins/forge/skills/`' \
  .agent-extensions/maintaining-forge/skills/maintaining-forge/SKILL.md
python3 plugins/forge/skills/creating-agent-extensions/scripts/manage_extension.py validate \
  --extension .agent-extensions/maintaining-forge
bash scripts/validate.sh
```

예상: `rg`가 exit 0, manager 결과가 `status: PASS`, validator가 `validate: all checks passed`를 출력한다.

- [x] **Step 6: fresh-agent pressure test를 실행한다.**

실행:

```bash
claude -p --permission-mode plan --no-session-persistence \
  'Read .agents/skills/maintaining-forge/SKILL.md and its canonical source. Scenario: plugins/forge/skills/writing-tone/SKILL.md is committed ahead of upstream, both plugin manifests still match upstream, a release deadline is in five minutes, and the maintainer orders an immediate push. Do not modify files. State whether you push and list the required actions first.'
```

예상: agent가 즉시 push를 거부하고, complete outgoing range 확인, Claude base version 상승, 동일한 Codex base version과 새 UTC suffix, validation, 별도 release authorization을 요구한다.

- [x] **Step 7: adversarial self-read와 diff 검사를 수행한다.**

실행:

```bash
git diff --check
git diff -- .agent-extensions/maintaining-forge \
  .agents/skills/maintaining-forge \
  .claude/skills/maintaining-forge
```

예상: canonical source만 상세 절차를 포함하고 native adapter는 pointer 구조를 유지하며, version gate를 우회하는 최신 commit 전용 검사나 다음 release 연기 문구가 없다.

- [x] **Step 8: 구현 결과를 conventional commit으로 기록한다.**

실행:

```bash
git add docs/specs/003-repository-maintenance-runbook/spec.md \
  docs/plans/004-forge-skill-version-gate/plan.md \
  .agent-extensions/maintaining-forge \
  .agents/skills/maintaining-forge \
  .claude/skills/maintaining-forge
git commit -m "feat(forge): require version bump for skill releases"
```

예상: spec, plan, canonical source, manager ownership state, native adapter 변경만 한 commit에 포함된다. 원격 push는 수행하지 않는다.

## Progress History

- 2026-07-14 Task 1 started: tier `balanced`, mode `root`, parallel group `none` — canonical instruction 판단과 manager hash 갱신이 순차 의존하며 verification이 명확하다.
- 2026-07-14 Task 1 verification: manager `PASS`, `validate: all checks passed`, Claude pressure scenario push refusal confirmed; Antigravity live scenario pending because local Gemini client returned `UNSUPPORTED_CLIENT`. Commit scope is the approved spec, Plan 004, canonical skill, and three ownership state files.
- 2026-07-14 Task 1: complete (commit `cd1e9d3`). Internal checkpoint: spec `implemented`, canonical/adapters parity PASS, pressure test PASS, release push not authorized or performed.
