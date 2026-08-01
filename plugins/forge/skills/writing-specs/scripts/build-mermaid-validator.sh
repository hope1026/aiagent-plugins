#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ASSET_DIR="$SKILL_DIR/assets"
ENTRY="$SCRIPT_DIR/mermaid_validate.mjs"
BOOLBASE_LICENSE="$SCRIPT_DIR/boolbase.LICENSE"

temporary_paths=()
cleanup() {
  local path
  for path in "${temporary_paths[@]:-}"; do
    if [[ -n "$path" && -d "$path" ]]; then
      rm -rf -- "$path"
    fi
  done
}
trap cleanup EXIT

new_temporary_directory() {
  NEW_TEMPORARY_DIRECTORY="$(mktemp -d "${TMPDIR:-/tmp}/forge-mermaid-build.XXXXXX")"
  temporary_paths+=("$NEW_TEMPORARY_DIRECTORY")
}

build_into() {
  local output_dir="$1"
  local build_root
  new_temporary_directory
  build_root="$NEW_TEMPORARY_DIRECTORY"
  mkdir -p "$output_dir"
  cp "$SCRIPT_DIR/package.json" "$SCRIPT_DIR/package-lock.json" "$ENTRY" "$BOOLBASE_LICENSE" "$build_root/"
  (
    cd "$build_root"
    npm ci --ignore-scripts --no-audit --no-fund --loglevel=error
    ./node_modules/.bin/esbuild mermaid_validate.mjs \
      --bundle \
      --platform=node \
      --format=esm \
      --target=node20 \
      --metafile="$output_dir/mermaid-validator.meta.json" \
      --outfile="$output_dir/mermaid-validator.bundle.mjs"
  )
  (
    cd "$build_root"
    node --input-type=module --eval '
    import { readFileSync, readdirSync, writeFileSync } from "node:fs";
    import { join } from "node:path";

    const metafile = JSON.parse(readFileSync(process.argv[1], "utf8"));
    const overridePath = process.argv[2];
    const outputPath = process.argv[3];
    const packageRoots = new Set();

    for (const input of Object.keys(metafile.inputs)) {
      const marker = "node_modules/";
      const offset = input.lastIndexOf(marker);
      if (offset < 0) {
        continue;
      }
      const segments = input.slice(offset + marker.length).split("/");
      const packageSegments = segments[0].startsWith("@") ? segments.slice(0, 2) : segments.slice(0, 1);
      packageRoots.add(`${input.slice(0, offset + marker.length)}${packageSegments.join("/")}`);
    }

    const packages = [...packageRoots].map((root) => {
      const manifest = JSON.parse(readFileSync(join(root, "package.json"), "utf8"));
      return { root, manifest };
    }).sort((left, right) => {
      const leftKey = `${left.manifest.name}@${left.manifest.version}\u0000${left.root}`;
      const rightKey = `${right.manifest.name}@${right.manifest.version}\u0000${right.root}`;
      return leftKey < rightKey ? -1 : leftKey > rightKey ? 1 : 0;
    });

    const sections = [];
    for (const item of packages) {
      const packageId = `${item.manifest.name}@${item.manifest.version}`;
      const licenseFiles = readdirSync(item.root, { withFileTypes: true })
        .filter((entry) => entry.isFile())
        .map((entry) => entry.name)
        .filter((name) => /^(?:licen[sc]e|copying|notice)(?:$|[-_.])/i.test(name))
        .filter((name) => !/\.(?:c?js|mjs|ts|json)$/i.test(name))
        .sort();

      const texts = licenseFiles.map((name) => ({
        source: name,
        text: readFileSync(join(item.root, name), "utf8"),
      }));
      if (packageId === "boolbase@1.0.0" && texts.length === 0) {
        texts.push({ source: "Forge boolbase.LICENSE override", text: readFileSync(overridePath, "utf8") });
      }
      if (texts.length === 0) {
        throw new Error(`Bundled package ${packageId} has no distributable license or notice text.`);
      }

      const declared = typeof item.manifest.license === "string"
        ? item.manifest.license
        : "See included license text";
      const body = texts.map(({ source, text }) => {
        const normalized = text.replace(/\r\n?/g, "\n").trimEnd();
        if (!normalized) {
          throw new Error(`Bundled package ${packageId} has an empty license file: ${source}`);
        }
        return `Source file: ${source}\n----- BEGIN LICENSE TEXT -----\n${normalized}\n----- END LICENSE TEXT -----`;
      }).join("\n\n");
      sections.push(`Package: ${packageId}\nPackage root: ${item.root}\nDeclared license: ${declared}\n${body}`);
    }

    const header = [
      "Forge Mermaid validator third-party notices",
      "Generated from the esbuild metafile and installed package license files.",
      "Only package instances whose code is present in the distributed bundle are listed.",
      "Do not edit this generated file.",
      "",
    ].join("\n");
    writeFileSync(outputPath, `${header}${sections.join("\n\n========================================\n\n")}\n`, "utf8");
    ' "$output_dir/mermaid-validator.meta.json" "$build_root/boolbase.LICENSE" "$output_dir/mermaid-validator-THIRD-PARTY.txt"
  )
}

refresh() {
  local generated
  new_temporary_directory
  generated="$NEW_TEMPORARY_DIRECTORY"
  build_into "$generated"
  mkdir -p "$ASSET_DIR"
  cp "$generated/mermaid-validator.bundle.mjs" "$ASSET_DIR/mermaid-validator.bundle.mjs"
  cp "$generated/mermaid-validator-THIRD-PARTY.txt" "$ASSET_DIR/mermaid-validator-THIRD-PARTY.txt"
  (
    cd "$ASSET_DIR"
    shasum -a 256 mermaid.min.js mermaid.LICENSE \
      mermaid-validator.bundle.mjs mermaid-validator-THIRD-PARTY.txt \
      > mermaid.sha256
  )
}

check() {
  local first second
  new_temporary_directory
  first="$NEW_TEMPORARY_DIRECTORY"
  new_temporary_directory
  second="$NEW_TEMPORARY_DIRECTORY"
  build_into "$first"
  build_into "$second"
  cmp "$first/mermaid-validator.bundle.mjs" "$second/mermaid-validator.bundle.mjs"
  cmp "$first/mermaid-validator-THIRD-PARTY.txt" "$second/mermaid-validator-THIRD-PARTY.txt"
  cmp "$first/mermaid-validator.bundle.mjs" "$ASSET_DIR/mermaid-validator.bundle.mjs"
  cmp "$first/mermaid-validator-THIRD-PARTY.txt" "$ASSET_DIR/mermaid-validator-THIRD-PARTY.txt"
  (
    cd "$ASSET_DIR"
    shasum -a 256 --strict -c mermaid.sha256
  )
}

case "${1:-}" in
  --refresh)
    refresh
    ;;
  --check)
    check
    ;;
  *)
    printf 'Usage: %s --refresh|--check\n' "$0" >&2
    exit 2
    ;;
esac
