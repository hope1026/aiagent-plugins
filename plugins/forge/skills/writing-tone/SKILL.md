---
name: writing-tone
description: 'Use when writing or editing anything humans will read - natural, human-readable prose without AI-like filler; documentation, README, PR descriptions, commit messages, error messages, UI copy, Slack messages, emails, reports - in any language, especially Korean technical communication. Triggers: "톤앤매너", "말투", "자연스럽게", "사람처럼", "AI스럽지 않게", "문서", "메시지 작성", "리드미", drafting or reviewing prose.'
---

# Writing Tone

Announce at start: "Using the forge writing-tone skill to shape this prose."

Respond to the user in the user's language. These rules govern whatever language the deliverable is written in.

## Overview

Prose that humans read is a deliverable, not an afterthought. Vigorous writing is concise: every sentence carries information the reader needs, in the order the reader needs it. This is the base tone skill for natural, human-readable writing; purpose-specific skills such as marketing or operations tone may layer on top of it.

## Iron Law

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
2. Substantial prose: read references/style-rules.md BEFORE drafting. Short messages: apply the core rules directly — except Korean output, where you read part 2 of the reference first, for every message, at any length.
3. Draft, leading with the point.
4. Cut pass: delete hedges, filler, and anything the reader does not need in order to act.
5. Read once as the reader: is the ask explicit — who does what, by when, and what happens next?

For substantial prose, create one todo per step of this checklist. For short messages, still run steps 3–5 — the cut pass is never optional.

## Limited-Context Strategy

If the reference will not fit in the remaining context: draft with the core rules and your judgment, then dispatch a subagent with the draft plus references/style-rules.md to copyedit against the rules. If no subagent capability is available, re-read only part 2 of the reference for Korean output and edit the draft yourself. Never skip both.

## When NOT to Use

Code, configuration, lockfiles, generated output, machine-parsed formats — anything no human reads as prose.

## Working Files

This skill creates no artifacts in the forge working directory `.forge/` — the prose lands where it belongs: docs, specs under docs/specs/, PR bodies, messages. Drafts that should not be committed go to `.forge/scratch/` (gitignored).

## Red Flags

| Excuse | Reality |
|---|---|
| "It's just a quick Slack message" | Short messages are read the most. The core rules take seconds to apply. |
| "More detail looks more thorough" | Padding buries the point. The reader pays for every needless word. |
| "Hedging sounds polite" | False uncertainty hides real risk. State evidence, remaining risk, and next action. |
| "The reader will figure out what I need" | Implicit asks stall. Say who does what, by when, and what happens next. |
| "I'll polish it after it ships" | Readers act on the first version they see. Edit before sending. |
| "Reading the reference is overkill here" | For substantial prose it is the difference between designed and default — and it is short. |
| "My default writing is already clear" | Unedited drafts hedge and pad. These rules exist because default output reads as default. |
| "I know Korean; I don't need part 2" | Part 2 encodes house voice and message shapes, not grammar. Fluency is not the standard — the shapes are. |

## Handoff

**Prose delivered. Return to the workflow that needed it; if the text claims work is complete, run the forge verifying-work skill first.**
