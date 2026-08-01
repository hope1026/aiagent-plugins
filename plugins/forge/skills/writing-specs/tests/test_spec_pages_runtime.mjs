import assert from 'node:assert/strict';

import {
  aggregateRelationTargets,
  decodeCatalogValues,
  filterCatalog,
  normalizeHashTarget,
} from '../assets/spec-pages-runtime.mjs';


const records = [
  {
    id: '001-a',
    title: 'Alpha Parser',
    status: 'approved',
    kind: 'feature',
    areas: ['forge'],
    components: ['parser'],
  },
  {
    id: '002-b',
    title: 'Beta Viewer',
    status: 'draft',
    kind: 'policy',
    areas: ['docs'],
    components: ['viewer'],
  },
];

assert.deepEqual(
  filterCatalog(records, {
    query: 'ALPHA',
    status: 'approved',
    kind: '',
    area: '',
    component: '',
  }).map((item) => item.id),
  ['001-a'],
);
assert.deepEqual(
  filterCatalog(records, {
    query: 'viewer',
    status: '',
    kind: 'policy',
    area: 'docs',
    component: 'viewer',
  }).map((item) => item.id),
  ['002-b'],
);
assert.deepEqual(
  filterCatalog(records, {
    query: '',
    status: 'implemented',
    kind: '',
    area: '',
    component: '',
  }),
  [],
);

assert.equal(normalizeHashTarget('#acceptance'), 'acceptance');
assert.equal(normalizeHashTarget('#AC1'), 'acceptance');
assert.equal(normalizeHashTarget('#R22'), 'requirements');
assert.equal(normalizeHashTarget('#unknown'), 'overview');
assert.equal(normalizeHashTarget(''), 'overview');

assert.deepEqual(
  aggregateRelationTargets([
    { id: '002-b' },
    { id: '001-a' },
    { id: '001-a' },
    { id: '' },
  ]),
  ['001-a', '002-b'],
);

assert.deepEqual(
  decodeCatalogValues('["developer tools","parser"]'),
  ['developer tools', 'parser'],
);
assert.deepEqual(decodeCatalogValues('developer tools parser'), []);
assert.deepEqual(decodeCatalogValues('{"value":"developer tools"}'), []);
assert.deepEqual(decodeCatalogValues('["developer tools",7]'), []);

console.log('spec pages runtime tests: OK');
