"""Tests for the venvm command-line interface."""

import unittest
from pathlib import Path
from unittest.mock import patch

from venvm.cli import build_parser, main
from venvm.config import ProjectConfig, ProjectContext


class CliTests(unittest.TestCase):
    """Verify argument parsing and command routing."""

    def test_parser_collects_module_arguments(self) -> None:
        arguments = build_parser().parse_args(
            ["--env", ".venv", "--module", "pytest", "-q"]
        )
        self.assertEqual(arguments.env, ".venv")
        self.assertEqual(arguments.module, ["pytest", "-q"])

    def test_parser_accepts_explicit_dependency_installation(self) -> None:
        arguments = build_parser().parse_args(["--yes", "--install-deps", "app.py"])
        self.assertTrue(arguments.yes)
        self.assertTrue(arguments.install_deps)

    @patch("venvm.cli.list_environments", return_value=0)
    @patch("venvm.cli.load_project_context")
    def test_main_lists_environments_from_project_root(
        self,
        load_context,
        list_all,
    ) -> None:
        project_root = Path("project")
        load_context.return_value = ProjectContext(
            root=project_root,
            config_path=project_root / ".venvm.json",
            config=ProjectConfig(),
        )

        result = main(["--list"])

        self.assertEqual(result, 0)
        list_all.assert_called_once_with(project_root)

    @patch("venvm.cli.run_script", return_value=0)
    @patch("venvm.cli.resolve_script", return_value=Path("project/app.py"))
    @patch("venvm.cli.select_python", return_value=Path("python"))
    @patch("venvm.cli.load_project_context")
    def test_cli_environment_overrides_project_config(
        self,
        load_context,
        select_interpreter,
        resolve_target,
        run_target,
    ) -> None:
        project_root = Path("project")
        load_context.return_value = ProjectContext(
            root=project_root,
            config_path=project_root / ".venvm.json",
            config=ProjectConfig(environment="config-env"),
        )

        result = main(["--env", "cli-env", "app.py"])

        self.assertEqual(result, 0)
        select_interpreter.assert_called_once_with(
            project_root,
            preferred_environment="cli-env",
            use_system=False,
            assume_yes=False,
            install_dependencies=False,
        )
        resolve_target.assert_called_once_with(
            project_root,
            "app.py",
            assume_yes=False,
        )
        run_target.assert_called_once_with(
            Path("python"),
            Path("project/app.py"),
            [],
            project_root,
        )

    @patch("venvm.cli.run_module", return_value=7)
    def test_main_runs_module_and_preserves_exit_code(self, run_selected_module) -> None:
        result = main(["--system", "--module", "pytest", "-q"])

        self.assertEqual(result, 7)
        run_selected_module.assert_called_once_with(
            Path(__import__("sys").executable),
            "pytest",
            ["-q"],
            Path.cwd(),
        )


if __name__ == "__main__":
    unittest.main()
