from __future__ import annotations

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
from review_sources import collect_plan_sources, collect_spec_sources  # noqa: E402


class ReviewIRTest(unittest.TestCase):
    def test_every_source_block_is_preserved_once(self) -> None:
        with TemporaryDirectory() as temporary:
            repository = Path(temporary)
            shutil.copytree(REPOSITORY, repository, dirs_exist_ok=True)
            source = repository / "docs/specs/008-alpha/spec.md"
            source.write_text(
                source.read_text(encoding="utf-8")
                .replace("kind: system", "kind: system\nsubtype: workflow", 1)
                .replace(
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
            source_lines = source.read_text(encoding="utf-8").splitlines()

        blocks = tuple(block for document in ir.documents for block in document.blocks)
        keys = [block.key for block in blocks]
        self.assertGreater(len(blocks), 0)
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(ir.coverage.total_blocks, len(blocks))
        self.assertEqual(ir.coverage.represented_blocks, len(blocks))
        frontmatter_end = source_lines.index("---", 1) + 1
        expected_lines = {
            line_number
            for line_number, line in enumerate(source_lines, 1)
            if line_number > frontmatter_end
            and line.strip()
            and not line.startswith("#")
        }
        represented_lines = [
            line_number
            for block in blocks
            for line_number in range(block.line, block.end_line + 1)
        ]
        self.assertEqual(set(represented_lines), expected_lines)
        self.assertEqual(len(represented_lines), len(set(represented_lines)))
        self.assertEqual(
            {"prose", "list", "table", "code", "mermaid", "generic"}
            - {block.kind for block in blocks},
            set(),
        )
        self.assertEqual(ir.documents[0].metadata["subtype"], "workflow")
        self.assertIn("Unknown Section", ir.documents[0].outline)
        self.assertTrue(
            any(
                block.key.startswith("current--008-alpha:unknown-section:")
                and "review-note" in block.body
                for block in blocks
            )
        )

    def test_spec_entities_are_source_anchored(self) -> None:
        bundle = collect_spec_sources(
            REPOSITORY / "docs/specs/008-alpha/spec.md", (), REPOSITORY
        )

        ir = build_semantic_ir(bundle)

        document = ir.documents[0]
        block_keys = {block.key for block in document.blocks}
        self.assertEqual(
            {"requirement", "acceptance", "mermaid", "decision", "interface"}
            - {entity.entity_type for entity in document.entities},
            set(),
        )
        self.assertTrue(
            all(
                entity.source_namespace == document.namespace
                and entity.block_key in block_keys
                for entity in document.entities
            )
        )

    def test_acceptance_relations_reference_existing_entities(self) -> None:
        bundle = collect_spec_sources(
            REPOSITORY / "docs/specs/008-alpha/spec.md", (), REPOSITORY
        )

        ir = build_semantic_ir(bundle)

        entity_keys = {
            entity.key for document in ir.documents for entity in document.entities
        }
        covers = [
            relation for relation in ir.relations if relation.relation_type == "covers"
        ]
        self.assertEqual(len(covers), 3)
        self.assertTrue(
            all(
                relation.from_entity in entity_keys
                and relation.to_entity in entity_keys
                and relation.source_namespace == "current--008-alpha"
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
        self.assertEqual(
            len([item for item in ir.relations if item.relation_type == "traces"]),
            7,
        )
        entity_keys = {item.key for item in entities}
        self.assertTrue(
            all(
                relation.from_entity in entity_keys and relation.to_entity in entity_keys
                for relation in ir.relations
            )
        )


if __name__ == "__main__":
    unittest.main()
