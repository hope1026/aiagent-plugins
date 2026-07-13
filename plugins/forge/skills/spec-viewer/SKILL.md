---
name: spec-viewer
description: 'Use when a spec or implementation plan needs a self-contained HTML review view with diagrams, tables, traceability, freshness checks, or an acceptance checklist, or when a user asks to visualize a spec or plan. Triggers: "스펙 시각화", "스펙 보여줘", "계획 시각화", "spec html", "plan viewer", "스펙 뷰어", "다이어그램으로", reviewing a spec or plan with a human.'
---

# Spec Viewer

Announce at start: "Using the forge spec-viewer skill to render an independent spec or plan review Viewer."

Respond to the user in the user's language. This skill file stays in English. Viewer prose follows the primary source language; preserve proper nouns, API, service, schema, protocol, and code identifiers in their established language.

## Overview

Assembly, not invention. This skill combines a fixed HTML shell, a source-owned six-panel content fragment, and source metadata into an independent `spec` or `plan` review View. Markdown remains authoritative. A generated `view.html` is read-only, shared beside its source, and reports whether its embedded SHA-256 values match current Markdown.

The reading order is deliberate: summary table → visual flow → source detail → acceptance evidence. A Viewer helps a person find answers; it never adds decisions that the source does not contain.

The generated file is a convenience artifact for human review, not an implementation deliverable. A successful build ends Viewer generation; do not add a separate validation, render, screenshot, or layout-QA phase for that generated file.

## Iron Law

```
THE HTML IS A VIEW, NEVER THE TRUTH.
SOURCE MERMAID STAYS VERBATIM. DERIVED VIEWS ADD NO NEW MEANING.
NO EXPLICIT USER REQUEST, NO BUILD OR REBUILD.
SUCCESSFUL BUILD ENDS GENERATION. NO POST-BUILD VIEWER QA.
```

## When to Use / When NOT

**Use only after an explicit user request when:**

- The user asks to visualize, present, print, or share a spec or plan.
- The user asks to create or update a `spec` or `plan` Viewer.

**Do NOT use when:**

- The source itself needs writing or changing — use the forge writing-specs or writing-plans skill.
- The user did not explicitly request Viewer creation or update. Complexity, approval, handoff, checkpoint, and an existing stale Viewer do not grant permission.
- Building product UI — use the forge ui-design skill.
- A plan links Related Specs and the desired relationship is absent from the plan — keep the link; do not merge spec content into the plan View.

## Source Ownership and Modes

| Mode | Primary source | Auxiliary source | Output |
|---|---|---|---|
| `spec` | `docs/specs/NNN-<slug>/spec.md` | none | `docs/specs/NNN-<slug>/view.html` |
| `plan` | `docs/plans/PPP-<slug>/plan.md` | optional `progress.md`, optional `tasks/*.md` | `docs/plans/PPP-<slug>/view.html` |

Spec and plan identifiers, paths, and lifetimes are independent. Related Specs in a plan remain navigation links; they are not plan Viewer sources. The removed `combined` mode must never be used as a compatibility fallback.

## The Process

Create one todo per numbered step before starting.

1. **Choose one mode and read every selected source.** Confirm paths, primary source language, and optional plan sources. Record expected Task, Step, R, AC, and Mermaid counts for that mode only.

2. **Enforce the request gate.** Confirm the user explicitly requested creation or update for the current sources. Otherwise stop at Markdown review. Never infer permission from complexity, lifecycle stage, or an existing View.

3. **Author the six-panel fragment.** Read `references/content-patterns.md`, then write `.forge/scratch/<source-id>-content.html`. Keep these panel IDs in order: `overview`, `requirements`, `flows`, `data`, `acceptance`, `history`. Add no doctype, shell markup, style, or script.

4. **Preserve diagram ownership.** Copy spec Mermaid byte-for-byte and label it `Spec source`. Copy plan-source Mermaid byte-for-byte and label it `Plan source` with its path. Label mechanically calculated Route, dependency, and coverage diagrams `Derived view`; use only relationships explicit in the selected mode's sources.

5. **Package every diagram for people.** Before each diagram provide a question-shaped title, what to confirm, and a one-sentence reading guide. Before a wide sequence diagram provide a runtime responsibility summary table. Keep wide diagrams in independent horizontal scroll regions and provide a source-derived mobile summary.

6. **Prepare local intermediates.** Keep content fragments and build staging in `.forge/scratch/` or `.forge/viewer-build/`. These directories remain uncommitted. The final `view.html` is committed beside its Markdown source.

7. **Build with source metadata.** Run one matching command from the project root:

   ```bash
   bash <spec-viewer-skill>/scripts/build-viewer.sh \
     --mode spec --locale ko \
     --spec docs/specs/NNN-<slug>/spec.md \
     -c .forge/scratch/NNN-<slug>-content.html \
     -t "<question-shaped title>" -s "<status>" --offline
   ```

   ```bash
   bash <spec-viewer-skill>/scripts/build-viewer.sh \
     --mode plan --locale ko \
     --plan docs/plans/PPP-<slug>/plan.md \
     --progress docs/plans/PPP-<slug>/progress.md \
     --tasks-dir docs/plans/PPP-<slug>/tasks \
     -c .forge/scratch/PPP-<slug>-content.html \
     -t "<question-shaped title>" -s "<status>" --offline
   ```

   Omit `--progress` and `--tasks-dir` when absent. Omit `--locale ko` only when the primary source language is English. Output defaults to `view.html` beside the primary source; `-o` remains available for deliberate overrides. `--offline` inlines Mermaid 11.

8. **Stop after a successful build.** If the build command exits successfully, hand the generated View to the user. Do not run `--check`, open it in a browser, render screenshots, resize viewports, inspect layout, or test tabs, deep links, checkboxes, Mermaid, print, offline behavior, or freshness states. Do not invoke the forge verifying-work skill for the generated file. If the build fails, report the failure instead of presenting the View.

9. **Handle later source changes.** Source edits can make a committed View stale. The View's own read-time freshness UI may report that state; do not manually validate it. Repeat this process only after another explicit user request. Freshness never grants rebuild permission.

## Diagram Classification

| Label | Allowed content | Prohibited content |
|---|---|---|
| `Spec source` | exact Mermaid text from the selected spec | formatting or semantic edits |
| `Plan source` | exact Mermaid text from the selected plan source file | relationships absent from plan sources |
| `Derived view` | mechanically calculated Route, Task dependency, and explicit coverage | new runtime responsibility, transaction order, state transition, or decision |

When source Mermaid is invalid, show its error summary, available line and column, and original text. Fix the Markdown source and rebuild; never repair only the HTML.

## Working Files

| File | Role | Committed? |
|---|---|---|
| `docs/specs/NNN-<slug>/spec.md` | permanent requirement source | yes |
| `docs/specs/NNN-<slug>/view.html` | explicitly requested spec View | yes |
| `docs/plans/PPP-<slug>/plan.md` | work-scoped plan source | yes |
| `docs/plans/PPP-<slug>/progress.md` | optional long progress source | yes |
| `docs/plans/PPP-<slug>/tasks/*.md` | optional independent Task sources | yes |
| `docs/plans/PPP-<slug>/view.html` | explicitly requested plan View | yes |
| `.forge/scratch/*-content.html` | six-panel fragment | no |
| `.forge/viewer-build/` | local build staging | no |

## Red Flags

| Excuse | Reality |
|---|---|
| "The HTML is easier to edit than the Markdown." | Editing the derivative creates drift. Change the owning source and rebuild after an explicit request. |
| "The plan links one spec, so I can merge it into the View." | A link is not source ownership. Plan Views read plan-local sources only. |
| "Combined mode still helps this one plan." | The mode encodes a false 1:1 lifecycle and has been removed. |
| "The Mermaid is valid after I cleaned up its wording." | Source diagrams stay byte-for-byte identical, not merely equivalent. |
| "The build succeeded, so freshness is current." | Build-time hash capture is not read-time verification. The initial state is `unverified`. |
| "A fetch error probably means the file is unchanged." | An unreadable source is `unverified`, never `current`. |
| "The checkpoint changed only one Task, so I should refresh the View." | Staleness does not grant update permission. Report it and wait for an explicit request. |
| "Committing HTML makes it the source of truth." | Sharing a derived View does not transfer ownership away from Markdown. |
| "I should verify the generated layout before handoff." | The fixed shell is not re-qualified for every generated document. Build success ends generation; the user reviews the convenience View. |
| "A second `--check` is cheap insurance." | Per-artifact verification is intentionally out of scope. Reserve validation for changes to the Viewer builder, template, or scripts. |

## Handoff

**Viewer rebuilt from its current independent source set. If review changes requirements, use the forge writing-specs skill; if it changes execution detail, use the forge writing-plans skill; if the plan is ready, use the forge executing-plans skill.**
