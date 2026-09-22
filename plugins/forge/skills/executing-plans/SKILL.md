---
name: executing-plans
description: 'Use when executing or resuming an existing plan whose dependencies, coordination, or recovery state need attention. Triggers: "계획 실행", "구현 진행", "다음 태스크", "중단 작업 재개", execute the plan.'
---

# Executing Plans

Complete authorized work using the existing plan as the work record. Respond in the user's language. A plan organizes execution; it does not override the user or approved Canonical Specs.

## Execute and adapt

Read the goal, unfinished tasks, relevant contracts, and recorded evidence. Confirm the resume point against current files and changes. Reuse completed work and applicable evidence; investigate conflicting state rather than blindly trusting either memory or a checkbox.

Use the forge using-forge skill's task-context guidance when handing work to another agent or resuming from a summary. Inspect relevant conditions and exceptions at their source. A saved packet may help detect changed files, but its hashes cannot establish that all dependencies were selected or that previous conclusions remain correct.

Choose an order that respects dependencies and user priorities. Correct stale paths, commands, or implementation steps within the authorized scope and record changes that matter for recovery. A changed product outcome or unresolved contract conflict needs a user decision; independent authorized work can continue.

Perform each bounded outcome and verify it using suitable existing tests, additional regression protection, or direct observation. TDD is optional unless requested or required by the project. Inspect worker results and confirm their evidence applies to the integrated state; rerun only missing or invalidated checks.

Keep enough progress to resume safely: completed outcomes, unresolved decisions, useful evidence, and the next step. Use the plan's checklist or the app's existing record; no duplicate todos, per-task route scores, fixed ledger format, or mandatory commit cadence. Commit only with authorization.

Report meaningful progress, failures, or required decisions. A status update does not pause execution. Continue through safe work until the requested outcome is complete or a necessary user decision remains.

## Delegation

Choose root or worker execution by task independence, context-transfer cost, available capabilities, and review effort. Consult `references/adaptive-routing.md` when coordination needs more guidance. Inherit current model settings unless a supported, authorized override is useful. Respect platform and user concurrency limits; Forge adds no fixed worker count or tier ladder.

Root retains integration and final judgment. Do not parallelize overlapping writes or dependent outcomes without resolving ownership and ordering. A worker's success summary alone is not completion evidence.

## Authority and completion

Reuse authorization for concrete work already approved. Pause dependent actions only for a new product or scope decision, unresolved Canonical conflict, or an effect outside existing permissions. The forge writing-specs skill handles durable contract changes; a mechanical plan correction needs no new approval.

Use the forge verifying-work skill when assessing completion or Canonical lifecycle status. Match the claim to the requested scope; finishing tasks does not imply an entire Spec Bundle is implemented.

Visual Docs are derived outputs. Do not inspect, generate, or refresh them merely because a plan or source changed. A requested visualization of Forge sources uses the forge visual-docs skill for meaning preservation and format choice; general diagrams use current app capabilities. Report possible staleness when relevant.

Keep a retained plan in the project's chosen location, with separate progress or task files only when useful. Interpret its outcomes, dependencies and unfinished work without requiring particular heading tokens or numbering. Promote durable decisions before removing the plan. Requested local views default to `.forge/visual-docs/`; a project handbook follows the user's path or project convention and remains derived output, never an execution source.
