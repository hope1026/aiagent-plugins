import assert from 'node:assert/strict';
import * as freshness from '../assets/viewer-freshness.mjs';

const {
  aggregateFreshness,
  bundleSha256,
  manifestSources,
  memberRelativePath,
  sha256Hex,
  shouldAutoFetch,
  sourceMatchKey,
  verifyLocalSource,
} = freshness;

assert.equal(typeof freshness.sourceKey, 'function', 'sourceKey must use the internal manifest key');
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
  freshness.sourceKey({ key: 'source-5f1c', path: 'docs/specs/example/member.md' }),
  'source-5f1c',
);
assert.equal(
  memberRelativePath({
    bundle_path: 'docs/specs/example',
    path: 'docs/specs/example/member.md',
  }),
  'member.md',
);
assert.deepEqual(
  manifestSources({
    member_sources: [{ key: 'member' }],
    document_sources: [{ key: 'plan' }],
  }).map((source) => source.key),
  ['member', 'plan'],
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
    { path: 'docs/specs/example-bundle/member.md' },
    '../../../',
    'http://127.0.0.1:4173/.forge/visual-docs/demo/view.html',
  ).href,
  'http://127.0.0.1:4173/docs/specs/example-bundle/member.md',
);
assert.equal(shouldAutoFetch('file:'), false);
assert.equal(shouldAutoFetch('http:'), true);
assert.equal(shouldAutoFetch('https:'), true);

const abcSource = {
  bundle_path: 'docs/specs/example',
  path: 'docs/specs/example/member.md',
  sha256: 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',
};
const localCurrent = await verifyLocalSource(abcSource, {
  name: 'member.md',
  arrayBuffer: async () => new TextEncoder().encode('abc').buffer,
});
assert.equal(localCurrent.state, 'current');
const localStale = await verifyLocalSource(abcSource, {
  name: 'member.md',
  arrayBuffer: async () => new TextEncoder().encode('changed').buffer,
});
assert.equal(localStale.state, 'stale');
const wrongMember = await verifyLocalSource(abcSource, {
  name: 'different.md',
  arrayBuffer: async () => new TextEncoder().encode('abc').buffer,
});
assert.equal(wrongMember.state, 'unverified');
assert.match(wrongMember.error, /member.md/);

assert.equal(
  await bundleSha256('docs/specs/demo', [{
    path: 'docs/specs/demo/root.md',
    bytes: new TextEncoder().encode('abc'),
  }]),
  '9b984d9d8bf0cafe0808ca2f5ba7aee9ba119ecf94ece7b63fa724ae572d7dfe',
);

console.log('test-visual-docs-freshness: all checks passed');
