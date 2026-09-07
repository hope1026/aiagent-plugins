---
name: web-app-design
description: 'Use when designing, implementing, or reviewing browser application UI such as dashboards, admin panels, settings, tables, forms, controls, internal tools, SaaS workspaces, and PWAs. Triggers: "대시보드", "관리자 화면", "설정 화면", "웹앱", "PWA", "table UI", "form UI", "control panel".'
---

# Web App Design

Announce once when first applied: "Using the forge web-app-design skill to declare the inherited product UI system and state geometry before writing UI code."

Respond to the user in the user's language. This skill file stays in English.

## Overview

Browser application UI helps a person inspect state and complete work. Its design quality comes from legible task-relevant information, intentional composition, stable geometry, obvious interaction, and complete state coverage. The rendered result must feel visually resolved as one product system, not merely satisfy a component checklist.

## Iron Law

```text
NEW OR STRUCTURAL UI WORK NEEDS A DECLARED SYSTEM AND RELEVANT STATE MATRIX.
FOCUSED ADJUSTMENTS REUSE THE EXISTING SYSTEM AND CHECK THE AFFECTED SURFACE.
SECONDARY CONTENT NEVER OUTRANKS THE PRIMARY TASK.
STATE CHANGES MUST NOT CAUSE UNPLANNED GEOMETRY CHANGES.
RENDERED VISUAL QUALITY AND TASK-RELEVANT INFORMATION MUST BOTH HOLD.
```

## When to Use / When NOT

Use for browser and PWA dashboards, authenticated workspaces, admin panels, settings, tables, forms, filters, controls, and operational tools.

Do NOT use for:

- public landing pages, marketing sites, portfolios, editorial sites, or public content sites — use the forge website-design skill;
- native iOS, Android, React Native, Flutter, desktop, Electron, or Tauri apps — the browser app contract does not own native platform behavior;
- fixed Visual Docs generation — a single requested `visual-docs` build needs no UI design skill;
- logic changes with no visible or interactive surface.

Visual Docs tooling changes use `web-app-design`: shell, component grammar, template, CSS, runtime, interaction, responsive behavior, and accessibility changes require the viewport×state matrix and full rendered verification below.

## The Process

Choose the scope before changing UI code. Reuse the work checklist.

**Focused adjustment:** for one bounded label, spacing, color-role, or component correction that preserves the existing information hierarchy, data relationships, interaction model, and cross-component layout, inspect inherited roles, make the change, and check the affected viewports and actual states. A short goal-and-check update is enough; do not post the full system block or invent loading, disclosure, and mode cases. Test new interaction logic when present.

**New or structural surface:** use the full process below. Treat a change as structural when it changes information exposure or hierarchy, data relationships, the interaction or state model, or layout across components, even when every edited component already exists. If no design system exists, choose a coherent one from product context and established platform conventions; a missing inherited system does not require a new user decision for every token.

### Step 1 — Read product truth

Read the current plan Task when one exists and the governing Spec sections. Then inspect the actual component, design tokens, typography roles, spacing, control states, information architecture, and responsive rules already used by the product. Existing values are inherited unless the approved spec requires a change. Treat examples from another product as evidence for a general design question, never as this product's default structure, terminology, feature set, or numeric target.

### Step 2 — Classify the primary task and interaction

State:

- the user's primary task;
- which labels, controls, values, descriptions, and metadata support it, and which information must be compared or understood together;
- each information group's exposure level: visible by default, visible after explicit disclosure, or always visible in an applicable exception state;
- which elements are interactive and how their default, hover, focus, selected, disabled, loading, success, and error states are signaled;
- whether the page is one authenticated workflow or contains a separately owned public website surface.

Choose exposure from decision relevance, frequency of use, and the consequence of omission. Put values and decisions needed for the primary task first. Paths, timestamps, identifiers, complete long values, and explanatory metadata are candidates for disclosure when immediate judgment does not need them; keep them visible when the current task does. Keep the existence and actionable summary of errors and blockers in the default view while allowing full diagnostics in disclosure.

Do not make passive information look clickable. Do not make controls look like static labels.

### Step 3 — Declare the app UI system

For new or structural UI, summarize this system before UI code. Keep it concise and use the existing product vocabulary:

```text
WEB APP SYSTEM — browser application surface
Intent: <product-specific operational intent>
Inherited tokens: <actual type, color, spacing, radius, and depth sources>
Role scale: Primary <setting or task role> / Secondary ceiling <help role that cannot exceed primary> / Metadata <supporting role>
Palette: <neutral work surface, semantic states, and one interaction accent>
Spacing: <base unit and density rule>
Depth: <one primary separation strategy>
Control affordance: <how interactive, selected, disabled, and focus states differ from information>
State geometry: <stable row, column, action slot, and disclosure behavior>
Information exposure: <default, disclosed, and exception-visible groups with reasons>
Visual character: <product-appropriate composition, type, spacing, surface, and detail choices>
```

Rules:

- Continuous reading copy stays at least 16px. Compact labels and metadata may use an inherited 12–14px role only when readability is verified and they do not carry the primary task.
- Help, tooltip, and “how it works” content uses the inherited secondary role. Opening it must not make its type size, weight, contrast, or spacing stronger than the setting or menu item it explains.
- A 44px hit area is an interaction floor, not a mandate for a 44px-tall visible control. Use padding or a wrapper so compact controls remain visually proportional.
- Selected tabs, segmented controls, mode choices, toggles, and buttons must look operable before hover and must differ from static status text.
- Use spacing, weight, and color before introducing a larger title size. Preserve the product's established role scale.
- Choose color by semantic role rather than a feature name or action verb. Map the roles the product actually supports—primary interaction, neutral action, premium identity, success, warning, information, system error, and destructive action—to its existing palette. Add and Create do not become success or diff-add actions by name. Verify that supported light and dark themes preserve meaning and prominence.
- Make typography, alignment, spacing rhythm, color relationships, surface treatment, and component proportions look intentional together. Visual detail may add character, but it must strengthen grouping, affordance, or orientation instead of competing with the task.

### Step 4 — Declare the viewport×state matrix

List the affected viewport and state combinations. Include relevant cases below; mark non-existent or unaffected cases N/A with a short reason instead of creating them:

| Dimension | Required cases |
|---|---|
| Viewport | desktop working width, narrow or mobile width supported by the product |
| Data | empty, one item, typical workload, high-volume fixture, long label or value |
| Request | idle, loading, success, error |
| Control | default, keyboard focus, selected, disabled |
| Disclosure | help closed, help open |
| Mode | every mode that swaps controls or lists |
| Theme | every light or dark theme the affected surface supports |
| Reordering | source, insertion point, boundaries, saving, save failure, and live update when the feature exists |

For the same data row, record the pre-change height, core column widths, and action slot. Help disclosure may intentionally add a subordinate region; changing a mode must keep comparable geometry stable unless the requested change intentionally defines a different layout.

For data-rich surfaces, use the same viewport and record the distance from the page start to the first primary value, the default row or cell height, and the number of primary values visible in the initial viewport for one-item, typical, and high-volume fixtures. Use these measurements to assess scanning and comparison, not as universal targets. Never gain density by shrinking primary information into a metadata role or hiding errors and blockers.

### Step 5 — Implement within the declared system

Reuse product components and tokens before adding new ones. Keep DOM order aligned with reading and keyboard order. Reserve stable space for controls that swap by mode. Use semantic controls, visible focus, programmatic labels, and semantic status announcements.

Disclosure, filtering, grouping, pagination, and layout editing are presentation operations unless the product contract explicitly defines a data mutation. Preserve relevant input drafts, focus, scroll position, and live subscriptions across those operations; move focus or scroll only when the interaction contract calls for it, and do not reset unrelated state.

When reordering exists, preserve stable item identity and define the drag source, insertion position, final order, movement boundaries, saving state, and save-failure recovery. Keyboard and touch operation must produce the same final order as pointer dragging. During live updates, keep the moving item and intended position stable, and handle deletion or concurrent reordering according to the product contract.

Motion is optional. When used, keep it under 300ms and animate `transform` or `opacity`; never use `transition: all`.

### Step 6 — Verify rendered behavior

Use a real browser and execute the viewport×state matrix. For each case:

- compare primary, secondary, and metadata hierarchy;
- confirm default, disclosed, and exception-visible information matches the primary task and keeps actionable errors and blockers visible;
- verify interactive and informational regions are distinguishable;
- measure row height, core column width, and action slot before and after mode changes;
- compare applicable density measurements for one-item, typical, and high-volume fixtures;
- verify semantic color roles in every supported theme rather than inferring meaning from an action label;
- operate presentation controls and confirm stored data, drafts, relevant focus and scroll, and live subscriptions retain the intended state;
- when reordering exists, verify source, insertion feedback, final order, movement boundaries, saving, failure recovery, keyboard, touch, and live-update behavior;
- confirm the visible control and its 44px hit area are independently intentional;
- navigate every control by keyboard and inspect focus;
- check clipping, overflow, loading, success, error, disabled, empty, and long-content behavior.

After rendering, critique hierarchy, information relationships, typography, alignment, spacing rhythm, color harmony, component proportion, density, affordance, and visual coherence. Confirm that the primary task and related information are easy to find and understand. Fix observed problems within the request and recheck the changed cases. A completed declaration is not proof of visual quality.

Rendered behavior is the evidence. If a real browser is unavailable, report the missing verification instead of claiming completion.

## Red Flags

| Excuse | Reality |
|---|---|
| "The explanation deserves a larger font because it is newly opened." | Disclosure changes visibility, not ownership. Secondary help stays below the primary setting. |
| "A 44px hit target means every visible control should be 44px tall." | Hit geometry and visual geometry are separate decisions. |
| "Auto and Manual use different content, so different row geometry is expected." | Different content still needs a shared comparable row, core columns, and action slot. |
| "The selected option is obvious from context." | A control must communicate interaction and selection without requiring inference. |
| "A tiny adjustment needs the full design declaration." | Inspect the inherited roles and verify the changed surface. Reserve the full declaration for new or structural UI. |
| "Desktop looks correct, so responsive states are implied." | Every viewport×state case needs rendered evidence. |
| "This worked in another dashboard, so it is a general rule." | Preserve the design question, then derive the answer from this product's task, system, and states. |
| "Create is positive, so the button should be green." | Action wording does not define semantic color. Use the product's interaction role. |
| "More rows above the fold always improves density." | Density serves scanning and comparison; primary information and errors keep readable roles. |
| "Filtering is only visual, so losing the draft is harmless." | Presentation operations preserve relevant working state unless the product contract says otherwise. |
| "Pointer drag succeeded, so reordering is complete." | Verify boundaries, persistence, recovery, keyboard, touch, and applicable live-update behavior. |
| "The state matrix passed, so the UI looks finished." | Rendered typography, alignment, spacing, color, proportion, and information hierarchy still require visual critique. |

## Handoff

- Public website surface discovered during the task → isolate its owned files and use the forge website-design skill for that surface only.
- UI copy changes → use the forge writing-tone skill.
- Claiming completion → return to the current direct route or the forge executing-plans skill, then use the forge verifying-work skill against the affected work scope.
