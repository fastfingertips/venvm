"""Project configuration support for venvm."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CONFIG_FILENAME = ".venvm.json"


class ConfigError(ValueError):
    """Raised when a project configuration file is invalid."""


@dataclass(frozen=True)
class ProjectConfig:
    """Defaults loaded from a project's configuration file."""

    environment: str | None = None
    script: str | None = None
    module: str | None = None


@dataclass(frozen=True)
class ProjectContext:
    """Configuration values and paths resolved for a project."""

    root: Path
    config_path: Path | None
    config: ProjectConfig


def _optional_string(data: dict[str, Any], key: str) -> str | None:
    """Read an optional non-empty string value."""

    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"'{key}' must be a non-empty string")
    return value


def load_project_config(root: Path) -> ProjectConfig:
    """Load ``.venvm.json`` from *root* when it exists."""

    path = root / CONFIG_FILENAME
    if not path.exists():
        return ProjectConfig()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ConfigError(f"cannot read {CONFIG_FILENAME}: {error}") from error
    if not isinstance(data, dict):
        raise ConfigError(f"{CONFIG_FILENAME} must contain a JSON object")

    supported = {"environment", "script", "module"}
    unknown = sorted(set(data) - supported)
    if unknown:
        raise ConfigError(f"unknown setting: {unknown[0]}")

    config = ProjectConfig(
        environment=_optional_string(data, "environment"),
        script=_optional_string(data, "script"),
        module=_optional_string(data, "module"),
    )
    if config.script and config.module:
        raise ConfigError("'script' and 'module' cannot be used together")
    return config


def load_project_context(start: Path) -> ProjectContext:
    """Find the nearest project configuration at or above *start*."""

    try:
        root = start.resolve()
    except OSError as error:
        raise ConfigError(f"cannot resolve project path: {error}") from error

    for directory in (root, *root.parents):
        config_path = directory / CONFIG_FILENAME
        try:
            exists = config_path.exists()
        except OSError as error:
            raise ConfigError(f"cannot inspect {config_path}: {error}") from error
        if exists:
            return ProjectContext(
                root=directory,
                config_path=config_path,
                config=load_project_config(directory),
            )

    return ProjectContext(root=root, config_path=None, config=ProjectConfig())
