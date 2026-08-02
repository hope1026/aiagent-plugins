# Spec Supersession Acceptance Evidence

이 문서는 `008-structured-spec-pages`의 current-state supersession delta와 기존 Spec Pages 계약을 release candidate에서 fresh하게 재검증한 결과다.

## Candidate

- Verification base: `017e9eff4d12f247eec88ce6dbea9707a6ab24c5`
- Upstream base: `9f10cae0246fae666f73b57039f99c0c15a28b66`
- Claude version: `0.1.7`
- Codex version: `0.1.7+codex.20260802062451`
- Checked at UTC: `2026-08-02T06:29:44Z`
- Repository Review Viewer output: 0 files
- Target repository mutations: 0; `weppy-roblox-mcp-private` cutover remains a separate release-dependent plan

## Fresh command evidence

| Gate | Command | Result |
|---|---|---|
| Structured parser, validator, renderer and CLI | `python3 -m unittest discover -s plugins/forge/skills/writing-specs/tests -p 'test_*.py' -q` | PASS, 74 tests |
| Mermaid and Spec Pages runtime | `test_mermaid_validate.mjs`; `test_spec_pages_runtime.mjs` | PASS |
| Review Viewer shared-consumer integration | `test_review_sources.py -q`; `test_review_renderer.py -q`; freshness/build suites | PASS, 13 + 20 tests and both Node/shell gates |
| Supersession policy and isolation | `test-forge-spec-docs-policy.sh`; `test-forge-spec-supersession.sh` | PASS, seven registered worktree cases |
| Installed export parity | `test-forge-review-viewer-install.sh` | PASS for Claude Code, Codex and Antigravity, including transition parser hash parity |
| Repository policies | CI-equivalent shell policy sequence | PASS |
| Full repository validator | `bash scripts/validate.sh` | PASS, final line `validate: all checks passed` |
| Spec Pages deterministic build | full offline `build`; `check` | PASS, 8 pages plus catalog |
| Spec Pages browser | `run-spec-pages-browser.sh` | PASS, desktop/mobile 6/6 |
| Review Viewer browser regression | `run-review-viewer-browser.sh` | PASS, desktop/mobile 6/6 |
| Behavioral pressure test | deadline + inferred approval + replay + changed-only build + Viewer assumption scenario | PASS, unsafe shortcuts refused, P0/P1 0 |

전체 통합 검증의 첫 실행은 Review Viewer의 isolated-layout fixture가 새 sibling `spec_transitions.py`를 복사하지 않아 3건 실패했다. 해당 소비자 fixture를 수정하고 정확한 13-test reproduction과 위 전체 sequence를 다시 실행해 최종 실패 0을 확인했다.

## Acceptance walk

| AC | Verdict | Evidence |
|---|---|---|
| AC1 | PASS | 74-test writing-specs suite가 canonical frontmatter, sections, IDs, coverage와 relation contract를 검증했다. |
| AC2 | PASS | invalid matrix와 baseline validator suite가 정렬된 diagnostics와 non-zero 차단을 검증했고 repository validation이 통과했다. |
| AC3 | PASS | policy gate와 shared parser consumer tests가 lifecycle status를 frontmatter parser에서 읽는 것을 확인했다. |
| AC4 | PASS | renderer transaction tests, full build/check와 browser 6/6이 source/page/catalog 동시 freshness를 검증했다. |
| AC5 | PASS | renderer·CLI supersession regression이 build 전 orphan/missing/stale 실패, full build 후 성공, second-build diff 0을 확인했다. |
| AC6 | PASS | runtime tests와 desktop/mobile browser가 한국어 navigation, identifier·Mermaid fidelity와 read-only output을 검증했다. |
| AC7 | PASS | runtime/browser catalog matrix가 status, kind, area, component, relation filter와 navigation을 검증했다. |
| AC8 | PASS | pinned browser harness가 desktop·390px, keyboard, overflow, offline과 Mermaid failure state를 6/6 통과했다. |
| AC9 | PASS | lifecycle/artifact policy와 repository scan이 명시 요청 없는 Review Viewer 생성·갱신 0을 확인했다. |
| AC10 | PASS | repository validation과 source scan에서 structured active spec 8개, legacy body `Status:`와 production compatibility branch 0을 확인했다. |
| AC11 | PASS | 기존 `007` migration evidence와 `migration-map.json`, artifact/lifecycle gates가 atomic cutover와 sibling isolation을 보존한다. 이번 Forge diff의 target mutation은 0이다. |
| AC12 | PASS | isolated install fixture가 세 export에서 parser, validator, builder, template, offline assets와 transition parser의 동일 결과를 확인했다. |
| AC13 | PASS | 13 transition parser tests와 valid implemented→approved fixture가 exact JSON/key/type/SHA/path/symlink/evidence 계약을 검증했다. |
| AC14 | PASS | validator·renderer·CLI tests가 binding, baseline target, draft/missing target, prefix/replay, duplicate, same-diff chain, historical old identity, later-diff chain과 page cutover를 검증했다. |
| AC15 | PASS | executable pressure fixture가 deletion/SHA/reference/build/check 실패와 late root drift에서 HEAD/index/tracked/untracked bytes를 보존하고 success candidate만 fast-forward했으며 Viewer count는 0이었다. |

## Traceability

- `docs/plans/008-spec-supersession/plan.md`의 AC Coverage는 이번 delta AC2, AC5, AC9, AC12–AC15를 Tasks 1–5에 연결한다.
- 기존 AC1–AC12의 구현 provenance는 `docs/plans/007-structured-spec-review-experience/acceptance-evidence.md`에 보존되어 있으며, 이번 candidate에서 모두 fresh하게 재실행했다.
- Task 1–5는 각 route의 tier, mode, parallel group, root review, verification과 commit 범위를 plan `Progress History`에 기록한다.
