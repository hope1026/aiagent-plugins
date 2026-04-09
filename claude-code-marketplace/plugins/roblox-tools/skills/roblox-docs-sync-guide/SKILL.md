---
name: roblox-docs-sync-guide
description: Guide for keeping Roblox MCP documentation in sync with code changes. Trigger when tools/actions/tiers/counts change and multilingual docs, tool references, release docs, or the dashboard "What's New" announcements must be updated consistently.
---

# Roblox Docs Sync Guide

## Use This Skill When
- Tool/action definitions changed in `mcp-server/`.
- Basic/Pro classification changed in plugin handler or tier files.
- Tool counts/categories changed and docs may be stale.
- Release documentation must stay aligned across supported languages.
- A user-visible behavior change needs a dashboard announcement (reset of stats/history, new page, migration side-effects, etc.).

## Do Not Use This Skill For
- Feature implementation with no documentation impact.
- Isolated copy edits unrelated to tool/action/tier truth.
- Internal refactors that do not affect what the user sees, runs, or stores on disk.

## Supported Languages
- `en`: `deploy/publish/hope1026-roblox-mcp/README.md`
- `ko`: `deploy/publish/hope1026-roblox-mcp/docs/ko/README.md`
- `ja`: `deploy/publish/hope1026-roblox-mcp/docs/ja/README.md`
- `es`: `deploy/publish/hope1026-roblox-mcp/docs/es/README.md`
- `pt-br`: `deploy/publish/hope1026-roblox-mcp/docs/pt-br/README.md`
- `id`: `deploy/publish/hope1026-roblox-mcp/docs/id/README.md`

## Source of Truth (Read First)
### SSOT (Single Source of Truth)
- `tool-codegen/tools.yaml` — single source of truth for all tool/action definitions, including handler, tier, route, and `paramAliases`

### Generated Files (auto-generated, do not edit directly)
- `mcp-server/src/generated/dispatch-map.generated.ts` — action-to-plugin-command mapping
- `mcp-server/src/generated/tier-map.generated.ts` — Basic/Pro tier gating
- `mcp-server/src/generated/route-map.generated.ts` — action-to-route mapping
- `plugin/src/Generated/ProActions.generated.luau` — list of Pro actions
- `cd mcp-server && npm run codegen:check` or `./tool-codegen/verify-sync.sh` — generated-file drift verification

### MCP server side (TypeScript)
- `mcp-server/src/tools/consolidated/*.ts` — tool schemas and definitions
- `mcp-server/src/utils/tool-dispatcher.ts` — generated dispatch-map import
- `mcp-server/src/utils/tier-checker.ts` — generated tier-map import

### Plugin side
- `plugin/src/CommandHandlers/init.luau` (`HANDLER_REGISTRY`; `PRO_ACTIONS` is imported from Generated)

## Documentation Targets

### Main README (all languages)
- `deploy/publish/hope1026-roblox-mcp/README.md`
- `deploy/publish/hope1026-roblox-mcp/docs/ko/README.md`
- `deploy/publish/hope1026-roblox-mcp/docs/ja/README.md`
- `deploy/publish/hope1026-roblox-mcp/docs/es/README.md`
- `deploy/publish/hope1026-roblox-mcp/docs/pt-br/README.md`
- `deploy/publish/hope1026-roblox-mcp/docs/id/README.md`

### Installation guide (all languages)
- `deploy/publish/hope1026-roblox-mcp/docs/en/installation/README.md`
- `deploy/publish/hope1026-roblox-mcp/docs/ko/installation/README.md`
- `deploy/publish/hope1026-roblox-mcp/docs/ja/installation/README.md`
- `deploy/publish/hope1026-roblox-mcp/docs/es/installation/README.md`
- `deploy/publish/hope1026-roblox-mcp/docs/pt-br/installation/README.md`
- `deploy/publish/hope1026-roblox-mcp/docs/id/installation/README.md`

### Pro upgrade guide (all languages)
- `deploy/publish/hope1026-roblox-mcp/docs/en/pro-upgrade.md`
- `deploy/publish/hope1026-roblox-mcp/docs/ko/pro-upgrade.md`
- `deploy/publish/hope1026-roblox-mcp/docs/ja/pro-upgrade.md`
- `deploy/publish/hope1026-roblox-mcp/docs/es/pro-upgrade.md`
- `deploy/publish/hope1026-roblox-mcp/docs/pt-br/pro-upgrade.md`
- `deploy/publish/hope1026-roblox-mcp/docs/id/pro-upgrade.md`

### Tool overview (all languages)
- `deploy/publish/hope1026-roblox-mcp/docs/en/tools/overview.md`
- `deploy/publish/hope1026-roblox-mcp/docs/ko/tools/overview.md`
- `deploy/publish/hope1026-roblox-mcp/docs/ja/tools/overview.md`
- `deploy/publish/hope1026-roblox-mcp/docs/es/tools/overview.md`
- `deploy/publish/hope1026-roblox-mcp/docs/pt-br/tools/overview.md`
- `deploy/publish/hope1026-roblox-mcp/docs/id/tools/overview.md`

### Setup guide (all languages)
- `deploy/publish/roblox-plugin-package/weppy-roblox-mcp/SETUP-GUIDE-en.md`
- `deploy/publish/roblox-plugin-package/weppy-roblox-mcp/SETUP-GUIDE-ko.md`
- `deploy/publish/roblox-plugin-package/weppy-roblox-mcp/SETUP-GUIDE-ja.md`
- `deploy/publish/roblox-plugin-package/weppy-roblox-mcp/SETUP-GUIDE-es.md`
- `deploy/publish/roblox-plugin-package/weppy-roblox-mcp/SETUP-GUIDE-pt-br.md`
- `deploy/publish/roblox-plugin-package/weppy-roblox-mcp/SETUP-GUIDE-id.md`

### Plugin localization (all languages)
- `plugin/src/Localization/en.luau`
- `plugin/src/Localization/ko.luau`
- `plugin/src/Localization/ja.luau`
- `plugin/src/Localization/es.luau`
- `plugin/src/Localization/pt-br.luau`
- `plugin/src/Localization/id.luau`

### Gumroad product entry
- `deploy/docs/gumroad/GUMROAD-PRODUCT-ENTRY-GUIDE.md`

### Global project docs (when tool totals/categories change)
- `CLAUDE.md`
- `deploy/publish/hope1026-roblox-mcp/CHANGELOG.md`

### Dashboard "What's New" announcements
- `mcp-dashboard/src/features/whats-new/announcements.data.ts` — bundled `ANNOUNCEMENTS[]` array shown in the dashboard's What's New page. See the "Dashboard Announcements" section below for when and how to add an entry.

## Execution Workflow
1. Read source-of-truth files.
- Never infer tool list from memory.
2. Build a change matrix.
- Added tools/actions
- Removed tools/actions
- Renamed tools/actions
- Basic/Pro reclassification
- Description/category changes
3. Update all affected docs.
- Keep table format, ordering, and style consistent.
- Apply changes across all supported language variants where required.
4. Validate consistency.
- Check counts, categories, and Basic/Pro tags across all updated files.
- Ensure each tool appears once per reference surface.
5. Report summary.
- Include totals and per-category impact.

## Language Selector Rule
All README language selectors must stay consistent.
- Active language entry should be bold, not linked.
- Cross-links must remain valid and relative-path correct.

## Dashboard Announcements (`ANNOUNCEMENTS`)

The dashboard "What's New" tab reads a bundled array from
`mcp-dashboard/src/features/whats-new/announcements.data.ts`. Treat it as the
place to surface user-visible changes that the user needs to be aware of —
not as an internal changelog.

### When to Add an Entry

Add an announcement when a shipped release introduces any of the following:

- A user-visible reset or format change that affects data the user already
  has on disk (tool statistics, command/changelog history, sync state,
  config files). If the user will notice "my numbers are gone" or "my old
  entries are missing", it needs an announcement.
- A new dashboard page, tab, or major UI area that the user should know
  about.
- A breaking change to a user-facing workflow (installation, connection,
  placeId handling, sync root resolution, license activation).
- A deprecation that the user must act on, or a migration the user must
  perform manually.
- A security or privacy notice the user should acknowledge.

### When NOT to Add an Entry

- Internal refactors with no user-visible impact (e.g., file reorganization,
  renaming internal identifiers, generated-code churn, test restructuring).
- Bug fixes that simply restore expected behavior without changing data,
  files, or UI.
- Code comments, typing improvements, or developer tooling changes.
- Any change the user cannot observe from the dashboard, plugin UI, CLI,
  or files they own on disk.

Rule of thumb: if the only thing that changed is how the code is organized,
the user does not need to know. If something on their screen or in their
project folder changes, they do.

### Translating Internal Changes Into User Framing

Write the announcement from the user's point of view. The user does not
care about internal identifier names, schema field renames, or refactor
rationale. They care about:

1. What will look different to them.
2. Whether any of their data was touched.
3. What, if anything, they need to do.

**Example — bad (internal framing):**
> Renamed `action` to `command` across the codebase. `CommandHistoryEntry`
> schema version bumped. Plugin `HANDLER_REGISTRY` rekeyed.

**Example — good (user framing):**
> Tool usage stats reset after upgrade. Your accumulated counts start from
> zero. The previous file is preserved as a `.bak` backup in each place's
> observability folder — nothing is lost.

The second version tells the user exactly what they will see, whether any
action is required, and where to find their old data if they want it. The
first version describes internal plumbing the user has no context for.

### Schema

Each entry in `ANNOUNCEMENTS` must match this shape
(`announcements.types.ts`):

```ts
{
  id: string;              // stable unique ID, never reused
  date: string;            // "YYYY-MM-DD"
  title: { en: string; ko: string };
  body:  { en: string; ko: string };  // plain text, \n for linebreaks
  severity: 'info' | 'warning' | 'critical';
  category: 'release' | 'notice' | 'deprecation' | 'tip';
  version?: string;                             // optional, e.g. "mcp-server 1.5.0"
  link?: { url: string; label: { en: string; ko: string } }; // optional
}
```

### Authoring Rules

- **ID**: use `YYYY-MM-DD-short-slug`. Never reuse an ID — once shipped, it
  is a stable user-facing read-state key tracked in `localStorage`. Editing
  body text in place is fine; changing the ID is not.
- **Order**: newest first. The module order is the display order in the
  dashboard.
- **Languages**: both `en` and `ko` are required. Do not ship an entry with
  only one language. If you cannot translate confidently, ask for help —
  do not machine-translate into the file.
- **Tone**: concise, factual, present-tense, no marketing language. Write
  what the user will see, not what you implemented.
- **Body**: plain text only. `\n` is preserved as a linebreak via
  `white-space: pre-wrap`. There is no markdown renderer — do not use
  `**bold**`, `[links](url)`, or list markers expecting formatting.
- **Links**: if you need to point at docs or a PR, use the optional `link`
  field. Do not paste raw URLs inside `body`.
- **Severity**:
  - `info` — neutral notice, new feature, informational tip.
  - `warning` — the user should pay attention; something on disk or in the
    UI changed and they should know where to find their data.
  - `critical` — immediate action required, data at risk, or a breaking
    change that blocks a workflow.
- **Category**:
  - `release` — new release / new feature highlight.
  - `notice` — general user-facing notice (resets, format changes, reminders).
  - `deprecation` — something is going away; user must migrate.
  - `tip` — optional guidance or best-practice nudge.
- **Avoid jargon**: words like "schema version", "dispatch map", "handler
  registry", "codegen", "tier map" belong in commit messages, not here.

### Verifying an Announcement Change

After editing `announcements.data.ts`:

1. `cd mcp-dashboard && npx tsc --noEmit` — no type errors.
2. `npx vitest run src/features/whats-new/` — all What's New tests pass.
3. `npm run build` — production build succeeds.
4. Optional sanity check: open the dashboard, visit `/whats-new`, confirm
   your entry renders with correct severity bar, category chip, and that
   both locales display correctly when switching language.

### Common Mistakes To Avoid

- Announcing an internal refactor that the user cannot see. (Skip it.)
- Reusing an ID from a previous announcement. (Users have already marked
  it as read in `localStorage`; they will never see the new text.)
- Writing only `en` or only `ko`. (The other locale will fall back, but
  this is a shipping defect.)
- Using markdown syntax expecting it to render.
- Embedding URLs inside `body` instead of the `link` field.
- Using severity `critical` for cosmetic or informational changes.

## Verification Checklist
- [ ] All changed tools/actions reflected in docs
- [ ] No removed tools remain in docs
- [ ] No duplicates introduced
- [ ] Basic/Pro classification matches source files
- [ ] Tool counts/categories synchronized (including `CLAUDE.md` when needed)
- [ ] Language selector format preserved
- [ ] Localization keys updated for all 6 languages
- [ ] Gumroad product entry description updated if Pro features changed
- [ ] Dashboard `ANNOUNCEMENTS` entry added when a user-visible reset, migration, new page, or breaking change shipped
- [ ] Announcement `id` is new (never reused); both `en` and `ko` are populated

## Output Contract
When using this skill, return:
- Number of tools/actions added, removed, reclassified
- Affected categories
- Files updated
- Verification results and any unresolved discrepancies

## Current-State Documentation Rule

Documentation is a snapshot of the currently running system. Do not include the following unless truly necessary:

- **Removed features/paths/files**: Statements like "legacy X path: removed" or "X was deleted" are unnecessary. What does not exist should simply be absent from the docs.
- **Backward-compatibility explanations**: Remove phrases like "for v1 compatibility..." or "for legacy support...". However, if the runtime currently handles multiple formats (e.g., parsing `v1.` prefix tokens), that is current behavior and should be documented.
- **Migration guides**: Guides like "when migrating from v1 to v2..." are unnecessary.
- **Deprecation labels**: Instead of labeling items as "deprecated" or "no longer used", remove them from the documentation entirely.

**Decision test**: "If I delete this sentence, can the current system still be fully understood and implemented?" → If yes, delete it.

**Exception**: Constraints driven by safety or compliance (e.g., "Do not use RunService:Stop() — it crashes Studio") describe current restrictions and should be kept.

## Important Constraints
- Keep total MCP tools under 100 and ensure docs do not imply otherwise.
- Do not write tool count numbers (72, 140, 132, etc.) in any user-facing text or manifests. This includes README, marketplace.json, plugin.json, CHANGELOG, and Gumroad descriptions. Tool/action counts change frequently during development and stale numbers mislead users.
- Preserve existing language quality; do not rewrite unrelated translated text.
- If a translation cannot be confidently updated, keep structure intact and call out the gap explicitly.
