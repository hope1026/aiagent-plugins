# UI Verification

Use this reference when verifying changed UI behavior or visual quality, including shared Visual Docs tooling. Follow the product contract, supported platforms, existing design system, and the user's requested result. Design guidance already selected for the work may help; no separate design skill or installation is required.

## Select the affected evidence

Identify what the user must see, compare, and do in the changed surface. Operate changed controls in the real browser at representative supported viewports and meaningful states, using typical and relevant boundary data. Native applications need equivalent evidence from their own platform. A build or a design statement alone does not prove the result.

Check readable hierarchy, alignment, typography, spacing, color, component proportions, overflow, and interaction together. Compare relevant peer roles across affected tabs, pages, or components while preserving intentional contextual differences. Equal font sizes can still express hierarchy through weight, spacing, and grouping. Record computed styles or density measurements only when diagnosing a discrepancy or protecting a regression; do not impose universal pixel values or a full viewport-by-state matrix.

Confirm task-critical values, errors, and blockers remain discoverable. Paths, identifiers, timestamps, and long values should be visible when the task needs them; supporting detail may be disclosed separately. Check color against product semantic roles across supported themes. An Add or Create action does not automatically imply success green. With dense data, verify reading and comparison quality at realistic volumes rather than shrinking important values or hiding failures to fit.

## Preserve state and recover from failure

For detail views, filtering, grouping, pagination, and layout changes, check that presentation operations do not unintentionally mutate stored data or lose relevant input drafts, focus, scroll position, or live subscriptions. Intentional changes defined by the interaction contract are allowed; preserve unrelated state. Keep comparable geometry stable where the task depends on comparison.

For reordering, verify the source identity, insertion position, final order, movement boundaries, saving state, persistence, and recovery after a save failure. Exercise the product's supported keyboard and touch paths as well as pointer interaction. With live data, check stable identity and the applicable behavior when an item is deleted or its order changes concurrently.

Exercise relevant loading, empty, selected, disabled, success, and error states. Check semantic controls, labels, visible keyboard focus, operable targets, suitable contrast, and accessible status feedback against the product's accessibility target. Respect reduced motion and check for accidental layout shifts. Do not invent unsupported input modes or unrelated state combinations merely to fill a checklist.

## Use evidence proportionately

Fix observed issues within scope and recheck the affected cases. Reuse applicable evidence from implementation or specialist review. Report unavailable browser checks and unobserved states accurately; one screenshot cannot establish interaction or recovery behavior.

For a requested Forge document, the forge visual-docs skill owns source fidelity and reading checks. HTML alone does not require a separate design workflow. Changes to shared tooling need the relevant UI checks above; an individual document does not require rerunning unchanged tooling's full suite.
