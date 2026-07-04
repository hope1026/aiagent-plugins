# Root-Cause Tracing

Backward tracing from a symptom to the first wrong state. Read this during Phase 3 of the forge systematic-debugging skill.

## Core Principle

Bugs usually surface far from where they were caused: the crash is deep in a library call, but the bad value entered the system many frames earlier. Fixing where the error *appears* treats a symptom. Trace backward through the chain of calls and data until you find the **first wrong state** — the earliest point where reality diverged from correct — and fix there.

## First-Wrong-State Discipline

At every step of the trace, ask one question: **"Was the state already wrong when it arrived here, or did this code make it wrong?"**

- Already wrong on arrival → this frame is innocent; go one level up (the caller, the producer, the config loader, the test setup).
- Became wrong here → you found the source. Stop tracing; this is where the fix belongs.

Repeat until the answer flips. The frame where "arrived correct, left wrong" is the root cause site. Everything below it is symptom territory — guards added there only hide the source.

## The Tracing Process

1. **Observe the symptom precisely.** The exact error, the exact wrong output, the exact location.
2. **Find the immediate cause.** Which statement directly produced the symptom? What were its actual inputs at that moment?
3. **Ask: who called this, with what?** Walk one level up the stack or one step back in the data flow. Check the value at that level.
4. **Keep walking up** while the value is already wrong on arrival. Cross boundaries when needed — function to caller, module to importer, process to config, code to test fixture.
5. **Name the original trigger.** The place where correct became wrong: an unvalidated input, a wrong default, an ordering assumption, setup code that ran too early or not at all.

### Worked example

- **Symptom:** files are created in the source tree during tests.
- **Immediate cause:** a workspace-setup routine runs with an empty `baseDir` argument, and an empty path resolves to the current working directory.
- **One level up:** the session factory passed `baseDir` straight through — already empty on arrival. Innocent.
- **Two levels up:** the test read a `tempDir` field from a shared helper *before* the per-test setup hook had populated it — the helper's initial value is the empty string. **Correct became wrong here.**
- **Root cause:** top-level access to a value that only becomes valid after setup runs.
- **Fix at source:** make the helper fail loudly when the field is read before setup — not a fallback path in the workspace routine (that would be a symptom guard).

## Instrumentation Patterns

When the chain cannot be traced by reading code, make the program tell you.

- **Log before the dangerous operation, not after it fails.** Once it throws, the interesting state may be gone.
- **Log actual values with context:** the suspect argument, the working directory, relevant environment values, a timestamp.
- **Capture the call chain.** Most runtimes can produce a stack trace on demand (for example, constructing an error object just to read its stack). Attach it to the log line so each occurrence names its trigger.
- **Write to a channel that cannot be swallowed.** Test frameworks and loggers often suppress normal output; use the standard error stream for temporary diagnostics.
- **Make each log line greppable.** Prefix with a distinctive marker (such as `DEBUG-TRACE`) so you can filter the full run output down to your evidence in one search.
- **Boundary logging in multi-component systems:** for each component boundary, log what enters and what exits. One run of the reproduction then shows the first boundary where the data is wrong — that is where to focus the trace.
- **Remove all instrumentation** once the root cause is confirmed. Debug scaffolding belongs in `.forge/scratch/`, never in the change you ship.

## Finding a Trigger by Bisection

When a symptom appears only after many operations (a polluted test run, a corrupted cache) and you do not know which operation causes it:

1. Run half of the operations. Symptom present → the trigger is in that half; absent → the other half.
2. Recurse until one operation remains — that is your trigger, and the trace starts from it.

The same halving works across commits (version-control bisection), across input records, and across test files run one at a time.

## Key Rule

**Never fix only where the error appears.** After fixing at the source, it is fine to *also* add validation at intermediate layers — but defense-in-depth is a supplement to the source fix, never a substitute for it.
