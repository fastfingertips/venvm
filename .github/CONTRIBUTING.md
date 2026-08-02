# Contributing

## Development Setup

venvm requires Python 3.9 or newer and has no runtime dependencies.

```console
python -m venv .venv
python -m pip install -e .
python -m unittest discover -s tests -v
```

Use English for source code, docstrings, CLI messages, tests, and commit messages.
Keep changes focused and preserve standard-library-only runtime behavior.

## Pull Requests

- Add or update tests for behavior changes.
- Run the complete test suite before opening a pull request.
- Update both README files when user-facing commands change.
- Keep unrelated refactoring out of the same pull request.

