# Authoring a grounded composition

This contract applies only to the optional managed renderer. Freely authored explanations do not use this input schema or rendering pipeline.

The agent edits a constrained JSON explanation, not a template. The renderer supplies visual consistency; the author supplies the reader's questions, useful ordering and source-grounded meaning. Do not automatically transform every source block into a section or every sentence into a diagram.

## Prepare the source

Run from the target repository. Select one source kind:

```bash
bash <visual-docs-skill>/scripts/build-visual-docs.sh \
  --kind spec --spec docs/specs/<bundle>/ --view-id <view-id> \
  --locale ko --intent review --audience product --prepare --format json
```

Replace `--kind spec --spec ...` with `--kind brief --brief ...`, `--kind plan --plan ...` or `--kind project --project-map ...` as applicable. Spec permits explicit `--comparison <bundle>` entries; Plan permits `--progress` and `--tasks-dir`. Use identical selectors, locale, intent and audience for prepare, preflight and build. `--prepare` creates no artifact and cannot be combined with `--composition` or `--dry-run`.

Read the packet's source texts and their roles. Copy `source_fingerprint` and the full `context` unchanged. Select evidence by meaning; each reference contains a source block `id` and an exact non-empty excerpt from its `text` or `heading`. Source IDs stay internal and must not become human headings.

## JSON contract

This abbreviated example uses placeholders for values taken from the prepared packet. It is an authoring example, not a ready build input.

```json
{
  "schema": "forge/visual-doc-composition@1",
  "source_fingerprint": "<prepared source fingerprint>",
  "context": {
    "kind": "spec", "spec_kind": "system", "subtype": "workflow",
    "intent": "review", "audience": "product", "locale": "ko",
    "export_mode": "standalone"
  },
  "title": "요청이 처리되는 과정",
  "lead": {
    "text": "유효한 요청은 검토를 거쳐 처리하고, 누락된 정보는 먼저 보완합니다.",
    "refs": [{"source": "<source block id>", "quote": "<exact supporting excerpt>"}]
  },
  "questions": [{"text": "어떤 경우에 보완이 필요한가?", "answer_blocks": ["missing-information"]}],
  "sections": [{
    "id": "conditions", "title": "처리 조건",
    "blocks": [{
      "id": "missing-information", "type": "prose",
      "text": "필수 정보가 빠졌다면 보완한 뒤 검토를 진행합니다.",
      "refs": [{"source": "<source block id>", "quote": "<exact supporting excerpt>"}]
    }]
  }],
  "review": {
    "method": "agent", "reviewer": "Current authoring agent",
    "notes": "조건과 예외를 주변 원문과 비교했습니다. 실제 표시와 읽기는 build 후 확인합니다."
  }
}
```

Every section has an `id`, readable `title` and non-empty `blocks`. Section IDs and globally unique block IDs start with a lowercase letter and contain at most 64 lowercase letters, digits or hyphens. A question has non-empty `answer_blocks` pointing to actual blocks. Several questions may share an answer; several blocks may answer one question. Do not invent questions merely to fill a template.

All block types contain `id`, `type`, plain `text` and non-empty `refs`. Add exactly the following type-specific fields:

| Type | Additional data | Reader purpose |
|---|---|---|
| `prose` | None | Explain a fact, qualification, decision or an explicit source limitation. |
| `example` | `assumptions: [string, ...]`, possibly empty | Illustrate a source rule. Show actual assumptions separately and check arithmetic. |
| `table` | `columns: [string, ...]`, `rows: [{cells: [string, ...], refs: [...]}, ...]` | Compare meaningful dimensions. Each row has the same number of cells as columns and its own supporting evidence. |
| `flow` | `nodes: [{id, text, refs}, ...]`, `edges: [{from, to, text, refs}, ...]` | Explain directional behavior, including branches. |
| `relationship` | Same as `flow` | Explain ownership, structure or dependencies with labeled relationships. |

For graphs, every edge has a non-empty relation/condition label and supporting evidence. Node IDs are local to the graph; endpoints must exist and every node must have a relation. Use the original conditions on branches; do not turn co-occurrence or an example into required order. The block's `text` explains how to read it. The renderer provides a textual relationship summary and exact evidence in addition to the diagram, including on narrow screens and print. A graph needs no arbitrary minimum node count, and a simple sentence may communicate the same fact better.

All authored text is plain text. Executable/layout markup, code fences and Mermaid directives are rejected; plain identifiers such as `List<T>` are escaped without renaming. Use exact API identifiers as text; source excerpts may contain source syntax because they are escaped and shown as quotations. Titles and comparison labels must also be supported by the surrounding evidence.

`review.method` is `agent` or `human`; identify the actual reviewer in `reviewer` and record findings in `notes`. Never assert human review unless it occurred. This is a semantic review record, not a magic completion flag. A schema validator cannot decide whether a paraphrase entails the cited source. If evidence is real but the explanation contradicts it, reject or correct the explanation during semantic review.

## Save, preflight and build

Save local inputs at `.forge/visual-docs/<view-id>/composition.json`. For a tracked Project Handbook use `docs/project/visual-doc-composition.json` so a checkout can reproduce it. Both are derived, versioned schema inputs; neither owns product truth. No new permanent source type is introduced.

```bash
bash <visual-docs-skill>/scripts/build-visual-docs.sh \
  --kind spec --spec docs/specs/<bundle>/ --view-id <view-id> \
  --locale ko --intent review --audience product \
  --composition .forge/visual-docs/<view-id>/composition.json \
  --dry-run --format json
```

Inspect `quality`, the complete `composition`, source context and actual answer blocks. Correct the composition if it merely enumerates files or conceals the main answers. Then run the same command without `--dry-run --format json`; add `--offline` when required. A fixed `--generated-at <ISO timestamp>` makes deterministic testing possible. The builder refuses mismatched source fingerprints or context and invalid quotes before writing output.

The manifest stores the composition and its digest, generator digest and input file hash. An old output retains the explanation it was built from; `--check` detects changes to source or the saved composition. Re-read affected explanations after either changes. Never update fingerprints merely to bypass a stale failure.

## Review from the reader's position

Write the key questions and expected facts before generation. Inspect the primary reading path and answer those questions without opening the source library; then use evidence to verify important qualifications. Record omissions, incorrect answers and misleading order, not just whether elements exist.

For tooling evaluation, use a fresh reviewer and a held-out source from a different task. Compare the answers with the prewritten expected facts. Include short, prose-only, conditional, unfamiliar-language and insufficient-source cases across the evaluation set. A reader may correctly answer “the source does not specify this”; do not invent completeness. Agent evaluation is useful but is not evidence of a human study.

Keep interpretation and display failures distinct. A semantic failure needs a corrected explanation; a navigation or overflow failure needs composition simplification or shared tooling correction. Do not patch a generated HTML result to hide either failure.
