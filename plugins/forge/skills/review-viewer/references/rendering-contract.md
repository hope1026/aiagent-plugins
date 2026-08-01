# Review Viewer rendering contract

`review_renderer.render_review()` turns one validated `ReviewBundle` into a read-only HTML snapshot. Markdown and the typed source model own every statement in the snapshot.

## Input and output

The renderer accepts one `spec` or `plan` bundle plus explicit review metadata. It performs no repository reads except fixed Forge assets: the Viewer template, freshness runtime, shared sibling Markdown renderer, and checksum-verified Mermaid bundle.

The CLI writes one file through a same-directory temporary file and atomic replace:

```text
.forge/reviews/<review-id>/view.html
```

The resolved output parent must stay inside the repository. The build never writes Spec Pages, selected Markdown, or source-adjacent HTML.

## Six panels

Every snapshot contains these panel IDs in order:

| Panel | Spec mode | Plan mode |
|---|---|---|
| `overview` | source counts and overview | H1 plan title, canonical `**Goal:**`/`**목표:**`, status, source-set counts, completion summary, and a source-owned `## User Experience`/`## 사용자 경험` section only when present |
| `requirements` | current and comparison requirements | source-owned English/Korean constraint (`Constraints`, `제약`) and policy (`Policy`, `정책`) sections with provenance, explicit typed Route title·Task scope·Route prerequisites, Related Specs context |
| `flows` | source Mermaid | Route Map, explicit dependencies, source Mermaid |
| `data` | source Data & Interfaces | Runtime Atlas including bilingual runtime·architecture·data·interface·flow·server authority·files·remotes·transactions sections, collapsed provenance-bearing main `## Tasks` source detail, parsed Task and Step detail |
| `acceptance` | source AC review items | AC Coverage, verification evidence, context AC review items |
| `history` | provenance and source history | provenance, read-only source plan status and main/auxiliary Task·Step Markdown checkbox state, Progress History, collapsed `progress.md` and `tasks/*.md` detail |

The reading order is summary, visual flow, source detail, then acceptance evidence. Main `## Tasks` and auxiliary source detail stay collapsed until the reviewer opens them; their source-owned Files, Remote, transaction, Interface, or localized metadata remains verbatim Markdown-derived content rather than a generated claim.

## Identity and provenance

DOM targets use the selected source namespace:

```text
<spec-namespace>-R1
<spec-namespace>-AC1
<plan-namespace>-Task1
<plan-namespace>-Task1-Step1
```

Review checkbox storage keys contain `review-id`, source namespace, item kind, and item ID. Equal `R1`, `AC1`, or `spec.md` basenames from different sources remain independent.

Each source diagram records one origin and repository-relative path:

- `Current spec source`
- `Comparison source`
- `Plan source`
- `Related spec context`

Mechanically calculated Route, dependency, and coverage views use `Derived view`. They may use only typed Route membership, dependency edges, source-qualified R·AC references, Task membership, Steps, and verification evidence. AC Coverage exposes each actual namespaced Step ID as a link instead of replacing source identity with a count.

Only selected context items become link targets. If a selected AC names an R that was not selected, or a Task trace names any unselected context item, the relation stays visible as plain text marked `unselected`; the renderer must not emit an `href` whose DOM target is absent.

## Mermaid delivery

Source Mermaid text is escaped for HTML but otherwise unchanged. Each block records the SHA-256 of its UTF-8 source text.

CDN mode uses exactly:

```text
https://cdn.jsdelivr.net/npm/mermaid@11.16.0/dist/mermaid.min.js
```

Offline mode inlines the sibling `writing-specs/assets/mermaid.min.js` only after its recorded checksum passes. A render failure replaces only that diagram with the error summary, available line and column, and original source.

## Manifest and freshness

The embedded `forge-source-manifest` matches `review_freshness.check_review()`:

- required review metadata and source-set counts;
- initial `freshness: unverified`;
- ordered source rows with role, namespace, repository-relative path, SHA-256, selected requirements, selected acceptance criteria, and status.

HTTP views resolve source URLs through `source_base` and fetch same-origin bytes with `cache: no-store`. File views keep every source `unverified` until its own row picker hashes a local file with Web Crypto. Selected bytes stay in the browser.

Set aggregation follows one rule: any stale source makes the set stale; otherwise any unverified source makes it unverified; every source must match for current. An empty set is unverified.

## Determinism

With identical source bytes, review options, generator assets, `generated_at`, checkpoint, and commit, `render_review()` returns identical UTF-8 text. It excludes absolute paths, cwd, hostname, and implicit timestamps.
