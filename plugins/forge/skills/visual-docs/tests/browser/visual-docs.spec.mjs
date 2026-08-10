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
    await expect(page.locator('[data-project-root="true"] .project-tree-label')).toHaveText([
      '개요', '설계 기준', '프로젝트 구조',
    ]);
    await expect(page.locator('[role="tree"]')).toBeVisible();
    await expect(page.locator('[data-node-kind="spec-bundle"]')).toHaveCount(1);
    await expect(page.locator('[data-node-kind="spec-member"]')).toHaveCount(5);
    await expect(page.locator('[data-node-kind="spec-section"]')).not.toHaveCount(0);
    if (viewport.name === 'mobile') {
      await expect(page.locator('.project-master')).toBeVisible();
      await expect(page.locator('.project-detail-pane')).toBeHidden();
    } else {
      await expect(page.locator('[data-project-detail][data-route="project-overview"]')).toBeVisible();
    }

    const designRoot = page.locator('[data-route="project-design-criteria"][role="treeitem"]');
    const designToggle = page.locator('[data-tree-toggle][data-route="project-design-criteria"]');
    const designGroup = page.locator('[role="group"][data-parent-route="project-design-criteria"]');
    await expect(designRoot).toHaveAttribute('aria-expanded', 'false');
    await expect(designToggle).toHaveAttribute('aria-expanded', 'false');
    await expect(designGroup).toBeHidden();
    await designToggle.click();
    await expect(designRoot).toHaveAttribute('aria-expanded', 'true');
    await expect(designToggle).toHaveAttribute('aria-expanded', 'true');
    await expect(designGroup).toBeVisible();
    await designToggle.click();
    await expect(designRoot).toHaveAttribute('aria-expanded', 'false');
    await expect(designGroup).toBeHidden();

    const structureToggle = page.locator('[data-tree-toggle][data-route="project-structure"]');
    await structureToggle.click();

    const structureItem = page.locator('[data-node-kind="structure-entry"]').first();
    await structureItem.click();
    const structureDetail = page.locator('[data-project-detail].is-active');
    await expect(structureDetail).toContainText('역할');
    await expect(structureDetail).toContainText('담당 범위');
    await expect(structureDetail).toContainText('주요 파일');
    const ownershipBeforeEvidence = await structureDetail.evaluate((detail) => {
      const ownership = detail.querySelector('.structure-ownership');
      const evidence = detail.querySelector('.project-evidence');
      return Boolean(
        ownership
        && evidence
        && (ownership.compareDocumentPosition(evidence) & Node.DOCUMENT_POSITION_FOLLOWING),
      );
    });
    expect(ownershipBeforeEvidence).toBe(true);
    await expect(structureDetail.locator('.project-evidence')).not.toHaveAttribute('open', '');
    if (viewport.name === 'mobile') {
      await page.locator('.project-back').click();
      await expect(page.locator('.project-master')).toBeVisible();
    } else {
      const scrollGeometry = await page.locator('.project-master').evaluate((master) => {
        const nav = master.querySelector('.project-tree-navigation');
        const masterRight = master.getBoundingClientRect().right;
        const navRight = nav.getBoundingClientRect().right;
        return { edgeOffset: Math.abs(masterRight - navRight) };
      });
      expect(scrollGeometry.edgeOffset).toBeLessThanOrEqual(1);
    }

    const treeItem = page.locator('[role="treeitem"]:visible').first();
    await treeItem.focus();
    await treeItem.press('ArrowDown');
    await expect(page.locator('[role="treeitem"]:focus')).not.toHaveCount(0);
    const focusedOutline = await page.locator('[role="treeitem"]:focus').evaluate(
      (element) => getComputedStyle(element).outlineWidth,
    );
    expect(Number.parseFloat(focusedOutline)).toBeGreaterThanOrEqual(3);
    await page.locator('#project-search').fill('Statement Traceability');
    await expect(page.locator('[data-node-kind="spec-member"]:visible')).toHaveCount(1);
    await page.locator('#project-search').fill('nothing-matches-this');
    await expect(page.locator('.project-search-empty')).toBeVisible();
    await page.locator('#project-search').fill('');
    await expect(page.locator('.project-search-empty')).toBeHidden();

    const memberItem = page.locator('[data-node-kind="spec-member"]').filter({ hasText: 'Statement Traceability' });
    await memberItem.click();
    await expect(page).toHaveURL(/#spec-member-/);
    await page.reload();
    await expect(page.locator('[data-project-detail].is-active')).toContainText('Statement Traceability');

    if (viewport.name === 'mobile') {
      await expect(page.locator('.project-master')).toBeHidden();
      await expect(page.locator('.project-detail-pane')).toBeVisible();
      await page.locator('.project-back').click();
      await expect(page.locator('.project-master')).toBeVisible();
      await expect(page.locator('.project-detail-pane')).toBeHidden();
    } else {
      await expect(page.locator('.project-master')).toBeVisible();
      await expect(page.locator('.project-detail-pane')).toBeVisible();
    }

    await expect(page.locator('[data-freshness-group="primary"] .freshness-state')).toHaveText('current');
    await expect(page.locator('[data-freshness-group="context"] .freshness-state')).toHaveText('current');
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
