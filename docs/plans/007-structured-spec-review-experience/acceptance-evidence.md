# Structured Spec Cutover Acceptance Evidence

이 문서는 Task 8 migration cutover와 Task 9 release evidence를 같은 고정 schema로 누적한다. Task 8에서는 production root를 변경하지 않은 disposable overlay 결과만 기록하며, `cutoverCommit`은 아직 `null`이다.

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

Task 9가 `Spec | AC | Task | Evidence type | Command or artifact | Result | Checked at UTC | Commit` schema로 008 AC1–AC12와 002 AC1–AC31의 stable cutover commit evidence를 보완한다.
