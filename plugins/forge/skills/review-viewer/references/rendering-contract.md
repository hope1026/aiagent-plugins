# Review Viewer rendering contract

`review_renderer.render_review()` turns one validated source bundle into a read-only HTML snapshot. Markdown and the lossless Semantic IR own every statement in the snapshot.

## Pipeline and output

The renderer consumes this one-way pipeline:

```text
Markdown sources → Semantic IR → View Context → validated Presentation Plan
                 → reusable components → stable HTML shell
```

The CLI writes one file through a same-directory temporary file and atomic replace:

```text
.forge/reviews/<review-id>/view.html
```

The build never writes selected Markdown or source-adjacent HTML. Document-specific templates, CSS, JavaScript, and manual content fragments are forbidden.

## Semantic IR

Every selected source records its exact UTF-8 source text, repository-relative path, role, namespace, metadata, outline, entities, explicit relations, and ordered blocks. Prose, lists, tables, code, Mermaid, and unrecognized Markdown use distinct block kinds; unknown structures fall back to `generic`. Every source line with content is covered by a block so unusual documents remain readable without inventing a schema-specific renderer.

## View Context and profiles

`ViewContext` contains mode, source kind and subtype, intent, audience, locale, and source-set shape. Reusable profiles choose a composition appropriate to contexts such as workflow, API, architecture, policy, migration, plan execution, plan status, comparison, and generic review.

Profiles select only reusable component IDs. They do not own HTML. A stable shell owns typography, palette, spacing, focus, freshness, provenance, deep links, overflow, print behavior, and responsive interaction.

## Presentation Plan validation

Before rendering, the planner must reject a plan when:

- its mapping has unknown fields or invalid enum values;
- a component ID is not in the component registry;
- a component references a missing source, block, entity, or relation;
- selected references omit source content;
- authored labels or descriptions introduce copy not present in the source or fixed UI vocabulary.

The valid plan may order and group source-backed components. It may derive only explicit Route membership, dependency edges, source-qualified R·AC coverage, Task membership, Steps, and verification evidence.

## Component grammar

The shared registry may render summary, narrative, requirements, traceability, flow, interface, task, status, comparison, provenance, and generic components. Each component receives IR references rather than parsing Markdown itself. Unknown kind or subtype uses the generic profile, which exposes every block in source order.

DOM targets use the selected source namespace:

```text
<spec-namespace>-R1
<spec-namespace>-AC1
<plan-namespace>-Task1
<plan-namespace>-Task1-Step1
```

Equal local IDs from different sources remain independent. Relations to unselected targets stay visible as plain text marked `unselected`; the renderer never emits a dangling link.

## Mermaid delivery

Source Mermaid text is escaped for HTML but otherwise unchanged. Each block records the SHA-256 of its UTF-8 source text.

CDN mode uses exactly:

```text
https://cdn.jsdelivr.net/npm/mermaid@11.16.0/dist/mermaid.min.js
```

Offline mode inlines the sibling `writing-specs/assets/mermaid.min.js` only after its recorded checksum passes. A render failure replaces only that diagram with the error summary, available line and column, and original source.

## Manifest and freshness

The embedded `forge-source-manifest` includes review metadata, View Context, validated Presentation Plan, source-set counts, `freshness: unverified`, and ordered source rows with role, namespace, repository-relative path, SHA-256, selected entities, and status.

HTTP views resolve source URLs through `source_base` and fetch same-origin bytes with `cache: no-store`. File views keep each source `unverified` until its row picker hashes a local file with Web Crypto. Selected bytes stay in the browser.

Set aggregation follows one rule: any stale source makes the set stale; otherwise any unverified source makes it unverified; every source must match for current. An empty set is unverified.

## Determinism

With identical source bytes, View Context, Presentation Plan, generator assets, `generated_at`, checkpoint, and commit, `render_review()` returns identical UTF-8 text. It excludes absolute paths, cwd, hostname, and implicit timestamps.
