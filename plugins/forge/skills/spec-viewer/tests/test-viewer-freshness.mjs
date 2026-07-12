import assert from 'node:assert/strict';
import {
  aggregateFreshness,
  sha256Hex,
  sourceMatchKey,
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

console.log('test-viewer-freshness: all checks passed');
