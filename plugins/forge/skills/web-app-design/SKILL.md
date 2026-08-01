---
name: web-app-design
description: 'Use when designing, implementing, or reviewing browser application UI such as dashboards, admin panels, settings, tables, forms, controls, internal tools, SaaS workspaces, and PWAs. Triggers: "대시보드", "관리자 화면", "설정 화면", "웹앱", "PWA", "table UI", "form UI", "control panel".'
---

# Web App Design

Announce at start: "Using the forge web-app-design skill to declare the inherited product UI system and state geometry before writing UI code."

Respond to the user in the user's language. This skill file stays in English.

## Overview

Browser application UI helps a person inspect state and complete work. Its design quality comes from clear relative hierarchy, stable geometry, obvious interaction, and complete state coverage. Decorative novelty never outranks scan speed or control predictability.

## Iron Law

```text
NO WEB APP UI CODE BEFORE THE INHERITED SYSTEM, ROLE HIERARCHY, AND STATE MATRIX ARE DECLARED.
SECONDARY CONTENT NEVER OUTRANKS THE PRIMARY TASK.
STATE CHANGES MUST NOT CAUSE UNPLANNED GEOMETRY CHANGES.
```

## When to Use / When NOT

Use for browser and PWA dashboards, authenticated workspaces, admin panels, settings, tables, forms, filters, controls, and operational tools.

Do NOT use for:

- public landing pages, marketing sites, portfolios, editorial sites, or public content sites — use the forge website-design skill;
- native iOS, Android, React Native, Flutter, desktop, Electron, or Tauri apps — the browser app contract does not own native platform behavior;
- fixed Review Viewer generation — a single requested `review-viewer` build needs no UI design skill;
- logic changes with no visible or interactive surface.

Review Viewer tooling and Spec Pages tooling changes use `web-app-design`: shell, template, CSS, runtime, interaction, responsive behavior, and accessibility changes require the viewport×state matrix and full rendered verification below.

## The Process

Create one todo per numbered step before changing UI code.

### Step 1 — Read product truth

Read the current plan Task and every Related Spec. Then inspect the actual component, design tokens, typography roles, spacing, control states, and responsive rules already used by the product. Existing values are inherited unless the approved spec requires a change.

### Step 2 — Classify the primary task and interaction

State:

- the user's primary task;
- which labels, controls, values, descriptions, and metadata support it;
- which elements are interactive and how their default, hover, focus, selected, disabled, loading, success, and error states are signaled;
- whether the page is one authenticated workflow or contains a separately owned public website surface.

Do not make passive information look clickable. Do not make controls look like static labels.

### Step 3 — Declare the app UI system

Post this completed block to the user before UI code:

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
```

Rules:

- Continuous reading copy stays at least 16px. Compact labels and metadata may use an inherited 12–14px role only when readability is verified and they do not carry the primary task.
- Help, tooltip, and “how it works” content uses the inherited secondary role. Opening it must not make its type size, weight, contrast, or spacing stronger than the setting or menu item it explains.
- A 44px hit area is an interaction floor, not a mandate for a 44px-tall visible control. Use padding or a wrapper so compact controls remain visually proportional.
- Selected tabs, segmented controls, Auto·Manual choices, toggles, and buttons must look operable before hover and must differ from static status text.
- Use spacing, weight, and color before introducing a larger title size. Preserve the product's established role scale.

### Step 4 — Declare the viewport×state matrix

List every viewport and state combination that will be verified. At minimum include:

| Dimension | Required cases |
|---|---|
| Viewport | desktop working width, narrow or mobile width supported by the product |
| Data | empty, typical, long label or value |
| Request | idle, loading, success, error |
| Control | default, keyboard focus, selected, disabled |
| Disclosure | help closed, help open |
| Mode | every mode that swaps controls or lists |

For the same data row, record the pre-change height, core column widths, and action slot. Help disclosure may intentionally add a subordinate region; changing a mode must keep the comparable row and core columns within 1px unless the approved spec defines a different layout.

### Step 5 — Implement within the declared system

Reuse product components and tokens before adding new ones. Keep DOM order aligned with reading and keyboard order. Reserve stable space for controls that swap by mode. Use semantic controls, visible focus, programmatic labels, and semantic status announcements.

Motion is optional. When used, keep it under 300ms and animate `transform` or `opacity`; never use `transition: all`.

### Step 6 — Verify rendered behavior

Use a real browser and execute the viewport×state matrix. For each case:

- compare primary, secondary, and metadata hierarchy;
- verify interactive and informational regions are distinguishable;
- measure row height, core column width, and action slot before and after mode changes;
- confirm the visible control and its 44px hit area are independently intentional;
- navigate every control by keyboard and inspect focus;
- check clipping, overflow, loading, success, error, disabled, empty, and long-content behavior.

Rendered behavior is the evidence. If a real browser is unavailable, report the missing verification instead of claiming completion.

## Red Flags

| Excuse | Reality |
|---|---|
| "The explanation deserves a larger font because it is newly opened." | Disclosure changes visibility, not ownership. Secondary help stays below the primary setting. |
| "A 44px hit target means every visible control should be 44px tall." | Hit geometry and visual geometry are separate decisions. |
| "Auto and Manual use different content, so different row geometry is expected." | Different content still needs a shared comparable row, core columns, and action slot. |
| "The selected option is obvious from context." | A control must communicate interaction and selection without requiring inference. |
| "The existing design system means no declaration is needed." | Read it and declare the inherited roles; otherwise the implementation is guessing. |
| "Desktop looks correct, so responsive states are implied." | Every viewport×state case needs rendered evidence. |

## Handoff

- Public website surface discovered during the task → isolate its owned files and use the forge website-design skill for that surface only.
- UI copy changes → use the forge writing-tone skill.
- Claiming completion → return to the forge executing-plans skill, then use the forge verifying-work skill against the approved acceptance criteria.
