---
name: spec-viewer
description: 'Use when a spec needs to be rendered for human review as a self-contained HTML document with diagrams, tables, and an acceptance checklist, or when the user asks to visualize or present a spec. Triggers: "스펙 시각화", "스펙 보여줘", "spec html", "스펙 뷰어", "다이어그램으로", reviewing a spec with a human.'
---

# Spec Viewer

Announce at start: "Using the forge spec-viewer skill to render the spec as a self-contained HTML viewer."

Respond to the user in the user's language. This skill file stays in English.

## Overview

Assembly, not generation. This skill ships a fixed HTML shell (`assets/viewer-template.html`) and a build script (`scripts/build-viewer.sh`); you author only a content fragment lifted from `spec.md`, and the script splices it into the shell. The generated HTML is a regenerable VIEW for human review — `spec.md` stays the single source of truth.

## Iron Law

```
THE HTML IS A VIEW, NEVER THE TRUTH.
NEVER HAND-WRITE THE SHELL. NEVER EMIT THE MERMAID BUNDLE.
IF THE VIEWER LOOKS WRONG, FIX spec.md OR THE FRAGMENT, THEN REBUILD.
```

## When to Use / When NOT

**Use when:**
- A human will review or approve a spec and wants it presented (tabs, diagrams, checklist).
- The user asks to visualize, present, print, or share a spec.
- Walking acceptance criteria with a stakeholder (checkbox state persists in the browser).

**Do NOT use when:**
- The spec itself needs writing or changing — that is the forge writing-specs skill.
- You just need to read the spec yourself — read the markdown directly.
- Building actual product UI — that is the forge ui-design skill.

## The Process

Create one todo per numbered step below before starting.

1. **Read the spec.** Locate `docs/specs/NNN-<slug>/spec.md` and read it in full. Note the feature name (for `-t`), the `Status:` line (for `-s`), and which template sections are present.

2. **Author the content fragment** at `.forge/scratch/NNN-<slug>-content.html` (in the forge working directory `.forge/` of the target project). Follow the Fragment Rules below exactly. Ensure `.forge/scratch/.gitignore` containing `*` exists (create it if missing).

3. **Ensure the output directory is self-ignoring.** Create `.forge/viewer/.gitignore` containing `*` if missing.

4. **Build.** Run in the shell, from the target project root:

   ```
   bash <path-to-this-skill>/scripts/build-viewer.sh \
     -c .forge/scratch/NNN-<slug>-content.html \
     -t "<Feature name>" -s "<status>" \
     -o .forge/viewer/NNN-<slug>.html
   ```

   Expect a `built: .forge/viewer/NNN-<slug>.html` line. Default output loads Mermaid from a CDN (small file, needs network to render diagrams). Add `--offline` to inline the Mermaid bundle (~3 MB file, renders with no network).

5. **Verify and report.** Confirm the file exists and the `built:` line printed. If a browser is available, open it and check: tabs switch, diagrams render as SVG, invalid diagrams show their source (never a blank page). Tell the user the output path, note that checkbox state persists locally in their browser, and offer `--offline` if they need a no-network file. Do not claim it renders without having built it.

### Fragment Rules

The fragment is ONLY the six tab panels — no doctype, no head, no scripts, no styles. The shell provides everything else.

- Six `<section class="tab-panel" id="..." data-title="...">` blocks, in this fixed order mirroring spec.md: `overview` (Overview) · `requirements` (Requirements) · `flows` (Flows) · `data` (Data &amp; Interfaces) · `acceptance` (Acceptance) · `history` (History). Keep all six even if a spec section is empty — put a one-line note like `<p>None.</p>`.
- **Mermaid fences are lifted verbatim** from spec.md into `<pre class="mermaid">` blocks. Do not "fix", reformat, or invent diagrams. If a fence is broken, the viewer shows its source as an error — then fix spec.md and rebuild.
- Markdown tables become HTML `<table>` with `<thead>`/`<tbody>`.
- Requirements render as a table whose rows carry R-ID anchor ids, so `#R3` deep-links work:
  `<tr id="R1"><td>R1</td><td>WHEN ... THE SYSTEM SHALL ...</td></tr>`
- Acceptance criteria render as checkboxes with the full Given/When/Then text and their R-IDs:
  `<label class="ac-item"><input type="checkbox" data-ac="AC1"> <span><strong>AC1</strong> Given ... When ... Then ... <em>(R1, R2)</em></span></label>`
- **Escape raw text**: `&` becomes `&amp;` and `<` becomes `&lt;` in all spec text — including inside `<pre class="mermaid">` (the browser decodes entities back to the original source before parsing).
- Deep links: any panel opens directly via hash, e.g. `viewer.html#flows`.

## Working Files

| File | Role |
|---|---|
| `docs/specs/NNN-<slug>/spec.md` | Input — the source of truth; never edited by this skill |
| `.forge/scratch/NNN-<slug>-content.html` | Content fragment you author (gitignored) |
| `.forge/scratch/.gitignore` | Contains `*`; create if missing |
| `.forge/viewer/NNN-<slug>.html` | Generated viewer output (gitignored, regenerable) |
| `.forge/viewer/.gitignore` | Contains `*`; create if missing |

## Red Flags

| Excuse | Reality |
|---|---|
| "The shell is close, I'll just tweak the HTML output directly" | The output is disposable. Edit the fragment or spec.md and rebuild; hand-edits are lost on the next build. |
| "This diagram has a syntax error, I'll fix it in the HTML" | Fix the fence in spec.md, re-lift it, rebuild. The viewer must never diverge from the spec. |
| "I'll write the mermaid script tag / bundle myself" | Never. The build script handles CDN vs `--offline`; emitting the bundle bloats context and breaks the file. |
| "The spec has no Flows section, I'll invent a diagram to fill the tab" | Render what exists. An empty panel with a note is honest; an invented diagram is a lie about the spec. |
| "I'll skip the build script and write the whole page — it's faster" | Freestyled shells break tabs, print, persistence, and error fallback. Assembly only. |
| "I can't find the build script, so I'll improvise the HTML" | The script ships with this skill at `scripts/build-viewer.sh`, next to this SKILL.md. Locate the skill directory (search for `build-viewer.sh` if needed) — improvising is never the fallback. |
| "I'll commit the viewer HTML so the team can see it" | `.forge/viewer/` is gitignored by design. Share the file directly or regenerate on demand; the committed truth is spec.md. |
| "It built, so it renders" | A `built:` line proves assembly, not rendering. Open it (or say you could not) before claiming it works. |

## Handoff

**Viewer built at `.forge/viewer/NNN-<slug>.html` — report the path to the user and offer `--offline`. If the review produces spec changes, next is the forge writing-specs skill in change mode; if the spec is approved and has no plan yet, next is the forge writing-plans skill.**
