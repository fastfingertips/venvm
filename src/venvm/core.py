"""Core filesystem and process operations for venvm."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class VirtualEnvironment:
    """A virtual environment discovered in the working directory."""

    path: Path
    python: Path


@dataclass(frozen=True)
class DependencySource:
    """A dependency definition that can be installed into an environment."""

    path: Path
    arguments: tuple[str, ...]


def interpreter_path(environment: Path, platform: str | None = None) -> Path:
    """Return the expected interpreter path for an environment."""

    current_platform = platform or os.name
    if current_platform == "nt":
        return environment / "Scripts" / "python.exe"
    return environment / "bin" / "python"


def discover_environments(root: Path) -> tuple[list[VirtualEnvironment], list[Path]]:
    """Find valid and broken virtual environments directly below *root*."""

    valid: list[VirtualEnvironment] = []
    broken: list[Path] = []

    try:
        children = sorted(root.iterdir(), key=lambda path: path.name.casefold())
    except OSError:
        return valid, broken

    for child in children:
        try:
            is_environment = child.is_dir() and (child / "pyvenv.cfg").is_file()
        except OSError:
            continue
        if not is_environment:
            continue

        python = interpreter_path(child)
        try:
            if python.is_file():
                valid.append(VirtualEnvironment(path=child, python=python))
            else:
                broken.append(child)
        except OSError:
            broken.append(child)

    return valid, broken


def discover_scripts(root: Path) -> list[Path]:
    """Find Python scripts directly inside *root*."""

    try:
        return sorted(
            (
                path
                for path in root.iterdir()
                if path.is_file() and path.suffix.casefold() == ".py"
            ),
            key=lambda path: path.name.casefold(),
        )
    except OSError:
        return []


def resolve_environment(root: Path, value: str) -> VirtualEnvironment | None:
    """Resolve and validate an environment path supplied by the user."""

    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    try:
        path = path.resolve()
        if not path.is_dir() or not (path / "pyvenv.cfg").is_file():
            return None
        python = interpreter_path(path)
        if not python.is_file():
            return None
    except OSError:
        return None
    return VirtualEnvironment(path=path, python=python)


def discover_dependency_sources(root: Path) -> list[DependencySource]:
    """Find supported dependency definitions in installation order."""

    sources: list[DependencySource] = []
    for filename in ("requirements.txt", "requirements-dev.txt"):
        path = root / filename
        try:
            if path.is_file():
                sources.append(
                    DependencySource(path=path, arguments=("-r", str(path)))
                )
        except OSError:
            continue

    pyproject = root / "pyproject.toml"
    try:
        if pyproject.is_file():
            sources.append(
                DependencySource(path=pyproject, arguments=("-e", str(root)))
            )
    except OSError:
        pass
    return sources


def create_environment(root: Path, name: str = ".venv") -> VirtualEnvironment:
    """Create a virtual environment with the current Python interpreter."""

    environment_path = root / name
    subprocess.run(
        [sys.executable, "-m", "venv", str(environment_path)],
        cwd=root,
        check=True,
    )
    python = interpreter_path(environment_path)
    if not python.is_file():
        raise RuntimeError("The environment was created without a Python interpreter.")
    return VirtualEnvironment(path=environment_path, python=python)


def run_script(
    python: Path,
    script: Path,
    arguments: Sequence[str],
    root: Path,
) -> int:
    """Run a script and return its exit code."""

    completed = subprocess.run(
        [str(python), str(script), *arguments],
        cwd=root,
        check=False,
    )
    return completed.returncode


def run_module(
    python: Path,
    module: str,
    arguments: Sequence[str],
    root: Path,
) -> int:
    """Run a Python module and return its exit code."""

    completed = subprocess.run(
        [str(python), "-m", module, *arguments],
        cwd=root,
        check=False,
    )
    return completed.returncode


def install_dependency_source(
    python: Path,
    source: DependencySource,
    root: Path,
) -> int:
    """Install one dependency definition and return pip's exit code."""

    completed = subprocess.run(
        [str(python), "-m", "pip", "install", *source.arguments],
        cwd=root,
        check=False,
    )
    return completed.returncode
