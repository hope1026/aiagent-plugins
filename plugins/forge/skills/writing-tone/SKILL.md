---
name: writing-tone
description: 'Use when writing or editing human-readable replies, progress reports, technical explanations, documentation, Spec or Plan views, README, PR descriptions, commit messages, error messages, UI copy, Slack messages, emails or reports in any language. Triggers: "답변", "기술 설명", "스펙 뷰어", "플랜 뷰어", "톤앤매너", "말투", "자연스럽게", "사람처럼", "AI스럽지 않게", "문서", "메시지 작성", "리드미", drafting or reviewing prose.'
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

1. **Use active voice when the actor is known.** "The build failed" — not "a failure was experienced by the build". Preserve uncertainty about an unknown actor.
2. **Prefer direct positive wording when it preserves meaning.** "The cache is stale" is clear. Keep explicit prohibitions, negative conditions and failures when they define the behavior.
3. **Use definite, specific, concrete language.** "Makes at most 3 total attempts within 30s" beats "retries a few times for a while".
4. **Omit needless words.** "the fact that", "in order to", "it should be noted that" — delete.
5. **Remove AI-like filler.** Skip stock openings, exaggerated praise, generic reassurance, and sign-offs that add no useful information.

Above all: **lead with the point** — decision, result, or ask first; background after.

Accuracy and preserved source meaning take priority over brevity, positive wording and stylistic variation.

## Clear technical explanations

Apply these principles to technical replies, progress reports, documents and requested Spec or Plan views. They adapt useful clarity principles from ASD-STE100; they do not establish compliance with that controlled English standard, particularly in Korean. Keep the purpose-specific voice of marketing and operations copy.

- State concrete actors, actions, conditions and results where they matter. Use active voice when the actor is known; preserve uncertainty when it is unknown.
- Give each sentence one main point and keep related sentences connected. Put a condition before an instruction when the reader needs it before acting. Explain causes, dependencies and rationale rather than reducing everything to disconnected commands.
- Use familiar words while preserving precise technical terms. Explain an unfamiliar term at first use. For naming decisions and definition ownership, use the forge using-forge skill's terminology guidance; reuse the resulting terms consistently rather than varying them for style.
- Shortening or simplifying prose must preserve exceptions, prohibitions, failure cases, quantities, units, uncertainty and obligation levels. Distinguish required behavior, permitted behavior and observed results. Keep exact identifiers, protocol values and quotations intact.

For example, replace "A robust retry mechanism guarantees consistency" with the actual behavior: "If the request times out, the client retries with the same request ID. While the stored result remains available, the server returns it without repeating the charge." Those conditions are illustrative, not a contract for other systems.

Sources: [ASD-STE100 overview](https://www.asd-ste100.org/about.html) and [official FAQ](https://www.asd-ste100.org/STE_faq.html). Use the principles that improve understanding, without importing its full dictionary, English word-count limits or a compulsory document layout.

## The Process

1. Decide the scope: substantial prose (documentation, README, reports, multi-paragraph PR descriptions) or a short message (Slack reply, commit message, brief comment).
2. Use references/style-rules.md when substantial prose or house voice needs its examples. Short messages can use the core rules directly. Use part 2 for Korean house voice when needed and reuse it while available.
3. Draft, leading with the point.
4. Cut pass: delete hedges, filler, and anything the reader does not need in order to act.
5. Read once as the reader: is the ask explicit — who does what, by when, and what happens next?

## Review Surface Copy

For requested Visual Docs:

- Choose titles that help the reader find the answer; a question or a concrete descriptive label can work.
- State what to confirm before background or source detail.
- Add a reading guide when a diagram needs context.
- Use the user's language for labels whose meaning survives translation. Preserve established API, service, schema, protocol, and code identifiers in their original form.
- Order content around the reader's question. Put source detail where it supports verification without interrupting the explanation; no fixed section order or mandatory diagram is required.
- Prefer concrete actor, responsibility, state, count, and verification wording over abstract labels such as "Architecture Overview".

For substantial prose, reuse the work checklist for drafting and review. For short messages, edit directly; keep the cut pass internal and return the requested text without process narration.


## When NOT to Use

Code, configuration, lockfiles, generated output, machine-parsed formats — anything no human reads as prose.

## Working Files

This skill creates no artifacts in the forge working directory `.forge/` — the prose lands where it belongs: docs, specs under docs/specs/, PR bodies, messages. Drafts that should not be committed go to `.forge/scratch/` (gitignored).
