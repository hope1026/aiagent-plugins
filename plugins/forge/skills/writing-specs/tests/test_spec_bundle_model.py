from __future__ import annotations

import sys
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


if __name__ == "__main__":
    unittest.main()
