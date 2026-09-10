---
name: web-app-design
description: 'Use when designing, implementing, or reviewing browser application UI such as dashboards, admin panels, settings, tables, forms, controls, internal tools, SaaS workspaces, and PWAs. Triggers: "대시보드", "관리자 화면", "설정 화면", "웹앱", "PWA", "table UI", "form UI", "control panel".'
---

# Web App Design

Design browser and PWA applications around the user's primary task, coherent product conventions, and actual rendered quality. Respond in the user's language. Public content sites use the forge website-design skill; native applications need platform-specific guidance. Fixed Visual Docs generation belongs to the forge visual-docs skill. Visual Docs tooling UI changes use this skill at the scale of the affected surface.

## Design from the product

Inspect the current interface, relevant contract, shared components, tokens, typography, and responsive behavior. Inherit the coherent system; correct demonstrated inconsistencies within scope. Another product's structure or pixel values are examples, not this product's requirements.

Identify what the user must see, compare, and do. Place task-critical values and decisions first. Disclose supporting detail when appropriate, while keeping actionable errors and blockers visible. Paths, identifiers, and long values stay visible when the task needs them.

Keep primary, secondary, and metadata roles distinguishable through typography, contrast, spacing, and grouping. Help should have subordinate overall prominence without sacrificing readable copy. Compare representative equivalent roles in affected tabs, pages, or components; preserve intentional contextual variants. Hierarchy need not always use different font sizes.

Make controls visibly operable and selection, focus, disabled, loading, success, and error states understandable. Use semantic color roles from the product palette; Add or Create does not imply success green. Preserve meaning across supported themes.

New or structural work needs a coherent design direction and consideration of relevant states. A short explanation, existing system, or sketch may be enough; a fixed system declaration or exhaustive viewport×state matrix is not required. Focused adjustments need only affected roles and relevant peers.

## Implement and inspect

Use semantic controls, labels, visible keyboard focus, suitable contrast, and accessible status feedback. Derive hit targets, readable type, density, and motion from supported devices, the design system, and the project's accessibility target. A 44px hit area can be a useful touch default; it is not a universal rule for all interfaces. No universal 16px text or 300ms motion gate applies. Respect reduced motion and avoid accidental layout shifts.

Preserve relevant input drafts, focus, scroll position, stored data, and live subscriptions across presentation operations unless the product contract calls for a change. Keep comparable geometry stable across mode changes where the task needs comparison.

For reordering, verify identity, insertion and final order, boundaries, persistence, and failure recovery. Support the product's keyboard and touch interactions as well as pointer input, and handle applicable live updates consistently.

Inspect the real browser result at affected supported viewports and meaningful states. Choose representative typical and boundary data for the changed behavior. Check hierarchy, alignment, typography, color, affordance, overflow, and reading or interaction quality together. Operate changed controls and relevant error paths.

Record computed styles, row dimensions, or density measurements when they help diagnose a discrepancy or protect a regression. Do not measure every role or execute unaffected state combinations merely to fill a checklist. A successful declaration or build is not rendered evidence.

Fix observed issues within scope and recheck changed cases. Reuse applicable evidence and report unavailable checks or unobserved scope honestly. Use the forge verifying-work skill for completion judgment when needed.
