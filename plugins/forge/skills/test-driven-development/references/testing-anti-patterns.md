# Testing Anti-Patterns

**Read this when:** writing or changing tests, adding mocks or snapshots, testing async behavior, or whenever a test feels like it just mirrors the code.

**Core principle:** tests verify observable behavior. Not internal mechanics, not the mocks, not the passage of time.

## 1. Testing Implementation Details

**The violation:** asserting on private state, internal call order, or which helper got invoked.

```typescript
// BAD: breaks on any refactor, even when behavior is identical
expect(cart._items.length).toBe(2);
expect(spyOnRecalculate).toHaveBeenCalledTimes(1);

// GOOD: assert the observable outcome
expect(cart.totalPrice()).toBe(3400);
```

**Why it is wrong:** these tests protect the current structure, not the required behavior. Every refactor breaks them, so people stop trusting red tests — or stop refactoring.

**The fix:** assert through the public interface: inputs in, observable outputs and effects out. If a behavior can only be checked by peeking inside, the design is missing a seam — fix the design, not the test.

**Gate:** "If I refactored the internals without changing behavior, would this test still pass?" If no, rewrite the assertion.

## 2. Mocking What You Own

**The violation:** replacing your own classes or modules with mocks, then asserting the mock was called.

```typescript
// BAD: the real OrderService never runs; the test verifies the mock
const orderService = mock(OrderService);
checkout(cart, orderService);
expect(orderService.place).toHaveBeenCalled();

// GOOD: real objects for code you own; fake only the true boundary
const orderService = new OrderService(new InMemoryPaymentGateway());
const receipt = checkout(cart, orderService);
expect(receipt.status).toBe('paid');
```

**Why it is wrong:** you end up testing mock behavior. Integration bugs between your own components sail through green tests and surface in production.

**The fix:** mock only at boundaries you do not control — network, clock, filesystem, third-party services. Run real instances of your own code; if that is painful, the pain is telling you the coupling is too tight.

**Completeness rule:** when you must mock a boundary, mirror the complete real data structure, not just the fields your test touches. Partial mocks fail silently when downstream code reads an omitted field.

**Gate:** before mocking anything, ask "do I own this?" If yes, do not mock it. Then ask "does the test depend on a side effect of the real thing?" If unsure, run the test against the real implementation first and observe.

## 3. Assertion-Free Tests

**The violation:** a test that runs code and asserts nothing — or only asserts that no exception was thrown.

```typescript
// BAD: cannot fail meaningfully; pure coverage theater
test('processes the report', async () => {
  await generateReport(fixtureData);
});

// GOOD: states the expected outcome
test('report sums amounts per category', async () => {
  const report = await generateReport(fixtureData);
  expect(report.totals['food']).toBe(120_00);
});
```

**Why it is wrong:** coverage numbers rise while nothing is verified. The suite goes green whether the code is right or wrong.

**The fix:** every test asserts at least one concrete expected value or observable effect. If you cannot state the expected outcome, you do not understand the behavior yet — go back to RED and figure it out before coding.

## 4. Snapshot Overuse

**The violation:** giant serialized snapshots as the primary assertion, and failures "fixed" by regenerating the snapshot without reading the diff.

**Why it is wrong:** a snapshot is a change detector, not a behavior specification. Nobody reviews a 400-line snapshot diff, so wrong output gets snapshotted and locked in as "expected".

**The fix:**

- Prefer targeted assertions on the fields that matter.
- Keep any snapshot small enough that a reviewer can verify its correctness by reading it.
- Never update a snapshot without reading the diff and being able to explain, in one sentence, why the new output is correct.

## 5. Test Interdependence

**The violation:** tests that only pass in a certain order, or that share mutable state — module-level fixtures, a shared database row, leftover files on disk.

**Why it is wrong:** one failure cascades into many, single tests cannot be run in isolation, and parallel or shuffled runs turn flaky. Debugging starts with "which OTHER test broke this?"

**The fix:** each test builds its own world and tears it down. Every test must pass alone and in any order. If setup is expensive, share only truly immutable fixtures; anything a test mutates belongs to that test.

**Gate:** run the single test by itself. If it fails alone but passes in the suite (or the reverse), you have hidden coupling — fix it now.

## 6. Sleeping Instead of Waiting on Conditions

**The violation:** a fixed sleep to "give the async thing time to finish".

```typescript
// BAD: too short = flaky under load; long enough = slow suite
await sleep(2000);
expect(queue.size()).toBe(0);

// GOOD: wait on the actual condition, with a deadline
await waitFor(() => queue.size() === 0, { timeout: 2000 });
```

**Why it is wrong:** wall-clock time is not a synchronization primitive. The sleep that passes on your machine fails in CI, and the suite pays the full delay on every run even when the condition is met instantly.

**The fix:** await the promise or event directly; poll the condition with a deadline; use the test framework's wait-for utility; or inject a fake clock and advance it deterministically. A timeout is the failure bound, not the expected duration.

## Quick Reference

| Anti-pattern | Fix |
|--------------|-----|
| Testing implementation details | Assert observable behavior through the public interface |
| Mocking what you own | Real objects for owned code; mock only external boundaries, completely |
| Assertion-free tests | Every test states a concrete expected outcome |
| Snapshot overuse | Targeted assertions; snapshots small, reviewed, explained |
| Test interdependence | Each test owns its world; passes alone and in any order |
| Sleeping for async | Wait on the condition, not the clock |

## The Bottom Line

Strict RED-GREEN-REFACTOR prevents all six: writing the test first forces you to define observable behavior, and watching it fail proves the test exercises real code rather than mocks, snapshots, ordering luck, or timing.
