const SECTION_IDS = new Set([
  'overview',
  'flows',
  'requirements',
  'data',
  'acceptance',
  'history',
]);


function normalized(value) {
  return String(value ?? '').trim().toLocaleLowerCase('en');
}


export function filterCatalog(records, filters) {
  const query = normalized(filters.query);
  const status = normalized(filters.status);
  const kind = normalized(filters.kind);
  const area = normalized(filters.area);
  const component = normalized(filters.component);
  return records.filter((record) => {
    const searchable = normalized(`${record.id} ${record.title}`);
    return (
      (!query || searchable.includes(query))
      && (!status || normalized(record.status) === status)
      && (!kind || normalized(record.kind) === kind)
      && (!area || (record.areas ?? []).some((item) => normalized(item) === area))
      && (!component || (record.components ?? []).some((item) => normalized(item) === component))
    );
  });
}


export function normalizeHashTarget(hash) {
  let target;
  try {
    target = decodeURIComponent(String(hash ?? '').replace(/^#/, ''));
  } catch {
    return 'overview';
  }
  if (SECTION_IDS.has(target)) {
    return target;
  }
  if (/^R\d+$/.test(target)) {
    return 'requirements';
  }
  if (/^AC\d+$/.test(target)) {
    return 'acceptance';
  }
  return 'overview';
}


export function aggregateRelationTargets(relations) {
  return [...new Set(relations.map((item) => item.id).filter(Boolean))].sort();
}


export function decodeCatalogValues(value) {
  try {
    const parsed = JSON.parse(String(value ?? ''));
    return Array.isArray(parsed) && parsed.every((item) => typeof item === 'string')
      ? parsed
      : [];
  } catch {
    return [];
  }
}


function catalogRecords(document) {
  return [...document.querySelectorAll('.catalog-entry')].map((element) => ({
    areas: decodeCatalogValues(element.dataset.areas),
    components: decodeCatalogValues(element.dataset.components),
    element,
    id: element.dataset.specId ?? '',
    kind: element.dataset.kind ?? '',
    status: element.dataset.status ?? '',
    title: element.querySelector('h2')?.textContent ?? '',
  }));
}


function catalogFilters(form) {
  return {
    query: form.elements.namedItem('query')?.value ?? '',
    status: form.elements.namedItem('status')?.value ?? '',
    kind: form.elements.namedItem('kind')?.value ?? '',
    area: form.elements.namedItem('area')?.value ?? '',
    component: form.elements.namedItem('component')?.value ?? '',
  };
}


function installCatalog(document) {
  const form = document.querySelector('.filters');
  if (!form) {
    return;
  }
  const records = catalogRecords(document);
  const status = document.createElement('p');
  status.className = 'filter-count shell';
  status.setAttribute('aria-live', 'polite');
  const count = document.createElement('span');
  count.dataset.filterCount = '';
  status.append(count, document.createTextNode(' specs'));
  form.insertAdjacentElement('afterend', status);

  const empty = document.createElement('p');
  empty.className = 'catalog-empty';
  empty.dataset.emptyState = '';
  empty.textContent = document.documentElement.lang === 'ko'
    ? '조건과 일치하는 Spec이 없습니다.'
    : 'No specs match these filters.';
  empty.hidden = true;
  document.querySelector('.catalog')?.prepend(empty);

  const apply = () => {
    const visible = new Set(filterCatalog(records, catalogFilters(form)));
    for (const record of records) {
      record.element.hidden = !visible.has(record);
    }
    count.textContent = String(visible.size);
    empty.hidden = visible.size !== 0;
  };
  form.addEventListener('input', apply);
  form.addEventListener('change', apply);
  form.addEventListener('submit', (event) => event.preventDefault());
  apply();
}


function installSectionNavigation(document) {
  const navigation = document.querySelector('.section-nav');
  if (!navigation) {
    return;
  }
  const links = [...navigation.querySelectorAll('a[href^="#"]')];
  const update = () => {
    const active = normalizeHashTarget(globalThis.location?.hash ?? '');
    for (const link of links) {
      const current = link.getAttribute('href') === `#${active}`;
      if (current) {
        link.setAttribute('aria-current', 'location');
      } else {
        link.removeAttribute('aria-current');
      }
    }
  };
  navigation.addEventListener('keydown', (event) => {
    if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) {
      return;
    }
    const current = links.indexOf(document.activeElement);
    if (current === -1) {
      return;
    }
    event.preventDefault();
    const direction = event.key === 'ArrowRight' ? 1 : -1;
    links[(current + direction + links.length) % links.length].focus();
  });
  globalThis.addEventListener?.('hashchange', update);
  update();
}


function errorText(error) {
  return String(error?.message ?? error ?? 'render failed').split('\n', 1)[0];
}


async function renderDiagrams(document, mermaid) {
  const blocks = [...document.querySelectorAll('pre.mermaid')];
  if (blocks.length === 0) {
    return;
  }
  if (!mermaid || typeof mermaid.render !== 'function') {
    mermaid = {
      async parse() {
        throw new Error('Mermaid runtime unavailable');
      },
    };
  } else {
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      theme: 'neutral',
    });
  }

  for (const [index, block] of blocks.entries()) {
    const wrapper = block.closest('.diagram-scroll') ?? block.parentElement;
    const source = block.textContent ?? '';
    try {
      await mermaid.parse(source);
      const result = await mermaid.render(`forge-spec-diagram-${index}`, source);
      const rendered = document.createElement('div');
      rendered.className = 'mermaid-rendered';
      rendered.innerHTML = result.svg;
      result.bindFunctions?.(rendered);

      const disclosure = document.createElement('details');
      disclosure.className = 'mermaid-source-disclosure';
      const summary = document.createElement('summary');
      summary.textContent = document.documentElement.lang === 'ko'
        ? 'Mermaid source 보기'
        : 'Show Mermaid source';
      const preserved = document.createElement('pre');
      preserved.className = 'mermaid-source';
      preserved.textContent = source;
      disclosure.append(summary, preserved);
      wrapper.replaceChildren(rendered, disclosure);
    } catch (error) {
      wrapper.classList.add('diagram-error');
      const message = document.createElement('p');
      message.className = 'mermaid-error-message';
      message.textContent = `${document.documentElement.lang === 'ko' ? 'Diagram을 렌더링하지 못했습니다' : 'Diagram render failed'}: ${errorText(error)}`;
      const preserved = document.createElement('pre');
      preserved.className = 'mermaid-error-source';
      preserved.textContent = source;
      wrapper.replaceChildren(message, preserved);
    }
  }
}


export async function initializeSpecPages(
  document = globalThis.document,
  mermaid = globalThis.mermaid,
) {
  if (!document) {
    return;
  }
  installCatalog(document);
  installSectionNavigation(document);
  await renderDiagrams(document, mermaid);
  document.documentElement.dataset.specPagesReady = 'true';
}


if (typeof document !== 'undefined') {
  const start = () => {
    initializeSpecPages().catch((error) => {
      document.documentElement.dataset.specPagesReady = 'error';
      console.error('Spec Pages runtime failed', error);
    });
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    queueMicrotask(start);
  }
}
