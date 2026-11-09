# Bundle Authoring

Use when creating or changing structured bundle files. The schema and exact references are consumed by Forge tooling.

## Choose the content boundary

A Canonical Spec records durable intent and approved behavior. A Change Brief, Spec Delta, or execution record does not acquire that authority by using similar headings. Follow the forge writing-specs skill for authorization and the writer transaction; [spec-template.md](spec-template.md) owns the bundle syntax and examples.

Keep one file when it remains readable. Split members when one durable contract has independently reviewable concerns, such as a separate interface or policy. Separate unrelated contract boundaries into different bundles even when they share a technical area. File count alone does not justify splitting or merging.

Explain behavior, rationale, conditions, exceptions, and observable outcomes where the reader needs them. Keep implementation sequences and temporary investigation in the work record. When a decision changes, preserve superseded detail in Git or transition evidence and retain all still-valid independent decisions in the active bundle.

Use [spec-delta-template.md](spec-delta-template.md) only when a standalone proposal helps review. Reuse the existing authorized meaning and baseline evidence instead of creating a second approval document merely to follow a template.

