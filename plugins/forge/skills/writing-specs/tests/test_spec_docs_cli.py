from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest


TEST_DIR = Path(__file__).parent
FIXTURES = TEST_DIR / "fixtures" / "repository"
WRAPPER = TEST_DIR.parent / "scripts" / "spec-docs.sh"


def run_cli(*arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(WRAPPER), *arguments],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


class SpecDocsCliTest(unittest.TestCase):
    def test_cli_exposes_only_validate_and_inspect(self) -> None:
        result = run_cli("--help")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("validate", result.stdout)
        self.assertIn("inspect", result.stdout)
        self.assertNotIn("build", result.stdout)
        self.assertNotIn("check", result.stdout)

    def test_validate_changes_no_html_files(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            shutil.copytree(FIXTURES / "valid-repository", repo)
            sentinel = repo / "existing.html"
            sentinel.write_text("existing HTML must remain unchanged\n", encoding="utf-8")
            before = {
                path.relative_to(repo): path.read_bytes() for path in repo.rglob("*.html")
            }

            result = run_cli(
                "--repo-root", str(repo), "validate", "--root", "docs/specs"
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            after = {
                path.relative_to(repo): path.read_bytes() for path in repo.rglob("*.html")
            }
            self.assertEqual(after, before)

    def test_wrapper_is_executable(self) -> None:
        self.assertTrue(os.access(WRAPPER, os.X_OK))

    def test_explicit_overlay_root_does_not_require_git(self) -> None:
        repo = FIXTURES / "valid-repository"
        result = run_cli(
            "--repo-root",
            str(repo),
            "validate",
            "--root",
            "docs/specs",
            cwd=TEST_DIR.parents[4],
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")

    def test_global_option_after_subcommand_is_usage_failure(self) -> None:
        repo = FIXTURES / "valid-repository"
        result = run_cli(
            "validate",
            "--repo-root",
            str(repo),
            "--root",
            "docs/specs",
        )
        self.assertEqual(result.returncode, 2)

    def test_validate_prints_sorted_contract_diagnostics(self) -> None:
        repo = FIXTURES / "invalid-repository"
        result = run_cli("--repo-root", str(repo), "validate", "--root", "docs/specs")
        self.assertEqual(result.returncode, 1)
        lines = result.stdout.splitlines()
        diagnostic_keys = []
        for line in lines:
            path, line_number, remainder = line.split(":", 2)
            code = remainder.strip().split(" ", 1)[0]
            diagnostic_keys.append((path, int(line_number), code))
        self.assertEqual(diagnostic_keys, sorted(diagnostic_keys))
        self.assertTrue(all(line.startswith("docs/specs/") for line in lines))

    def test_inspect_json_has_exact_order_and_repository_diagnostics(self) -> None:
        repo = FIXTURES / "inspect-invalid-repository"
        result = run_cli(
            "--repo-root",
            str(repo),
            "inspect",
            "--spec",
            "docs/specs/001-inspect/spec.md",
            "--format",
            "json",
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(
            list(payload),
            [
                "schema",
                "id",
                "status",
                "language",
                "kind",
                "path",
                "sourceSha256",
                "requirements",
                "acceptance",
                "diagnostics",
            ],
        )
        self.assertEqual(list(payload["requirements"][0]), ["id", "text", "line", "removed"])
        self.assertEqual(
            list(payload["acceptance"][0]),
            ["id", "requirements", "text", "line"],
        )
        self.assertEqual(
            list(payload["diagnostics"][0]),
            ["path", "line", "code", "message"],
        )
        self.assertIn(
            "SPEC_REQUIREMENT_UNCOVERED",
            {item["code"] for item in payload["diagnostics"]},
        )
        self.assertEqual(
            {item["code"] for item in payload["diagnostics"]},
            {
                "SPEC_RELATED_MISSING",
                "SPEC_LINK_BROKEN",
                "SPEC_REQUIREMENT_UNCOVERED",
                "SPEC_MERMAID_SYNTAX",
            },
        )

    def test_inspect_parse_failure_uses_null_scalars_and_empty_arrays(self) -> None:
        repo = FIXTURES / "inspect-parse-error"
        result = run_cli(
            "--repo-root",
            str(repo),
            "inspect",
            "--spec",
            "docs/specs/001-broken/spec.md",
            "--format",
            "json",
        )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        for key in ("schema", "id", "status", "language", "kind", "sourceSha256"):
            self.assertIsNone(payload[key])
        self.assertEqual(payload["path"], "docs/specs/001-broken/spec.md")
        self.assertEqual(payload["requirements"], [])
        self.assertEqual(payload["acceptance"], [])
        self.assertTrue(payload["diagnostics"])

    def test_repo_discovery_accepts_git_directory_and_file(self) -> None:
        for git_kind in ("directory", "file"):
            with self.subTest(git_kind=git_kind), TemporaryDirectory() as temporary:
                repo = Path(temporary) / "overlay"
                shutil.copytree(FIXTURES / "valid-repository", repo)
                marker = repo / ".git"
                if git_kind == "directory":
                    marker.mkdir()
                else:
                    marker.write_text("gitdir: /nonexistent/test-git-dir\n")
                nested = repo / "nested/work"
                nested.mkdir(parents=True)
                result = run_cli("validate", "--root", "docs/specs", cwd=nested)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_gitless_explicit_root_rejects_baseline_as_usage(self) -> None:
        repo = FIXTURES / "valid-repository"
        result = run_cli(
            "--repo-root",
            str(repo),
            "validate",
            "--root",
            "docs/specs",
            "--baseline-ref",
            "HEAD",
        )
        self.assertEqual(result.returncode, 2)

    def test_baseline_with_any_legacy_source_is_usage_failure(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            shutil.copytree(FIXTURES / "valid-repository", repo)
            legacy = repo / "docs/specs/099-legacy/spec.md"
            legacy.parent.mkdir(parents=True)
            legacy.write_text("# Legacy\n\nStatus: approved\n")
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
                    "mixed baseline",
                ],
                cwd=repo,
                check=True,
            )
            legacy.unlink()
            result = run_cli(
                "--repo-root",
                str(repo),
                "validate",
                "--root",
                "docs/specs",
                "--baseline-ref",
                "HEAD",
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

if __name__ == "__main__":
    unittest.main()
