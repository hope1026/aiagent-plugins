export function aggregateFreshness(states) {
  if (states.includes('stale')) return 'stale';
  if (states.length > 0 && states.every((state) => state === 'current')) return 'current';
  return 'unverified';
}

export function sourceGroup(role) {
  if (role === 'comparison_spec') return 'comparison';
  if (['related_spec_context', 'declared_spec', 'repository_evidence'].includes(role)) return 'context';
  return ['primary_spec', 'brief_source', 'primary_plan', 'plan_progress', 'plan_task', 'project_map'].includes(role)
    ? 'primary'
    : null;
}

export function manifestSources(manifest) {
  return [...(manifest.member_sources || []), ...(manifest.document_sources || [])];
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

function frame(value) {
  const bytes = value instanceof Uint8Array ? value : new Uint8Array(value);
  const result = new Uint8Array(8 + bytes.byteLength);
  new DataView(result.buffer).setBigUint64(0, BigInt(bytes.byteLength));
  result.set(bytes, 8);
  return result;
}

export async function bundleSha256(bundlePath, members) {
  const encoder = new TextEncoder();
  const relativePath = (member) => memberRelativePath({
    ...member,
    bundle_path: member.bundle_path || bundlePath,
  });
  const ordered = [...members].sort((left, right) => {
    const leftPath = relativePath(left);
    const rightPath = relativePath(right);
    return leftPath < rightPath ? -1 : leftPath > rightPath ? 1 : 0;
  });
  const frames = [frame(encoder.encode(sourceMatchKey(bundlePath)))];
  ordered.forEach((member) => {
    frames.push(frame(encoder.encode(relativePath(member))));
    frames.push(frame(member.bytes));
  });
  const length = frames.reduce((total, value) => total + value.byteLength, 0);
  const payload = new Uint8Array(length);
  let offset = 0;
  frames.forEach((value) => {
    payload.set(value, offset);
    offset += value.byteLength;
  });
  return sha256Hex(payload);
}

export function sourceMatchKey(path) {
  return String(path).replace(/\\/g, '/').replace(/^\.\//, '').replace(/^\/+/, '');
}

export function sourceKey(source) {
  return String(source.key);
}

export function memberRelativePath(source) {
  const sourcePath = sourceMatchKey(source.path);
  const bundlePath = sourceMatchKey(source.bundle_path || '');
  const prefix = bundlePath ? `${bundlePath}/` : '';
  return prefix && sourcePath.startsWith(prefix) ? sourcePath.slice(prefix.length) : sourcePath;
}

export function selectedFileMatchesSource(source, file) {
  const selected = sourceMatchKey(file.webkitRelativePath || file.name || '');
  const relative = memberRelativePath(source);
  if (!selected || !relative) return false;
  return selected === sourceMatchKey(source.path)
    || selected === relative
    || selected.endsWith(`/${relative}`);
}

export function shouldAutoFetch(protocol) {
  return protocol === 'http:' || protocol === 'https:';
}

export function sourceUrl(source, sourceBase, locationHref) {
  return new URL(source.path, new URL(sourceBase, locationHref));
}

export async function verifyLocalSource(source, file) {
  if (!selectedFileMatchesSource(source, file)) {
    return {
      state: 'unverified',
      error: `select ${memberRelativePath(source)}`,
    };
  }
  try {
    const bytes = new Uint8Array(await file.arrayBuffer());
    const actual = await sha256Hex(bytes);
    return actual === source.sha256
      ? { state: 'current', actual, bytes }
      : { state: 'stale', actual, bytes, error: 'selected file SHA-256 differs' };
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
    const bytes = new Uint8Array(await response.arrayBuffer());
    const actual = await sha256Hex(bytes);
    return actual === source.sha256
      ? { state: 'current', actual, bytes }
      : { state: 'stale', actual, bytes, error: 'source SHA-256 differs' };
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

function renderAggregates(sources, results) {
  const states = results.map((result) => result.state);
  const groups = aggregateByGroup(sources, states);
  Object.entries(groups).forEach(([group, state]) => {
    const container = document.querySelector(`[data-freshness-group="${group}"]`);
    const target = container && container.querySelector('.freshness-state');
    if (target) setState(target, state);
  });
  const overallTarget = document.querySelector('[data-freshness-overall]');
  if (overallTarget) setState(overallTarget, aggregateFreshness(states));
}

async function applyBundleFreshness(manifest, sources, results) {
  for (const bundle of manifest.bundles || []) {
    const indexes = sources
      .map((source, index) => [source, index])
      .filter(([source]) => source.bundle_path === bundle.path)
      .map(([, index]) => index);
    if (!indexes.length || indexes.some((index) => !results[index].bytes)) continue;
    const members = indexes.map((index) => ({
      ...sources[index],
      bytes: results[index].bytes,
    }));
    if (await bundleSha256(bundle.path, members) !== bundle.sha256) {
      indexes.forEach((index) => {
        results[index] = { ...results[index], state: 'stale', error: 'bundle SHA-256 differs' };
      });
    }
  }
}

function installLocalPickers(manifest, sources, results) {
  document.querySelectorAll('[data-source-picker]').forEach((picker) => {
    const key = picker.getAttribute('data-source-key');
    const index = sources.findIndex((source) => sourceKey(source) === key);
    if (index < 0) return;
    picker.addEventListener('change', async () => {
      const file = picker.files && picker.files[0];
      const result = file
        ? await verifyLocalSource(sources[index], file)
        : { state: 'unverified', error: `select ${memberRelativePath(sources[index])}` };
      results[index] = result;
      await applyBundleFreshness(manifest, sources, results);
      results.forEach((item, itemIndex) => renderSource(sources[itemIndex], item));
      renderAggregates(sources, results);
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
  const sources = manifestSources(manifest);
  const results = sources.map(() => ({ state: 'unverified' }));
  renderAggregates(sources, results);
  installLocalPickers(manifest, sources, results);
  if (!shouldAutoFetch(location.protocol)) return;
  const fetched = await Promise.all(
    sources.map((source) => verifyFetchedSource(source, manifest.source_base, location.href)),
  );
  fetched.forEach((result, index) => { results[index] = result; });
  await applyBundleFreshness(manifest, sources, results);
  results.forEach((result, index) => renderSource(sources[index], result));
  renderAggregates(sources, results);
}

if (typeof document !== 'undefined') {
  initFreshness();
}
