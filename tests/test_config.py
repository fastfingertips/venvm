"""Tests for project configuration loading."""

import json
import tempfile
import unittest
from pathlib import Path

from venvm.config import ConfigError, ProjectConfig, load_project_config


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


if __name__ == "__main__":
    unittest.main()
