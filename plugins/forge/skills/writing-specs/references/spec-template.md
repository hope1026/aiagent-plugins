# Spec Template

Canonical structure for `docs/specs/NNN-<slug>/spec.md`. Section headings must match this template exactly — plans, verification, and the forge spec-viewer skill all navigate by these names.

## Language rules

- Keep only the canonical `##` section headings below exactly as written because downstream forge skills parse them. Localize body labels such as `Non-goals:` and table column labels.
- Write every other human-readable part of the spec in the user's language, including the title, explanations, requirements, acceptance criteria, diagram labels, table labels and descriptions, and history explanations.
- Preserve proper nouns, product and framework names, API and protocol names, code identifiers, commands, quoted UI labels, and established domain terms in their original form. Explain them and their surrounding context in the user's language instead of forcing a translation or transliteration.
- Keep requirement and acceptance-criterion IDs, Status keywords, history tags, and the `[NEEDS CLARIFICATION: ...]` marker prefix in English as fixed traceability and lifecycle tokens. EARS and acceptance-criterion prose follow the user's language.

## Traceability IDs

- `R` means Requirement: a required system behavior or constraint.
- `AC` means Acceptance Criterion: observable evidence that one or more requirements are satisfied.
- Every AC cites the R-IDs it verifies. Downstream planning and verification trace these IDs, not English sentence keywords.

## Status line semantics

The `Status:` line is the lifecycle gate token. It moves forward `draft → approved → implemented`; a change delta moves it back to `draft` until the user re-approves.

| Status | Meaning | Who may set it |
|---|---|---|
| `draft` | Being written or revised; not a valid basis for planning or coding | The agent, while authoring or revising |
| `approved` | The user explicitly approved the content; planning may start. Requires zero `[NEEDS CLARIFICATION]` markers | The user only — the agent records it after an explicit approval message, never infers it |
| `implemented` | Every acceptance criterion verified PASS with fresh evidence | Only the forge verifying-work skill, after walking all ACs |

## Template

````markdown
# <Feature name in the user's language>

Status: draft

## Overview

<In the user's language: 2–4 sentences explaining what this is and why it exists.>

<Non-goals label in the user's language>:
- <In the user's language: what this spec deliberately does not cover>

## Requirements

<Start with one short line in the user's language defining R as Requirement: a required system behavior or constraint. Then write the requirements in the user's language, except for stable IDs. Use EARS semantics without
forcing English keywords: state the trigger or condition and the required behavior clearly. Never renumber or reuse a removed ID. Each requirement must be testable. Mark unresolved ambiguity inline:
[NEEDS CLARIFICATION: the exact open question in the user's language].>

- R1. <In the user's language: event or condition, followed by the required behavior>
- R2. <In the user's language: exception condition, followed by the required response>

## Behavior & Flows

<Mermaid flowchart / sequenceDiagram / stateDiagram fences with human-readable
labels in the user's language. These fences are the single diagram source — the spec viewer lifts them verbatim.>

## Data & Interfaces

<Entities and fields as tables; API and event contracts as tables. Write table labels and descriptions in the user's language while preserving identifiers and established original-language terms.>

## Acceptance Criteria

<Start with one short line in the user's language defining AC as Acceptance Criterion: observable evidence that cited requirements are satisfied. Then write AC1..ACn, each citing the R-IDs it verifies. In the user's language, state the precondition, action, and observable outcome clearly.>

- AC1 (R1): <In the user's language: precondition, action, and observable outcome>

## Decisions & History

<In the user's language: dated log of decisions, clarifications, change deltas,
drift findings, and rejected options. Append-only; keep history tags in English.>

- YYYY-MM-DD [DECISION] <what was decided and why>
````

## EARS semantic reference

Use these semantic shapes in the user's language. The English keywords are explanatory labels, not required output tokens.

| Pattern | Meaning |
|---|---|
| Ubiquitous | A behavior that is always required |
| Event-driven | An event or trigger followed by the required behavior |
| State-driven | A state that remains true while the required behavior applies |
| Unwanted behavior | An abnormal or failure condition followed by the required response |
| Optional feature | A feature-presence condition followed by the required behavior |

## Filled examples

These examples demonstrate structure and token placement. Use their English prose only when the user's language is English; otherwise write equivalent content in the user's language while preserving applicable original-language terms.

Running example: login with account lockout.

### Requirements (EARS semantics)

- R1. When a user submits valid credentials, the system creates a session and redirects to the dashboard within 2 seconds.
- R2. If a fifth login attempt for the same account fails within 10 minutes, the system locks the account for 15 minutes and displays the lockout message.

### Acceptance criterion (precondition / action / outcome)

- AC1 (R2): With an account at four failed login attempts in the last 10 minutes, a fifth failed attempt makes the account reject even correct credentials for 15 minutes and makes the login page show the lockout message.

### Behavior & Flows

```mermaid
flowchart TD
    A[Login submitted] --> B{Credentials valid?}
    B -- yes --> C[Create session]
    C --> D[Redirect to dashboard]
    B -- no --> E{5th failure in 10 min?}
    E -- no --> F[Show error message]
    E -- yes --> G[Lock account for 15 min]
    G --> H[Show lockout message]
```

```mermaid
sequenceDiagram
    participant U as User
    participant W as Web app
    participant S as Auth service
    U->>W: submit credentials
    W->>S: POST /sessions
    alt valid credentials
        S-->>W: 201 token
        W-->>U: redirect to dashboard
    else account locked
        S-->>W: 423 Locked
        W-->>U: lockout message
    end
```

### Data & Interfaces

Entity table:

| Entity | Field | Type | Constraints | Notes |
|---|---|---|---|---|
| Account | email | string | unique | login identifier |
| Account | failed_attempts | integer | >= 0 | reset to 0 on success |
| Account | locked_until | timestamp, nullable | — | null = not locked |

API contract table:

| Endpoint | Method | Request | Success | Errors |
|---|---|---|---|---|
| /sessions | POST | { email, password } | 201 { token } | 401 invalid credentials; 423 account locked |

### Decisions & History entry formats

```
- 2026-07-04 [DECISION] Account-level lockout instead of IP throttling: shared-office IPs cause false positives.
- 2026-07-04 [CLARIFIED] R2: failure-count window is 10 minutes (user answer).
- 2026-07-04 [CHANGE] R3 MODIFIED: lockout duration 30 -> 15 minutes (change request).
- 2026-07-04 [CHANGE] R9 ADDED: admin unlock endpoint (change request).
- 2026-07-04 [DRIFT] Code returns 429 instead of 423 on lockout; reconciliation pending.
- 2026-07-04 [REJECTED] CAPTCHA after third failure: too much friction for the target users.
```

Tags: `[DECISION]` design choices · `[CLARIFIED]` resolved markers · `[CHANGE]` approved deltas (`R3 MODIFIED: …`, `R7 REMOVED: …`, `R9 ADDED: …`) · `[DRIFT]` code/spec mismatches found by sync mode · `[REJECTED]` options considered and dropped.
