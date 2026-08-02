<div align="center">
  <h1>venvm</h1>
  <p>Select a Python virtual environment and run scripts or modules with it.</p>
  <p>
    <a href="https://pypi.org/project/venvm/"><img alt="PyPI version" src="https://img.shields.io/pypi/v/venvm.svg"></a>
    <a href="https://pypi.org/project/venvm/"><img alt="Python versions" src="https://img.shields.io/pypi/pyversions/venvm.svg"></a>
    <a href="https://github.com/fastfingertips/venvm/actions/workflows/tests.yml"><img alt="Tests" src="https://github.com/fastfingertips/venvm/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://github.com/fastfingertips/venvm/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/venvm.svg"></a>
  </p>
  <p><strong>English</strong> | <a href="https://github.com/fastfingertips/venvm/blob/main/README.tr.md">Türkçe</a></p>
</div>

## Installation

Install venvm from PyPI:

```console
python -m pip install venvm
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

Install the repository in editable mode:

```console
python -m pip install -e .
```

Run the standard-library test suite:

```console
python -m unittest discover -s tests
```

## Roadmap

Planned configuration and project management work is tracked in
[`.github/TODO.md`](https://github.com/fastfingertips/venvm/blob/main/.github/TODO.md).
