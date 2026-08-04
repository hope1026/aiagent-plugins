from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

from spec_model import load_spec, parse_frontmatter


ROOT = Path(__file__).parent / "fixtures" / "spec-model"
CANONICAL_SECTIONS = (
    "Overview",
    "Requirements",
    "Behavior & Flows",
    "Data & Interfaces",
    "Acceptance Criteria",
    "Decisions & History",
)


class SpecModelTest(unittest.TestCase):
    def test_valid_ko_contract(self) -> None:
        path = ROOT / "001-valid-ko" / "spec.md"
        doc, errors = load_spec(path, ROOT)

        self.assertEqual(errors, ())
        self.assertIsNotNone(doc)
        assert doc is not None
        self.assertEqual(doc.path, Path("001-valid-ko/spec.md"))
        self.assertEqual(doc.metadata.schema, "forge/spec@2")
        self.assertIsNone(doc.metadata.subtype)
        self.assertEqual(doc.metadata.id, "001-valid-ko")
        self.assertEqual(doc.metadata.status, "approved")
        self.assertEqual(doc.metadata.language, "ko")
        self.assertEqual(doc.metadata.kind, "feature")
        self.assertEqual(doc.metadata.areas, ("forge",))
        self.assertEqual(doc.metadata.components, ("spec-model",))
        self.assertEqual(
            [(item.id, item.relation) for item in doc.metadata.related_specs],
            [("002-example", "relatedTo")],
        )
        self.assertEqual(doc.title, "구조화 스펙 예제")
        self.assertEqual(tuple(doc.sections), CANONICAL_SECTIONS)
        self.assertEqual([item.id for item in doc.requirements], ["R1", "R2"])
        self.assertFalse(doc.requirements[0].removed)
        self.assertTrue(doc.requirements[1].removed)
        self.assertEqual(doc.acceptance[0].requirements, ("R1", "R2"))
        self.assertEqual(len(doc.mermaid), 1)
        self.assertEqual(doc.mermaid[0].section, "Behavior & Flows")
        self.assertEqual(doc.mermaid[0].text, "flowchart TD\n    A[입력] --> B[검증]")
        self.assertEqual(doc.mermaid[0].line, 24)
        self.assertEqual(doc.source_sha256, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_frontmatter_parser_uses_json_collections(self) -> None:
        path = ROOT / "001-valid-ko" / "spec.md"
        metadata, body_start, errors = parse_frontmatter(path.read_text(), path)

        self.assertEqual(errors, ())
        self.assertEqual(body_start, 10)
        self.assertEqual(metadata["areas"], ["forge"])
        self.assertEqual(
            metadata["relatedSpecs"],
            [{"id": "002-example", "relation": "relatedTo"}],
        )

    def test_v2_accepts_flexible_narrative_sections(self) -> None:
        path = ROOT / "002-flexible-api" / "spec.md"
        document, diagnostics = load_spec(path, ROOT)

        self.assertEqual(diagnostics, ())
        self.assertIsNotNone(document)
        assert document is not None
        self.assertEqual(document.metadata.schema, "forge/spec@2")
        self.assertEqual(document.metadata.subtype, "api")
        self.assertEqual(
            document.section_order,
            (
                "Problem",
                "Endpoints",
                "Requirements",
                "Examples",
                "Acceptance Criteria",
                "Decisions & History",
            ),
        )
        self.assertEqual([block.section for block in document.mermaid], ["Endpoints"])

    def test_v2_preserves_workflow_section_order(self) -> None:
        path = ROOT / "003-flexible-workflow" / "spec.md"
        document, diagnostics = load_spec(path, ROOT)

        self.assertEqual(diagnostics, ())
        self.assertIsNotNone(document)
        assert document is not None
        self.assertEqual(document.metadata.subtype, "workflow")
        self.assertEqual(
            document.section_order,
            (
                "Actors",
                "Requirements",
                "State Transitions",
                "Acceptance Criteria",
                "Decisions & History",
                "Operational Notes",
            ),
        )
        self.assertEqual([block.section for block in document.mermaid], ["State Transitions"])

    def test_invalid_matrix_has_stable_codes(self) -> None:
        expected = {
            "wrong-schema": "SPEC_SCHEMA",
            "id-path": "SPEC_ID_PATH",
            "duplicate-section": "SPEC_SECTION_DUPLICATE",
            "missing-heading": "SPEC_SECTION_MISSING",
            "implicit-yaml": "SPEC_FRONTMATTER_VALUE",
            "anchor": "SPEC_FRONTMATTER_VALUE",
            "tag": "SPEC_FRONTMATTER_VALUE",
            "block-scalar": "SPEC_FRONTMATTER_VALUE",
            "duplicate-r": "SPEC_REQUIREMENT_DUPLICATE",
            "duplicate-ac": "SPEC_AC_DUPLICATE",
            "bad-tombstone": "SPEC_REQUIREMENT_TOMBSTONE",
            "implemented-clarification": "SPEC_CLARIFICATION_STATUS",
            "unsupported-locale": "SPEC_LANGUAGE",
            "unsupported-status": "SPEC_STATUS",
            "unsupported-kind": "SPEC_KIND",
            "invalid-subtype": "SPEC_SUBTYPE",
            "missing-key": "SPEC_FRONTMATTER_KEY",
            "extra-key": "SPEC_FRONTMATTER_KEY",
            "scalar-type": "SPEC_FRONTMATTER_TYPE",
            "body-status": "SPEC_STATUS_BODY",
            "requirement-sequence": "SPEC_REQUIREMENT_SEQUENCE",
            "ac-sequence": "SPEC_AC_SEQUENCE",
        }
        for case, code in expected.items():
            with self.subTest(case=case):
                case_root = ROOT / "invalid" / case
                doc, errors = load_spec(case_root / "001-valid-ko" / "spec.md", case_root)
                self.assertIsNone(doc)
                self.assertIn(code, {error.code for error in errors})
                self.assertEqual(tuple(sorted(errors)), errors)

    def test_malformed_mermaid_is_preserved_for_authoritative_validator(self) -> None:
        case_root = ROOT / "invalid" / "malformed-mermaid"
        doc, errors = load_spec(case_root / "001-valid-ko" / "spec.md", case_root)

        self.assertEqual(errors, ())
        self.assertIsNotNone(doc)
        assert doc is not None
        self.assertEqual(doc.mermaid[0].text, "flowchart TD\n    A[입력] -->>")


if __name__ == "__main__":
    unittest.main()
