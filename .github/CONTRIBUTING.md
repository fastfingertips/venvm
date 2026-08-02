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

## Commit Messages

After `Initial commit`, every commit subject must:

- follow Conventional Commits, such as `fix: handle missing script`;
- be entirely lowercase;
- contain no more than 45 characters.

## Pull Requests

- Add or update tests for behavior changes.
- Use a compliant commit subject.
- Run the complete test suite before opening a pull request.
- Update both README files when user-facing commands change.
- Keep unrelated refactoring out of the same pull request.
