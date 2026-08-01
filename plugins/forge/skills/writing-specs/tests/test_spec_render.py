from __future__ import annotations

import html
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from html.parser import HTMLParser

import spec_render
from markdown_render import render_markdown
from spec_render import RenderFailure, build_pages, check_pages, expected_outputs
from spec_validate import validate_repository


TEST_DIR = Path(__file__).parent
FIXTURE_ROOT = TEST_DIR / "fixtures" / "pages-repository"
WRAPPER = TEST_DIR.parent / "scripts" / "spec-docs.sh"


def snapshot_tree(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(WRAPPER), *arguments],
        text=True,
        capture_output=True,
        check=False,
    )


class MermaidTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_mermaid = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = dict(attrs).get("class", "") or ""
        if tag == "pre" and "mermaid" in classes.split():
            self.in_mermaid = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "pre" and self.in_mermaid:
            self.in_mermaid = False

    def handle_data(self, data: str) -> None:
        if self.in_mermaid:
            self.parts.append(data)


class MarkdownRenderTest(unittest.TestCase):
    def test_supported_blocks_are_semantic_and_escape_first(self) -> None:
        source = """### Heading <unsafe>

Paragraph with `code <tag>` and [safe](https://example.com/a?x=\"quoted\").

- one
- two

1. first
2. second

| Name | Value |
|---|---|
| API | `<value>` |

```python
print(\"<unsafe>\")
```

<script>alert(1)</script>

[javascript](javascript:alert(1)) [data](data:text/html,bad) [control](https://example.com/\x01bad) [malformed](http://[invalid)
"""
        rendered = render_markdown(source)

        self.assertIn("<h3>Heading &lt;unsafe&gt;</h3>", rendered)
        self.assertIn("<ul>", rendered)
        self.assertIn("<ol>", rendered)
        self.assertIn('class="table-scroll"', rendered)
        self.assertIn('class="language-python"', rendered)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", rendered)
        self.assertNotIn("<script>alert(1)</script>", rendered)
        self.assertIn("code &lt;tag&gt;", rendered)
        self.assertIn("&quot;quoted&quot;", rendered)
        self.assertNotIn('href="javascript:', rendered)
        self.assertNotIn('href="data:', rendered)
        self.assertNotIn("\x01", rendered)
        self.assertIn('<span class="unsafe-link">malformed</span>', rendered)

    def test_mermaid_dom_text_is_byte_for_character_source_equivalent(self) -> None:
        mermaid = "flowchart LR\n    A[\"<source> & value\"] --> B"
        rendered = render_markdown(f"```mermaid\n{mermaid}\n```")
        parser = MermaidTextParser()
        parser.feed(rendered)
        self.assertEqual("".join(parser.parts), mermaid)
        self.assertIn('class="diagram-scroll"', rendered)


class SpecRenderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.repo_root = (Path(self.temporary.name) / "repository").resolve()
        shutil.copytree(FIXTURE_ROOT, self.repo_root)
        self.spec_root = self.repo_root / "docs/specs"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _documents(self):
        result = validate_repository(self.repo_root, Path("docs/specs"))
        self.assertEqual(result.diagnostics, ())
        return result.documents

    def _codes(self) -> set[str]:
        return {item.code for item in check_pages(self.repo_root, Path("docs/specs"))}

    def _build(self) -> tuple[Path, ...]:
        return build_pages(
            self.repo_root,
            Path("docs/specs"),
            changed=None,
            offline=True,
        )

    def test_expected_outputs_are_absolute_ordered_semantic_and_deterministic(self) -> None:
        outputs_one = expected_outputs(self.repo_root, self._documents())
        outputs_two = expected_outputs(self.repo_root, self._documents())

        self.assertEqual(list(outputs_one), sorted(outputs_one))
        self.assertTrue(all(path.is_absolute() for path in outputs_one))
        self.assertEqual(outputs_one, outputs_two)
        self.assertEqual(
            {path.relative_to(self.repo_root).as_posix() for path in outputs_one},
            {
                "docs/specs/001-basic/index.html",
                "docs/specs/002-related/index.html",
                "docs/specs/index.html",
            },
        )

        page = outputs_one[self.spec_root / "001-basic/index.html"].decode("utf-8")
        catalog = outputs_one[self.spec_root / "index.html"].decode("utf-8")
        self.assertTrue(page.endswith("\n"))
        self.assertFalse(page.endswith("\n\n"))
        self.assertNotIn("\r", page)
        self.assertTrue(catalog.endswith("\n"))
        self.assertFalse(catalog.endswith("\n\n"))
        self.assertNotIn("\r", catalog)
        unresolved_token = r"\{\{[A-Z][A-Z0-9_]*\}\}"
        self.assertNotRegex(page, unresolved_token)
        self.assertNotRegex(catalog, unresolved_token)
        self.assertIn('data-forge-spec-page="forge/spec-page@1"', page)
        self.assertIn('id="forge-spec-manifest"', page)
        self.assertIn('href="spec.md"', page)
        self.assertIn('href="../002-related/index.html"', page)
        self.assertIn('id="R1"', page)
        self.assertIn('id="AC1"', page)
        self.assertIn("요약", page)
        self.assertLess(page.index('id="overview"'), page.index('id="flows"'))
        self.assertLess(page.index('id="flows"'), page.index('id="requirements"'))
        self.assertLess(page.index('id="requirements"'), page.index('id="acceptance"'))
        self.assertIn('data-forge-spec-catalog="forge/spec-catalog@1"', catalog)
        self.assertIn('type="search"', catalog)
        self.assertIn('data-status="draft"', catalog)
        self.assertIn('data-kind="system"', catalog)
        self.assertIn('href="001-basic/spec.md"', catalog)
        self.assertIn('href="001-basic/index.html"', catalog)
        self.assertIn("deterministic-renderer-with-an-intentionally-long-component-label", catalog)

        manifest_match = re.search(
            r'<script type="application/json" id="forge-spec-manifest">(.*?)</script>',
            page,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(manifest_match)
        manifest = json.loads(manifest_match.group(1))
        self.assertEqual(manifest["schema"], "forge/spec-page@1")
        self.assertEqual(manifest["generator"], "forge-spec-pages/1")
        self.assertEqual(manifest["source_path"], "docs/specs/001-basic/spec.md")
        self.assertEqual(manifest["locale"], "ko")
        self.assertEqual(len(manifest["source_sha256"]), 64)
        self.assertEqual(len(manifest["asset_fingerprint"]), 64)

        for forbidden in (
            str(self.repo_root),
            str(Path.cwd()),
            socket.gethostname(),
        ):
            self.assertNotIn(forbidden, page)
            self.assertNotIn(forbidden, catalog)
        self.assertIsNone(re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", page))

    def test_catalog_metadata_values_with_spaces_are_json_encoded_losslessly(self) -> None:
        outputs = expected_outputs(self.repo_root, self._documents())
        catalog = outputs[self.spec_root / "index.html"].decode("utf-8")
        expected_components = [
            "parser",
            "developer tools",
            "deterministic-renderer-with-an-intentionally-long-component-label",
        ]
        encoded = (
            '[&quot;parser&quot;,&quot;developer tools&quot;,'
            '&quot;deterministic-renderer-with-an-intentionally-long-component-label&quot;]'
        )
        entry = re.search(
            r'<article class="catalog-entry" data-spec-id="002-related"[^>]*'
            r'data-components="([^"]*)"',
            catalog,
        )
        self.assertIsNotNone(entry)
        self.assertEqual(entry.group(1), encoded)
        self.assertEqual(json.loads(html.unescape(entry.group(1))), expected_components)
        self.assertIn('<option value="developer tools">developer tools</option>', catalog)

    def test_two_builds_are_byte_stable_and_check_is_read_only(self) -> None:
        first = self._build()
        bytes_one = {path: path.read_bytes() for path in first}
        second = self._build()
        self.assertEqual(bytes_one, {path: path.read_bytes() for path in second})
        before_check = snapshot_tree(self.spec_root)
        self.assertEqual(check_pages(self.repo_root, Path("docs/specs")), ())
        self.assertEqual(before_check, snapshot_tree(self.spec_root))

    def test_check_detects_source_page_catalog_manual_and_missing_drift(self) -> None:
        self._build()

        source = self.spec_root / "001-basic/spec.md"
        source.write_text(
            source.read_text(encoding="utf-8").replace("설명한다.", "설명한다!", 1),
            encoding="utf-8",
        )
        self.assertIn("SPEC_PAGE_STALE", self._codes())
        self._build()
        self.assertEqual(self._codes(), set())

        page = self.spec_root / "001-basic/index.html"
        page.write_text(page.read_text(encoding="utf-8") + "manual\n", encoding="utf-8")
        self.assertIn("SPEC_PAGE_STALE", self._codes())
        self._build()

        page.unlink()
        self.assertIn("SPEC_PAGE_MISSING", self._codes())
        self._build()

        catalog = self.spec_root / "index.html"
        catalog.unlink()
        self.assertIn("SPEC_PAGE_MISSING", self._codes())
        self._build()
        self.assertEqual(self._codes(), set())

    def test_check_detects_and_full_build_removes_orphan(self) -> None:
        self._build()
        orphan = self.spec_root / "099-orphan/index.html"
        orphan.parent.mkdir()
        orphan.write_bytes((self.spec_root / "001-basic/index.html").read_bytes())
        before = snapshot_tree(self.spec_root)
        self.assertIn("SPEC_PAGE_ORPHAN", self._codes())
        self.assertEqual(before, snapshot_tree(self.spec_root))
        self._build()
        self.assertFalse(orphan.exists())
        self.assertEqual(self._codes(), set())

    def test_user_index_and_outside_symlink_directory_are_not_orphans_or_touched(self) -> None:
        self._build()
        user_index = self.spec_root / "097-user-owned/index.html"
        user_index.parent.mkdir()
        user_index.write_text("<!doctype html><title>User owned</title>\n", encoding="utf-8")

        outside = self.repo_root.parent / "outside-owned"
        outside.mkdir()
        outside_index = outside / "index.html"
        outside_index.write_bytes((self.spec_root / "001-basic/index.html").read_bytes())
        symlink_parent = self.spec_root / "098-outside-link"
        symlink_parent.symlink_to(outside, target_is_directory=True)

        user_before = user_index.read_bytes()
        outside_before = outside_index.read_bytes()
        diagnostics = check_pages(self.repo_root, Path("docs/specs"))
        self.assertNotIn(
            "docs/specs/097-user-owned/index.html",
            {item.path for item in diagnostics if item.code == "SPEC_PAGE_ORPHAN"},
        )
        self.assertNotIn(
            "docs/specs/098-outside-link/index.html",
            {item.path for item in diagnostics if item.code == "SPEC_PAGE_ORPHAN"},
        )

        self._build()
        self.assertEqual(user_index.read_bytes(), user_before)
        self.assertEqual(outside_index.read_bytes(), outside_before)
        self.assertTrue(symlink_parent.is_symlink())

    def test_template_and_generator_drift_are_stale_until_full_build(self) -> None:
        self._build()
        original_template = spec_render.PAGE_TEMPLATE_PATH
        replacement = self.repo_root / "page-template.html"
        replacement.write_bytes(
            original_template.read_bytes().replace(b"#f7f4ee", b"#f7f4ef", 1)
        )

        with patch.object(spec_render, "PAGE_TEMPLATE_PATH", replacement):
            self.assertIn("SPEC_PAGE_STALE", self._codes())
            self._build()
            self.assertEqual(self._codes(), set())

        self.assertIn("SPEC_PAGE_STALE", self._codes())
        self._build()
        self.assertEqual(self._codes(), set())

        with patch.object(spec_render, "GENERATOR_VERSION", "forge-spec-pages/2"):
            self.assertIn("SPEC_PAGE_STALE", self._codes())
            self._build()
            self.assertEqual(self._codes(), set())

        self.assertIn("SPEC_PAGE_STALE", self._codes())

    def test_changed_build_replaces_exact_page_and_catalog_only(self) -> None:
        outputs = self._build()
        unchanged = self.spec_root / "002-related/index.html"
        changed_page = self.spec_root / "001-basic/index.html"
        catalog = self.spec_root / "index.html"
        for path in outputs:
            os.utime(path, ns=(1_000_000_000, 1_000_000_000))

        source = self.spec_root / "001-basic/spec.md"
        source.write_text(
            source.read_text(encoding="utf-8").replace("설명한다.", "설명한다!", 1),
            encoding="utf-8",
        )
        built = build_pages(
            self.repo_root,
            Path("docs/specs"),
            changed=Path("docs/specs/001-basic/spec.md"),
            offline=True,
        )
        self.assertEqual(built, (changed_page, catalog))
        self.assertEqual(unchanged.stat().st_mtime_ns, 1_000_000_000)
        self.assertNotEqual(changed_page.stat().st_mtime_ns, 1_000_000_000)
        self.assertNotEqual(catalog.stat().st_mtime_ns, 1_000_000_000)
        self.assertEqual(self._codes(), set())

    def test_shared_fingerprint_or_generator_drift_expands_changed_build(self) -> None:
        outputs = self._build()
        replacement = self.repo_root / "page-template.html"
        replacement.write_bytes(
            spec_render.PAGE_TEMPLATE_PATH.read_bytes().replace(
                b"#f7f4ee", b"#f7f4ef", 1
            )
        )

        for drift in ("template", "generator"):
            with self.subTest(drift=drift):
                for path in outputs:
                    os.utime(path, ns=(1_000_000_000, 1_000_000_000))
                context = (
                    patch.object(spec_render, "PAGE_TEMPLATE_PATH", replacement)
                    if drift == "template"
                    else patch.object(spec_render, "GENERATOR_VERSION", "forge-spec-pages/2")
                )
                with context:
                    built = build_pages(
                        self.repo_root,
                        Path("docs/specs"),
                        changed=Path("docs/specs/001-basic/spec.md"),
                        offline=True,
                    )
                    self.assertEqual(set(built), set(outputs))
                    self.assertTrue(
                        all(path.stat().st_mtime_ns != 1_000_000_000 for path in outputs)
                    )
                self._build()

    def test_runtime_and_mermaid_asset_drift_are_stale_and_expand_changed_build(self) -> None:
        cases = (
            (
                "RUNTIME_PATH",
                TEST_DIR.parent / "assets/spec-pages-runtime.mjs",
            ),
            (
                "MERMAID_PATH",
                TEST_DIR.parent / "assets/mermaid.min.js",
            ),
        )
        for constant, source_asset in cases:
            with self.subTest(asset=source_asset.name):
                outputs = self._build()
                replacement = self.repo_root / source_asset.name
                original = source_asset.read_bytes()
                replacement.write_bytes(
                    (b"'" if original[:1] != b"'" else b'"') + original[1:]
                )
                with patch.object(spec_render, constant, replacement, create=True):
                    self.assertIn("SPEC_PAGE_STALE", self._codes())
                    built = build_pages(
                        self.repo_root,
                        Path("docs/specs"),
                        changed=Path("docs/specs/001-basic/spec.md"),
                        offline=True,
                    )
                    self.assertEqual(set(built), set(outputs))
                    self.assertEqual(self._codes(), set())
                self.assertIn("SPEC_PAGE_STALE", self._codes())
                self._build()

    def test_render_failure_computes_all_bytes_before_any_write(self) -> None:
        orphan = self.spec_root / "099-orphan/index.html"
        orphan.parent.mkdir()
        orphan.write_text("orphan\n", encoding="utf-8")
        before = snapshot_tree(self.spec_root)
        with patch(
            "spec_render.render_spec_page",
            side_effect=[b"first", RenderFailure("injected render failure")],
        ):
            with self.assertRaisesRegex(RenderFailure, "injected"):
                self._build()
        self.assertEqual(before, snapshot_tree(self.spec_root))

    def test_second_publish_failure_rolls_back_replacements_and_orphan_deletion(self) -> None:
        outputs = self._build()
        source = self.spec_root / "001-basic/spec.md"
        source.write_text(
            source.read_text(encoding="utf-8").replace("설명한다.", "설명한다!", 1),
            encoding="utf-8",
        )
        orphan = self.spec_root / "099-orphan/index.html"
        orphan.parent.mkdir()
        orphan.write_bytes((self.spec_root / "001-basic/index.html").read_bytes())
        before = snapshot_tree(self.spec_root)
        output_set = {path.resolve() for path in outputs}
        real_replace = os.replace
        publication_count = 0
        fault_injected = False

        def fail_second_publication(source_path, destination_path) -> None:
            nonlocal publication_count, fault_injected
            destination = Path(destination_path).resolve()
            if destination in output_set and not fault_injected:
                publication_count += 1
                if publication_count == 2:
                    fault_injected = True
                    raise OSError("injected second publication failure")
            real_replace(source_path, destination_path)

        with patch.object(spec_render.os, "replace", side_effect=fail_second_publication):
            with self.assertRaisesRegex(RenderFailure, "second publication"):
                self._build()

        self.assertEqual(before, snapshot_tree(self.spec_root))
        leftovers = [
            path
            for path in self.spec_root.rglob("*")
            if path.name.startswith(".index.html.")
        ]
        self.assertEqual(leftovers, [])

    def test_invalid_repository_fails_without_writes(self) -> None:
        source = self.spec_root / "001-basic/spec.md"
        source.write_text(source.read_text(encoding="utf-8") + "\n## Extra\n", encoding="utf-8")
        before = snapshot_tree(self.spec_root)
        with self.assertRaises(RenderFailure):
            self._build()
        self.assertEqual(before, snapshot_tree(self.spec_root))

    def test_cli_build_check_status_and_path_safety_contract(self) -> None:
        build = run_cli(
            "--repo-root",
            str(self.repo_root),
            "build",
            "--root",
            "docs/specs",
            "--offline",
        )
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        self.assertEqual(
            build.stdout.splitlines(),
            [
                "docs/specs/001-basic/index.html",
                "docs/specs/002-related/index.html",
                "docs/specs/index.html",
            ],
        )
        checked = run_cli(
            "--repo-root", str(self.repo_root), "check", "--root", "docs/specs"
        )
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

        (self.spec_root / "001-basic/index.html").write_text("manual\n", encoding="utf-8")
        contract_failure = run_cli(
            "--repo-root", str(self.repo_root), "check", "--root", "docs/specs"
        )
        self.assertEqual(contract_failure.returncode, 1)
        self.assertIn("SPEC_PAGE_STALE", contract_failure.stdout)

        for command in (
            ("build", "--root", str(self.spec_root), "--offline"),
            ("check", "--root", str(self.spec_root)),
            (
                "build",
                "--root",
                "docs/specs",
                "--changed",
                str(self.spec_root / "001-basic/spec.md"),
                "--offline",
            ),
            (
                "build",
                "--root",
                "docs/specs",
                "--changed",
                "docs/specs/001-basic/not-spec.md",
                "--offline",
            ),
            (
                "build",
                "--root",
                "docs/specs",
                "--changed",
                "../escape/spec.md",
                "--offline",
            ),
            ("build", "--root", "docs/specs"),
        ):
            before = snapshot_tree(self.spec_root)
            result = run_cli("--repo-root", str(self.repo_root), *command)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(before, snapshot_tree(self.spec_root))

    def test_cli_shape_valid_missing_changed_is_usage_without_writes(self) -> None:
        self._build()
        before = snapshot_tree(self.spec_root)
        result = run_cli(
            "--repo-root",
            str(self.repo_root),
            "build",
            "--root",
            "docs/specs",
            "--changed",
            "docs/specs/099-missing/spec.md",
            "--offline",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(before, snapshot_tree(self.spec_root))


if __name__ == "__main__":
    unittest.main()
