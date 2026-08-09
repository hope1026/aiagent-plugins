from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


TEST_DIR = Path(__file__).resolve().parent
SCRIPT_DIR = TEST_DIR.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from spec_validate import validate_repository  # noqa: E402


FIXTURE_REPOSITORY = (
    TEST_DIR / "fixtures/spec-bundle-repository/valid-multi-bundle"
)
SEMANTIC_ROOT = Path("docs/specs/semantic-workflows/workflow-contract.md")
CONTAINMENT_MEMBER = Path(
    "docs/specs/semantic-workflows/bundle-containment-rules.md"
)
OUTCOMES_MEMBER = Path(
    "docs/specs/semantic-workflows/repository-validation-outcomes.md"
)
HISTORY_MEMBER = Path(
    "docs/specs/semantic-workflows/semantic-workflow-decisions.md"
)
REVIEW_ROOT = Path("docs/specs/review-lifecycle/review-lifecycle-contract.md")


class SpecBundleRepositoryValidationTest(unittest.TestCase):
    def _repository(self) -> tuple[TemporaryDirectory[str], Path]:
        temporary = TemporaryDirectory()
        repository = Path(temporary.name) / "repo"
        shutil.copytree(FIXTURE_REPOSITORY, repository)
        return temporary, repository

    def _replace(self, repository: Path, path: Path, old: str, new: str) -> None:
        source = repository / path
        text = source.read_text(encoding="utf-8")
        self.assertIn(old, text)
        source.write_text(text.replace(old, new), encoding="utf-8")

    def _codes(self, repository: Path) -> set[str]:
        return {
            diagnostic.code
            for diagnostic in validate_repository(
                repository, Path("docs/specs")
            ).diagnostics
        }

    def _assert_mutation_code(self, code: str, mutation) -> None:
        temporary, repository = self._repository()
        with temporary:
            mutation(repository)
            self.assertIn(code, self._codes(repository))

    def test_path_transition_authorizes_exact_v3_bundle_replacement(self) -> None:
        temporary, repository = self._repository()
        with temporary:
            baseline_result = validate_repository(repository)
            source_bundle = next(
                bundle
                for bundle in baseline_result.bundles
                if bundle.path == Path("docs/specs/semantic-workflows")
            )
            subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
            subprocess.run(["git", "add", "."], cwd=repository, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Forge Test",
                    "-c",
                    "user.email=forge@example.invalid",
                    "commit",
                    "-qm",
                    "v3 baseline",
                ],
                cwd=repository,
                check=True,
            )
            old_bundle = repository / "docs/specs/semantic-workflows"
            new_bundle = repository / "docs/specs/replacement-workflows"
            old_bundle.rename(new_bundle)
            evidence = repository / "docs/evidence/bundle-replacement.md"
            evidence.parent.mkdir(parents=True)
            evidence.write_text("Replacement evidence.\n", encoding="utf-8")
            manifest = {
                "schema": "forge/spec-bundle-transitions@1",
                "transitions": [
                    {
                        "fromSourcePath": "docs/specs/semantic-workflows",
                        "fromSourceSha256": source_bundle.bundle_sha256,
                        "disposition": "superseded",
                        "toBundlePath": "docs/specs/replacement-workflows",
                        "evidencePath": "docs/evidence/bundle-replacement.md",
                        "reason": "Replace the current bundle with a newly named contract boundary.",
                    }
                ],
            }
            (repository / "docs/specs/.bundle-transitions.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )

            result = validate_repository(repository, baseline_ref="HEAD")

            self.assertTrue(result.ok, result.diagnostics)

    def test_approved_v3_history_may_replace_baseline_entries_with_current_facts(self) -> None:
        temporary, repository = self._repository()
        with temporary:
            subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
            subprocess.run(["git", "add", "."], cwd=repository, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Forge Test",
                    "-c",
                    "user.email=forge@example.invalid",
                    "commit",
                    "-qm",
                    "approved v3 baseline",
                ],
                cwd=repository,
                check=True,
            )
            history = repository / HISTORY_MEMBER
            history.write_text(
                "# Semantic Workflow Decisions\n\n"
                "## Decisions & History\n\n"
                "- 2026-08-09 [CURRENT] The active contract uses semantic bundle paths "
                "and full statements.\n",
                encoding="utf-8",
            )

            result = validate_repository(repository, baseline_ref="HEAD")

            self.assertTrue(result.ok, result.diagnostics)
            self.assertNotIn(
                "Repository discovery uses semantic bundle paths and full statements.",
                history.read_text(encoding="utf-8"),
            )

    def test_transition_prefix_and_retired_bundle_cannot_be_rewritten(self) -> None:
        temporary, repository = self._repository()
        with temporary:
            evidence = repository / "docs/evidence/historical-transition.md"
            evidence.parent.mkdir(parents=True)
            evidence.write_text("Historical evidence.\n", encoding="utf-8")
            record = {
                "fromSourcePath": "docs/specs/retired-workflows",
                "fromSourceSha256": "a" * 64,
                "disposition": "superseded",
                "toBundlePath": "docs/specs/semantic-workflows",
                "evidencePath": "docs/evidence/historical-transition.md",
                "reason": "The prior bundle was superseded by the current workflow contract.",
            }
            manifest_path = repository / "docs/specs/.bundle-transitions.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema": "forge/spec-bundle-transitions@1",
                        "transitions": [record],
                    }
                ),
                encoding="utf-8",
            )
            subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
            subprocess.run(["git", "add", "."], cwd=repository, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Forge Test",
                    "-c",
                    "user.email=forge@example.invalid",
                    "commit",
                    "-qm",
                    "historical transition baseline",
                ],
                cwd=repository,
                check=True,
            )
            record["reason"] = "The append-only record was rewritten."
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema": "forge/spec-bundle-transitions@1",
                        "transitions": [record],
                    }
                ),
                encoding="utf-8",
            )
            resurrected = repository / "docs/specs/retired-workflows"
            resurrected.mkdir(parents=True)

            result = validate_repository(repository, baseline_ref="HEAD")
            codes = {item.code for item in result.diagnostics}

            self.assertIn("SPEC_TRANSITION_BASELINE_PREFIX", codes)
            self.assertIn("SPEC_TRANSITION_OLD_SOURCE", codes)

    def test_approved_bundle_removal_requires_a_path_transition(self) -> None:
        temporary, repository = self._repository()
        with temporary:
            subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
            subprocess.run(["git", "add", "."], cwd=repository, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Forge Test",
                    "-c",
                    "user.email=forge@example.invalid",
                    "commit",
                    "-qm",
                    "approved v3 baseline",
                ],
                cwd=repository,
                check=True,
            )
            shutil.rmtree(repository / "docs/specs/semantic-workflows")

            result = validate_repository(repository, baseline_ref="HEAD")
            codes = {item.code for item in result.diagnostics}

            self.assertIn("SPEC_TRANSITION_REQUIRED", codes)

    def test_discovers_direct_child_semantic_bundles_in_lexical_order(self) -> None:
        result = validate_repository(FIXTURE_REPOSITORY, Path("docs/specs"))
        bundles = result.bundles

        self.assertTrue(result.ok, result.diagnostics)
        self.assertEqual(
            [bundle.path.as_posix() for bundle in bundles],
            [
                "docs/specs/review-lifecycle",
                "docs/specs/semantic-workflows",
            ],
        )
        self.assertNotIn(
            "docs/specs/README.md",
            [bundle.path.as_posix() for bundle in bundles],
        )

    def test_bundle_root_and_inventory_failure_matrix(self) -> None:
        def duplicate_root(repository: Path) -> None:
            source = (repository / REVIEW_ROOT).read_text(encoding="utf-8")
            (repository / "docs/specs/review-lifecycle/alternate-review-contract.md").write_text(
                source.replace("# Review Lifecycle Contract", "# Alternate Review Contract"),
                encoding="utf-8",
            )

        def undeclared_member(repository: Path) -> None:
            (repository / "docs/specs/semantic-workflows/extra-context.md").write_text(
                "# Extra Context\n", encoding="utf-8"
            )

        def missing_member(repository: Path) -> None:
            (repository / CONTAINMENT_MEMBER).unlink()

        def duplicate_inventory(repository: Path) -> None:
            line = "- contract: [Bundle Containment Rules](bundle-containment-rules.md)"
            self._replace(repository, SEMANTIC_ROOT, line, f"{line}\n{line}")

        def wrong_root_role(repository: Path) -> None:
            self._replace(
                repository,
                SEMANTIC_ROOT,
                "- root: [Semantic Workflow Contract](workflow-contract.md)",
                "- contract: [Semantic Workflow Contract](workflow-contract.md)",
            )

        def member_frontmatter(repository: Path) -> None:
            source = repository / CONTAINMENT_MEMBER
            source.write_text(
                "---\nschema: forge/spec@3\nrole: contract\n---\n" + source.read_text(),
                encoding="utf-8",
            )

        cases = (
            ("BUNDLE_ROOT_COUNT", duplicate_root),
            ("BUNDLE_MEMBER_UNDECLARED", undeclared_member),
            ("BUNDLE_MEMBER_MISSING", missing_member),
            ("BUNDLE_MEMBER_DUPLICATE", duplicate_inventory),
            ("BUNDLE_ROOT_INVENTORY_ROLE", wrong_root_role),
            ("BUNDLE_MEMBER_FRONTMATTER", member_frontmatter),
        )
        for code, mutation in cases:
            with self.subTest(code=code):
                self._assert_mutation_code(code, mutation)

    def test_semantic_directory_and_filename_failure_matrix(self) -> None:
        def rename_bundle(repository: Path, name: str) -> None:
            source = repository / "docs/specs/semantic-workflows"
            source.rename(source.with_name(name))

        def rename_member(repository: Path, name: str) -> None:
            old_name = CONTAINMENT_MEMBER.name
            source = repository / CONTAINMENT_MEMBER
            source.rename(source.with_name(name))
            self._replace(repository, SEMANTIC_ROOT, old_name, name)
            self._replace(repository, OUTCOMES_MEMBER, old_name, name)

        cases = (
            (
                "BUNDLE_DIRECTORY_NUMERIC_PREFIX",
                lambda repository: rename_bundle(repository, "002-semantic-workflows"),
            ),
            (
                "BUNDLE_DIRECTORY_NAME",
                lambda repository: rename_bundle(repository, "Semantic_Workflows"),
            ),
            (
                "BUNDLE_FILENAME_NUMERIC_PREFIX",
                lambda repository: rename_member(repository, "002-bundle-containment-rules.md"),
            ),
            (
                "BUNDLE_FILENAME_NAME",
                lambda repository: rename_member(repository, "Bundle_Containment_Rules.md"),
            ),
            (
                "BUNDLE_FILENAME_GENERIC",
                lambda repository: rename_member(repository, "requirements.md"),
            ),
        )
        for code, mutation in cases:
            with self.subTest(code=code):
                self._assert_mutation_code(code, mutation)

    def test_bundle_wide_semantic_section_failure_matrix(self) -> None:
        def missing_requirements(repository: Path) -> None:
            self._replace(
                repository,
                SEMANTIC_ROOT,
                "\n## Requirements\n\n### Each spec bundle is discovered as a direct child of the spec root\n\nRepository discovery uses the bundle directory as the durable identity.\n",
                "\n",
            )
            self._replace(
                repository,
                CONTAINMENT_MEMBER,
                "\n## Requirements\n\n### Every declared member remains inside its own spec bundle\n\nThe member inventory contains only direct Markdown children of the bundle.\n",
                "\n",
            )

        def missing_acceptance(repository: Path) -> None:
            (repository / OUTCOMES_MEMBER).write_text(
                "# Repository Validation Outcomes\n", encoding="utf-8"
            )

        def duplicate_history(repository: Path) -> None:
            source = repository / CONTAINMENT_MEMBER
            source.write_text(
                source.read_text()
                + "\n## Decisions & History\n\n- 2026-08-09 [CURRENT] Duplicate history.\n",
                encoding="utf-8",
            )

        cases = (
            ("BUNDLE_REQUIREMENTS_MISSING", missing_requirements),
            ("BUNDLE_ACCEPTANCE_MISSING", missing_acceptance),
            ("BUNDLE_HISTORY_COUNT", duplicate_history),
        )
        for code, mutation in cases:
            with self.subTest(code=code):
                self._assert_mutation_code(code, mutation)

    def test_statement_uniqueness_reference_and_coverage_failure_matrix(self) -> None:
        exact_heading = "Each spec bundle is discovered as a direct child of the spec root"
        normalized_heading = (
            "EACH   SPEC BUNDLE IS DISCOVERED AS A DIRECT CHILD OF THE SPEC ROOT"
        )

        def append_requirement(repository: Path, heading: str) -> None:
            source = repository / CONTAINMENT_MEMBER
            source.write_text(
                source.read_text()
                + f"\n### {heading}\n\nA duplicate statement used by validation tests.\n",
                encoding="utf-8",
            )

        def missing_target(repository: Path) -> None:
            self._replace(
                repository,
                OUTCOMES_MEMBER,
                "workflow-contract.md#each-spec-bundle-is-discovered-as-a-direct-child-of-the-spec-root",
                "missing-contract.md#each-spec-bundle-is-discovered-as-a-direct-child-of-the-spec-root",
            )

        def mismatched_text(repository: Path) -> None:
            self._replace(
                repository,
                OUTCOMES_MEMBER,
                f"[{exact_heading}]",
                "[A different requirement sentence]",
            )

        def mismatched_anchor(repository: Path) -> None:
            self._replace(
                repository,
                OUTCOMES_MEMBER,
                "#each-spec-bundle-is-discovered-as-a-direct-child-of-the-spec-root)",
                "#not-the-requirement-anchor)",
            )

        def acceptance_target(repository: Path) -> None:
            self._replace(
                repository,
                OUTCOMES_MEMBER,
                f"[{exact_heading}](workflow-contract.md#each-spec-bundle-is-discovered-as-a-direct-child-of-the-spec-root)",
                "[A semantic workflow with valid members passes repository validation]"
                "(repository-validation-outcomes.md#a-semantic-workflow-with-valid-members-passes-repository-validation)",
            )

        def uncovered_requirement(repository: Path) -> None:
            self._replace(
                repository,
                OUTCOMES_MEMBER,
                "- [Every declared member remains inside its own spec bundle]"
                "(bundle-containment-rules.md#every-declared-member-remains-inside-its-own-spec-bundle)\n",
                "",
            )

        cases = (
            ("STATEMENT_DUPLICATE", lambda repository: append_requirement(repository, exact_heading)),
            (
                "STATEMENT_NORMALIZED_DUPLICATE",
                lambda repository: append_requirement(repository, normalized_heading),
            ),
            ("STATEMENT_REFERENCE_PATH", missing_target),
            ("STATEMENT_REFERENCE_TEXT", mismatched_text),
            ("STATEMENT_REFERENCE_ANCHOR", mismatched_anchor),
            ("STATEMENT_REFERENCE_KIND", acceptance_target),
            ("STATEMENT_COVERAGE", uncovered_requirement),
        )
        for code, mutation in cases:
            with self.subTest(code=code):
                self._assert_mutation_code(code, mutation)

    def test_related_bundle_failure_matrix(self) -> None:
        def related_path(repository: Path, replacement: str) -> None:
            self._replace(
                repository,
                SEMANTIC_ROOT,
                "docs/specs/review-lifecycle/",
                replacement,
            )

        cases = (
            (
                "BUNDLE_RELATED_MISSING",
                lambda repository: related_path(repository, "docs/specs/missing-bundle/"),
            ),
            (
                "BUNDLE_RELATED_SELF",
                lambda repository: related_path(repository, "docs/specs/semantic-workflows/"),
            ),
        )
        for code, mutation in cases:
            with self.subTest(code=code):
                self._assert_mutation_code(code, mutation)

    def test_member_symlink_and_directory_escape_failure_matrix(self) -> None:
        def symlink_member(repository: Path) -> None:
            member = repository / CONTAINMENT_MEMBER
            outside = repository.parent / "outside-contract.md"
            outside.write_text(member.read_text(), encoding="utf-8")
            member.unlink()
            member.symlink_to(outside)

        def escaped_inventory(repository: Path) -> None:
            member = repository / CONTAINMENT_MEMBER
            outside = repository / "docs/specs/outside-contract.md"
            member.rename(outside)
            self._replace(
                repository,
                SEMANTIC_ROOT,
                "bundle-containment-rules.md",
                "../outside-contract.md",
            )

        cases = (
            ("BUNDLE_MEMBER_SYMLINK", symlink_member),
            ("BUNDLE_MEMBER_PATH_ESCAPE", escaped_inventory),
        )
        for code, mutation in cases:
            with self.subTest(code=code):
                self._assert_mutation_code(code, mutation)

    def test_diagnostics_are_repo_relative_repeatable_and_sorted(self) -> None:
        temporary, repository = self._repository()
        with temporary:
            (repository / "docs/specs/semantic-workflows/extra-context.md").write_text(
                "# Extra Context\n", encoding="utf-8"
            )
            self._replace(
                repository,
                OUTCOMES_MEMBER,
                "[Each spec bundle is discovered as a direct child of the spec root]",
                "[A different requirement sentence]",
            )
            self._replace(
                repository,
                SEMANTIC_ROOT,
                "docs/specs/review-lifecycle/",
                "docs/specs/missing-bundle/",
            )

            first = validate_repository(repository, Path("docs/specs")).diagnostics
            second = validate_repository(repository, Path("docs/specs")).diagnostics
            keys = [(item.path, item.line, item.code) for item in first]

            self.assertEqual(first, second)
            self.assertEqual(keys, sorted(keys))
            self.assertTrue(first)
            self.assertTrue(
                all(not Path(diagnostic.path).is_absolute() for diagnostic in first)
            )


if __name__ == "__main__":
    unittest.main()
