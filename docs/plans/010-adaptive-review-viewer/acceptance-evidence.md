# Adaptive Review Viewer acceptance evidence

검증일: 2026-08-04

## Fresh command evidence

| ID | Command | Result |
|---|---|---|
| E1 | `bash scripts/validate.sh` | PASS — `validate: all checks passed` |
| E2 | `PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_*.py' -v` in `writing-specs` | PASS — 59 tests, 0 failures |
| E3 | `python3 -m unittest discover -s tests -p 'test_*.py' -v` in `review-viewer` | PASS — 29 tests, 0 failures |
| E4 | `node --test tests/test-viewer-freshness.mjs` | PASS — 1 test, 0 failures |
| E5 | `for test_file in scripts/tests/test-forge-*.sh; do bash "$test_file"; done` | PASS — artifact, lifecycle, install, spec-docs, supersession, UI install contracts |
| E6 | `bash plugins/forge/skills/review-viewer/tests/run-review-viewer-browser.sh` | PASS — desktop/mobile 4 tests; adaptive spec, plan, Mermaid fallback, focus/navigation/overflow |
| E7 | `spec-docs.sh inspect` for specs 002 and 008 | PASS — `forge/spec@2`, `approved`, diagnostics 0 before implementation status transition |
| E8 | artifact inventory with `git ls-files`, `find .forge/reviews`, and removed-builder paths | PASS — tracked spec HTML 0, workspace Review Viewer HTML 0, legacy builder files 0 |
| E9 | fresh-agent deadline+sunk-cost+custom-HTML pressure scenario | PASS — automatic HTML, manual HTML, validation bypass rejected |
| E10 | `git diff --name-only origin/main...HEAD -- 'weppy-roblox-mcp-private/**'` | PASS — changed paths 0 |

Browser setup reported two high-severity findings in its isolated temporary npm dependency tree. The harness removed that temporary tree after the run; repository dependency files and release payload were unchanged.

## Spec 002 verdicts

| AC | Verdict | Evidence |
|---|---|---|
| AC1 | PASS | E5, E9 — stale source never authorizes rebuild |
| AC2 | PASS | E5, E9 — Markdown remains the default at every complexity |
| AC3 | PASS | E3, E5 — independent spec/plan modes and invalid mode contract |
| AC4 | PASS | E3, E6 — namespaced comparison provenance and Mermaid hashes |
| AC5 | PASS | E3, E5 — plan auxiliary sources, counts, traceability and deep links |
| AC6 | PASS | E3 — Route membership remains plan-owned |
| AC7 | PASS | E3, E6 — source and derived provenance remain distinct |
| AC8 | PASS | E3, E6 — diagram orientation and responsibility context |
| AC9 | PASS | E6 — 390px overflow remains component-local |
| AC10 | PASS | E3, E6 — accessible diagrams, favicon and tabular numerics |
| AC11 | PASS | E6 — invalid Mermaid falls back without breaking the view |
| AC12 | PASS | E3, E4, E6 — namespaced state persists without collisions |
| AC13 | PASS | E5 — independent plan identity, Routes, traceability and checkpoint policy |
| AC14 | PASS | E3, E5, E9 — adaptive pipeline only; no document-specific HTML |
| AC15 | PASS | E5, E9 — individual build ends after one command; tooling changes receive full verification |
| AC16 | PASS | E3, E6 — CDN and offline Mermaid delivery |
| AC17 | PASS | E3 — execution and status intents compose differently in one shell |
| AC18 | PASS | E3, E4 — manifest metadata and source-level freshness |
| AC19 | PASS | E6 — tooling change verified at desktop and mobile widths |
| AC20 | PASS | E3 — IR, validated plan, manifest and profile HTML contain no unresolved references |
| AC21 | PASS | E5, E9 — no explicit request means no Viewer |
| AC22 | PASS | E5, E9 — plan checkpoint changes do not refresh Viewer |
| AC23 | PASS | E5, E8 — source paths remain tracked; Viewer remains absent and untracked |
| AC24 | PASS | E2, E5 — Related Specs identity, containment and item gates |
| AC25 | PASS | E5 — plan artifact lifetime policy remains enforced |
| AC26 | PASS | E4, E6 — HTTP freshness uses no-store and SHA-256 |
| AC27 | PASS | E4, E6 — file views stay unverified until namespace-specific local selection |
| AC28 | PASS | E4 — primary/context aggregation follows current/stale/unverified rules |
| AC29 | PASS | E4, E5 — read-only checker exit contract; no regeneration |
| AC30 | PASS | E5, E8 — `.forge/` remains untracked and durable records remain under docs |
| AC31 | PASS | E5, E8, E9 — normal lifecycle HTML count is 0 |
| AC32 | PASS | E3, E6 — Mermaid runtime is conditional and deterministic |
| AC33 | PASS | E3 — summary metrics and detail counts agree |
| AC34 | PASS | E3 — provenance grouping preserves role, path, hash and targets |
| AC35 | PASS | E6, E9 — tooling gets browser verification; individual generation does not |
| AC36 | PASS | E3 — every source block has one source-qualified IR record and 100% coverage |
| AC37 | PASS | E3, E6 — intent changes composition while preserving the stable shell |
| AC38 | PASS | E3 — unknown, dangling, authored and uncovered plans are rejected |
| AC39 | PASS | E3, E9 — known profiles and generic fallback remain request-gated |
| AC40 | PASS | E3, E5, E6 — deterministic build and responsive state matrix |

## Spec 008 verdicts

| AC | Verdict | Evidence |
|---|---|---|
| AC1 | PASS | E2 — flexible `forge/spec@2` API, workflow and architecture fixtures |
| AC2 | PASS | E2 — deterministic invalid matrix; HTML count remains 0 |
| AC3 | PASS | E2, E5 — lifecycle consumers use typed frontmatter status |
| AC4 | PASS | E5, E8 — lifecycle mutations produce Markdown only |
| AC5 | PASS | E5, E8, E9 — complexity and stale artifacts never authorize HTML |
| AC6 | PASS | E3, E6 — Korean UI preserves technical identifiers |
| AC7 | PASS | E2, E5 — navigation depends on Markdown paths and relations, not a catalog |
| AC8 | PASS | E3, E4, E8 — requested Viewer is read-only, adaptive and untracked |
| AC9 | PASS | E5, E9 — source validation does not trigger Viewer generation |
| AC10 | PASS | E1, E5, E8 — repository and lifecycle cut over to v2 with tracked HTML 0 |
| AC11 | PASS | E5, E8, E10 — atomic migration/rollback fixture passes; sibling repository changes 0 |
| AC12 | PASS | E5 — three-agent install payload includes parser, IR, planner, components and renderer |
| AC13 | PASS | E2, E5 — exact supersession binding and invalid transition matrix |
| AC14 | PASS | E2, E5 — invalid transitions fail; valid candidate passes without HTML |
| AC15 | PASS | E5, E8 — candidate failure preserves production fingerprint; successful Viewer count 0 |

All 55 acceptance criteria passed with fresh command or browser evidence. No Review Viewer was generated in the repository during this work.
