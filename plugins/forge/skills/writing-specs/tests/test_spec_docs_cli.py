from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest


TEST_DIR = Path(__file__).parent
BUNDLE_FIXTURE = TEST_DIR / "fixtures/spec-bundle/valid-multi-file"
REPOSITORY_FIXTURE = (
    TEST_DIR / "fixtures/spec-bundle-repository/valid-multi-bundle"
)
WRAPPER = TEST_DIR.parent / "scripts/spec-docs.sh"


def run_cli(*arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(WRAPPER), *arguments],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


class SpecDocsCliTest(unittest.TestCase):
    def test_inspect_bundle_json_uses_paths_and_full_statements_without_id(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            bundle_path = repo / "docs/specs/semantic-spec-bundles"
            bundle_path.parent.mkdir(parents=True)
            shutil.copytree(BUNDLE_FIXTURE, bundle_path)

            result = run_cli(
                "--repo-root",
                str(repo),
                "inspect",
                "--spec",
                "docs/specs/semantic-spec-bundles/",
                "--format",
                "json",
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertNotIn("id", payload)
            self.assertEqual(
                list(payload),
                [
                    "schema",
                    "bundlePath",
                    "rootPath",
                    "title",
                    "status",
                    "language",
                    "kind",
                    "subtype",
                    "areas",
                    "components",
                    "relatedSpecs",
                    "bundleSha256",
                    "members",
                    "statements",
                    "diagnostics",
                ],
            )
            self.assertEqual(
                list(payload["members"][0]),
                ["path", "title", "role", "sourceSha256"],
            )
            self.assertEqual(
                list(payload["statements"][0]),
                ["kind", "path", "heading", "line", "references"],
            )
            self.assertEqual(
                payload["statements"][0]["heading"],
                "Each bundle has exactly one root document",
            )

    def test_inspect_requires_a_bundle_directory(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            bundle_path = repo / "docs/specs/semantic-spec-bundles"
            bundle_path.parent.mkdir(parents=True)
            shutil.copytree(BUNDLE_FIXTURE, bundle_path)
            result = run_cli(
                "--repo-root",
                str(repo),
                "inspect",
                "--spec",
                "docs/specs/semantic-spec-bundles/semantic-spec-bundle-contract.md",
                "--format",
                "json",
            )
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(
                {item["code"] for item in payload["diagnostics"]},
                {"BUNDLE_SOURCE_PATH"},
            )
            self.assertNotIn("id", payload)

    def test_inspect_parse_failure_uses_bundle_shaped_empty_values(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            bundle = repo / "docs/specs/broken-bundle"
            bundle.mkdir(parents=True)
            (bundle / "broken-contract.md").write_text("# Broken\n", encoding="utf-8")
            result = run_cli(
                "--repo-root",
                str(repo),
                "inspect",
                "--spec",
                "docs/specs/broken-bundle",
                "--format",
                "json",
            )
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            for key in ("schema", "rootPath", "title", "status", "language", "kind"):
                self.assertIsNone(payload[key])
            self.assertEqual(payload["bundlePath"], "docs/specs/broken-bundle")
            self.assertEqual(payload["members"], [])
            self.assertEqual(payload["statements"], [])
            self.assertTrue(payload["diagnostics"])

    def test_validate_changes_no_html_files(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            shutil.copytree(REPOSITORY_FIXTURE, repo)
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

    def test_validate_prints_sorted_bundle_diagnostics(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            broken = repo / "docs/specs/broken-bundle"
            broken.mkdir(parents=True)
            (broken / "broken-contract.md").write_text("# Broken\n", encoding="utf-8")
            result = run_cli(
                "--repo-root", str(repo), "validate", "--root", "docs/specs"
            )
            self.assertEqual(result.returncode, 1)
            keys = []
            for line in result.stdout.splitlines():
                path, line_number, remainder = line.split(":", 2)
                keys.append((path, int(line_number), remainder.strip().split(" ", 1)[0]))
            self.assertEqual(keys, sorted(keys))
            self.assertTrue(all(path.startswith("docs/specs/") for path, _, _ in keys))

    def test_validate_rejects_active_bundle_demotion_against_git_baseline(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            shutil.copytree(REPOSITORY_FIXTURE, repo)
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
                    "active baseline",
                ],
                cwd=repo,
                check=True,
            )
            root = repo / "docs/specs/review-lifecycle/review-lifecycle-contract.md"
            root.write_text(
                root.read_text(encoding="utf-8").replace(
                    "status: implemented", "status: draft"
                ),
                encoding="utf-8",
            )

            result = run_cli(
                "--repo-root",
                str(repo),
                "validate",
                "--root",
                "docs/specs",
                "--baseline-ref",
                "HEAD",
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("SPEC_ACTIVE_STATUS_DOWNGRADE", result.stdout)

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
                    "demote active bundle",
                ],
                cwd=repo,
                check=True,
            )
            committed_result = run_cli(
                "--repo-root",
                str(repo),
                "validate",
                "--root",
                "docs/specs",
                "--baseline-ref",
                "HEAD^",
            )

            self.assertEqual(committed_result.returncode, 1)
            self.assertIn("SPEC_ACTIVE_STATUS_DOWNGRADE", committed_result.stdout)

    def test_cli_exposes_only_validate_and_inspect(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("validate", result.stdout)
        self.assertIn("inspect", result.stdout)
        self.assertNotIn("build", result.stdout)
        self.assertNotIn("check", result.stdout)

    def test_wrapper_is_executable(self) -> None:
        self.assertTrue(os.access(WRAPPER, os.X_OK))

    def test_explicit_overlay_root_does_not_require_git(self) -> None:
        result = run_cli(
            "--repo-root",
            str(REPOSITORY_FIXTURE),
            "validate",
            "--root",
            "docs/specs",
            cwd=TEST_DIR.parents[4],
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")

    def test_global_option_after_subcommand_is_usage_failure(self) -> None:
        result = run_cli(
            "validate",
            "--repo-root",
            str(REPOSITORY_FIXTURE),
            "--root",
            "docs/specs",
        )
        self.assertEqual(result.returncode, 2)

    def test_repo_discovery_accepts_git_directory_and_file(self) -> None:
        for git_kind in ("directory", "file"):
            with self.subTest(git_kind=git_kind), TemporaryDirectory() as temporary:
                repo = Path(temporary) / "overlay"
                shutil.copytree(REPOSITORY_FIXTURE, repo)
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
        result = run_cli(
            "--repo-root",
            str(REPOSITORY_FIXTURE),
            "validate",
            "--root",
            "docs/specs",
            "--baseline-ref",
            "HEAD",
        )
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
