"""Interactive environment and target selection workflows."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from venvm.console import InputFunction, ask_yes_no, choose
from venvm.core import (
    VirtualEnvironment,
    create_environment,
    discover_dependency_sources,
    discover_environments,
    discover_scripts,
    install_dependency_source,
    resolve_environment,
)


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
