from __future__ import annotations

from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest

TEST_DIR = Path(__file__).resolve().parent
SCRIPTS = TEST_DIR.parent / "scripts"
FIXTURE = TEST_DIR / "fixtures" / "repository"
sys.path.insert(0, str(SCRIPTS))

from project_map import load_project_map  # noqa: E402


class ProjectMapTest(unittest.TestCase):
    def test_valid_map_preserves_human_authored_structure(self) -> None:
        project = load_project_map(FIXTURE / "docs/project/project-map.md", FIXTURE)
        self.assertEqual(project.title, "Demo Project")
        self.assertEqual(project.spec_paths, ("docs/specs/semantic-spec-bundles",))
        self.assertEqual(project.structure[0].path, "docs")
        self.assertEqual(project.structure[0].purpose, "사람이 읽는 프로젝트 문서를 보관한다.")
        self.assertIn("docs/project/project-map.md", project.structure[0].entry_points)
        self.assertEqual(
            project.structure[0].governing_statements[0].heading,
            "Every declared member enters the review source set exactly once",
        )
        self.assertEqual(
            project.structure[0].governing_statements[0].member_path,
            "docs/specs/semantic-spec-bundles/member-loading-and-provenance.md",
        )

    def test_missing_purpose_returns_path_qualified_diagnostic(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            shutil.copytree(FIXTURE, root)
            source = root / "docs/project/project-map.md"
            source.write_text(source.read_text().replace("**Purpose:** 사람이 읽는 프로젝트 문서를 보관한다.\n\n", ""))
            with self.assertRaisesRegex(ValueError, r"docs/project/project-map.md:.*Purpose"):
                load_project_map(source, root)

    def test_missing_entry_point_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            shutil.copytree(FIXTURE, root)
            source = root / "docs/project/project-map.md"
            source.write_text(source.read_text().replace("docs/project/project-map.md", "docs/project/missing.md", 1))
            with self.assertRaisesRegex(ValueError, r"Entry Point.*missing"):
                load_project_map(source, root)


if __name__ == "__main__":
    unittest.main()
