from __future__ import annotations

from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest


TEST_DIR = Path(__file__).resolve().parent
REPOSITORY = TEST_DIR / "fixtures" / "repository"
SPEC_BUNDLE_FIXTURES = (
    TEST_DIR.parents[1] / "writing-specs" / "tests" / "fixtures" / "spec-bundle"
)
PLAN_BUNDLE_REPOSITORY = (
    TEST_DIR.parents[1]
    / "writing-specs"
    / "tests"
    / "fixtures"
    / "plan-bundle-repository"
)
SCRIPTS = TEST_DIR.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from review_ir import build_semantic_ir  # noqa: E402
from review_sources import collect_plan_sources, collect_spec_sources  # noqa: E402


class ReviewIRTest(unittest.TestCase):
    def test_five_member_bundle_enters_ir_once_with_cross_member_relation(self) -> None:
        bundle = collect_spec_sources(
            SPEC_BUNDLE_FIXTURES / "valid-five-file",
            (),
            SPEC_BUNDLE_FIXTURES,
        )

        ir = build_semantic_ir(bundle)

        self.assertEqual(len(ir.documents), 5)
        self.assertEqual(ir.coverage.ratio, 1.0)
        entities = [entity for document in ir.documents for entity in document.entities]
        self.assertEqual(
            {entity.entity_type for entity in entities},
            {"requirement", "acceptance", "decision", "mermaid"},
        )
        headings = [
            block
            for document in ir.documents
            for block in document.blocks
            if block.kind == "heading"
        ]
        self.assertEqual(
            {block.body for block in headings},
            {
                "### Every declared member contributes to one bundle",
                "### All five declared members load as one typed bundle",
            },
        )
        covers = [relation for relation in ir.relations if relation.relation_type == "covers"]
        self.assertEqual(len(covers), 1)
        by_key = {entity.key: entity for entity in entities}
        self.assertEqual(
            (
                by_key[covers[0].from_entity].attributes["heading"],
                by_key[covers[0].to_entity].attributes["heading"],
            ),
            (
                "All five declared members load as one typed bundle",
                "Every declared member contributes to one bundle",
            ),
        )

    def test_same_statement_in_two_bundles_has_distinct_qualified_entities(self) -> None:
        with TemporaryDirectory() as temporary:
            repository = Path(temporary)
            first = repository / "docs/specs/first-bundle"
            second = repository / "docs/specs/second-bundle"
            shutil.copytree(SPEC_BUNDLE_FIXTURES / "valid-five-file", first)
            shutil.copytree(SPEC_BUNDLE_FIXTURES / "valid-five-file", second)

            ir = build_semantic_ir(collect_spec_sources(first, (second,), repository))

        requirements = [
            entity
            for document in ir.documents
            for entity in document.entities
            if entity.entity_type == "requirement"
        ]
        self.assertEqual(len(requirements), 2)
        self.assertEqual(len({entity.key for entity in requirements}), 2)
        self.assertEqual(
            {entity.attributes["bundle_path"] for entity in requirements},
            {"docs/specs/first-bundle", "docs/specs/second-bundle"},
        )

    def test_plan_traces_exact_statement_entities_without_document_ids(self) -> None:
        bundle = collect_plan_sources(
            PLAN_BUNDLE_REPOSITORY
            / "docs/plans/semantic-migration/valid-plan.md",
            PLAN_BUNDLE_REPOSITORY,
        )

        ir = build_semantic_ir(bundle)

        traces = [relation for relation in ir.relations if relation.relation_type == "traces"]
        self.assertEqual(len(traces), 2)
        targets = {
            entity.key: entity
            for document in ir.documents
            for entity in document.entities
        }
        self.assertEqual(
            {targets[relation.to_entity].attributes["heading"] for relation in traces},
            {
                "Each bundle has exactly one root document",
                "A bundle with one declared root passes structural validation",
            },
        )
        self.assertTrue(
            all("id" not in document.metadata for document in ir.documents if document.role == "related_spec_context")
        )

    def test_every_source_block_is_preserved_once(self) -> None:
        with TemporaryDirectory() as temporary:
            repository = Path(temporary)
            shutil.copytree(REPOSITORY, repository, dirs_exist_ok=True)
            source = repository / "docs/specs/semantic-spec-bundles"
            history = source / "decisions-and-history.md"
            history.write_text(
                history.read_text(encoding="utf-8").replace(
                    "## Decisions & History",
                    """## Unknown Section

<review-note>preserve this unknown block</review-note>

| State | Owner |
|---|---|
| draft | author |

```json
{"state":"draft"}
```

## Decisions & History""",
                    1,
                ),
                encoding="utf-8",
            )

            bundle = collect_spec_sources(source, (), repository)
            ir = build_semantic_ir(bundle)

        blocks = tuple(block for document in ir.documents for block in document.blocks)
        keys = [block.key for block in blocks]
        self.assertGreater(len(blocks), 0)
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(ir.coverage.total_blocks, len(blocks))
        self.assertEqual(ir.coverage.represented_blocks, len(blocks))
        self.assertEqual(
            {"prose", "list", "table", "code", "mermaid", "generic", "heading"}
            - {block.kind for block in blocks},
            set(),
        )
        self.assertEqual(ir.documents[0].metadata["subtype"], "workflow")
        history_document = next(
            document for document in ir.documents if document.path.endswith("decisions-and-history.md")
        )
        self.assertIn("Unknown Section", history_document.outline)
        self.assertTrue(
            any(
                block.heading == "Unknown Section" and "review-note" in block.body
                for block in blocks
            )
        )

    def test_spec_entities_are_source_anchored(self) -> None:
        bundle = collect_spec_sources(
            REPOSITORY / "docs/specs/semantic-spec-bundles", (), REPOSITORY
        )

        ir = build_semantic_ir(bundle)

        block_keys = {block.key for document in ir.documents for block in document.blocks}
        self.assertEqual(
            {"requirement", "acceptance", "mermaid", "decision", "interface"}
            - {
                entity.entity_type
                for document in ir.documents
                for entity in document.entities
            },
            {"interface"},
        )
        self.assertTrue(
            all(
                entity.source_namespace == document.namespace
                and entity.block_key in block_keys
                for document in ir.documents
                for entity in document.entities
            )
        )

    def test_acceptance_relations_reference_existing_entities(self) -> None:
        bundle = collect_spec_sources(
            REPOSITORY / "docs/specs/semantic-spec-bundles", (), REPOSITORY
        )

        ir = build_semantic_ir(bundle)

        entity_keys = {
            entity.key for document in ir.documents for entity in document.entities
        }
        covers = [
            relation for relation in ir.relations if relation.relation_type == "covers"
        ]
        self.assertEqual(len(covers), 1)
        self.assertTrue(
            all(
                relation.from_entity in entity_keys
                and relation.to_entity in entity_keys
                and relation.source_namespace.endswith(
                    "statement-traceability-and-validation.md"
                )
                for relation in covers
            )
        )

    def test_plan_tasks_steps_and_traces_keep_source_ownership(self) -> None:
        bundle = collect_plan_sources(
            REPOSITORY / "docs/plans/001-demo/plan.md", REPOSITORY
        )

        ir = build_semantic_ir(bundle)

        entities = [
            entity for document in ir.documents for entity in document.entities
        ]
        task_entities = [item for item in entities if item.entity_type == "task"]
        step_entities = [item for item in entities if item.entity_type == "step"]
        self.assertEqual(
            {(item.source_namespace, item.entity_id) for item in task_entities},
            {("plan--001-demo", "Task1"), ("task--002-manifest", "Task2")},
        )
        self.assertEqual(len(step_entities), 3)
        self.assertEqual(
            len([item for item in ir.relations if item.relation_type == "belongs-to"]),
            3,
        )
        self.assertEqual(len([item for item in ir.relations if item.relation_type == "traces"]), 2)
        entity_keys = {item.key for item in entities}
        self.assertTrue(
            all(
                relation.from_entity in entity_keys and relation.to_entity in entity_keys
                for relation in ir.relations
            )
        )


if __name__ == "__main__":
    unittest.main()
