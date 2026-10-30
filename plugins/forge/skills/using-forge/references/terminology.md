# Terminology and Naming

Use when introducing a domain concept, choosing a consequential identifier, or
changing a name whose meaning is shared across work. This is Forge's shared
naming guidance. Other skills apply it rather than maintaining another policy.
The forge writing-tone skill owns how to express the resulting explanation.

## Establish the concept before its name

Describe what the concept represents and the boundary that distinguishes it.
Inspect the relevant approved contracts, implementation, tests and consumers.
Use responsibility, lifetime, state, inputs or results where they distinguish
the concept; do not invent fields just to complete a form.

Compare nearby concepts before selecting a name. Reuse an established name for
the same concept in the same context. Preserve distinctions between different
concepts even when their current implementations look alike. A shared word in
different domains can be valid when its context is clear; global uniqueness is
not the objective. State the difference when a reader could confuse the terms.

For example, a scheduling domain might distinguish a reusable job definition,
one run of that job, and an attempt within the run. `Job`, `JobRun` and `Attempt`
are illustrative choices, not universal names or a required model. Inspect the
project's actual retry and lifetime boundaries before adopting any of them.

## Check fit and established usage

For core design terms and public identifiers, compare candidates with relevant
standards, official documentation for the technology in use, and inspected
project usage. Keep the evidence near a consequential naming decision. Say when
a name is project-specific or evidence is insufficient; do not describe a
familiar-sounding name as an industry convention without support. Routine local
variables do not require external research.

Preserve approved project meaning when an external convention differs. Explain
the discrepancy and resolve a material contract change through the forge
writing-specs skill. Existing ambiguous names can be improved within authorized
scope; neither familiarity nor popularity proves semantic fit.

Consider adjacent concepts, affected consumers and already planned extensions.
Avoid a name narrower than the known responsibility or broader than its actual
scope. Do not create abstractions, types or vocabulary solely for hypothetical
future features. Use explicit qualifiers where they expose a real distinction;
do not hide an undefined responsibility behind a generic label.

## Check what the name promises at its use site

Read a representative call site as well as the declaration. Can a reader infer
the target and responsibility without reconstructing a long explanation? Match
the name to actual behavior: a read-like name must not conceal creation or
mutation, and a partial check must not imply full validation or authorization.
For example, `verifyLicenseSignature` describes a signature-only check more
precisely than `validateLicense`; neither name proves current access is allowed.

Expose scope, state and units when they prevent a real misunderstanding, such
as request-scoped reuse, cached versus current data, or milliseconds versus
seconds. Qualifiers like `verified` must identify what was verified when the
context does not make it clear. Judge generic words such as `data`, `manager`
and `valid` in context; replace them with the actual target, responsibility or
condition when ambiguous. Do not impose prefixes, suffixes or longer names on
every local identifier.

## Keep definitions in their owning source

Reuse the project's existing authoritative definition. For a durable shared
concept, keep its definition in the relevant approved Canonical Spec through
the forge writing-specs skill. Describe the preferred term, meaning and scope,
nearby distinctions, and code-identifier or translation mappings where needed.
Examples or counterexamples should resolve actual ambiguity. No global glossary,
separate terminology file, or per-variable Spec is required.

Plans, handoffs, replies and requested views refer to that definition. A local
reading aid may summarize it with a source link but is not maintained as a
second authoritative glossary. Mark a proposed concept as proposed. Explain
display-name and identifier mappings; preserve exact external identifiers,
protocol values and quotations. Different abstraction levels need not share a
name simply because a view places them together.

Specs reuse existing owning definitions and preferred terms. Plans retain the
referenced Spec's terms for the same concepts rather than substituting synonyms,
abbreviations or translations. When implementation needs a more specific name,
explain its mapping to the Spec concept. For example, a plan can map license
revocation to `revokeLicense()`; calling it license deletion would suggest a
different operation. Resolve an ambiguous definition or changed meaning in its
owning Spec within authorization before relying on it in the dependent plan;
do not silently redefine it there. Independent authorized work can continue.

When renaming a public API, persisted field or other external contract, inspect
consumers and authorized compatibility, migration and verification needs before
changing it. A local rename does not authorize a contract migration.

## Check meaning across the result

Compare affected code, tests, Specs, Plans, replies, tables and diagram labels.
Look for both one concept split across accidental synonyms and different
concepts hidden behind one name. Search assists this review; identical strings
alone do not prove identical meaning. For a representative change, ask a
separate reader to classify examples, distinguish nearby concepts and explain
their conditions from the delivered explanation. Report agent-reader evidence
as such. Preserve unresolved definitions as uncertainty instead of inventing a
settled meaning to finish the document.
