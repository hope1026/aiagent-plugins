# Canonical Spec Bundle Template

Use the `forge/spec@3` semantic contract for a Canonical Spec Bundle at `docs/specs/<semantic-bundle-name>/`. The normalized bundle directory path is the human-facing identity. Do not add a separate document identifier or a numeric prefix.

The bundle contains exactly one root Markdown document and zero or more member Markdown documents. Choose descriptive filenames that explain the content. Do not use a generic filename. Keep one document while it stays readable; split members only when one durable contract has several independently reviewable concerns.

Canonical Specs record durable system intent, contracts, policy, and invariants. Do not use this template for a task brief, implementation sequence, temporary investigation, or execution log. Use `spec-delta-template.md` for the non-authoritative approval proposal that precedes a new or changed bundle.

## Language rules

- Keep `Documents`, `Requirements`, and `Decisions & History` exactly as written. Keep `Acceptance Criteria` exactly as written when the bundle uses it. Choose any other `##` sections and order that best fit the bundle.
- Requirements are mandatory. Write each Requirement as a complete `###` heading centered on one independently reviewable durable condition and required behavior, without pointing to another section or a legacy source as a placeholder. Put supporting numbers, examples, translations, exceptions, and interface detail in its body or another Requirement. Do not use a mechanical heading-length limit.
- Acceptance Criteria are optional at bundle level. A Requirement-only bundle omits the `Acceptance Criteria` section and any acceptance-only member instead of leaving an empty section.
- When Acceptance Criteria are present, include at least one Acceptance statement, write every statement as a complete `###` heading, and cover every Requirement. Use EARS as a semantic discipline in the user's language: each Acceptance heading states a precondition, action, and observable outcome instead of only saying that a source matches.
- Under each Acceptance statement, add `Verifies:` for English or `검증하는 요구사항:` for Korean, then link exact Requirement heading text to its member path and anchor.
- Preserve lifecycle values, code identifiers, commands, and established technical names. Keep only the current adopted decision in the active history section.
- Put source-owned Mermaid, tables, examples, and code in the member where a reader naturally needs them.

## Lifecycle

Only `approved` and `implemented` bundles are project SOT. `approved` records accepted intent that may be partially implemented; `implemented` records verified alignment for the whole bundle. `draft` is a proposal token for incomplete isolated candidate handling and never replaces existing approved authority. A complete Spec Delta shows the intended post-approval bundle with `status: approved`, but remains non-authoritative outside `docs/specs/` until explicit approval and the writer transaction. Partial work verifies and reports its affected scope without changing lifecycle. Only the forge verifying-work skill sets `implemented` after evidence passes for the bundle's complete Canonical verification set: all Acceptance statements when any exist, otherwise all Requirement statements. Any authoritative body, metadata, layout, or status edit is incomplete until repository Markdown validation passes. It never implies HTML generation.

## Root template

This example uses a separate Acceptance member. For a Requirement-only bundle, omit the `acceptance` inventory entry and the Acceptance member. Never create an empty `Acceptance Criteria` section.

````markdown
---
schema: forge/spec@3
role: root
status: <draft|approved|implemented>
language: ko
kind: <feature|system|interface|policy>
subtype: <optional-lowercase-kebab-case>
areas: ["<area>"]
components: ["<component>"]
relatedSpecs: []
---
# <사용자 언어로 쓴 내용을 정확히 표현하는 제목>

## Documents

- root: [<root H1>](<descriptive-root-name>.md)
- contract: [<contract member H1>](<descriptive-contract-name>.md)
- acceptance: [<acceptance member H1>](<descriptive-acceptance-name>.md)
- history: [<history member H1>](<descriptive-history-name>.md)

## <bundle에 맞는 서술 section>

<목적과 범위. 일반적인 설명은 사용자의 언어로 쓴다.>

<비목표 레이블>:
- <의도적으로 포함하지 않는 범위>

## Requirements

### <조건 또는 사건과 필요한 시스템 동작을 한 문장으로 표현>

<필요한 세부 설명>
````

## Acceptance member template

Use this member only when the bundle includes Acceptance Criteria. Include at least one Acceptance statement.

````markdown
# <검증 범위를 정확히 표현하는 제목>

## Acceptance Criteria

### <선행조건, 행동, 관찰 가능한 결과를 한 문장으로 표현>

검증하는 요구사항:

- [<Requirement heading의 정확한 문장>](<requirement-member-name>.md#<heading에서-계산한-anchor>)
````

## History member template

````markdown
# <bundle의 현재 결정을 표현하는 제목>

## Decisions & History

- YYYY-MM-DD [CURRENT] <현재 채택된 결정과 이유>
````

The root may also own Requirements, Acceptance Criteria, or Decisions & History. Across the whole bundle, Requirements appear at least once. Acceptance Criteria are optional; when used, they contain at least one Acceptance statement. Decisions & History appears exactly once and contains current facts rather than completed migration history.

## Frontmatter fields

| Field | Contract |
|---|---|
| `schema` | exact `forge/spec@3` |
| `role` | exact `root`; member documents have no Forge frontmatter |
| `status` | `draft`, `approved`, or `implemented` |
| `language` | `en` or `ko` |
| `kind` | exact enum `feature`, `system`, `interface`, or `policy` |
| `subtype` | optional lowercase kebab-case presentation hint such as `workflow`, `api`, or `architecture` |
| `areas` | JSON string array |
| `components` | JSON string array |
| `relatedSpecs` | JSON object array with `path` and `relation`; each path names a semantic bundle directory |

## Bundle and traceability rules

- The bundle directory and every filename are semantic lowercase kebab-case without a numeric prefix.
- The root `Documents` section lists every direct Markdown member exactly once, including the root, with role `root`, `contract`, `acceptance`, `history`, or `reference`. Link text exactly matches the member H1.
- H1 values are the display names. Member paths are the navigation and provenance keys.
- Requirement headings are unique across the bundle after normalization. Acceptance headings follow the same rule.
- When Acceptance Criteria are present, at least one Acceptance statement covers each Requirement. Every Acceptance statement links one or more Requirements in the same bundle using exact heading text, member path, and anchor.
- A Requirement-only bundle omits the `Acceptance Criteria` section. An acceptance-bearing bundle never leaves that section empty.
- `[NEEDS CLARIFICATION: ...]` is allowed only while `status` is `draft`.
- Replacing one active path is the narrow exception: use one-to-one `superseded` in `docs/specs/.bundle-transitions.json` only after approval and isolated candidate verification. Consolidating two or more active paths into one new current boundary uses coordinated many-to-one `merged` records in `docs/specs/.bundle-transitions.json` with exact source hashes, one shared target, and one shared evidence file. Neither shape permits partial removal or an unvalidated current-tree mutation.

## Current decision

Use one dated `[CURRENT]` entry that explains the adopted contract in ordinary language. Keep completed migration detail, rejected options and superseded clauses in Git or validated transition evidence instead of the active bundle.
