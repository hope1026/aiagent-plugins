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

    def test_related_specs_reject_escape_and_id_mismatch(self) -> None:
        repo = FIXTURES / "plan-repository"
        refs, errors = parse_plan_related_specs(repo / "plans/bad-plan.md", repo)
        self.assertEqual(refs, ())
        self.assertEqual(
            {item.code for item in errors},
            {"PLAN_SPEC_PATH_ESCAPE", "PLAN_SPEC_ID_PATH_MISMATCH"},
        )

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

    def test_related_specs_bare_zero_entry_block_is_not_canonical_none(self) -> None:
        repo = FIXTURES / "plan-repository"
        refs, errors = parse_plan_related_specs(repo / "plans/bare-plan.md", repo)
        self.assertEqual(refs, ())
        self.assertEqual({item.code for item in errors}, {"PLAN_SPEC_FORMAT"})

    def test_related_specs_require_explicit_ids(self) -> None:
        repo = FIXTURES / "plan-repository"
        refs, errors = parse_plan_related_specs(repo / "plans/range-plan.md", repo)
        self.assertEqual(refs, ())
        self.assertIn("PLAN_SPEC_RANGE_FORBIDDEN", {item.code for item in errors})

    def test_related_specs_allow_approved_and_implemented(self) -> None:
        repo = FIXTURES / "plan-repository"
        for name, expected_id in (
            ("approved-plan.md", "001-approved-source"),
            ("implemented-plan.md", "002-implemented-source"),
        ):
            with self.subTest(name=name):
                refs, errors = parse_plan_related_specs(repo / "plans" / name, repo)
                self.assertEqual(errors, ())
                self.assertEqual([item.id for item in refs], [expected_id])
                self.assertEqual(refs[0].requirements, ("R1",))
                self.assertEqual(refs[0].acceptance, ("AC1",))

        refs, errors = parse_plan_related_specs(repo / "plans/empty-arrays-plan.md", repo)
        self.assertEqual(errors, ())
        self.assertEqual((refs[0].requirements, refs[0].acceptance), ((), ()))

        refs, errors = parse_plan_related_specs(repo / "plans/multiple-plan.md", repo)
        self.assertEqual(errors, ())
        self.assertEqual(
            [item.id for item in refs],
            ["001-approved-source", "002-implemented-source"],
        )

    def test_related_specs_validate_status_presence_and_item_ids(self) -> None:
        repo = FIXTURES / "plan-repository"
        expected = {
            "draft-plan.md": "PLAN_SPEC_STATUS",
            "missing-plan.md": "PLAN_SPEC_MISSING",
            "missing-requirement-plan.md": "PLAN_SPEC_REQUIREMENT_MISSING",
            "missing-acceptance-plan.md": "PLAN_SPEC_ACCEPTANCE_MISSING",
            "duplicate-plan.md": "PLAN_SPEC_DUPLICATE",
        }
        for name, code in expected.items():
            with self.subTest(name=name):
                refs, errors = parse_plan_related_specs(repo / "plans" / name, repo)
                self.assertEqual(refs, ())
                self.assertIn(code, {item.code for item in errors})

        refs, errors = parse_plan_related_specs(repo / "plans/none-plan.md", repo)
        self.assertEqual((refs, errors), ((), ()))

    def test_related_specs_reject_symlink_escape(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            outside = root / "outside"
            (repo / "plans").mkdir(parents=True)
            outside.mkdir()
            shutil.copy(
                FIXTURES / "plan-repository/docs/specs/001-approved-source/spec.md",
                outside / "spec.md",
            )
            (repo / "linked-spec").symlink_to(outside, target_is_directory=True)
            plan = repo / "plans/symlink-plan.md"
            plan.write_text(
                "# Plan\n\n**Related Specs:**\n"
                "- id: 001-approved-source\n"
                "  path: linked-spec/spec.md\n"
                "  requirements: [R1]\n"
                "  acceptance: [AC1]\n"
            )
            refs, errors = parse_plan_related_specs(plan, repo)
            self.assertEqual(refs, ())
            self.assertEqual({item.code for item in errors}, {"PLAN_SPEC_PATH_ESCAPE"})


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
