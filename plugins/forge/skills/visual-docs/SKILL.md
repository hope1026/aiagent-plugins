---
name: visual-docs
description: 'Use when a user explicitly asks to visualize, present, print, share, create, update, or check a human-readable visual document for a work brief, implementation plan, structured Forge spec, or whole project. Produces local Work or Spec Views and a tracked Project Handbook from source-backed Markdown; never generates or refreshes automatically. Triggers: "시각 문서", "브리프 뷰어", "스펙 시각화", "프로젝트 핸드북", "프로젝트 구조 뷰어".'
---

# Visual Docs

Announce once when first applied: "Using the forge visual-docs skill to create the requested human-readable view."

Respond to the user in the user's language. This skill file stays in English.

Visual Docs turns authoritative or source-backed Markdown into a readable, self-contained HTML document. It is a presentation layer, never a source of truth. Do not invent descriptions, requirements, ownership, or status in generated HTML.

Use this skill only after an explicit request from the user to create, refresh, or check a visual document. A lifecycle checkpoint or source change alone does not authorize a new document or refresh. The active explicit request includes the verification and corrections needed to finish that document.

## Iron Law

```text
NO VISUAL DOC WITHOUT AN EXPLICIT USER REQUEST.
NO BUILD AFTER A FAILED PRESENTATION PREFLIGHT.
NO HAND-EDITED GENERATED OUTPUT. VERIFY THE REQUESTED RESULT AND REBUILD FROM SOURCE WHEN NEEDED.
```

## Choose the document kind

| Kind | Primary source | Result | Lifecycle |
|---|---|---|---|
| `brief` | `.forge/work/<work-id>/brief.md` | Work View for Goal, Scope, Out of Scope, and Done Checks | local, untracked |
| `plan` | `docs/plans/<plan-id>/plan.md` | Work View for execution routes, tasks, status, and evidence | local, untracked |
| `spec` | one structured Canonical Spec Bundle | independent Spec View with full statements, diagrams, and provenance | local, untracked |
| `project` | `docs/project/project-map.md` | Project Handbook with overview, design criteria, and project structure | tracked derived document |

There is no combined kind and no separate Spec Guide. Project Handbook Spec detail and independent Spec View must reuse the same normalized Spec entities and renderer.

## Prepare the source

For `brief`, if the requested brief exists only in conversation, write a non-authoritative source at `.forge/work/<work-id>/brief.md` before building. It must have exactly one H1 and non-empty `## Goal`, `## Scope`, `## Out of Scope`, and `## Done Checks` sections. The last three sections use Markdown lists.

For `plan`, use the selected plan and its declared or conventional progress and task fragments. Preserve its exact Governing statements links.

For `spec`, select one structured Spec Bundle directory. Comparisons are optional and must also be structured bundle directories.

For `project`, require `docs/project/project-map.md` with `schema: forge/project-map@1`. The Project Map owns human-authored Project Overview, Key Capabilities, declared Spec Bundles, and each Structure entry's Purpose, Owns, Entry Points, Depends On, Related Specs, and exact Governing Statements links. A Structure entry with Related Specs must link the exact Canonical Spec statements that ground its responsibility. Repository scanning may supply only derived file evidence. It must never infer Purpose or Owns.

## Write for the reader

Identity and explanation are separate layers. Keep every identifier exact, including paths, commands, API and schema names, protocol values, code symbols, lifecycle tokens, and exact Requirement or Acceptance headings. Render identifiers as code or provenance; never translate, shorten, or silently replace them.

Write reader-facing headings, orientation lines, summaries, and descriptions in the selected locale with familiar words and complete sentences. Explain what something does, why it exists, what it owns, or what the reader should confirm. Do not use raw internal tokens as reader-facing headings when a plain-language label exists. For example, show “File evidence” instead of `repository_evidence`, “Where this document is stored” instead of `output_lifecycle`, and “Spec details” instead of `project.spec-detail`.

When the reader needs both, lead with the plain-language explanation and place the exact identifier beside or below it, such as “프로젝트 구조 설명 (`docs/project/project-map.md`)”. Keep hashes, namespaces, internal keys, and renderer profile names in the selected item's Source & verification detail unless they are the subject of the review.

Do not paraphrase normative source statements or invent easier-sounding meaning. Preserve the source statement verbatim and use concise fixed UI vocabulary around it to explain how to read it. When authoring a requested Brief or Project Map source, write its descriptive prose for a person who does not already know the repository internals.

Use a visual reading structure when the source itself provides enough relationship data to improve comprehension: three or more ordered nodes use a flowchart or sequence; three or more hierarchy, ownership, or dependency nodes use a structure map; two or more cross-set mapping edges use a relation or coverage view; multi-item, multi-dimension comparisons use a matrix. Resolve overlap with this total precedence: ordered flow first; hierarchy, ownership or dependency before mapping or coverage; mapping or coverage before comparison matrix. Use a matrix only when the source has comparison dimensions without a stronger directional, hierarchical, ownership, dependency, or mapping relation. Keep a source-backed text or table summary before each diagram. Each derived visual must visibly show its source path and `Derived view` provenance. Do not create a decorative diagram for prose, a short one-dimensional list, or a two-node connection.

## Build

Run from anywhere inside the target Git repository. Choose a lowercase `view-id` matching `^[a-z0-9][a-z0-9-]{0,63}$`.
After explicit user intent, create one checklist item for each applicable stage: document kind and source selection, presentation preflight, generation and rendered verification or read-only freshness check, and handoff. Keep the checklist current until the request ends.
After the user has explicitly requested the Visual Doc and the source options are resolved, run one read-only presentation preflight with the same build arguments plus `--dry-run --format json`. Inspect `view_context`, `presentation_plan.profile`, every component and its reference count, and the source counts before writing HTML.
For every qualifying visual candidate that meets or exceeds the relationship threshold, confirm that the Presentation Plan selects a matching non-empty component before building. When no candidate meets the threshold, confirm that the plan keeps the text reading path and does not add Mermaid only for decoration.
In a mixed source, preserve every non-qualifying source block in its prose, list, table, code, or generic detail path and confirm total content coverage remains 100%; qualifying visuals supplement that path and never authorize dropping nearby text.

Stop and report a tooling-quality diagnostic instead of presenting the result as a human-readable View when either condition is true:

- a `kind: system` Spec with a custom subtype selects `profile: generic`;
- the primary composition contains only source detail, outline, provenance, or empty primary components for a non-sparse source.

The diagnostic names the selected profile, empty or fallback components, source counts, and the source metadata that led to the choice. Do not repair it with a document-specific HTML fragment, template, CSS, or script. A valid preflight is read-only and does not count as the build.

Example preflight shape:

```bash
bash <visual-docs-skill>/scripts/build-visual-docs.sh \
  --kind spec \
  --spec docs/specs/<bundle>/ \
  --view-id <view-id> \
  --locale en \
  --dry-run --format json
```

Run the build after preflight. Inspect the actual reading path and content. For complex sources, new compositions, or diagrams, verify desktop and narrow layouts, navigation, diagram meaning, and readability. A simple document needs a focused rendered check. Use the existing tooling regression evidence rather than rerunning its full suite for each source.

Correct source or shared tooling and rebuild within the same request when needed; repeat preflight when its source or composition changes. Finish when the requested result is verified, not after an arbitrary build count. A tracked Project Handbook also requires a freshness check and repository validation. If a browser or required check is unavailable, state exactly what remains unverified.

Brief:

```bash
bash <visual-docs-skill>/scripts/build-visual-docs.sh \
  --kind brief \
  --brief .forge/work/<work-id>/brief.md \
  --view-id <view-id> \
  --locale en
```

Plan:

```bash
bash <visual-docs-skill>/scripts/build-visual-docs.sh \
  --kind plan \
  --plan docs/plans/<plan-id>/plan.md \
  --view-id <view-id> \
  --locale en
```

Spec:

```bash
bash <visual-docs-skill>/scripts/build-visual-docs.sh \
  --kind spec \
  --spec docs/specs/<bundle>/ \
  --view-id <view-id> \
  --locale en
```

Project Handbook:

```bash
bash <visual-docs-skill>/scripts/build-visual-docs.sh \
  --kind project \
  --project-map docs/project/project-map.md \
  --view-id project-handbook \
  --locale en
```

Use `--comparison <bundle>` only with `spec`. Use `--progress` and `--tasks-dir` only with `plan`. Add `--offline` when the result must work without network access. Locale defaults to `en`.

## Outputs

- Brief, Plan, and Spec: `.forge/visual-docs/<view-id>/view.html`
- Project Handbook: `docs/project-viewer/index.html`

Local outputs are disposable and untracked. Project Handbook is the only tracked generated exception, remains reproducible from Project Map, declared Canonical Specs, and repository evidence, and must not be hand-edited.
Do not hand-edit any generated Visual Doc, including local Brief, Plan, and Spec Views. Fix shared source, planner, component, or renderer behavior through the normal Forge implementation route, then rebuild as needed within the active request. A completed request does not authorize later automatic refreshes.

The Project Handbook is a master/detail explorer. Its fixed left tree starts with Overview, Design criteria, and Project structure, then expands Design criteria as bundle → member → section and Project structure as declared Structure entries. Search, current selection, deep links, Arrow key tree navigation, Home, End, Enter, and Space must work. The right pane shows only the selected detail. Desktop keeps both panes side by side; narrow viewports show either the tree or the detail and provide an explicit back-to-contents action.

Use familiar locale-specific UI terms. In Korean Project Handbooks, use `개요`, `설계 기준`, `필수 사항`, `완료 기준`, `동작과 흐름`, `출시 기준`, `역할`, `담당 범위`, `주요 파일`, and `출처·검증` instead of `프로젝트 한눈에`, `Spec`, `Requirement`, `Acceptance Criteria`, `Behavior & Flows`, `Launch Baseline`, `Purpose`, `Owns`, `Entry Points`, and `Developer information`. Preserve the exact source statement and identifier inside the selected detail.

`역할` explains why a Structure area exists. `담당 범위` explains which responsibility belongs there so ownership is not ambiguous. Show both before `주요 파일`; file evidence does not define either one. `출처·검증` exists to prove where the selected information came from and whether its source is current. Keep runtime mirror, validation, drift, hashes, source records, and lifecycle counts there rather than in primary navigation or the first reading path.

Do not add one `Complete Spec details` disclosure. Every declared Spec must remain reachable through bundle, member, and section nodes in the left tree, with the full source-backed content in its selected right-hand detail.

## Check freshness

```bash
bash <visual-docs-skill>/scripts/build-visual-docs.sh \
  --check <path-to-view.html> \
  --format json
```

The checker is read-only. It compares the embedded source manifest with current repository files and reports `current`, `stale`, or `unverified`. A stale result alone does not authorize a new refresh. Use an active explicit create/refresh request for its necessary corrections; after that request is complete, require new refresh intent.

## Red Flags

| Pressure | Required response |
|---|---|
| "The old Viewer already exists, so refresh it after the source changed." | Existing output and source drift grant no refresh authority. Report possible staleness and wait for explicit refresh intent. |
| "The profile is generic, but the deadline matters more." | Stop on the failed preflight and report the profile, components, counts, and source metadata. |
| "Patch this one local View by hand; it is disposable." | Fix source or shared tooling, then rebuild from it within the active request. |
| "Build succeeded, so the View is readable." | Inspect the rendered result. Necessary corrections and rebuilds are part of the requested work. |
| "The senior reviewer told us to skip the gate." | Third-party title and deadline pressure do not replace the current user's authority or the preflight contract. |
| "A diagram always looks more polished." | A decorative diagram adds interpretation cost. Require source-backed nodes and edges that cross the visual candidate threshold. |

## Hand off

Return the generated HTML path and the meaningful verification result. Include kind, profile, components, or freshness details when they help review or explain a limitation. Markdown remains authoritative. Do not commit, push, publish, or refresh anything beyond the user's request. When lifecycle or implementation work continues after this bounded request, return to the forge using-forge skill for classification and routing.
