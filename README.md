# venvm

**English** | [Türkçe](README.tr.md)

`venvm` selects a Python virtual environment in the current directory and runs
a Python script or module with that environment's interpreter.

## Installation

Install the development version from the repository:

```console
python -m pip install -e .
```

## Usage

Select an environment and script interactively:

```console
venvm
```

Run a script with arguments:

```console
venvm app.py --port 8000
```

Select an environment explicitly or use the system interpreter:

```console
venvm --env .venv app.py
venvm --system app.py
```

Run a Python module:

```console
venvm --env .venv --module pytest -q
venvm --system --module http.server 8000
```

Values after `--module` are passed directly to the module. Place environment
options before `--module`.

List detected environments without running anything:

```console
venvm --list
```

`--yes` accepts confirmation prompts. If multiple environments exist, `.venv`
is used when available. Otherwise, specify the environment with `--env`.

Use `--install-deps` to install detected dependency sources without additional
confirmation. `--yes` alone never installs dependencies automatically.

The command scans direct children of the current directory for `pyvenv.cfg` and
the platform-specific Python executable. If no environment exists, it offers to
create `.venv`. The system Python interpreter remains available as an option.

After creating an environment, `venvm` detects `requirements.txt`,
`requirements-dev.txt`, and `pyproject.toml`. It asks for confirmation before
installing each source.

## Project Configuration

Add `.venvm.json` to the project root to define defaults:

```json
{
  "environment": ".venv",
  "script": "app.py"
}
```

For a module:

```json
{
  "environment": ".venv",
  "module": "pytest"
}
```

`script` and `module` cannot be used together. Command-line values override the
configuration file.

## Development

Run the standard-library test suite:

```console
python -m unittest discover -s tests
```

## Roadmap

Planned configuration and project management work is tracked in
[`.github/TODO.md`](.github/TODO.md).
