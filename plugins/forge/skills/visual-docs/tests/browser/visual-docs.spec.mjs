import { expect, test } from '@playwright/test';
import fs from 'node:fs';


const baseURL = process.env.FORGE_VISUAL_DOCS_BASE_URL;
const mermaidPath = process.env.FORGE_VISUAL_DOCS_MERMAID;
const mermaidURL = 'https://cdn.jsdelivr.net/npm/mermaid@11.16.0/dist/mermaid.min.js';
if (!baseURL || !mermaidPath) throw new Error('Visual Docs browser environment is incomplete');

const viewports = [
  { name: 'desktop', width: 1440, height: 1000 },
  { name: 'mobile', width: 390, height: 844 },
];

async function expectReady(page) {
  await expect(page.locator('html')).toHaveAttribute('data-visual-docs-ready', 'true');
  expect(await page.locator('[data-component]').count()).toBeGreaterThan(0);
}

async function expectNoDocumentOverflow(page) {
  const sizes = await page.evaluate(() => ({
    client: document.documentElement.clientWidth,
    scroll: document.documentElement.scrollWidth,
  }));
  expect(sizes.scroll).toBeLessThanOrEqual(sizes.client);
}

for (const viewport of viewports) {
  test(`Project Handbook human-first navigation — ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto(`${baseURL}/docs/project-viewer/index.html`);
    await expectReady(page);
    await expect(page.locator('h1')).toHaveText('Demo Project');
    await expect(page.locator('.review-navigation a')).toHaveText([
      '프로젝트 한눈에', 'Spec', '구조',
    ]);
    await expect(page.locator('.structure-card')).toHaveCount(1);
    await expect(page.locator('.structure-ownership dt')).toHaveText(['Purpose', 'Owns']);
    const ownershipBeforeEvidence = await page.locator('.structure-card').evaluate((card) => {
      const ownership = card.querySelector('.structure-ownership');
      const evidence = card.querySelector('.derived-evidence');
      return Boolean(
        ownership
        && evidence
        && (ownership.compareDocumentPosition(evidence) & Node.DOCUMENT_POSITION_FOLLOWING),
      );
    });
    expect(ownershipBeforeEvidence).toBe(true);
    await expect(page.locator('.developer-disclosure')).not.toHaveAttribute('open', '');
    await expect(page.locator('.derived-evidence')).not.toHaveAttribute('open', '');
    await expect(page.locator('[data-freshness-group="primary"] .freshness-state')).toHaveText('current');
    await expect(page.locator('[data-freshness-group="context"] .freshness-state')).toHaveText('current');
    await page.locator('.developer-disclosure > summary').focus();
    const outline = await page.locator('.developer-disclosure > summary').evaluate(
      (element) => getComputedStyle(element).outlineWidth,
    );
    expect(Number.parseFloat(outline)).toBeGreaterThanOrEqual(3);
    await expectNoDocumentOverflow(page);
  });

  test(`adaptive spec composition and stable shell — ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.route(mermaidURL, async (route) => {
      await route.fulfill({ status: 200, contentType: 'text/javascript', body: fs.readFileSync(mermaidPath) });
    });
    await page.goto(`${baseURL}/.forge/visual-docs/spec-cdn/view.html`);
    await expectReady(page);
    await expect(page.locator('h1')).toHaveText('Semantic Spec Bundle Contract');
    await expect(page.locator('.review-navigation')).toBeVisible();
    await expect(page.locator('[data-component="source-detail"]')).toBeVisible();
    await expect(page.locator('[data-freshness-group="primary"] .freshness-state')).toHaveText('current');
    await expect(page.locator('[data-freshness-group="comparison"] .freshness-state')).toHaveText('current');
    const requirements = page.locator('[data-statement-kind="requirement"]');
    await expect(requirements).toHaveCount(2);
    const requirementIds = await requirements.evaluateAll((elements) => elements.map((element) => element.id));
    expect(new Set(requirementIds).size).toBe(2);
    expect(await requirements.locator('h3 a').allTextContents()).toEqual([
      'Every declared member enters the review source set exactly once',
      'Every declared member enters the review source set exactly once',
    ]);
    const acceptanceChecks = page.locator('[data-statement-kind="acceptance"] [data-review-check]');
    await expect(acceptanceChecks).toHaveCount(2);
    await acceptanceChecks.first().check();
    await page.reload();
    await expect(acceptanceChecks.first()).toBeChecked();
    await expect(acceptanceChecks.nth(1)).not.toBeChecked();
    const firstLink = page.locator('.review-navigation a').first();
    await firstLink.focus();
    const outline = await firstLink.evaluate((element) => getComputedStyle(element).outlineWidth);
    expect(Number.parseFloat(outline)).toBeGreaterThanOrEqual(3);
    await expect(page.locator('.diagram-scroll svg')).toHaveCount(2);
    await expectNoDocumentOverflow(page);
  });

  test(`adaptive plan and Mermaid fallback — ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto(`${baseURL}/.forge/visual-docs/plan-offline/view.html`);
    await expectReady(page);
    await expect(page.locator('[data-component]').first()).toHaveAttribute('data-component', 'route-map');
    await expect(page.locator('[data-component="runtime-atlas"]')).toBeVisible();
    await expect(page.locator('[data-component="source-detail"]')).toContainText('002-manifest.md');
    await expect(page.locator('[data-freshness-group="context"] .freshness-state')).toHaveText('current');
    await expectNoDocumentOverflow(page);

    await page.goto(`${baseURL}/.forge/visual-docs/invalid-offline/view.html`);
    await expectReady(page);
    await expect(page.locator('.diagram-error')).toHaveCount(1);
    await expect(page.locator('.mermaid-error-source')).toContainText('flowchart LR');
  });
}
