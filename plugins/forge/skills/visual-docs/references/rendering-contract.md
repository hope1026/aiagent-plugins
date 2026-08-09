# Visual Docs rendering contract

`review_renderer.render_review()` turns one validated source set into a read-only HTML document. Markdown and the lossless Semantic IR own every statement in the result.

## Pipeline and outputs

The renderer consumes one shared pipeline:

```text
Markdown sources → Semantic IR → View Context → validated Presentation Plan
                 → reusable components → stable HTML shell
```

The CLI writes through a same-directory temporary file and atomic replace:

```text
brief | plan | spec → .forge/visual-docs/<view-id>/view.html
project             → docs/project-viewer/index.html
```

Local views are untracked. Project Handbook is a tracked derived document reproducible from Project Map, declared Canonical Specs, and repository evidence. The builder never edits selected Markdown or writes source-adjacent HTML.

## Source ownership

Brief owns Goal, Scope, Out of Scope, and Done Checks. An Execution Plan owns routes, tasks, progress, and evidence. A Canonical Spec Bundle owns requirements, acceptance statements, decisions, and source Mermaid. Project Map owns Project Overview, Key Capabilities, declared Spec Bundles, and Structure Purpose and Owns.

Repository scanning may enumerate file evidence and hash bytes. It must not infer folder Purpose, ownership, project capabilities, or Spec meaning.

## Reader-facing language

Identity and explanation are separate layers. The HTML preserves exact paths, commands, API and schema names, protocol values, code symbols, lifecycle tokens, Requirement and Acceptance headings, and provenance. It never translates or abbreviates an identifier.

Reader-facing headings, orientation lines, summaries, captions, and descriptions use familiar words and complete sentences in the selected locale. They answer what the item does, why it exists, what it owns, or what the reader should confirm. The renderer localizes only fixed UI vocabulary; it does not generate freeform paraphrases of source meaning.

When both layers are useful, the plain-language explanation leads and the exact identifier follows as code or subordinate provenance. Raw profile names, internal keys, namespaces, hashes, and manifest field names do not become primary headings. They remain in source provenance or collapsed Developer information unless the review is specifically about that identifier.

Normative source statements remain verbatim. Human-readable orientation may frame those statements, but it must not weaken, expand, or reinterpret them. Brief and Project Map descriptive prose should already be written for a reader who does not know the repository internals.

## Semantic IR

Every selected source records exact repository-relative paths, H1 titles, roles, metadata, outlines, full-statement entities, explicit relations, and ordered blocks. Prose, lists, tables, code, Mermaid, and unrecognized Markdown use distinct block kinds; unknown structures fall back to `generic`.

Independent Spec View and Project Handbook Spec detail use the same normalized Spec entities. Their member paths, full Requirement and Acceptance headings, Mermaid SHA-256, and provenance must match.

## View Context and profiles

`ViewContext` contains document `kind`, `spec_kind`, subtype, intent, audience, locale, and export mode. The registry provides at least `generic`, `brief.summary`, `spec.workflow`, `spec.api`, `spec.architecture`, `spec.policy`, `spec.migration`, `plan.execution`, `plan.status`, `project.handbook`, `project.structure`, `project.spec-detail`, and `comparison`.

Profiles compose reusable component IDs. They do not own document-specific templates. The stable shell owns typography, palette, spacing, focus, freshness, provenance, deep links, overflow, print behavior, and responsive interaction.

## Project Handbook information architecture

Primary navigation is limited to Project at a glance, Spec, and Structure. The Overview presents Project Map content without repeating detailed Spec statements. Structure cards present Purpose, Owns, and Entry Points before derived file evidence.

Runtime mirror, validation, drift, hashes, source rows, and lifecycle counts are developer evidence. They remain in collapsed Developer information and never become primary navigation.

## Presentation Plan validation

Before rendering, the planner rejects a plan when:

- its mapping has unknown fields or invalid enum values;
- a component ID is absent from the component registry;
- a component references a missing block or entity;
- selected references omit source content;
- authored labels or descriptions introduce copy absent from source or fixed UI vocabulary.

The valid plan may order and group source-backed components. It may derive only explicit relationships, counts, file evidence, and freshness state.

## Mermaid delivery

Source Mermaid text is escaped for HTML but otherwise unchanged. Each block records the SHA-256 of its UTF-8 source text. CDN mode uses exactly `https://cdn.jsdelivr.net/npm/mermaid@11.16.0/dist/mermaid.min.js`. Offline mode inlines the sibling `writing-specs/assets/mermaid.min.js` only after its recorded checksum passes.

## Manifest and freshness

The embedded `forge-source-manifest` includes `kind`, `view_id`, `output_lifecycle`, generation metadata, View Context, validated Presentation Plan, counts, `freshness: unverified`, and ordered bundle, member, and document source rows with roles, paths, and SHA-256. Project documents also record Project Map path, declared Spec Bundles, and repository evidence sources.

HTTP views resolve source URLs through output-relative `source_base` and fetch only same-origin bytes. File views keep each source `unverified` until its row picker hashes a local file. Any stale source makes its group stale; otherwise any unverified source makes it unverified; every source must match for current.

## Determinism

With identical source bytes, View Context, Presentation Plan, generator assets, `generated_at`, checkpoint, and commit, `render_review()` returns identical UTF-8 text. It excludes absolute paths, cwd, hostname, and implicit timestamps.
