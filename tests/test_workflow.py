"""Tests for interactive selection workflows."""

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import ANY, patch

from venvm.core import DependencySource, VirtualEnvironment
from venvm.workflow import (
    install_discovered_dependencies,
    resolve_script,
    select_python,
)


def answers(*values: str):
    """Return a deterministic input function for interactive tests."""

    iterator = iter(values)
    return lambda _prompt: next(iterator)


class WorkflowTests(unittest.TestCase):
    """Verify environment and script selection workflows."""

    def test_resolve_script_rejects_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(resolve_script(Path(directory), "missing.py"))

    def test_resolve_script_selects_the_only_script(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "main.py"
            script.touch()
            self.assertEqual(resolve_script(root, None), script)

    def test_assume_yes_rejects_ambiguous_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "first.py").touch()
            (root / "second.py").touch()

            selected = resolve_script(root, None, assume_yes=True)

        self.assertIsNone(selected)

    def test_select_python_offers_system_python_after_creation_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch(
            "venvm.workflow.create_environment",
            side_effect=subprocess.CalledProcessError(1, "venv"),
        ):
            selected = select_python(
                Path(directory),
                input_fn=answers("y", "1"),
            )

        self.assertIsNotNone(selected)

    def test_select_python_uses_new_environment_immediately(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            environment = VirtualEnvironment(root / ".venv", root / ".venv/python")
            with patch("venvm.workflow.create_environment", return_value=environment):
                selected = select_python(root, input_fn=answers("y"))

        self.assertEqual(selected, environment.python)

    @patch("venvm.workflow.install_discovered_dependencies")
    def test_assume_yes_does_not_install_dependencies_implicitly(self, install) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            environment = VirtualEnvironment(root / ".venv", root / ".venv/python")
            with patch("venvm.workflow.create_environment", return_value=environment):
                select_python(root, assume_yes=True)

        install.assert_not_called()

    @patch("venvm.workflow.install_discovered_dependencies")
    def test_install_dependencies_requires_explicit_option(self, install) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            environment = VirtualEnvironment(root / ".venv", root / ".venv/python")
            with patch("venvm.workflow.create_environment", return_value=environment):
                select_python(
                    root,
                    assume_yes=True,
                    install_dependencies=True,
                )

        install.assert_called_once_with(environment, root, True, ANY)

    def test_select_python_uses_system_without_discovery(self) -> None:
        with patch("venvm.workflow.discover_environments") as discover:
            selected = select_python(Path("workspace"), use_system=True)

        self.assertEqual(selected, Path(__import__("sys").executable))
        discover.assert_not_called()

    def test_assume_yes_rejects_ambiguous_environments(self) -> None:
        environments = [
            VirtualEnvironment(Path("first"), Path("first/python")),
            VirtualEnvironment(Path("second"), Path("second/python")),
        ]
        with patch(
            "venvm.workflow.discover_environments",
            return_value=(environments, []),
        ):
            selected = select_python(Path("workspace"), assume_yes=True)

        self.assertIsNone(selected)

    @patch("venvm.workflow.install_dependency_source", return_value=0)
    @patch("venvm.workflow.discover_dependency_sources")
    def test_dependency_installation_can_be_accepted(
        self,
        discover_sources,
        install_source,
    ) -> None:
        source = DependencySource(Path("requirements.txt"), ("-r", "requirements.txt"))
        discover_sources.return_value = [source]
        environment = VirtualEnvironment(Path(".venv"), Path(".venv/python"))

        install_discovered_dependencies(
            environment,
            Path("workspace"),
            assume_yes=False,
            input_fn=answers("y"),
        )

        install_source.assert_called_once_with(
            environment.python,
            source,
            Path("workspace"),
        )


if __name__ == "__main__":
    unittest.main()
