# Error Identity and Cause Preservation

Use when implementing, changing, or evaluating error handling at API, DB or
external-service boundaries, including wrappers, adapters and shared handlers.
Follow the affected project's existing code, response and diagnostic contracts.
Unrelated work needs no error-system redesign, new logging infrastructure or
global error catalog.

## Preserve distinctions that change response or diagnosis

Inspect the failure paths and their consumers before defining or mapping codes.
Keep failures distinguishable when caller action or operational diagnosis
differs. Authentication expiry, denied access, rate limiting, transport failure
and malformed upstream responses must not survive only as one generic
`API_ERROR`. Common handling and an authorized generic public response are
compatible with retaining those distinctions in internal structured diagnostics.

Use one code for the same meaning and separate codes for materially different
meanings within the project's scope. Follow existing naming conventions and
definitions; symbolic names such as `AUTH_TOKEN_EXPIRED` or
`PAYMENT_PROVIDER_TIMEOUT` are examples, not a required prefix or format.
Do not allocate a new code for every throw site or embed request IDs, timestamps
or dynamic message text in a code. An HTTP status or display message alone may
not distinguish the failures that matter to consumers and diagnosis.

Keep code meanings stable when messages or implementation locations change.
Do not reuse a retired code for a different meaning. Maintain the meaning,
trigger conditions, caller response and disclosure scope in the existing owning
definitions, types, API documentation or Canonical Spec as appropriate; a
separate registry is not mandatory. Inspect consumers and use the forge
writing-specs skill when public codes or their meaning, retry or recovery
behavior change a durable contract. A local identifier needs no new Spec.

## Retain cause and occurrence context through shared handling

When wrapping or translating an error, preserve a safe cause chain or an
equivalent diagnostic link, the operation that failed, and relevant upstream
code, status and request ID when available. A many-to-one mapping must still
leave enough internal context to distinguish the underlying failures. Do not
invent a root cause when only a symptom is known.

An error code identifies a kind of failure. A request ID, trace ID or equivalent
diagnostic identifier locates the affected request or occurrence; it is not a
new error code. Reuse and propagate the project's existing correlation context
across relevant calls and diagnostics, and provide a safe way to connect a
reported failure to its evidence. Use the actual protocol and boundary; no
dedicated distributed tracing system or universal response field is required.

Unexpected errors may use a fallback code, but retain safe diagnostic context
and a way to locate the occurrence. Do not turn an unknown error or uncertain
write outcome into success, empty data or confirmed absence. Follow the owning
retry and reconciliation contract; a timeout code alone does not prove that
repeating a side effect is safe.

## Separate public information from protected diagnostics

Display messages may be shared by several error kinds. Public responses follow
the approved disclosure contract; do not expose secrets, tokens, personal data
or internal stacks. Protected diagnostics also minimize and redact sensitive
values. Cause preservation does not require storing complete raw requests,
responses or exception dumps. Existing cause links and one suitable diagnostic
boundary can suffice; duplicate logging at every layer is not required.

## Verify the affected failure paths

Exercise representative failures through the changed wrapper, mapping and
shared handler. Use existing tests or controlled fault injection. Select cases
that demonstrate the distinctions at risk, stable identity for the same meaning
at different sites, fallback behavior, correlation to safe cause context and
disclosure boundaries where affected. Checking a list of codes or message text
alone does not prove that the path preserves these properties.

Match verification to the change; do not require every failure combination or
introduce a testing framework for a small repair. State unobserved paths and
remaining uncertainty accurately. The forge verifying-work skill owns the
completion claim.
