from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest


TEST_DIR = Path(__file__).resolve().parent
SCRIPTS = TEST_DIR.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from review_freshness import check_review  # noqa: E402


def framed_bundle_sha256(bundle_path: str, members: dict[str, bytes]) -> str:
    digest = hashlib.sha256()

    def frame(value: bytes) -> None:
        digest.update(len(value).to_bytes(8, "big"))
        digest.update(value)

    frame(bundle_path.encode("utf-8"))
    for path, contents in sorted(members.items()):
        frame(path.encode("utf-8"))
        frame(contents)
    return digest.hexdigest()


class ReviewFreshnessTest(unittest.TestCase):
    def test_any_declared_bundle_member_change_makes_bundle_stale(self) -> None:
        with TemporaryDirectory() as temporary:
            repository = Path(temporary)
            bundle_path = "docs/specs/review-contract"
            members = {
                "review-contract.md": b"# Review Contract\n",
                "statement-validation.md": b"# Statement Validation\n",
            }
            member_rows = []
            for index, (relative, contents) in enumerate(members.items(), 1):
                path = repository / bundle_path / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(contents)
                member_rows.append(
                    {
                        "key": f"source-{index}",
                        "role": "primary_spec",
                        "namespace": f"internal-{index}",
                        "bundle_path": bundle_path,
                        "bundle_title": "Review Contract",
                        "bundle_sha256": framed_bundle_sha256(bundle_path, members),
                        "path": f"{bundle_path}/{relative}",
                        "title": path.stem.replace("-", " ").title(),
                        "member_role": "root" if index == 1 else "contract",
                        "sha256": hashlib.sha256(contents).hexdigest(),
                        "status": "approved",
                    }
                )
            manifest = {
                "review_id": "bundle-freshness",
                "mode": "spec",
                "locale": "en",
                "generated_at": "2026-08-09T00:00:00Z",
                "checkpoint": "bundle-rendered",
                "commit": None,
                "rebuild_command": (
                    "build-review-viewer.sh --mode spec "
                    "--spec docs/specs/review-contract"
                ),
                "source_base": "../../../",
                "offline": False,
                "counts": {
                    "primary": {"requirement": 0, "acceptance": 0, "mermaid": 0},
                    "comparison": {},
                    "context": {},
                },
                "freshness": "unverified",
                "bundles": [
                    {
                        "role": "primary_spec",
                        "path": bundle_path,
                        "root_path": f"{bundle_path}/review-contract.md",
                        "title": "Review Contract",
                        "sha256": framed_bundle_sha256(bundle_path, members),
                    }
                ],
                "member_sources": member_rows,
                "plan_sources": [],
                "view_context": {},
                "presentation_plan": {},
            }
            viewer = repository / ".forge/reviews/bundle-freshness/view.html"
            viewer.parent.mkdir(parents=True)
            viewer.write_text(
                '<script type="application/json" id="forge-source-manifest">'
                + json.dumps(manifest, sort_keys=True)
                + "</script>\n",
                encoding="utf-8",
            )

            current = check_review(viewer, repository)
            changed = repository / bundle_path / "statement-validation.md"
            changed.write_bytes(changed.read_bytes() + b"changed\n")
            stale = check_review(viewer, repository)

        self.assertEqual(current.overall, "current")
        self.assertEqual(current.aggregates["primary"], "current")
        self.assertEqual(stale.overall, "stale")
        self.assertEqual(stale.aggregates["primary"], "stale")
        self.assertIn("stale source: docs/specs/review-contract/statement-validation.md", stale.diagnostics)


if __name__ == "__main__":
    unittest.main()
