export function aggregateFreshness(states) {
  if (states.includes('stale')) return 'stale';
  if (states.length > 0 && states.every((state) => state === 'current')) return 'current';
  return 'unverified';
}

export function sourceGroup(role) {
  if (role === 'comparison_spec') return 'comparison';
  if (role === 'related_spec_context') return 'context';
  return ['primary_spec', 'primary_plan', 'plan_progress', 'plan_task'].includes(role)
    ? 'primary'
    : null;
}

export function aggregateByGroup(sources, states) {
  const grouped = { primary: [], comparison: [], context: [] };
  sources.forEach((source, index) => {
    const group = sourceGroup(source.role);
    if (group) grouped[group].push(states[index] ?? 'unverified');
  });
  return Object.fromEntries(
    Object.entries(grouped).map(([group, values]) => [group, aggregateFreshness(values)]),
  );
}

export async function sha256Hex(bytes) {
  const buffer = bytes instanceof ArrayBuffer
    ? bytes
    : bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  const digest = await globalThis.crypto.subtle.digest('SHA-256', buffer);
  return Array.from(new Uint8Array(digest), (value) => value.toString(16).padStart(2, '0')).join('');
}

export function sourceMatchKey(path) {
  return String(path).replace(/\\/g, '/').replace(/^\.\//, '').replace(/^\/+/, '');
}

export function sourceKey(source) {
  return `${String(source.namespace)}:${sourceMatchKey(source.path)}`;
}

export function shouldAutoFetch(protocol) {
  return protocol === 'http:' || protocol === 'https:';
}

export function sourceUrl(source, sourceBase, locationHref) {
  return new URL(source.path, new URL(sourceBase, locationHref));
}

export async function verifyLocalSource(source, file) {
  try {
    const actual = await sha256Hex(await file.arrayBuffer());
    return actual === source.sha256
      ? { state: 'current', actual }
      : { state: 'stale', actual, error: 'selected file SHA-256 differs' };
  } catch (error) {
    return { state: 'unverified', error: String(error && error.message || error) };
  }
}

export async function verifyFetchedSource(source, sourceBase, locationHref) {
  try {
    const locationUrl = new URL(locationHref);
    const url = sourceUrl(source, sourceBase, locationHref);
    if (!['http:', 'https:'].includes(locationUrl.protocol) || url.origin !== locationUrl.origin) {
      return { state: 'unverified', error: 'same-origin HTTP source access unavailable' };
    }
    const response = await fetch(url, { cache: 'no-store' });
    if (!response.ok) {
      return { state: 'unverified', error: `source fetch failed: HTTP ${response.status}` };
    }
    const actual = await sha256Hex(await response.arrayBuffer());
    return actual === source.sha256
      ? { state: 'current', actual }
      : { state: 'stale', actual, error: 'source SHA-256 differs' };
  } catch (error) {
    return { state: 'unverified', error: String(error && error.message || error) };
  }
}

function readManifest() {
  const element = document.getElementById('forge-source-manifest');
  if (!element) throw new Error('source manifest not found');
  return JSON.parse(element.textContent);
}

function sourceRow(key) {
  return document.querySelector(`[data-source-key="${CSS.escape(key)}"]`);
}

function setState(target, state) {
  target.textContent = state;
  target.className = `freshness-state freshness-${state}`;
}

function renderSource(source, result) {
  const row = sourceRow(sourceKey(source));
  if (!row) return;
  const state = row.querySelector('[data-source-state]');
  const error = row.querySelector('[data-source-error]');
  if (state) setState(state, result.state);
  if (error) error.textContent = result.error || '';
}

function renderAggregates(manifest, results) {
  const states = results.map((result) => result.state);
  const groups = aggregateByGroup(manifest.sources, states);
  Object.entries(groups).forEach(([group, state]) => {
    const container = document.querySelector(`[data-freshness-group="${group}"]`);
    const target = container && container.querySelector('.freshness-state');
    if (target) setState(target, state);
  });
  const overallTarget = document.querySelector('[data-freshness-overall]');
  if (overallTarget) setState(overallTarget, aggregateFreshness(states));
}

function installLocalPickers(manifest, results) {
  document.querySelectorAll('[data-source-picker]').forEach((picker) => {
    const key = picker.getAttribute('data-source-key');
    const index = manifest.sources.findIndex((source) => sourceKey(source) === key);
    if (index < 0) return;
    picker.addEventListener('change', async () => {
      const file = picker.files && picker.files[0];
      const result = file
        ? await verifyLocalSource(manifest.sources[index], file)
        : { state: 'unverified', error: 'matching local file not selected' };
      results[index] = result;
      renderSource(manifest.sources[index], result);
      renderAggregates(manifest, results);
    });
  });
}

async function initFreshness() {
  let manifest;
  try {
    manifest = readManifest();
  } catch (error) {
    const target = document.querySelector('[data-freshness-overall]');
    if (target) setState(target, 'unverified');
    return;
  }
  const results = manifest.sources.map(() => ({ state: 'unverified' }));
  renderAggregates(manifest, results);
  installLocalPickers(manifest, results);
  if (!shouldAutoFetch(location.protocol)) return;
  const fetched = await Promise.all(
    manifest.sources.map((source) => verifyFetchedSource(
      source,
      manifest.source_base,
      location.href,
    )),
  );
  fetched.forEach((result, index) => {
    results[index] = result;
    renderSource(manifest.sources[index], result);
  });
  renderAggregates(manifest, results);
}

if (typeof document !== 'undefined') {
  initFreshness();
}
