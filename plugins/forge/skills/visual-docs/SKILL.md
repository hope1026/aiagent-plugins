---
name: visual-docs
description: 'Use when explaining or visualizing Forge Brief, Plan, Canonical Spec or project documentation while preserving source meaning. Triggers: "Forge 스펙 시각화", "포지 계획 시각화", "프로젝트 핸드북 갱신", "Visual Docs 최신성 검사". Not for general diagrams, explanations or website design.'
---

# Visual Docs

Help the reader understand Forge sources while preserving their meaning and authority. Respond in the user's language. General visualization uses the current app's capabilities without this skill.

## Choose the useful format

Identify what this reader needs to understand or decide before choosing the presentation. A newcomer needs purpose and behavior; a change reviewer needs before/after meaning and consequences; a handoff needs progress and next actions. Write down the few key questions and expected facts when they will support a later reading check. These needs can overlap and do not prescribe document sections.

Use the format that best answers the request: prose and tables, Mermaid, an available visualization tool, or directly authored HTML, CSS and JavaScript. Let the content and reader determine layout and interaction. A short explanation can stay in the conversation. Forge supplies no visual template, required section order or fixed navigation layout.

Use existing sources, including a conversational Brief or session plan. Do not create a Brief file, Project Map, composition JSON or manifest solely to fit a renderer. Save an artifact only when the request needs one; follow the user's location or project convention, with `.forge/visual-docs/<view-id>/view.html` as the default for local HTML. Freely authored output can be edited directly.

For an existing document, inspect its source and any project-owned build process before updating it. Follow an existing generator when the project maintains one; otherwise edit the document directly. The former Forge managed builder is no longer supplied. Preserve existing content and useful interactions when changing its presentation, and remove obsolete generator or freshness claims from the updated artifact.

Preserve the source locations behind important explanations. For saved documents that will be reused, record the source revision or selected file hashes when useful. The forge using-forge skill's source-context reference describes an optional layout-independent capture/check tool; existing project methods are equally valid. If the request needs reproducible builds, retain the authored files and build command and test that property separately. Such requests do not require a particular layout or authoring schema.

## Preserve the source

Read the material that supports the explanation. Keep conditions, exceptions, numbers, responsibilities, approval states and the roles of Brief, Plan and Canonical Spec intact. Distinguish examples and assumptions from source facts; identify what the source leaves unspecified.

Connect important explanations to source paths or statement links, quoting exact wording when needed. Relevant evidence matters more than citation volume. A simple document needs no per-sentence JSON references or separate review form. The view remains a derived explanation; it does not replace Markdown authority or establish product implementation status.

## Verify the requested result

Check that the primary reading path answers the reader's question and preserves the source's qualifications. Inspect the actual delivered surface, operate relevant links and interactions, and check narrow layouts when the document's complexity warrants it. Keep titles, explanations and provenance distinguishable. Use design guidance when the artifact needs it; HTML alone does not require a separate web design workflow.

For a representative new explanation approach, have a separate reader answer the preselected questions from the delivered explanation before consulting its sources. Compare their answers with the source facts and look for lost exceptions, mistaken certainty or hidden dependencies. An agent reader is useful evidence, not a human comprehension study. Small edits can reuse existing reading evidence where it still applies.

Correct the affected explanation or display within the active request and reuse checks that still apply. Match verification to the document's meaning and interactions. Report any unavailable rendered check accurately.

An active visualization request includes necessary corrections and verification. Source changes or implementation completion alone do not request a new view or refresh a completed document. Return the result with its source links and meaningful verification limits; do not publish or commit beyond the user's authorization.
