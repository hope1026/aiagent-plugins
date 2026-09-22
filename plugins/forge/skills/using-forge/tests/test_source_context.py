import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/source_context.py"
spec = importlib.util.spec_from_file_location("source_context", SCRIPT)
context = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context)


class SourceContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "policy.md").write_text(
            "# 초대\n\n운영자만 초대한다.\n\n## 예외\n만료된 초대는 무료로 재발급한다.\n",
            encoding="utf-8",
        )
        (self.root / "worker.py").write_bytes(b"# observed implementation\r\nTTL = 24\r\n")
        (self.root / "guide.html").write_text("<p>운영자 초대 안내</p>", encoding="utf-8")

    def capture(self):
        return context.capture(self.root, ["policy.md", "worker.py"], ["guide.html"], "초대 검토")

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--repo-root", str(self.root), *args],
            capture_output=True, text=True,
        )

    def save_snapshot(self, value):
        (self.root / "snapshot.json").write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def test_plain_prose_and_code_are_lossless_without_metadata(self):
        snapshot = self.capture()
        self.assertEqual([r["path"] for r in snapshot["sources"]], ["policy.md", "worker.py"])
        for row in snapshot["sources"]:
            original = (self.root / row["path"]).read_bytes()
            self.assertEqual(row["content"].encode("utf-8"), original)
            self.assertEqual(row["sha256"], context.digest(original))
        self.assertNotIn("content", snapshot["artifacts"][0])

    def test_file_selection_order_does_not_change_snapshot(self):
        self.assertEqual(self.capture(), context.capture(
            self.root, ["worker.py", "policy.md"], ["guide.html"], "초대 검토"))

    def test_heading_language_and_section_order_do_not_hide_exceptions(self):
        for title in ("Overview", "목적", "초대를 다시 보내는 경우"):
            for reverse in (False, True):
                sections = ["운영자만 초대한다.", "만료된 초대는 무료로 재발급한다."]
                if reverse:
                    sections.reverse()
                text = "# " + title + "\n\n" + "\n\n".join(sections)
                (self.root / "policy.md").write_text(text, encoding="utf-8")
                row = self.capture()["sources"][0]
                self.assertEqual(row["content"], text)
                self.assertTrue(all(section in row["content"] for section in sections))

    def test_check_changes_and_missing_files_never_rewrites_snapshot_or_artifact(self):
        self.save_snapshot(self.capture())
        snapshot_bytes = (self.root / "snapshot.json").read_bytes()
        artifact_bytes = (self.root / "guide.html").read_bytes()
        result = self.cli("check", "--snapshot", "snapshot.json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["state"], "unchanged")
        (self.root / "policy.md").write_text("수정된 정책", encoding="utf-8")
        result = self.cli("check", "--snapshot", "snapshot.json")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["state"], "changed")
        (self.root / "worker.py").unlink()
        result = self.cli("check", "--snapshot", "snapshot.json")
        self.assertEqual(result.returncode, 1)
        rows = {r["path"]: r for r in json.loads(result.stdout)["files"]}
        self.assertEqual(rows["policy.md"]["state"], "changed")
        self.assertEqual(rows["worker.py"]["state"], "missing")
        self.assertEqual(rows["guide.html"]["state"], "unchanged")
        self.assertEqual((self.root / "snapshot.json").read_bytes(), snapshot_bytes)
        self.assertEqual((self.root / "guide.html").read_bytes(), artifact_bytes)

    def test_artifact_changes_are_independent_of_source_changes(self):
        snapshot = self.capture()
        (self.root / "guide.html").write_text("<p>new explanation</p>")
        result, code = context.check(self.root, snapshot)
        self.assertEqual(code, 1)
        self.assertEqual([r["state"] for r in result["files"]], ["unchanged", "unchanged", "changed"])

    def test_unreadable_selected_file_is_unavailable(self):
        snapshot = self.capture()
        original_hash = context.file_hash
        def blocked_hash(path):
            if path.name == "policy.md":
                raise PermissionError("read denied")
            return original_hash(path)
        with patch.object(context, "file_hash", side_effect=blocked_hash):
            result, code = context.check(self.root, snapshot)
        self.assertEqual(code, 1)
        self.assertEqual(result["state"], "unavailable")
        self.assertEqual(result["files"][0]["state"], "unavailable")

    def test_unselected_dependency_change_is_not_claimed_as_detected(self):
        snapshot = self.capture()
        (self.root / "other.md").write_text("unselected dependency")
        result, code = context.check(self.root, snapshot)
        self.assertEqual(code, 0)
        self.assertIn("not semantic correctness", result["scope"])

    def test_invalid_paths_and_duplicate_selections_are_rejected(self):
        for path in ("../outside", "/etc/passwd", "a/../policy.md", "./policy.md", "a//b", "C:/data"):
            with self.subTest(path=path), self.assertRaises(context.ContextError):
                context.capture(self.root, [path], [])
        for sources, artifacts in ((["policy.md", "policy.md"], []), (["policy.md"], ["policy.md"])):
            with self.assertRaises(context.ContextError):
                context.capture(self.root, sources, artifacts)

    def test_symlink_escape_is_rejected_on_capture_and_after_capture(self):
        snapshot = self.capture()
        with tempfile.TemporaryDirectory() as outside:
            external = Path(outside) / "external.md"
            external.write_text("outside content must not be emitted")
            (self.root / "policy.md").unlink()
            (self.root / "policy.md").symlink_to(external)
            result = self.cli("capture", "--source", "policy.md")
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("outside content must not be emitted", result.stdout)
            with self.assertRaises(context.ContextError):
                context.check(self.root, snapshot)

    def test_byte_limits_are_exact_and_fail_without_partial_output(self):
        (self.root / "size.txt").write_bytes(b"12345")
        (self.root / "extra.txt").write_bytes(b"6")
        self.assertEqual(context.capture(self.root, ["size.txt"], [], max_source_bytes=5,
                                        max_total_bytes=5)["sources"][0]["content"], "12345")
        for sources, per_file, total in ((["size.txt"], 4, 5), (["size.txt", "extra.txt"], 5, 5)):
            with self.assertRaisesRegex(context.ContextError, "no content truncated"):
                context.capture(self.root, sources, [], max_source_bytes=per_file, max_total_bytes=total)
        result = self.cli("capture", "--source", "policy.md", "--max-source-bytes", "1")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(set(json.loads(result.stdout)), {"error"})

    def test_invalid_utf8_and_directories_fail_as_sources(self):
        (self.root / "binary").write_bytes(b"\xff")
        (self.root / "folder").mkdir()
        for source in ("binary", "folder", "missing"):
            with self.assertRaises(context.ContextError):
                context.capture(self.root, [source], [])

    def test_modified_snapshot_content_and_duplicate_records_fail(self):
        snapshot = self.capture()
        invalid = copy.deepcopy(snapshot)
        invalid["sources"][0]["content"] = "invented policy"
        with self.assertRaisesRegex(context.ContextError, "does not match"):
            context.check(self.root, invalid)
        invalid = copy.deepcopy(snapshot)
        invalid["sources"].append(invalid["sources"][0])
        with self.assertRaisesRegex(context.ContextError, "duplicate"):
            context.check(self.root, invalid)

    def test_bad_schema_and_duplicate_json_keys_fail_without_tracebacks(self):
        for value in ([], {}, {"schema": "unknown"}, {**self.capture(), "sources": []}):
            self.save_snapshot(value)
            result = self.cli("check", "--snapshot", "snapshot.json")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stderr, "")
            self.assertIn("error", json.loads(result.stdout))
        (self.root / "snapshot.json").write_text('{"schema":1,"schema":2}')
        result = self.cli("check", "--snapshot", "snapshot.json")
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicate JSON key", result.stdout)


if __name__ == "__main__":
    unittest.main()
