import assert from 'node:assert/strict';
import {
  aggregateFreshness,
  sha256Hex,
  shouldAutoFetch,
  sourceMatchKey,
  verifyLocalSource,
} from '../assets/viewer-freshness.mjs';

assert.equal(aggregateFreshness(['current', 'current']), 'current');
assert.equal(aggregateFreshness(['current', 'unverified']), 'unverified');
assert.equal(aggregateFreshness(['unverified', 'stale']), 'stale');
assert.equal(aggregateFreshness([]), 'unverified');
assert.equal(
  await sha256Hex(new TextEncoder().encode('abc')),
  'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',
);
assert.equal(sourceMatchKey('./tasks/001-api.md'), 'tasks/001-api.md');
assert.equal(sourceMatchKey('tasks\\001-api.md'), 'tasks/001-api.md');
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
