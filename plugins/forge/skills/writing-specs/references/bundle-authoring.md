# Bundle Authoring

Use when creating or changing structured bundle files. The schema and exact references are consumed by Forge tooling.

## Authority Contract

A Canonical Spec is a Spec Bundle at `docs/specs/<semantic-bundle-name>/`. The normalized repository-relative bundle path is its human-facing identity. Do not assign a separate document identifier. Consult [spec-template.md](spec-template.md) when creating a bundle or changing its structure.

Each bundle has exactly one `forge/spec@3` root document and one or more Markdown members. The root owns lifecycle metadata and a complete `Documents` inventory. Root and member filenames describe their contents; generic names and numeric filename or directory prefixes are invalid. Keep one file when it remains readable. Split it only when several independently reviewable concerns need distinct members, and keep every member in the same bundle directory.

Each Requirement heading centers on one independently reviewable durable condition and required behavior. Keep the complete-sentence identity, but place supporting numbers, examples, translations, exceptions, and interface detail in its body or a separate Requirement. Do not impose a mechanical heading-length limit.

`Requirements` and `Decisions & History` carry normative project authority. Requirements are mandatory. Acceptance Criteria are optional at bundle level and carry normative authority when used. A Requirement-only bundle omits the `Acceptance Criteria` section instead of leaving it empty. When Acceptance Criteria are present, the bundle contains at least one Acceptance statement, every Requirement is covered, and each Acceptance statement includes `Verifies:` or `검증하는 요구사항:` followed by Markdown links whose member path, anchor, and link text exactly identify the Requirement headings it verifies. A Requirement or Acceptance statement is a complete `###` heading, not a short code. A Change Brief and a Spec Delta remain non-authoritative work inputs. Use [spec-delta-template.md](spec-delta-template.md) when a standalone proposal helps review.

Use EARS as a semantic discipline in the user's language. Each Requirement heading states the actual durable condition and required behavior; do not write a placeholder that merely points to another section or says to follow a legacy source. When used, each Acceptance heading states a precondition, action, and observable outcome; do not write a placeholder that only says the source matches. Keep `Decisions & History` focused on the current adopted decision; Git and validated transition evidence retain superseded detail.

