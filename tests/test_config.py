"""Tests for project configuration loading."""

import json
import tempfile
import unittest
from pathlib import Path

from venvm.config import (
    ConfigError,
    ProjectConfig,
    load_project_config,
    load_project_context,
)


class ConfigTests(unittest.TestCase):
    """Verify optional JSON configuration defaults."""

    def test_missing_config_returns_empty_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(load_project_config(Path(directory)), ProjectConfig())

    def test_config_loads_supported_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".venvm.json").write_text(
                json.dumps({"environment": ".venv", "module": "pytest"}),
                encoding="utf-8",
            )

            config = load_project_config(root)

            self.assertEqual(config.environment, ".venv")
            self.assertEqual(config.module, "pytest")

    def test_config_rejects_script_and_module_together(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".venvm.json").write_text(
                json.dumps({"script": "app.py", "module": "app"}),
                encoding="utf-8",
            )

            with self.assertRaises(ConfigError):
                load_project_config(root)

    def test_context_finds_nearest_parent_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "src" / "package"
            nested.mkdir(parents=True)
            config_path = root / ".venvm.json"
            config_path.write_text(
                json.dumps({"environment": ".venv"}),
                encoding="utf-8",
            )

            context = load_project_context(nested)

            self.assertEqual(context.root, root.resolve())
            self.assertEqual(context.config_path, config_path.resolve())
            self.assertEqual(context.config.environment, ".venv")

    def test_context_prefers_nearest_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "nested"
            nested.mkdir()
            (root / ".venvm.json").write_text(
                json.dumps({"environment": "root-env"}),
                encoding="utf-8",
            )
            (nested / ".venvm.json").write_text(
                json.dumps({"environment": "nested-env"}),
                encoding="utf-8",
            )

            context = load_project_context(nested)

            self.assertEqual(context.root, nested.resolve())
            self.assertEqual(context.config.environment, "nested-env")

    def test_context_without_configuration_uses_start_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            context = load_project_context(root)

            self.assertEqual(context.root, root.resolve())
            self.assertIsNone(context.config_path)
            self.assertEqual(context.config, ProjectConfig())


if __name__ == "__main__":
    unittest.main()
