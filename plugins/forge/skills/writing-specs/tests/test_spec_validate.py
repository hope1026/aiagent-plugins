from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import spec_validate
from spec_validate import parse_plan_related_specs, validate_repository


FIXTURES = Path(__file__).parent / "fixtures" / "repository"
PLAN_BUNDLE_FIXTURES = Path(__file__).parent / "fixtures" / "plan-bundle-repository"


class RepositoryValidationTest(unittest.TestCase):
    def test_bundle_mode_detection_reads_frontmatter_not_body_examples(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            shutil.copytree(FIXTURES / "valid-repository", repo)
            source = repo / "docs/specs/001-valid-feature/spec.md"
            source.write_text(
                source.read_text(encoding="utf-8")
                + "\n```yaml\nschema: forge/spec@3\nrole: root\n```\n",
                encoding="utf-8",
            )

            result = validate_repository(repo)

            self.assertTrue(result.ok, result.diagnostics)
            self.assertEqual(len(result.documents), 2)
            self.assertEqual(result.bundles, ())

    def test_repository_rejects_symlinked_spec_source_escape_without_crashing(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            outside = root / "outside-spec.md"
            linked = repo / "docs/specs/001-linked/spec.md"
            linked.parent.mkdir(parents=True)
            source = (FIXTURES / "baseline-template/spec.md").read_text().replace(
                "001-history", "001-linked"
            )
            outside.write_text(source)
            linked.symlink_to(outside)

            result = validate_repository(repo)
            self.assertEqual(
                {item.code for item in result.diagnostics},
                {"SPEC_SOURCE_PATH_ESCAPE"},
            )
            self.assertTrue(all(not Path(item.path).is_absolute() for item in result.diagnostics))

    def test_valid_repository_returns_repo_relative_documents(self) -> None:
        repo = FIXTURES / "valid-repository"
        result = validate_repository(repo, Path("docs/specs"))

        self.assertTrue(result.ok)
        self.assertEqual(result.diagnostics, ())
        self.assertEqual(
            [item.path.as_posix() for item in result.documents],
            [
                "docs/specs/001-valid-feature/spec.md",
                "docs/specs/002-implemented-context/spec.md",
            ],
        )

    def test_diagnostics_are_sorted_and_complete(self) -> None:
        repo = FIXTURES / "invalid-repository"
        result = validate_repository(repo, Path("docs/specs"))

        self.assertEqual(list(result.diagnostics), sorted(result.diagnostics))
        self.assertEqual(
            {item.code for item in result.diagnostics},
            {
                "SPEC_DUPLICATE_ID",
                "SPEC_PATH_LAYOUT",
                "SPEC_RELATED_MISSING",
                "SPEC_LINK_BROKEN",
                "SPEC_REQUIREMENT_UNCOVERED",
            },
        )
        self.assertTrue(all(not Path(item.path).is_absolute() for item in result.diagnostics))

    def test_isolated_repository_failure_matrix(self) -> None:
        expected = {
            "wrong-schema": "SPEC_SCHEMA",
            "id-path": "SPEC_ID_PATH",
            "self-relation": "SPEC_RELATED_SELF",
            "duplicate-ac": "SPEC_AC_DUPLICATE",
            "removed-reference": "SPEC_AC_REFERENCE_REMOVED",
            "approved-clarification": "SPEC_CLARIFICATION_STATUS",
            "implemented-clarification": "SPEC_CLARIFICATION_STATUS",
            "invalid-mermaid": "SPEC_MERMAID_SYNTAX",
        }
        for case, code in expected.items():
            with self.subTest(case=case):
                repo = FIXTURES / "cases" / case
                result = validate_repository(repo, Path("docs/specs"))
                self.assertEqual({item.code for item in result.diagnostics}, {code})

    def test_mermaid_runtime_unavailable_is_not_silently_skipped(self) -> None:
        missing = FIXTURES / "missing-mermaid-validator.bundle.mjs"
        with patch.object(spec_validate, "MERMAID_VALIDATOR_BUNDLE", missing):
            result = validate_repository(FIXTURES / "valid-repository")
        self.assertIn(
            "SPEC_MERMAID_RUNTIME_UNAVAILABLE",
            {item.code for item in result.diagnostics},
        )

    def test_mermaid_runtime_malformed_response_and_nonstandard_exit_are_unavailable(self) -> None:
        responses = (
            subprocess.CompletedProcess([], 0, "not-json", ""),
            subprocess.CompletedProcess(
                [],
                7,
                '{"valid":false,"diagnostics":[{"line":1,"code":"SPEC_MERMAID_SYNTAX","message":"x"}]}',
                "",
            ),
        )
        for response in responses:
            with self.subTest(returncode=response.returncode), patch.object(
                spec_validate.subprocess, "run", return_value=response
            ):
                result = validate_repository(FIXTURES / "valid-repository")
                self.assertEqual(
                    {item.code for item in result.diagnostics},
                    {"SPEC_MERMAID_RUNTIME_UNAVAILABLE"},
                )

    def test_mermaid_runtime_uses_explicit_utf8_bytes_and_normalizes_codec_failure(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            shutil.copytree(FIXTURES / "valid-repository", repo)
            source = repo / "docs/specs/001-valid-feature/spec.md"
            source.write_text(source.read_text().replace("A[Input]", "A[입력]"))

            def utf8_validator(arguments, **kwargs):
                self.assertIsInstance(kwargs["input"], bytes)
                self.assertNotIn("text", kwargs)
                self.assertIn("입력", kwargs["input"].decode("utf-8"))
                return subprocess.CompletedProcess(
                    arguments,
                    0,
                    b'{"valid":true,"diagnostics":[]}\n',
                    b"",
                )

            with patch.object(spec_validate.subprocess, "run", side_effect=utf8_validator):
                self.assertTrue(validate_repository(repo).ok)

            codec_failure = subprocess.CompletedProcess([], 0, b"\xff", b"")
            with patch.object(spec_validate.subprocess, "run", return_value=codec_failure):
                result = validate_repository(repo)
            self.assertEqual(
                {item.code for item in result.diagnostics},
                {"SPEC_MERMAID_RUNTIME_UNAVAILABLE"},
            )

    def test_related_bundles_and_governing_statements_resolve_exact_headings(self) -> None:
        repo = PLAN_BUNDLE_FIXTURES
        plan = repo / "docs/plans/semantic-migration/valid-plan.md"

        refs, diagnostics = parse_plan_related_specs(plan, repo)

        self.assertEqual(diagnostics, ())
        self.assertEqual(
            [ref.bundle_path.as_posix() for ref in refs],
            ["docs/specs/semantic-spec-bundles"],
        )
        task_refs, diagnostics = spec_validate.parse_plan_governing_statements(
            plan, repo, refs
        )
        self.assertEqual(diagnostics, ())
        self.assertEqual(
            [(ref.kind, ref.heading) for ref in task_refs],
            [
                ("requirement", "Each bundle has exactly one root document"),
                ("acceptance", "A bundle with one declared root passes structural validation"),
            ],
        )
        self.assertEqual(
            task_refs[0].member_path.as_posix(),
            "docs/specs/semantic-spec-bundles/semantic-spec-bundle-contract.md",
        )
        self.assertEqual(
            task_refs[0].anchor,
            "each-bundle-has-exactly-one-root-document",
        )
        self.assertGreater(task_refs[0].line, 1)

    def test_related_specs_reject_plan_source_escape_before_reading(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            repo.mkdir()
            outside_plan = root / "outside-plan.md"

            refs, errors = parse_plan_related_specs(outside_plan, repo)
            self.assertEqual(refs, ())
            self.assertEqual({item.code for item in errors}, {"PLAN_SPEC_PATH_ESCAPE"})
            self.assertTrue(all(not Path(item.path).is_absolute() for item in errors))

    def test_related_specs_accept_only_bundle_paths_or_canonical_none(self) -> None:
        repo = PLAN_BUNDLE_FIXTURES
        none_plan = repo / "docs/plans/semantic-migration/none-plan.md"
        refs, errors = parse_plan_related_specs(none_plan, repo)
        self.assertEqual((refs, errors), ((), ()))

        invalid_cases = {
            "noncanonical-plan.md": "PLAN_SPEC_FORMAT",
            "bare.md": "PLAN_SPEC_FORMAT",
            "array.md": "PLAN_SPEC_FORMAT",
        }
        with TemporaryDirectory() as temporary:
            copied_repo = Path(temporary) / "repo"
            shutil.copytree(repo, copied_repo)
            plans = copied_repo / "docs/plans/semantic-migration"
            (plans / "bare.md").write_text(
                "# Plan\n\n**Related Specs:**\n\n### Task 1: Work\n",
                encoding="utf-8",
            )
            (plans / "array.md").write_text(
                "# Plan\n\n**Related Specs:**\n\n- bundle: [docs/specs/semantic-spec-bundles/]\n",
                encoding="utf-8",
            )
            for name, code in invalid_cases.items():
                with self.subTest(name=name):
                    refs, errors = parse_plan_related_specs(plans / name, copied_repo)
                    self.assertEqual(refs, ())
                    self.assertIn(code, {item.code for item in errors})

    def test_related_specs_validate_duplicates_missing_draft_and_escape(self) -> None:
        repo = PLAN_BUNDLE_FIXTURES
        valid = (
            repo / "docs/plans/semantic-migration/valid-plan.md"
        ).read_text(encoding="utf-8")
        replacements = {
            "duplicate.md": (
                "- bundle: docs/specs/semantic-spec-bundles/",
                "- bundle: docs/specs/semantic-spec-bundles/\n"
                "- bundle: docs/specs/semantic-spec-bundles/",
                "PLAN_SPEC_DUPLICATE",
            ),
            "missing.md": (
                "docs/specs/semantic-spec-bundles/",
                "docs/specs/not-present/",
                "PLAN_SPEC_MISSING",
            ),
            "escape.md": (
                "docs/specs/semantic-spec-bundles/",
                "docs/specs/../outside/",
                "PLAN_SPEC_PATH_ESCAPE",
            ),
        }
        with TemporaryDirectory() as temporary:
            copied_repo = Path(temporary) / "repo"
            shutil.copytree(repo, copied_repo)
            plans = copied_repo / "docs/plans/semantic-migration"
            for name, (old, new, code) in replacements.items():
                with self.subTest(name=name):
                    plan = plans / name
                    plan.write_text(valid.replace(old, new, 1), encoding="utf-8")
                    refs, errors = parse_plan_related_specs(plan, copied_repo)
                    self.assertEqual(refs, ())
                    self.assertIn(code, {item.code for item in errors})

            root = (
                copied_repo
                / "docs/specs/semantic-spec-bundles/semantic-spec-bundle-contract.md"
            )
            root.write_text(
                root.read_text(encoding="utf-8").replace(
                    "status: approved", "status: draft"
                ),
                encoding="utf-8",
            )
            draft_plan = plans / "draft.md"
            draft_plan.write_text(valid, encoding="utf-8")
            refs, errors = parse_plan_related_specs(draft_plan, copied_repo)
            self.assertEqual(refs, ())
            self.assertIn("PLAN_SPEC_STATUS", {item.code for item in errors})

    def test_related_specs_reject_symlink_escape(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            outside = root / "outside"
            (repo / "plans").mkdir(parents=True)
            outside.mkdir()
            shutil.copytree(
                PLAN_BUNDLE_FIXTURES / "docs/specs/semantic-spec-bundles",
                outside / "escaped-bundle",
            )
            (repo / "docs/specs").mkdir(parents=True)
            (repo / "docs/plans").mkdir(parents=True)
            (repo / "docs/specs/linked-bundle").symlink_to(
                outside / "escaped-bundle", target_is_directory=True
            )
            plan = repo / "docs/plans/symlink-plan.md"
            plan.write_text(
                "# Plan\n\n**Related Specs:**\n\n"
                "- bundle: docs/specs/linked-bundle/\n",
                encoding="utf-8",
            )
            refs, errors = parse_plan_related_specs(plan, repo)
            self.assertEqual(refs, ())
            self.assertEqual({item.code for item in errors}, {"PLAN_SPEC_PATH_ESCAPE"})

    def test_governing_statements_reject_invalid_trace_matrix(self) -> None:
        repo = PLAN_BUNDLE_FIXTURES
        plan_path = repo / "docs/plans/semantic-migration/valid-plan.md"
        valid = plan_path.read_text(encoding="utf-8")
        cases = {
            "dangling.md": (
                "[Each bundle has exactly one root document]"
                "(../../specs/semantic-spec-bundles/semantic-spec-bundle-contract.md"
                "#each-bundle-has-exactly-one-root-document)",
                "[A statement that is not present]"
                "(../../specs/semantic-spec-bundles/semantic-spec-bundle-contract.md"
                "#a-statement-that-is-not-present)",
                "PLAN_STATEMENT_MISSING",
            ),
            "text.md": (
                "[Each bundle has exactly one root document]",
                "[Different visible statement text]",
                "PLAN_STATEMENT_TEXT",
            ),
            "anchor.md": (
                "#each-bundle-has-exactly-one-root-document",
                "#a-bundle-with-one-declared-root-passes-structural-validation",
                "PLAN_STATEMENT_ANCHOR",
            ),
            "unrelated.md": (
                "../../specs/semantic-spec-bundles/semantic-spec-bundle-contract.md"
                "#each-bundle-has-exactly-one-root-document",
                "../../specs/supporting-policy/supporting-policy-contract.md"
                "#plans-preserve-repository-contained-source-links",
                "PLAN_STATEMENT_BUNDLE",
            ),
            "duplicate.md": (
                "- [A bundle with one declared root passes structural validation]",
                "- [Each bundle has exactly one root document]"
                "(../../specs/semantic-spec-bundles/semantic-spec-bundle-contract.md"
                "#each-bundle-has-exactly-one-root-document)\n"
                "- [A bundle with one declared root passes structural validation]",
                "PLAN_STATEMENT_DUPLICATE",
            ),
        }
        with TemporaryDirectory() as temporary:
            copied_repo = Path(temporary) / "repo"
            shutil.copytree(repo, copied_repo)
            copied_plan = copied_repo / plan_path.relative_to(repo)
            refs, errors = parse_plan_related_specs(copied_plan, copied_repo)
            self.assertEqual(errors, ())
            for name, (old, new, expected_code) in cases.items():
                with self.subTest(name=name):
                    changed = copied_plan.with_name(name)
                    changed.write_text(valid.replace(old, new, 1), encoding="utf-8")
                    task_refs, errors = spec_validate.parse_plan_governing_statements(
                        changed, copied_repo, refs
                    )
                    self.assertEqual(task_refs, ())
                    self.assertEqual(list(errors), sorted(errors))
                    self.assertIn(expected_code, {item.code for item in errors})

    def test_governing_statement_must_target_a_normative_statement_kind(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            shutil.copytree(PLAN_BUNDLE_FIXTURES, repo)
            root = (
                repo
                / "docs/specs/semantic-spec-bundles/semantic-spec-bundle-contract.md"
            )
            root.write_text(
                root.read_text(encoding="utf-8")
                + "\n## Supporting Notes\n\n### Internal parser note\n\nNot normative.\n",
                encoding="utf-8",
            )
            plan = repo / "docs/plans/semantic-migration/valid-plan.md"
            plan.write_text(
                plan.read_text(encoding="utf-8").replace(
                    "[Each bundle has exactly one root document]"
                    "(../../specs/semantic-spec-bundles/semantic-spec-bundle-contract.md"
                    "#each-bundle-has-exactly-one-root-document)",
                    "[Internal parser note]"
                    "(../../specs/semantic-spec-bundles/semantic-spec-bundle-contract.md"
                    "#internal-parser-note)",
                    1,
                ),
                encoding="utf-8",
            )
            refs, errors = parse_plan_related_specs(plan, repo)
            self.assertEqual(errors, ())
            task_refs, errors = spec_validate.parse_plan_governing_statements(
                plan, repo, refs
            )
            self.assertEqual(task_refs, ())
            self.assertEqual({item.code for item in errors}, {"PLAN_STATEMENT_KIND"})

    def test_governed_plan_requires_nonempty_statement_block_for_every_task(self) -> None:
        repo = PLAN_BUNDLE_FIXTURES
        plan_path = repo / "docs/plans/semantic-migration/valid-plan.md"
        valid = plan_path.read_text(encoding="utf-8")
        cases = {
            "missing-block.md": valid.replace("Governing statements:\n", "", 1),
            "empty-block.md": valid.replace(
                "- [Each bundle has exactly one root document]"
                "(../../specs/semantic-spec-bundles/semantic-spec-bundle-contract.md"
                "#each-bundle-has-exactly-one-root-document)\n"
                "- [A bundle with one declared root passes structural validation]"
                "(../../specs/semantic-spec-bundles/bundle-validation-outcomes.md"
                "#a-bundle-with-one-declared-root-passes-structural-validation)\n",
                "",
                1,
            ),
        }
        with TemporaryDirectory() as temporary:
            copied_repo = Path(temporary) / "repo"
            shutil.copytree(repo, copied_repo)
            copied_plan = copied_repo / plan_path.relative_to(repo)
            refs, errors = parse_plan_related_specs(copied_plan, copied_repo)
            self.assertEqual(errors, ())
            for name, source in cases.items():
                with self.subTest(name=name):
                    changed = copied_plan.with_name(name)
                    changed.write_text(source, encoding="utf-8")
                    task_refs, errors = spec_validate.parse_plan_governing_statements(
                        changed, copied_repo, refs
                    )
                    self.assertEqual(task_refs, ())
                    self.assertIn(
                        "PLAN_STATEMENT_BLOCK_MISSING"
                        if name == "missing-block.md"
                        else "PLAN_STATEMENT_EMPTY",
                        {item.code for item in errors},
                    )

    def test_governing_statement_path_rejects_symlink_escape(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            shutil.copytree(PLAN_BUNDLE_FIXTURES, repo)
            outside = root / "outside.md"
            outside.write_text("# Outside\n", encoding="utf-8")
            linked = repo / "docs/links/escaped.md"
            linked.parent.mkdir()
            linked.symlink_to(outside)
            plan = repo / "docs/plans/semantic-migration/valid-plan.md"
            plan.write_text(
                plan.read_text(encoding="utf-8").replace(
                    "../../specs/semantic-spec-bundles/semantic-spec-bundle-contract.md",
                    "../../links/escaped.md",
                    1,
                ),
                encoding="utf-8",
            )
            refs, errors = parse_plan_related_specs(plan, repo)
            self.assertEqual(errors, ())
            task_refs, errors = spec_validate.parse_plan_governing_statements(
                plan, repo, refs
            )
            self.assertEqual(task_refs, ())
            self.assertIn("PLAN_STATEMENT_PATH_ESCAPE", {item.code for item in errors})


class BaselineValidationTest(unittest.TestCase):
    def _git_repository(self, status: str) -> tuple[TemporaryDirectory[str], Path, Path]:
        temporary = TemporaryDirectory()
        repo = Path(temporary.name)
        source = repo / "docs/specs/001-history/spec.md"
        source.parent.mkdir(parents=True)
        fixture = (FIXTURES / "baseline-template/spec.md").read_text()
        source.write_text(fixture.replace("status: approved", f"status: {status}"))
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Forge Test",
                "-c",
                "user.email=forge@example.invalid",
                "commit",
                "-qm",
                "baseline",
            ],
            cwd=repo,
            check=True,
        )
        return temporary, repo, source

    def test_history_accepts_exact_prefix_append(self) -> None:
        temporary, repo, source = self._git_repository("approved")
        with temporary:
            source.write_text(
                source.read_text()
                + "- 2026-08-02 [DECISION] append only.\n"
            )
            result = validate_repository(repo, baseline_ref="HEAD")
            self.assertTrue(result.ok, result.diagnostics)

    def test_history_rejects_existing_line_modification(self) -> None:
        temporary, repo, source = self._git_repository("approved")
        with temporary:
            source.write_text(source.read_text().replace("baseline decision", "changed decision"))
            result = validate_repository(repo, baseline_ref="HEAD")
            self.assertIn(
                "SPEC_HISTORY_NOT_APPEND_ONLY",
                {item.code for item in result.diagnostics},
            )

    def test_history_rejects_line_deletion_and_whitespace_mutation(self) -> None:
        replacements = ("", "- 2026-08-01 [DECISION] baseline  decision.\n")
        for replacement in replacements:
            with self.subTest(replacement=repr(replacement)):
                temporary, repo, source = self._git_repository("implemented")
                with temporary:
                    source.write_text(
                        source.read_text().replace(
                            "- 2026-08-01 [DECISION] baseline decision.\n",
                            replacement,
                        )
                    )
                    result = validate_repository(repo, baseline_ref="HEAD")
                    self.assertIn(
                        "SPEC_HISTORY_NOT_APPEND_ONLY",
                        {item.code for item in result.diagnostics},
                    )

    def test_history_normalizes_only_line_endings(self) -> None:
        temporary, repo, source = self._git_repository("approved")
        with temporary:
            source.write_bytes(source.read_text().replace("\n", "\r\n").encode("utf-8"))
            result = validate_repository(repo, baseline_ref="HEAD")
            self.assertTrue(result.ok, result.diagnostics)

    def test_draft_and_legacy_baselines_do_not_claim_append_only(self) -> None:
        temporary, repo, source = self._git_repository("draft")
        with temporary:
            source.write_text(source.read_text().replace("baseline decision", "changed"))
            self.assertTrue(validate_repository(repo, baseline_ref="HEAD").ok)

        with TemporaryDirectory() as temporary_name:
            legacy_repo = Path(temporary_name)
            legacy = legacy_repo / "docs/specs/legacy/spec.md"
            legacy.parent.mkdir(parents=True)
            legacy.write_text("# Legacy\n\nStatus: approved\n")
            subprocess.run(["git", "init", "-q"], cwd=legacy_repo, check=True)
            subprocess.run(["git", "add", "."], cwd=legacy_repo, check=True)
            subprocess.run(
                ["git", "-c", "user.name=X", "-c", "user.email=x@y", "commit", "-qm", "legacy"],
                cwd=legacy_repo,
                check=True,
            )
            legacy.unlink()
            self.assertTrue(validate_repository(legacy_repo, baseline_ref="HEAD").ok)

    def test_invalid_ref_and_gitless_baseline_are_diagnostics(self) -> None:
        temporary, repo, _ = self._git_repository("approved")
        with temporary:
            result = validate_repository(repo, baseline_ref="missing-ref")
            self.assertEqual(
                {item.code for item in result.diagnostics},
                {"SPEC_BASELINE_UNAVAILABLE"},
            )
        result = validate_repository(FIXTURES / "valid-repository", baseline_ref="HEAD")
        self.assertIn("SPEC_BASELINE_UNAVAILABLE", {item.code for item in result.diagnostics})

    def test_baseline_rejects_full_approved_or_implemented_source_deletion(self) -> None:
        for status in ("approved", "implemented"):
            with self.subTest(status=status):
                temporary, repo, source = self._git_repository(status)
                with temporary:
                    source.unlink()
                    result = validate_repository(repo, baseline_ref="HEAD")
                    self.assertIn(
                        "SPEC_HISTORY_NOT_APPEND_ONLY",
                        {item.code for item in result.diagnostics},
                    )


if __name__ == "__main__":
    unittest.main()
