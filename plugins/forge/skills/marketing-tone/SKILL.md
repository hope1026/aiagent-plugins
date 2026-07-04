---
name: marketing-tone
description: 'Use when writing or revising marketing, product, landing page, launch, campaign, social, sales, or positioning copy that should sound confident, factual, and trustworthy. Triggers: "마케팅", "랜딩페이지", "제품 소개", "카피", "캠페인", "SNS", "출시", "프로모션", marketing copy, product copy, launch copy.'
---

# Marketing Tone

Announce at start: "Using the forge marketing-tone skill to shape product and marketing copy."

Respond to the user in the user's language. This skill is an overlay on top of the forge writing-tone skill.

## Overview

Marketing copy should make a product easier to trust, not louder. Use a confident voice only when the claim is supported by product facts, observed usage, a concrete workflow, or a clear limitation. The base prose rules come from the forge writing-tone skill; this skill adds product positioning and claim discipline.

## Iron Law

```
CONFIDENCE COMES FROM FACTS. CUT HYPE THAT THE PRODUCT CANNOT PROVE.
```

## Core Rules

Apply the forge writing-tone skill first, then apply these rules:

1. **Lead with the useful promise.** State what the product helps the reader do.
2. **Anchor trust in evidence.** Use features, workflow steps, integrations, metrics, demos, constraints, or customer-observable outcomes.
3. **Make the claim specific.** "Syncs changes back to Roblox Studio" beats "improves your workflow".
4. **Use confident but bounded language.** Prefer `designed for`, `helps`, `supports`, `lets you`, and `built to`.
5. **Avoid unsupported superiority.** Do not say `best`, `only`, `perfect`, `guaranteed`, or `fully automated` unless the evidence is explicit.
6. **Keep the reader's job in view.** Show the problem, the product action, and what the reader can verify.

## The Process

1. Identify the reader and the surface: landing page, launch post, short social copy, email, ad, product page, or release note.
2. Extract the usable facts: product name, concrete feature, proof point, demo context, metric, limitation, and CTA.
3. Draft in this order: reader problem, product action, proof or visible result, next step.
4. Run a claim audit: mark each strong claim as `proven`, `supported`, `assumed`, or `unsupported`.
5. Rewrite or delete every `assumed` or `unsupported` claim.
6. Apply the forge writing-tone cut pass: remove filler, generic excitement, and stock marketing phrases.

For substantial copy, create one todo per step. For short posts, still run the claim audit before returning the copy.

## Patterns

Trust-building shape:

```text
<Product> helps <reader> do <specific job>.
It works by <concrete mechanism or workflow>.
You can verify it through <observable result>.
<CTA>.
```

Product update shape:

```text
<Feature/update> is now available.
It changes <specific workflow> by <specific product action>.
This matters when <reader situation>.
Try it from <place/link/action>.
```

## When NOT to Use

Do not use this skill for neutral docs, internal status updates, code comments, or customer support replies unless the user explicitly asks for marketing copy. Use the forge operations-tone skill for customer-facing support or incident updates.

## Working Files

This skill creates no Forge artifacts. Put the finished copy where the user requested: docs, product pages, posts, emails, launch notes, or message drafts.

## Red Flags

| Excuse | Reality |
|---|---|
| "Marketing should sound more impressive" | Trust comes from specific evidence, not inflated adjectives. |
| "Everyone says best-in-class" | Generic superiority claims are forgettable and risky without proof. |
| "The reader will infer the value" | State the product action and visible result directly. |
| "A broad promise fits more audiences" | Broad copy fits no one. Name the reader and job. |
| "The limitation weakens the message" | Clear boundaries make the confident parts more believable. |
| "This is just a short post" | Short copy still needs a claim audit. |

## Handoff

**Marketing copy delivered. Return to the workflow that needed it; if the copy claims work is complete, run the forge verifying-work skill first.**
