---
name: ui-design
description: 'Use when a caller explicitly invokes the legacy Forge ui-design skill or an older workflow names it and the request must be handed to the replacement web UI skill. Triggers: explicit "ui-design", legacy Forge UI skill references, 오래된 ui-design 호출.'
---

# UI Design Compatibility Router

Announce at start: "The forge ui-design skill is DEPRECATED; I am classifying this surface and handing it to its active replacement."

Respond to the user in the user's language. This skill file stays in English.

## Overview

This is a one-release compatibility entry point for explicit legacy calls. It preserves old prompts long enough to classify their surface, then hands the work to one active skill. It contains no visual design procedure.

## Iron Law

```text
CLASSIFY AND HAND OFF. DO NOT DESIGN.
NEVER WRITE A VISUAL SYSTEM, CSS, OR UI IMPLEMENTATION FROM THIS SKILL.
NEVER ROUTE A NATIVE APP TO A WEB SKILL.
```

## When to Use / When NOT

Use only when the caller explicitly names `ui-design` or an older Forge workflow invokes it.

Do NOT select this skill for a new general UI request. The forge using-forge skill routes new work directly to an active skill.

## The Process

Create one checklist item per numbered step before classifying the surface.

1. Tell the user once that `ui-design` is deprecated and will be removed after the compatibility period.
2. Classify the requested surface:
   - browser or PWA dashboard, admin, settings, table, form, control, internal tool, or authenticated workflow → hand off to the forge web-app-design skill;
   - public landing page, homepage, marketing or product site, editorial site, portfolio, or public documentation → hand off to the forge website-design skill;
   - one approved Task changing separately owned application and public website files → name both file groups and hand each group to its matching skill;
   - native mobile or desktop app → explain that this compatibility router has no active native replacement and do not force it into a web skill;
   - insufficient context → ask one question: "Is this a stateful browser application or a public content website?"
3. Stop using this skill after the handoff. The selected active skill owns every design declaration, implementation rule, and browser check.

## Red Flags

| Excuse | Reality |
|---|---|
| "The old skill already has useful visual rules." | Compatibility means routing old callers, not preserving a second competing design process. |
| "I can start the CSS while deciding the replacement." | DO NOT DESIGN. Classification completes before any UI work. |
| "Using both replacements is safer." | One surface gets one owner; use both only for separately owned app and website files in the same approved Task. |
| "Electron is web technology, so web-app-design is close enough." | Runtime technology does not make a native desktop product a browser application. |
| "The request is vague, so loading both active skills is safer." | Ask one classification question, then hand off to exactly one active skill. |

## Handoff

The selected active replacement owns the task immediately. This compatibility router performs no later verification or completion claim.
