from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
MANAGER = SKILL_DIR / "scripts" / "manage_extension.py"


class ManagerTestCase(unittest.TestCase):
    def run_manager(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(MANAGER), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def write_skill(
        self,
        directory: Path,
        name: str = "example-skill",
        body: str = "Follow the confirmed example workflow.",
    ) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{name}.md"
        path.write_text(
            "\n".join(
                [
                    "---",
                    f"name: {name}",
                    "description: 'Use when the confirmed example workflow applies.'",
                    "---",
                    "",
                    "# Example Skill",
                    "",
                    body,
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return path

    def write_mcp(self, directory: Path, payload: dict | None = None) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "servers.json"
        document = payload or {
            "mcpServers": {
                "local-tools": {
                    "transport": "stdio",
                    "command": "python3",
                    "args": ["server.py"],
                    "envVars": ["LOCAL_TOOLS_TOKEN"],
                },
                "remote-tools": {
                    "transport": "http",
                    "url": "https://example.test/mcp",
                    "headersFromEnv": {"Authorization": "REMOTE_TOOLS_TOKEN"},
                },
            }
        }
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        return path

    def snapshot(self, root: Path) -> dict[str, bytes]:
        return {
            str(path.relative_to(root)): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    def common_args(
        self,
        action: str,
        scope: str,
        base: Path,
        skill: Path,
        mcp: Path,
        name: str = "example-extension",
    ) -> list[str]:
        return [
            action,
            "--scope",
            scope,
            "--base-dir",
            str(base),
            "--name",
            name,
            "--description",
            "Example extension for confirmed workflows.",
            "--profile",
            "bundle",
            "--skill-source",
            str(skill),
            "--mcp-source",
            str(mcp),
        ]

    def test_plan_is_write_free_and_lists_repository_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base = root / "repo"
            stage = root / "stage"
            base.mkdir()
            skill = self.write_skill(stage)
            mcp = self.write_mcp(stage)
            before = self.snapshot(root)

            result = self.run_manager(
                *self.common_args("plan", "repository", base, skill, mcp)
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.snapshot(root), before)
            preview = json.loads(result.stdout)
            self.assertEqual(preview["action"], "plan")
            self.assertEqual(preview["scope"], "repository")
            self.assertEqual(preview["profile"], "bundle")
            self.assertEqual(
                Path(preview["extensionRoot"]),
                base.resolve() / ".agent-extensions" / "example-extension",
            )
            self.assertEqual(
                {Path(path) for path in preview["nativeTargets"]},
                {
                    base.resolve() / ".agents" / "skills" / "example-skill" / "SKILL.md",
                    base.resolve() / ".claude" / "skills" / "example-skill" / "SKILL.md",
                    base.resolve() / ".codex" / "config.toml",
                    base.resolve() / ".mcp.json",
                    base.resolve() / ".agents" / "mcp_config.json",
                },
            )
            self.assertEqual(preview["collisions"], [])
            self.assertFalse(preview["requiresConfirmation"])

    def test_user_init_requires_confirmation_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "home"
            stage = root / "stage"
            home.mkdir()
            skill = self.write_skill(stage)
            mcp = self.write_mcp(stage)
            before = self.snapshot(root)

            result = self.run_manager(
                *self.common_args("init", "user", home, skill, mcp)
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("E_CONFIRMATION", result.stderr)
            self.assertEqual(self.snapshot(root), before)
            self.assertFalse((home / ".agent-extensions").exists())

    def test_init_copies_valid_skill_and_mcp_sources_into_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base = root / "repo"
            stage = root / "stage"
            base.mkdir()
            skill = self.write_skill(stage)
            mcp = self.write_mcp(stage)

            result = self.run_manager(
                *self.common_args("init", "repository", base, skill, mcp)
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            extension = base / ".agent-extensions" / "example-extension"
            manifest = json.loads((extension / "extension.json").read_text())
            self.assertEqual(manifest["schemaVersion"], 1)
            self.assertEqual(manifest["name"], "example-extension")
            self.assertEqual(manifest["scope"], "repository")
            self.assertEqual(
                manifest["targets"], ["codex", "claude-code", "antigravity"]
            )
            self.assertEqual(
                manifest["components"]["skills"],
                [
                    {
                        "name": "example-skill",
                        "description": "Use when the confirmed example workflow applies.",
                        "path": "skills/example-skill/SKILL.md",
                    }
                ],
            )
            self.assertEqual(
                manifest["components"]["mcpServers"],
                [
                    {"name": "local-tools", "path": "mcp/servers.json"},
                    {"name": "remote-tools", "path": "mcp/servers.json"},
                ],
            )
            self.assertEqual(
                (extension / "skills" / "example-skill" / "SKILL.md").read_bytes(),
                skill.read_bytes(),
            )
            self.assertEqual((extension / "mcp" / "servers.json").read_bytes(), mcp.read_bytes())

    def test_init_rejects_invalid_name_placeholder_and_secret(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            stage = root / "stage"
            valid_skill = self.write_skill(stage)
            valid_mcp = self.write_mcp(stage)

            invalid_base = root / "invalid-name"
            invalid_base.mkdir()
            invalid = self.run_manager(
                *self.common_args(
                    "init",
                    "repository",
                    invalid_base,
                    valid_skill,
                    valid_mcp,
                    name="Bad_Name",
                )
            )
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("E_NAME", invalid.stderr)
            self.assertFalse((invalid_base / ".agent-extensions").exists())

            placeholder_base = root / "placeholder"
            placeholder_base.mkdir()
            placeholder_skill = self.write_skill(
                root / "placeholder-stage", body="TBD: complete this later."
            )
            placeholder = self.run_manager(
                *self.common_args(
                    "init",
                    "repository",
                    placeholder_base,
                    placeholder_skill,
                    valid_mcp,
                )
            )
            self.assertNotEqual(placeholder.returncode, 0)
            self.assertIn("E_PLACEHOLDER", placeholder.stderr)
            self.assertFalse((placeholder_base / ".agent-extensions").exists())

            secret_base = root / "secret"
            secret_base.mkdir()
            secret_mcp = self.write_mcp(
                root / "secret-stage",
                {
                    "mcpServers": {
                        "unsafe": {
                            "transport": "stdio",
                            "command": "python3",
                            "env": {"API_TOKEN": "plain-secret-value"},
                        }
                    }
                },
            )
            secret = self.run_manager(
                *self.common_args(
                    "init",
                    "repository",
                    secret_base,
                    valid_skill,
                    secret_mcp,
                )
            )
            self.assertNotEqual(secret.returncode, 0)
            self.assertIn("E_SECRET", secret.stderr)
            self.assertFalse((secret_base / ".agent-extensions").exists())


if __name__ == "__main__":
    unittest.main()
