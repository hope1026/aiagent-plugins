# UI Verification

Use this reference when verifying changed UI behavior or visual quality, including requested visual documents. Follow the product contract, supported platforms, existing design system, and the user's requested result. Apply the forge using-forge skill's UI guidance as the shared design and implementation criteria; this reference owns the observation needed to verify them. No separate design skill or installation is required.

## Select the affected evidence

Identify what the user must see, compare, and do in the changed surface. Operate changed controls in the real browser at representative supported viewports and meaningful states, using typical and relevant boundary data. Native applications need equivalent evidence from their own platform. A build or a design statement alone does not prove the result.

Use the affected parts of the rendered layout to judge alignment, spacing and reading order.

- In a row, trace the baseline of neighboring labels. Compare the top and bottom edges of peer buttons and fields, then check whether icons, labels and smaller badges sit on the intended center. Where controls wrap, resize through the first line break with realistic labels and see whether each action still sits with its group.
- In a panel, follow the starting edge from the heading to its body. Look at the first and last lines, including wrapped text, for crowding against the border. Scan for the title or key value first, then read its unit and explanation. Check that the secondary text is legible and clearly belongs to that value.
- In a list, populate several entries with a mix of short and long content. Find the same field in successive rows. Look for unnecessary scrolling from stacked short fields or repeated padding, as well as rows packed so tightly that neighboring entries run together.

Compare peer components across affected surfaces where relevant. Check whether text or controls overflow or become hard to operate as the layout changes. Inspect bounds or computed styles when they help diagnose a visible discrepancy or protect a regression. Use the product's scale and supported layouts to judge the result.

Follow the user's reading and action path: can they identify the main action, compare necessary information, discover detail and understand the current state? Confirm task-critical values, costs, consequences, errors and blockers remain discoverable before a decision. Paths, identifiers, timestamps and long values should be visible when the task needs them; supporting detail may be disclosed separately. Check that repeated explanations or misplaced emphasis do not displace the action. Check color against product semantic roles across supported themes. An Add or Create action does not automatically imply success green. With dense data, verify reading and comparison quality at realistic volumes rather than shrinking important values or hiding failures to fit.

## Check prerequisites and high-risk actions

For affected unavailable features, exercise relevant missing-setup, read-only,
processing, permission and failed-check states. Verify the explanation matches
the actual cause and the next step is reachable with the user's permissions.
Check setup navigation and return, preserved input, and availability refresh
when prerequisites change. Essential guidance must be discoverable without
hovering a disabled control; verify the supported keyboard and touch paths.
Do not require every state combination for an unrelated change.

For high-risk actions, observe the target, scope, consequences and recovery
limits before confirming. Check that opening, cancellation and applicable
Escape dismissal issue no command, and final confirmation does not duplicate
submission. Check accidental keyboard activation, pending feedback, failure
and unknown outcome as relevant. Closing after submission must not falsely
report cancellation or success. Preserve server guards and relevant drafts.
Do not add a second confirmation when an existing step already suffices.

If a web modal is used, check its accessible name, initial focus, keyboard
containment, dismissal and logical focus return, including when the original
trigger disappears. Use the actual platform's equivalent behavior for native
UI. A screenshot alone does not establish these properties.

## Preserve state and recover from failure

For detail views, filtering, grouping, pagination, and layout changes, check that presentation operations do not unintentionally mutate stored data or lose relevant input drafts, focus, scroll position, or live subscriptions. Intentional changes defined by the interaction contract are allowed; preserve unrelated state. Keep comparable geometry stable where the task depends on comparison.

For reordering, verify the source identity, insertion position, final order, movement boundaries, saving state, persistence, and recovery after a save failure. Exercise the product's supported keyboard and touch paths as well as pointer interaction. With live data, check stable identity and the applicable behavior when an item is deleted or its order changes concurrently.

Exercise relevant loading, empty, selected, disabled, success, and error states. Check semantic controls, labels, visible keyboard focus, operable targets, suitable contrast, and accessible status feedback against the product's accessibility target. Respect reduced motion and check for accidental layout shifts. Check relevant long or translated content and text enlargement against the product's accessibility target. For web text resizing, [W3C SC 1.4.4](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html) describes enlargement up to 200% without loss of content or functionality, subject to its exceptions; narrowing the viewport alone is not proof of text enlargement. Do not invent unsupported input modes or unrelated state combinations merely to fill a checklist.

## Use evidence proportionately

Inspect which UI checks the chosen test command actually includes; a default or critical suite may omit relevant visual regressions. Add focused protection only for missing material risk, not assertions that mirror every style declaration. Fix observed issues within scope and recheck the affected cases. Reuse applicable evidence from implementation or specialist review. Report unavailable browser checks and unobserved states accurately; one screenshot cannot establish interaction or recovery behavior.

For a requested Forge document, the forge visual-docs skill owns source fidelity and reading checks. HTML alone does not require a separate design workflow. Changes to shared tooling need the relevant UI checks above; an individual document does not require rerunning unchanged tooling's full suite.
