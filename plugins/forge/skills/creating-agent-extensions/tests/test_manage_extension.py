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

    def init_skill_extension(
        self,
        root: Path,
        scope: str = "repository",
        skill_names: tuple[str, ...] = ("example-skill",),
    ) -> tuple[Path, Path]:
        base = root / ("home" if scope == "user" else "repo")
        stage = root / "stage"
        base.mkdir()
        skills = [self.write_skill(stage, name=name) for name in skill_names]
        args = [
            "init",
            "--scope",
            scope,
            "--base-dir",
            str(base),
            "--name",
            "example-extension",
            "--description",
            "Example extension for confirmed workflows.",
            "--profile",
            "skill",
        ]
        for skill in skills:
            args.extend(["--skill-source", str(skill)])
        if scope == "user":
            args.append("--confirm-user-write")
        result = self.run_manager(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return base.resolve(), base.resolve() / ".agent-extensions" / "example-extension"

    def init_mcp_extension(
        self,
        root: Path,
        scope: str = "repository",
        existing_configs: bool = False,
    ) -> tuple[Path, Path]:
        base = root / ("home" if scope == "user" else "repo")
        stage = root / "stage"
        base.mkdir()
        if existing_configs:
            self.write_existing_native_configs(base, scope)
        mcp = self.write_mcp(stage)
        args = [
            "init",
            "--scope",
            scope,
            "--base-dir",
            str(base),
            "--name",
            "example-extension",
            "--description",
            "Example extension for confirmed workflows.",
            "--profile",
            "mcp",
            "--mcp-source",
            str(mcp),
        ]
        if scope == "user":
            args.append("--confirm-user-write")
        result = self.run_manager(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return base.resolve(), base.resolve() / ".agent-extensions" / "example-extension"

    def write_existing_native_configs(self, base: Path, scope: str) -> None:
        codex = base / ".codex" / "config.toml"
        codex.parent.mkdir(parents=True)
        codex.write_text(
            'model = "gpt-5"\n\n[mcp_servers.existing]\ncommand = "existing-command"\n',
            encoding="utf-8",
        )
        if scope == "repository":
            claude = base / ".mcp.json"
            antigravity = base / ".agents" / "mcp_config.json"
        else:
            claude = base / ".claude.json"
            antigravity = base / ".gemini" / "config" / "mcp_config.json"
        for path, marker in ((claude, "claude"), (antigravity, "antigravity")):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(
                    {
                        "theme": marker,
                        "nested": {"keep": [1, 2, 3]},
                        "mcpServers": {
                            "existing": {"command": "existing-command", "args": []}
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

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
            self.assertEqual(
                preview["credentialRequirements"],
                ["LOCAL_TOOLS_TOKEN", "REMOTE_TOOLS_TOKEN"],
            )
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

    def test_repository_skill_render_uses_shared_agents_and_claude_wrappers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base, extension = self.init_skill_extension(Path(temporary))

            result = self.run_manager("render", "--extension", str(extension))

            self.assertEqual(result.returncode, 0, result.stderr)
            agents_wrapper = base / ".agents" / "skills" / "example-skill" / "SKILL.md"
            claude_wrapper = base / ".claude" / "skills" / "example-skill" / "SKILL.md"
            self.assertEqual(agents_wrapper.read_text(), claude_wrapper.read_text())
            self.assertIn(
                "../../../.agent-extensions/example-extension/skills/example-skill/SKILL.md",
                agents_wrapper.read_text(),
            )
            self.assertNotIn("Follow the confirmed example workflow.", agents_wrapper.read_text())

            expected_targets = {
                "codex": ".agents/skills/example-skill/SKILL.md",
                "claude-code": ".claude/skills/example-skill/SKILL.md",
                "antigravity": ".agents/skills/example-skill/SKILL.md",
            }
            for agent, expected_target in expected_targets.items():
                state = json.loads(
                    (extension / "adapters" / agent / "state.json").read_text()
                )
                self.assertEqual(state["extension"], "example-extension")
                self.assertEqual(len(state["canonicalHash"]), 64)
                self.assertEqual(len(state["entries"]), 1)
                self.assertEqual(state["entries"][0]["kind"], "skill")
                self.assertEqual(state["entries"][0]["target"], expected_target)

            validation = self.run_manager("validate", "--extension", str(extension))
            self.assertEqual(validation.returncode, 0, validation.stderr)
            self.assertEqual(json.loads(validation.stdout)["status"], "PASS")

    def test_user_skill_render_previews_three_targets_before_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base, extension = self.init_skill_extension(Path(temporary), scope="user")
            before = self.snapshot(base)

            refused = self.run_manager("render", "--extension", str(extension))

            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("E_CONFIRMATION", refused.stderr)
            preview = json.loads(refused.stdout)
            self.assertEqual(len(preview["nativeTargets"]), 3)
            self.assertEqual(len(preview["changes"]), 3)
            self.assertEqual({item["action"] for item in preview["changes"]}, {"create"})
            self.assertEqual(preview["collisions"], [])
            self.assertEqual(self.snapshot(base), before)

            rendered = self.run_manager(
                "render",
                "--extension",
                str(extension),
                "--confirm-user-write",
            )
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            wrapper_paths = [
                base / ".agents" / "skills" / "example-skill" / "SKILL.md",
                base / ".claude" / "skills" / "example-skill" / "SKILL.md",
                base / ".gemini" / "config" / "skills" / "example-skill" / "SKILL.md",
            ]
            for wrapper_path in wrapper_paths:
                self.assertTrue(wrapper_path.is_file())
                self.assertIn(str(extension / "skills" / "example-skill" / "SKILL.md"), wrapper_path.read_text())

    def test_skill_collision_never_overwrites_other_owner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base, extension = self.init_skill_extension(Path(temporary))
            collision = base / ".agents" / "skills" / "example-skill" / "SKILL.md"
            collision.parent.mkdir(parents=True)
            sentinel = b"owned by another source\n"
            collision.write_bytes(sentinel)

            result = self.run_manager("render", "--extension", str(extension))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("E_COLLISION", result.stderr)
            self.assertEqual(collision.read_bytes(), sentinel)
            self.assertFalse(
                (base / ".claude" / "skills" / "example-skill" / "SKILL.md").exists()
            )
            self.assertFalse((extension / "adapters").exists())

    def test_validate_reports_skill_wrapper_and_canonical_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base, extension = self.init_skill_extension(Path(temporary))
            rendered = self.run_manager("render", "--extension", str(extension))
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            wrapper = base / ".claude" / "skills" / "example-skill" / "SKILL.md"
            wrapper.write_text(wrapper.read_text() + "drift\n", encoding="utf-8")

            validation = self.run_manager("validate", "--extension", str(extension))

            self.assertNotEqual(validation.returncode, 0)
            self.assertIn("E_DRIFT", validation.stderr)
            self.assertIn("example-extension", validation.stderr)
            self.assertIn(str(wrapper), validation.stderr)

        with tempfile.TemporaryDirectory() as temporary:
            _, extension = self.init_skill_extension(Path(temporary))
            rendered = self.run_manager("render", "--extension", str(extension))
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            canonical = extension / "skills" / "example-skill" / "SKILL.md"
            canonical.write_text(canonical.read_text() + "Canonical change.\n", encoding="utf-8")

            validation = self.run_manager("validate", "--extension", str(extension))

            self.assertNotEqual(validation.returncode, 0)
            self.assertIn("E_DRIFT", validation.stderr)
            self.assertIn("canonical hash", validation.stderr)

    def test_multiple_skills_are_tracked_in_all_agent_states(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            _, extension = self.init_skill_extension(
                Path(temporary), skill_names=("example-skill", "review-skill")
            )

            result = self.run_manager("render", "--extension", str(extension))

            self.assertEqual(result.returncode, 0, result.stderr)
            for agent in ("codex", "claude-code", "antigravity"):
                state = json.loads(
                    (extension / "adapters" / agent / "state.json").read_text()
                )
                self.assertEqual(
                    {entry["name"] for entry in state["entries"]},
                    {"example-skill", "review-skill"},
                )

    def test_repository_mcp_render_preserves_unrelated_json_and_toml(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base, extension = self.init_mcp_extension(
                Path(temporary), existing_configs=True
            )
            codex = base / ".codex" / "config.toml"
            claude = base / ".mcp.json"
            antigravity = base / ".agents" / "mcp_config.json"
            codex_before = codex.read_bytes()
            json_before = {
                path: json.loads(path.read_text()) for path in (claude, antigravity)
            }

            result = self.run_manager("render", "--extension", str(extension))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(codex.read_bytes().startswith(codex_before))
            codex_text = codex.read_text()
            self.assertIn("# BEGIN creating-agent-extensions:example-extension", codex_text)
            self.assertIn('[mcp_servers."local-tools"]', codex_text)
            self.assertIn('env_vars = ["LOCAL_TOOLS_TOKEN"]', codex_text)
            self.assertIn('[mcp_servers."remote-tools"]', codex_text)
            self.assertIn(
                'env_http_headers = { "Authorization" = "REMOTE_TOOLS_TOKEN" }',
                codex_text,
            )
            for path in (claude, antigravity):
                after = json.loads(path.read_text())
                self.assertEqual(after["theme"], json_before[path]["theme"])
                self.assertEqual(after["nested"], json_before[path]["nested"])
                self.assertEqual(
                    after["mcpServers"]["existing"],
                    json_before[path]["mcpServers"]["existing"],
                )
                self.assertEqual(
                    after["mcpServers"]["local-tools"]["env"],
                    {"LOCAL_TOOLS_TOKEN": "${LOCAL_TOOLS_TOKEN}"},
                )
                self.assertEqual(
                    after["mcpServers"]["remote-tools"]["headers"],
                    {"Authorization": "${REMOTE_TOOLS_TOKEN}"},
                )
            validation = self.run_manager("validate", "--extension", str(extension))
            self.assertEqual(validation.returncode, 0, validation.stderr)

    def test_user_mcp_render_requires_confirmation_and_preserves_settings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base, extension = self.init_mcp_extension(
                Path(temporary), scope="user", existing_configs=True
            )
            before = self.snapshot(base)

            refused = self.run_manager("render", "--extension", str(extension))

            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("E_CONFIRMATION", refused.stderr)
            preview = json.loads(refused.stdout)
            self.assertEqual(len(preview["nativeTargets"]), 3)
            self.assertEqual(len(preview["changes"]), 6)
            self.assertEqual({item["action"] for item in preview["changes"]}, {"create"})
            self.assertEqual(
                preview["credentialRequirements"],
                ["LOCAL_TOOLS_TOKEN", "REMOTE_TOOLS_TOKEN"],
            )
            self.assertEqual(preview["collisions"], [])
            self.assertEqual(self.snapshot(base), before)

            rendered = self.run_manager(
                "render",
                "--extension",
                str(extension),
                "--confirm-user-write",
            )
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            self.assertIn("local-tools", (base / ".codex" / "config.toml").read_text())
            for path in (
                base / ".claude.json",
                base / ".gemini" / "config" / "mcp_config.json",
            ):
                document = json.loads(path.read_text())
                self.assertIn("local-tools", document["mcpServers"])
                self.assertEqual(document["nested"], {"keep": [1, 2, 3]})

    def test_mcp_collision_refuses_same_name_from_other_owner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base, extension = self.init_mcp_extension(Path(temporary))
            collision = base / ".mcp.json"
            collision.write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "local-tools": {"command": "other-owner", "args": []}
                        }
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            sentinel = collision.read_bytes()

            result = self.run_manager("render", "--extension", str(extension))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("E_COLLISION", result.stderr)
            self.assertEqual(collision.read_bytes(), sentinel)
            self.assertFalse((base / ".codex" / "config.toml").exists())
            self.assertFalse((base / ".agents" / "mcp_config.json").exists())
            self.assertFalse((extension / "adapters").exists())

    def test_validate_reports_json_and_toml_entry_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base, extension = self.init_mcp_extension(Path(temporary))
            rendered = self.run_manager("render", "--extension", str(extension))
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            claude = base / ".mcp.json"
            document = json.loads(claude.read_text())
            document["mcpServers"]["local-tools"]["command"] = "drifted-command"
            claude.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

            validation = self.run_manager("validate", "--extension", str(extension))

            self.assertNotEqual(validation.returncode, 0)
            self.assertIn("E_DRIFT", validation.stderr)
            self.assertIn(str(claude), validation.stderr)

        with tempfile.TemporaryDirectory() as temporary:
            base, extension = self.init_mcp_extension(Path(temporary))
            rendered = self.run_manager("render", "--extension", str(extension))
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            codex = base / ".codex" / "config.toml"
            codex.write_text(
                codex.read_text().replace('command = "python3"', 'command = "drifted"'),
                encoding="utf-8",
            )

            validation = self.run_manager("validate", "--extension", str(extension))

            self.assertNotEqual(validation.returncode, 0)
            self.assertIn("E_DRIFT", validation.stderr)
            self.assertIn(str(codex), validation.stderr)

    def test_stdio_env_vars_and_http_headers_from_env_never_embed_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base, extension = self.init_mcp_extension(Path(temporary))

            result = self.run_manager("render", "--extension", str(extension))

            self.assertEqual(result.returncode, 0, result.stderr)
            all_native = "\n".join(
                [
                    (base / ".codex" / "config.toml").read_text(),
                    (base / ".mcp.json").read_text(),
                    (base / ".agents" / "mcp_config.json").read_text(),
                ]
            )
            self.assertNotIn("plain-secret-value", all_native)
            self.assertIn("LOCAL_TOOLS_TOKEN", all_native)
            self.assertIn("REMOTE_TOOLS_TOKEN", all_native)

    def test_bundle_tracks_skills_and_mcp_in_all_agent_states(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base = root / "repo"
            stage = root / "stage"
            base.mkdir()
            first = self.write_skill(stage, name="example-skill")
            second = self.write_skill(stage, name="review-skill")
            mcp = self.write_mcp(stage)
            init = self.run_manager(
                "init",
                "--scope",
                "repository",
                "--base-dir",
                str(base),
                "--name",
                "example-extension",
                "--description",
                "Example extension for confirmed workflows.",
                "--profile",
                "bundle",
                "--skill-source",
                str(first),
                "--skill-source",
                str(second),
                "--mcp-source",
                str(mcp),
            )
            self.assertEqual(init.returncode, 0, init.stderr)
            extension = base.resolve() / ".agent-extensions" / "example-extension"

            rendered = self.run_manager("render", "--extension", str(extension))

            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            for agent in ("codex", "claude-code", "antigravity"):
                state = json.loads(
                    (extension / "adapters" / agent / "state.json").read_text()
                )
                self.assertEqual(
                    {(entry["kind"], entry["name"]) for entry in state["entries"]},
                    {
                        ("skill", "example-skill"),
                        ("skill", "review-skill"),
                        ("mcp", "local-tools"),
                        ("mcp", "remote-tools"),
                    },
                )
            validation = self.run_manager("validate", "--extension", str(extension))
            self.assertEqual(validation.returncode, 0, validation.stderr)

    def test_init_copies_skill_resources_and_digest_detects_resource_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base = root / "repo"
            source_root = root / "stage" / "resource-skill"
            base.mkdir()
            source_root.mkdir(parents=True)
            skill = source_root / "SKILL.md"
            skill.write_text(
                "\n".join(
                    [
                        "---",
                        "name: resource-skill",
                        "description: 'Use when a confirmed resource workflow applies.'",
                        "---",
                        "",
                        "# Resource Skill",
                        "",
                        "Read references/guide.md and run scripts/check.py.",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            reference = source_root / "references" / "guide.md"
            script = source_root / "scripts" / "check.py"
            reference.parent.mkdir()
            script.parent.mkdir()
            reference.write_text("# Confirmed Guide\n\nFollow the confirmed flow.\n")
            script.write_text("print('confirmed')\n")
            args = [
                "--scope",
                "repository",
                "--base-dir",
                str(base),
                "--name",
                "resource-extension",
                "--description",
                "Resource extension for confirmed workflows.",
                "--profile",
                "skill",
                "--skill-source",
                str(skill),
            ]

            preview_result = self.run_manager("plan", *args)

            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            preview = json.loads(preview_result.stdout)
            self.assertIn(
                "skills/resource-skill/references/guide.md",
                preview["canonicalWrites"],
            )
            self.assertIn(
                "skills/resource-skill/scripts/check.py",
                preview["canonicalWrites"],
            )

            initialized = self.run_manager("init", *args)
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            extension = base.resolve() / ".agent-extensions" / "resource-extension"
            canonical_reference = (
                extension / "skills" / "resource-skill" / "references" / "guide.md"
            )
            self.assertEqual(canonical_reference.read_bytes(), reference.read_bytes())
            rendered = self.run_manager("render", "--extension", str(extension))
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            self.assertEqual(
                self.run_manager("validate", "--extension", str(extension)).returncode,
                0,
            )

            canonical_reference.write_text(
                canonical_reference.read_text() + "Changed resource.\n",
                encoding="utf-8",
            )
            validation = self.run_manager("validate", "--extension", str(extension))
            self.assertNotEqual(validation.returncode, 0)
            self.assertIn("canonical hash", validation.stderr)


if __name__ == "__main__":
    unittest.main()
