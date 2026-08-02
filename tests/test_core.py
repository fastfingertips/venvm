"""Tests for venvm core operations."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from venvm.core import (
    DependencySource,
    discover_dependency_sources,
    discover_environments,
    discover_scripts,
    install_dependency_source,
    interpreter_path,
    resolve_environment,
    run_module,
)


class CoreTests(unittest.TestCase):
    """Verify filesystem discovery without external test dependencies."""

    def test_interpreter_path_is_platform_specific(self) -> None:
        root = Path("workspace")
        self.assertEqual(
            interpreter_path(root / ".venv", "nt"),
            root / ".venv" / "Scripts" / "python.exe",
        )
        self.assertEqual(
            interpreter_path(root / ".venv", "posix"),
            root / ".venv" / "bin" / "python",
        )

    def test_discover_environments_separates_broken_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid_path = root / ".venv"
            valid_path.mkdir()
            (valid_path / "pyvenv.cfg").touch()
            python = interpreter_path(valid_path)
            python.parent.mkdir()
            python.touch()

            broken_path = root / "broken-env"
            broken_path.mkdir()
            (broken_path / "pyvenv.cfg").touch()

            environments, broken = discover_environments(root)

            self.assertEqual(
                [environment.path for environment in environments],
                [valid_path],
            )
            self.assertEqual(broken, [broken_path])

    def test_discover_scripts_only_returns_top_level_python_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "run.py").touch()
            (root / "notes.txt").touch()
            nested = root / "nested"
            nested.mkdir()
            (nested / "hidden.py").touch()

            self.assertEqual(discover_scripts(root), [root / "run.py"])

    def test_resolve_environment_validates_interpreter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            environment_path = root / ".venv"
            environment_path.mkdir()
            (environment_path / "pyvenv.cfg").touch()
            python = interpreter_path(environment_path)
            python.parent.mkdir()
            python.touch()

            environment = resolve_environment(root, ".venv")

            self.assertIsNotNone(environment)
            self.assertEqual(environment.python, python)

    def test_discover_dependency_sources_finds_supported_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for filename in ("requirements.txt", "requirements-dev.txt", "pyproject.toml"):
                (root / filename).touch()

            sources = discover_dependency_sources(root)

            self.assertEqual(
                [source.path.name for source in sources],
                ["requirements.txt", "requirements-dev.txt", "pyproject.toml"],
            )

    @patch("venvm.core.subprocess.run")
    def test_run_module_uses_python_dash_m(self, run) -> None:
        run.return_value.returncode = 7

        result = run_module(Path("python"), "pytest", ["-q"], Path("workspace"))

        self.assertEqual(result, 7)
        run.assert_called_once_with(
            ["python", "-m", "pytest", "-q"],
            cwd=Path("workspace"),
            check=False,
        )

    @patch("venvm.core.subprocess.run")
    def test_install_dependency_source_uses_selected_python(self, run) -> None:
        run.return_value.returncode = 0
        source = DependencySource(Path("requirements.txt"), ("-r", "requirements.txt"))

        result = install_dependency_source(
            Path(".venv/python"),
            source,
            Path("workspace"),
        )

        self.assertEqual(result, 0)
        run.assert_called_once_with(
            [
                str(Path(".venv/python")),
                "-m",
                "pip",
                "install",
                "-r",
                "requirements.txt",
            ],
            cwd=Path("workspace"),
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
