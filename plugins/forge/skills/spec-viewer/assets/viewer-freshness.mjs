export function aggregateFreshness(states) {
  if (states.includes('stale')) return 'stale';
  if (states.length > 0 && states.every((state) => state === 'current')) return 'current';
  return 'unverified';
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

export function shouldAutoFetch(protocol) {
  return protocol === 'http:' || protocol === 'https:';
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

export async function verifyFetchedSource(source, baseUrl) {
  try {
    const url = new URL(source.path, baseUrl);
    const base = new URL(baseUrl);
    if (!['http:', 'https:'].includes(base.protocol) || url.origin !== base.origin) {
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

function sourceRow(path) {
  return document.querySelector(`[data-source-path="${CSS.escape(path)}"]`);
}

function renderSource(path, result) {
  const row = sourceRow(path);
  if (!row) return;
  const state = row.querySelector('[data-source-state]');
  const error = row.querySelector('[data-source-error]');
  state.textContent = result.state;
  state.className = `freshness-state freshness-${result.state}`;
  error.textContent = result.error || '';
}

function renderOverall(results) {
  const overall = aggregateFreshness(results.map((result) => result.state));
  const target = document.querySelector('[data-freshness-overall]');
  if (target) {
    target.textContent = overall;
    target.className = `freshness-state freshness-${overall}`;
  }
}

function matchFile(source, sources, files) {
  const key = sourceMatchKey(source.path);
  const exact = files.filter((file) => {
    const candidate = sourceMatchKey(file.webkitRelativePath || file.name);
    return candidate === key || candidate.endsWith(`/${key}`);
  });
  if (exact.length === 1) return exact[0];
  const basename = key.split('/').pop();
  const basenameIsUnique = sources.filter(
    (item) => sourceMatchKey(item.path).split('/').pop() === basename,
  ).length === 1;
  if (!basenameIsUnique) return null;
  const byName = files.filter((file) => file.name === basename);
  return byName.length === 1 ? byName[0] : null;
}

async function verifySelectedFiles(manifest, fileList) {
  const files = Array.from(fileList);
  const results = [];
  for (const source of manifest.sources) {
    const file = matchFile(source, manifest.sources, files);
    if (!file) {
      const result = { state: 'unverified', error: 'matching local file not selected' };
      renderSource(source.path, result);
      results.push(result);
      continue;
    }
    const result = await verifyLocalSource(source, file);
    renderSource(source.path, result);
    results.push(result);
  }
  renderOverall(results);
}

async function initFreshness() {
  let manifest;
  try {
    manifest = readManifest();
  } catch (error) {
    renderOverall([{ state: 'unverified', error: String(error) }]);
    return;
  }
  const initial = manifest.sources.map(() => ({ state: 'unverified' }));
  renderOverall(initial);
  if (shouldAutoFetch(location.protocol)) {
    const results = await Promise.all(
      manifest.sources.map((source) => verifyFetchedSource(source, location.href)),
    );
    manifest.sources.forEach((source, index) => renderSource(source.path, results[index]));
    renderOverall(results);
  }
  const picker = document.getElementById('forge-source-picker');
  if (picker) {
    picker.addEventListener('change', () => verifySelectedFiles(manifest, picker.files));
  }
}

if (typeof document !== 'undefined') {
  initFreshness();
}
