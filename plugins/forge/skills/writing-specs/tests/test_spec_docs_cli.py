from __future__ import annotations

import hashlib
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

    def test_full_build_completes_supersession_cutover_and_second_build_has_no_diff(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            old_source = repo / "docs/specs/001-history/spec.md"
            old_source.parent.mkdir(parents=True)
            old_source.write_bytes(
                (FIXTURES / "baseline-template/spec.md").read_bytes()
            )

            initial_build = run_cli(
                "--repo-root",
                str(repo),
                "build",
                "--root",
                "docs/specs",
                "--offline",
            )
            self.assertEqual(
                initial_build.returncode,
                0,
                initial_build.stdout + initial_build.stderr,
            )
            old_page = repo / "docs/specs/001-history/index.html"
            self.assertTrue(old_page.is_file())

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
                    "baseline pages",
                ],
                cwd=repo,
                check=True,
            )

            old_sha256 = hashlib.sha256(old_source.read_bytes()).hexdigest()
            replacement = repo / "docs/specs/001-current/spec.md"
            replacement.parent.mkdir()
            replacement.write_text(
                old_source.read_text(encoding="utf-8")
                .replace("001-history", "001-current")
                .replace("status: approved", "status: implemented", 1),
                encoding="utf-8",
            )
            evidence = repo / "docs/plans/001-history/evidence.md"
            evidence.parent.mkdir(parents=True)
            evidence.write_text("# Historical evidence\n", encoding="utf-8")
            (repo / "docs/specs/.transitions.json").write_text(
                json.dumps(
                    {
                        "schema": "forge/spec-transitions@1",
                        "transitions": [
                            {
                                "fromId": "001-history",
                                "fromPath": "docs/specs/001-history/spec.md",
                                "fromSourceSha256": old_sha256,
                                "disposition": "superseded",
                                "toId": "001-current",
                                "toPath": "docs/specs/001-current/spec.md",
                                "evidencePath": "docs/plans/001-history/evidence.md",
                                "reason": "Keep the active specification limited to current facts.",
                            }
                        ],
                    },
                    separators=(",", ":"),
                ),
                encoding="utf-8",
            )
            old_source.unlink()

            validation = run_cli(
                "--repo-root",
                str(repo),
                "validate",
                "--root",
                "docs/specs",
                "--baseline-ref",
                "HEAD",
            )
            self.assertEqual(
                validation.returncode,
                0,
                validation.stdout + validation.stderr,
            )

            prebuild_check = run_cli(
                "--repo-root", str(repo), "check", "--root", "docs/specs"
            )
            self.assertEqual(prebuild_check.returncode, 1)
            self.assertIn("SPEC_PAGE_ORPHAN", prebuild_check.stdout)
            self.assertIn("SPEC_PAGE_MISSING", prebuild_check.stdout)
            self.assertIn("SPEC_PAGE_STALE", prebuild_check.stdout)

            first_build = run_cli(
                "--repo-root",
                str(repo),
                "build",
                "--root",
                "docs/specs",
                "--offline",
            )
            self.assertEqual(
                first_build.returncode, 0, first_build.stdout + first_build.stderr
            )
            replacement_page = repo / "docs/specs/001-current/index.html"
            catalog = repo / "docs/specs/index.html"
            self.assertFalse(old_page.exists())
            self.assertTrue(replacement_page.is_file())
            self.assertTrue(catalog.is_file())
            self.assertNotIn("001-history", catalog.read_text(encoding="utf-8"))
            self.assertIn("001-current", catalog.read_text(encoding="utf-8"))

            postbuild_check = run_cli(
                "--repo-root", str(repo), "check", "--root", "docs/specs"
            )
            self.assertEqual(
                postbuild_check.returncode,
                0,
                postbuild_check.stdout + postbuild_check.stderr,
            )
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
                    "candidate cutover",
                ],
                cwd=repo,
                check=True,
            )

            second_build = run_cli(
                "--repo-root",
                str(repo),
                "build",
                "--root",
                "docs/specs",
                "--offline",
            )
            self.assertEqual(
                second_build.returncode,
                0,
                second_build.stdout + second_build.stderr,
            )
            diff = subprocess.run(
                ["git", "diff", "--exit-code"],
                cwd=repo,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(diff.returncode, 0, diff.stdout + diff.stderr)


if __name__ == "__main__":
    unittest.main()
