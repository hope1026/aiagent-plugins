from __future__ import annotations

from dataclasses import FrozenInstanceError
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from spec_transitions import (
    SpecBundleTransition,
    TransitionManifest,
    load_transition_manifest,
)


class TransitionManifestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / "repo"
        self.spec_root = Path("docs/specs")
        (self.repo / self.spec_root / "current-contract").mkdir(parents=True)
        (self.repo / self.spec_root / "current-contract/current-contract.md").write_text(
            "current", encoding="utf-8"
        )
        (self.repo / "docs/evidence").mkdir(parents=True)
        (self.repo / "docs/evidence/semantic-bundle-migration.md").write_text(
            "evidence", encoding="utf-8"
        )

    def record(self, **overrides: object) -> dict[str, object]:
        record: dict[str, object] = {
            "fromSourcePath": "docs/specs/prior-contract",
            "fromSourceSha256": "a" * 64,
            "disposition": "superseded",
            "toBundlePath": "docs/specs/current-contract",
            "evidencePath": "docs/evidence/semantic-bundle-migration.md",
            "reason": "Replace the prior bundle with the current contract boundary.",
        }
        record.update(overrides)
        return record

    def source(
        self,
        record: dict[str, object] | None = None,
        *,
        records: list[dict[str, object]] | None = None,
    ) -> bytes:
        payload = {
            "schema": "forge/spec-bundle-transitions@1",
            "transitions": records
            if records is not None
            else [record if record is not None else self.record()],
        }
        return json.dumps(payload, separators=(",", ":")).encode("utf-8")

    def diagnostics(self, source: bytes):
        _, diagnostics = load_transition_manifest(
            self.repo, self.spec_root, source=source
        )
        return diagnostics

    def codes(self, source: bytes) -> set[str]:
        return {item.code for item in self.diagnostics(source)}

    def test_valid_manifest_returns_frozen_path_only_model(self) -> None:
        manifest, diagnostics = load_transition_manifest(
            self.repo, self.spec_root, source=self.source()
        )

        self.assertEqual(diagnostics, ())
        self.assertEqual(
            manifest,
            TransitionManifest(
                transitions=(
                    SpecBundleTransition(
                        from_source_path=Path("docs/specs/prior-contract"),
                        from_source_sha256="a" * 64,
                        disposition="superseded",
                        to_bundle_path=Path("docs/specs/current-contract"),
                        evidence_path=Path(
                            "docs/evidence/semantic-bundle-migration.md"
                        ),
                        reason="Replace the prior bundle with the current contract boundary.",
                    ),
                )
            ),
        )
        assert manifest is not None
        with self.assertRaises(FrozenInstanceError):
            manifest.transitions = ()  # type: ignore[misc]

    def test_missing_manifest_is_optional_and_new_filename_is_read(self) -> None:
        manifest, diagnostics = load_transition_manifest(self.repo, self.spec_root)
        self.assertIsNone(manifest)
        self.assertEqual(diagnostics, ())

        path = self.repo / self.spec_root / ".bundle-transitions.json"
        path.write_bytes(self.source())
        manifest, diagnostics = load_transition_manifest(self.repo, self.spec_root)
        self.assertIsNotNone(manifest)
        self.assertEqual(diagnostics, ())

    def test_manifest_rejects_invalid_json_duplicate_unknown_missing_and_types(self) -> None:
        valid_json = self.source().decode("utf-8")
        duplicate_record_key = valid_json.replace(
            '"fromSourcePath":"docs/specs/prior-contract"',
            '"fromSourcePath":"docs/specs/prior-contract",'
            '"fromSourcePath":"docs/specs/other-contract"',
        ).encode("utf-8")
        missing_reason = {
            key: value for key, value in self.record().items() if key != "reason"
        }
        cases = (
            (b"{", "SPEC_TRANSITION_JSON"),
            (
                b'{"schema":"forge/spec-bundle-transitions@1","schema":"x","transitions":[]}',
                "SPEC_TRANSITION_KEY",
            ),
            (
                b'{"schema":"forge/spec-bundle-transitions@1","transitions":[],"extra":1}',
                "SPEC_TRANSITION_KEY",
            ),
            (b"[]", "SPEC_TRANSITION_TYPE"),
            (
                b'{"schema":"forge/spec-bundle-transitions@1","transitions":{}}',
                "SPEC_TRANSITION_TYPE",
            ),
            (
                b'{"schema":"forge/spec-bundle-transitions@1","transitions":[1]}',
                "SPEC_TRANSITION_TYPE",
            ),
            (duplicate_record_key, "SPEC_TRANSITION_KEY"),
            (self.source(self.record(extra="value")), "SPEC_TRANSITION_KEY"),
            (self.source(missing_reason), "SPEC_TRANSITION_KEY"),
            (self.source(self.record(reason=7)), "SPEC_TRANSITION_TYPE"),
        )
        for source, code in cases:
            with self.subTest(code=code, source=source):
                self.assertIn(code, self.codes(source))

    def test_unknown_identity_fields_are_rejected_and_path_fields_are_required(self) -> None:
        invalid = {
            "sourceIdentity": "prior-contract",
            "source": "docs/specs/prior-contract",
            "fromSourceSha256": "a" * 64,
            "disposition": "superseded",
            "targetIdentity": "current-contract",
            "target": "docs/specs/current-contract",
            "evidencePath": "docs/evidence/semantic-bundle-migration.md",
            "reason": "invalid key shape",
        }
        diagnostics = self.diagnostics(self.source(invalid))
        messages = "\n".join(item.message for item in diagnostics)
        self.assertIn("sourceIdentity", messages)
        self.assertIn("targetIdentity", messages)
        self.assertIn("fromSourcePath", messages)
        self.assertIn("toBundlePath", messages)

    def test_manifest_rejects_schema_disposition_hash_and_empty_strings(self) -> None:
        invalid_cases = (
            (
                json.dumps(
                    {"schema": "forge/spec-bundle-transitions@2", "transitions": []}
                ).encode(),
                "SPEC_TRANSITION_SCHEMA",
            ),
            (
                self.source(self.record(disposition="retired")),
                "SPEC_TRANSITION_DISPOSITION",
            ),
            (
                self.source(self.record(fromSourceSha256="A" * 64)),
                "SPEC_TRANSITION_SHA256",
            ),
            (
                self.source(self.record(fromSourceSha256="a" * 63)),
                "SPEC_TRANSITION_SHA256",
            ),
        )
        for source, code in invalid_cases:
            with self.subTest(code=code):
                self.assertIn(code, self.codes(source))

        for field in self.record():
            with self.subTest(empty_field=field):
                self.assertIn(
                    "SPEC_TRANSITION_VALUE",
                    self.codes(self.source(self.record(**{field: " \t"}))),
                )

    def test_record_paths_must_be_normalized_repository_relative_posix_paths(self) -> None:
        invalid_paths = (
            "/docs/specs/prior-contract",
            "C:/docs/specs/prior-contract",
            "//server/docs/specs/prior-contract",
            r"docs\specs\prior-contract",
            "docs/specs//prior-contract",
            "docs/specs/./prior-contract",
            "docs/specs/../prior-contract",
            "docs/specs/prior-contract/",
            "docs/specs/prior-\x00contract",
        )
        for path in invalid_paths:
            with self.subTest(path=path):
                self.assertIn(
                    "SPEC_TRANSITION_PATH",
                    self.codes(
                        self.source(self.record(fromSourcePath=path))
                    ),
                )

    def test_source_and_target_paths_have_exact_semantic_bundle_layouts(self) -> None:
        invalid_cases = (
            {"fromSourcePath": "docs/specs/prior-contract/nested"},
            {"fromSourcePath": "docs/specs/prior_contract"},
            {"fromSourcePath": "docs/plans/prior-contract"},
            {"toBundlePath": "docs/specs/current-contract/current-contract.md"},
            {"toBundlePath": "docs/specs/current-contract/nested"},
            {"toBundlePath": "docs/plans/current-contract"},
            {"toBundlePath": "docs/specs/004-current-contract"},
            {"toBundlePath": "docs/specs/Current-Contract"},
            {"toBundlePath": "docs/specs/current_contract"},
            {"evidencePath": "docs/specs/current-contract/current-contract.md"},
            {"evidencePath": "docs/other/evidence.md"},
        )
        for override in invalid_cases:
            with self.subTest(override=override):
                self.assertIn(
                    "SPEC_TRANSITION_PATH",
                    self.codes(self.source(self.record(**override))),
                )

    def test_source_path_accepts_a_semantic_bundle_directory(self) -> None:
        manifest, diagnostics = load_transition_manifest(
            self.repo,
            self.spec_root,
            source=self.source(
                self.record(fromSourcePath="docs/specs/prior-contract")
            ),
        )

        self.assertEqual(diagnostics, ())
        self.assertEqual(
            manifest.transitions[0].from_source_path,
            Path("docs/specs/prior-contract"),
        )

    def test_duplicate_sources_and_targets_are_rejected(self) -> None:
        other = self.record(
            fromSourcePath="docs/specs/another-prior",
            toBundlePath="docs/specs/another-current",
        )
        duplicate_source = dict(
            other,
            fromSourcePath="docs/specs/prior-contract",
        )
        duplicate_target = dict(other, toBundlePath="docs/specs/current-contract")

        self.assertIn(
            "SPEC_TRANSITION_DUPLICATE",
            self.codes(self.source(records=[self.record(), duplicate_source])),
        )
        self.assertIn(
            "SPEC_TRANSITION_DUPLICATE",
            self.codes(self.source(records=[self.record(), duplicate_target])),
        )

    def test_valid_merged_group_reuses_target_and_evidence(self) -> None:
        records = [
            self.record(
                fromSourcePath=f"docs/specs/prior-{index}",
                fromSourceSha256=str(index) * 64,
                disposition="merged",
                reason="Consolidate exact active contracts.",
            )
            for index in (1, 2, 3)
        ]

        manifest, diagnostics = load_transition_manifest(
            self.repo, self.spec_root, source=self.source(records=records)
        )

        self.assertEqual(diagnostics, ())
        self.assertIsNotNone(manifest)
        assert manifest is not None
        self.assertEqual(len(manifest.transitions), 3)

    def test_invalid_merge_groups_are_rejected(self) -> None:
        merged = self.record(
            fromSourcePath="docs/specs/prior-a",
            disposition="merged",
        )
        cases = (
            ([merged], "SPEC_TRANSITION_MERGE_GROUP"),
            (
                [
                    merged,
                    self.record(fromSourcePath="docs/specs/prior-b"),
                ],
                "SPEC_TRANSITION_DUPLICATE",
            ),
            (
                [
                    merged,
                    self.record(
                        fromSourcePath="docs/specs/prior-b",
                        disposition="merged",
                        evidencePath="docs/evidence/other.md",
                    ),
                ],
                "SPEC_TRANSITION_MERGE_GROUP",
            ),
        )
        (self.repo / "docs/evidence/other.md").write_text(
            "other", encoding="utf-8"
        )

        for records, expected_code in cases:
            with self.subTest(records=records):
                self.assertIn(
                    expected_code,
                    self.codes(self.source(records=records)),
                )

    def test_record_paths_reject_existing_symlink_components(self) -> None:
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (outside / "contract.md").write_text("outside", encoding="utf-8")
        (self.repo / "docs/specs/linked-contract").symlink_to(
            outside, target_is_directory=True
        )

        self.assertIn(
            "SPEC_TRANSITION_PATH_SYMLINK",
            self.codes(
                self.source(
                    self.record(fromSourcePath="docs/specs/linked-contract")
                )
            ),
        )
        self.assertIn(
            "SPEC_TRANSITION_PATH_SYMLINK",
            self.codes(
                self.source(
                    self.record(toBundlePath="docs/specs/linked-contract")
                )
            ),
        )

        evidence = self.repo / "docs/evidence/semantic-bundle-migration.md"
        evidence.unlink()
        evidence.symlink_to(outside / "contract.md")
        self.assertIn("SPEC_TRANSITION_PATH_SYMLINK", self.codes(self.source()))

    def test_evidence_path_must_be_an_existing_regular_file(self) -> None:
        self.assertIn(
            "SPEC_TRANSITION_EVIDENCE",
            self.codes(
                self.source(
                    self.record(evidencePath="docs/evidence/missing-evidence.md")
                )
            ),
        )

        directory = self.repo / "docs/evidence/directory"
        directory.mkdir()
        self.assertIn(
            "SPEC_TRANSITION_EVIDENCE",
            self.codes(
                self.source(self.record(evidencePath="docs/evidence/directory"))
            ),
        )

    def test_manifest_path_must_be_a_regular_non_symlink_file(self) -> None:
        target = self.repo / "manifest-target.json"
        target.write_bytes(self.source())
        manifest_path = self.repo / self.spec_root / ".bundle-transitions.json"
        manifest_path.symlink_to(target)

        manifest, diagnostics = load_transition_manifest(self.repo, self.spec_root)

        self.assertIsNone(manifest)
        self.assertEqual(
            {item.code for item in diagnostics},
            {"SPEC_TRANSITION_MANIFEST_PATH"},
        )

    def test_invalid_utf8_and_non_regular_manifest_are_diagnostics(self) -> None:
        self.assertIn("SPEC_TRANSITION_JSON", self.codes(b"\xff"))

        manifest_path = self.repo / self.spec_root / ".bundle-transitions.json"
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
                fromSourcePath="docs/specs/../prior-contract",
                fromSourceSha256="BAD",
                disposition="retired",
                reason="",
            )
        )

        first = self.diagnostics(source)
        second = self.diagnostics(source)

        self.assertEqual(first, tuple(sorted(first)))
        self.assertEqual(first, second)
        self.assertTrue(
            all(
                item.path == "docs/specs/.bundle-transitions.json"
                for item in first
            )
        )


if __name__ == "__main__":
    unittest.main()
