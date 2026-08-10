from __future__ import annotations

from dataclasses import replace
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest


TEST_DIR = Path(__file__).resolve().parent
SCRIPTS = TEST_DIR.parent / "scripts"
REPOSITORY = TEST_DIR / "fixtures" / "repository"
sys.path.insert(0, str(SCRIPTS))

import review_renderer  # noqa: E402
import review_components  # noqa: E402
from review_ir import build_semantic_ir  # noqa: E402
from review_planner import ViewContext  # noqa: E402
from review_renderer import render_review  # noqa: E402
from review_sources import (  # noqa: E402
    collect_brief_sources,
    collect_plan_sources,
    collect_project_sources,
    collect_spec_sources,
)


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.components: list[str] = []
        self.manifest_text: list[str] = []
        self.mermaid: list[str] = []
        self.visible_text: list[str] = []
        self._manifest = False
        self._mermaid = False
        self._hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("data-component"):
            self.components.append(values["data-component"])
        if tag == "script" and values.get("id") == "forge-source-manifest":
            self._manifest = True
        if tag in {"script", "style"}:
            self._hidden_depth += 1
        if tag == "pre" and "mermaid" in (values.get("class") or "").split():
            self._mermaid = True
            self.mermaid.append("")

    def handle_endtag(self, tag):
        if tag == "script":
            self._manifest = False
        if tag in {"script", "style"}:
            self._hidden_depth -= 1
        if tag == "pre":
            self._mermaid = False

    def handle_data(self, data):
        if self._manifest:
            self.manifest_text.append(data)
        if self._mermaid:
            self.mermaid[-1] += data
        if self._hidden_depth == 0:
            self.visible_text.append(data)

    @property
    def manifest(self):
        return json.loads("".join(self.manifest_text))

    @property
    def visible(self):
        return " ".join(" ".join(self.visible_text).split())


def spec_bundle(comparison: bool = False):
    comparisons = (
        (REPOSITORY / "docs/specs/supporting-policy",) if comparison else ()
    )
    return collect_spec_sources(
        REPOSITORY / "docs/specs/semantic-spec-bundles", comparisons, REPOSITORY
    )


def plan_bundle():
    return collect_plan_sources(REPOSITORY / "docs/plans/001-demo/plan.md", REPOSITORY)


def project_bundle():
    return collect_project_sources(
        REPOSITORY / "docs/project/project-map.md", REPOSITORY
    )


def render(bundle, *, intent=None, subtype=None, locale="en", offline=False):
    kwargs = {}
    if intent is not None:
        ir = build_semantic_ir(bundle)
        kwargs = {
            "semantic_ir": ir,
            "view_context": ViewContext(
                bundle.kind,
                "system" if bundle.kind == "spec" else bundle.kind,
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
        rebuild_command="build-visual-docs.sh --kind spec",
        source_base="../../" if bundle.kind == "project" else "../../../",
        offline=offline,
        **kwargs,
    )


class ReviewRendererTest(unittest.TestCase):
    def test_project_handbook_is_human_first_and_reuses_spec_entities(self) -> None:
        handbook = render(project_bundle(), locale="ko")
        spec = render(spec_bundle(), locale="ko")
        project_parsed = DocumentParser()
        project_parsed.feed(handbook)
        spec_parsed = DocumentParser()
        spec_parsed.feed(spec)

        self.assertIn('class="project-workspace"', handbook)
        self.assertIn('id="project-search"', handbook)
        self.assertIn('role="tree"', handbook)
        self.assertIn('class="project-detail-pane"', handbook)
        self.assertIn('class="project-back"', handbook)
        self.assertEqual(
            re.findall(
                r'data-project-root="true"[^>]*>.*?'
                r'<span class="project-tree-label">([^<]+)</span>',
                handbook,
                re.DOTALL,
            ),
            ["개요", "설계 기준", "프로젝트 구조"],
        )
        self.assertIn('data-node-kind="spec-bundle"', handbook)
        self.assertIn('data-node-kind="spec-member"', handbook)
        self.assertIn('data-node-kind="spec-section"', handbook)
        self.assertIn('data-node-kind="structure-entry"', handbook)
        self.assertIn('data-project-detail data-route="project-overview"', handbook)
        self.assertIn("역할", project_parsed.visible)
        self.assertIn("담당 범위", project_parsed.visible)
        self.assertIn("주요 파일", project_parsed.visible)
        self.assertIn("출처·검증", project_parsed.visible)
        self.assertLess(handbook.index("역할"), handbook.index("담당 범위"))
        self.assertLess(handbook.index("담당 범위"), handbook.index("주요 파일"))
        self.assertNotIn("Complete Spec details", handbook)
        self.assertNotIn("Developer information", project_parsed.visible)
        self.assertNotIn("개발자 정보", project_parsed.visible)
        self.assertEqual(review_components._project_term("Launch Baseline", True), "출시 기준")
        self.assertEqual(review_components._project_term("Behaviour & Flows", True), "동작과 흐름")

        project_members = {
            (row["path"], row["sha256"])
            for row in project_parsed.manifest["member_sources"]
            if row["role"] == "declared_spec"
        }
        spec_members = {
            (row["path"], row["sha256"])
            for row in spec_parsed.manifest["member_sources"]
            if row["role"] == "primary_spec"
        }
        self.assertEqual(project_members, spec_members)
        self.assertEqual(
            re.findall(r'data-mermaid-sha256="([0-9a-f]{64})"', handbook),
            re.findall(r'data-mermaid-sha256="([0-9a-f]{64})"', spec),
        )
        self.assertIn(
            "Every declared member enters the review source set exactly once",
            project_parsed.visible,
        )
        self.assertIn(
            "Defines how structured Spec Bundle members and statements remain traceable.",
            project_parsed.visible,
        )
        self.assertIn("docs/specs/semantic-spec-bundles", project_parsed.visible)
        self.assertIn("forge", project_parsed.visible)
        self.assertRegex(
            handbook,
            r'근거 문장.*href="#statement-[0-9a-f]{20}"',
        )

    def test_bundle_titles_paths_and_full_statements_are_visible_without_internal_ids(self) -> None:
        with TemporaryDirectory() as temporary:
            repository = Path(temporary)
            source = REPOSITORY / "docs/specs/semantic-spec-bundles"
            current = repository / "docs/specs/current-review-contract"
            comparison = repository / "docs/specs/comparison-review-contract"
            shutil.copytree(source, current)
            shutil.copytree(source, comparison)
            document = render(
                collect_spec_sources(current, (comparison,), repository),
                intent="comparison",
                locale="ko",
            )

        parsed = DocumentParser()
        parsed.feed(document)
        self.assertIn("<h1>Semantic Spec Bundle Contract</h1>", document)
        self.assertIn("Statement Traceability and Validation", parsed.visible)
        self.assertIn("statement-traceability-and-validation.md", parsed.visible)
        self.assertIn(
            "Every declared member enters the review source set exactly once",
            parsed.visible,
        )
        self.assertIn(
            "Acceptance statements connect to requirements across member files",
            parsed.visible,
        )
        self.assertIsNone(re.search(r"\b(?:R|AC)[0-9]+\b", parsed.visible))
        self.assertNotIn("primary--", parsed.visible)
        self.assertNotIn("primary_spec", parsed.visible)
        self.assertNotIn("comparison_spec", parsed.visible)
        self.assertIsNone(re.search(r"\b[0-9a-f]{64}\b", parsed.visible))

        self.assertEqual(set(parsed.manifest), {
            "bundles", "checkpoint", "commit", "counts", "freshness",
            "generated_at", "kind", "locale", "offline", "document_sources",
            "output_lifecycle", "presentation_plan", "rebuild_command", "view_id",
            "source_base", "member_sources", "view_context",
        })
        self.assertEqual(len(parsed.manifest["bundles"]), 2)
        self.assertEqual(len(parsed.manifest["member_sources"]), 10)
        for bundle_row in parsed.manifest["bundles"]:
            members = [
                row for row in parsed.manifest["member_sources"]
                if row["bundle_path"] == bundle_row["path"]
            ]
            self.assertTrue(members)
            self.assertEqual(
                {row["bundle_sha256"] for row in members},
                {bundle_row["sha256"]},
            )

        requirement_targets = re.findall(
            r'id="([^"]+)"[^>]*data-statement-kind="requirement"', document
        )
        acceptance_keys = re.findall(
            r'data-statement-kind="acceptance"[^>]*data-storage-key="([^"]+)"',
            document,
        )
        covered_targets = re.findall(
            r'data-relation="covers" href="#([^"]+)"', document
        )
        self.assertEqual(len(requirement_targets), len(set(requirement_targets)))
        self.assertEqual(len(acceptance_keys), len(set(acceptance_keys)))
        self.assertEqual(covered_targets, requirement_targets)

    def test_adaptive_renderer_emits_component_navigation(self) -> None:
        document = render(spec_bundle(comparison=True))
        parsed = DocumentParser()
        parsed.feed(document)
        self.assertIn('class="review-navigation"', document)
        self.assertIn("source-detail", parsed.components)
        self.assertNotIn('class="tab-bar"', document)
        self.assertNotIn(".orientation", parsed.visible)
        self.assertIn("Trace each item to its source path.", parsed.visible)
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
        self.assertIn(
            'data-source-path="docs/specs/semantic-spec-bundles/supporting-visual-map.md"',
            document,
        )
        self.assertIn("Semantic Spec Bundle Contract", document)

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
