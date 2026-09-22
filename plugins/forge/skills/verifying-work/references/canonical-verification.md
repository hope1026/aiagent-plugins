# Canonical Verification

Read for affected-contract evidence or a lifecycle status change. Reuse already inspected unchanged context.

## Work-class Matrix

| Work class | Required fresh evidence | Canonical lifecycle effect |
|---|---|---|
| Quick | focused test, build, lint, type check, real run, or observation that directly proves the claim | none |
| Plan-only | every plan verification command and goal-level Done Check | none |
| Existing-contract restoration | original reproduction or equivalent fault-boundary observation passes, affected contract matches, relevant regression evidence passes | none |
| Partial implementation of an approved contract | every directly or indirectly affected statement plus relevant regression evidence | none; report the implemented work scope |
| Approved Spec Delta against an implemented baseline | every affected statement in the Canonical verification set passes plus regression command for unchanged behavior | `approved → implemented` after validation |
| Full implementation of a new or never-implemented approved baseline | every statement in the Canonical verification set passes plus the full relevant suite | `approved → implemented` after validation |

Keep an applied Spec Delta through verification so its baseline lifecycle and affected statement links remain available. Remove it after evidence is recorded or promote it only as explicitly non-authoritative evidence.

## Match contract evidence to the claim

For existing-contract restoration, partial implementation, or approved Spec Delta work:

1. Inspect each governing bundle with `bash <writing-specs-skill>/scripts/spec-docs.sh --repo-root . inspect --spec <bundle-directory> --format json`. Require `forge/spec@3`, lifecycle `approved|implemented` appropriate to the class, and empty diagnostics.
2. Calculate each bundle's Canonical verification set: use every Acceptance statement when one or more exist; otherwise use every Requirement statement. Then select the required statements from the work class:
   - restoration: the statements whose approved behavior the fix restores;
   - partial implementation or Delta against an implemented baseline: the affected statements linked in the approved scope, plus any statement whose observable outcome the change touches;
   - full implementation claim for a new Canonical Spec or never-implemented approved baseline: every statement in the bundle's Canonical verification set.
3. Associate the required statements with inspected evidence. Group statements proved by the same observation; use a detailed table only when it improves review or lifecycle accountability.
4. Confirm each required observable outcome. Code reading alone does not prove runtime behavior. Record failures and unobserved scope accurately.
5. When an Execution Plan exists, confirm the contracts it actually covers, its completion checks and recorded outcomes agree with the implementation. Find this information by meaning; no fixed plan headings or repeated statement-link blocks are required.

Unchanged statements retain prior implementation evidence when the approved scope identifies every affected statement and current regression evidence covers unchanged behavior. Any concrete uncertainty expands the affected set. Do not expand merely because more tests or statements exist.

Set `status: implemented` only after all evidence required for the claimed lifecycle scope passes. Apply the writer transaction through the forge writing-specs skill. A failed transaction blocks the lifecycle claim. Preserve partial status and report partial work when the whole baseline is not implemented.

An already implemented baseline changed by an authorized Delta can return to implemented after affected-statement and regression verification; it does not require rechecking the entire unchanged bundle. A mitigation with an unconfirmed cause is not a confirmed restoration claim.
