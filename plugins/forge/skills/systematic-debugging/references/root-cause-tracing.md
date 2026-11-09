# Root-Cause Tracing

Backward tracing from a symptom to the first wrong state. Use this optional technique when tracing is useful during the forge systematic-debugging skill.

## Core Principle

Bugs usually surface far from where they were caused: the crash is deep in a library call, but the bad value entered the system many frames earlier. Fixing where the error *appears* treats a symptom. Trace backward through the chain of calls and data until you find the **first wrong state** — the earliest point where reality diverged from correct — then choose a correction boundary based on the responsible contracts and evidence.

## First-Wrong-State Discipline

At every step of the trace, ask one question: **"Was the state already wrong when it arrived here, or did this code make it wrong?"**

- Already wrong on arrival → trace the producer and check whether the receiving boundary was also responsible for rejecting or handling that input.
- Became wrong here → investigate why and whether this boundary violated its contract.

Choose the correction at the boundary responsible for the violated contract. More than one boundary can require a correction; an observed first wrong state alone does not establish responsibility.

## The Tracing Process

1. **Observe the symptom precisely.** The exact error, the exact wrong output, the exact location.
2. **Find the immediate cause.** Which statement directly produced the symptom? What were its actual inputs at that moment?
3. **Ask: who called this, with what?** Walk one level up the stack or one step back in the data flow. Check the value at that level.
4. **Keep walking up** while the value is already wrong on arrival. Cross boundaries when needed — function to caller, module to importer, process to config, code to test fixture.
5. **Name the original trigger.** The place where correct became wrong: an unvalidated input, a wrong default, an ordering assumption, setup code that ran too early or not at all.

### Worked example

- **Symptom:** files are created in the source tree during tests.
- **Immediate cause:** a workspace-setup routine runs with an empty `baseDir` argument, and an empty path resolves to the current working directory.
- **One level up:** the session factory passed `baseDir` straight through — already empty on arrival. Check its contract.
- **Two levels up:** the test read a `tempDir` field from a shared helper *before* the per-test setup hook had populated it — the helper's initial value is the empty string. **Correct became wrong here.**
- **Root cause:** top-level access to a value that only becomes valid after setup runs.
- **Correction:** make the helper fail loudly when read before setup. If the workspace routine also promises to reject empty paths, enforce that contract there too.

## Instrumentation Patterns

When the chain cannot be traced by reading code, make the program tell you.

- **Log before the dangerous operation, not after it fails.** Once it throws, the interesting state may be gone.
- **Log safe context:** record only necessary, sanitized or redacted values and metadata, such as a timestamp. Do not log raw secrets, credentials, tokens, or sensitive environment values.
- **Capture the call chain.** Most runtimes can produce a stack trace on demand (for example, constructing an error object just to read its stack). Sanitize it before logging so each occurrence can identify its trigger without exposing sensitive data.
- **Write to a channel that cannot be swallowed.** Test frameworks and loggers often suppress normal output; use the standard error stream for temporary diagnostics.
- **Make each log line greppable.** Prefix with a distinctive marker (such as `DEBUG-TRACE`) so you can filter the full run output down to your evidence in one search.
- **Boundary logging in multi-component systems:** at relevant component boundaries, log safe summaries of what enters and exits. Use the reproduction to identify where the data becomes wrong and focus the trace there.
- **Remove temporary probes** when no longer needed. Keep useful durable diagnostics only when safe, appropriate, and justified; keep disposable scaffolding in `.forge/scratch/`.

## Finding a Trigger by Bisection

When a symptom appears only after many operations, define a reproducible failure predicate and reset state between trials. Preserve relevant order and setup. Test prefixes, subsets, and complements as appropriate: an absent symptom in one half does not prove the other half contains a standalone trigger, because operations may interact or depend on prior state. Reduce the sequence only while the predicate still reproduces, then trace the remaining interaction. Commit bisection similarly requires a reproducible predicate and comparable environments.

## Choosing the Correction

Fix the responsible contract boundary when evidence supports it. If the root cause cannot yet be confirmed, an authorized, evidence-supported mitigation may be appropriate; describe what it improves and what remains unresolved. Do not present a symptom guard as a confirmed root-cause fix.
