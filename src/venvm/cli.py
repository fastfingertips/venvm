"""Command-line interface for venvm."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from venvm import __version__
from venvm.config import ConfigError, ProjectConfig, load_project_config
from venvm.console import InputFunction, ask_yes_no, choose
from venvm.core import (
    VirtualEnvironment,
    create_environment,
    discover_dependency_sources,
    discover_environments,
    discover_scripts,
    install_dependency_source,
    resolve_environment,
    run_module,
    run_script,
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


def install_discovered_dependencies(
    environment: VirtualEnvironment,
    root: Path,
    assume_yes: bool,
    input_fn: InputFunction = input,
) -> None:
    """Offer to install dependency definitions into a new environment."""

    for source in discover_dependency_sources(root):
        should_install = assume_yes or ask_yes_no(
            f"Found {source.path.name}. Install its dependencies?",
            input_fn,
        )
        if not should_install:
            continue
        print(f"Installing: {source.path.name}")
        try:
            return_code = install_dependency_source(
                environment.python,
                source,
                root,
            )
        except OSError as error:
            print(f"Warning: Could not install dependencies: {error}", file=sys.stderr)
            continue
        if return_code != 0:
            print(
                f"Warning: {source.path.name} installation exited with code "
                f"{return_code}.",
                file=sys.stderr,
            )


def select_python(
    root: Path,
    preferred_environment: str | None = None,
    use_system: bool = False,
    assume_yes: bool = False,
    install_dependencies: bool = False,
    input_fn: InputFunction = input,
) -> Path | None:
    """Resolve, create, or interactively select a Python interpreter."""

    if use_system:
        return Path(sys.executable)
    if preferred_environment:
        environment = resolve_environment(root, preferred_environment)
        if environment is None:
            print(
                f"Error: No valid virtual environment found: {preferred_environment}",
                file=sys.stderr,
            )
            return None
        return environment.python

    environments, broken = discover_environments(root)
    for path in broken:
        print(f"Warning: Skipping broken environment: {path.name}", file=sys.stderr)

    create_new = not environments and (
        assume_yes
        or ask_yes_no(
            "No virtual environment found. Create a new .venv?",
            input_fn,
        )
    )
    if create_new:
        print("Creating .venv...")
        try:
            environment = create_environment(root)
            print(f"Virtual environment ready: {environment.path.name}")
            if install_dependencies:
                install_discovered_dependencies(environment, root, True, input_fn)
            elif not assume_yes:
                install_discovered_dependencies(environment, root, False, input_fn)
            return environment.python
        except (OSError, subprocess.SubprocessError, RuntimeError) as error:
            print(f"Error: Could not create virtual environment: {error}", file=sys.stderr)
            if assume_yes:
                print("Using the system Python interpreter.", file=sys.stderr)
                return Path(sys.executable)
            print("You can continue with the system Python interpreter.", file=sys.stderr)

    if assume_yes:
        if len(environments) == 1:
            return environments[0].python
        default = next(
            (item for item in environments if item.path.name == ".venv"),
            None,
        )
        if default:
            return default.python
        if environments:
            print(
                "Error: Multiple environments found; select one with --env.",
                file=sys.stderr,
            )
            return None
        return Path(sys.executable)

    options: list[tuple[str, Path]] = [
        (environment.path.name, environment.python)
        for environment in environments
    ]
    options.append((f"System Python ({sys.executable})", Path(sys.executable)))
    return choose("Select a Python interpreter:", options, input_fn)


def list_environments(root: Path) -> int:
    """Print detected interpreters without starting an interactive flow."""

    environments, broken = discover_environments(root)
    print("Virtual environments:")
    if environments:
        for environment in environments:
            print(f"  {environment.path.name}: {environment.python}")
    else:
        print("  None found")
    for path in broken:
        print(f"  {path.name}: broken")
    print(f"System Python: {sys.executable}")
    return 0


def resolve_script(
    root: Path,
    value: str | None,
    assume_yes: bool = False,
    input_fn: InputFunction = input,
) -> Path | None:
    """Validate an explicit script or ask the user to select one."""

    if value is not None:
        script = Path(value).expanduser()
        if not script.is_absolute():
            script = root / script
        if not script.is_file():
            print(f"Error: Script not found: {value}", file=sys.stderr)
            return None
        if script.suffix.casefold() != ".py":
            print(f"Error: Target must be a .py file: {value}", file=sys.stderr)
            return None
        return script.resolve()

    scripts = discover_scripts(root)
    if not scripts:
        print("Error: No Python scripts found in this directory.", file=sys.stderr)
        return None
    if len(scripts) == 1:
        print(f"Script: {scripts[0].name}")
        return scripts[0]
    if assume_yes:
        print(
            "Error: Multiple scripts found; specify the script to run.",
            file=sys.stderr,
        )
        return None
    return choose(
        "Select a script to run:",
        [(script.name, script) for script in scripts],
        input_fn,
    )


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
