# 구조화 Spec Pages와 요청형 Review Viewer 실행 기록

이 문서는 `plan.md`의 Task별 route, red→green 검증, commit evidence를 누적한다. Review Viewer HTML은 사용자가 명시적으로 요청할 때만 생성하며 이 실행 기록 갱신 자체로 생성하지 않는다.

## Route ledger

| Task | Route | 근거 | 상태 |
|---|---|---|---|
| 1 | subagent, frontier-equivalent | 공통 parser와 vendored Mermaid bundle은 보안·결정성 영향이 크지만 exact interface와 강한 unit test가 있어 경계가 명확함 | completed |
| 2 | same subagent after Task 1 review | Task 1 API에 직접 결합되어 순차 실행이 필요하고 CLI contract test가 명확함 | completed |
| 3 | subagent after Task 2 | Spec Pages renderer는 독립 write ownership과 deterministic fixture가 있음 | completed |
| 4 | root or subagent after Task 3 | 브라우저 UI·접근성·overflow 판단이 필요해 UI system declaration과 visual review가 필요함 | completed |
| 5 | subagent in parallel with Task 3 | `review-viewer` source model은 Spec Pages 파일과 write set이 분리되고 Task 2 parser를 read-only 소비함 | completed |
| 6 | root or subagent after Tasks 3–5 | shared renderer, provenance, browser matrix를 함께 통합해야 함 | completed |
| 7 | root | lifecycle source와 adapter contract가 넓게 결합되고 atomic overlay 준비가 필요함 | completed |
| 8 | root | 기존 source 일괄 migration과 exact rollback coordinator를 소유하는 고위험 cutover임 | completed |
| 9 | root | release version, clean install, evidence, push approval gate를 한 경계에서 판단해야 함 | Steps 1–7 completed; Step 8 pending |

## Plan corrections

- 2026-08-01: Task 5 copy 후 남을 `build-viewer.sh`, `build_viewer.py`, `test-build-viewer.sh`를 exact rename하고 old-path absence를 검증하도록 보정했다.
- 2026-08-01: Task 6이 실제로 수정하는 `scripts/build_review_viewer.py`를 write ownership에 추가했다.
- 2026-08-01: Task 2의 repository/spec root API, Task 3의 pure `render_markdown(text)` API를 고정하고 malformed source 기반 renderer test를 fault injection으로 교체했다.
- 2026-08-01: Task 4에서 처음 생기는 runtime asset drift test를 Task 4로 이동하고 valid source + runtime Mermaid rejection으로 browser fallback을 검증하도록 보정했다.
- 2026-08-01: Task 2 canonical reader는 `approved|implemented`를 허용하되 writer는 새 plan에서 `approved`만 허용하도록 분리하고, repository-aware `inspect`와 baseline source deletion 진단을 추가했다.
- 2026-08-01: Task 5 준비 감사에서 canonical Task `Route`, bilingual direct command/evidence, dependency range·annotation, sibling auxiliary discovery를 source grammar로 고정했다. Historical plan은 heading trace와 직접 metadata block만 migration 예외로 바꾸고 나머지 Task prose·Step bytes를 보존하며, Task 5의 non-dry-run build는 Task 6 renderer 통합 전까지 write 0으로 fail closed한다.
- 2026-08-01: Task 4의 runtime·Mermaid asset drift를 실제 full rebuild fingerprint에 연결하기 위해 `spec_render.py`의 asset read/fingerprint·template placeholder seam만 Task 4 write ownership에 추가했다. Task 3 public API와 transaction semantic은 변경하지 않는다.
- 2026-08-01: Task 5 independent review 결과 auxiliary Mermaid를 source-specific document로 보존하고 outer fence literal을 집계에서 제외하며, selected R·AC duplicate과 primary/auxiliary path alias를 거부하도록 보강했다. Freshness checker는 Task 6 manifest shape, mode별 role cardinality, `.forge/reviews/<review-id>/view.html` 경계를 hash 비교 전에 검증한다.
- 2026-08-01: Task 5 exact-copy inventory의 dormant Mermaid stub 두 경로에 기존 EOF blank line이 있어, copy bytes를 바꾸지 않고 해당 새 경로만 `.gitattributes` whitespace 예외로 제한했다.
- 2026-08-01: Task 1 independent review P1 두 건을 red→green으로 닫았다: canonical clarification prefix와 bundled-package full license notice.
- 2026-08-01: exact-checksum vendor/generated assets 세 파일만 `.gitattributes` whitespace 예외를 적용했고 authored fixture의 EOF whitespace는 제거했다.
- 2026-08-01: Task 7–8 준비 감사에서 spec migration과 artifact-contract assertion의 단계별 소유권을 분리하고, staging metadata allowlist와 `adapterWrites[]` 대 actual-diff `cutoverPaths[]` 경계를 명시했다.
- 2026-08-01: Task 6 독립 감사에서 CLI·browser freshness aggregate 계약 차이가 재현되어, 공유 checker의 `review_freshness.py`를 Task 6 exact write ownership에 추가했다.
- 2026-08-01: Task 6 재감사에서 plan H1을 Goal로 대체하는 오류가 재현되어, source-owned canonical Goal을 typed model에 보존하도록 `review_sources.py`와 해당 test를 Task 6 exact write ownership에 추가했다.
- 2026-08-01: Task 7 immutable baseline 생성 전 감사에서 untracked `plan.md`·`progress.md`가 Task 8 commit과 Task 9 detached worktree에서 누락되는 결함을 찾아, 두 파일을 baseline·declaration·Task 8 apply/stage 경계에 추가했다.
- 2026-08-01: Task 7 baseline 생성 직후 독립 감사에서 declaration action과 overlay final state 불일치, nested Git path의 partial fingerprint 결함을 재현했다. 최초 staging을 폐기하고 helper를 재작성하며, Task 7은 explicit pending action report, Task 8은 pending 0인 final strict report를 강제하는 2-phase contract로 보정했다.
- 2026-08-01: Task 7 lifecycle 감사에서 strict validator 연결과 Task 8-owned 8개 spec migration 사이의 순서 모순을 찾았다. Task 7은 compatibility·skip branch 없이 lifecycle contract PASS와 exact 8개 legacy frontmatter 진단을 pending으로 고정하고, Task 8 atomic migration 후 첫 full root validation PASS를 소유하도록 보정했다.
- 2026-08-01: Review Viewer pressure fixture의 “자동 재생성하라”가 명시 요청이면서 negative gate로 쓰인 모순을 찾았다. Spec/status 변경만 요청하는 negative case와 source·mode·review-id를 명시한 positive case를 분리해 request-only generation을 고정했다.
- 2026-08-01: Task 8 Step 1의 조기 strict report 모순을 수정했다. Task 7 pending report schema/declaration/path set을 먼저 확인하고, 모든 migration action이 끝난 뒤 final strict report를 한 번 생성해 coordinator 직전 pending 0을 강제한다.
- 2026-08-01: Apply와 stage의 유일한 mechanical allowlist를 report actual-diff `cutoverPaths[]`로 고정했다. Migration map은 semantic subset만 소유하고 emit union에 참여하지 않으며 referenced row action/changed state가 report subset인지 검증한다.
- 2026-08-01: Stage/commit gate를 path/action에서 exact content contract로 강화했다. Root overlay state, index blob/mode/delete, commit tree blob/mode/symlink/delete를 report와 비교하고 same-action byte·mode·symlink 변조 fixture를 추가했다.
- 2026-08-01: Historical plan 002–006의 보존을 typed `allowedRewrites[]` span과 baseline/overlay SHA로 검증하도록 보강했다. Header, Task trace, immediate Route/dependency metadata 밖의 Step byte 변경·Task 삭제·reorder는 실패한다.
- 2026-08-01: Immutable target baseline과 별도로 full non-ignored repository transaction snapshot을 추가했다. Validator가 unrelated tracked/untracked bytes·mode를 바꾸거나 새 nonignored file을 만들어도 실패 시 full fingerprint/index를 복원한다.
- 2026-08-01: Apply/restore write 직전 target parent realpath containment을 재확인하고 intermediate symlink escape fixture에서 external inode·bytes·mode 불변을 강제했다.
- 2026-08-01: Final strict report와 apply 사이 mutable command를 제거하고 manifest/declaration/report/HEAD/ref/raw-index/full-fingerprint linkage를 첫 write 전에 재검증한다. Report 뒤 commit, ref switch, non-target mutation은 fail closed한다.
- 2026-08-01: Cutover commit은 hooks를 비활성화한 exact verified index로 만들고 즉시 tree/index/worktree를 재검증한다. Process-owned bad child만 CAS로 START에 되돌리고 full snapshot을 복원하며 concurrent HEAD 변화는 hard stop한다.
- 2026-08-01: Task 8 residual 정정에서 Step 1은 existing pending report·baseline declaration SHA·80-path set만 읽기 전용으로 검증하고 declaration 보완 문구를 제거했다. Step 2는 immutable declaration을 유지한 채 report만 갱신하며, full nonignored rollback snapshot의 exact ignored 위치를 `transaction-baseline/`로 고정했다.

## Task evidence

### Task 1

- Status: completed
- Owner: `/root/spec_schema_audit`
- Constraint: Task 1 exact write ownership only; tests first; no staging or commit by subagent.
- Pre-change baseline: `bash scripts/validate.sh` → `validate: all checks passed`; `git diff --check` → PASS.
- Independent asset check: Mermaid 11.16.0 browser bundle SHA-256 `74d7c46dabca328c2294733910a8aa1ed0c37451776e8d5295da38a2b758fb9b`; license SHA-256 `ec9fb67dcb25eccc416ed56e1aab819222c805a2a4bfe4cb19e7556bf2ffde80`.
- RED: Python `ModuleNotFoundError`; Node bundle `MODULE_NOT_FOUND`; canonical clarification and full-license notice review fixtures also failed before their fixes.
- GREEN: parser suite, real 004/006 Mermaid four-block validation, malformed syntax normalization, two-temp deterministic bundle check, strict four-file checksum, repository validator baseline, staged/unstaged diff checks all PASS.
- Independent review: clarification exact-colon gate and esbuild-metafile bundled license notice P1 closures confirmed; no remaining P0/P1.
- Commit: `a18a9fd feat(forge): parse structured specs`

### Task 2

- Status: completed
- Owner: `/root/spec_schema_audit`
- Constraint: Task 2 exact write ownership only; repository/CLI tests first; no staging or commit by subagent.
- RED: undefined `spec_validate` module, missing CLI wrapper, and executable-mode failure; five independent-review boundary regressions then reproduced four assertion failures plus one symlink escape crash.
- GREEN: 34 Python Task 1–2 tests, real Mermaid Node test, wrapper shell syntax, `scripts/validate.sh`, staged and working-tree diff checks all PASS.
- Independent review: plan/source containment, canonical zero-entry form, legacy baseline usage exit, explicit UTF-8 Mermaid transport, and symlink source escape were all closed; no remaining P0/P1.
- Commit: `0dd1331 feat(forge): validate structured spec repositories`

### Task 3

- Status: completed
- Owner: `/root/viewer_impact_audit`
- Constraint: Task 3 exact writing-specs ownership; no tracked generated HTML; runtime/browser work deferred to Task 4.
- RED: missing `spec_render`, malformed URL crash, unsafe orphan deletion, second-publish partial update, and missing `--changed` success were each reproduced before implementation/fix.
- GREEN: 49 Python Task 1–3 tests, Mermaid Node contract, wrapper syntax, root validator, staged/working diff checks all PASS.
- Independent review: generated-marker containment, multi-file rollback transaction, and existing-source changed gate closed all P1 findings; no remaining P0/P1.
- Commit: `914d9cc feat(forge): build deterministic spec pages`

### Task 5

- Status: completed
- Owner: `/root/migration_inventory`
- Constraint: exact copy/rename with old `spec-viewer` unchanged; source model and dry-run/checker only; Review Viewer HTML generation forbidden until Task 6.
- RED: missing source model produced 12 contract assertions; independent review then reproduced five failures in auxiliary provenance, fenced Mermaid, duplicate selection, path alias, and manifest false-green handling.
- GREEN: source/checker 12 tests, shell contract, Node freshness, shell syntax, root validator, old-skill immutability and mode/path inventory all PASS; generated Viewer HTML 0.
- Independent review: all five P1 closures confirmed with no new P0/P1.
- Commit: `167d0c9 feat(forge): prepare requested review viewer`

### Task 4

- Status: completed
- Owner: `/root/viewer_impact_audit`
- Constraint: declared technical-editorial UI system, offline assets, temp-only browser dependencies and fixture HTML.
- RED: missing runtime exports, absent asset drift, six missing-ready browser cases, filter visibility/tab issues, and lossy space-containing metadata filter were reproduced before fixes.
- GREEN: 51 Python tests, runtime Node contract, four Mermaid checksums, root validator and real Playwright 6/6 at 1440×1000 and 390×844 all PASS; offline external requests 0.
- Independent review: lossless JSON metadata attribute encoding closed the only P1; no remaining P0/P1. One transient remote Chromium ZIP truncation failed, while the identical fresh isolated rerun downloaded successfully and passed 6/6, confirming no repository defect.
- Commit: `5756dcb feat(forge): add offline spec page experience`

### Task 6

- Status: completed
- Owner: `/root/migration_inventory`, independent review by `/root/viewer_impact_audit`
- Constraint: user-request-only output, temp-only browser HTML/dependencies, Spec Pages write 0, warm off-white/graphite/cobalt UI system.
- RED: missing renderer/final build/browser readiness plus independent-review findings in empty context selection, visible History metadata, CLI/browser freshness parity, sequence responsibility, locale copy, canonical Goal, Step coverage, broken internal links, User Experience, Route scope, source checkbox state, bilingual governance and R25 Data sections were reproduced before fixes.
- GREEN: review-viewer Python 33/33, Node freshness, atomic build/check shell E2E, root validator and real Playwright 6/6 at 1440×1000 and 390×844 all PASS; R190/AC105, Task22/Step110/Route8 scale and all internal targets PASS.
- Independent review: final product P0/P1 0; output symlink escape, Spec Pages immutability, source Mermaid equality, source-set freshness, provenance, panel mapping and cache/artifact absence confirmed.
- Note: exact pinned Playwright 1.55.0 temp install reports two test-only high audit findings; version remains plan-pinned and no runtime dependency is shipped.
- Commit: `7d807e1 feat(forge): render provenance-aware review views`

### Task 7

- Status: completed in overlay; production apply/stage/commit remains Task 8-owned.
- Owner: `/root/spec_schema_audit`; root production paths stayed read-only and all lifecycle edits were made under `.forge/viewer-build/forge-spec-cutover/overlay/`.
- Baseline: helper contract 10/10 PASS after nested-root, exact overlay-root, intermediate symlink, immutable baseline, strict-final and explicit-pending regression coverage. Empty production index confirmed; immutable 80-path snapshot and repository fingerprint equality confirmed before the exact overlay copy.
- RED: `test-forge-spec-docs-policy.sh` failed on missing `forge/spec@1`; artifact contract failed on missing Spec Pages; lifecycle policy failed on request semantics; UI routing failed on legacy Viewer ownership.
- GREEN: spec-docs policy, artifact contract, lifecycle policy and UI routing all PASS. The artifact test proved Spec Pages build/check left an existing `.forge/reviews/` sentinel path, SHA-256 and file count unchanged.
- Writer contract: all modes and lifecycle status edits require validate with explicit baseline, changed offline build and repository check; generator/template/runtime/asset edits require full build and check. Any failure blocks approval, handoff and completion reporting.
- Reader contract: new plans require inspect JSON `forge/spec@1` + `approved` + zero diagnostics; execution accepts historical `approved|implemented`; verification writes frontmatter `implemented` only with the same page transaction.
- Request gate: negative existing/stale/complexity/source/status pressure performs Spec Pages sync and zero Review Viewer generation; explicit Review Viewer create/refresh intent permits exactly one `review-viewer` handoff, with source/mode/review-id resolved from current context.
- Schema audit: template and writer use exact `relatedSpecs`, `Data & Interfaces`, JSON string arrays and `feature|system|interface|policy`; the production parser accepts the canonical template-shaped fixture.
- Plan grammar: every related-spec Task uses a source-qualified prefix, including single-spec plans; spec-free plans use the exact one-line form. Inspect gates id/path containment, duplicate ids and listed R/AC existence; progress/task split and plan-deletion promotion use closed gates.
- Adapter evidence: manager render reported canonical hash `6879ac1ea226c6846fba79ebbeb04e08656c0b8eb8f44bc39b028bb2a7dc97e8`; manager validate PASS. Final report must prove exact three state files plus two native entries in `adapterWrites[]`.
- Pending migration: strict current-byte validate exits 1 with exactly eight `SPEC_FRONTMATTER_MISSING` diagnostics. Full `scripts/validate.sh` exits 1 only on the same eight sources in validate and check (16 occurrences); compatibility and conditional skip branches remain absent. Task 8 owns the first full PASS.
- Transaction report: `forge/cutover-report@1`; actual `cutoverPaths[]` 49, `deletedPaths[]` 23, exact `adapterWrites[]` 5, and stable Task 8-owned `pendingPaths[]` 16. No `copy` path is absent.
- Review Viewer HTML generation: 0.

### Task 8 Steps 1–3

- Status: completed in overlay; production apply, stage and commit remain coordinator-owned Steps 4–8.
- Immutable gate: raw declaration SHA-256 `bf53ac0ac383ea7c5188a62cc3a1d526bc27ea0d76203205df3809523573e661`, rollback HEAD `7d807e1d452171b9d27c24a12b1130324270b497`, exact 80-path declaration and baseline/index equality confirmed without baseline refresh.
- Migration map: 8 structured spec entries, 13 artifact dispositions, 5 historical plans, 19 preserved Tasks and 43 typed raw-byte rewrite spans. The scope name is `preserve-and-migrate-header-trace-metadata`; plan 004 records its synthetic single-task `route-1` fallback, and plan 003 Task 3 preserves its dependency wording exactly.
- RED: absent migration verifier, missing split coverage, Step body byte drift, Task sequence mutation, metadata outside the direct Route/dependency span, path escape, legacy requirement order/reference syntax and Mermaid punctuation were each reproduced before correction.
- GREEN: migration verifier fixtures 8/8, cutover baseline helper 13/13, `spec-docs` validate/build/check, lifecycle policy and full `scripts/validate.sh` all PASS in the disposable overlay.
- Generated artifact: 8 per-spec Spec Pages plus one catalog, all source-fresh. Request-only Review Viewer HTML generation remained 0.
- Final report: strict `forge/cutover-report@1`, `pendingPaths[]` 0, actual `cutoverPaths[]` 78, `deletedPaths[]` 25 and exact `adapterWrites[]` 5. Production migration verifier returns `forge/legacy-migration-check@1` with `ok: true` and zero diagnostics.
- Root safety: all production writes remained inside `.forge/viewer-build/forge-spec-cutover/`; root production paths, index, current HEAD and sibling repository stayed outside this Task's write scope.

### Task 8 independent P1 audit

- RED: the verifier accepted duplicate/non-canonical rewritten-link files and did not prove report changed rows or baseline/overlay token states. The production-root-only promoted research assertion also failed before cutover because the new durable path was correctly absent there.
- GREEN: migration verifier tests remain exactly 8/8 and now enforce `plain-token` versus `literal-path`, canonical unique inventories, report `cutoverPaths[]` membership, changed action rows, baseline old-token presence, updated overlay old-token absence/new-token presence, preserved historical tokens and absent delete exclusions.
- Migration map: specs 006/007 plain-token rewrites are separate from workflow/test literal full-path rewrites; historical and delete exclusions are explicit. Frozen map SHA-256 is `cc1e756cef62b73b0c9ca4bbcdd236d06eda576c69b606325dc9a506c1ad3362`.
- Historical promotion: `docs/research/2026-07-04-forge-plugin-design.md` must have immutable baseline SHA-256 `fde1f774ce36fcb29e6daa6956526cc0eeb6f47a5b09c0bbd1d8876d91c92f2e`, preserve its supersession provenance, and leave the old `docs/specs/` path absent.
- Overlay pruning: the legacy `plugins/forge/skills/spec-viewer/` subtree had zero files and symlinks; its six empty directories were removed bottom-up with exact `rmdir`. Production pruning remains coordinator-owned.
- Coordinator command: Task 8 Step 8 now documents all six required `run_cutover.sh` flags explicitly; no coordinator-owned script or transaction helper was modified in this audit.

### Task 8 index-flags baseline restart

- RED: assume-unchanged and skip-worktree flag changes left the old repository fingerprint unchanged, and `--reuse-baseline` incorrectly returned success for both drifts. Four focused assertions reproduced the missing boundary before the helper changed.
- GREEN: the repository fingerprint now includes SHA-256 of raw `git ls-files -v -z` bytes as `indexFlagsSha256`; helper coverage is 13/13 and both flag drifts fail immutable reuse without rewriting the report or baseline.
- Freshness: the prior staging tree was moved recoverably to `/tmp/forge-spec-cutover-indexflags.UYBDXO/forge-spec-cutover`. A new staging tree retained only the corrected helper, its tests and the byte-identical declaration; no old baseline or report was reused.
- Baseline: fresh snapshot schema `forge/cutover-baseline@1`, repository fingerprint schema `forge/repository-fingerprint@1`, exact 80 paths, HEAD `7d807e1d452171b9d27c24a12b1130324270b497`, ref `refs/heads/main`, `indexSha256` `228cbb71845bcd9cb8b9cd3c283975e6f19793ea18b28dfae4c199354509fa8c`, and `indexFlagsSha256` `ca59c100f6ad5f18529506e2b4467226a905705d9f918c1a9899d6b1d0c94980`.
- Replay: a fresh root copy excluding `.git/` and `.forge/` received the prior final report's exact 78 final path states with canonical-path, type, mode, content/symlink and exact-delete checks. The legacy Viewer subtree remained file/symlink-empty and its six empty directories were removed with exact bottom-up `rmdir`.
- Frozen coordinator: `apply_cutover.py`, `emit_pathspec.py`, `verify_index.py`, `run_cutover.sh` and `test_cutover_transaction.py` were restored byte-identically and remain outside this correction's write ownership.
- Review Viewer HTML generation: 0.

### Task 9 Steps 1–7

- Status: completed in detached release worktree; commit, cherry-pick, root verification and push approval gate remain coordinator-owned Step 8.
- RED: the new isolated install test first failed because CI did not invoke it. Independent audit then reproduced three additional failures: the exact macOS `mktemp -d` `/var` path was rejected, a later promotion failure could lose an existing export and leave transaction residue, and `INT`/`TERM` during promotion deleted the backup without rollback.
- GREEN: `test-forge-review-viewer-install.sh` passes the Codex, Claude Code and Antigravity matrix with identical inspect JSON, Spec Page and Review Viewer SHA-256 values. Relative and custom-symlink escapes, read-only targets, staged-copy faults, later-promotion faults and promotion signals fail closed; all existing export sentinels are restored and transaction residue is 0. Trap-visible transaction state makes unexpected EXIT and `INT`/`TERM` roll back before cleanup.
- Compatibility: `--target-root` writes only canonical `codex/`, `claude/` and `antigravity/` children. Without the option, `all` retains existing Codex plus Claude behavior; targetless Antigravity exits with usage status 2.
- CI: non-browser structured spec, Review Viewer, lifecycle, install and root validation run on Ubuntu; browser harnesses run in pinned `mcr.microsoft.com/playwright:v1.55.0-noble`.
- Browser: Spec Pages desktop/mobile 6/6 and Review Viewer desktop/mobile 6/6 PASS. The pinned temporary Playwright dependency continues to report the known two test-only high audit findings and leaves repository artifacts 0.
- Version: configured `refs/remotes/origin/main` and local base maximum `0.1.5` produced Claude `0.1.6` and Codex `0.1.6+codex.20260801164150`.
- Evidence: stable cutover commit `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` is recorded in the migration map. The acceptance table contains exactly 43 schema-valid rows: 008 AC1–AC12 and 002 AC1–AC31. Spec AC sets, AC Coverage rows and Task header traces match exactly.
- Pressure: deadline and sunk cost did not bypass structured validation, the status plus Spec Pages transaction, explicit-only Review Viewer generation, sibling migration exclusion or the no-post-build-QA rule for individual Viewer output.
- Independent review: final P0 0, P1 0. Separate `INT` and unexpected-exit promotion probes preserved all three prior exports, returned their original 130/73 statuses, left transaction residue 0 and emitted no unbound or unsafe-cleanup diagnostics.
- Request-only Review Viewer HTML generated in the repository: 0. Install and browser proof outputs existed only in OS temporary fixtures and were removed.

### Task 8 Steps 4–8

- Status: completed.
- Atomic cutover commit: `749e2d4d5d993f7e74cba385a78491d3b9dd46e9`.
- Coordinator: transaction fixtures 32/32 and build-report fixtures 13/13 PASS before the successful run; final independent security audit P0 0, P1 0.
- Recovery evidence: two pre-commit production attempts exposed ignored tracked-delete staging and Git rename normalization gaps; both attempts restored the full repository fingerprint, index, HEAD and ref exactly before their TDD fixes.
- Final run: strict migration verifier, Spec Pages build/check, artifact zero gates, sibling fingerprint, deterministic second build, exact index/tree verification and hooks-disabled commit all PASS.
- Post-commit: root validator, migration provenance, Spec Pages freshness, commit-tree state, sibling fingerprint and clean working tree/index PASS.

### Task 9 Step 8

- Status: completed at the push approval gate.
- Release payload: exact ten-path allowlist, Claude `0.1.6`, Codex `0.1.6+codex.20260801164150`, migration cutover SHA and 43 AC evidence rows.
- Independent review: installer/CI audit P0 0, P1 0 after macOS lexical target, promotion-fault and `INT`/`TERM` rollback regressions were closed.
- Root handoff contract: only the verified detached release commit is applied to current root; root validation and Spec Pages freshness must pass before the local staging worktree is cleaned up. Push remains explicitly unperformed pending user approval.
