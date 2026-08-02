"""Command-line interface for venvm."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from venvm import __version__
from venvm.config import ConfigError, ProjectConfig, load_project_config
from venvm.core import run_module, run_script
from venvm.workflow import (
    install_discovered_dependencies,
    list_environments,
    resolve_script,
    select_python,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="venvm",
        description="Select a Python environment and run a script or module.",
    )
    environment_group = parser.add_mutually_exclusive_group()
    environment_group.add_argument(
        "--env",
        metavar="PATH",
        help="use a specific virtual environment",
    )
    environment_group.add_argument(
        "--system",
        action="store_true",
        help="use the system Python interpreter",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="accept prompts and avoid interactive selection when unambiguous",
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="install detected dependency sources after creating an environment",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_environments",
        help="list detected environments and exit",
    )
    parser.add_argument(
        "-m",
        "--module",
        nargs=argparse.REMAINDER,
        metavar="MODULE_OR_ARG",
        help="run a module and pass all following values to it",
    )
    parser.add_argument("script", nargs="?", help="Python script to run")
    parser.add_argument(
        "script_args",
        nargs=argparse.REMAINDER,
        help="arguments passed to the Python script",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def _load_config(root: Path) -> ProjectConfig | None:
    """Load configuration and report user-facing errors."""

    try:
        return load_project_config(root)
    except ConfigError as error:
        print(f"Error: Invalid .venvm.json: {error}", file=sys.stderr)
        return None


def main(argv: Sequence[str] | None = None) -> int:
    """Run the venvm command-line application."""

    parser = build_parser()
    arguments = parser.parse_args(argv)
    if arguments.module is not None and arguments.script is not None:
        parser.error("script and --module cannot be used together")
    if arguments.module == []:
        parser.error("--module requires a module name")

    try:
        root = Path.cwd()
    except OSError as error:
        print(f"Error: Could not read the working directory: {error}", file=sys.stderr)
        return 1

    if arguments.list_environments:
        return list_environments(root)

    config = _load_config(root)
    if config is None:
        return 1
    preferred_environment = arguments.env or config.environment
    python = select_python(
        root,
        preferred_environment=preferred_environment,
        use_system=arguments.system,
        assume_yes=arguments.yes,
        install_dependencies=arguments.install_deps,
    )
    if python is None:
        return 1

    module_values = arguments.module
    if module_values is not None:
        module, target_arguments = module_values[0], module_values[1:]
    elif arguments.script is None and config.module:
        module, target_arguments = config.module, arguments.script_args
    else:
        module = None
        target_arguments = arguments.script_args

    try:
        if module:
            print(f"Running: {python} -m {module}")
            return run_module(python, module, target_arguments, root)

        script_value = arguments.script or config.script
        script = resolve_script(root, script_value, assume_yes=arguments.yes)
        if script is None:
            return 1
        print(f"Running: {python} {script.name}")
        return run_script(python, script, target_arguments, root)
    except OSError as error:
        print(f"Error: Could not run target: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
