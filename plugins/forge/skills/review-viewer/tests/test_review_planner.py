from __future__ import annotations

from dataclasses import asdict, replace
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest


TEST_DIR = Path(__file__).resolve().parent
REPOSITORY = TEST_DIR / "fixtures" / "repository"
SCRIPTS = TEST_DIR.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from review_ir import build_semantic_ir  # noqa: E402
from review_planner import (  # noqa: E402
    ComponentPlan,
    ViewContext,
    select_presentation_plan,
    validate_presentation_plan,
)
from review_sources import collect_plan_sources, collect_spec_sources  # noqa: E402


class ReviewPlannerTest(unittest.TestCase):
    def workflow_ir(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        repository = Path(temporary.name)
        shutil.copytree(REPOSITORY, repository, dirs_exist_ok=True)
        source = repository / "docs/specs/008-alpha/spec.md"
        source.write_text(
            source.read_text(encoding="utf-8").replace(
                "kind: system", "kind: system\nsubtype: workflow", 1
            ),
            encoding="utf-8",
        )
        return build_semantic_ir(collect_spec_sources(source, (), repository))

    def test_workflow_approval_selects_state_first(self) -> None:
        context = ViewContext(
            "spec", "system", "workflow", "approval", "mixed", "ko", "standalone"
        )

        plan = select_presentation_plan(self.workflow_ir(), context)

        self.assertEqual(plan.profile, "spec.workflow")
        self.assertEqual(plan.components[0].component, "state-map")
        self.assertEqual(
            validate_presentation_plan(self.workflow_ir(), plan),
            (),
        )

    def test_validator_rejects_uncovered_unknown_and_authored_content(self) -> None:
        ir = self.workflow_ir()
        context = ViewContext(
            "spec", "system", "workflow", "approval", "mixed", "ko", "standalone"
        )
        valid = select_presentation_plan(ir, context)
        unknown = ComponentPlan(
            "invented-panel", ("missing:source:ref",), "invented.orientation", "open"
        )

        uncovered_codes = {
            item.code
            for item in validate_presentation_plan(
                ir, replace(valid, components=())
            )
        }
        unknown_codes = {
            item.code
            for item in validate_presentation_plan(
                ir, replace(valid, components=(unknown,))
            )
        }
        authored_codes = {
            item.code
            for item in validate_presentation_plan(
                ir,
                {
                    "profile": "generic",
                    "primary_question_key": "generic.review",
                    "components": [],
                    "authored_copy": "<script>alert(1)</script>",
                },
            )
        }

        self.assertEqual(uncovered_codes, {"VIEW_PLAN_UNCOVERED_BLOCK"})
        self.assertEqual(
            unknown_codes,
            {
                "VIEW_PLAN_COMPONENT",
                "VIEW_PLAN_DANGLING_REF",
                "VIEW_PLAN_UNCOVERED_BLOCK",
            },
        )
        self.assertEqual(authored_codes, {"VIEW_PLAN_AUTHORED_COPY"})

    def test_strict_mapping_plan_uses_the_same_validation_path(self) -> None:
        ir = self.workflow_ir()
        context = ViewContext(
            "spec", "system", "workflow", "approval", "mixed", "ko", "standalone"
        )
        selected = select_presentation_plan(ir, context)
        payload = asdict(selected)

        diagnostics = validate_presentation_plan(ir, payload)

        self.assertEqual(diagnostics, ())

    def test_profile_registry_covers_known_and_generic_contexts(self) -> None:
        ir = self.workflow_ir()
        expected = {
            "workflow": "spec.workflow",
            "api": "spec.api",
            "architecture": "spec.architecture",
            "policy": "spec.policy",
            "migration": "spec.migration",
            "unusual": "generic",
        }
        for subtype, profile in expected.items():
            with self.subTest(subtype=subtype):
                context = ViewContext(
                    "spec", "system", subtype, "review", "mixed", "ko", "standalone"
                )
                selected = select_presentation_plan(ir, context)
                self.assertEqual(selected.profile, profile)
                self.assertEqual(validate_presentation_plan(ir, selected), ())

        implementation = select_presentation_plan(
            ir,
            ViewContext(
                "spec",
                "system",
                "workflow",
                "implementation",
                "engineering",
                "ko",
                "standalone",
            ),
        )
        self.assertEqual(implementation.components[0].component, "runtime-atlas")

        plan_ir = build_semantic_ir(
            collect_plan_sources(
                REPOSITORY / "docs/plans/001-demo/plan.md", REPOSITORY
            )
        )
        for intent, profile in (("execution", "plan.execution"), ("status", "plan.status")):
            with self.subTest(intent=intent):
                selected = select_presentation_plan(
                    plan_ir,
                    ViewContext(
                        "plan", "plan", None, intent, "mixed", "en", "standalone"
                    ),
                )
                self.assertEqual(selected.profile, profile)
                self.assertEqual(validate_presentation_plan(plan_ir, selected), ())

    def test_view_context_rejects_unknown_enums(self) -> None:
        invalid = (
            ("combined", "review", "mixed", "standalone"),
            ("spec", "invented", "mixed", "standalone"),
            ("spec", "review", "executives", "standalone"),
            ("spec", "review", "mixed", "hosted"),
        )
        for mode, intent, audience, export_mode in invalid:
            with self.subTest(value=(mode, intent, audience, export_mode)):
                with self.assertRaises(ValueError):
                    ViewContext(
                        mode,
                        "system",
                        "workflow",
                        intent,
                        audience,
                        "ko",
                        export_mode,
                    )


if __name__ == "__main__":
    unittest.main()
