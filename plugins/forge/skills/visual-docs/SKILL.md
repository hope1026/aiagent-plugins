---
name: visual-docs
description: 'Use when visualizing Forge Brief, Plan, Canonical Spec or Project Map sources, or creating, updating or checking a managed Forge document. Triggers: "Forge 스펙 시각화", "포지 계획 시각화", "프로젝트 핸드북 갱신", "Visual Docs 최신성 검사". Not for general diagrams, explanations or website design.'
---

# Visual Docs

Help the reader understand Forge sources while preserving their meaning and authority. Respond in the user's language. General visualization uses the current app's capabilities without this skill.

## Choose the useful format

For a one-time explanation, use the format that best answers the request: prose and tables, Mermaid, an available visualization tool, or directly authored HTML, CSS and JavaScript. Let the content and reader determine layout and interaction. A short explanation can stay in the conversation.

Use existing sources, including a conversational Brief or session plan. Do not create a Brief file, Project Map, composition JSON or manifest solely to fit a renderer. Save an artifact only when the request needs one; follow the user's location or project convention, with `.forge/visual-docs/<view-id>/view.html` as the default for local HTML. Freely authored output can be edited directly.

Choose the managed renderer when the request needs a reproducible tracked Project Handbook, explicit source freshness checks, deterministic rebuilds, or an update to an existing managed document. A generic project overview or the word “handbook” alone does not require that path. Infer the choice from the requested result and existing artifact; ask only when an unresolved choice materially changes the deliverable.

Only for the managed path, read `references/managed-renderer.md`. It retains the existing CLI, structured source kinds, composition input, source navigation and freshness contracts. Keep its generated HTML reproducible by editing inputs or shared tooling and rebuilding. Do not claim those guarantees for freely authored output.

## Preserve the source

Read the material that supports the explanation. Keep conditions, exceptions, numbers, responsibilities, approval states and the roles of Brief, Plan and Canonical Spec intact. Distinguish examples and assumptions from source facts; identify what the source leaves unspecified.

Connect important explanations to source paths or statement links, quoting exact wording when needed. Relevant evidence matters more than citation volume. A simple document needs no per-sentence JSON references or separate review form. The view remains a derived explanation; it does not replace Markdown authority or establish product implementation status.

## Verify the requested result

Check that the primary reading path answers the reader's question and preserves the source's qualifications. Inspect the actual delivered surface, operate relevant links and interactions, and check narrow layouts when the document's complexity warrants it. Keep titles, explanations and provenance distinguishable. Use design guidance when the artifact needs it; HTML alone does not require a separate web design workflow.

Correct the affected explanation or display within the active request and reuse checks that still apply. A simple table or diagram needs a focused reading check, not the shared renderer's full regression suite. Report any unavailable rendered check accurately.

An active visualization request includes necessary corrections and verification. Source changes or implementation completion alone do not request a new view or refresh a completed document. Return the result with its source links and meaningful verification limits; do not publish or commit beyond the user's authorization.
