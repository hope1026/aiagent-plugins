# UI Work

Use when designing, implementing, changing, or evaluating UI. Follow the
product contract, supported platform, user's direction, and useful design
guidance already selected. Forge supplies shared judgment, not a visual style
or a required design package. Apply it to the affected task; no role worksheet,
new design system, separate plan, or full UI audit is required for every change.

## Establish consistent roles before implementation

Inspect the existing product, approved design system, and relevant components.
Identify the main and supporting actions, headings, body content, status, and
supporting information needed for the task. Reuse their established tokens,
components and variants. Keep the product's visual concept coherent across
affected surfaces while preserving differences justified by role and context.
Do not copy an accidental inconsistency as the standard. Resolve disagreement
with the owning contract; if no standard exists, choose the smallest coherent
approach supported by the user's direction and task.

Consider type size, weight, line height, contrast, spacing and grouping together.
Match controls by role, including size, alignment, labels, icons and states.
Do not shrink important content to fit or make every action equally prominent.
Different tasks and platforms may need different density and emphasis; Forge
prescribes no universal font size, button height, layout or one-primary-button
quota for an entire page.

Prefer extending a suitable component or variant to accumulating local patches.
When web styles conflict, trace inheritance, selector specificity, load order
and overrides such as `!important` in the affected path. Check the rendered
result rather than the declaration alone. Do not blanket-ban overrides or
flatten intentional differences with global rules. Use the equivalent style
and component mechanisms for native UI.

## Reveal information according to the task

Keep what users need to decide, compare and act visible and close to the related
action. Make less frequent detail, explanations and diagnostics available through
clearly named entry points. Omit irrelevant content and redundant explanations.
Essential costs, consequences, errors and blockers must remain discoverable
before the decision; do not hide them merely to make a screen look clean.

Choose disclosure boundaries from the work. Do not split information that users
must compare or add steps simply to reduce visible content. Preserve relevant
drafts, selection, focus and context across disclosure and setup navigation.
Explain implementation details only when they help the user make a decision.

## Explain unavailable features and a usable next step

Distinguish hidden, read-only, unmet prerequisites, processing, permission
restriction and failed availability checks. Choose from the product contract
and task relevance rather than representing all of them as a grey button.

When a relevant feature becomes usable after setup, keep it discoverable,
prevent execution until prerequisites are met, and explain the missing condition
with an accessible route to resolve it. Do not disable the prerequisite setup
itself or direct users to settings they cannot access. Use an authorized request
or support route when that is the available next step. Content that is useful
but not editable should remain readable. Permission-based visibility follows
the product policy; do not expose restricted information to explain a control.

A failed check is not evidence that setup is missing or the feature does not
exist. Show the uncertainty and an appropriate retry or recovery path. Keep
required explanations and setup links discoverable without hovering a disabled
control; support the product's keyboard, touch and assistive-technology paths.
Tooltips may supplement essential guidance, not be its only location.

## Confirm high-risk actions before execution

Assess actual impact and reversibility, not only labels such as Delete, Stop
or Change permission. For high-risk actions, show the target, scope, important
consequences and recovery limits, then require explicit confirmation with a
specific action label. Colour or a generic "Are you sure?" cannot carry that
meaning alone. Choose a confirmation page, dialog or another suitable product
pattern; do not mandate a modal.

Opening or cancelling confirmation must not issue the command. Avoid accidental
confirmation through initial focus or keyboard defaults. When using a modal,
provide appropriate focus placement, contained keyboard navigation, dismissal
and focus restoration. Preserve an existing sufficient final confirmation
instead of adding another. Require name re-entry or additional authentication
only when the risk or owning contract justifies it. Do not add confirmations to
routine low-risk reversible actions or promise undo that the system lacks.

Prevent duplicate submission while processing. Distinguish confirmed success,
failure and unknown outcome; preserve relevant input and a recovery path.
Closing a UI after submission does not by itself cancel server work or prove
success. Keep server authorization, fresh state checks and atomic protections.
These are confirmations by the product's users, not new chat approval gates
for coding work already authorized by the user.

## Verify the result

Use the forge verifying-work skill's UI reference to check the affected reading
and interaction path, including prerequisite resolution and confirmation where
relevant. Inspect which checks the chosen test command actually runs; its name
or a successful build does not prove visual quality. Reuse applicable evidence
and report unobserved scope rather than requiring unrelated testing.

## Sources and scope

Reviewed 2026-11-05. These sources inform judgment; they do not replace product
contracts or require browsing on every UI task.

- [Material typography](https://m3.material.io/styles/typography/applying-type):
  role-based type, without adopting its scale as a universal default.
- [W3C consistent identification](https://www.w3.org/WAI/WCAG22/Understanding/consistent-identification.html):
  recognizable repeated functions, not identical geometry for every control.
- [NN/g progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/):
  essential tasks first, with discoverable detail and proportionate navigation.
- [Carbon disabled states](https://www.carbondesignsystem.com/building-blocks/core/patterns/disabled-states)
  and [tooltips](https://www.carbondesignsystem.com/building-blocks/core/components/tooltip/guidelines):
  distinguish unavailable states and keep required guidance accessible.
- [GOV.UK buttons](https://design-system.service.gov.uk/components/button/):
  meaningful emphasis and destructive confirmation. Its caution about disabled
  buttons and Carbon's temporary-disabled guidance require contextual choice.
- [W3C modal dialogs](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/):
  keyboard and focus behavior when a web modal is chosen.
