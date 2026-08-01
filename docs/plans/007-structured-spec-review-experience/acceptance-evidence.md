# Structured Spec Cutover Acceptance Evidence

이 문서는 Task 8 migration cutover와 Task 9 release evidence를 같은 고정 schema로 누적한다. Task 9 evidence는 stable cutover commit `749e2d4d5d993f7e74cba385a78491d3b9dd46e9`에서 만든 detached release worktree에서 수집했다.

## Migration Evidence

- Rollback HEAD: `7d807e1d452171b9d27c24a12b1130324270b497`
- Immutable declaration raw SHA-256: `bf53ac0ac383ea7c5188a62cc3a1d526bc27ea0d76203205df3809523573e661`
- Frozen migration map SHA-256 before final report: `cc1e756cef62b73b0c9ca4bbcdd236d06eda576c69b606325dc9a506c1ad3362`
- Structured specs: 8
- Historical plans preserved: 5
- Historical Tasks preserved: 19
- Typed historical rewrite spans: 43
- Rewritten link inventories: 2 (`plain-token` for specs 006/007, `literal-path` for workflow/tests), with explicit historical and delete exclusions
- Generated Spec Pages: 8 per-spec pages and 1 catalog
- Request-only Review Viewer output generated: 0

| Gate | Command or artifact | Result | Checked at UTC |
|---|---|---|---|
| migration verifier unit and CLI fixtures | `python3 .forge/viewer-build/forge-spec-cutover/test_migration_cutover.py -v` | PASS, 8 tests | 2026-08-01T15:28:39Z |
| structured spec validation | `spec-docs.sh --repo-root . validate --root docs/specs` in overlay | PASS | 2026-08-01T15:27:23Z |
| deterministic Spec Pages build | `spec-docs.sh --repo-root . build --root docs/specs --offline` in overlay | PASS, 9 pages | 2026-08-01T15:27:25Z |
| generated source freshness | `spec-docs.sh --repo-root . check --root docs/specs` in overlay | PASS | 2026-08-01T15:27:27Z |
| promoted research byte/provenance artifact contract | `bash scripts/tests/test-forge-artifact-contract.sh` in overlay | PASS | 2026-08-01T15:27:37Z |
| lifecycle policy | `bash scripts/tests/test-forge-lifecycle-policy.sh` in overlay | PASS | 2026-08-01T15:27:37Z |
| complete repository validator | `bash scripts/validate.sh` in overlay | PASS, `validate: all checks passed` | 2026-08-01T15:27:41Z |

## Release Evidence

정적 traceability audit에서 두 spec의 AC 집합, plan의 AC Coverage 행, Task header trace가 exact match임을 확인했다: `008` AC1–AC12와 `002` AC1–AC31, 누락·중복·추가 0개. 아래 표도 동일한 43개 AC를 각각 한 행으로만 기록한다.

Deadline+sunk-cost pressure scenario는 structured spec gate, status와 두 Spec Pages의 동일 transaction, 명시 요청 전 Review Viewer 생성 금지, sibling `weppy-roblox-mcp-private` 제외, 개별 Viewer build 후 browser·layout QA 금지를 모두 유지했다. Request-only Review Viewer repository output은 0개이며, install proof와 browser output은 OS temporary fixture 안에서만 생성·정리했다.

Release version gate는 configured upstream `refs/remotes/origin/main`과 local cutover의 Claude/Codex base `0.1.5` 중 최댓값을 사용했다. 따라서 Claude는 최소 next patch `0.1.6`, Codex는 같은 base와 fresh UTC suffix를 가진 `0.1.6+codex.20260801164150`이다.

| Spec | AC | Task | Evidence type | Command or artifact | Result | Checked at UTC | Commit |
|---|---|---|---|---|---|---|---|
| 008 | AC1 | 1, 2 | unit + source | `python3 -m unittest discover -s plugins/forge/skills/writing-specs/tests -p 'test_*.py' -v` | PASS, 51 tests | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 008 | AC2 | 1, 2 | unit + validation | writing-specs Python suite; `spec-docs.sh validate --root docs/specs --baseline-ref HEAD` | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 008 | AC3 | 2, 7 | policy + inspect | `test-forge-spec-docs-policy.sh`; `spec-docs.sh inspect --spec docs/specs/008-structured-spec-pages/spec.md --format json` | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 008 | AC4 | 3, 4, 7 | unit + browser | writing-specs Python suite; `run-spec-pages-browser.sh` | PASS, browser 6/6 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 008 | AC5 | 3 | unit + freshness | writing-specs Python suite; `spec-docs.sh check --root docs/specs` | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 008 | AC6 | 3, 4 | runtime + browser | `test_spec_pages_runtime.mjs`; `run-spec-pages-browser.sh` | PASS, browser 6/6 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 008 | AC7 | 3, 4 | runtime + browser | `test_spec_pages_runtime.mjs`; `run-spec-pages-browser.sh` | PASS, browser 6/6 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 008 | AC8 | 4 | browser | `run-spec-pages-browser.sh` at desktop and 390px | PASS, 6/6 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 008 | AC9 | 5, 7 | request policy | `test-forge-lifecycle-policy.sh`; `test-forge-artifact-contract.sh` | PASS, repository Viewer HTML 0 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 008 | AC10 | 7, 8 | migration + policy | `test-forge-spec-docs-policy.sh`; `scripts/validate.sh` | PASS, no legacy active source | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 008 | AC11 | 8 | migration artifact | `migration-map.json`; stable cutover `749e2d4`; sibling fingerprint from Task 8 | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 008 | AC12 | 9 | install matrix | `test-forge-review-viewer-install.sh` | PASS, three hashes equal; path/fault/signal rollback | 2026-08-01T16:56:02Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC1 | 5, 7 | request policy | `test-forge-lifecycle-policy.sh`; pressure scenario | PASS, automatic refresh 0 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC2 | 7 | request policy | `test-forge-lifecycle-policy.sh`; pressure scenario | PASS, explicit request required | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC3 | 5 | CLI | `test-build-review-viewer.sh` | PASS, spec/plan modes and combined rejection | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC4 | 5, 6 | unit + source equality | `test_review_sources.py`; `test_review_renderer.py`; `test-build-review-viewer.sh` | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC5 | 5, 6 | scale fixture | Review Viewer Python suites | PASS, Task 22/Step 110 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC6 | 6 | scale fixture | `test_review_renderer.py` route coverage | PASS, 8 routes | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC7 | 6 | provenance unit | Review Viewer Python suites | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC8 | 6 | renderer + browser | `test_review_renderer.py`; `run-review-viewer-browser.sh` | PASS, browser 6/6 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC9 | 6 | responsive browser | `run-review-viewer-browser.sh` at 390px | PASS, 6/6 matrix | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC10 | 6 | accessibility browser | `run-review-viewer-browser.sh` | PASS, favicon and computed-style assertions | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC11 | 6 | browser fault fixture | `run-review-viewer-browser.sh` malformed Mermaid case | PASS, 6/6 matrix | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC12 | 5, 6 | namespace persistence | Review Viewer Python suites; `run-review-viewer-browser.sh` | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC13 | 7 | plan policy | `test-forge-spec-docs-policy.sh`; `test-forge-lifecycle-policy.sh` | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC14 | 5, 6 | renderer policy | `test-forge-artifact-contract.sh`; Review Viewer Python suites | PASS, six panels | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC15 | 5, 7 | lifecycle policy | `test-forge-lifecycle-policy.sh`; pressure scenario | PASS, no per-view post-build QA | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC16 | 6 | offline browser | `run-review-viewer-browser.sh` | PASS, offline external requests 0 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC17 | 6 | renderer + browser | `test_review_renderer.py`; `run-review-viewer-browser.sh` | PASS, six panels | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC18 | 5, 6 | provenance + freshness | Review Viewer Python/Node suites | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC19 | 6, 9 | release browser | pinned Playwright 1.55.0 Spec Pages and Review Viewer harnesses | PASS, 6/6 + 6/6 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC20 | 5, 6 | deterministic renderer | `test_review_renderer.py`; `test-build-review-viewer.sh` | PASS, unresolved placeholders 0 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC21 | 7 | request policy | `test-forge-lifecycle-policy.sh`; pressure scenario | PASS, generated before request 0 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC22 | 5, 7 | request policy | `test-forge-lifecycle-policy.sh`; Review Viewer source tests | PASS, automatic refresh 0 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC23 | 5, 7, 8 | artifact policy | `test-forge-artifact-contract.sh`; `git status --short` | PASS, tracked Review Viewer HTML 0 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC24 | 2, 7 | relation validation | writing-specs Python suite; `test-forge-spec-docs-policy.sh` | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC25 | 7 | lifecycle policy | `test-forge-lifecycle-policy.sh` | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC26 | 6 | HTTP freshness browser | `test-viewer-freshness.mjs`; `run-review-viewer-browser.sh` | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC27 | 6 | file freshness browser | `run-review-viewer-browser.sh` local picker case | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC28 | 6 | aggregate freshness | `test-viewer-freshness.mjs`; Review Viewer Python suites | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC29 | 5, 6 | checker | `test-viewer-freshness.mjs`; `test-build-review-viewer.sh` | PASS, stale did not regenerate | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC30 | 7, 8 | migration artifact | `migration-map.json` durable research/debug dispositions | PASS | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
| 002 | AC31 | 3, 5, 7, 8 | artifact separation | `test-forge-artifact-contract.sh`; `spec-docs.sh check --root docs/specs` | PASS, Viewer build changed Spec Pages 0 | 2026-08-01T16:46:05Z | `749e2d4d5d993f7e74cba385a78491d3b9dd46e9` |
