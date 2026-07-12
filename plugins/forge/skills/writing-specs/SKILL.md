---
name: writing-specs
description: 'Use when creating features, changing any behavior, starting a project, or when requirements are unclear - BEFORE any plan or implementation. Also use for spec change requests, resolving [NEEDS CLARIFICATION] markers, or syncing a spec with existing code (drift repair). Triggers: "스펙", "스펙 작성", "기능 추가", "기능 변경", "요구사항", "설계", "brainstorm", "new feature", "change request".'
---

# Writing Specs

Announce at start: "Using the forge writing-specs skill — mode: <new | change | clarify | sync>."

Respond to the user in the user's language. This skill file stays in English. Write the spec in the user's language; this is mandatory, not optional. Keep the template's canonical `##` headings, traceability IDs, lifecycle tokens, code identifiers, and established original-language terms unchanged.

## Overview

The spec is the source of truth. Every behavior change starts by writing or editing a spec under `docs/specs/`, getting the user's approval, and only then planning and coding. This skill turns intent into an approved spec through collaborative dialogue — it never produces code.

## Spec Language

- Determine the language from the user's current request and established conversation language. If they explicitly request another language for the spec, follow that request.
- Write all human-readable spec content in that language: the title, overview, non-goals, requirements, acceptance criteria, diagram labels, table labels and descriptions, and decision history explanations.
- Preserve terms whose identity or established meaning belongs to their original language. This includes proper nouns, product and framework names, API and protocol names, code identifiers, commands, quoted UI labels, and domain terms with a recognized original form. Do not force-translate or transliterate them.
- Explain preserved terms and all surrounding prose in the user's language. Original-language terms are not permission to leave explanatory sentences in another language.
- Use EARS as a semantic discipline, not fixed English syntax: state the trigger or condition and the required system behavior clearly in the user's language. Do not force `WHEN`, `WHILE`, `IF`, `WHERE`, or `THE SYSTEM SHALL` into a non-English sentence.
- Write each acceptance criterion in the user's language with an explicit precondition, action, and observable outcome. Do not force `GIVEN`, `WHEN`, or `THEN` into a non-English sentence.
- On first use in the spec, add a short localized legend: `R` means Requirement (required behavior or constraint), and `AC` means Acceptance Criterion (observable evidence that cited requirements are satisfied).
- Keep only the template's canonical `##` section headings, requirement and acceptance-criterion IDs (`R1`, `AC1`), Status keywords, history tags, and clarification marker prefix unchanged. Localize ordinary body labels such as `Non-goals:` and table column labels.

## Iron Law

```
HARD GATE: NO IMPLEMENTATION SKILL, NO CODE, NO SCAFFOLDING,
NO PROJECT SETUP UNTIL THE USER HAS APPROVED THE SPEC.
```

This applies to every task regardless of perceived simplicity. A todo app, a one-function utility, a config behavior change — all of them. "Simple" is where unexamined assumptions waste the most work.

## When to Use / When NOT

**Use for:** new features, new projects, any behavior change request, unclear requirements, resolving `[NEEDS CLARIFICATION]` markers, and reconciling a spec with what the code actually does.

**Exempt (closed list — nothing else qualifies):**

- typo / comment / formatting-only changes
- dependency bumps with no API change
- CI/tooling config not affecting build outputs
- pure refactors with no observable behavior change AND existing tests pass

Everything else gets a spec. **Scale rule:** a small change gets a small spec — ten lines is fine — but the file exists.

## The Process

Pick the mode first:

| Situation | Mode |
|---|---|
| No spec governs this feature or project yet | **new** |
| A spec exists and the user wants different behavior | **change** |
| The spec contains `[NEEDS CLARIFICATION]` markers | **clarify** |
| Code and spec disagree about existing behavior (brownfield, drift) | **sync** |

If both change and sync seem to apply: sync records what the code already does; change captures new user intent. Run sync first, then change.

Read `references/spec-template.md` in this skill before writing or editing any spec. Create one todo per numbered step of your mode and complete them in order.

The Spec Language rules apply in every mode, including deltas, clarification rewrites, drift records, and reconciliation outcomes. Never treat an existing spec's language as permission to continue in a language that differs from the user's language; surface the mismatch and bring its human-readable content into the user's language as part of the spec edit.

### Mode: new

1. **Explore context** — files, docs, recent commits. If the request spans multiple independent subsystems, decompose first: agree on the sub-projects and their order, then spec the first one.
2. **Ask clarifying questions** — ONE question per message. Prefer multiple choice. Focus on purpose, constraints, success criteria. Flag anything still ambiguous inline as `[NEEDS CLARIFICATION: question]` instead of guessing.
3. **Propose 2–3 approaches** — with trade-offs; lead with your recommendation and why.
4. **Write the spec** — from the template, to `docs/specs/NNN-<slug>/spec.md`, `Status: draft`, following the Spec Language rules above. Mermaid fences go in Behavior & Flows; they are the single diagram source (the forge spec-viewer skill lifts them verbatim).
5. **Self-review** — language compliance (all explanations use the user's language; EARS and acceptance criteria read naturally in that language; established original-language terms remain intact), placeholder scan (TBD, TODO, vague phrasing), internal consistency (do sections contradict each other?), ambiguity (any requirement readable two ways → fix or mark), scope (one plan's worth of work, or decompose). Fix inline.
6. **User approval gate** — ask the user to review the spec file (offer the forge spec-viewer skill for a rendered view). Wait for the answer. Only the user can approve.
7. **On approval** — set `Status: approved` (requires zero `[NEEDS CLARIFICATION]` markers) and log the approval in Decisions & History.

### Mode: change

1. **Locate the governing spec** in `docs/specs/`. If none exists, switch to new mode.
2. **Draft the delta** — mark each affected requirement `MODIFIED` or `REMOVED`, add new R-IDs for `ADDED` requirements (never renumber or reuse IDs), and update the affected flows, interfaces, and ACs. Set `Status: draft`.
3. **Record the delta** in Decisions & History: `- YYYY-MM-DD [CHANGE] R3 MODIFIED: ...`.
4. **User approval gate** — same as new mode; on approval set `Status: approved`.
5. **Hand off** to the forge writing-plans skill.

Never patch the code first and back-fill the spec. The change request edits the spec; the code follows the plan.

### Mode: clarify

1. **Enumerate** every `[NEEDS CLARIFICATION]` marker in the spec.
2. **Resolve each one** — one question per message, multiple choice preferred.
3. **Rewrite** the requirement with the answer, delete the marker, log a `[CLARIFIED]` entry in Decisions & History.
4. **Zero markers** is a precondition for `Status: approved`. While any marker remains, the spec stays draft.

### Mode: sync

1. **Read the code** the spec claims to cover and note its actual behavior. Keep investigation notes in `.forge/research/` when the dig is non-trivial.
2. **Diff** actual behavior against each requirement.
3. **Append each mismatch** to Decisions & History with a `[DRIFT]` tag. Do not silently rewrite requirements.
4. **Propose reconciliation per item** — either a spec change (accept what the code does) or a code fix (restore what the spec says). The user decides each item; never both silently.
5. **Apply the outcomes** — approved spec changes are edited in with `[CHANGE]` entries; code fixes go through the forge writing-plans skill.

## Working Files

| Artifact | Path | Committed |
|---|---|---|
| Spec — source of truth | `docs/specs/NNN-<slug>/spec.md` | yes |
| Investigation notes (new/sync exploration) | `.forge/research/YYYY-MM-DD-<slug>.md` | yes |
| Rendered viewer (via the forge spec-viewer skill) | `.forge/viewer/NNN-<slug>.html` | no |

Numbering: `NNN` is the next unused three-digit number in `docs/specs/` (001, 002, …); the directory is `docs/specs/NNN-<slug>/` with the fixed filename `spec.md`. Change, clarify, and sync reuse the existing spec's number.

## Red Flags

| Excuse | Reality |
|---|---|
| "The change is too small for a spec." | Small change = small spec. Ten lines is fine. Only the closed exemption list skips the file. |
| "I'll spec it after coding." | A back-filled spec documents what you built, not what was needed. Spec first is the entire point. |
| "The user seems in a hurry." | Rework from one wrong assumption costs more than five minutes of questions. Speed comes through the gate, not around it. |
| "The requirements are obvious." | Obvious means unexamined. Ambiguity hides inside "obvious" — write it down and let the user confirm. |
| "The user already told me exactly what to build." | Then the spec takes minutes and approval is instant. Writing it makes the intent checkable. |
| "I'll just scaffold the project while we talk." | Scaffolding is implementation. The hard gate covers it. |
| "One [NEEDS CLARIFICATION] marker won't block approval." | Approved requires zero markers. An unresolved marker is an unwritten requirement. |
| "It's just a prototype / throwaway experiment." | Prototypes ship. If it changes observable behavior, it gets a spec — only the closed exemption list skips one. |
| "The user liked my recommended approach — that counts as approval." | Approval applies to the written spec file the user reviewed, never to a chat summary of an approach. Until the user approves the file, the gate holds. |
| "English is clearer for technical specs." | The user's language is required for every explanation. Preserve only established original-language terms and the fixed traceability and lifecycle tokens. |
| "A few untranslated sentences are fine because they contain technical terms." | Preserve the terms, not the surrounding prose. Explain them in the user's language. |
| "EARS and Given/When/Then must stay English for downstream automation." | Downstream skills trace `R-ID` and `AC-ID`; they do not parse those English words. Preserve the semantics and write the sentences in the user's language. |
| "Labels copied from the English template should stay English." | Only canonical `##` headings and fixed traceability and lifecycle tokens stay unchanged. Localize body and table labels such as `Non-goals:`. |

## Handoff

**Spec approved. The next step is the forge writing-plans skill — do not start coding directly.**

Exception: if the mode was clarify, the spec is now marker-free but still draft — offer it for the user approval gate and stop; planning and coding stay gated until the user approves. If sync ended with spec-only changes, there is nothing to build — report the updated spec to the user and stop.
