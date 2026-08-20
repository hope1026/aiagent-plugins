from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


TEST_DIR = Path(__file__).resolve().parent
REPO = TEST_DIR / "fixtures" / "repository"
SPEC_BUNDLE_FIXTURES = (
    TEST_DIR.parents[1] / "writing-specs" / "tests" / "fixtures" / "spec-bundle"
)
PLAN_BUNDLE_REPOSITORY = (
    TEST_DIR.parents[1]
    / "writing-specs"
    / "tests"
    / "fixtures"
    / "plan-bundle-repository"
)
SCRIPTS = TEST_DIR.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from review_sources import (  # noqa: E402
    collect_brief_sources,
    collect_plan_sources,
    collect_project_sources,
    collect_spec_sources,
    repository_relative,
    validate_view_id,
)
from review_freshness import find_repository_root  # noqa: E402


BUILDER = TEST_DIR.parent / "scripts" / "build-visual-docs.sh"


def repository_snapshot(root: Path) -> tuple[tuple[str, str], ...]:
    return tuple(
        (
            path.relative_to(root).as_posix(),
            hashlib.sha256(path.read_bytes()).hexdigest(),
        )
        for path in sorted(root.rglob("*"))
        if path.is_file() and ".git" not in path.relative_to(root).parts
    )


def initialize_git_repository(root: Path) -> None:
    commands = (
        ("init", "-q"),
        ("config", "user.name", "fixture"),
        ("config", "user.email", "fixture@example.invalid"),
        ("add", "."),
        ("commit", "-qm", "fixture"),
    )
    for arguments in commands:
        subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )


def run_builder(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(BUILDER), *arguments],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


class ReviewSourcesTest(unittest.TestCase):
    def test_brief_preserves_human_authored_orientation_sections(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".forge/work/demo").mkdir(parents=True)
            brief = root / ".forge/work/demo/brief.md"
            brief.write_text(
                """# Visual Docs rename

## Goal

Help people understand the project.

## Scope

- Brief View
- Project Handbook

## Out of Scope

- Automatic refresh

## Done Checks

- Four document kinds build successfully
""",
                encoding="utf-8",
            )

            bundle = collect_brief_sources(brief, root)

        self.assertEqual(bundle.kind, "brief")
        self.assertEqual([source.role for source in bundle.primary], ["brief_source"])
        document = bundle.primary[0].document
        assert document is not None
        self.assertEqual(document.title, "Visual Docs rename")
        self.assertEqual(document.goal, "Help people understand the project.")
        self.assertEqual(document.scope, ("Brief View", "Project Handbook"))
        self.assertEqual(document.out_of_scope, ("Automatic refresh",))
        self.assertEqual(document.done_checks, ("Four document kinds build successfully",))

    def test_project_collects_map_specs_and_repository_evidence_separately(self) -> None:
        bundle = collect_project_sources(
            REPO / "docs/project/project-map.md",
            REPO,
        )

        self.assertEqual(bundle.kind, "project")
        self.assertEqual([source.role for source in bundle.primary], ["project_map"])
        self.assertEqual(
            {source.role for source in bundle.context},
            {"declared_spec", "repository_evidence"},
        )
        project = bundle.primary[0].document
        assert project is not None
        self.assertEqual(
            project.structure[0].purpose,
            "사람이 읽는 프로젝트 문서를 보관한다.",
        )
        evidence = next(
            source.document
            for source in bundle.context
            if source.role == "repository_evidence"
        )
        assert evidence is not None
        self.assertIn("docs/plans/001-demo/plan.md", evidence.files)
        self.assertNotIn("docs/project/project-map.md", evidence.files)
        self.assertNotIn("Purpose", evidence.text)

    def test_project_rejects_dangling_structure_statement_link(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(REPO, root, dirs_exist_ok=True)
            project_map = root / "docs/project/project-map.md"
            project_map.write_text(
                project_map.read_text(encoding="utf-8").replace(
                    "#every-declared-member-enters-the-review-source-set-exactly-once)",
                    "#missing-statement)",
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ValueError,
                "docs/project/project-map.md:.*Governing Statements.*missing-statement",
            ):
                collect_project_sources(project_map, root)

    def test_five_member_bundle_preserves_member_and_bundle_provenance_once(self) -> None:
        bundle_path = SPEC_BUNDLE_FIXTURES / "valid-five-file"

        bundle = collect_spec_sources(bundle_path, (), SPEC_BUNDLE_FIXTURES)

        self.assertEqual(len(bundle.sources), 5)
        self.assertEqual(
            [source.path for source in bundle.primary],
            [
                "valid-five-file/multi-document-bundle.md",
                "valid-five-file/runtime-behavior.md",
                "valid-five-file/acceptance-outcomes.md",
                "valid-five-file/decisions-and-history.md",
                "valid-five-file/supporting-context.md",
            ],
        )
        self.assertEqual(len({source.path for source in bundle.primary}), 5)
        self.assertEqual(len({source.bundle_sha256 for source in bundle.primary}), 1)
        self.assertTrue(
            all(
                source.bundle_path == "valid-five-file"
                and source.member_title
                and source.member_role
                and source.sha256 == hashlib.sha256(source.source_bytes).hexdigest()
                for source in bundle.primary
            )
        )

    def test_unsupported_single_file_spec_is_not_a_review_source(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid structured Spec Bundle"):
            collect_spec_sources(
                TEST_DIR / "fixtures/unsupported-single-file.md",
                (),
                TEST_DIR / "fixtures",
            )

    def test_plan_collects_every_related_bundle_member_and_exact_statement_refs(self) -> None:
        bundle = collect_plan_sources(
            PLAN_BUNDLE_REPOSITORY
            / "docs/plans/semantic-migration/valid-plan.md",
            PLAN_BUNDLE_REPOSITORY,
        )

        document = bundle.primary[0].document
        assert document is not None
        self.assertEqual(
            [source.path for source in bundle.context],
            [
                "docs/specs/semantic-spec-bundles/semantic-spec-bundle-contract.md",
                "docs/specs/semantic-spec-bundles/bundle-validation-outcomes.md",
            ],
        )
        self.assertEqual(
            [reference.heading for reference in document.tasks[0].governing_statements],
            [
                "Each bundle has exactly one root document",
                "A bundle with one declared root passes structural validation",
            ],
        )

    def test_plan_document_preserves_canonical_goal_in_both_locales(self) -> None:
        english = collect_plan_sources(
            REPO / "docs/plans/001-demo/plan.md",
            REPO,
        ).primary[0].document
        assert english is not None
        self.assertEqual(
            english.goal,
            "Build a deterministic review source bundle.",
        )

        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(REPO, root, dirs_exist_ok=True)
            plan = root / "docs/plans/001-demo/plan.md"
            plan.write_text(
                plan.read_text(encoding="utf-8").replace(
                    "**Goal:** Build a deterministic review source bundle.",
                    "**목표:** 정본 목표 문장을 보존한다.",
                )
                + "\n```markdown\n**Goal:** 코드 예시는 목표가 아니다.\n```\n",
                encoding="utf-8",
            )
            korean = collect_plan_sources(plan, root).primary[0].document
            assert korean is not None
            self.assertEqual(korean.goal, "정본 목표 문장을 보존한다.")

    def test_auxiliary_documents_preserve_source_specific_mermaid_provenance(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(REPO, root, dirs_exist_ok=True)
            progress = root / "docs/plans/001-demo/progress.md"
            progress.write_text(
                progress.read_text(encoding="utf-8")
                + "\n```mermaid\nP[Progress] --> S[State]\n```\n",
                encoding="utf-8",
            )
            task = root / "docs/plans/001-demo/tasks/002-manifest.md"
            task.write_text(
                task.read_text(encoding="utf-8")
                + "\n```mermaid\nT[Task] --> M[Manifest]\n```\n",
                encoding="utf-8",
            )

            bundle = collect_plan_sources(root / "docs/plans/001-demo/plan.md", root)
            primary, progress_source, task_source = bundle.primary
            auxiliary = (progress_source.document, task_source.document)
            observed = (
                tuple(block.text for block in primary.document.mermaid),
                tuple(
                    (
                        type(document).__name__,
                        getattr(document, "path", None),
                        tuple(block.text for block in getattr(document, "mermaid", ())),
                        getattr(
                            getattr(type(document), "__dataclass_params__", None),
                            "frozen",
                            False,
                        ),
                    )
                    for document in auxiliary
                ),
                tuple(block.text for block in bundle.mermaid),
            )
            self.assertEqual(
                observed,
                (
                    ("flowchart LR\n    P[Plan] --> T[Tasks]",),
                    (
                        (
                            "PlanAuxiliaryDocument",
                            "docs/plans/001-demo/progress.md",
                            ("P[Progress] --> S[State]",),
                            True,
                        ),
                        (
                            "PlanAuxiliaryDocument",
                            "docs/plans/001-demo/tasks/002-manifest.md",
                            ("T[Task] --> M[Manifest]",),
                            True,
                        ),
                    ),
                    (
                        "flowchart LR\n    P[Plan] --> T[Tasks]",
                        "P[Progress] --> S[State]",
                        "T[Task] --> M[Manifest]",
                        "flowchart LR\n    A[Source] --> B[Bundle]",
                    ),
                ),
            )

    def test_outer_markdown_fences_hide_literal_mermaid_examples(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(REPO, root, dirs_exist_ok=True)
            plan = root / "docs/plans/001-demo/plan.md"
            plan.write_text(
                plan.read_text(encoding="utf-8")
                + """

````text
```mermaid
SHOULD_NOT --> COUNT_BACKTICK
```
````

~~~~text
```mermaid
SHOULD_NOT --> COUNT_TILDE
```
~~~~
""",
                encoding="utf-8",
            )
            bundle = collect_plan_sources(plan, root)
            document = bundle.primary[0].document
            assert document is not None
            self.assertEqual(
                tuple(block.text for block in document.mermaid),
                ("flowchart LR\n    P[Plan] --> T[Tasks]",),
            )

    def test_duplicate_related_bundle_fails_source_collection(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(REPO, root, dirs_exist_ok=True)
            plan = root / "docs/plans/001-demo/plan.md"
            plan.write_text(
                plan.read_text(encoding="utf-8").replace(
                    "- bundle: docs/specs/supporting-policy/",
                    "- bundle: docs/specs/semantic-spec-bundles/",
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicated"):
                collect_plan_sources(plan, root)

    def test_resolved_plan_source_aliases_fail_public_and_cli_collection(self) -> None:
        results: list[tuple[str | None, int, bool]] = []
        for role in ("progress", "task"):
            with TemporaryDirectory() as temporary:
                root = Path(temporary)
                shutil.copytree(REPO, root, dirs_exist_ok=True)
                plan = root / "docs/plans/001-demo/plan.md"
                if role == "progress":
                    progress = plan.parent / "progress.md"
                    progress.unlink()
                    progress.symlink_to("plan.md")
                else:
                    (plan.parent / "tasks/003-alias.md").symlink_to("../plan.md")
                try:
                    collect_plan_sources(plan, root)
                except ValueError as error:
                    public_error = str(error)
                else:
                    public_error = None
                initialize_git_repository(root)
                before = repository_snapshot(root)
                result = run_builder(
                    root,
                    "--kind",
                    "plan",
                    "--plan",
                    "docs/plans/001-demo/plan.md",
                    "--view-id",
                    "source-alias",
                    "--generated-at",
                    "2026-08-01T00:00:00Z",
                    "--dry-run",
                    "--format",
                    "json",
                )
                results.append((public_error, result.returncode, before == repository_snapshot(root)))
        self.assertEqual(
            tuple((error is not None and "alias" in error, code, unchanged) for error, code, unchanged in results),
            ((True, 2, True), (True, 2, True)),
        )

    def test_spec_primary_and_comparison_are_namespaced(self) -> None:
        bundle = collect_spec_sources(
            REPO / "docs/specs/semantic-spec-bundles",
            [REPO / "docs/specs/supporting-policy"],
            REPO,
        )

        self.assertEqual(bundle.kind, "spec")
        self.assertEqual(len(bundle.primary), 5)
        self.assertEqual({source.role for source in bundle.primary}, {"primary_spec"})
        self.assertEqual({source.role for source in bundle.comparison}, {"comparison_spec"})
        self.assertNotEqual(bundle.primary[0].namespace, bundle.comparison[0].namespace)
        self.assertEqual(
            bundle.primary[0].path,
            "docs/specs/semantic-spec-bundles/semantic-spec-bundle-contract.md",
        )
        self.assertEqual(bundle.counts["primary"]["requirement"], 1)
        self.assertEqual(
            bundle.counts["comparison"]["docs/specs/supporting-policy"]["acceptance"],
            1,
        )

    def test_plan_primary_auxiliary_and_context_are_separate(self) -> None:
        bundle = collect_plan_sources(REPO / "docs/plans/001-demo/plan.md", REPO)

        self.assertEqual(
            [source.role for source in bundle.primary],
            ["primary_plan", "plan_progress", "plan_task"],
        )
        self.assertEqual(
            [source.role for source in bundle.context],
            ["related_spec_context"] * 7,
        )
        self.assertEqual(bundle.counts["primary"]["task"], 2)
        self.assertEqual(bundle.counts["primary"]["step"], 3)
        self.assertEqual(
            bundle.counts["context"]["docs/specs/semantic-spec-bundles"]["requirement"],
            1,
        )
        self.assertEqual(
            bundle.counts["context"]["docs/specs/supporting-policy"]["acceptance"],
            1,
        )

        document = bundle.primary[0].document
        self.assertIsNotNone(document)
        assert document is not None
        self.assertEqual(
            [item.heading for item in document.tasks[0].governing_statements],
            [
                "Every declared member enters the review source set exactly once",
                "Repository-contained review inputs load successfully",
                "Requirement-only policy remains directly traceable",
            ],
        )
        self.assertEqual(
            [(item.from_task, item.to_task) for item in document.dependencies],
            [("Task1", "Task2")],
        )
        self.assertEqual(
            [(route.id, route.dependencies, route.task_ids) for route in document.routes],
            [
                ("source-model", (), ("Task1",)),
                ("cli", ("source-model",), ("Task2",)),
            ],
        )
        self.assertEqual(
            [(item.id, item.command, item.expected) for item in document.verification],
            [
                ("Task1-V1", "python3 tests/test_review_sources.py", "source collection succeeds"),
                ("Task2-V1", "bash tests/test-build-visual-docs.sh", "dry-run writes no files"),
            ],
        )

    def test_statement_trace_and_dependency_errors_fail_closed(self) -> None:
        plan = (REPO / "docs/plans/001-demo/plan.md").read_text(encoding="utf-8")
        task = (
            REPO / "docs/plans/001-demo/tasks/002-manifest.md"
        ).read_text(encoding="utf-8")
        cases = {
            "wrong heading": plan.replace(
                "Every declared member enters the review source set exactly once",
                "A missing statement heading",
                1,
            ),
            "wrong anchor": plan.replace(
                "#every-declared-member-enters-the-review-source-set-exactly-once)",
                "#wrong-anchor)",
                1,
            ),
            "missing dependency": task.replace("Tasks 1–1", "Task 9"),
            "self dependency": task.replace("Tasks 1–1", "Task 2"),
            "cycle": plan.replace("- Dependencies: none", "- Dependencies: Task 2"),
        }
        for name, replacement in cases.items():
            with self.subTest(name=name), TemporaryDirectory() as temporary:
                root = Path(temporary)
                shutil.copytree(REPO, root, dirs_exist_ok=True)
                target = root / "docs/plans/001-demo/plan.md"
                fragment = root / "docs/plans/001-demo/tasks/002-manifest.md"
                if name in {"wrong heading", "wrong anchor", "cycle"}:
                    target.write_text(replacement, encoding="utf-8")
                else:
                    fragment.write_text(replacement, encoding="utf-8")
                with self.assertRaises(ValueError):
                    collect_plan_sources(target, root)

    def test_dependency_grammar_and_historical_task_are_preserved(self) -> None:
        task_three = """\
### Task 3: Historical record

Governing statements:

- [Every declared member enters the review source set exactly once](../../specs/semantic-spec-bundles/member-loading-and-provenance.md#every-declared-member-enters-the-review-source-set-exactly-once)

- Dependencies: Tasks 1–2; both canonical tasks are prerequisites

```text
## This fenced heading is not a plan section
Run: this fenced example is not evidence
Expected: this fenced example is ignored
```
"""
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(REPO, root, dirs_exist_ok=True)
            plan_path = root / "docs/plans/001-demo/plan.md"
            plan_path.write_text(
                plan_path.read_text(encoding="utf-8") + "\n" + task_three,
                encoding="utf-8",
            )
            bundle = collect_plan_sources(plan_path, root)
            document = bundle.primary[0].document
            assert document is not None
            historical = next(item for item in document.tasks if item.id == "Task3")
            self.assertIsNone(historical.route)
            self.assertNotIn("This fenced heading is not a plan section", document.sections)
            self.assertEqual(
                [
                    (item.from_task, item.to_task, item.reason)
                    for item in document.dependencies
                    if item.to_task == "Task3"
                ],
                [
                    ("Task1", "Task3", "both canonical tasks are prerequisites"),
                    ("Task2", "Task3", "both canonical tasks are prerequisites"),
                ],
            )
            self.assertEqual(
                [item.id for item in document.verification],
                ["Task1-V1", "Task2-V1"],
            )

            cases = (
                "- Dependencies: Task 1, Task 2; English reason",
                "- 의존성: Task 1, Task 2; 한국어 reason",
            )
            for metadata in cases:
                with self.subTest(metadata=metadata):
                    changed = plan_path.read_text(encoding="utf-8").replace(
                        "- Dependencies: Tasks 1–2; both canonical tasks are prerequisites",
                        metadata,
                    )
                    plan_path.write_text(changed, encoding="utf-8")
                    parsed = collect_plan_sources(plan_path, root)
                    parsed_document = parsed.primary[0].document
                    assert parsed_document is not None
                    self.assertEqual(
                        [item.from_task for item in parsed_document.dependencies if item.to_task == "Task3"],
                        ["Task1", "Task2"],
                    )
                    plan_path.write_text(
                        changed.replace(
                            metadata,
                            "- Dependencies: Tasks 1–2; both canonical tasks are prerequisites",
                        ),
                        encoding="utf-8",
                    )

            plan_text = plan_path.read_text(encoding="utf-8").replace(
                "- Dependencies: none", "- 의존성: 없음"
            )
            plan_path.write_text(plan_text, encoding="utf-8")
            parsed = collect_plan_sources(plan_path, root)
            parsed_document = parsed.primary[0].document
            assert parsed_document is not None
            self.assertFalse(
                [item for item in parsed_document.dependencies if item.to_task == "Task1"]
            )

    def test_plan_sibling_tasks_are_collected_in_lexical_path_order(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(REPO, root, dirs_exist_ok=True)
            first = root / "docs/plans/001-demo/tasks/001-first.md"
            first.write_text(
                """### Task 4: Lexically first source

- Route: source-model
- Dependencies: none
""",
                encoding="utf-8",
            )
            bundle = collect_plan_sources(root / "docs/plans/001-demo/plan.md", root)
            self.assertEqual(
                [source.path for source in bundle.primary if source.role == "plan_task"],
                [
                    "docs/plans/001-demo/tasks/001-first.md",
                    "docs/plans/001-demo/tasks/002-manifest.md",
                ],
            )

    def test_review_id_and_repository_containment(self) -> None:
        self.assertEqual(validate_view_id("view-1"), "view-1")
        for invalid in ("../escape", "UPPER", "-leading", "a" * 65):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "view-id"):
                validate_view_id(invalid)
        with self.assertRaisesRegex(ValueError, "repository"):
            repository_relative(REPO / "../outside.md", REPO)

        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            outside = root.parent / f"{root.name}-outside.md"
            outside.write_text("outside", encoding="utf-8")
            try:
                link = root / "link.md"
                link.symlink_to(outside)
                with self.assertRaisesRegex(ValueError, "repository"):
                    repository_relative(link, root)
            finally:
                outside.unlink(missing_ok=True)

        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
            nested = root / "nested/work"
            nested.mkdir(parents=True)
            self.assertEqual(find_repository_root(nested), root.resolve())

    def test_shared_parser_imports_from_exact_sibling_in_three_layouts(self) -> None:
        layouts = (
            Path("repo/plugins/forge/skills"),
            Path("home/.agents/skills"),
            Path("home/.claude/skills/forge/skills"),
        )
        writing_scripts = (
            TEST_DIR.parents[1] / "writing-specs" / "scripts"
        )
        for layout in layouts:
            with self.subTest(layout=layout.as_posix()), TemporaryDirectory() as temporary:
                skills = Path(temporary) / layout
                review_scripts = skills / "visual-docs/scripts"
                sibling_scripts = skills / "writing-specs/scripts"
                review_scripts.mkdir(parents=True)
                sibling_scripts.mkdir(parents=True)
                shutil.copy2(SCRIPTS / "review_sources.py", review_scripts)
                shutil.copy2(SCRIPTS / "project_map.py", review_scripts)
                for name in (
                    "spec_model.py",
                    "spec_transitions.py",
                    "spec_validate.py",
                ):
                    shutil.copy2(writing_scripts / name, sibling_scripts)
                command = (
                    "import pathlib, review_sources, spec_model; "
                    "print(pathlib.Path(spec_model.__file__).resolve())"
                )
                environment = dict(os.environ)
                environment.pop("PYTHONPATH", None)
                result = subprocess.run(
                    [sys.executable, "-c", command],
                    cwd=review_scripts,
                    env=environment,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    Path(result.stdout.strip()),
                    (sibling_scripts / "spec_model.py").resolve(),
                )


if __name__ == "__main__":
    unittest.main()
