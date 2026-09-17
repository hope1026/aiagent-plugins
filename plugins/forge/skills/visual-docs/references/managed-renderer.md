# Managed Visual Docs

Turn the selected work into a document that a person can understand and use to decide what matters. Respond to the user in their language. This skill stays in English.

A readable Visual Doc needs editorial work: understand the source, identify the reader's questions, explain the answers in a useful order, and choose prose, tables, examples or diagrams that clarify them. File order, heading names, document kinds and renderer profiles are hints, not the reading structure. A short document can stay short.

This reference applies only after choosing the managed renderer for reproducible handbooks, explicit source freshness or deterministic rebuilds, or updates to an existing managed document. Its source files, JSON, renderer and generated-HTML constraints do not apply to freely authored views.

## Request and source boundaries

Create, refresh or check a Visual Doc only when the user requests it. An active request includes the corrections and verification needed to finish that document. A source change or completed implementation alone does not authorize generation or refresh.

| Kind | Source | Output |
|---|---|---|
| `brief` | `.forge/work/<work-id>/brief.md` | local `.forge/visual-docs/<view-id>/view.html` |
| `plan` | `docs/plans/<plan-id>/plan.md`, declared/conventional progress and tasks | local `.forge/visual-docs/<view-id>/view.html` |
| `spec` | one structured Canonical Spec Bundle, optional explicit comparisons | local `.forge/visual-docs/<view-id>/view.html` |
| `project` | `docs/project/project-map.md` and its declared sources | tracked `docs/project-viewer/index.html` |

For a conversational Brief, save one H1 and non-empty `## Goal`, `## Scope`, `## Out of Scope`, `## Done Checks`; the last three contain lists. A Project Map uses `schema: forge/project-map@1` and owns its purpose and responsibilities. Repository scans provide file evidence, never inferred Purpose or Owns. Preserve Spec/Plan/Project source roles, exact governing statement links and lifecycle states. There is no combined kind or separate Spec Guide.

## Understand and compose

Read `composition-authoring.md` for the public input contract and commands. Run the same source selectors with `--prepare --format json` to obtain a read-only packet of source blocks, roles, exact text, source fingerprint and View Context. This creates no HTML. Read the actual source content, not only counts or metadata.

Determine from the request what the reader should understand or decide. Infer routine defaults from context; ask only if a material user-owned choice is missing. Defaults are `review` for Brief/Spec/Project, `execution` for Plan, `mixed` audience and `en` locale. Pass the user's locale and explicit intent/audience.

Write a composition containing:

- A purpose and opening explanation grounded in the selected source.
- The reader's key questions and links to the blocks that answer them.
- Sections in the order that makes the content understandable. Include necessary background, behavior, conditions, differences, responsibilities or next actions according to the actual task.
- Plain-language explanations with exact source excerpts as evidence. Use tables for useful comparisons, diagrams for meaningful relationships and examples for difficult rules. No fixed section count, node threshold or mandatory diagram.
- A truthful semantic review record describing who checked it, how and any unresolved limits.

Preserve exact identifiers and normative quotations in evidence and original detail. You may paraphrase explanations, group explicitly stated facts and illustrate a stated calculation. Preserve obligation strength, conditions, exceptions, numbers, responsibility, status and source role. Distinguish example assumptions from source values. Do not invent missing policy, ownership, causality or approval; explicitly say when the source cannot answer a question. Do not rewrite the Canonical Spec merely to make rendering easier.

Every explanation and graph relation needs relevant evidence, not an arbitrary valid citation. Re-read each claim against its quoted source and relevant surrounding conditions. A valid quote proves provenance, not entailment. Reject an attractive summary that drops an exception. Text-only flows can be explained from prose without modifying the source into arrow syntax.

Use the shared renderer. Do not author document-specific HTML, CSS or JavaScript and do not edit generated HTML. Shared tooling changes use the forge web-app-design skill; individual compositions use the existing visual system.

## Build and verify

Save the local composition at `.forge/visual-docs/<view-id>/composition.json`. For a tracked Project Handbook, save the reproducible input at `docs/project/visual-doc-composition.json`. It is a derived input, not a new source of truth. Keep it with the same output lifecycle and inspect tracked diffs before release.

Run the build arguments with `--composition <path> --dry-run --format json`. Inspect the actual title, questions, answers, reading order, source binding and review limitations. The preflight must report `reading-check-required`, not `source-browser`. Stale sources/context or invalid evidence must be corrected before a build. Do not replace a failing composition with source-browser and call the request complete.

Run the same command without `--dry-run --format json`. The source browser remains accessible for complete original content, deep links and verification. The explanation comes first. Build without a composition is a diagnostic/compatibility source browser, not a finished human-readable explanation.

Verify three different things:

1. **Mechanical integrity:** source/context binding, exact quotations, complete original access, working links, deterministic frozen input and source/composition freshness.
2. **Semantic fidelity:** explanations, tables, example assumptions and every graph edge preserve source meaning and relevant qualifications. Record actual review method and findings. Never label an agent review as human observation.
3. **Reading and display:** inspect the generated document and answer its key questions from the primary reading path. Check that important answers do not require opening files or searching a long source list. Operate evidence and original-navigation links. Inspect representative desktop and narrow layouts for complex/new compositions, tables or diagrams; compare heading, body and provenance hierarchy. Simple documents need a focused rendered check.

A schema pass, exact quote or all-source coverage does not prove semantic accuracy or human comprehension. The generated manifest retains `reading-check-required`; record actual reading evidence in the task rather than hand-editing the HTML to mark it passed. Use an independent reader evaluation for shared tooling changes and include previously unused source material. Do not impose a new independent-agent requirement for every small document.

Correct composition or shared tooling and rebuild within the active request when a check fails. Reuse unaffected regression evidence; do not rerun the entire tooling suite for each document. If a required browser/check is unavailable, state the unverified part and do not claim it passed. A tracked Handbook additionally needs freshness `--check` and repository validation.

## Provenance, navigation and handoff

Keep paths, hashes, renderer metadata and validation details subordinate to explanations. Use familiar locale-specific labels such as `개요`, `역할`, `담당 범위`, `완료 기준`, `출처·검증`. Preserve exact identifiers inside evidence.

The original Project Handbook keeps its searchable bundle/member/section and structure master/detail navigation, keyboard controls, deep links and narrow-layout back action. Independent Spec originals reuse normalized statements and the source renderer. All original content remains reachable; do not flatten it into an inaccessible dump.

The read-only freshness command is:

```bash
bash <visual-docs-skill>/scripts/build-visual-docs.sh --check <output-path> --format json
```

It checks original sources and the saved composition input. A stale result does not authorize a new refresh after the request ends. Generator and frozen composition digests identify the implementation and explanation used; frozen inputs reproduce output, while a new editorial pass need not choose the same prose.

Return the output path and meaningful verification evidence. Distinguish a source browser, an explanation awaiting reading verification and the reading checks actually performed. Markdown remains authoritative. Do not commit, publish, install or refresh beyond the user's authorization.
