import { expect, test } from '@playwright/test';


const baseURL = process.env.FORGE_SPEC_PAGES_BASE_URL || 'http://127.0.0.1:4173';
const mermaidSource = 'flowchart LR\n    S[spec.md] --> P[index.html]';
const viewports = [
  { name: 'desktop', width: 1440, height: 1000 },
  { name: 'mobile', width: 390, height: 844 },
];


function externalRequestLog(page) {
  const external = [];
  page.on('request', (request) => {
    const url = request.url();
    if (!url.startsWith(baseURL) && !url.startsWith('data:') && !url.startsWith('blob:')) {
      external.push(url);
    }
  });
  return external;
}


async function expectNoViewportOverflow(page) {
  const geometry = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  expect(geometry.scrollWidth).toBeLessThanOrEqual(geometry.clientWidth + 1);
}


async function expectVisibleFocus(page, locator) {
  await expect(locator).toBeFocused();
  const focus = await locator.evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      style: style.outlineStyle,
      width: Number.parseFloat(style.outlineWidth),
    };
  });
  expect(focus.style).not.toBe('none');
  expect(focus.width).toBeGreaterThanOrEqual(3);
}


for (const viewport of viewports) {
  test(`catalog filters, count, empty and long states — ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    const external = externalRequestLog(page);
    await page.goto(`${baseURL}/docs/specs/index.html`);
    await expect(page.locator('html')).toHaveAttribute('data-spec-pages-ready', 'true');

    await page.keyboard.press('Tab');
    await expectVisibleFocus(page, page.locator('input[name="query"]'));
    await expect(page.locator('[data-filter-count]')).toHaveText('2');
    await expect(page.locator('.catalog-entry:visible')).toHaveCount(2);

    await page.locator('input[name="query"]').fill('RELATED');
    await expect(page.locator('[data-filter-count]')).toHaveText('1');
    await expect(page.locator('.catalog-entry:visible')).toHaveCount(1);
    await expect(page.locator('.catalog-entry:visible')).toHaveAttribute('data-spec-id', '002-related');

    await page.locator('input[name="query"]').fill('');
    await page.locator('select[name="component"]').selectOption('developer tools');
    await expect(page.locator('[data-filter-count]')).toHaveText('1');
    await expect(page.locator('.catalog-entry:visible')).toHaveAttribute('data-spec-id', '002-related');

    await page.locator('select[name="component"]').selectOption('');
    await page.locator('select[name="status"]').selectOption('draft');
    await expect(page.locator('[data-filter-count]')).toHaveText('1');
    await expect(page.locator('.catalog-entry:visible')).toHaveAttribute('data-spec-id', '001-basic');
    await expect(page.locator('.catalog-entry[data-spec-id="001-basic"] .catalog-relations a')).toHaveAttribute(
      'href',
      '002-related/index.html',
    );

    await page.locator('select[name="status"]').selectOption('');
    await page.locator('input[name="query"]').fill('no matching spec');
    await expect(page.locator('[data-filter-count]')).toHaveText('0');
    await expect(page.locator('[data-empty-state]')).toBeVisible();
    await expect(page.locator('.catalog-entry:visible')).toHaveCount(0);

    await expect(page.locator('.catalog-entry[data-spec-id="002-related"]')).toHaveAttribute('data-areas', '[]');
    await expect(
      page.locator('.catalog-entry[data-spec-id="002-related"] .tag', {
        hasText: 'deterministic-renderer-with-an-intentionally-long-component-label',
      }),
    ).toHaveCount(1);
    await expectNoViewportOverflow(page);
    expect(external).toEqual([]);
  });

  test(`page navigation, relations, overflow and real Mermaid — ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    const external = externalRequestLog(page);
    await page.goto(`${baseURL}/docs/specs/001-basic/index.html#AC1`);
    await expect(page.locator('html')).toHaveAttribute('data-spec-pages-ready', 'true');
    await expect(page.locator('.section-nav a[href="#acceptance"]')).toHaveAttribute(
      'aria-current',
      'location',
    );

    await page.locator('body').press('Home');
    await page.locator('body').click({ position: { x: 2, y: 2 } });
    await page.keyboard.press('Tab');
    await expectVisibleFocus(page, page.locator('.source-link'));
    const firstNavLink = page.locator('.section-nav a').first();
    await firstNavLink.focus();
    await expectVisibleFocus(page, firstNavLink);
    await page.keyboard.press('ArrowRight');
    await expect(page.locator('.section-nav a').nth(1)).toBeFocused();
    await expect(page.locator('.section-nav')).toHaveCSS('position', 'sticky');

    await expect(page.locator('.relation[href="../002-related/index.html"]')).toHaveCount(1);
    await expect(page.locator('.mermaid-rendered svg')).toHaveCount(1);
    await expect(page.locator('.diagram-error')).toHaveCount(0);
    await expect(page.locator('.mermaid-source')).toHaveText(mermaidSource);

    const wrappers = await page.locator('.table-scroll, .diagram-scroll').evaluateAll((elements) =>
      elements.map((element) => ({
        clientWidth: element.clientWidth,
        overflowX: getComputedStyle(element).overflowX,
        scrollWidth: element.scrollWidth,
      })),
    );
    expect(wrappers.length).toBeGreaterThanOrEqual(3);
    expect(wrappers.every((item) => item.overflowX === 'auto')).toBe(true);
    if (viewport.name === 'mobile') {
      expect(wrappers.some((item) => item.scrollWidth > item.clientWidth)).toBe(true);
    }
    await expectNoViewportOverflow(page);
    expect(external).toEqual([]);
  });

  test(`runtime Mermaid rejection preserves source and other content — ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.addInitScript(() => {
      let value;
      Object.defineProperty(globalThis, 'mermaid', {
        configurable: true,
        get() {
          return value;
        },
        set(next) {
          next.render = async () => {
            throw new Error('injected runtime render rejection');
          };
          value = next;
        },
      });
    });
    const external = externalRequestLog(page);
    await page.goto(`${baseURL}/docs/specs/001-basic/index.html`);
    await expect(page.locator('html')).toHaveAttribute('data-spec-pages-ready', 'true');
    await expect(page.locator('.diagram-error')).toHaveCount(1);
    await expect(page.locator('.mermaid-error-message')).toContainText('injected runtime render rejection');
    await expect(page.locator('.mermaid-error-source')).toHaveText(mermaidSource);
    await expect(page.locator('#acceptance')).toBeVisible();
    await expect(page.locator('#AC1')).toBeVisible();
    await expectNoViewportOverflow(page);
    expect(external).toEqual([]);
  });
}
