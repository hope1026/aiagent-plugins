#!/usr/bin/env python3
"""Task 6 rendering contract tests for requested Review Viewers."""

from __future__ import annotations

from html.parser import HTMLParser
import hashlib
import json
from dataclasses import replace
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


TEST_DIR = Path(__file__).resolve().parent
SKILL_DIR = TEST_DIR.parent
SCRIPTS = SKILL_DIR / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from review_sources import collect_plan_sources, collect_spec_sources  # noqa: E402
from review_freshness import _aggregate  # noqa: E402

try:
    import review_renderer  # type: ignore[import-not-found]  # noqa: E402
    from review_renderer import render_review  # noqa: E402
except ModuleNotFoundError:
    review_renderer = None
    render_review = None


FIXTURE_ROOT = TEST_DIR / "fixtures/repository"
PANEL_IDS = ("overview", "requirements", "flows", "data", "acceptance", "history")


class _DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.panels: list[str] = []
        self.mermaid: list[str] = []
        self.manifest_parts: list[str] = []
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self._mermaid = False
        self._manifest = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = (values.get("class") or "").split()
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if values.get("href"):
            self.hrefs.append(values["href"] or "")
        if tag == "section" and "tab-panel" in classes:
            self.panels.append(values.get("id") or "")
        if tag == "pre" and "mermaid" in classes:
            self._mermaid = True
            self.mermaid.append("")
        if tag == "script" and values.get("id") == "forge-source-manifest":
            self._manifest = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "pre" and self._mermaid:
            self._mermaid = False
        if tag == "script" and self._manifest:
            self._manifest = False

    def handle_data(self, data: str) -> None:
        if self._mermaid:
            self.mermaid[-1] += data
        if self._manifest:
            self.manifest_parts.append(data)

    @property
    def manifest(self) -> dict[str, object]:
        return json.loads("".join(self.manifest_parts))


def _spec_bundle():
    return collect_spec_sources(
        FIXTURE_ROOT / "docs/specs/008-alpha/spec.md",
        [FIXTURE_ROOT / "docs/specs/002-beta/spec.md"],
        FIXTURE_ROOT,
    )


def _plan_bundle():
    return collect_plan_sources(
        FIXTURE_ROOT / "docs/plans/001-demo/plan.md",
        FIXTURE_ROOT,
    )


def _render(bundle, *, review_id: str, locale: str, offline: bool) -> str:
    if render_review is None:
        raise AssertionError("Task 6 render_review must be implemented")
    return render_review(
        bundle,
        review_id=review_id,
        locale=locale,
        generated_at="2026-08-01T00:00:00Z",
        checkpoint="source-model-ready",
        commit="0123456789abcdef",
        rebuild_command="build-review-viewer.sh --mode plan --review-id demo",
        source_base="../../../",
        offline=offline,
    )


class ReviewRendererTest(unittest.TestCase):
    def test_ac20_renderer_uses_six_panels_and_task5_manifest_shape(self) -> None:
        document = _render(_spec_bundle(), review_id="spec-review", locale="en", offline=False)
        parsed = _DocumentParser()
        parsed.feed(document)

        self.assertEqual(parsed.panels, list(PANEL_IDS))
        manifest = parsed.manifest
        self.assertEqual(
            set(manifest),
            {
                "review_id", "mode", "locale", "generated_at", "checkpoint",
                "commit", "rebuild_command", "source_base", "offline", "counts",
                "freshness", "sources",
            },
        )
        self.assertEqual(manifest["freshness"], "unverified")
        self.assertEqual(manifest["source_base"], "../../../")
        self.assertEqual(
            [row["role"] for row in manifest["sources"]],
            ["primary_spec", "comparison_spec"],
        )
        self.assertNotRegex(document, r"\{\{[A-Z][A-Z0-9_]*\}\}")

    def test_ac4_source_mermaid_is_byte_identical_and_provenanced(self) -> None:
        bundle = _spec_bundle()
        document = _render(bundle, review_id="spec-review", locale="en", offline=False)
        parsed = _DocumentParser()
        parsed.feed(document)

        self.assertEqual(parsed.mermaid, [block.text for block in bundle.mermaid])
        for block in bundle.mermaid:
            digest = hashlib.sha256(block.text.encode("utf-8")).hexdigest()
            self.assertIn(f'data-mermaid-sha256="{digest}"', document)
        self.assertIn('data-origin="Current spec source"', document)
        self.assertIn('data-source-path="docs/specs/008-alpha/spec.md"', document)

    def test_ac5_plan_has_namespaced_trace_and_three_signature_views(self) -> None:
        document = _render(_plan_bundle(), review_id="plan-review", locale="ko", offline=True)

        self.assertIn('id="plan--001-demo-Task1"', document)
        self.assertIn('id="plan--001-demo-Task1-Step1"', document)
        self.assertIn('id="context--008-alpha-R1"', document)
        self.assertIn('id="context--002-beta-AC6"', document)
        self.assertIn("Route Map", document)
        self.assertIn("Runtime Atlas", document)
        self.assertIn("AC Coverage", document)
        self.assertIn('data-origin="Derived view"', document)
        self.assertIn('data-origin="Related spec context"', document)
        self.assertNotIn("inferred relation", document.lower())

    def test_ac17_plan_overview_uses_canonical_goal_not_h1_title(self) -> None:
        document = _render(_plan_bundle(), review_id="plan-review", locale="en", offline=False)

        self.assertIn(
            "<strong>Goal:</strong> Build a deterministic review source bundle.",
            document,
        )
        self.assertIn("<strong>Plan title:</strong> Demo implementation plan", document)
        self.assertNotIn("<strong>Goal:</strong> Demo implementation plan", document)

    def test_r22_overview_shows_only_source_owned_user_experience_with_provenance(self) -> None:
        without_section = _render(
            _plan_bundle(),
            review_id="plan-review",
            locale="en",
            offline=False,
        )
        self.assertNotIn("data-plan-user-experience", without_section)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(FIXTURE_ROOT, root, dirs_exist_ok=True)
            plan = root / "docs/plans/001-demo/plan.md"
            plan.write_text(
                plan.read_text(encoding="utf-8")
                + "\n## User Experience\n\nReviewers see source-owned context without inferred guidance.\n",
                encoding="utf-8",
            )
            bundle = collect_plan_sources(plan, root)
            document = _render(bundle, review_id="plan-review", locale="en", offline=False)

        overview = re.search(
            r'<section class="tab-panel" id="overview".*?>(.*?)</section>',
            document,
            re.DOTALL,
        )
        self.assertIsNotNone(overview)
        body = overview.group(1)
        self.assertIn('data-plan-user-experience="User Experience"', body)
        self.assertIn("Reviewers see source-owned context without inferred guidance.", body)
        self.assertIn("Plan source", body)
        self.assertIn("docs/plans/001-demo/plan.md", body)

    def test_r23_requirements_lists_every_explicit_route_scope(self) -> None:
        bundle = _plan_bundle()
        plan_source = bundle.primary[0]
        document = _render(bundle, review_id="plan-review", locale="en", offline=False)
        requirements = re.search(
            r'<section class="tab-panel" id="requirements".*?>(.*?)</section>',
            document,
            re.DOTALL,
        )
        self.assertIsNotNone(requirements)
        body = requirements.group(1)
        self.assertIn('data-route-scope-table', body)
        self.assertIn("Plan source", body)
        self.assertIn("docs/plans/001-demo/plan.md", body)
        plan_document = plan_source.document
        assert plan_document is not None
        for route in plan_document.routes:
            self.assertIn(f'data-route-scope="{route.id}"', body)
            self.assertIn(route.title, body)
            for task_id in route.task_ids:
                self.assertIn(
                    f'href="#{plan_source.namespace}-{task_id}"',
                    body,
                )
            for dependency in route.dependencies:
                self.assertIn(dependency, body)

    def test_r23_requirements_preserves_korean_constraint_and_policy_sections(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(FIXTURE_ROOT, root, dirs_exist_ok=True)
            plan = root / "docs/plans/001-demo/plan.md"
            plan.write_text(
                plan.read_text(encoding="utf-8")
                + "\n## 제약\n\n- 한국어 제약 원문.\n"
                + "\n## 정책\n\n- 한국어 정책 원문.\n",
                encoding="utf-8",
            )
            document = _render(
                collect_plan_sources(plan, root),
                review_id="plan-review",
                locale="ko",
                offline=False,
            )

        requirements = re.search(
            r'<section class="tab-panel" id="requirements".*?>(.*?)</section>',
            document,
            re.DOTALL,
        )
        self.assertIsNotNone(requirements)
        body = requirements.group(1)
        for heading, text in (("제약", "한국어 제약 원문."), ("정책", "한국어 정책 원문.")):
            self.assertIn(f'data-plan-governance-section="{heading}"', body)
            self.assertIn(text, body)
        self.assertGreaterEqual(body.count("Plan source"), 2)
        self.assertGreaterEqual(body.count("docs/plans/001-demo/plan.md"), 2)

    def test_r25_runtime_atlas_includes_all_bilingual_canonical_sections(self) -> None:
        sections = (
            ("Server Authority", "English server authority source."),
            ("Files", "English files source."),
            ("Remotes", "English remotes source."),
            ("Transactions", "English transactions source."),
            ("서버 권위", "한국어 서버 권위 원문."),
            ("파일", "한국어 파일 원문."),
            ("리모트", "한국어 리모트 원문."),
            ("트랜잭션", "한국어 트랜잭션 원문."),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(FIXTURE_ROOT, root, dirs_exist_ok=True)
            plan = root / "docs/plans/001-demo/plan.md"
            addition = "".join(f"\n## {heading}\n\n{text}\n" for heading, text in sections)
            addition += "\n## Profile\n\nUnrelated profile source.\n"
            plan.write_text(plan.read_text(encoding="utf-8") + addition, encoding="utf-8")
            document = _render(
                collect_plan_sources(plan, root),
                review_id="plan-review",
                locale="en",
                offline=False,
            )

        data = re.search(
            r'<section class="tab-panel" id="data".*?>(.*?)</section>\s*'
            r'<section class="tab-panel" id="acceptance"',
            document,
            re.DOTALL,
        )
        self.assertIsNotNone(data)
        body = data.group(1)
        for heading, text in sections:
            self.assertIn(f'data-runtime-section="{heading}"', body)
            self.assertIn(text, body)
        self.assertNotIn('data-runtime-section="Profile"', body)
        self.assertNotIn("Unrelated profile source.", body)
        self.assertIn("Plan source", body)
        self.assertIn("docs/plans/001-demo/plan.md", body)

    def test_r28_data_preserves_main_tasks_body_as_collapsed_source_detail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(FIXTURE_ROOT, root, dirs_exist_ok=True)
            plan = root / "docs/plans/001-demo/plan.md"
            plan.write_text(
                plan.read_text(encoding="utf-8").replace(
                    "- Route: source-model",
                    "- Route: source-model\n"
                    "- 파일: `scripts/source_model.py`\n"
                    "- Remote: `ReviewManifest`\n"
                    "- 트랜잭션: atomic replace\n"
                    "- Interface: `collect_sources()`",
                ),
                encoding="utf-8",
            )
            document = _render(
                collect_plan_sources(plan, root),
                review_id="plan-review",
                locale="ko",
                offline=False,
            )

        data = re.search(
            r'<section class="tab-panel" id="data".*?>(.*?)</section>\s*'
            r'<section class="tab-panel" id="acceptance"',
            document,
            re.DOTALL,
        )
        self.assertIsNotNone(data)
        body = data.group(1)
        detail = re.search(
            r'<details[^>]+data-main-task-detail="plan--001-demo:docs/plans/001-demo/plan.md"(?![^>]*\bopen)[^>]*>(.*?)</details>',
            body,
            re.DOTALL,
        )
        self.assertIsNotNone(detail)
        source = detail.group(1)
        for expected in (
            "scripts/source_model.py",
            "ReviewManifest",
            "atomic replace",
            "collect_sources()",
        ):
            self.assertIn(expected, source)
        self.assertIn("Plan source", source)
        self.assertIn("docs/plans/001-demo/plan.md", source)

    def test_r27_history_shows_read_only_source_status_and_main_auxiliary_checks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(FIXTURE_ROOT, root, dirs_exist_ok=True)
            plan = root / "docs/plans/001-demo/plan.md"
            plan.write_text(
                plan.read_text(encoding="utf-8").replace(
                    "- [ ] **Step 1: Read the primary source**",
                    "- [x] **Step 1: Read the primary source**",
                ),
                encoding="utf-8",
            )
            bundle = collect_plan_sources(plan, root)
            document = _render(bundle, review_id="plan-review", locale="en", offline=False)

        history = re.search(
            r'<section class="tab-panel" id="history".*?>(.*?)</section>',
            document,
            re.DOTALL,
        )
        self.assertIsNotNone(history)
        body = history.group(1)
        summary = re.search(
            r'<article[^>]+data-source-state-summary[^>]*>(.*?)</article>',
            body,
            re.DOTALL,
        )
        self.assertIsNotNone(summary)
        state = summary.group(1)
        self.assertIn("Source plan status", state)
        self.assertIn("active", state)
        self.assertIn("Task1-Step1", state)
        self.assertIn('data-source-check-state="checked"', state)
        self.assertIn("docs/plans/001-demo/plan.md", state)
        self.assertIn("Task2-Step1", state)
        self.assertIn('data-source-check-state="unchecked"', state)
        self.assertIn("docs/plans/001-demo/tasks/002-manifest.md", state)
        self.assertIn("Read-only source Markdown state", state)
        self.assertNotIn("<input", state)

    def test_ac5_coverage_links_actual_namespaced_steps(self) -> None:
        document = _render(_plan_bundle(), review_id="plan-review", locale="en", offline=False)
        match = re.search(
            r'<section class="signature-view" data-origin="Derived view"><h3>AC Coverage</h3>(.*?)</section>',
            document,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        coverage = match.group(1)
        for step_id in ("Task1-Step1", "Task1-Step2", "Task2-Step1"):
            self.assertIn(
                f'<a href="#plan--001-demo-{step_id}">{step_id}</a>',
                coverage,
            )
        self.assertNotRegex(coverage, r'<td>\s*[0-9]+\s*</td>')

    def test_ac12_unselected_context_relations_never_create_broken_links(self) -> None:
        bundle = _plan_bundle()
        acceptance_only = replace(
            bundle.context[0],
            requirements=(),
            acceptance=("AC1",),
        )
        restricted = replace(bundle, context=(acceptance_only, bundle.context[1]))
        document = _render(restricted, review_id="plan-review", locale="en", offline=False)
        parsed = _DocumentParser()
        parsed.feed(document)

        self.assertIn('id="context--008-alpha-AC1"', document)
        self.assertIn('data-relation-state="unselected"', document)
        for requirement in ("R1", "R2", "R3"):
            self.assertNotIn(f'href="#context--008-alpha-{requirement}"', document)
            self.assertIn(f"{requirement} (unselected)", document)
        internal_targets = {
            href.removeprefix("#")
            for href in parsed.hrefs
            if href.startswith("#")
        }
        self.assertEqual(internal_targets - parsed.ids, set())

    def test_ac5_r27_split_plan_detail_is_counted_and_disclosed_in_history(self) -> None:
        document = _render(_plan_bundle(), review_id="plan-review", locale="ko", offline=True)

        self.assertEqual(document.count('class="task-card"'), 2)
        self.assertEqual(document.count('data-kind="step"'), 3)
        self.assertIn('data-source-detail="progress--001-demo:docs/plans/001-demo/progress.md"', document)
        self.assertIn('data-source-detail="task--002-manifest:docs/plans/001-demo/tasks/002-manifest.md"', document)
        self.assertIn("source-model-ready", document)
        self.assertIn("Emit a normalized manifest", document)
        self.assertRegex(
            document,
            r'<details[^>]+data-source-detail="progress--001-demo:[^"]+"[^>]*>.*?Plan source.*?progress\.md',
        )

    def test_ac5_empty_context_selection_renders_zero_items(self) -> None:
        bundle = _plan_bundle()
        empty_context = replace(bundle.context[0], requirements=(), acceptance=())
        restricted = replace(bundle, context=(empty_context, bundle.context[1]))
        document = _render(restricted, review_id="plan-review", locale="en", offline=False)

        self.assertNotIn('id="context--008-alpha-R1"', document)
        self.assertNotIn('id="context--008-alpha-AC1"', document)
        self.assertIn('id="context--002-beta-R1"', document)
        self.assertIn('id="context--002-beta-AC6"', document)

    def test_ac18_history_visibly_contains_full_review_metadata(self) -> None:
        document = _render(_plan_bundle(), review_id="plan-review", locale="ko", offline=False)
        match = re.search(
            r'<section class="tab-panel" id="history".*?>(.*)</section>',
            document,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        history = match.group(1)
        self.assertIn('data-review-metadata', history)
        for expected in (
            "plan", "ko", "2026-08-01T00:00:00Z", "source-model-ready",
            "0123456789abcdef", "build-review-viewer.sh --mode plan --review-id demo",
            "primary / task", "primary / step", "context / 008-alpha / requirement",
        ):
            self.assertIn(expected, history)

    def test_r81_cli_aggregate_matches_browser_three_state_contract(self) -> None:
        self.assertEqual(_aggregate([]), "unverified")
        self.assertEqual(_aggregate(["current", "current"]), "current")
        self.assertEqual(_aggregate(["current", "missing"]), "unverified")
        self.assertEqual(_aggregate(["malformed", "current"]), "unverified")
        self.assertEqual(_aggregate(["missing", "stale", "malformed"]), "stale")

    def test_renderer_is_deterministic_for_identical_explicit_metadata(self) -> None:
        bundle = _plan_bundle()
        first = _render(bundle, review_id="plan-review", locale="ko", offline=True)
        second = _render(bundle, review_id="plan-review", locale="ko", offline=True)
        self.assertEqual(first, second)
        self.assertTrue(first.endswith("\n"))
        self.assertFalse(first.endswith("\n\n"))
        self.assertIsNone(re.search(r"/Users/|/home/|[A-Z]:\\", first))

    def test_shell_uses_declared_warm_graphite_cobalt_system(self) -> None:
        document = _render(_spec_bundle(), review_id="spec-review", locale="en", offline=False)
        self.assertIn("--bg: #f7f3eb", document)
        self.assertIn("--text: #20262b", document)
        self.assertIn("--accent: #2557a7", document)
        self.assertIn("fill='%232557a7'", document)

    def test_ac5_ac6_scale_fixture_has_exact_counts_and_eight_routes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(
                [sys.executable, str(TEST_DIR / "fixtures/generate-scale-fixture.py"), str(root)],
                check=True,
            )
            bundle = collect_plan_sources(root / "docs/plans/001-scale/plan.md", root)
            self.assertEqual(bundle.counts["primary"]["task"], 22)
            self.assertEqual(bundle.counts["primary"]["step"], 110)
            self.assertEqual(bundle.counts["context"]["001-scale"]["requirement"], 190)
            self.assertEqual(bundle.counts["context"]["001-scale"]["acceptance"], 105)
            document = _render(bundle, review_id="scale-review", locale="en", offline=False)

        self.assertEqual(document.count('class="task-card"'), 22)
        self.assertEqual(document.count('data-kind="step"'), 110)
        self.assertIn('id="context--001-scale-R190"', document)
        self.assertIn('id="context--001-scale-AC105"', document)
        for route in range(1, 9):
            self.assertIn(f'data-route="expedition-route-{route}"', document)
            self.assertIn(f'data-route-scope="expedition-route-{route}"', document)
        for task in range(1, 23):
            for step in range(1, 6):
                step_id = f"Task{task}-Step{step}"
                self.assertIn(
                    f'<a href="#plan--001-scale-{step_id}">{step_id}</a>',
                    document,
                )
        self.assertIn("Source-declared interaction", document)
        self.assertIn("Sends “open review” to Viewer", document)

    def test_authored_copy_does_not_mix_english_and_korean_locales(self) -> None:
        english = _render(_spec_bundle(), review_id="spec-review", locale="en", offline=False)
        korean = _render(_plan_bundle(), review_id="plan-review", locale="ko", offline=False)

        self.assertNotIn("관계와 provenance", english)
        self.assertNotIn("노드와 화살표", english)
        for english_heading in (
            "What outcome and execution scale should be reviewed?",
            "Which constraints and product context govern this plan?",
            "How do explicit Routes, dependencies, and source flows connect?",
            "Where are runtime and interface responsibilities declared?",
            "Which explicit trace and evidence should be reviewed?",
            "Which sources and checkpoints produced this snapshot?",
        ):
            self.assertNotIn(english_heading, korean)
        self.assertIn("어떤 목표와 실행 규모를 검토할까?", korean)
        self.assertIn("명시된 Route와 dependency, source flow는 어떻게 연결될까?", korean)


def build_spec_bundle_with_mermaid():
    return collect_spec_sources(
        primary=FIXTURE_ROOT / "docs" / "specs" / "008-alpha" / "spec.md",
        comparisons=(),
        repo_root=FIXTURE_ROOT,
    )


def build_spec_bundle_without_mermaid():
    bundle = build_spec_bundle_with_mermaid()
    primary = tuple(
        replace(source, document=replace(source.document, mermaid=()))
        if source.document is not None
        else source
        for source in bundle.primary
    )
    return replace(bundle, primary=primary)


def build_plan_bundle_with_governance_and_routes():
    return collect_plan_sources(
        plan=FIXTURE_ROOT / "docs" / "plans" / "001-demo" / "plan.md",
        repo_root=FIXTURE_ROOT,
    )


def _without_mermaid(source):
    if source.document is None:
        return source
    return replace(source, document=replace(source.document, mermaid=()))


def build_plan_bundle_without_routes_or_mermaid():
    bundle = build_plan_bundle_with_governance_and_routes()
    plan_source = bundle.primary[0]
    document = plan_source.document
    stripped_document = replace(document, routes=(), dependencies=(), mermaid=())
    primary = tuple(
        _without_mermaid(replace(source, document=stripped_document))
        if source is plan_source
        else _without_mermaid(source)
        for source in bundle.primary
    )
    context = tuple(_without_mermaid(source) for source in bundle.context)
    comparison = tuple(_without_mermaid(source) for source in bundle.comparison)
    return replace(bundle, primary=primary, comparison=comparison, context=context)


class ConditionalMermaidLoaderTest(unittest.TestCase):
    def test_offline_bundle_without_diagram_omits_runtime(self) -> None:
        bundle = build_spec_bundle_without_mermaid()
        self.assertFalse(review_renderer.bundle_needs_mermaid(bundle))
        self.assertEqual(review_renderer._mermaid_loader(True, bundle), "")

    def test_offline_bundle_with_diagram_embeds_runtime(self) -> None:
        bundle = build_spec_bundle_with_mermaid()
        self.assertTrue(review_renderer.bundle_needs_mermaid(bundle))
        self.assertIn(
            'data-mermaid-delivery="offline"',
            review_renderer._mermaid_loader(True, bundle),
        )

    def test_cdn_bundle_without_diagram_omits_loader(self) -> None:
        bundle = build_spec_bundle_without_mermaid()
        self.assertEqual(review_renderer._mermaid_loader(False, bundle), "")

    def test_plan_bundle_without_routes_or_mermaid_omits_runtime(self) -> None:
        bundle = build_plan_bundle_without_routes_or_mermaid()
        self.assertFalse(review_renderer.bundle_needs_mermaid(bundle))

    def test_plan_bundle_with_routes_needs_runtime_for_route_map(self) -> None:
        bundle = build_plan_bundle_with_governance_and_routes()
        self.assertTrue(review_renderer.bundle_needs_mermaid(bundle))


class OverviewMetricStripTest(unittest.TestCase):
    def test_strip_precedes_detail_table(self) -> None:
        bundle = build_spec_bundle_with_mermaid()
        labels = review_renderer.LABELS["en"]
        panels = review_renderer._spec_panels(bundle, "inspect", labels)
        strip_index = panels["overview"].index('class="metric-strip"')
        table_index = panels["overview"].index('class="count-table"')
        self.assertLess(strip_index, table_index)

    def test_strip_values_match_flattened_counts(self) -> None:
        bundle = build_spec_bundle_with_mermaid()
        markup = review_renderer._metric_strip(bundle)
        for _, value in review_renderer._count_rows(bundle.counts):
            self.assertIn(f">{value}<", markup)

    def test_detail_table_is_retained(self) -> None:
        bundle = build_spec_bundle_with_mermaid()
        labels = review_renderer.LABELS["en"]
        panels = review_renderer._spec_panels(bundle, "inspect", labels)
        self.assertIn('class="count-table"', panels["overview"])


if __name__ == "__main__":
    unittest.main()
