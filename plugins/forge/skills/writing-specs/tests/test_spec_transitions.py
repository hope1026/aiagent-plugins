from __future__ import annotations

from dataclasses import FrozenInstanceError
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from spec_transitions import (
    SpecTransition,
    TransitionManifest,
    load_transition_manifest,
)


class TransitionManifestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / "repo"
        self.spec_root = Path("docs/specs")
        (self.repo / self.spec_root).mkdir(parents=True)
        (self.repo / "docs/specs/001-current").mkdir(parents=True)
        (self.repo / "docs/specs/001-current/spec.md").write_text("current")
        (self.repo / "docs/plans/001-history").mkdir(parents=True)
        (self.repo / "docs/plans/001-history/evidence.md").write_text("evidence")

    def record(self, **overrides: object) -> dict[str, object]:
        record: dict[str, object] = {
            "fromId": "001-old",
            "fromPath": "docs/specs/001-old/spec.md",
            "fromSourceSha256": "a" * 64,
            "disposition": "superseded",
            "toId": "001-current",
            "toPath": "docs/specs/001-current/spec.md",
            "evidencePath": "docs/plans/001-history/evidence.md",
            "reason": "Keep the active spec limited to current facts.",
        }
        record.update(overrides)
        return record

    def source(self, record: dict[str, object] | None = None) -> bytes:
        payload = {
            "schema": "forge/spec-transitions@1",
            "transitions": [record if record is not None else self.record()],
        }
        return json.dumps(payload, separators=(",", ":")).encode("utf-8")

    def codes(self, source: bytes) -> set[str]:
        _, diagnostics = load_transition_manifest(
            self.repo, self.spec_root, source=source
        )
        return {item.code for item in diagnostics}

    def test_valid_manifest_returns_frozen_typed_model(self) -> None:
        manifest, diagnostics = load_transition_manifest(
            self.repo, self.spec_root, source=self.source()
        )

        self.assertEqual(diagnostics, ())
        self.assertEqual(
            manifest,
            TransitionManifest(
                transitions=(
                    SpecTransition(
                        from_id="001-old",
                        from_path=Path("docs/specs/001-old/spec.md"),
                        from_source_sha256="a" * 64,
                        disposition="superseded",
                        to_id="001-current",
                        to_path=Path("docs/specs/001-current/spec.md"),
                        evidence_path=Path("docs/plans/001-history/evidence.md"),
                        reason="Keep the active spec limited to current facts.",
                    ),
                )
            ),
        )
        assert manifest is not None
        with self.assertRaises(FrozenInstanceError):
            manifest.transitions = ()  # type: ignore[misc]

    def test_missing_manifest_is_an_optional_absent_value(self) -> None:
        manifest, diagnostics = load_transition_manifest(self.repo, self.spec_root)
        self.assertIsNone(manifest)
        self.assertEqual(diagnostics, ())

    def test_manifest_file_is_read_when_source_is_not_supplied(self) -> None:
        path = self.repo / self.spec_root / ".transitions.json"
        path.write_bytes(self.source())

        manifest, diagnostics = load_transition_manifest(self.repo, self.spec_root)

        self.assertIsNotNone(manifest)
        self.assertEqual(diagnostics, ())

    def test_manifest_rejects_invalid_json_keys_and_types(self) -> None:
        invalid_cases = (
            (b"{", "SPEC_TRANSITION_JSON"),
            (
                b'{"schema":"forge/spec-transitions@1","schema":"x","transitions":[]}',
                "SPEC_TRANSITION_KEY",
            ),
            (
                b'{"schema":"forge/spec-transitions@1","transitions":{},"extra":1}',
                "SPEC_TRANSITION_KEY",
            ),
            (b'[]', "SPEC_TRANSITION_TYPE"),
            (
                b'{"schema":"forge/spec-transitions@1","transitions":{}}',
                "SPEC_TRANSITION_TYPE",
            ),
            (
                b'{"schema":"forge/spec-transitions@1","transitions":[1]}',
                "SPEC_TRANSITION_TYPE",
            ),
        )
        for source, code in invalid_cases:
            with self.subTest(code=code, source=source):
                self.assertIn(code, self.codes(source))

    def test_record_rejects_duplicate_unknown_missing_and_non_string_fields(self) -> None:
        valid_json = self.source().decode("utf-8")
        duplicate_record_key = valid_json.replace(
            '"fromId":"001-old"',
            '"fromId":"001-old","fromId":"001-other"',
        ).encode("utf-8")
        cases = (
            (duplicate_record_key, "SPEC_TRANSITION_KEY"),
            (self.source(self.record(extra="value")), "SPEC_TRANSITION_KEY"),
            (
                self.source(
                    {
                        key: value
                        for key, value in self.record().items()
                        if key != "reason"
                    }
                ),
                "SPEC_TRANSITION_KEY",
            ),
            (self.source(self.record(reason=7)), "SPEC_TRANSITION_TYPE"),
        )
        for source, code in cases:
            with self.subTest(code=code):
                self.assertIn(code, self.codes(source))

    def test_manifest_rejects_schema_disposition_hash_and_empty_strings(self) -> None:
        invalid_cases = (
            (
                json.dumps(
                    {"schema": "forge/spec-transitions@2", "transitions": []}
                ).encode(),
                "SPEC_TRANSITION_SCHEMA",
            ),
            (
                self.source(self.record(disposition="retired")),
                "SPEC_TRANSITION_DISPOSITION",
            ),
            (self.source(self.record(fromSourceSha256="A" * 64)), "SPEC_TRANSITION_SHA256"),
            (self.source(self.record(fromSourceSha256="a" * 63)), "SPEC_TRANSITION_SHA256"),
        )
        for source, code in invalid_cases:
            with self.subTest(code=code):
                self.assertIn(code, self.codes(source))

        for field in self.record():
            with self.subTest(empty_field=field):
                self.assertIn(
                    "SPEC_TRANSITION_VALUE",
                    self.codes(self.source(self.record(**{field: ""}))),
                )

    def test_record_paths_must_be_normalized_repository_relative_posix_paths(self) -> None:
        invalid_paths = (
            "/docs/specs/001-old/spec.md",
            "C:/docs/specs/001-old/spec.md",
            "//server/docs/specs/001-old/spec.md",
            r"docs\specs\001-old\spec.md",
            "docs/specs//001-old/spec.md",
            "docs/specs/./001-old/spec.md",
            "docs/specs/../001-old/spec.md",
            "docs/specs/001-old/spec.md/",
            "docs/specs/001-\x00old/spec.md",
        )
        for path in invalid_paths:
            with self.subTest(path=path):
                self.assertIn(
                    "SPEC_TRANSITION_PATH",
                    self.codes(self.source(self.record(fromPath=path))),
                )

    def test_record_paths_are_restricted_to_their_contract_roots(self) -> None:
        invalid_cases = (
            {"fromPath": "docs/plans/001-old/spec.md"},
            {"toPath": "docs/specs/001-current/other.md"},
            {"evidencePath": "docs/specs/001-current/spec.md"},
            {"evidencePath": "docs/other/evidence.md"},
        )
        for override in invalid_cases:
            with self.subTest(override=override):
                self.assertIn(
                    "SPEC_TRANSITION_PATH",
                    self.codes(self.source(self.record(**override))),
                )

    def test_record_paths_reject_existing_symlink_components(self) -> None:
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (outside / "spec.md").write_text("outside")
        (self.repo / "docs/specs/002-linked").symlink_to(outside, target_is_directory=True)

        self.assertIn(
            "SPEC_TRANSITION_PATH_SYMLINK",
            self.codes(
                self.source(
                    self.record(toId="002-linked", toPath="docs/specs/002-linked/spec.md")
                )
            ),
        )

        evidence = self.repo / "docs/plans/001-history/evidence.md"
        evidence.unlink()
        evidence.symlink_to(outside / "spec.md")
        self.assertIn(
            "SPEC_TRANSITION_PATH_SYMLINK",
            self.codes(self.source()),
        )

    def test_evidence_path_must_be_an_existing_regular_file(self) -> None:
        missing = self.source(
            self.record(evidencePath="docs/evidence/missing/evidence.md")
        )
        self.assertIn("SPEC_TRANSITION_EVIDENCE", self.codes(missing))

        directory = self.repo / "docs/evidence/directory"
        directory.mkdir(parents=True)
        self.assertIn(
            "SPEC_TRANSITION_EVIDENCE",
            self.codes(
                self.source(self.record(evidencePath="docs/evidence/directory"))
            ),
        )

    def test_manifest_path_must_be_a_regular_non_symlink_file(self) -> None:
        target = self.repo / "manifest-target.json"
        target.write_bytes(self.source())
        manifest_path = self.repo / self.spec_root / ".transitions.json"
        manifest_path.symlink_to(target)

        manifest, diagnostics = load_transition_manifest(self.repo, self.spec_root)

        self.assertIsNone(manifest)
        self.assertEqual(
            {item.code for item in diagnostics},
            {"SPEC_TRANSITION_MANIFEST_PATH"},
        )

    def test_invalid_utf8_and_unreadable_manifest_shape_are_diagnostics(self) -> None:
        self.assertIn("SPEC_TRANSITION_JSON", self.codes(b"\xff"))

        manifest_path = self.repo / self.spec_root / ".transitions.json"
        manifest_path.mkdir()
        manifest, diagnostics = load_transition_manifest(self.repo, self.spec_root)
        self.assertIsNone(manifest)
        self.assertEqual(
            {item.code for item in diagnostics},
            {"SPEC_TRANSITION_MANIFEST_PATH"},
        )

    def test_diagnostics_are_deterministically_sorted(self) -> None:
        source = self.source(
            self.record(
                fromId="",
                fromPath="docs/specs/../old/spec.md",
                fromSourceSha256="BAD",
                disposition="retired",
                reason="",
            )
        )

        _, first = load_transition_manifest(
            self.repo, self.spec_root, source=source
        )
        _, second = load_transition_manifest(
            self.repo, self.spec_root, source=source
        )

        self.assertEqual(first, tuple(sorted(first)))
        self.assertEqual(first, second)
        self.assertTrue(
            all(item.path == "docs/specs/.transitions.json" for item in first)
        )


if __name__ == "__main__":
    unittest.main()
