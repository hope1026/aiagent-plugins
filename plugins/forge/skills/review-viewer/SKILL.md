---
name: review-viewer
description: Use when a user explicitly asks to create, update, visualize, present, print, or share a human-readable Review Viewer for a structured Forge spec or implementation plan, or explicitly asks to check an existing Review Viewer for stale sources. Supports independent spec and plan HTML review snapshots with provenance, traceability, diagrams, and freshness; does not trigger from complexity, lifecycle checkpoints, or source changes alone.
---

# Review Viewer

Announce: "Using the forge review-viewer skill to create the requested spec or plan review snapshot."

Keep Markdown authoritative. Treat `.forge/reviews/<review-id>/view.html` as a read-only, untracked snapshot. Never edit source meaning in HTML and never generate or refresh a Review Viewer without an explicit request for the current source set.

## Entry contract

Follow this order exactly:

1. Confirm that the user explicitly requested creation or refresh. If the user asked only to write a spec, make a plan, continue work, approve a checkpoint, or report stale state, do not build.
2. Select exactly one mode and its source set.
3. Run one build command.
4. Hand off the resulting `.forge/reviews/<review-id>/view.html` and stop.

Use `--check` instead of a build only when the user asks to inspect freshness. A check is read-only and never grants permission to rebuild.

## Source selection

| Mode | Primary set | Non-primary set |
|---|---|---|
| `spec` | one structured `docs/specs/NNN-<slug>/spec.md` | zero or more user-selected comparison specs |
| `plan` | one `plan.md`; existing sibling `progress.md` and lexical `tasks/*.md` by default | the plan's canonical `Related Specs` as context |

Keep source roles distinct. Comparison specs are non-authoritative. Related Specs explain product context but do not become plan-owned requirements. Do not infer relationships missing from the selected Markdown.

Use explicit `--progress` or `--tasks-dir` only to override the plan sibling convention. Reject `combined` mode, manual HTML fragments, `-c/--content`, `-o/--output`, and source-adjacent `view.html` output.

## Build once

Run from anywhere inside the target Git repository. Choose a lowercase `review-id` matching `^[a-z0-9][a-z0-9-]{0,63}$`.

Spec mode:

```bash
bash <review-viewer-skill>/scripts/build-review-viewer.sh \
  --mode spec \
  --spec docs/specs/NNN-<slug>/spec.md \
  --comparison docs/specs/OOO-<slug>/spec.md \
  --review-id <review-id> \
  --locale en
```

Repeat `--comparison` as requested or omit it. Plan mode:

```bash
bash <review-viewer-skill>/scripts/build-review-viewer.sh \
  --mode plan \
  --plan docs/plans/PPP-<slug>/plan.md \
  --review-id <review-id> \
  --locale en \
  --checkpoint working-tree
```

Use `--locale ko` for Korean viewer labels. Use `--offline` when the snapshot must open without external Mermaid requests. Use `--generated-at <RFC3339>` only for a repeatable fixture or an explicitly fixed timestamp.

The deterministic builder reads selected Markdown directly, preserves source Mermaid, derives only explicit Route, dependency, and coverage relationships, and writes exactly:

```text
.forge/reviews/<review-id>/view.html
```

Do not author an HTML content fragment. Do not choose another output path. Do not run browser, screenshot, layout, or renderer E2E checks for an individual generated snapshot. A successful single build ends generation.

## Freshness check

Run a read-only check when explicitly requested:

```bash
bash <review-viewer-skill>/scripts/build-review-viewer.sh \
  --check .forge/reviews/<review-id>/view.html \
  --format json
```

Exit `0` means every recorded source is current. Exit `1` means stale, missing, malformed, or otherwise unverified. Exit `2` means usage failure. Report the result; rebuild only after a separate explicit create or update request.

## Working files

| Path | Role | Git policy |
|---|---|---|
| `docs/specs/NNN-<slug>/spec.md` | permanent requirement source | tracked |
| `docs/plans/PPP-<slug>/plan.md` | work-scoped execution source | tracked while retained |
| `docs/plans/PPP-<slug>/progress.md` | optional long progress source | tracked while retained |
| `docs/plans/PPP-<slug>/tasks/*.md` | optional independently owned Task source | tracked while retained |
| `.forge/reviews/<review-id>/view.html` | explicitly requested review snapshot | untracked |

If review feedback changes requirements, return to `writing-specs`. If it changes execution detail, return to `writing-plans`. If the plan is ready to run, return to `executing-plans`.

## Non-negotiable rules

- HTML is a view, never the source of truth.
- No explicit request means no build or rebuild.
- Spec and plan modes remain independent; there is no combined fallback.
- Source Mermaid remains source-owned; derived views add no new meaning.
- Staleness can be reported but never authorizes regeneration.
- Spec Pages under `docs/specs/**/index.html` are separate committed artifacts and are never generated or updated by this skill.
