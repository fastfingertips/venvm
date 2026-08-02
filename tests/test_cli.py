"""Tests for the venvm command-line interface."""

import unittest
from pathlib import Path
from unittest.mock import patch

from venvm.cli import build_parser, main


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
