---
name: operations-tone
description: 'Use when writing or revising customer support, operations updates, incident replies, GitHub issue responses, support emails, bug status notices, release/update replies, or service status messages that should sound trustworthy and clear. Triggers: "운영", "고객 답변", "고객 응대", "지원 답변", "이슈 답변", "장애 안내", "수정 예정", support reply, incident update, customer response.'
---

# Operations Tone

Announce once when first applied: "Using the forge operations-tone skill to shape customer and operations communication."

Respond to the user in the user's language. This skill is an overlay on top of the forge writing-tone skill.

## Overview

Operations communication should reduce uncertainty for the customer. The default is not a root-cause report; the default is confirmed status, customer impact, action plan, customer action required, and the next update condition. The base prose rules come from the forge writing-tone skill; this skill adds customer trust and support discipline.

## Iron Law

```
STATUS AND NEXT ACTION FIRST. DO NOT EXPLAIN CAUSE DETAILS UNTIL THEY HELP THE CUSTOMER.
```

## Core Rules

Apply the forge writing-tone skill first, then apply these rules:

1. **Lead with confirmed status.** Say whether the issue is confirmed, fixed, under review, needs information, or not reproduced.
2. **State customer impact in plain language.** Translate technical details into what the customer sees or needs to do.
3. **Give the action plan.** Say whether a fix is planned, in progress, released, or blocked on missing information.
4. **Name customer action.** If there is nothing for the customer to do, say that directly.
5. **Set the next update condition when known.** Use an actual commitment; do not invent a follow-up, date, or service promise to fill the template.
6. **Keep cause detail conditional.** Include root cause only when requested, confirmed, safe to share, and useful for customer action.
7. **Avoid customer blame.** Describe states and actions, not fault.

## The Process

1. Classify the reply: confirmed issue, fix planned, fix released, needs information, cannot reproduce, billing/account handoff, or general usage guidance.
2. Choose the status sentence before writing anything else.
3. Add customer impact and current action in one short paragraph.
4. Add customer action: no action needed, restart/update/check version, provide logs, email support, or wait for the next update.
5. Decide whether cause detail is allowed. If not, leave it out.
6. Apply the forge writing-tone cut pass: remove hedges, internal process detail, generic apologies, and unnecessary technical depth.

For substantial replies, reuse the work checklist. For short replies, check status, customer action, and cause detail internally; return the requested message without process narration.

## Default Shapes

Confirmed issue, fix planned:

```text
The issue has been confirmed. We are preparing a fix, and no action is needed on your side right now.

We will update this thread once the fix is available. If a temporary workaround is confirmed before then, we will share it here as well.
```

Fix released:

```text
This has been fixed in <version or update>. Please restart <product/client> and check that you are on <version or later>.

If the same issue still appears after that, please send <specific info> so we can continue investigating.
```

Needs information:

```text
We need one more detail to investigate this.

Could you send <specific log/screenshot/version>? Once we have that, we can check the failing step directly.
```

Not reproduced:

```text
We checked the same scenario but could not reproduce it yet.

Please send <specific reproduction detail>. We will keep the issue open while we verify the missing case.
```

## Cause Detail Gate

Include cause detail only when all conditions are true:

- The customer asked why, or the cause changes what the customer should do.
- The cause is confirmed, not guessed.
- The explanation is safe to share publicly or with that customer.
- The explanation can be stated in customer language without exposing internals.

If any condition fails, use status language instead:

- `The issue has been confirmed.`
- `We are preparing a fix.`
- `No action is needed on your side right now.`
- `We need one more detail to reproduce this.`
- `The fix is available in <version> or later.`

## When NOT to Use

Do not use this skill for marketing copy, sales pages, or launch posts. Use the forge marketing-tone skill for product promotion. Do not use this skill as a substitute for investigation; it shapes the reply after the status is known.

## Working Files

This skill creates no Forge artifacts. Put the finished reply where the user requested: issue comments, support emails, Slack updates, status pages, release replies, or message drafts.

## Red Flags

| Excuse | Reality |
|---|---|
| "A detailed cause explanation sounds transparent" | Extra internals can confuse customers and create unsupported commitments. |
| "We should explain everything we know" | Customers need status, action, and next update first. |
| "The cause is probably obvious" | Probable is not confirmed. Mark it as an estimate or leave it out. |
| "No action needed is implied" | Say it directly so the customer can stop troubleshooting. |
| "Technical accuracy requires technical detail" | Translate technical detail into customer impact unless the customer asked for internals. |
| "A long apology builds trust" | Concrete action builds trust. Apologize only when it is warranted. |

## Handoff

**Operations reply delivered. Return to the workflow that needed it; if the reply claims a fix is complete, run the forge verifying-work skill first.**
