from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path
import hashlib
import shutil
import tempfile
import unittest


TEST_DIR = Path(__file__).resolve().parent
SCRIPT_DIR = TEST_DIR.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import spec_model  # noqa: E402


class SpecBundleModelTest(unittest.TestCase):
    def test_loads_root_members_statements_and_deterministic_hash(self) -> None:
        fixture = TEST_DIR / "fixtures/spec-bundle/valid-multi-file"
        loader = getattr(spec_model, "load_spec_bundle", None)

        self.assertIsNotNone(loader, "load_spec_bundle must exist")
        bundle, diagnostics = loader(fixture, TEST_DIR)

        self.assertEqual(diagnostics, ())
        self.assertIsNotNone(bundle)
        assert bundle is not None
        self.assertEqual(bundle.metadata.schema, "forge/spec@3")
        self.assertEqual(
            bundle.path.as_posix(),
            "fixtures/spec-bundle/valid-multi-file",
        )
        self.assertEqual(
            [member.role for member in bundle.members],
            ["root", "contract"],
        )
        self.assertEqual(
            [statement.kind for statement in bundle.statements],
            ["requirement", "acceptance"],
        )
        requirement, acceptance = bundle.statements
        self.assertEqual(
            (
                requirement.heading,
                requirement.member_path.as_posix(),
                requirement.line,
                requirement.references,
            ),
            (
                "Each bundle has exactly one root document",
                "fixtures/spec-bundle/valid-multi-file/semantic-spec-bundle-contract.md",
                20,
                (),
            ),
        )
        self.assertEqual(
            (
                acceptance.heading,
                acceptance.member_path.as_posix(),
                acceptance.line,
            ),
            (
                "A bundle with one declared root passes structural validation",
                "fixtures/spec-bundle/valid-multi-file/authoring-and-file-organization.md",
                5,
            ),
        )
        self.assertEqual(len(acceptance.references), 1)
        reference = acceptance.references[0]
        self.assertEqual(
            (
                reference.member_path.as_posix(),
                reference.heading,
                reference.anchor,
                reference.line,
            ),
            (
                "fixtures/spec-bundle/valid-multi-file/semantic-spec-bundle-contract.md",
                "Each bundle has exactly one root document",
                "each-bundle-has-exactly-one-root-document",
                9,
            ),
        )
        self.assertRegex(bundle.bundle_sha256, r"^[0-9a-f]{64}$")

        second_bundle, second_diagnostics = loader(fixture, TEST_DIR)
        self.assertEqual(second_diagnostics, ())
        self.assertEqual(second_bundle.bundle_sha256, bundle.bundle_sha256)

    def test_hash_uses_normalized_path_length_frames_and_exact_crlf_bytes(self) -> None:
        source = TEST_DIR / "fixtures/spec-bundle/valid-multi-file"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "docs/specs/semantic-spec-bundles"
            shutil.copytree(source, fixture)
            root_file = fixture / "semantic-spec-bundle-contract.md"
            root_file.write_bytes(root_file.read_bytes().replace(b"\n", b"\r\n"))

            bundle, diagnostics = spec_model.load_spec_bundle(fixture, root)

            self.assertEqual(diagnostics, ())
            self.assertIsNotNone(bundle)
            assert bundle is not None

            digest = hashlib.sha256()

            def add_frame(value: bytes) -> None:
                digest.update(len(value).to_bytes(8, "big"))
                digest.update(value)

            add_frame(b"docs/specs/semantic-spec-bundles")
            for member_path in sorted(fixture.glob("*.md"), key=lambda item: item.name):
                add_frame(member_path.name.encode("utf-8"))
                add_frame(member_path.read_bytes())

            self.assertEqual(bundle.bundle_sha256, digest.hexdigest())

    def test_allows_repeated_arbitrary_sections_and_preserves_exact_bytes(self) -> None:
        source = TEST_DIR / "fixtures/spec-bundle/valid-one-file"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "docs/specs/repeated-notes"
            shutil.copytree(source, fixture)
            root_file = fixture / "single-document-contract.md"
            exact_bytes = root_file.read_bytes().replace(
                b"## Decisions & History",
                b"## Notes\n\nFirst note.\n\n## Notes\n\nSecond note.\n\n## Decisions & History",
            ).replace(b"\n", b"\r\n")
            root_file.write_bytes(exact_bytes)

            bundle, diagnostics = spec_model.load_spec_bundle(fixture, root)

            self.assertEqual(diagnostics, ())
            self.assertIsNotNone(bundle)
            assert bundle is not None
            self.assertEqual(bundle.members[0].source_bytes, exact_bytes)
            self.assertEqual(bundle.members[0].source_text.encode("utf-8"), exact_bytes)
            self.assertEqual(bundle.members[0].section_order.count("Notes"), 2)

    def test_ignores_documents_and_verifies_markers_inside_fenced_code(self) -> None:
        source = TEST_DIR / "fixtures/spec-bundle/valid-one-file"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "docs/specs/fenced-examples"
            shutil.copytree(source, fixture)
            root_file = fixture / "single-document-contract.md"
            text = root_file.read_text(encoding="utf-8")
            text = text.replace(
                "- root: [Single Document Contract](single-document-contract.md)",
                "- root: [Single Document Contract](single-document-contract.md)\n\n"
                "```markdown\n"
                "## Documents\n\n"
                "- root: [Escaped Document](../escaped-document.md)\n"
                "```",
            )
            text = text.replace(
                "Verifies:\n\n- [A single-file bundle is a valid bundle](single-document-contract.md#a-single-file-bundle-is-a-valid-bundle)",
                "```markdown\n"
                "Verifies:\n\n"
                "- [Escaped requirement](../escaped-document.md#escaped-requirement)\n"
                "```\n\n"
                "Verifies:\n\n"
                "- [A single-file bundle is a valid bundle](single-document-contract.md#a-single-file-bundle-is-a-valid-bundle)",
            )
            root_file.write_text(text, encoding="utf-8")

            bundle, diagnostics = spec_model.load_spec_bundle(fixture, root)

            self.assertEqual(diagnostics, ())
            self.assertIsNotNone(bundle)
            assert bundle is not None
            acceptance = next(
                statement for statement in bundle.statements if statement.kind == "acceptance"
            )
            self.assertEqual(len(acceptance.references), 1)
            self.assertEqual(
                acceptance.references[0].member_path,
                bundle.path / "single-document-contract.md",
            )

    def test_inventory_declares_every_markdown_member_exactly_once(self) -> None:
        source = TEST_DIR / "fixtures/spec-bundle/valid-multi-file"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            duplicate = root / "docs/specs/duplicate-member"
            shutil.copytree(source, duplicate)
            root_file = duplicate / "semantic-spec-bundle-contract.md"
            text = root_file.read_text(encoding="utf-8")
            text = text.replace(
                "- contract: [Bundle Validation Outcomes](authoring-and-file-organization.md)",
                "- contract: [Bundle Validation Outcomes](authoring-and-file-organization.md)\n"
                "- reference: [Bundle Validation Outcomes](authoring-and-file-organization.md)",
            )
            root_file.write_text(text, encoding="utf-8")

            bundle, diagnostics = spec_model.load_spec_bundle(duplicate, root)

            self.assertIsNone(bundle)
            self.assertIn("BUNDLE_DOCUMENT_DUPLICATE", {item.code for item in diagnostics})

            undeclared = root / "docs/specs/undeclared-member"
            shutil.copytree(source, undeclared)
            (undeclared / "supporting-context.md").write_text(
                "# Supporting Context\n\nNo contract statements.\n",
                encoding="utf-8",
            )

            bundle, diagnostics = spec_model.load_spec_bundle(undeclared, root)

            self.assertIsNone(bundle)
            self.assertIn("BUNDLE_DOCUMENT_UNDECLARED", {item.code for item in diagnostics})

    def test_hash_is_order_independent_and_changes_for_identity_path_or_bytes(self) -> None:
        fixture = TEST_DIR / "fixtures/spec-bundle/valid-multi-file"
        bundle, diagnostics = spec_model.load_spec_bundle(fixture, TEST_DIR)
        self.assertEqual(diagnostics, ())
        self.assertIsNotNone(bundle)
        assert bundle is not None
        baseline = bundle.bundle_sha256

        self.assertEqual(
            spec_model.bundle_sha256(bundle.path, tuple(reversed(bundle.members))),
            baseline,
        )
        changed_bytes = replace(
            bundle.members[0],
            source_bytes=bundle.members[0].source_bytes + b"\n",
        )
        self.assertNotEqual(
            spec_model.bundle_sha256(bundle.path, (changed_bytes, *bundle.members[1:])),
            baseline,
        )
        changed_member_path = replace(
            bundle.members[0],
            path=bundle.path / "renamed-contract.md",
        )
        self.assertNotEqual(
            spec_model.bundle_sha256(bundle.path, (changed_member_path, *bundle.members[1:])),
            baseline,
        )
        renamed_bundle_path = Path("docs/specs/renamed-bundle")
        renamed_members = tuple(
            replace(member, path=renamed_bundle_path / member.path.name)
            for member in bundle.members
        )
        self.assertNotEqual(
            spec_model.bundle_sha256(renamed_bundle_path, renamed_members),
            baseline,
        )

    def test_hash_rejects_non_normalized_or_non_relative_paths(self) -> None:
        fixture = TEST_DIR / "fixtures/spec-bundle/valid-multi-file"
        bundle, diagnostics = spec_model.load_spec_bundle(fixture, TEST_DIR)
        self.assertEqual(diagnostics, ())
        self.assertIsNotNone(bundle)
        assert bundle is not None

        invalid_bundle_paths = (
            Path("/docs/specs/absolute-bundle"),
            Path("docs/specs/../escaped-bundle"),
        )
        for invalid_path in invalid_bundle_paths:
            with self.subTest(bundle_path=invalid_path), self.assertRaises(ValueError):
                spec_model.bundle_sha256(invalid_path, bundle.members)

        outside_member = replace(bundle.members[0], path=Path("docs/outside.md"))
        with self.assertRaises(ValueError):
            spec_model.bundle_sha256(bundle.path, (outside_member, *bundle.members[1:]))
        absolute_member = replace(bundle.members[0], path=Path("/tmp/outside.md"))
        with self.assertRaises(ValueError):
            spec_model.bundle_sha256(bundle.path, (absolute_member, *bundle.members[1:]))

    def test_parses_one_file_and_five_file_bundle_boundaries(self) -> None:
        cases = (
            ("valid-one-file", 1, ["root"], 2),
            (
                "valid-five-file",
                5,
                ["root", "contract", "acceptance", "history", "reference"],
                2,
            ),
        )
        for fixture_name, member_count, roles, statement_count in cases:
            with self.subTest(fixture=fixture_name):
                fixture = TEST_DIR / "fixtures/spec-bundle" / fixture_name
                bundle, diagnostics = spec_model.load_spec_bundle(fixture, TEST_DIR)
                self.assertEqual(diagnostics, ())
                self.assertIsNotNone(bundle)
                assert bundle is not None
                self.assertEqual(len(bundle.members), member_count)
                self.assertEqual([member.role for member in bundle.members], roles)
                self.assertEqual(len(bundle.statements), statement_count)
                self.assertEqual(len({member.path for member in bundle.members}), member_count)
                if fixture_name == "valid-five-file":
                    supporting_context = bundle.members[-1]
                    self.assertEqual(
                        supporting_context.mermaid,
                        (
                            spec_model.MermaidBlock(
                                text='flowchart LR\n    ROOT["Bundle root"] --> MEMBER["Declared member"]',
                                line=9,
                                section="Runtime Map",
                            ),
                        ),
                    )

    def test_parses_korean_reference_label_and_exact_statement_metadata(self) -> None:
        source = TEST_DIR / "fixtures/spec-bundle/valid-one-file"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "docs/specs/korean-contract"
            shutil.copytree(source, fixture)
            root_file = fixture / "single-document-contract.md"
            text = root_file.read_text(encoding="utf-8")
            replacements = {
                "language: en": "language: ko",
                "A single-file bundle is a valid bundle": "단일 파일도 하나의 유효한 번들이다",
                "A declared requirement has a matching acceptance statement": "선언된 요구사항은 대응하는 인수 문장을 가진다",
                "Verifies:": "검증하는 요구사항:",
                "#a-single-file-bundle-is-a-valid-bundle": "#단일-파일도-하나의-유효한-번들이다",
            }
            for old, new in replacements.items():
                text = text.replace(old, new)
            root_file.write_text(text, encoding="utf-8")

            bundle, diagnostics = spec_model.load_spec_bundle(fixture, root)

            self.assertEqual(diagnostics, ())
            self.assertIsNotNone(bundle)
            assert bundle is not None
            requirement, acceptance = bundle.statements
            self.assertEqual(requirement.heading, "단일 파일도 하나의 유효한 번들이다")
            self.assertEqual(acceptance.heading, "선언된 요구사항은 대응하는 인수 문장을 가진다")
            self.assertEqual(
                acceptance.references,
                (
                    spec_model.StatementReference(
                        member_path=bundle.path / "single-document-contract.md",
                        heading="단일 파일도 하나의 유효한 번들이다",
                        anchor="단일-파일도-하나의-유효한-번들이다",
                        line=29,
                    ),
                ),
            )

    def test_rejects_parent_traversal_and_symlink_escape_before_member_read(self) -> None:
        source = TEST_DIR / "fixtures/spec-bundle/valid-one-file"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            traversal = root / "docs/specs/parent-traversal"
            shutil.copytree(source, traversal)
            root_file = traversal / "single-document-contract.md"
            text = root_file.read_text(encoding="utf-8").replace(
                "- root: [Single Document Contract](single-document-contract.md)",
                "- root: [Single Document Contract](single-document-contract.md)\n"
                "- reference: [Outside](../outside.md)",
            )
            root_file.write_text(text, encoding="utf-8")

            bundle, diagnostics = spec_model.load_spec_bundle(traversal, root)

            self.assertIsNone(bundle)
            self.assertIn("BUNDLE_MEMBER_PATH", {item.code for item in diagnostics})

            symlink_bundle = root / "docs/specs/symlink-escape"
            shutil.copytree(source, symlink_bundle)
            symlink_root = symlink_bundle / "single-document-contract.md"
            symlink_text = symlink_root.read_text(encoding="utf-8").replace(
                "- root: [Single Document Contract](single-document-contract.md)",
                "- root: [Single Document Contract](single-document-contract.md)\n"
                "- reference: [Outside](outside.md)",
            )
            symlink_root.write_text(symlink_text, encoding="utf-8")
            outside = root / "outside.md"
            outside.write_text("# Outside\n", encoding="utf-8")
            (symlink_bundle / "outside.md").symlink_to(outside)

            bundle, diagnostics = spec_model.load_spec_bundle(symlink_bundle, root)

            self.assertIsNone(bundle)
            self.assertIn("BUNDLE_MEMBER_PATH", {item.code for item in diagnostics})


if __name__ == "__main__":
    unittest.main()
