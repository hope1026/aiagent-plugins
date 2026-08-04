from __future__ import annotations

from dataclasses import replace
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unittest


TEST_DIR = Path(__file__).resolve().parent
SCRIPTS = TEST_DIR.parent / "scripts"
REPOSITORY = TEST_DIR / "fixtures" / "repository"
sys.path.insert(0, str(SCRIPTS))

import review_renderer  # noqa: E402
from review_ir import build_semantic_ir  # noqa: E402
from review_planner import ViewContext  # noqa: E402
from review_renderer import render_review  # noqa: E402
from review_sources import collect_plan_sources, collect_spec_sources  # noqa: E402


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.components: list[str] = []
        self.manifest_text: list[str] = []
        self.mermaid: list[str] = []
        self._manifest = False
        self._mermaid = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("data-component"):
            self.components.append(values["data-component"])
        if tag == "script" and values.get("id") == "forge-source-manifest":
            self._manifest = True
        if tag == "pre" and "mermaid" in (values.get("class") or "").split():
            self._mermaid = True
            self.mermaid.append("")

    def handle_endtag(self, tag):
        if tag == "script":
            self._manifest = False
        if tag == "pre":
            self._mermaid = False

    def handle_data(self, data):
        if self._manifest:
            self.manifest_text.append(data)
        if self._mermaid:
            self.mermaid[-1] += data

    @property
    def manifest(self):
        return json.loads("".join(self.manifest_text))


def spec_bundle(comparison: bool = False):
    comparisons = (REPOSITORY / "docs/specs/002-beta/spec.md",) if comparison else ()
    return collect_spec_sources(
        REPOSITORY / "docs/specs/008-alpha/spec.md", comparisons, REPOSITORY
    )


def plan_bundle():
    return collect_plan_sources(REPOSITORY / "docs/plans/001-demo/plan.md", REPOSITORY)


def render(bundle, *, intent=None, subtype=None, locale="en", offline=False):
    kwargs = {}
    if intent is not None:
        ir = build_semantic_ir(bundle)
        kwargs = {
            "semantic_ir": ir,
            "view_context": ViewContext(
                bundle.mode,
                "system" if bundle.mode == "spec" else "plan",
                subtype,
                intent,
                "mixed",
                locale,
                "standalone",
            ),
        }
    return render_review(
        bundle,
        review_id="adaptive-review",
        locale=locale,
        generated_at="2026-08-04T00:00:00Z",
        checkpoint="component-ready",
        commit="0123456789abcdef",
        rebuild_command="build-review-viewer.sh --mode spec",
        source_base="../../../",
        offline=offline,
        **kwargs,
    )


class ReviewRendererTest(unittest.TestCase):
    def test_adaptive_renderer_emits_component_navigation(self) -> None:
        document = render(spec_bundle(comparison=True))
        parsed = DocumentParser()
        parsed.feed(document)
        self.assertIn('class="review-navigation"', document)
        self.assertIn("source-detail", parsed.components)
        self.assertNotIn('class="tab-bar"', document)
        self.assertNotRegex(document, r"\{\{[A-Z][A-Z0-9_]*\}\}")
        self.assertEqual(parsed.manifest["freshness"], "unverified")

    def test_same_source_changes_composition_by_intent(self) -> None:
        bundle = spec_bundle()
        approval = render(bundle, intent="approval", subtype="workflow")
        implementation = render(bundle, intent="implementation", subtype="workflow")
        self.assertLess(approval.index('data-component="state-map"'), approval.index('data-component="source-detail"'))
        self.assertLess(implementation.index('data-component="runtime-atlas"'), implementation.index('data-component="acceptance-coverage"'))
        self.assertNotEqual(approval, implementation)

    def test_source_mermaid_and_provenance_are_preserved(self) -> None:
        bundle = spec_bundle()
        document = render(bundle, intent="review", subtype="workflow")
        parsed = DocumentParser()
        parsed.feed(document)
        self.assertEqual(parsed.mermaid, [block.text for block in bundle.mermaid])
        self.assertIn('data-source-path="docs/specs/008-alpha/spec.md"', document)
        self.assertIn("current--008-alpha", document)

    def test_plan_uses_execution_components_and_all_source_detail(self) -> None:
        document = render(plan_bundle(), intent="execution")
        parsed = DocumentParser()
        parsed.feed(document)
        self.assertEqual(parsed.components[0], "route-map")
        self.assertIn("runtime-atlas", parsed.components)
        self.assertIn("source-detail", parsed.components)
        self.assertIn("docs/plans/001-demo/tasks/002-manifest.md", document)

    def test_renderer_is_deterministic_and_keeps_visual_system(self) -> None:
        first = render(spec_bundle(), intent="review", subtype="api")
        second = render(spec_bundle(), intent="review", subtype="api")
        self.assertEqual(first, second)
        self.assertTrue(first.endswith("\n"))
        self.assertIn("--bg: #f7f3eb", first)
        self.assertIn("--accent: #2557a7", first)
        self.assertIsNone(re.search(r"/Users/|/home/|[A-Z]:\\", first))


class ConditionalMermaidLoaderTest(unittest.TestCase):
    def test_bundle_without_diagram_omits_runtime(self) -> None:
        bundle = spec_bundle()
        primary = tuple(
            replace(source, document=replace(source.document, mermaid=()))
            for source in bundle.primary
        )
        without = replace(bundle, primary=primary)
        self.assertFalse(review_renderer.bundle_needs_mermaid(without))
        self.assertEqual(review_renderer._mermaid_loader(False, without), "")

    def test_offline_bundle_with_diagram_embeds_runtime(self) -> None:
        bundle = spec_bundle()
        self.assertTrue(review_renderer.bundle_needs_mermaid(bundle))
        self.assertIn('data-mermaid-delivery="offline"', review_renderer._mermaid_loader(True, bundle))


if __name__ == "__main__":
    unittest.main()
