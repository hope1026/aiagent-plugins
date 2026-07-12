---
name: spec-viewer
description: 'Use when a spec or implementation plan needs a self-contained HTML review view with diagrams, tables, traceability, or an acceptance checklist, or when a user asks to visualize a spec or plan. Triggers: "스펙 시각화", "스펙 보여줘", "계획 시각화", "spec html", "plan viewer", "스펙 뷰어", "다이어그램으로", reviewing a spec or plan with a human.'
---

# Spec Viewer

Announce at start: "Using the forge spec-viewer skill to render source documents as a lifecycle review Viewer."

Respond to the user in the user's language. This skill file stays in English. Viewer prose follows the primary source language; preserve proper nouns, API, service, schema, protocol, and code identifiers in their established language.

## Overview

Assembly, not invention. This skill combines a fixed HTML shell, a source-owned six-panel content fragment, and source metadata into `spec`, `plan`, or `combined` review views. The Markdown sources remain authoritative throughout delivery; generated HTML is read-only and regenerable.

The reading order is deliberate: summary table → visual flow → detailed Task → AC evidence → source. A Viewer helps a person find answers; it never adds decisions that the source does not contain.

## Iron Law

```
THE HTML IS A VIEW, NEVER THE TRUTH.
SOURCE MERMAID STAYS VERBATIM. DERIVED VIEWS ADD NO NEW MEANING.
NO EXPLICIT USER REQUEST, NO BUILD OR REBUILD.
```

## When to Use / When NOT

**Use only after an explicit user request when:**

- The user asks to visualize, present, print, or share a spec or plan.
- The user asks to create or update a `spec`, `plan`, or `combined` Viewer.

**Do NOT use when:**

- The source itself needs writing or changing — use the forge writing-specs or writing-plans skill.
- The user did not make an explicit user request for Viewer creation or update. Complexity, approval, handoff, checkpoint, and an existing stale Viewer do not count as a request.
- Building product UI — use the forge ui-design skill.
- The desired relationship is not present in source — return to the governing source instead of inventing it here.

## Source Ownership and Modes

| Mode | Primary source | Auxiliary source | Output |
|---|---|---|---|
| `spec` | `docs/specs/NNN-<slug>/spec.md` | none | `.forge/viewer/NNN-<slug>.html` |
| `plan` | `.forge/plans/NNN-<slug>.md` | approved spec for R, AC, and approved Mermaid | `.forge/viewer/NNN-<slug>-plan.html` |
| `combined` | approved spec + plan | `.forge/scratch/progress-NNN.md` when present | `.forge/viewer/NNN-<slug>-review.html` |

In `spec` mode, the spec owns all displayed meaning. In `plan` mode, the plan owns Route, Task, Step, file, interface, and verification detail; the spec is supporting evidence only. In `combined` mode, label each field by its source and link the two sources without merging their responsibilities.

## The Process

Create one todo per numbered step before starting.

1. **Choose the mode and read every selected source.** Confirm paths, spec status, primary source language, and whether a progress ledger exists. Record expected Task, Step, R, AC, and Mermaid counts.

2. **Enforce the request gate.** Confirm the user explicitly requested Viewer creation or update for the selected current sources. If not, stop and return to the Markdown review path. Never infer permission from complexity, lifecycle stage, or an existing Viewer.

3. **Author the six-panel fragment.** Read `references/content-patterns.md`, then write `.forge/scratch/NNN-<slug>-content.html`. Keep exactly these panel IDs in order: `overview`, `requirements`, `flows`, `data`, `acceptance`, `history`. The fragment contains no doctype, shell markup, style, or script.

4. **Preserve diagram ownership.** Copy approved spec Mermaid byte-for-byte and label it `Spec source`. Copy plan Mermaid byte-for-byte and label it `Plan source`. Label mechanically calculated Route, dependency, and coverage diagrams `Derived view`; use only explicit Task IDs, Route membership, dependencies, and R·AC mappings.

5. **Package every diagram for people.** Before each diagram provide a question-shaped title, what to confirm, and a one-sentence reading guide. Before a wide sequence diagram provide a runtime responsibility summary table. Keep the original wide diagram in a horizontal scroll region; add a vertical summary before it when mobile text would otherwise be unreadable.

6. **Prepare ignored working directories.** Ensure `.forge/scratch/.gitignore` and `.forge/viewer/.gitignore` each contain exactly `*`. Generated HTML remains uncommitted.

7. **Build with source metadata.** Run the matching command from the project root:

   ```bash
   bash <spec-viewer-skill>/scripts/build-viewer.sh \
     --mode spec --locale ko \
     --spec docs/specs/NNN-<slug>/spec.md \
     -c .forge/scratch/NNN-<slug>-content.html \
     -t "<question-shaped title>" -s "<status>"
   ```

   ```bash
   bash <spec-viewer-skill>/scripts/build-viewer.sh \
     --mode plan --locale ko \
     --spec docs/specs/NNN-<slug>/spec.md \
     --plan .forge/plans/NNN-<slug>.md \
     -c .forge/scratch/NNN-<slug>-content.html \
     -t "<question-shaped title>" -s "<status>"
   ```

   ```bash
   bash <spec-viewer-skill>/scripts/build-viewer.sh \
     --mode combined --locale ko \
     --spec docs/specs/NNN-<slug>/spec.md \
     --plan .forge/plans/NNN-<slug>.md \
     --progress .forge/scratch/progress-NNN.md \
     -c .forge/scratch/NNN-<slug>-content.html \
     -t "<question-shaped title>" -s "<status>" --offline
   ```

   Omit `--progress` when no ledger exists. Omit `--locale ko` only when the primary source language is English. Output names are derived when `-o` is omitted; `-o` remains available for deliberate overrides. `--offline` inlines Mermaid 11 instead of requesting the CDN.

8. **Verify the view.** Confirm six panels, exact counts, source paths and source hash, `current` freshness, unresolved placeholders 0, source Mermaid equality, and fragment shell markup 0. In a real browser verify 1440px and 390px, tabs, Task/R/AC deep links, AC and Step checkbox persistence, independent table and diagram scroll, Mermaid errors, favicon requests, and offline rendering.

9. **Handle later source changes.** Approval, plan edits, execution progress, and checkpoints can make the generated file stale. Report it as stale; repeat this process only after another explicit user request to update the Viewer.

## Diagram Classification

| Label | Allowed content | Prohibited content |
|---|---|---|
| `Spec source` | exact Mermaid text from the governing spec | formatting or semantic edits |
| `Plan source` | exact Mermaid text from the implementation plan | relationships absent from the plan |
| `Derived view` | mechanically calculated Route, Task dependency, and R·AC coverage | new runtime responsibility, transaction order, state transition, or decision |

When a source Mermaid is invalid, show its error summary, available line and column, and original text. Fix the source, lift it again, and rebuild; never repair only the HTML.

## Working Files

| File | Role | Committed? |
|---|---|---|
| `docs/specs/NNN-<slug>/spec.md` | requirement and approval source | yes |
| `.forge/plans/NNN-<slug>.md` | implementation source | yes |
| `.forge/scratch/progress-NNN.md` | checkpoint evidence | no |
| `.forge/scratch/NNN-<slug>-content.html` | six-panel fragment | no |
| `.forge/viewer/NNN-<slug>*.html` | generated review views | no |

## Red Flags

| Excuse | Reality |
|---|---|
| "The HTML is easier to edit than the Markdown." | Editing the derivative creates drift. Change the owning source and rebuild. |
| "The relationship is obvious, so the derived diagram can add it." | Obvious is still unsourced. Add the decision to spec or plan first. |
| "The Mermaid is valid after I cleaned up its wording." | A source diagram must be byte-for-byte identical, not merely equivalent. |
| "The build succeeded, so review is complete." | Assembly does not prove browser rendering, mobile readability, or persistence. |
| "One huge Task graph is more complete." | Group Tasks into 6–10 Routes first so a person can form a mental model. |
| "Mobile can pinch-zoom the sequence diagram." | Provide the responsibility summary first and keep readable horizontal scrolling. |
| "The checkpoint changed only one Task, so I should keep the Viewer current." | The prior view is stale, but freshness does not grant update permission. Report it and wait for an explicit user request. |
| "Committing HTML makes maintenance easier." | The source, manifest, and rebuild command make it maintainable; generated HTML stays disposable. |

## Handoff

**Viewer rebuilt from its current source. If review changes requirements, use the forge writing-specs skill; if an approved spec needs a plan, use the forge writing-plans skill; if the plan is approved, use the forge executing-plans skill.**
