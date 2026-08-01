# Lifecycle Viewer Content Patterns

Use these patterns when authoring the content fragment. The fixed shell owns layout, color, spacing, interaction, Mermaid runtime, and persistence. The fragment owns only source-derived content and semantic markup.

## Six panels

```html
<section class="tab-panel" id="overview" data-title="개요">...</section>
<section class="tab-panel" id="requirements" data-title="요구사항">...</section>
<section class="tab-panel" id="flows" data-title="흐름">...</section>
<section class="tab-panel" id="data" data-title="데이터와 인터페이스">...</section>
<section class="tab-panel" id="acceptance" data-title="승인 기준">...</section>
<section class="tab-panel" id="history" data-title="변경 이력">...</section>
```

Keep all six panels. For an empty section, state that the source contains no corresponding information. Do not invent filler.

## Panel content by mode

| Panel | Spec mode | Plan mode |
|---|---|---|
| Overview | purpose, status, counts | goal, completion state, Routes, reading order |
| Requirements | R list and policies | Global Constraints, Related Specs links, and Route scope |
| Flows | source behavior diagrams | Route map, dependency, runtime, extension flow |
| Data | source data and interfaces | files, server authority, Remote, transaction, interfaces |
| Acceptance | AC checklist | AC→Task→verification when related; otherwise Task→verification |
| History | decisions and source metadata | Progress History, checkpoints, source hashes, rebuild command |

## Diagram package

```html
<div class="diagram-block" data-origin="Spec source">
  <h3 id="runtime-flow-title">요청은 어디에서 검증되고 저장될까?</h3>
  <p><strong>이 화면에서 확인할 것:</strong> 서버가 검증과 transaction을 소유하는지 확인한다.</p>
  <p>읽는 법: 왼쪽 actor에서 시작해 응답이 돌아올 때까지 화살표를 따른다.</p>
  <div class="table-scroll" role="region" aria-label="Runtime 책임 요약">
    <table>...</table>
  </div>
  <div class="diagram-scroll" role="region" aria-labelledby="runtime-flow-title">
    <pre class="mermaid">sequenceDiagram
    Client-&gt;&gt;Server: request</pre>
  </div>
</div>
```

Escape raw Mermaid text for HTML: `&` becomes `&amp;` and `<` becomes `&lt;`. Do not otherwise alter the source. The browser decodes the entities before Mermaid parses the block.

Use `data-origin="Spec source"`, `data-origin="Plan source"`, or `data-origin="Derived view"`. A derived diagram must be reproducible from explicit source fields.

## Deep links

```html
<tr id="R17"><td><a href="#R17">R17</a></td><td>...</td></tr>
<article id="Task4"><h3><a href="#Task4">Task 4</a></h3>...</article>
<label class="ac-item" id="AC9"><input type="checkbox" data-ac="AC9"> ...</label>
<label class="ac-item" id="Task4-Step2"><input type="checkbox" data-step="Task4-Step2"> ...</label>
```

Step keys are Task-scoped because plan Step numbers restart inside each Task. AC and Step checkboxes record review progress only; do not label them product PASS or FAIL.

## History manifest

The fixed shell displays mode, locale, relative source path, generated SHA-256, generated time, counts, read-time freshness, and rebuild command. The History panel adds source decisions, checkpoint summaries, and commit IDs when those exist in the selected source set.

Spec View deep links stay within R and AC content. Plan View deep links stay within Task and Step content. Related Specs are navigation links only; never create a cross-source combined traceability panel.

## Mobile fallback

For sequence diagrams or large dependency graphs:

1. Show an actor or Route summary table first.
2. If the horizontal diagram still needs interpretation, add a source-derived vertical ordered list or flowchart.
3. Keep the original source diagram unchanged inside `.diagram-scroll`.

The fixed shell owns responsive layout. Do not add a post-build viewport or scroll verification step for an individual generated View.
