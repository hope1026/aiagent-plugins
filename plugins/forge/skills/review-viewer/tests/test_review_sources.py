from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


TEST_DIR = Path(__file__).resolve().parent
REPO = TEST_DIR / "fixtures" / "repository"
SCRIPTS = TEST_DIR.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from review_sources import (  # noqa: E402
    collect_plan_sources,
    collect_spec_sources,
    repository_relative,
    validate_review_id,
)
from review_freshness import find_repository_root  # noqa: E402
from review_freshness import check_review  # noqa: E402


BUILDER = TEST_DIR.parent / "scripts" / "build-review-viewer.sh"


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


def write_viewer(path: Path, manifest: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '<script type="application/json" id="forge-source-manifest">'
        + json.dumps(manifest, sort_keys=True)
        + "</script>\n",
        encoding="utf-8",
    )


class ReviewSourcesTest(unittest.TestCase):
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

    def test_duplicate_related_spec_selections_fail_public_and_cli_collection(self) -> None:
        results: list[tuple[str | None, int, bool]] = []
        replacements = (
            ("requirements: [R1]", "requirements: [R1, R1]"),
            ("acceptance: [AC4, AC6]", "acceptance: [AC4, AC4]"),
        )
        for old, new in replacements:
            with TemporaryDirectory() as temporary:
                root = Path(temporary)
                shutil.copytree(REPO, root, dirs_exist_ok=True)
                plan = root / "docs/plans/001-demo/plan.md"
                plan.write_text(
                    plan.read_text(encoding="utf-8").replace(old, new),
                    encoding="utf-8",
                )
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
                    "--mode",
                    "plan",
                    "--plan",
                    "docs/plans/001-demo/plan.md",
                    "--review-id",
                    "duplicate-selection",
                    "--generated-at",
                    "2026-08-01T00:00:00Z",
                    "--dry-run",
                    "--format",
                    "json",
                )
                results.append((public_error, result.returncode, before == repository_snapshot(root)))
        self.assertEqual(
            tuple((error is not None and "duplicate" in error, code, unchanged) for error, code, unchanged in results),
            ((True, 2, True), (True, 2, True)),
        )

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
                    "--mode",
                    "plan",
                    "--plan",
                    "docs/plans/001-demo/plan.md",
                    "--review-id",
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

    def test_checker_rejects_wrong_path_shape_and_mode_cardinality_read_only(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(REPO, root, dirs_exist_ok=True)
            initialize_git_repository(root)
            alpha = root / "docs/specs/008-alpha/spec.md"
            beta = root / "docs/specs/002-beta/spec.md"

            def source(role: str, path: Path, namespace: str) -> dict[str, object]:
                return {
                    "role": role,
                    "path": path.relative_to(root).as_posix(),
                    "namespace": namespace,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "requirements": ["R1"],
                    "acceptance": ["AC1"],
                }

            primary = source("primary_spec", alpha, "current--008-alpha")
            manifest: dict[str, object] = {
                "review_id": "checker",
                "mode": "spec",
                "locale": "en",
                "generated_at": "2026-08-01T00:00:00Z",
                "checkpoint": "working-tree",
                "commit": "fixture",
                "rebuild_command": "build-review-viewer.sh --mode spec",
                "source_base": "../../../",
                "offline": False,
                "counts": {
                    "primary": {"requirement": 3},
                    "comparison": {},
                    "context": {},
                },
                "freshness": "unverified",
                "sources": [primary],
            }
            fixed = root / ".forge/reviews/checker/view.html"
            write_viewer(fixed, manifest)
            valid_state = check_review(fixed, root).overall

            invalid_states: list[str] = []
            wrong_path = root / "docs/specs/008-alpha/view.html"
            write_viewer(wrong_path, manifest)
            invalid_states.append(check_review(wrong_path, root).overall)

            cases: list[dict[str, object]] = []
            mismatch = dict(manifest)
            mismatch["review_id"] = "different"
            cases.append(mismatch)
            invalid_mode = dict(manifest)
            invalid_mode["mode"] = 7
            cases.append(invalid_mode)
            cases.append({"sources": [primary]})
            comparison_only = dict(manifest)
            comparison_only["sources"] = [
                source("comparison_spec", alpha, "comparison-1--008-alpha")
            ]
            cases.append(comparison_only)
            missing_arrays = dict(manifest)
            missing_arrays["sources"] = [
                {key: value for key, value in primary.items() if key != "acceptance"}
            ]
            cases.append(missing_arrays)
            plan_duplicate = dict(manifest)
            plan_duplicate["mode"] = "plan"
            plan_duplicate["sources"] = [
                source("primary_plan", alpha, "plan--one"),
                source("primary_plan", beta, "plan--two"),
            ]
            cases.append(plan_duplicate)
            for case in cases:
                write_viewer(fixed, case)
                invalid_states.append(check_review(fixed, root).overall)

            plan_manifest = dict(manifest)
            plan_manifest["review_id"] = "plan-checker"
            plan_manifest["mode"] = "plan"
            plan_rows = [
                source(
                    "primary_plan",
                    root / "docs/plans/001-demo/plan.md",
                    "plan--001-demo",
                ),
                source(
                    "plan_progress",
                    root / "docs/plans/001-demo/progress.md",
                    "progress--001-demo",
                ),
                source(
                    "plan_task",
                    root / "docs/plans/001-demo/tasks/002-manifest.md",
                    "task--002-manifest",
                ),
                source("related_spec_context", alpha, "context--008-alpha"),
                source("related_spec_context", beta, "context--002-beta"),
            ]
            for row in plan_rows[:3]:
                row["requirements"] = []
                row["acceptance"] = []
            plan_manifest["sources"] = plan_rows
            plan_viewer = root / ".forge/reviews/plan-checker/view.html"
            write_viewer(plan_viewer, plan_manifest)
            valid_plan_state = check_review(plan_viewer, root).overall

            before = repository_snapshot(root)
            cli = run_builder(
                root,
                "--check",
                ".forge/reviews/checker/view.html",
                "--repo-root",
                str(root),
                "--format",
                "json",
            )
            self.assertEqual(
                (
                    valid_state,
                    valid_plan_state,
                    tuple(invalid_states),
                    cli.returncode,
                    before == repository_snapshot(root),
                ),
                (
                    "current",
                    "current",
                    ("malformed",) * 7,
                    1,
                    True,
                ),
            )

    def test_spec_primary_and_comparison_are_namespaced(self) -> None:
        bundle = collect_spec_sources(
            REPO / "docs/specs/008-alpha/spec.md",
            [REPO / "docs/specs/002-beta/spec.md"],
            REPO,
        )

        self.assertEqual(bundle.mode, "spec")
        self.assertEqual([source.role for source in bundle.primary], ["primary_spec"])
        self.assertEqual(
            [source.role for source in bundle.comparison], ["comparison_spec"]
        )
        self.assertNotEqual(bundle.primary[0].namespace, bundle.comparison[0].namespace)
        self.assertEqual(bundle.primary[0].path, "docs/specs/008-alpha/spec.md")
        self.assertEqual(bundle.counts["primary"]["requirement"], 3)
        self.assertEqual(bundle.counts["comparison"]["002-beta"]["acceptance"], 6)

    def test_plan_primary_auxiliary_and_context_are_separate(self) -> None:
        bundle = collect_plan_sources(REPO / "docs/plans/001-demo/plan.md", REPO)

        self.assertEqual(
            [source.role for source in bundle.primary],
            ["primary_plan", "plan_progress", "plan_task"],
        )
        self.assertEqual(
            [source.role for source in bundle.context],
            ["related_spec_context", "related_spec_context"],
        )
        self.assertEqual(bundle.counts["primary"]["task"], 2)
        self.assertEqual(bundle.counts["primary"]["step"], 3)
        self.assertEqual(bundle.counts["context"]["008-alpha"]["requirement"], 3)
        self.assertEqual(bundle.counts["context"]["002-beta"]["acceptance"], 2)

        document = bundle.primary[0].document
        self.assertIsNotNone(document)
        assert document is not None
        self.assertEqual(
            document.tasks[0].requirements,
            tuple(type(document.tasks[0].requirements[0])("008-alpha", f"R{number}") for number in range(1, 4)),
        )
        self.assertEqual(
            document.tasks[0].acceptance,
            (
                type(document.tasks[0].acceptance[0])("002-beta", "AC4"),
                type(document.tasks[0].acceptance[0])("002-beta", "AC6"),
            ),
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
                ("Task2-V1", "bash tests/test-build-review-viewer.sh", "dry-run writes no files"),
            ],
        )

    def test_trace_and_dependency_errors_fail_closed(self) -> None:
        plan = (REPO / "docs/plans/001-demo/plan.md").read_text(encoding="utf-8")
        task = (
            REPO / "docs/plans/001-demo/tasks/002-manifest.md"
        ).read_text(encoding="utf-8")
        cases = {
            "unknown prefix": plan.replace("008 R1–R3", "999 R1–R3"),
            "descending range": plan.replace("008 R1–R3", "008 R3–R1"),
            "mixed range": plan.replace("008 R1–R3", "008 R1–AC3"),
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
                if name in {"unknown prefix", "descending range", "mixed range", "cycle"}:
                    target.write_text(replacement, encoding="utf-8")
                else:
                    fragment.write_text(replacement, encoding="utf-8")
                with self.assertRaises(ValueError):
                    collect_plan_sources(target, root)

    def test_dependency_grammar_and_historical_task_are_preserved(self) -> None:
        task_three = """\
### Task 3: Historical record (008 R1 · 002 AC4)

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
                """### Task 4: Lexically first source (008 R1)

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
        self.assertEqual(validate_review_id("review-1"), "review-1")
        for invalid in ("../escape", "UPPER", "-leading", "a" * 65):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "review-id"):
                validate_review_id(invalid)
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
                review_scripts = skills / "review-viewer/scripts"
                sibling_scripts = skills / "writing-specs/scripts"
                review_scripts.mkdir(parents=True)
                sibling_scripts.mkdir(parents=True)
                shutil.copy2(SCRIPTS / "review_sources.py", review_scripts)
                for name in ("spec_model.py", "spec_validate.py"):
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
