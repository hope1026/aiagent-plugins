---
name: website-design
description: 'Use when designing, implementing, or reviewing public websites such as landing pages, homepages, marketing sites, product pages, editorial sites, portfolios, and public documentation sites. Triggers: "웹사이트", "랜딩 페이지", "홈페이지", "마케팅 사이트", "제품 페이지", "포트폴리오", "public docs", "website redesign".'
---

# Website Design

Announce at start: "Using the forge website-design skill to declare the website thesis and content composition before writing UI code."

Respond to the user in the user's language. This skill file stays in English.

## Overview

A public website communicates a story, establishes trust, and guides a visitor toward a next action. Its design begins with content hierarchy and a distinct visual thesis, then uses typography, imagery, composition, and restrained motion to make that thesis visible.

## Iron Law

```text
NO WEBSITE UI CODE BEFORE THE VISUAL THESIS AND CONTENT HIERARCHY ARE DECLARED.
ONE CLEAR VISUAL IDEA, ONE PRIMARY ACTION, AND ONE COHERENT SYSTEM.
REAL RESPONSIVE COMPOSITION IS REQUIRED; A SHRUNK DESKTOP IS NOT MOBILE DESIGN.
```

## When to Use / When NOT

Use for public landing pages, homepages, marketing and product sites, editorial sites, portfolios, campaign pages, and public documentation sites.

Do NOT use for:

- authenticated dashboards, settings, operational tables, admin panels, or SaaS workflows — use the forge web-app-design skill;
- native mobile or desktop app interfaces;
- fixed Review Viewer generation;
- Review Viewer tooling, which is a browser application review surface owned by `web-app-design`;
- a content-only copy change with no visual or layout decision.

## The Process

Create one todo per numbered step before changing UI code.

### Step 1 — Read product and content truth

Read the current plan Task and every Related Spec. Inspect the existing brand, type, color, imagery, components, performance budget, analytics goal, and page content. Preserve established tokens unless the approved spec requires a new direction.

### Step 2 — Define the visitor journey

State:

- the primary audience and their starting context;
- the one primary action;
- the page promise and proof needed before that action;
- the content sequence from first viewport to final decision;
- whether any authenticated application surface must be separated into files owned by the forge web-app-design skill.

### Step 3 — Declare the website system

Post this completed block to the user before UI code:

```text
WEBSITE SYSTEM — public content surface
Visual thesis: <one specific visual idea that expresses this product>
Audience and action: <visitor context and one primary action>
Content hierarchy: <ordered story from promise through proof to action>
Typography: <display, body, utility roles and why they fit the thesis>
Palette: <dominant field, supporting color, and one accent>
Spacing: <base unit and section rhythm>
Depth: <one primary separation strategy>
Imagery: <photography, illustration, product media, or an intentional non-image anchor>
Responsive composition: <desktop and mobile hierarchy, crop, stacking, and reading order>
Motion: <purpose, trigger, duration, and reduced-motion behavior>
```

Rules:

- The Visual thesis must be specific enough that it could not label an unrelated company.
- Content hierarchy comes before decorative sections. Every section must advance the visitor from promise to proof or action.
- Continuous body copy stays at least 16px with a readable line length and contrast.
- Imagery must carry meaning, proof, atmosphere, or product understanding. Do not use abstract decoration as a fake product screenshot.
- Use one accent and one dominant visual gesture. Repeating large type, saturated color, gradients, floating cards, and motion as simultaneous focal points creates noise.
- Motion is restrained, optional, and subordinate to reading. Respect reduced motion and avoid `transition: all`.

### Step 4 — Compose desktop and mobile deliberately

Define the first viewport, section rhythm, image crops, reading order, action placement, and navigation behavior at desktop and mobile widths. Mobile may reorder or remove decorative content, but it must preserve the promise, proof, and primary action.

Do not apply browser app table geometry or dense operational state matrices to a public website. Interactive forms still need keyboard, focus, error, loading, and success states appropriate to the form.

### Step 5 — Implement with accessible, performant media

Use semantic landmarks and heading order. Provide visible focus, labels, alt decisions, sufficient contrast, responsive image sources, explicit media dimensions, and lazy loading below the fold. Avoid layout shifts and assets whose cost is not justified by the visual thesis.

### Step 6 — Verify the rendered website

Use a real browser at desktop and mobile widths. Confirm:

- first-viewport promise, visual anchor, and primary action remain legible;
- heading hierarchy and reading order match the content plan;
- imagery crops intentionally and does not shift layout;
- body copy remains readable and no horizontal overflow appears;
- keyboard focus, form states, reduced motion, and semantic structure work;
- performance-sensitive media and motion stay within the declared budget.

Rendered output is the evidence. If a real browser or performance inspection is unavailable, report the missing verification instead of claiming completion.

## Red Flags

| Excuse | Reality |
|---|---|
| "A clean modern website is the thesis." | That phrase fits every product and therefore directs nothing. |
| "The hero can explain everything." | A first viewport needs one promise, a visual anchor, and one next action. |
| "More sections make the product look substantial." | Sections without a job dilute the story. |
| "A gradient, oversized type, floating cards, and motion will make it memorable." | One dominant gesture is memorable; four gestures compete. |
| "Mobile can stack the desktop layout." | Mobile composition needs its own hierarchy, crops, and action placement. |
| "The asset looks good, so its weight is acceptable." | Visual value must justify performance cost and layout stability. |

## Handoff

- Authenticated browser application surface discovered during the task → isolate its owned files and use the forge web-app-design skill for that surface only.
- Marketing or product copy changes → use the forge writing-tone skill with the forge marketing-tone skill.
- Claiming completion → return to the forge executing-plans skill, then use the forge verifying-work skill against the approved acceptance criteria.
