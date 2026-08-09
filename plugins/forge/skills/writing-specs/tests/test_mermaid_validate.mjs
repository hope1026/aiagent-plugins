import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, readdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";


const testDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(testDir, "../../../../../");
const skillRoot = resolve(repoRoot, "plugins/forge/skills/writing-specs");
const bundle = resolve(skillRoot, "assets/mermaid-validator.bundle.mjs");
const buildScript = resolve(skillRoot, "scripts/build-mermaid-validator.sh");
const noticePath = resolve(skillRoot, "assets/mermaid-validator-THIRD-PARTY.txt");

const notice = readFileSync(noticePath, "utf8");
assert.match(notice, /Package: mermaid@11\.16\.0/);
assert.match(notice, /Package: linkedom@0\.18\.12/);
assert.match(notice, /Package: boolbase@1\.0\.0/);
assert.match(notice, /BEGIN LICENSE TEXT/);
assert.match(notice, /Copyright \(c\) 2014-2015, Felix Boehm/);
assert.match(notice, /Package: dompurify@3\.4\.12[\s\S]*Source file: LICENSE-MPL/);
assert.doesNotMatch(notice, /UNKNOWN/);
assert.doesNotMatch(notice, /Package: @esbuild\//);

function validate(source) {
  const result = spawnSync(
    process.execPath,
    [bundle, "--stdin", "--format", "json"],
    { input: source, encoding: "utf8" },
  );
  assert.equal(result.stderr, "", `validator leaked stderr: ${result.stderr}`);
  assert.ok(result.stdout, "validator must emit normalized JSON");
  return { status: result.status, payload: JSON.parse(result.stdout) };
}

function extractMermaid(path) {
  const source = readFileSync(path, "utf8");
  return [...source.matchAll(/```mermaid\r?\n([\s\S]*?)\r?\n```/g)].map(
    (match) => match[1],
  );
}

const specMarkdown = readdirSync(resolve(repoRoot, "docs/specs"), {
  recursive: true,
  withFileTypes: true,
})
  .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
  .map((entry) => resolve(entry.parentPath, entry.name));
const diagrams = specMarkdown.flatMap(extractMermaid);
assert.ok(diagrams.length > 0, "active Spec Bundles must provide Mermaid coverage");
for (const diagram of diagrams) {
  const { status, payload } = validate(diagram);
  assert.equal(status, 0);
  assert.deepEqual(payload, { valid: true, diagnostics: [] });
}

const malformed = "flowchart TD\n    A[broken";
const first = validate(malformed);
const second = validate(malformed);
assert.notEqual(first.status, 0);
assert.deepEqual(first.payload, second.payload, "diagnostic JSON must be stable");
assert.equal(first.payload.valid, false);
assert.deepEqual(first.payload.diagnostics, [
  {
    line: 2,
    code: "SPEC_MERMAID_SYNTAX",
    message: "Mermaid syntax is invalid.",
  },
]);
assert.doesNotMatch(JSON.stringify(first.payload), /(?:Error:| at |\/Users\/|node_modules)/);

const scratch = mkdtempSync(resolve(tmpdir(), "forge-mermaid-test-"));
try {
  execFileSync("bash", [buildScript, "--check"], {
    cwd: repoRoot,
    encoding: "utf8",
    env: { ...process.env, TMPDIR: scratch },
    stdio: "pipe",
  });
} finally {
  rmSync(scratch, { recursive: true, force: true });
}

console.log("mermaid validator tests: OK");
