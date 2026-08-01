import assert from 'node:assert/strict';
import * as freshness from '../assets/viewer-freshness.mjs';

const {
  aggregateFreshness,
  sha256Hex,
  shouldAutoFetch,
  sourceMatchKey,
  verifyLocalSource,
} = freshness;

assert.equal(typeof freshness.sourceKey, 'function', 'sourceKey must namespace path identity');
assert.equal(typeof freshness.aggregateByGroup, 'function', 'group freshness must remain independent');
assert.equal(typeof freshness.sourceUrl, 'function', 'HTTP URLs must resolve through source_base');

assert.equal(aggregateFreshness(['current', 'current']), 'current');
assert.equal(aggregateFreshness(['current', 'unverified']), 'unverified');
assert.equal(aggregateFreshness(['current', 'missing']), 'unverified');
assert.equal(aggregateFreshness(['malformed']), 'unverified');
assert.equal(aggregateFreshness(['unverified', 'stale']), 'stale');
assert.equal(aggregateFreshness([]), 'unverified');
assert.equal(
  await sha256Hex(new TextEncoder().encode('abc')),
  'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',
);
assert.equal(sourceMatchKey('./tasks/001-api.md'), 'tasks/001-api.md');
assert.equal(sourceMatchKey('tasks\\001-api.md'), 'tasks/001-api.md');
assert.equal(
  freshness.sourceKey({ namespace: 'context--001-alpha', path: 'docs/specs/001-alpha/spec.md' }),
  'context--001-alpha:docs/specs/001-alpha/spec.md',
);
assert.deepEqual(
  freshness.aggregateByGroup([
    { role: 'primary_plan' },
    { role: 'plan_task' },
    { role: 'related_spec_context' },
  ], ['current', 'unverified', 'stale']),
  { primary: 'unverified', comparison: 'unverified', context: 'stale' },
);
assert.equal(
  freshness.sourceUrl(
    { path: 'docs/specs/001-alpha/spec.md' },
    '../../../',
    'http://127.0.0.1:4173/.forge/reviews/demo/view.html',
  ).href,
  'http://127.0.0.1:4173/docs/specs/001-alpha/spec.md',
);
assert.equal(shouldAutoFetch('file:'), false);
assert.equal(shouldAutoFetch('http:'), true);
assert.equal(shouldAutoFetch('https:'), true);

const abcSource = {
  path: 'spec.md',
  sha256: 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',
};
const localCurrent = await verifyLocalSource(abcSource, {
  arrayBuffer: async () => new TextEncoder().encode('abc').buffer,
});
assert.equal(localCurrent.state, 'current');
const localStale = await verifyLocalSource(abcSource, {
  arrayBuffer: async () => new TextEncoder().encode('changed').buffer,
});
assert.equal(localStale.state, 'stale');

console.log('test-viewer-freshness: all checks passed');
