---
name: ui-design
description: 'Use when designing or implementing any user interface - web pages, components, dashboards, HTML artifacts, slides - or reviewing UI work. Triggers: "UI", "디자인", "화면", "예쁘게", "프론트", "landing page", "component", CSS/styling work.'
---

# UI Design

Announce at start: "Using the forge ui-design skill to declare the visual system before writing UI code."

Respond to the user in the user's language. This skill file stays in English; the visual system you declare and everything you say to the user follow their language.

## Overview

Undesigned UI is not neutral — it converges on the same recognizable defaults every model produces. The cure is to make every visual choice deliberate: declare the system first, state a WHY for each decision, then build inside it. Same craft everywhere; only the treatment changes with the context.

## Iron Law

```
NO UI CODE BEFORE THE VISUAL SYSTEM IS DECLARED.
EVERY CHOICE HAS A WHY. NO WHY = YOU ARE DEFAULTING.
```

If you cannot explain why a font, color, radius, or shadow is there, stop — you're defaulting.

## When to Use

- Building or restyling any web page, component, dashboard, HTML artifact, or slide deck.
- Reviewing UI work — walk the same checkpoints against the existing code.
- UI tasks inside a plan executed with the forge executing-plans skill.

## When NOT to Use

- Pure logic changes with zero visual surface (API handlers, data pipelines).
- Terminal-only output with no markup or styling decisions.

## The Process

Turn the steps below into todos — create one todo per step (and one per checkpoint field in Step 2) before writing any UI code.

### Step 0 — Effort calibration

Classify the work before anything else:

| Class | Examples | Treatment |
|---|---|---|
| **Utilitarian** | docs, admin panels, internal tools, debug views | Restraint: quiet palette, dense-but-breathing layout, zero decoration that slows scanning |
| **Editorial** | landing pages, marketing, showcases, portfolio pieces | Expression: distinctive type, confident color, one memorable moment |

Same craft, different treatment. Utilitarian is a treatment, not an exemption — a plain admin table still gets a declared type scale and palette.

### Step 1 — Read the context

If this UI belongs to planned work, read the Task in `docs/plans/PPP-slug/plan.md` or `tasks/*.md` and every Related Spec first. Related requirements and acceptance criteria bound what the UI must do; this skill governs how it looks.

### Step 2 — MANDATORY pre-code checkpoint: declare the visual system

Before any UI code, post this block visibly to the user (in their language) and fill every field.

This applies to existing codebases too: an existing design system does not skip the checkpoint — read the project's actual tokens and styles first, fill the block from them, and mark each field as inherited. Extending a UI whose system you never read is still defaulting.

**Fixed Viewer shell exception:** when a document Viewer ships a fixed, already-reviewed shell, declare Type, Palette, Spacing, and Depth as `inherited` after reading the actual template. Fragment authors add no CSS, script, doctype, head, or shell markup. The Signature comes from content structure such as Route Map, Runtime Atlas, and AC Coverage, not from decorative styling added by the fragment.

```
VISUAL SYSTEM — <what you are building>
Intent:    <one sentence, evocative not generic — "confident lab equipment", never "clean and modern">
Type:      <base size>px base, scale ratio <1.2–1.333> — weight and color do hierarchy work before size does
Palette:   60/30/10 — 60% <neutral> / 30% <secondary> / 10% <accent>; greys carry a hue bias toward the accent
Spacing:   <N>px base unit — one density decision, stated in px, applied everywhere
Depth:     <borders OR shadows OR layering> — pick ONE strategy and commit
Signature: <one element another AI would not produce>
```

Rules for the block:

- **Intent** — one sentence. If it could caption any product, rewrite it.
- **Type scale** — ratio between 1.2 and 1.333. Reach for weight and color to build hierarchy before reaching for size.
- **Palette** — 60/30/10 neutral/secondary/accent. Never pure `#808080`-style greys: bias them toward the accent hue.
- **Spacing** — one density decision in px; every gap derives from it.
- **Depth** — borders OR shadows OR layering. Mixing all three is the tell of no decision.
- **Signature** — name the one distinctive element. No signature, no ship.

If you can't explain why, stop — you're defaulting.

### Step 3 — Build within hard floors

These are floors, not preferences. Violating any of them is a defect:

- Hit targets ≥ 44px.
- Body text ≥ 16px on web, ≥ 24px on slides.
- Motion under 300ms, animating `transform`/`opacity` only; never `transition: all`.
- Tabular numbers (`font-variant-numeric: tabular-nums`) for any value that changes — timers, counters, prices, table columns.
- Layout spacing via flexbox/grid `gap`, not per-element margins.

**Spend your boldness in one place.** One oversized headline, one saturated accent, or one unusual layout move — chosen deliberately. Two or more competing bold moves cancel each other into noise.

### Step 4 — Check the anti-slop ban list

None of these may appear without a written justification in the visual system block:

1. **Default-font laziness** — Inter or Roboto without a stated reason.
2. **Purple-gradient-on-white** hero sections.
3. **Cream + terracotta "AI palette."**
4. **`rounded-lg` on everything** — one radius token slapped on every element.
5. **Emoji as section markers.**
6. **Rounded-card-with-left-border** as the universal callout.
7. **Centered-everything** layouts.
8. **CSS silhouettes faking product shots** — abstract shapes pretending to be screenshots.

### Step 5 — Self-tests before presenting

Run all four; failing any one means revise before showing the user:

- **Swap test** — would this design work for any product? Then it's not designed.
- **Squint test** — blur your eyes (or scale to 25%): is the hierarchy still visible?
- **Signature test** — point to the distinctive element. If you can't, there isn't one.
- **Token test** — read the CSS variable names aloud. `--primary`, `--gray-500` evoke nothing; do the names evoke this product?

### Step 6 — Verify in a real browser when possible

Rendered output is the only truth. Open the page or artifact, check the layout at desktop and mobile widths, and confirm the hard floors survived the build. If a browser genuinely isn't available, say so explicitly instead of claiming it looks right.

For document Viewers, verify both 1440px desktop and 390px mobile. A diagram is a complete review unit only when it includes a title, what to confirm, a one-sentence reading guide, and a mobile fallback summary. Wide sequence and dependency diagrams stay readable through an independent horizontal scroll region; if their text is still difficult to interpret at 390px, place a responsibility summary table or source-derived vertical flow before them.

## Working Files

| Path | Direction | Purpose |
|---|---|---|
| `docs/specs/NNN-slug/spec.md` | read | Requirements and acceptance criteria the UI must satisfy |
| `docs/plans/PPP-slug/plan.md` | read | The plan task this UI work belongs to, if any |
| `.forge/scratch/` | write (optional, gitignored) | Design explorations and comparison notes that shouldn't be committed |

## Red Flags

| Excuse | Reality |
|---|---|
| "It's just an internal tool, styling doesn't matter" | Utilitarian is a treatment with its own declared system, not an exemption from having one. |
| "I'll pick colors and fonts as I code" | Choosing mid-build means defaulting. The checkpoint exists because in-flight choices converge on slop. |
| "Inter is the safe choice" | Safe for whom? Unjustified defaults are the #1 tell of undesigned UI. State a reason or pick deliberately. |
| "A gradient here AND big type there will make it pop" | Boldness spent twice is boldness cancelled. One place. |
| "It looks right in my head" | Heads don't render CSS. Verify in a real browser or say you couldn't. |
| "The checkpoint block is ceremony slowing me down" | The block takes two minutes and prevents the full rewrite that follows a slop first draft. |
| "The user said 'make it pretty', they don't care about a system" | "Pretty" without a system produces the same page every model produces. The system is how it becomes pretty. |
| "The codebase already has a design system, no checkpoint needed" | Then the checkpoint takes one minute: read the tokens and restate them as inherited. If you can't fill the block from the code, you never knew the system you claim to follow. |
| "It's a one-line CSS tweak, not real UI work" | One line chosen outside the system is how drift starts. Name the system rule the tweak follows — that IS the checkpoint for a tweak. |
| "The fixed Viewer shell means the fragment can add one special style." | Fragment CSS creates mode-specific drift. Keep shell decisions inherited and create distinctiveness through source structure. |
| "The diagram exists, so mobile users can zoom it." | A diagram without a reading guide and mobile summary transfers interpretation work to the reviewer. Package all four parts and verify at 390px. |

## Handoff

- UI work done inside a plan task → return to the forge executing-plans skill to continue the plan.
- Claiming the UI is done, fixed, or matching the spec → use the forge verifying-work skill; walk the acceptance criteria with evidence.
- Writing UI copy, labels, empty states, or error messages → use the forge writing-tone skill.
