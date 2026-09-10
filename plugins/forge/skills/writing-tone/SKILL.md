---
name: writing-tone
description: 'Use when writing or editing anything humans will read - natural, human-readable prose without AI-like filler; documentation, README, PR descriptions, commit messages, error messages, UI copy, Slack messages, emails, reports - in any language, especially Korean technical communication. Triggers: "톤앤매너", "말투", "자연스럽게", "사람처럼", "AI스럽지 않게", "문서", "메시지 작성", "리드미", drafting or reviewing prose.'
---

# Writing Tone

Respond to the user in the user's language. These rules govern whatever language the deliverable is written in.

## Overview

Prose that humans read is a deliverable, not an afterthought. Vigorous writing is concise: every sentence carries information the reader needs, in the order the reader needs it. This is the base tone skill for natural, human-readable writing; purpose-specific skills such as marketing or operations tone may layer on top of it.

## Principle

```
LEAD WITH THE POINT. EVERY SENTENCE EARNS ITS PLACE — CUT WHAT THE READER DOES NOT NEED.
```

## Core Rules

Apply these to every sentence, in any language:

1. **Use active voice.** "The build failed" — not "a failure was experienced by the build".
2. **Put statements in positive form.** Say what is, not what is not: "the cache is stale" beats "the cache is not up to date".
3. **Use definite, specific, concrete language.** "Retries 3 times over 30s" beats "retries a few times for a while".
4. **Omit needless words.** "the fact that", "in order to", "it should be noted that" — delete.
5. **Remove AI-like filler.** Skip stock openings, exaggerated praise, generic reassurance, and sign-offs that add no useful information.

Above all: **lead with the point** — decision, result, or ask first; background after.

## The Process

1. Decide the scope: substantial prose (documentation, README, reports, multi-paragraph PR descriptions) or a short message (Slack reply, commit message, brief comment).
2. Use references/style-rules.md when substantial prose or house voice needs its examples. Short messages can use the core rules directly. Use part 2 for Korean house voice when needed and reuse it while available.
3. Draft, leading with the point.
4. Cut pass: delete hedges, filler, and anything the reader does not need in order to act.
5. Read once as the reader: is the ask explicit — who does what, by when, and what happens next?

## Review Surface Copy

For requested Visual Docs:

- Frame the page and diagram title as the question the reviewer wants answered, not as an internal system name.
- State what to confirm before background or source detail.
- Put a one-sentence reading guide immediately before every diagram.
- Use the user's language for labels whose meaning survives translation. Preserve established API, service, schema, protocol, and code identifiers in their original form.
- Order content as summary → visual flow → source detail → acceptance evidence. Keep the full source detail collapsed or later in the reading path when a summary is enough to orient the reader.
- Prefer concrete actor, responsibility, state, count, and verification wording over abstract labels such as "Architecture Overview".

For substantial prose, reuse the work checklist for drafting and review. For short messages, edit directly; keep the cut pass internal and return the requested text without process narration.


## When NOT to Use

Code, configuration, lockfiles, generated output, machine-parsed formats — anything no human reads as prose.

## Working Files

This skill creates no artifacts in the forge working directory `.forge/` — the prose lands where it belongs: docs, specs under docs/specs/, PR bodies, messages. Drafts that should not be committed go to `.forge/scratch/` (gitignored).
