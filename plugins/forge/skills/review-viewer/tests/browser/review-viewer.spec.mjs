import { expect, test } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';


const baseURL = process.env.FORGE_REVIEW_VIEWER_BASE_URL;
const repository = process.env.FORGE_REVIEW_VIEWER_REPOSITORY;
const mermaidPath = process.env.FORGE_REVIEW_VIEWER_MERMAID;
const mermaidURL = 'https://cdn.jsdelivr.net/npm/mermaid@11.16.0/dist/mermaid.min.js';
if (!baseURL || !repository || !mermaidPath) throw new Error('Review Viewer browser environment is incomplete');

const viewports = [
  { name: 'desktop', width: 1440, height: 1000 },
  { name: 'mobile', width: 390, height: 844 },
];


function externalRequests(page) {
  const requests = [];
  const ownOrigin = new URL(baseURL).origin;
  page.on('request', (request) => {
    const url = request.url();
    if (/^https?:/.test(url) && new URL(url).origin !== ownOrigin) requests.push(url);
  });
  return requests;
}


async function expectReady(page) {
  await expect(page.locator('html')).toHaveAttribute('data-review-viewer-ready', 'true');
  await expect(page.locator('.tab-panel')).toHaveCount(6);
}


async function expectNoDocumentOverflow(page) {
  const sizes = await page.evaluate(() => ({
    client: document.documentElement.clientWidth,
    scroll: document.documentElement.scrollWidth,
  }));
  expect(sizes.scroll).toBeLessThanOrEqual(sizes.client);
}


async function expectVisibleFocus(locator) {
  await locator.focus();
  const focus = await locator.evaluate((element) => {
    const style = getComputedStyle(element);
    return { style: style.outlineStyle, width: Number.parseFloat(style.outlineWidth) };
  });
  expect(focus.style).not.toBe('none');
  expect(focus.width).toBeGreaterThanOrEqual(3);
}


function contrastRatio(foreground, background) {
  const channels = (value) => value.match(/\d+/g).slice(0, 3).map(Number).map((channel) => {
    const normalized = channel / 255;
    return normalized <= 0.04045 ? normalized / 12.92 : ((normalized + 0.055) / 1.055) ** 2.4;
  });
  const luminance = (value) => {
    const [red, green, blue] = channels(value);
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue;
  };
  const first = luminance(foreground);
  const second = luminance(background);
  return (Math.max(first, second) + 0.05) / (Math.min(first, second) + 0.05);
}


for (const viewport of viewports) {
  test(`HTTP CDN spec provenance, deep links and persistence — ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    const external = externalRequests(page);
    await page.route(mermaidURL, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'text/javascript',
        body: fs.readFileSync(mermaidPath),
      });
    });
    await page.goto(`${baseURL}/.forge/reviews/spec-cdn/view.html`);
    await expectReady(page);
    const palette = await page.evaluate(() => ({
      accent: getComputedStyle(document.documentElement).getPropertyValue('--accent').trim(),
      status: getComputedStyle(document.querySelector('.status')).color,
      surface: getComputedStyle(document.querySelector('.doc-header')).backgroundColor,
    }));
    expect(palette.accent).toBe('#2557a7');
    expect(palette.status).toBe('rgb(37, 87, 167)');
    expect(contrastRatio(palette.status, palette.surface)).toBeGreaterThanOrEqual(4.5);
    await expect(page.locator('[data-freshness-group="primary"] .freshness-state')).toHaveText('current');
    await expect(page.locator('[data-freshness-group="comparison"] .freshness-state')).toHaveText('current');

    const firstTab = page.locator('[role="tab"]').first();
    await expectVisibleFocus(firstTab);
    await page.keyboard.press('ArrowRight');
    await expect(page.locator('[role="tab"]').nth(1)).toBeFocused();

    await page.goto(`${baseURL}/.forge/reviews/spec-cdn/view.html#comparison-1--002-beta-AC1`);
    await expect(page.locator('#acceptance')).toBeVisible();
    const checks = page.locator('[data-review-check][data-item="AC1"]');
    await expect(checks).toHaveCount(2);
    const keys = await checks.evaluateAll((items) => items.map((item) => item.dataset.storageKey));
    expect(new Set(keys).size).toBe(2);
    await checks.nth(1).check();
    await page.reload();
    await expect(page.locator('[data-review-check][data-item="AC1"]').nth(1)).toBeChecked();
    await expect(page.locator('[data-review-check][data-item="AC1"]').first()).not.toBeChecked();

    await page.locator('[role="tab"][data-tab="flows"]').click();
    await expect(page.locator('.diagram-scroll svg')).toHaveCount(1);
    await expect(page.locator('.diagram-error')).toHaveCount(0);
    await expectNoDocumentOverflow(page);
    expect(external.length).toBeGreaterThanOrEqual(1);
    expect(external.every((url) => url === mermaidURL)).toBe(true);
  });

  test(`HTTP offline plan freshness, overflow, print and fallback — ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    const external = externalRequests(page);
    await page.goto(`${baseURL}/.forge/reviews/plan-offline/view.html#plan--001-demo-Task1-Step1`);
    await expectReady(page);
    await expect(page.locator('#data')).toBeVisible();
    await expect(page.locator('[data-freshness-group="primary"] .freshness-state')).toHaveText('current');
    await expect(page.locator('[data-freshness-group="context"] .freshness-state')).toHaveText('current');

    await page.locator('[role="tab"][data-tab="overview"]').click();
    await expect(page.locator('#overview')).toContainText('Build a deterministic review source bundle.');
    await expect(page.locator('#overview [data-plan-user-experience]')).toHaveCount(0);
    await page.locator('[role="tab"][data-tab="requirements"]').click();
    await expect(page.locator('#requirements [data-route-scope]')).toHaveCount(2);
    await page.locator('[role="tab"][data-tab="history"]').click();
    await expect(page.locator('#history [data-source-state-summary]')).toContainText('active');
    await expect(page.locator('#history [data-source-state-summary] input')).toHaveCount(0);
    await page.locator('[role="tab"][data-tab="acceptance"]').click();
    await expect(page.locator('#acceptance a[href="#plan--001-demo-Task1-Step1"]').first()).toHaveText('Task1-Step1');
    const brokenTargets = await page.evaluate(() => Array.from(document.querySelectorAll('a[href^="#"]'))
      .map((anchor) => anchor.getAttribute('href').slice(1))
      .filter((id) => !document.getElementById(id)));
    expect(brokenTargets).toEqual([]);

    await page.locator('[role="tab"][data-tab="data"]').click();
    await expect(page.locator('#data [data-main-task-detail]')).toHaveCount(1);
    await expect(page.locator('#data [data-main-task-detail]')).not.toHaveAttribute('open', '');
    const step = page.locator('[data-storage-key="plan-offline:plan--001-demo:step:Task1-Step1"]');
    await step.check();
    await page.reload();
    await expect(step).toBeChecked();

    const changedSource = path.join(repository, 'docs/specs/002-beta/spec.md');
    const original = fs.readFileSync(changedSource);
    try {
      fs.appendFileSync(changedSource, '\n');
      await page.reload();
      await expect(page.locator('[data-freshness-group="context"] .freshness-state')).toHaveText('stale');
      await expect(page.locator('[data-source-group="context"] .source-error', { hasText: 'differs' })).toHaveCount(1);
    } finally {
      fs.writeFileSync(changedSource, original);
    }
    await page.reload();
    await expect(page.locator('[data-freshness-group="context"] .freshness-state')).toHaveText('current');

    await page.locator('[role="tab"][data-tab="flows"]').click();
    await expect(page.locator('.diagram-scroll svg')).toHaveCount(3);
    const wide = page.locator('.diagram-scroll.is-wide').first();
    if (viewport.name === 'mobile') {
      const dimensions = await wide.evaluate((element) => ({ client: element.clientWidth, scroll: element.scrollWidth }));
      expect(dimensions.scroll).toBeGreaterThan(dimensions.client);
    }
    await page.locator('[role="tab"][data-tab="overview"]').click();
    const table = page.locator('.table-scroll').first();
    await expect(table).toBeVisible();
    if (viewport.name === 'mobile') {
      const dimensions = await table.evaluate((element) => ({ client: element.clientWidth, scroll: element.scrollWidth }));
      expect(dimensions.scroll).toBeGreaterThan(dimensions.client);
    }
    await expectNoDocumentOverflow(page);

    await page.emulateMedia({ media: 'print' });
    for (const panel of ['overview', 'requirements', 'flows', 'data', 'acceptance', 'history']) {
      await expect(page.locator(`#${panel}`)).toBeVisible();
    }
    await page.emulateMedia({ media: 'screen' });

    await page.goto(`${baseURL}/.forge/reviews/invalid-offline/view.html#flows`);
    await expectReady(page);
    await expect(page.locator('.diagram-error')).toHaveCount(1);
    await expect(page.locator('.mermaid-error-message')).toContainText(/line|parse|syntax/i);
    await expect(page.locator('.mermaid-error-source')).toContainText('flowchart LR');
    await page.locator('[role="tab"][data-tab="overview"]').click();
    await expect(page.locator('#overview')).toBeVisible();
    expect(external).toEqual([]);
  });

  test(`file offline source-row pickers keep duplicate basenames independent — ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    const external = externalRequests(page);
    const viewer = pathToFileURL(path.join(repository, '.forge/reviews/plan-offline/view.html')).href;
    await page.goto(viewer);
    await expectReady(page);
    await expect(page.locator('[data-freshness-overall]')).toHaveText('unverified');
    const manifest = JSON.parse(await page.locator('#forge-source-manifest').textContent());
    for (const source of manifest.sources) {
      const key = `${source.namespace}:${source.path}`;
      await page.locator(`[data-source-picker][data-source-key=${JSON.stringify(key)}]`).setInputFiles(
        path.join(repository, source.path),
      );
    }
    await expect(page.locator('[data-freshness-group="primary"] .freshness-state')).toHaveText('current');
    await expect(page.locator('[data-freshness-group="context"] .freshness-state')).toHaveText('current');
    await expect(page.locator('[data-source-state]')).toHaveText(['current', 'current', 'current', 'current', 'current']);
    await page.locator('[role="tab"][data-tab="flows"]').click();
    await expect(page.locator('.diagram-scroll svg')).toHaveCount(3);
    await expectNoDocumentOverflow(page);
    expect(external).toEqual([]);
  });
}
