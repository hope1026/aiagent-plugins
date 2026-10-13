# Recommended Structure Views

Use these patterns when they answer the reader's question in a requested Forge
visualization. They are guidance for choosing and explaining content, not a
template, required section inventory or bundled renderer. A short policy
explanation may need neither pattern.

## Component and Connection Diagrams

A diagram should let the reader identify the important components, what connects
them and which boundary a connection crosses.

- Name nodes with source-supported service, module or resource identifiers. Add
  a short role or code path when it helps explain the component.
- Group nodes by meaningful deployment, ownership or trust boundaries supported
  by the sources. State what each boundary means.
- Label arrows with their meaning and direction: request, storage access,
  dependency, event production or event consumption. A return value does not
  automatically establish a reverse service dependency.
- Explain line styles and symbols in a legend or nearby text. Distinguish
  conditional or proposed connections with labels as well as visual styling.
- Separate physical deployment, logical behavior and code dependencies when a
  combined diagram makes those meanings hard to distinguish. For a dense system,
  separate core resources, administration and external integrations when useful.
- Keep important qualifications near the diagram. Identify whether it describes
  an approved design, inspected implementation or observed deployment, and give
  the source or inspection basis when relevant.

For example, a source may establish that a billing service owns its database,
produces and consumes its own queue, then calls a license service. Explain those
as separate labeled connections; do not imply that the license service consumes
the queue. An optional external integration should retain its activation
condition. These are illustrative facts, not requirements for other projects.

Use Mermaid, authored SVG or another suitable format. A small diagram can remain
static. Larger diagrams may benefit from fit/reset, zoom and panning, or separate
views. Keep labels readable and provide a nearby textual explanation or table
where the diagram alone leaves important relationships unclear. Useful detail
links may point to a component's code explanation or source statement.

## Folder Trees with Responsibilities

A folder explanation should help the reader locate a behavior and understand
the boundary affected by a change.

Inspect the relevant repository paths and supporting source before describing
the current structure. A path name alone does not establish responsibility or
ownership. If the source describes a future layout, label it as proposed rather
than implying that those paths exist.

Select important paths instead of copying a complete directory listing. Put a
concrete responsibility beside each selected folder or file. Include entry
points, adapters, migrations, shared packages or operational scripts where they
help the task. Omit generated output and dependency folders unless they are
the subject of the explanation.

This illustrative layout shows the level of explanation to aim for; it does not
prescribe a project structure:

```text
project/
├── billing-service/          Billing runtime and owned purchase records
│   ├── src/routes/           HTTP input validation and routing
│   ├── src/delivery.ts       License delivery and retry handling
│   └── migrations/           Billing database schema changes
├── packages/protocol/        Shared request and response contracts
└── scripts/release/          Deployment configuration and release checks
```

Explain mappings when folder names and deployed component names differ. Shared
packages can be included in several runtimes without being independently
deployed. Describe actual mixed file and folder arrangements rather than
rewriting them into an idealized uniform architecture.

When the tree is insufficient, add a compact table with the fields the reader
needs, such as path, responsibility, entry point or change boundary. For a
handoff, explain relevant dependency direction and what adjacent contract needs
checking when that code changes. Avoid making every possible field mandatory.

## Connect and Verify the Explanations

When both patterns help, let the reader move from a diagram component to its
folder explanation and relevant source. Stable anchors or ordinary links can
provide this connection; interaction is optional for a short static explanation.

Check the affected meaning against the sources and repository:

- Do connection directions, labels and conditions match the supported facts?
- Do selected paths exist when presented as current, and do descriptions match
  the code or source that was actually inspected?
- Are source folders, runtime units and storage resources distinguishable?
- Do component names, path mappings and links agree across the explanations?
- Can the reader identify a relevant connection and locate its implementation?

Inspect the delivered surface for readable labels, overlapping arrows or text,
and working links and controls. Check narrower layouts when the complexity
warrants it. Report the actual verification scope; repository checks alone do
not establish live deployment state.
